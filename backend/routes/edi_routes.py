"""
EDI API routes for job registration, customs declarations, and message processing.

This module provides REST API endpoints for EDI operations including:
- Job registration and management
- Customs declaration creation and submission
- EDI message processing and status tracking
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc
from sqlalchemy.orm import selectinload
from pydantic import BaseModel, Field

from database import get_async_session
from services.edi_service import EDIService
from routes.customer_auth import get_current_customer
from models.customer import Customer
from models.edi import (
    EDIMessage, EDIJob, CustomsDeclaration, DeclarationItem,
    EDIMessageType, EDIMessageStatus, JobStatus, DeclarationType, DeclarationStatus
)

router = APIRouter(prefix="/api/edi", tags=["EDI Operations"])


# Pydantic models for request/response

class JobRegistrationRequest(BaseModel):
    """Request model for job registration."""
    job_type: str = Field(..., description="Type of job (import, export, transit)")
    consignment_reference: str = Field(..., description="Consignment reference number")
    cargo_description: str = Field(..., description="Description of cargo")
    port_of_discharge: str = Field(..., description="Port of discharge")
    estimated_arrival: Optional[datetime] = Field(None, description="Estimated arrival date")
    vessel_voyage: Optional[str] = Field(None, description="Vessel and voyage information")
    port_of_loading: Optional[str] = Field(None, description="Port of loading")
    total_packages: Optional[int] = Field(None, description="Total number of packages")
    total_weight_kg: Optional[str] = Field(None, description="Total weight in kg")
    total_value_aud: Optional[str] = Field(None, description="Total value in AUD")
    clearance_deadline: Optional[datetime] = Field(None, description="Clearance deadline")
    priority: str = Field("normal", description="Job priority (low, normal, high, urgent)")


class JobResponse(BaseModel):
    """Response model for job information."""
    id: int
    job_number: str
    job_type: str
    status: str
    consignment_reference: str
    cargo_description: str
    port_of_discharge: str
    estimated_arrival: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class DeclarationRequest(BaseModel):
    """Request model for customs declaration creation."""
    job_id: int = Field(..., description="Associated job ID")
    declaration_type: str = Field(..., description="Type of declaration")
    importer_name: str = Field(..., description="Name of importer")
    importer_abn: Optional[str] = Field(None, description="Importer ABN")
    exporter_name: Optional[str] = Field(None, description="Name of exporter")
    exporter_address: Optional[str] = Field(None, description="Exporter address")
    total_invoice_value: str = Field(..., description="Total invoice value")
    currency: str = Field("AUD", description="Currency code")
    vessel_name: Optional[str] = Field(None, description="Vessel name")
    voyage_number: Optional[str] = Field(None, description="Voyage number")
    port_of_loading: Optional[str] = Field(None, description="Port of loading")
    commercial_reference: Optional[str] = Field(None, description="Commercial reference")


class DeclarationItemRequest(BaseModel):
    """Request model for declaration item."""
    item_number: int = Field(..., description="Item sequence number")
    description: str = Field(..., description="Item description")
    hs_code: str = Field(..., description="HS code")
    country_of_origin: str = Field(..., description="Country of origin (ISO code)")
    quantity: str = Field(..., description="Quantity")
    unit_of_measure: str = Field(..., description="Unit of measure")
    unit_price: str = Field(..., description="Unit price")
    currency: str = Field("AUD", description="Currency code")
    net_weight_kg: Optional[str] = Field(None, description="Net weight in kg")
    gross_weight_kg: Optional[str] = Field(None, description="Gross weight in kg")
    brand: Optional[str] = Field(None, description="Brand name")
    model: Optional[str] = Field(None, description="Model")
    serial_number: Optional[str] = Field(None, description="Serial number")


class DeclarationResponse(BaseModel):
    """Response model for declaration information."""
    id: int
    declaration_number: str
    declaration_type: str
    status: str
    job_id: int
    consignment_reference: str
    importer_name: str
    total_invoice_value: str
    currency: str
    submitted_at: Optional[datetime]
    created_at: datetime


class EDIMessageResponse(BaseModel):
    """Response model for EDI message information."""
    id: int
    message_id: str
    message_type: str
    direction: str
    status: str
    received_at: datetime
    processed_at: Optional[datetime]
    error_message: Optional[str]


class JobStatusResponse(BaseModel):
    """Response model for comprehensive job status."""
    job: JobResponse
    messages: List[EDIMessageResponse]
    declarations: List[DeclarationResponse]


# API Endpoints

@router.post("/jobs/register", response_model=JobResponse)
async def register_job(
    request: JobRegistrationRequest,
    current_customer: Customer = Depends(get_current_customer),
    db: AsyncSession = Depends(get_async_session)
):
    """Register a new customs clearance job."""
    try:
        edi_service = EDIService(db)
        
        job = await edi_service.register_job(
            customer_id=current_customer.id,
            job_type=request.job_type,
            consignment_reference=request.consignment_reference,
            cargo_description=request.cargo_description,
            port_of_discharge=request.port_of_discharge,
            estimated_arrival=request.estimated_arrival,
            vessel_voyage=request.vessel_voyage,
            port_of_loading=request.port_of_loading,
            total_packages=request.total_packages,
            total_weight_kg=request.total_weight_kg,
            total_value_aud=request.total_value_aud,
            clearance_deadline=request.clearance_deadline,
            priority=request.priority
        )
        
        return JobResponse(
            id=job.id,
            job_number=job.job_number,
            job_type=job.job_type,
            status=job.status,
            consignment_reference=job.consignment_reference,
            cargo_description=job.cargo_description,
            port_of_discharge=job.port_of_discharge,
            estimated_arrival=job.estimated_arrival,
            created_at=job.created_at,
            updated_at=job.updated_at
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to register job: {str(e)}"
        )


@router.get("/jobs", response_model=List[JobResponse])
async def get_customer_jobs(
    status_filter: Optional[str] = Query(None, description="Filter by job status"),
    limit: int = Query(50, description="Maximum number of jobs to return"),
    offset: int = Query(0, description="Number of jobs to skip"),
    current_customer: Customer = Depends(get_current_customer),
    db: AsyncSession = Depends(get_async_session)
):
    """Get customer's jobs with optional filtering."""
    try:
        query = select(EDIJob).where(EDIJob.customer_id == current_customer.id)
        
        if status_filter:
            query = query.where(EDIJob.status == status_filter)
        
        query = query.order_by(desc(EDIJob.created_at)).limit(limit).offset(offset)
        
        result = await db.execute(query)
        jobs = result.scalars().all()
        
        return [
            JobResponse(
                id=job.id,
                job_number=job.job_number,
                job_type=job.job_type,
                status=job.status,
                consignment_reference=job.consignment_reference,
                cargo_description=job.cargo_description,
                port_of_discharge=job.port_of_discharge,
                estimated_arrival=job.estimated_arrival,
                created_at=job.created_at,
                updated_at=job.updated_at
            )
            for job in jobs
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve jobs: {str(e)}"
        )


