from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload

from models.digital_loa import (
    DigitalLetterOfAuthority, LOASignature, LOAAuditLog, LOATemplate,
    LOAStatus, SignatureMethod
)
from models.customer import Customer
from services.digital_signature_service import DigitalSignatureService, LOAPDFGenerator
import secrets
import json

class LOAService:
    """
    Service for managing Digital Letters of Authority.
    Handles creation, signing, verification, and lifecycle management.
    """
    
    def __init__(self):
        self.signature_service = DigitalSignatureService()
        self.pdf_generator = LOAPDFGenerator()
    
    async def create_loa(
        self,
        db: AsyncSession,
        customer_id: int,
        loa_data: Dict[str, Any]
    ) -> DigitalLetterOfAuthority:
        """Create a new Letter of Authority."""
        
        # Generate unique LOA number
        loa_number = await self._generate_loa_number(db)
        
        # Create LOA instance
        loa = DigitalLetterOfAuthority(
            customer_id=customer_id,
            loa_number=loa_number,
            reference_number=loa_data.get('reference_number'),
            company_name=loa_data['company_name'],
            company_abn=loa_data['company_abn'],
            company_address=loa_data['company_address'],
            authorized_person_name=loa_data['authorized_person_name'],
            authorized_person_title=loa_data['authorized_person_title'],
            authorized_person_email=loa_data['authorized_person_email'],
            authorized_person_phone=loa_data.get('authorized_person_phone'),
            authority_scope=loa_data['authority_scope'],
            customs_broker_license=loa_data['customs_broker_license'],
            loa_content=loa_data['loa_content'],
            terms_and_conditions=loa_data.get('terms_and_conditions'),
            special_instructions=loa_data.get('special_instructions'),
            signature_method=loa_data.get('signature_method', SignatureMethod.ELECTRONIC_SIGNATURE),
            status=LOAStatus.DRAFT,
            verification_code=self.signature_service.generate_verification_code(),
            effective_date=loa_data.get('effective_date'),
            expiry_date=loa_data.get('expiry_date'),
            metadata=loa_data.get('metadata', {})
        )
        
        db.add(loa)
        await db.flush()  # Get the ID
        
        # Create audit log
        await self._create_audit_log(
            db, loa.id, "created", "customer", str(customer_id),
            loa_data['authorized_person_name'], "LOA created",
            metadata={"initial_data": loa_data}
        )
        
        await db.commit()
        return loa
    
    async def get_loa_by_id(
        self,
        db: AsyncSession,
        loa_id: int,
        customer_id: Optional[int] = None
    ) -> Optional[DigitalLetterOfAuthority]:
        """Get LOA by ID, optionally filtered by customer."""
        query = select(DigitalLetterOfAuthority).options(
            selectinload(DigitalLetterOfAuthority.customer),
            selectinload(DigitalLetterOfAuthority.signatures),
            selectinload(DigitalLetterOfAuthority.audit_logs)
        ).where(DigitalLetterOfAuthority.id == loa_id)
        
        if customer_id:
            query = query.where(DigitalLetterOfAuthority.customer_id == customer_id)
        
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_loa_by_number(
        self,
        db: AsyncSession,
        loa_number: str
    ) -> Optional[DigitalLetterOfAuthority]:
        """Get LOA by LOA number."""
        query = select(DigitalLetterOfAuthority).options(
            selectinload(DigitalLetterOfAuthority.customer),
            selectinload(DigitalLetterOfAuthority.signatures)
        ).where(DigitalLetterOfAuthority.loa_number == loa_number)
        
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_customer_loas(
        self,
        db: AsyncSession,
        customer_id: int,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[DigitalLetterOfAuthority]:
        """Get LOAs for a customer."""
        query = select(DigitalLetterOfAuthority).options(
            selectinload(DigitalLetterOfAuthority.signatures)
        ).where(DigitalLetterOfAuthority.customer_id == customer_id)
        
        if status:
            query = query.where(DigitalLetterOfAuthority.status == status)
        
        query = query.order_by(DigitalLetterOfAuthority.created_at.desc())
        query = query.offset(offset).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def update_loa(
        self,
        db: AsyncSession,
        loa_id: int,
        customer_id: int,
        update_data: Dict[str, Any],
        actor_name: str
    ) -> Optional[DigitalLetterOfAuthority]:
        """Update LOA (only if in draft status)."""
        loa = await self.get_loa_by_id(db, loa_id, customer_id)
        if not loa or loa.status != LOAStatus.DRAFT:
            return None
        
        # Track changes for audit
        changes = {}
        for field, new_value in update_data.items():
            if hasattr(loa, field):
                old_value = getattr(loa, field)
                if old_value != new_value:
                    changes[field] = {"old": old_value, "new": new_value}
                    setattr(loa, field, new_value)
        
        if changes:
            # Create audit logs for changes
            for field, change in changes.items():
                await self._create_audit_log(
                    db, loa.id, "updated", "customer", str(customer_id),
                    actor_name, f"Updated {field}",
                    field_changed=field,
                    old_value=str(change["old"]),
                    new_value=str(change["new"])
                )
            
            await db.commit()
        
        return loa
    
    async def sign_loa(
        self,
        db: AsyncSession,
        loa_id: int,
        customer_id: int,
        signature_data: Dict[str, Any],
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Optional[DigitalLetterOfAuthority]:
        """Sign the LOA."""
        loa = await self.get_loa_by_id(db, loa_id, customer_id)
        if not loa or loa.status not in [LOAStatus.DRAFT, LOAStatus.PENDING_SIGNATURE]:
            return None
        
        # Generate signature image
        signature_image = self.signature_service.generate_signature_image(
            loa.authorized_person_name,
            f"Digitally signed on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        # Create document hash
        document_content = self._create_document_content_for_hash(loa)
        document_hash = self.signature_service.create_document_hash(document_content)
        
        # Sign the document hash
        digital_signature = self.signature_service.sign_document_hash(document_hash)
        
        # Get certificate info
        cert_info = self.signature_service.get_certificate_info()
        
        # Update LOA with signature information
        loa.signature_data = signature_image
        loa.signature_timestamp = datetime.utcnow()
        loa.signature_ip_address = ip_address
        loa.signature_user_agent = user_agent
        loa.document_hash = document_hash
        loa.signature_certificate = digital_signature
        loa.status = LOAStatus.SIGNED
        loa.signed_at = datetime.utcnow()
        
        # Create signature record
        signature_record = LOASignature(
            loa_id=loa.id,
            signatory_name=loa.authorized_person_name,
            signatory_email=loa.authorized_person_email,
            signatory_role=loa.authorized_person_title,
            signature_method=loa.signature_method,
            signature_data=signature_image,
            signature_hash=self.signature_service.create_document_hash(signature_image),
            certificate_serial=cert_info["serial_number"],
            certificate_issuer=cert_info["issuer"],
            certificate_subject=cert_info["subject"],
            certificate_valid_from=datetime.fromisoformat(cert_info["valid_from"].replace('Z', '+00:00')),
            certificate_valid_to=datetime.fromisoformat(cert_info["valid_to"].replace('Z', '+00:00')),
            ip_address=ip_address,
            user_agent=user_agent,
            verification_status="verified"
        )
        
        db.add(signature_record)
        
        # Generate PDF
        try:
            pdf_path = self.pdf_generator.generate_loa_pdf(
                self._loa_to_dict(loa),
                signature_image
            )
            loa.signed_pdf_path = pdf_path
        except Exception as e:
            # Log error but don't fail the signing process
            print(f"PDF generation failed: {e}")
        
        # Create audit log
        await self._create_audit_log(
            db, loa.id, "signed", "customer", str(customer_id),
            loa.authorized_person_name, "LOA digitally signed",
            metadata={
                "signature_method": loa.signature_method,
                "ip_address": ip_address,
                "certificate_serial": cert_info["serial_number"]
            }
        )
        
        await db.commit()
        return loa
    
    async def activate_loa(
        self,
        db: AsyncSession,
        loa_id: int,
        admin_user: str
    ) -> Optional[DigitalLetterOfAuthority]:
        """Activate a signed LOA (admin function)."""
        loa = await self.get_loa_by_id(db, loa_id)
        if not loa or loa.status != LOAStatus.SIGNED:
            return None
        
        loa.status = LOAStatus.ACTIVE
        loa.is_active = True
        loa.activated_at = datetime.utcnow()
        
        # Set effective date if not already set
        if not loa.effective_date:
            loa.effective_date = datetime.utcnow()
        
        # Create audit log
        await self._create_audit_log(
            db, loa.id, "activated", "admin", admin_user,
            admin_user, "LOA activated by administrator"
        )
        
        await db.commit()
        return loa
    
    async def revoke_loa(
        self,
        db: AsyncSession,
        loa_id: int,
        reason: str,
        revoked_by: str,
        actor_type: str = "admin"
    ) -> Optional[DigitalLetterOfAuthority]:
        """Revoke an active LOA."""
        loa = await self.get_loa_by_id(db, loa_id)
        if not loa or loa.status not in [LOAStatus.ACTIVE, LOAStatus.SIGNED]:
            return None
        
        loa.status = LOAStatus.REVOKED
        loa.is_active = False
        loa.revoked_at = datetime.utcnow()
        loa.revocation_reason = reason
        loa.revoked_by = revoked_by
        
        # Create audit log
        await self._create_audit_log(
            db, loa.id, "revoked", actor_type, revoked_by,
            revoked_by, f"LOA revoked: {reason}"
        )
        
        await db.commit()
        return loa
    
    async def verify_loa(
        self,
        db: AsyncSession,
        loa_number: str,
        verification_code: str
    ) -> Dict[str, Any]:
        """Verify LOA authenticity."""
        loa = await self.get_loa_by_number(db, loa_number)
        
        if not loa:
            return {"valid": False, "error": "LOA not found"}
        
        if loa.verification_code != verification_code:
            return {"valid": False, "error": "Invalid verification code"}
        
        # Verify digital signature if present
        signature_valid = False
        if loa.document_hash and loa.signature_certificate:
            signature_valid = self.signature_service.verify_signature(
                loa.document_hash, loa.signature_certificate
            )
        
        return {
            "valid": True,
            "loa_number": loa.loa_number,
            "company_name": loa.company_name,
            "company_abn": loa.company_abn,
            "authorized_person": loa.authorized_person_name,
            "status": loa.status,
            "is_active": loa.is_active,
            "signed_at": loa.signed_at.isoformat() if loa.signed_at else None,
            "effective_date": loa.effective_date.isoformat() if loa.effective_date else None,
            "expiry_date": loa.expiry_date.isoformat() if loa.expiry_date else None,
            "signature_valid": signature_valid,
            "revoked": loa.status == LOAStatus.REVOKED,
            "revocation_reason": loa.revocation_reason if loa.status == LOAStatus.REVOKED else None
        }
    
    async def _generate_loa_number(self, db: AsyncSession) -> str:
        """Generate unique LOA number."""
        while True:
            # Format: LOA-YYYY-NNNNNN
            year = datetime.now().year
            random_part = secrets.randbelow(999999)
            loa_number = f"LOA-{year}-{random_part:06d}"
            
            # Check if already exists
            existing = await db.execute(
                select(DigitalLetterOfAuthority).where(
                    DigitalLetterOfAuthority.loa_number == loa_number
                )
            )
            if not existing.scalar_one_or_none():
                return loa_number
    
    async def _create_audit_log(
        self,
        db: AsyncSession,
        loa_id: int,
        action: str,
        actor_type: str,
        actor_id: str,
        actor_name: str,
        description: str,
        field_changed: Optional[str] = None,
        old_value: Optional[str] = None,
        new_value: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Create audit log entry."""
        audit_log = LOAAuditLog(
            loa_id=loa_id,
            action=action,
            actor_type=actor_type,
            actor_id=actor_id,
            actor_name=actor_name,
            field_changed=field_changed,
            old_value=old_value,
            new_value=new_value,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata=metadata
        )
        db.add(audit_log)
    
    def _create_document_content_for_hash(self, loa: DigitalLetterOfAuthority) -> str:
        """Create standardized document content for hashing."""
        content_parts = [
            f"LOA_NUMBER:{loa.loa_number}",
            f"COMPANY_NAME:{loa.company_name}",
            f"COMPANY_ABN:{loa.company_abn}",
            f"AUTHORIZED_PERSON:{loa.authorized_person_name}",
            f"AUTHORIZED_EMAIL:{loa.authorized_person_email}",
            f"AUTHORITY_SCOPE:{loa.authority_scope}",
            f"LOA_CONTENT:{loa.loa_content}",
            f"CUSTOMS_BROKER_LICENSE:{loa.customs_broker_license}",
            f"EFFECTIVE_DATE:{loa.effective_date.isoformat() if loa.effective_date else 'None'}",
            f"EXPIRY_DATE:{loa.expiry_date.isoformat() if loa.expiry_date else 'None'}"
        ]
        return "|".join(content_parts)
    
    def _loa_to_dict(self, loa: DigitalLetterOfAuthority) -> Dict[str, Any]:
        """Convert LOA to dictionary for PDF generation."""
        return {
            "loa_number": loa.loa_number,
            "reference_number": loa.reference_number,
            "company_name": loa.company_name,
            "company_abn": loa.company_abn,
            "company_address": loa.company_address,
            "authorized_person_name": loa.authorized_person_name,
            "authorized_person_title": loa.authorized_person_title,
            "authorized_person_email": loa.authorized_person_email,
            "authorized_person_phone": loa.authorized_person_phone,
            "authority_scope": loa.authority_scope,
            "customs_broker_license": loa.customs_broker_license,
            "loa_content": loa.loa_content,
            "terms_and_conditions": loa.terms_and_conditions,
            "special_instructions": loa.special_instructions,
            "verification_code": loa.verification_code,
            "effective_date": loa.effective_date,
            "expiry_date": loa.expiry_date
        }

class LOATemplateService:
    """Service for managing LOA templates."""
    
    async def get_default_template(self, db: AsyncSession) -> Optional[LOATemplate]:
        """Get the default LOA template."""
        query = select(LOATemplate).where(
            and_(LOATemplate.is_active == True, LOATemplate.is_default == True)
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_template_by_code(self, db: AsyncSession, template_code: str) -> Optional[LOATemplate]:
        """Get template by code."""
        query = select(LOATemplate).where(
            and_(LOATemplate.template_code == template_code, LOATemplate.is_active == True)
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    def get_default_loa_content(self) -> str:
        """Get default LOA content based on Australian customs requirements."""
        return """
I/We, {company_name} (ABN: {company_abn}), hereby authorize and appoint the licensed customs broker identified below to act as our agent for all matters relating to the importation and customs clearance of goods on our behalf.

This Letter of Authority is granted under Section 181 of the Customs Act 1901 and authorizes the customs broker to:

1. Lodge import declarations and other customs documents
2. Pay duties, taxes, and charges on our behalf
3. Receive goods from customs control
4. Represent us in all dealings with the Australian Border Force
5. Sign documents and make declarations as our authorized agent

CUSTOMS BROKER DETAILS:
License Number: {customs_broker_license}

This authority shall remain in effect until revoked in writing or until the expiry date specified below.

AUTHORIZED REPRESENTATIVE:
Name: {authorized_person_name}
Title: {authorized_person_title}
Email: {authorized_person_email}

By signing this Letter of Authority, I confirm that I am authorized to bind the company and that all information provided is true and correct.
        """.strip()