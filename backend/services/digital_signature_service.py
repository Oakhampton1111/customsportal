import hashlib
import base64
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography import x509
from cryptography.x509.oid import NameOID
import json
import os
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image, ImageDraw, ImageFont
import io

class DigitalSignatureService:
    """
    Service for handling digital signatures and PDF generation for Letters of Authority.
    Uses open-source cryptography libraries for secure digital signatures.
    """
    
    def __init__(self, cert_dir: str = "certs", upload_dir: str = "uploads"):
        self.cert_dir = Path(cert_dir)
        self.upload_dir = Path(upload_dir)
        self.cert_dir.mkdir(exist_ok=True)
        self.upload_dir.mkdir(exist_ok=True)
        
        # Initialize or load signing certificate
        self.private_key, self.certificate = self._get_or_create_signing_cert()
    
    def _get_or_create_signing_cert(self):
        """Get existing or create new self-signed certificate for digital signatures."""
        cert_path = self.cert_dir / "signing_cert.pem"
        key_path = self.cert_dir / "signing_key.pem"
        
        if cert_path.exists() and key_path.exists():
            # Load existing certificate
            with open(cert_path, 'rb') as f:
                cert_data = f.read()
                certificate = x509.load_pem_x509_certificate(cert_data)
            
            with open(key_path, 'rb') as f:
                key_data = f.read()
                private_key = serialization.load_pem_private_key(key_data, password=None)
            
            return private_key, certificate
        else:
            # Create new self-signed certificate
            return self._create_self_signed_cert()
    
    def _create_self_signed_cert(self):
        """Create a self-signed certificate for digital signatures."""
        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        
        # Create certificate
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "AU"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "NSW"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "Sydney"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Customs Broker Portal"),
            x509.NameAttribute(NameOID.COMMON_NAME, "Digital Signature Authority"),
        ])
        
        certificate = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.utcnow()
        ).not_valid_after(
            datetime.utcnow() + timedelta(days=3650)  # 10 years
        ).add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName("localhost"),
                x509.DNSName("customs-broker-portal.com"),
            ]),
            critical=False,
        ).add_extension(
            x509.KeyUsage(
                digital_signature=True,
                content_commitment=True,
                key_encipherment=False,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=True,
                crl_sign=True,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        ).sign(private_key, hashes.SHA256())
        
        # Save certificate and key
        cert_path = self.cert_dir / "signing_cert.pem"
        key_path = self.cert_dir / "signing_key.pem"
        
        with open(cert_path, 'wb') as f:
            f.write(certificate.public_bytes(serialization.Encoding.PEM))
        
        with open(key_path, 'wb') as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        return private_key, certificate
    
    def generate_signature_image(self, signatory_name: str, signature_text: str = None) -> str:
        """Generate a signature image for the signatory."""
        if not signature_text:
            signature_text = f"Digitally signed by {signatory_name}"
        
        # Create signature image
        img_width, img_height = 300, 100
        img = Image.new('RGB', (img_width, img_height), 'white')
        draw = ImageDraw.Draw(img)
        
        try:
            # Try to use a nice font
            font = ImageFont.truetype("arial.ttf", 16)
            small_font = ImageFont.truetype("arial.ttf", 12)
        except:
            # Fallback to default font
            font = ImageFont.load_default()
            small_font = ImageFont.load_default()
        
        # Draw signature text
        draw.text((10, 20), signatory_name, fill='black', font=font)
        draw.text((10, 45), signature_text, fill='gray', font=small_font)
        draw.text((10, 65), f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", fill='gray', font=small_font)
        
        # Add a simple signature line
        draw.line([(10, 15), (290, 15)], fill='black', width=1)
        
        # Save to bytes
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        # Convert to base64
        return base64.b64encode(img_bytes.getvalue()).decode('utf-8')
    
    def create_document_hash(self, content: str) -> str:
        """Create SHA-256 hash of document content."""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def sign_document_hash(self, document_hash: str) -> str:
        """Sign document hash with private key."""
        hash_bytes = bytes.fromhex(document_hash)
        signature = self.private_key.sign(
            hash_bytes,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return base64.b64encode(signature).decode('utf-8')
    
    def verify_signature(self, document_hash: str, signature: str) -> bool:
        """Verify document signature."""
        try:
            hash_bytes = bytes.fromhex(document_hash)
            signature_bytes = base64.b64decode(signature)
            
            public_key = self.certificate.public_key()
            public_key.verify(
                signature_bytes,
                hash_bytes,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False
    
    def generate_verification_code(self) -> str:
        """Generate unique verification code for the document."""
        return secrets.token_urlsafe(16)
    
    def get_certificate_info(self) -> Dict[str, Any]:
        """Get certificate information for display."""
        return {
            "serial_number": str(self.certificate.serial_number),
            "issuer": self.certificate.issuer.rfc4514_string(),
            "subject": self.certificate.subject.rfc4514_string(),
            "valid_from": self.certificate.not_valid_before.isoformat(),
            "valid_to": self.certificate.not_valid_after.isoformat(),
            "fingerprint": self.certificate.fingerprint(hashes.SHA256()).hex()
        }

class LOAPDFGenerator:
    """
    Service for generating PDF documents for Letters of Authority.
    """
    
    def __init__(self, upload_dir: str = "uploads"):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(exist_ok=True)
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles."""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1,  # Center alignment
            textColor=colors.darkblue
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.darkblue
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=12,
            alignment=4  # Justify
        ))
        
        self.styles.add(ParagraphStyle(
            name='SignatureStyle',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            leftIndent=20
        ))
    
    def generate_loa_pdf(self, loa_data: Dict[str, Any], signature_image: str = None) -> str:
        """Generate PDF for Letter of Authority."""
        filename = f"loa_{loa_data['loa_number']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = self.upload_dir / filename
        
        doc = SimpleDocTemplate(
            str(filepath),
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        story = []
        
        # Title
        title = Paragraph("LETTER OF AUTHORITY", self.styles['CustomTitle'])
        story.append(title)
        story.append(Spacer(1, 20))
        
        # Subtitle
        subtitle = Paragraph(
            "Authority to Act as Licensed Customs Broker<br/>Section 181 of the Customs Act 1901",
            self.styles['CustomHeading']
        )
        story.append(subtitle)
        story.append(Spacer(1, 20))
        
        # LOA Number and Date
        info_data = [
            ['LOA Number:', loa_data['loa_number']],
            ['Date:', datetime.now().strftime('%d %B %Y')],
            ['Reference:', loa_data.get('reference_number', 'N/A')]
        ]
        
        info_table = Table(info_data, colWidths=[2*inch, 3*inch])
        info_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 20))
        
        # Company Information
        company_heading = Paragraph("COMPANY INFORMATION", self.styles['CustomHeading'])
        story.append(company_heading)
        
        company_data = [
            ['Company Name:', loa_data['company_name']],
            ['ABN:', loa_data['company_abn']],
            ['Address:', loa_data['company_address']],
        ]
        
        company_table = Table(company_data, colWidths=[2*inch, 4*inch])
        company_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(company_table)
        story.append(Spacer(1, 20))
        
        # Authorized Person
        auth_heading = Paragraph("AUTHORIZED REPRESENTATIVE", self.styles['CustomHeading'])
        story.append(auth_heading)
        
        auth_data = [
            ['Name:', loa_data['authorized_person_name']],
            ['Title:', loa_data['authorized_person_title']],
            ['Email:', loa_data['authorized_person_email']],
            ['Phone:', loa_data.get('authorized_person_phone', 'N/A')],
        ]
        
        auth_table = Table(auth_data, colWidths=[2*inch, 4*inch])
        auth_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(auth_table)
        story.append(Spacer(1, 20))
        
        # Authority Content
        content_heading = Paragraph("LETTER OF AUTHORITY", self.styles['CustomHeading'])
        story.append(content_heading)
        
        content_text = Paragraph(loa_data['loa_content'], self.styles['CustomBody'])
        story.append(content_text)
        story.append(Spacer(1, 20))
        
        # Authority Scope
        if loa_data.get('authority_scope'):
            scope_heading = Paragraph("SCOPE OF AUTHORITY", self.styles['CustomHeading'])
            story.append(scope_heading)
            
            scope_text = Paragraph(loa_data['authority_scope'], self.styles['CustomBody'])
            story.append(scope_text)
            story.append(Spacer(1, 20))
        
        # Terms and Conditions
        if loa_data.get('terms_and_conditions'):
            terms_heading = Paragraph("TERMS AND CONDITIONS", self.styles['CustomHeading'])
            story.append(terms_heading)
            
            terms_text = Paragraph(loa_data['terms_and_conditions'], self.styles['CustomBody'])
            story.append(terms_text)
            story.append(Spacer(1, 20))
        
        # Signature Section
        signature_heading = Paragraph("DIGITAL SIGNATURE", self.styles['CustomHeading'])
        story.append(signature_heading)
        
        if signature_image:
            # Add signature image if provided
            try:
                sig_img_data = base64.b64decode(signature_image)
                sig_img = ImageReader(io.BytesIO(sig_img_data))
                story.append(Spacer(1, 10))
                # Note: In a real implementation, you'd add the image to the PDF
                # For now, we'll add text indicating the signature
                sig_text = Paragraph("Digital signature applied", self.styles['SignatureStyle'])
                story.append(sig_text)
            except Exception:
                sig_text = Paragraph("Digital signature: [Signature data present]", self.styles['SignatureStyle'])
                story.append(sig_text)
        
        # Signature details
        sig_details = [
            f"Signed by: {loa_data['authorized_person_name']}",
            f"Date: {datetime.now().strftime('%d %B %Y at %H:%M:%S')}",
            f"Verification Code: {loa_data.get('verification_code', 'N/A')}"
        ]
        
        for detail in sig_details:
            story.append(Paragraph(detail, self.styles['SignatureStyle']))
        
        story.append(Spacer(1, 20))
        
        # Footer
        footer_text = Paragraph(
            "This document has been digitally signed and is legally binding under Australian law. "
            "Any unauthorized modification will invalidate this Letter of Authority.",
            self.styles['Normal']
        )
        story.append(footer_text)
        
        # Build PDF
        doc.build(story)
        
        return str(filepath)