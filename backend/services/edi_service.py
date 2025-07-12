"""
EDI Service for processing Electronic Data Interchange messages.

This service handles EDIFACT/X12 message parsing, validation, and processing
for customs clearance operations including job registration and declarations.
"""

import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload

from models.edi import (
    EDIMessage, EDIJob, CustomsDeclaration, DeclarationItem,
    EDIMessageType, EDIMessageStatus, EDIDirection, JobStatus,
    DeclarationType, DeclarationStatus
)
from models.customer import Customer, CustomerShipment


class EDIStandard(str, Enum):
    """EDI standard enumeration."""
    EDIFACT = "EDIFACT"
    X12 = "X12"


@dataclass
class EDISegment:
    """Represents an EDI segment."""
    tag: str
    elements: List[str]
    
    def get_element(self, index: int, default: str = "") -> str:
        """Get element by index with default value."""
        return self.elements[index] if index < len(self.elements) else default


@dataclass
class ParsedEDIMessage:
    """Represents a parsed EDI message."""
    standard: EDIStandard
    message_type: str
    segments: List[EDISegment]
    interchange_control_number: Optional[str] = None
    functional_group_number: Optional[str] = None
    transaction_set_number: Optional[str] = None


class EDIParser:
    """EDI message parser for EDIFACT and X12 formats."""
    
    # EDIFACT delimiters
    EDIFACT_SEGMENT_TERMINATOR = "'"
    EDIFACT_ELEMENT_SEPARATOR = "+"
    EDIFACT_COMPONENT_SEPARATOR = ":"
    
    # X12 delimiters
    X12_SEGMENT_TERMINATOR = "~"
    X12_ELEMENT_SEPARATOR = "*"
    X12_COMPONENT_SEPARATOR = ">"
    
    @classmethod
    def detect_standard(cls, message: str) -> EDIStandard:
        """Detect EDI standard from message content."""
        # Remove whitespace and check for standard indicators
        clean_message = message.strip()
        
        # EDIFACT typically starts with UNA or UNB
        if clean_message.startswith(('UNA', 'UNB')):
            return EDIStandard.EDIFACT
        
        # X12 typically starts with ISA
        if clean_message.startswith('ISA'):
            return EDIStandard.X12
        
        # Fallback: check for common delimiters
        if "'" in clean_message and "+" in clean_message:
            return EDIStandard.EDIFACT
        elif "~" in clean_message and "*" in clean_message:
            return EDIStandard.X12
        
        # Default to EDIFACT
        return EDIStandard.EDIFACT
    
    @classmethod
    def parse_edifact(cls, message: str) -> ParsedEDIMessage:
        """Parse EDIFACT message."""
        segments = []
        interchange_control_number = None
        functional_group_number = None
        message_type = None
        
        # Split into segments
        segment_strings = message.split(cls.EDIFACT_SEGMENT_TERMINATOR)
        
        for segment_str in segment_strings:
            segment_str = segment_str.strip()
            if not segment_str:
                continue
            
            # Split into elements
            elements = segment_str.split(cls.EDIFACT_ELEMENT_SEPARATOR)
            if not elements:
                continue
            
            tag = elements[0]
            segment_elements = elements[1:] if len(elements) > 1 else []
            
            segment = EDISegment(tag=tag, elements=segment_elements)
            segments.append(segment)
            
            # Extract control numbers and message type
            if tag == "UNB":  # Interchange header
                if len(segment_elements) >= 5:
                    interchange_control_number = segment_elements[4]
            elif tag == "UNG":  # Functional group header
                if len(segment_elements) >= 5:
                    functional_group_number = segment_elements[4]
            elif tag == "UNH":  # Message header
                if len(segment_elements) >= 2:
                    message_type_info = segment_elements[1].split(cls.EDIFACT_COMPONENT_SEPARATOR)
                    if message_type_info:
                        message_type = message_type_info[0]
        
        return ParsedEDIMessage(
            standard=EDIStandard.EDIFACT,
            message_type=message_type or "UNKNOWN",
            segments=segments,
            interchange_control_number=interchange_control_number,
            functional_group_number=functional_group_number
        )
    
    @classmethod
    def parse_x12(cls, message: str) -> ParsedEDIMessage:
        """Parse X12 message."""
        segments = []
        interchange_control_number = None
        functional_group_number = None
        transaction_set_number = None
        message_type = None
        
        # Split into segments
        segment_strings = message.split(cls.X12_SEGMENT_TERMINATOR)
        
        for segment_str in segment_strings:
            segment_str = segment_str.strip()
            if not segment_str:
                continue
            
            # Split into elements
            elements = segment_str.split(cls.X12_ELEMENT_SEPARATOR)
            if not elements:
                continue
            
            tag = elements[0]
            segment_elements = elements[1:] if len(elements) > 1 else []
            
            segment = EDISegment(tag=tag, elements=segment_elements)
            segments.append(segment)
            
            # Extract control numbers and message type
            if tag == "ISA":  # Interchange header
                if len(segment_elements) >= 13:
                    interchange_control_number = segment_elements[12].strip()
            elif tag == "GS":  # Functional group header
                if len(segment_elements) >= 6:
                    functional_group_number = segment_elements[5]
                    message_type = segment_elements[0]  # Functional identifier code
            elif tag == "ST":  # Transaction set header
                if len(segment_elements) >= 2:
                    transaction_set_number = segment_elements[1]
                    if not message_type and len(segment_elements) >= 1:
                        message_type = segment_elements[0]
        
        return ParsedEDIMessage(
            standard=EDIStandard.X12,
            message_type=message_type or "UNKNOWN",
            segments=segments,
            interchange_control_number=interchange_control_number,
            functional_group_number=functional_group_number,
            transaction_set_number=transaction_set_number
        )
    
    @classmethod
    def parse_message(cls, message: str) -> ParsedEDIMessage:
        """Parse EDI message automatically detecting the standard."""
        standard = cls.detect_standard(message)
        
        if standard == EDIStandard.EDIFACT:
            return cls.parse_edifact(message)
        else:
            return cls.parse_x12(message)


