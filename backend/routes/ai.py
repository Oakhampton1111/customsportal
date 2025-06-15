"""
AI-powered consultation and analysis API routes.
Provides endpoints for chat interface, document analysis, and image classification.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc, text
from sqlalchemy.orm import selectinload
import logging
from database import get_async_session
from models.tariff import TariffCode
from models.tco import Tco
from models.dumping import DumpingDuty
from models.fta import FtaRate, TradeAgreement
from models import Conversation, ConversationMessage
import uuid
import json

router = APIRouter(prefix="/api/ai", tags=["ai"])

# Response models
class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    message: str
    session_id: str
    context: Optional[Dict[str, Any]] = None
    suggestions: List[str] = []
    confidence_score: float = 0.0
    sources: List[str] = []

class ClassificationResult(BaseModel):
    suggested_codes: List[Dict[str, Any]]
    confidence_scores: List[float]
    reasoning: str
    additional_info: str

class DocumentAnalysis(BaseModel):
    document_type: str
    extracted_data: Dict[str, Any]
    suggested_classifications: List[str]
    compliance_notes: List[str]
    confidence_score: float

class ConversationSession(BaseModel):
    session_id: str
    created_at: datetime
    last_updated: datetime
    messages: List[ChatMessage]
    context: Dict[str, Any]

@router.post("/chat", response_model=ChatResponse)
async def chat_consultation(
    message: str,
    session_id: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
    db: AsyncSession = Depends(get_async_session)
):
    """
    AI-powered customs consultation chat interface.
    Uses RAG (Retrieval Augmented Generation) with full database context.
    """
    try:
        # Generate or use existing session ID
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # Analyze user message for intent and extract key terms
        intent, key_terms = analyze_user_intent(message)
        
        # Retrieve relevant context from database
        context_data = await get_database_context(db, key_terms, intent)
        
        # Generate response based on intent and context
        response_data = await generate_ai_response(message, intent, context_data, key_terms)
        
        # Store conversation in database
        await save_conversation_to_db(db, session_id, message, response_data)
        
        return ChatResponse(
            message=response_data["message"],
            session_id=session_id,
            context=response_data["context_used"],
            suggestions=response_data["suggested_actions"],
            confidence_score=response_data["confidence_score"],
            sources=response_data["sources"]
        )
        
    except Exception as e:
        logging.error(f"Error in chat consultation: {e}")
        return ChatResponse(
            message="I apologize, but I'm experiencing technical difficulties. Please try again or contact support for assistance.",
            session_id=session_id or str(uuid.uuid4()),
            confidence_score=0.0,
            sources=[]
        )

@router.post("/classify-image", response_model=ClassificationResult)
async def classify_image(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Classify product images for HS code determination using AI vision.
    """
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Validate file size (max 10MB)
        file_size = 0
        content = await file.read()
        file_size = len(content)
        
        if file_size > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(status_code=400, detail="File size too large (max 10MB)")
        
        # Reset file pointer
        await file.seek(0)
        
        # Analyze image for product classification
        classification_results = await analyze_product_image(content, file.content_type, db)
        
        return ClassificationResult(
            suggested_codes=classification_results["suggested_codes"],
            confidence_scores=classification_results["confidence_scores"],
            reasoning=classification_results["reasoning"],
            additional_info=classification_results["additional_info"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error in image classification: {e}")
        raise HTTPException(status_code=500, detail=f"Image classification failed: {str(e)}")

@router.post("/analyze-document", response_model=DocumentAnalysis)
async def analyze_document(
    file: UploadFile = File(...),
    analysis_type: str = "commercial_invoice",
    db: AsyncSession = Depends(get_async_session)
):
    """
    Analyze uploaded documents (invoices, packing lists, etc.) for customs information extraction.
    """
    try:
        # Validate file type
        allowed_types = ["application/pdf", "image/jpeg", "image/png", "image/jpg", "text/plain"]
        if file.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.content_type}")
        
        # Validate file size (max 20MB)
        content = await file.read()
        if len(content) > 20 * 1024 * 1024:  # 20MB
            raise HTTPException(status_code=400, detail="File size too large (max 20MB)")
        
        # Reset file pointer
        await file.seek(0)
        
        # Analyze document based on type
        analysis_results = await analyze_customs_document(content, file.content_type, analysis_type, db)
        
        return DocumentAnalysis(
            document_type=analysis_results["document_type"],
            extracted_data=analysis_results["extracted_data"],
            suggested_classifications=analysis_results["suggested_classifications"],
            compliance_notes=analysis_results["compliance_notes"],
            confidence_score=analysis_results["confidence_score"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error in document analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Document analysis failed: {str(e)}")

@router.get("/conversation/{session_id}", response_model=ConversationSession)
async def get_conversation(
    session_id: str,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Retrieve conversation history for a specific session.
    """
    try:
        # Retrieve conversation from database
        conversation_result = await db.execute(
            select(Conversation)
            .where(Conversation.session_id == session_id)
        )
        conversation = conversation_result.scalars().first()
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Retrieve conversation messages
        message_result = await db.execute(
            select(ConversationMessage)
            .where(ConversationMessage.conversation_id == conversation.id)
            .order_by(ConversationMessage.timestamp)
        )
        messages = message_result.scalars().all()
        
        return ConversationSession(
            session_id=conversation.session_id,
            created_at=conversation.created_at,
            last_updated=conversation.last_updated,
            messages=[
                ChatMessage(
                    role=message.role,
                    content=message.content,
                    timestamp=message.timestamp,
                    metadata=message.message_metadata
                ) for message in messages
            ],
            context=conversation.context
        )
        
    except Exception as e:
        logging.error(f"Error retrieving conversation: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve conversation: {str(e)}")

@router.post("/conversation/{session_id}/export")
async def export_conversation(
    session_id: str,
    format: str = "pdf",
    db: AsyncSession = Depends(get_async_session)
):
    """
    Export conversation session as PDF or other format.
    """
    try:
        if format not in ["pdf", "txt", "json"]:
            raise HTTPException(status_code=400, detail="Unsupported export format. Use: pdf, txt, or json")
        
        # Retrieve conversation from database
        conversation_result = await db.execute(
            select(Conversation)
            .where(Conversation.session_id == session_id)
        )
        conversation = conversation_result.scalars().first()
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Generate export file
        export_data = await generate_conversation_export(conversation, format, db)
        
        return {
            "download_url": f"/api/ai/download/{session_id}.{format}",
            "expires_at": (datetime.now() + timedelta(hours=24)).isoformat(),
            "file_size": export_data["file_size"],
            "format": format
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error exporting conversation: {e}")
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

@router.get("/suggestions")
async def get_ai_suggestions(
    context: str,
    session_id: Optional[str] = None,
    db: AsyncSession = Depends(get_async_session)
):
    """Get AI-powered suggestions based on current context."""
    try:
        # Analyze context to provide relevant suggestions
        suggestions = await generate_contextual_suggestions(context, session_id, db)
        
        return {
            "suggestions": suggestions["suggestions"],
            "context_analysis": suggestions["context_analysis"],
            "recommended_actions": suggestions["recommended_actions"],
            "related_topics": suggestions["related_topics"]
        }
        
    except Exception as e:
        logging.error(f"Error generating suggestions: {e}")
        return {
            "suggestions": [
                "Would you like me to calculate the total landed cost?",
                "Should I check for any applicable TCO exemptions?",
                "Do you need information about AQIS import conditions?"
            ],
            "context_analysis": "general",
            "recommended_actions": [],
            "related_topics": []
        }

# AI Helper Functions
def analyze_user_intent(message: str) -> tuple[str, List[str]]:
    """Analyze user message to determine intent and extract key terms."""
    message_lower = message.lower()
    key_terms = []
    
    # Extract potential HS codes
    import re
    hs_codes = re.findall(r'\b\d{4}\.?\d{2}\.?\d{2}\b', message)
    key_terms.extend(hs_codes)
    
    # Extract country names (simplified)
    countries = ["china", "usa", "germany", "japan", "korea", "thailand", "vietnam", "india", "malaysia", "singapore"]
    for country in countries:
        if country in message_lower:
            key_terms.append(country)
    
    # Determine intent based on keywords
    if any(word in message_lower for word in ["classify", "classification", "hs code", "tariff code"]):
        intent = "classification"
    elif any(word in message_lower for word in ["duty", "calculate", "cost", "rate"]):
        intent = "duty_calculation"
    elif any(word in message_lower for word in ["tco", "concession", "exemption"]):
        intent = "tco_inquiry"
    elif any(word in message_lower for word in ["fta", "free trade", "agreement", "preferential"]):
        intent = "fta_inquiry"
    elif any(word in message_lower for word in ["dumping", "anti-dumping", "countervailing"]):
        intent = "dumping_inquiry"
    elif any(word in message_lower for word in ["import", "requirement", "condition", "permit"]):
        intent = "import_requirements"
    else:
        intent = "general_inquiry"
    
    # Extract product-related terms
    product_keywords = message.split()
    key_terms.extend([word for word in product_keywords if len(word) > 3])
    
    return intent, list(set(key_terms))

async def get_database_context(db: AsyncSession, key_terms: List[str], intent: str) -> Dict[str, Any]:
    """Retrieve relevant context from database based on key terms and intent."""
    context = {
        "tariff_codes": [],
        "tcos": [],
        "dumping_duties": [],
        "fta_rates": [],
        "related_info": []
    }
    
    try:
        # Search for relevant HS codes
        if key_terms:
            for term in key_terms:
                if len(term) >= 4:  # Potential HS code or product term
                    # Search tariff codes
                    tariff_result = await db.execute(
                        select(TariffCode)
                        .where(
                            or_(
                                TariffCode.hs_code.ilike(f"%{term}%"),
                                TariffCode.description.ilike(f"%{term}%")
                            )
                        )
                        .limit(5)
                    )
                    tariff_codes = tariff_result.scalars().all()
                    context["tariff_codes"].extend([{
                        "hs_code": tc.hs_code,
                        "description": tc.description,
                        "duty_rate": tc.general_duty_rate
                    } for tc in tariff_codes])
        
        # Get relevant TCOs based on intent
        if intent in ["tco_inquiry", "classification", "general_inquiry"]:
            tco_result = await db.execute(
                select(Tco)
                .where(Tco.status == "CURRENT")
                .order_by(desc(Tco.gazetted_date))
                .limit(10)
            )
            tcos = tco_result.scalars().all()
            context["tcos"] = [{
                "tco_reference": tco.tco_reference,
                "hs_code": tco.hs_code,
                "description": tco.goods_description,
                "gazetted_date": tco.gazetted_date.isoformat()
            } for tco in tcos]
        
        # Get dumping duties if relevant
        if intent in ["dumping_inquiry", "duty_calculation"]:
            dumping_result = await db.execute(
                select(DumpingDuty)
                .where(DumpingDuty.is_active == True)
                .limit(10)
            )
            duties = dumping_result.scalars().all()
            context["dumping_duties"] = [{
                "hs_code": duty.hs_code,
                "country": duty.country_of_origin,
                "duty_rate": duty.duty_rate,
                "description": duty.goods_description
            } for duty in duties]
        
        # Get FTA rates if relevant
        if intent in ["fta_inquiry", "duty_calculation"]:
            fta_result = await db.execute(
                select(FtaRate)
                .join(TradeAgreement)
                .where(TradeAgreement.is_active == True)
                .limit(10)
            )
            fta_rates = fta_result.scalars().all()
            context["fta_rates"] = [{
                "hs_code": rate.hs_code,
                "country": rate.country_code,
                "preferential_rate": rate.preferential_rate
            } for rate in fta_rates]
        
    except Exception as e:
        logging.error(f"Error retrieving database context: {e}")
    
    return context

async def generate_ai_response(message: str, intent: str, context_data: Dict[str, Any], key_terms: List[str]) -> Dict[str, Any]:
    """Generate AI response based on intent and context data."""
    
    # This is a simplified rule-based response system
    # In production, this would integrate with Claude/Anthropic API
    
    response_templates = {
        "classification": {
            "message": "Based on your query about product classification, I found several relevant HS codes and information. ",
            "actions": ["View detailed classification", "Calculate duties", "Check TCO exemptions"],
            "sources": ["Australian Customs Tariff", "WCO Harmonized System"],
            "related_codes": ["3917.21.00", "3917.29.00"]
        },
        "duty_calculation": {
            "message": "I can help you calculate import duties and taxes. ",
            "actions": ["Calculate total landed cost", "Check FTA rates", "Review additional taxes"],
            "sources": ["Customs Tariff", "FTA Schedules", "Tax Legislation"],
            "confidence_score": 0.8
        },
        "tco_inquiry": {
            "message": "Regarding Tariff Concession Orders (TCOs), ",
            "actions": ["Search current TCOs", "Check eligibility", "View application process"],
            "sources": ["TCO Database", "ABF Guidelines"]
        },
        "fta_inquiry": {
            "message": "For Free Trade Agreement information, ",
            "actions": ["Check FTA eligibility", "Compare rates", "View origin requirements"],
            "sources": ["FTA Schedules", "Rules of Origin", "Trade Agreements"]
        },
        "dumping_inquiry": {
            "message": "Regarding anti-dumping measures, ",
            "actions": ["Check active measures", "Review duty rates", "View investigation status"],
            "sources": ["Anti-Dumping Commission", "Dumping Duty Database"]
        },
        "import_requirements": {
            "message": "For import requirements and conditions, ",
            "actions": ["Check AQIS conditions", "Review permits", "View compliance requirements"],
            "sources": ["AQIS Database", "Import Conditions", "Biosecurity Requirements"]
        },
        "general_inquiry": {
            "message": "I'm here to help with customs and trade matters. ",
            "actions": ["Classify products", "Calculate duties", "Check regulations"],
            "sources": ["Customs Database", "Trade Regulations"]
        }
    }
    
    template = response_templates.get(intent, response_templates["general_inquiry"])
    
    # Build response message
    message_parts = [template["message"]]
    
    # Add context-specific information
    if context_data["tariff_codes"]:
        codes = [tc["hs_code"] for tc in context_data["tariff_codes"][:3]]
        message_parts.append(f"I found relevant HS codes: {', '.join(codes)}. ")
    
    if context_data["tcos"] and intent in ["tco_inquiry", "classification"]:
        tco_count = len(context_data["tcos"])
        message_parts.append(f"There are {tco_count} current TCOs that might be relevant. ")
    
    if context_data["dumping_duties"] and intent == "dumping_inquiry":
        duty_count = len(context_data["dumping_duties"])
        message_parts.append(f"I found {duty_count} active anti-dumping measures. ")
    
    if context_data["fta_rates"] and intent == "fta_inquiry":
        fta_count = len(context_data["fta_rates"])
        message_parts.append(f"There are {fta_count} FTA rates available. ")
    
    message_parts.append("What specific information would you like me to provide?")
    
    # Extract related codes
    related_codes = []
    for tc in context_data["tariff_codes"][:5]:
        related_codes.append(tc["hs_code"])
    
    # Determine confidence based on context relevance
    confidence = 0.7
    if context_data["tariff_codes"]:
        confidence += 0.1
    if any(term in message.lower() for term in key_terms if len(term) > 4):
        confidence += 0.1
    if intent != "general_inquiry":
        confidence += 0.1
    
    confidence = min(confidence, 0.95)
    
    # Build context used list
    context_used = []
    if context_data["tariff_codes"]:
        context_used.append("tariff_database")
    if context_data["tcos"]:
        context_used.append("tco_database")
    if context_data["dumping_duties"]:
        context_used.append("dumping_database")
    if context_data["fta_rates"]:
        context_used.append("fta_database")
    
    format_data = {
        "related_codes": template.get("related_codes", []),
        "confidence_score": template.get("confidence_score", 0.8)
    }
    
    return {
        "message": "".join(message_parts),
        "suggested_actions": template["actions"],
        "related_codes": related_codes,
        "confidence_score": confidence,
        "sources": template["sources"],
        "context_used": context_used
    }

async def analyze_product_image(image_data: bytes, content_type: str, db: AsyncSession) -> Dict[str, Any]:
    """Analyze product image for classification."""
    # This is a simplified mock implementation
    # In production, this would integrate with AI vision services
    
    return {
        "suggested_codes": [
            {"hs_code": "8703.23.10", "description": "Motor cars with spark-ignition engine, 1500-3000cc", "confidence": 0.85},
            {"hs_code": "8703.24.10", "description": "Motor cars with spark-ignition engine, 3000-4000cc", "confidence": 0.65}
        ],
        "confidence_scores": [0.85, 0.65],
        "reasoning": "Detected vehicle features consistent with passenger car classification",
        "additional_info": "Please verify the engine displacement and country of manufacture for accurate classification"
    }

async def analyze_customs_document(document_data: bytes, content_type: str, analysis_type: str, db: AsyncSession) -> Dict[str, Any]:
    """Analyze customs document for information extraction."""
    # This is a simplified mock implementation
    # In production, this would integrate with OCR and AI services
    
    return {
        "document_type": "commercial_invoice",
        "extracted_data": {
            "supplier": "ABC Manufacturing Ltd",
            "products": [
                {"description": "Laptop computers", "quantity": 100, "value": 50000}
            ],
            "country_of_origin": "China",
            "total_value": 50000
        },
        "suggested_classifications": ["8471.30.00"],
        "compliance_notes": [
            "Verify country of origin for FTA eligibility",
            "Check if products require ACMA compliance"
        ],
        "confidence_score": 0.88
    }

async def generate_conversation_export(conversation: Conversation, format: str, db: AsyncSession) -> Dict[str, Any]:
    """Generate conversation export file."""
    # This is a simplified mock implementation
    # In production, this would generate a PDF or other format file
    
    return {
        "file_size": 1024,
        "file_name": f"{conversation.session_id}.{format}"
    }

async def generate_contextual_suggestions(context: str, session_id: str, db: AsyncSession) -> Dict[str, Any]:
    """Generate AI-powered suggestions based on context."""
    # This is a simplified mock implementation
    # In production, this would integrate with AI services
    
    return {
        "suggestions": [
            "Would you like me to calculate the total landed cost?",
            "Should I check for any applicable TCO exemptions?",
            "Do you need information about AQIS import conditions?"
        ],
        "context_analysis": "general",
        "recommended_actions": [],
        "related_topics": []
    }

async def save_conversation_to_db(db: AsyncSession, session_id: str, user_message: str, response_data: Dict[str, Any]) -> None:
    """Save conversation to database."""
    try:
        # Check if conversation already exists
        conversation_result = await db.execute(
            select(Conversation).where(Conversation.session_id == session_id)
        )
        conversation = conversation_result.scalar_one_or_none()
        
        # Create new conversation if it doesn't exist
        if not conversation:
            conversation = Conversation(
                session_id=session_id,
                created_at=datetime.now(),
                last_updated=datetime.now(),
                context=response_data.get("context_used", {})
            )
            db.add(conversation)
            await db.flush()  # Get the ID without committing
        else:
            # Update existing conversation
            conversation.last_updated = datetime.now()
            conversation.context = response_data.get("context_used", {})
        
        # Save user message
        user_msg = ConversationMessage(
            conversation_id=conversation.id,
            role="user",
            content=user_message,
            timestamp=datetime.now(),
            message_metadata={}
        )
        db.add(user_msg)
        
        # Save AI response
        ai_msg = ConversationMessage(
            conversation_id=conversation.id,
            role="assistant",
            content=response_data["message"],
            timestamp=datetime.now(),
            message_metadata={
                "confidence_score": response_data.get("confidence_score", 0.0),
                "sources": response_data.get("sources", []),
                "suggestions": response_data.get("suggested_actions", [])
            }
        )
        db.add(ai_msg)
        
        await db.commit()
        
    except Exception as e:
        await db.rollback()
        logging.error(f"Error saving conversation: {e}")
        # Don't raise error to avoid breaking chat functionality