@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(
    job_id: int,
    current_customer: Customer = Depends(get_current_customer),
    db: AsyncSession = Depends(get_async_session)
):
    """Get comprehensive job status including messages and declarations."""
    try:
        edi_service = EDIService(db)
        
        # Verify job belongs to customer
        job = await db.get(EDIJob, job_id)
        if not job or job.customer_id != current_customer.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )
        
        job_status = await edi_service.get_job_status(job_id)
        
        return JobStatusResponse(
            job=JobResponse(**job_status["job"]),
            messages=[EDIMessageResponse(**msg) for msg in job_status["messages"]],
            declarations=[DeclarationResponse(**decl) for decl in job_status["declarations"]]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve job status: {str(e)}"
        )


@router.post("/declarations", response_model=DeclarationResponse)
async def create_declaration(
    request: DeclarationRequest,
    current_customer: Customer = Depends(get_current_customer),
    db: AsyncSession = Depends(get_async_session)
):
    """Create a new customs declaration."""
    try:
        # Verify job belongs to customer
        job = await db.get(EDIJob, request.job_id)
        if not job or job.customer_id != current_customer.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )
        
        edi_service = EDIService(db)
        
        declaration = await edi_service.create_declaration(
            job_id=request.job_id,
            declaration_type=DeclarationType(request.declaration_type),
            importer_name=request.importer_name,
            total_invoice_value=request.total_invoice_value,
            currency=request.currency,
            importer_abn=request.importer_abn,
            exporter_name=request.exporter_name,
            exporter_address=request.exporter_address,
            vessel_name=request.vessel_name,
            voyage_number=request.voyage_number,
            port_of_loading=request.port_of_loading,
            commercial_reference=request.commercial_reference
        )
        
        return DeclarationResponse(
            id=declaration.id,
            declaration_number=declaration.declaration_number,
            declaration_type=declaration.declaration_type,
            status=declaration.status,
            job_id=declaration.job_id,
            consignment_reference=declaration.consignment_reference,
            importer_name=declaration.importer_name,
            total_invoice_value=declaration.total_invoice_value,
            currency=declaration.currency,
            submitted_at=declaration.submitted_at,
            created_at=declaration.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create declaration: {str(e)}"
        )