class EDIService:
    """Service for processing EDI messages and managing customs operations."""
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self.parser = EDIParser()
    
    async def process_inbound_message(
        self, 
        raw_message: str,
        external_reference: Optional[str] = None
    ) -> EDIMessage:
        """Process an inbound EDI message."""
        try:
            # Parse the message
            parsed = self.parser.parse_message(raw_message)
            
            # Generate message ID
            message_id = self._generate_message_id(parsed)
            
            # Determine message type
            edi_message_type = self._map_message_type(parsed.message_type)
            
            # Create EDI message record
            edi_message = EDIMessage(
                message_id=message_id,
                message_type=edi_message_type,
                direction=EDIDirection.INBOUND,
                raw_message=raw_message,
                parsed_data=self._serialize_parsed_message(parsed),
                status=EDIMessageStatus.PENDING,
                external_reference=external_reference,
                abf_reference=parsed.interchange_control_number
            )
            
            self.db.add(edi_message)
            await self.db.commit()
            await self.db.refresh(edi_message)
            
            # Process based on message type
            await self._process_by_message_type(edi_message, parsed)
            
            return edi_message
            
        except Exception as e:
            # Create failed message record
            message_id = f"FAILED_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
            
            edi_message = EDIMessage(
                message_id=message_id,
                message_type=EDIMessageType.CUSRES,  # Default type
                direction=EDIDirection.INBOUND,
                raw_message=raw_message,
                status=EDIMessageStatus.FAILED,
                error_message=str(e),
                external_reference=external_reference
            )
            
            self.db.add(edi_message)
            await self.db.commit()
            
            raise
    
    async def register_job(
        self,
        customer_id: int,
        job_type: str,
        consignment_reference: str,
        cargo_description: str,
        port_of_discharge: str,
        estimated_arrival: Optional[datetime] = None,
        **kwargs
    ) -> EDIJob:
        """Register a new customs clearance job."""
        # Generate job number
        job_number = await self._generate_job_number()
        
        # Create job record
        job = EDIJob(
            job_number=job_number,
            job_type=job_type,
            customer_id=customer_id,
            consignment_reference=consignment_reference,
            cargo_description=cargo_description,
            port_of_discharge=port_of_discharge,
            estimated_arrival=estimated_arrival,
            status=JobStatus.REGISTERED,
            **kwargs
        )
        
        self.db.add(job)
        await self.db.commit()
        await self.db.refresh(job)
        
        # Generate and send job registration EDI message
        await self._send_job_registration_message(job)
        
        return job
    
    async def create_declaration(
        self,
        job_id: int,
        declaration_type: DeclarationType,
        importer_name: str,
        total_invoice_value: str,
        currency: str = "AUD",
        **kwargs
    ) -> CustomsDeclaration:
        """Create a new customs declaration."""
        # Get job details
        job = await self.db.get(EDIJob, job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")
        
        # Generate declaration number
        declaration_number = await self._generate_declaration_number()
        
        # Create declaration record
        declaration = CustomsDeclaration(
            declaration_number=declaration_number,
            declaration_type=declaration_type,
            job_id=job_id,
            customer_id=job.customer_id,
            consignment_reference=job.consignment_reference,
            importer_name=importer_name,
            total_invoice_value=total_invoice_value,
            currency=currency,
            port_of_discharge=job.port_of_discharge,
            status=DeclarationStatus.DRAFT,
            **kwargs
        )
        
        self.db.add(declaration)
        await self.db.commit()
        await self.db.refresh(declaration)
        
        return declaration
    
    async def submit_declaration(self, declaration_id: int) -> EDIMessage:
        """Submit a customs declaration to ABF."""
        # Get declaration with items
        result = await self.db.execute(
            select(CustomsDeclaration)
            .options(selectinload(CustomsDeclaration.declaration_items))
            .where(CustomsDeclaration.id == declaration_id)
        )
        declaration = result.scalar_one_or_none()
        
        if not declaration:
            raise ValueError(f"Declaration {declaration_id} not found")
        
        if declaration.status != DeclarationStatus.DRAFT:
            raise ValueError(f"Declaration {declaration_id} is not in draft status")
        
        # Generate CUSDEC message
        cusdec_message = await self._generate_cusdec_message(declaration)
        
        # Create outbound EDI message
        message_id = self._generate_message_id_for_declaration(declaration)
        
        edi_message = EDIMessage(
            message_id=message_id,
            message_type=EDIMessageType.CUSDEC,
            direction=EDIDirection.OUTBOUND,
            raw_message=cusdec_message,
            status=EDIMessageStatus.PENDING,
            customer_id=declaration.customer_id,
            job_id=declaration.job_id,
            declaration_id=declaration.id
        )
        
        self.db.add(edi_message)
        
        # Update declaration status
        declaration.status = DeclarationStatus.SUBMITTED
        declaration.submitted_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(edi_message)
        
        # Send to ABF (simulated)
        await self._send_to_abf(edi_message)
        
        return edi_message
    
    async def add_declaration_item(
        self,
        declaration_id: int,
        item_number: int,
        description: str,
        hs_code: str,
        quantity: str,
        unit_price: str,
        country_of_origin: str,
        **kwargs
    ) -> DeclarationItem:
        """Add an item to a customs declaration."""
        # Calculate total value
        try:
            qty = float(quantity)
            price = float(unit_price)
            total_value = str(qty * price)
        except ValueError:
            total_value = "0.00"
        
        item = DeclarationItem(
            declaration_id=declaration_id,
            item_number=item_number,
            description=description,
            hs_code=hs_code,
            quantity=quantity,
            unit_price=unit_price,
            total_value=total_value,
            country_of_origin=country_of_origin,
            **kwargs
        )
        
        self.db.add(item)
        await self.db.commit()
        await self.db.refresh(item)
        
        return item
    
    async def get_job_status(self, job_id: int) -> Dict[str, Any]:
        """Get comprehensive job status including messages and declarations."""
        result = await self.db.execute(
            select(EDIJob)
            .options(
                selectinload(EDIJob.messages),
                selectinload(EDIJob.declarations).selectinload(CustomsDeclaration.declaration_items)
            )
            .where(EDIJob.id == job_id)
        )
        job = result.scalar_one_or_none()
        
        if not job:
            raise ValueError(f"Job {job_id} not found")
        
        return {
            "job": {
                "id": job.id,
                "job_number": job.job_number,
                "status": job.status,
                "job_type": job.job_type,
                "consignment_reference": job.consignment_reference,
                "estimated_arrival": job.estimated_arrival,
                "created_at": job.created_at
            },
            "messages": [
                {
                    "id": msg.id,
                    "message_type": msg.message_type,
                    "direction": msg.direction,
                    "status": msg.status,
                    "received_at": msg.received_at
                }
                for msg in job.messages
            ],
            "declarations": [
                {
                    "id": decl.id,
                    "declaration_number": decl.declaration_number,
                    "declaration_type": decl.declaration_type,
                    "status": decl.status,
                    "submitted_at": decl.submitted_at,
                    "item_count": len(decl.declaration_items)
                }
                for decl in job.declarations
            ]
        }
    
    # Private helper methods
    
    def _generate_message_id(self, parsed: ParsedEDIMessage) -> str:
        """Generate unique message ID."""
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        control_num = parsed.interchange_control_number or "000000"
        return f"{parsed.message_type}_{timestamp}_{control_num}"
    
    def _generate_message_id_for_declaration(self, declaration: CustomsDeclaration) -> str:
        """Generate message ID for declaration submission."""
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        return f"CUSDEC_{declaration.declaration_number}_{timestamp}"
    
    def _map_message_type(self, message_type: str) -> EDIMessageType:
        """Map parsed message type to EDI message type enum."""
        type_mapping = {
            "CUSCAR": EDIMessageType.CUSCAR,
            "CUSRES": EDIMessageType.CUSRES,
            "CUSDEC": EDIMessageType.CUSDEC,
            "CUSREP": EDIMessageType.CUSREP,
            "JOBMAN": EDIMessageType.JOBMAN,
            "JOBRES": EDIMessageType.JOBRES,
            "INVOIC": EDIMessageType.INVOIC,
            "PAXLST": EDIMessageType.PAXLST,
            "CODECO": EDIMessageType.CODECO,
            "COPRAR": EDIMessageType.COPRAR
        }
        
        return type_mapping.get(message_type, EDIMessageType.CUSRES)
    
    def _serialize_parsed_message(self, parsed: ParsedEDIMessage) -> Dict[str, Any]:
        """Serialize parsed message for JSON storage."""
        return {
            "standard": parsed.standard,
            "message_type": parsed.message_type,
            "interchange_control_number": parsed.interchange_control_number,
            "functional_group_number": parsed.functional_group_number,
            "transaction_set_number": parsed.transaction_set_number,
            "segments": [
                {
                    "tag": seg.tag,
                    "elements": seg.elements
                }
                for seg in parsed.segments
            ]
        }
    
    async def _process_by_message_type(self, edi_message: EDIMessage, parsed: ParsedEDIMessage):
        """Process message based on its type."""
        try:
            if edi_message.message_type == EDIMessageType.CUSRES:
                await self._process_customs_response(edi_message, parsed)
            elif edi_message.message_type == EDIMessageType.JOBRES:
                await self._process_job_response(edi_message, parsed)
            elif edi_message.message_type == EDIMessageType.CUSCAR:
                await self._process_cargo_report(edi_message, parsed)
            
            # Update status to processed
            edi_message.status = EDIMessageStatus.PROCESSED
            edi_message.processed_at = datetime.utcnow()
            
        except Exception as e:
            edi_message.status = EDIMessageStatus.ERROR
            edi_message.error_message = str(e)
            edi_message.processing_attempts += 1
        
        await self.db.commit()
    
    async def _process_customs_response(self, edi_message: EDIMessage, parsed: ParsedEDIMessage):
        """Process customs response message."""
        # Extract response data and update related declaration
        for segment in parsed.segments:
            if segment.tag == "BGM":  # Beginning of message
                reference = segment.get_element(1)
                if reference:
                    # Find related declaration
                    result = await self.db.execute(
                        select(CustomsDeclaration)
                        .where(CustomsDeclaration.declaration_number == reference)
                    )
                    declaration = result.scalar_one_or_none()
                    
                    if declaration:
                        edi_message.declaration_id = declaration.id
                        # Update declaration status based on response
                        await self._update_declaration_from_response(declaration, parsed)
    
    async def _process_job_response(self, edi_message: EDIMessage, parsed: ParsedEDIMessage):
        """Process job response message."""
        # Extract job reference and update status
        for segment in parsed.segments:
            if segment.tag == "RFF":  # Reference
                if segment.get_element(0) == "JOB":
                    job_reference = segment.get_element(1)
                    if job_reference:
                        result = await self.db.execute(
                            select(EDIJob)
                            .where(EDIJob.job_number == job_reference)
                        )
                        job = result.scalar_one_or_none()
                        
                        if job:
                            edi_message.job_id = job.id
                            await self._update_job_from_response(job, parsed)
    
    async def _process_cargo_report(self, edi_message: EDIMessage, parsed: ParsedEDIMessage):
        """Process cargo report message."""
        # Extract cargo information and create/update job
        consignment_ref = None
        vessel_voyage = None
        
        for segment in parsed.segments:
            if segment.tag == "RFF":
                if segment.get_element(0) == "CN":  # Consignment reference
                    consignment_ref = segment.get_element(1)
            elif segment.tag == "TDT":  # Transport details
                vessel_voyage = segment.get_element(2)
        
        if consignment_ref:
            # Find or create job
            result = await self.db.execute(
                select(EDIJob)
                .where(EDIJob.consignment_reference == consignment_ref)
            )
            job = result.scalar_one_or_none()
            
            if job:
                edi_message.job_id = job.id
                if vessel_voyage:
                    job.vessel_voyage = vessel_voyage
    
    async def _update_declaration_from_response(self, declaration: CustomsDeclaration, parsed: ParsedEDIMessage):
        """Update declaration status from customs response."""
        # Parse response status
        for segment in parsed.segments:
            if segment.tag == "STS":  # Status
                status_code = segment.get_element(0)
                if status_code == "1":  # Accepted
                    declaration.status = DeclarationStatus.ASSESSED
                    declaration.assessed_at = datetime.utcnow()
                elif status_code == "2":  # Rejected
                    declaration.status = DeclarationStatus.REJECTED
                elif status_code == "3":  # Cleared
                    declaration.status = DeclarationStatus.CLEARED
                    declaration.cleared_at = datetime.utcnow()
    
    async def _update_job_from_response(self, job: EDIJob, parsed: ParsedEDIMessage):
        """Update job status from job response."""
        for segment in parsed.segments:
            if segment.tag == "STS":  # Status
                status_code = segment.get_element(0)
                if status_code == "IP":  # In Progress
                    job.status = JobStatus.IN_PROGRESS
                elif status_code == "CL":  # Cleared
                    job.status = JobStatus.CLEARED
                    job.completed_at = datetime.utcnow()
                elif status_code == "OH":  # On Hold
                    job.status = JobStatus.ON_HOLD
    
    async def _generate_job_number(self) -> str:
        """Generate unique job number."""
        timestamp = datetime.utcnow().strftime('%Y%m%d')
        
        # Get count of jobs created today
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        result = await self.db.execute(
            select(EDIJob)
            .where(EDIJob.created_at >= today_start)
        )
        count = len(result.scalars().all()) + 1
        
        return f"JOB{timestamp}{count:04d}"
    
    async def _generate_declaration_number(self) -> str:
        """Generate unique declaration number."""
        timestamp = datetime.utcnow().strftime('%Y%m%d')
        
        # Get count of declarations created today
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        result = await self.db.execute(
            select(CustomsDeclaration)
            .where(CustomsDeclaration.created_at >= today_start)
        )
        count = len(result.scalars().all()) + 1
        
        return f"DEC{timestamp}{count:04d}"
    
    async def _send_job_registration_message(self, job: EDIJob):
        """Send job registration message to ABF."""
        # Generate JOBMAN message
        jobman_message = self._generate_jobman_message(job)
        
        # Create outbound EDI message
        message_id = f"JOBMAN_{job.job_number}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        edi_message = EDIMessage(
            message_id=message_id,
            message_type=EDIMessageType.JOBMAN,
            direction=EDIDirection.OUTBOUND,
            raw_message=jobman_message,
            status=EDIMessageStatus.PENDING,
            customer_id=job.customer_id,
            job_id=job.id
        )
        
        self.db.add(edi_message)
        await self.db.commit()
        
        # Send to ABF (simulated)
        await self._send_to_abf(edi_message)
    
    def _generate_jobman_message(self, job: EDIJob) -> str:
        """Generate JOBMAN EDIFACT message for job registration."""
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M')
        
        segments = [
            f"UNB+UNOC:3+SENDER+ABF+{timestamp}+{job.job_number}'",
            f"UNH+1+JOBMAN:D:03B:UN:EAN008'",
            f"BGM+JOB+{job.job_number}+9'",
            f"DTM+137:{timestamp}:203'",
            f"RFF+CN:{job.consignment_reference}'",
            f"NAD+CN+++{job.customer.company_name or job.customer.first_name + ' ' + job.customer.last_name}'",
            f"TDT+20+++++{job.port_of_discharge}'",
            f"FTX+AAI+++{job.cargo_description}'",
            "UNT+8+1'",
            f"UNZ+1+{job.job_number}'"
        ]
        
        return "".join(segments)
    
    async def _generate_cusdec_message(self, declaration: CustomsDeclaration) -> str:
        """Generate CUSDEC EDIFACT message for customs declaration."""
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M')
        
        segments = [
            f"UNB+UNOC:3+SENDER+ABF+{timestamp}+{declaration.declaration_number}'",
            f"UNH+1+CUSDEC:D:03B:UN:EAN008'",
            f"BGM+DEC+{declaration.declaration_number}+9'",
            f"DTM+137:{timestamp}:203'",
            f"RFF+CN:{declaration.consignment_reference}'",
            f"NAD+IM+++{declaration.importer_name}'",
            f"MOA+128:{declaration.total_invoice_value}:{declaration.currency}'",
        ]
        
        # Add declaration items
        for item in declaration.declaration_items:
            segments.extend([
                f"LIN+{item.item_number}++{item.hs_code}:HS'",
                f"IMD+F++:::{item.description}'",
                f"QTY+12:{item.quantity}:{item.unit_of_measure}'",
                f"MOA+203:{item.total_value}:{declaration.currency}'",
                f"PRI+INV:{item.unit_price}:{declaration.currency}'",
                f"LOC+17+{item.country_of_origin}'"
            ])
        
        segments.extend([
            f"UNT+{len(segments) + 2}+1'",
            f"UNZ+1+{declaration.declaration_number}'"
        ])
        
        return "".join(segments)
    
    async def _send_to_abf(self, edi_message: EDIMessage):
        """Send EDI message to ABF (simulated)."""
        # In a real implementation, this would send to ABF's EDI gateway
        # For now, we'll simulate successful transmission
        edi_message.status = EDIMessageStatus.ACKNOWLEDGED
        edi_message.acknowledged_at = datetime.utcnow()
        await self.db.commit()