@router.post("/declarations/{declaration_id}/items")
async def add_declaration_item(
    declaration_id: int,
    request: DeclarationItemRequest,
    current_customer: Customer = Depends(get_current_customer),
    db: AsyncSession = Depends(get_async_session)
):
    """Add an item to a customs declaration."""
    try:
        # Verify declaration belongs to customer
        result = await db.execute(
            select(CustomsDeclaration)
            .join(EDIJob)
            .where(
                and_(
                    CustomsDeclaration.id == declaration_id,
                    EDIJob.customer_id == current_customer.id
                )
            )
        )
        declaration = result.scalar_one_or_none()
        
        if not declaration:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Declaration not found"
            )
        
        if declaration.status != DeclarationStatus.DRAFT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot modify submitted declaration"
            )
        
        edi_service = EDIService(db)
        
        item = await edi_service.add_declaration_item(
            declaration_id=declaration_id,
            item_number=request.item_number,
            description=request.description,
            hs_code=request.hs_code,
            quantity=request.quantity,
            unit_price=request.unit_price,
            country_of_origin=request.country_of_origin,
            unit_of_measure=request.unit_of_measure,
            currency=request.currency,
            net_weight_kg=request.net_weight_kg,
            gross_weight_kg=request.gross_weight_kg,
            brand=request.brand,
            model=request.model,
            serial_number=request.serial_number
        )
        
        return {"message": "Item added successfully", "item_id": item.id}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to add declaration item: {str(e)}"
        )


@router.post("/declarations/{declaration_id}/submit")
async def submit_declaration(
    declaration_id: int,
    current_customer: Customer = Depends(get_current_customer),
    db: AsyncSession = Depends(get_async_session)
):
    """Submit a customs declaration to ABF."""
    try:
        # Verify declaration belongs to customer
        result = await db.execute(
            select(CustomsDeclaration)
            .join(EDIJob)
            .where(
                and_(
                    CustomsDeclaration.id == declaration_id,
                    EDIJob.customer_id == current_customer.id
                )
            )
        )
        declaration = result.scalar_one_or_none()
        
        if not declaration:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Declaration not found"
            )
        
        edi_service = EDIService(db)
        
        edi_message = await edi_service.submit_declaration(declaration_id)
        
        return {
            "message": "Declaration submitted successfully",
            "declaration_number": declaration.declaration_number,
            "edi_message_id": edi_message.message_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to submit declaration: {str(e)}"
        )


@router.get("/declarations", response_model=List[DeclarationResponse])
async def get_customer_declarations(
    status_filter: Optional[str] = Query(None, description="Filter by declaration status"),
    job_id: Optional[int] = Query(None, description="Filter by job ID"),
    limit: int = Query(50, description="Maximum number of declarations to return"),
    offset: int = Query(0, description="Number of declarations to skip"),
    current_customer: Customer = Depends(get_current_customer),
    db: AsyncSession = Depends(get_async_session)
):
    """Get customer's declarations with optional filtering."""
    try:
        query = (
            select(CustomsDeclaration)
            .join(EDIJob)
            .where(EDIJob.customer_id == current_customer.id)
        )
        
        if status_filter:
            query = query.where(CustomsDeclaration.status == status_filter)
        
        if job_id:
            query = query.where(CustomsDeclaration.job_id == job_id)
        
        query = query.order_by(desc(CustomsDeclaration.created_at)).limit(limit).offset(offset)
        
        result = await db.execute(query)
        declarations = result.scalars().all()
        
        return [
            DeclarationResponse(
                id=decl.id,
                declaration_number=decl.declaration_number,
                declaration_type=decl.declaration_type,
                status=decl.status,
                job_id=decl.job_id,
                consignment_reference=decl.consignment_reference,
                importer_name=decl.importer_name,
                total_invoice_value=decl.total_invoice_value,
                currency=decl.currency,
                submitted_at=decl.submitted_at,
                created_at=decl.created_at
            )
            for decl in declarations
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve declarations: {str(e)}"
        )


@router.get("/declarations/{declaration_id}")
async def get_declaration_details(
    declaration_id: int,
    current_customer: Customer = Depends(get_current_customer),
    db: AsyncSession = Depends(get_async_session)
):
    """Get detailed declaration information including items."""
    try:
        # Get declaration with items
        result = await db.execute(
            select(CustomsDeclaration)
            .options(selectinload(CustomsDeclaration.declaration_items))
            .join(EDIJob)
            .where(
                and_(
                    CustomsDeclaration.id == declaration_id,
                    EDIJob.customer_id == current_customer.id
                )
            )
        )
        declaration = result.scalar_one_or_none()
        
        if not declaration:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Declaration not found"
            )
        
        return {
            "declaration": {
                "id": declaration.id,
                "declaration_number": declaration.declaration_number,
                "declaration_type": declaration.declaration_type,
                "status": declaration.status,
                "job_id": declaration.job_id,
                "consignment_reference": declaration.consignment_reference,
                "importer_name": declaration.importer_name,
                "importer_abn": declaration.importer_abn,
                "exporter_name": declaration.exporter_name,
                "total_invoice_value": declaration.total_invoice_value,
                "currency": declaration.currency,
                "vessel_name": declaration.vessel_name,
                "voyage_number": declaration.voyage_number,
                "port_of_loading": declaration.port_of_loading,
                "port_of_discharge": declaration.port_of_discharge,
                "submitted_at": declaration.submitted_at,
                "assessed_at": declaration.assessed_at,
                "cleared_at": declaration.cleared_at,
                "created_at": declaration.created_at
            },
            "items": [
                {
                    "id": item.id,
                    "item_number": item.item_number,
                    "description": item.description,
                    "hs_code": item.hs_code,
                    "country_of_origin": item.country_of_origin,
                    "quantity": item.quantity,
                    "unit_of_measure": item.unit_of_measure,
                    "unit_price": item.unit_price,
                    "total_value": item.total_value,
                    "currency": item.currency,
                    "net_weight_kg": item.net_weight_kg,
                    "gross_weight_kg": item.gross_weight_kg,
                    "duty_rate": item.duty_rate,
                    "duty_amount": item.duty_amount,
                    "gst_amount": item.gst_amount,
                    "brand": item.brand,
                    "model": item.model,
                    "serial_number": item.serial_number,
                    "is_examined": item.is_examined,
                    "examination_notes": item.examination_notes
                }
                for item in declaration.declaration_items
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve declaration details: {str(e)}"
        )


@router.get("/messages", response_model=List[EDIMessageResponse])
async def get_customer_messages(
    message_type: Optional[str] = Query(None, description="Filter by message type"),
    status_filter: Optional[str] = Query(None, description="Filter by message status"),
    job_id: Optional[int] = Query(None, description="Filter by job ID"),
    limit: int = Query(50, description="Maximum number of messages to return"),
    offset: int = Query(0, description="Number of messages to skip"),
    current_customer: Customer = Depends(get_current_customer),
    db: AsyncSession = Depends(get_async_session)
):
    """Get customer's EDI messages with optional filtering."""
    try:
        query = select(EDIMessage).where(EDIMessage.customer_id == current_customer.id)
        
        if message_type:
            query = query.where(EDIMessage.message_type == message_type)
        
        if status_filter:
            query = query.where(EDIMessage.status == status_filter)
        
        if job_id:
            query = query.where(EDIMessage.job_id == job_id)
        
        query = query.order_by(desc(EDIMessage.received_at)).limit(limit).offset(offset)
        
        result = await db.execute(query)
        messages = result.scalars().all()
        
        return [
            EDIMessageResponse(
                id=msg.id,
                message_id=msg.message_id,
                message_type=msg.message_type,
                direction=msg.direction,
                status=msg.status,
                received_at=msg.received_at,
                processed_at=msg.processed_at,
                error_message=msg.error_message
            )
            for msg in messages
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve messages: {str(e)}"
        )


@router.post("/messages/process")
async def process_inbound_message(
    raw_message: str = Body(..., description="Raw EDI message content"),
    external_reference: Optional[str] = Body(None, description="External reference"),
    db: AsyncSession = Depends(get_async_session)
):
    """Process an inbound EDI message (admin endpoint)."""
    try:
        edi_service = EDIService(db)
        
        edi_message = await edi_service.process_inbound_message(
            raw_message=raw_message,
            external_reference=external_reference
        )
        
        return {
            "message": "EDI message processed successfully",
            "message_id": edi_message.message_id,
            "status": edi_message.status
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to process EDI message: {str(e)}"
        )