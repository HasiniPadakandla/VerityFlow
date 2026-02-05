from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime, timezone
import uuid
import os
from motor.motor_asyncio import AsyncIOMotorDatabase

from services.scam_rules import ScamRuleDetector
from services.ml_classifier import MLClassifier
from services.llm_reasoning import LLMReasoning

router = APIRouter()

scam_detector = ScamRuleDetector()
ml_classifier = MLClassifier()
emergent_key = os.environ.get('EMERGENT_LLM_KEY')
llm_reasoning = LLMReasoning(api_key=emergent_key)

class AnalyzeRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=5000)

class AnalysisResult(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    message: str
    verdict: str
    confidence: float
    reasons: List[str]
    safety_advice: str
    red_flags: List[str]
    suspicious_urls: List[str]
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    explanation: Optional[str] = None

class HistoryResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str
    message: str
    verdict: str
    confidence: float
    timestamp: datetime

def get_db():
    from motor.motor_asyncio import AsyncIOMotorClient
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    return client[os.environ['DB_NAME']]

@router.post("/analyze-message", response_model=AnalysisResult)
async def analyze_message(request: AnalyzeRequest):
    """Analyze a message for scam, fake news, or phishing content"""
    message = request.message.strip()
    
    if not message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    rule_results = scam_detector.analyze(message)
    ml_results = ml_classifier.predict(message)
    
    rule_risk = rule_results['risk_score']
    ml_confidence = ml_results['confidence']
    ml_class = ml_results['predicted_class']
    
    if rule_risk > 0.5 or (ml_class != 'legitimate' and ml_confidence > 0.6):
        if ml_class in ['scam', 'phishing', 'fake_news']:
            final_verdict = ml_class.replace('_', ' ').title()
        else:
            final_verdict = "Scam"
    elif rule_risk > 0.2 or (ml_class != 'legitimate' and ml_confidence > 0.4):
        final_verdict = "Suspicious"
    else:
        final_verdict = "Legitimate"
    
    combined_confidence = (rule_risk * 0.4 + (1 - ml_confidence if ml_class == 'legitimate' else ml_confidence) * 0.6)
    
    if final_verdict == "Legitimate":
        combined_confidence = 1 - combined_confidence
    
    combined_confidence = max(0.5, min(0.99, combined_confidence))
    
    llm_result = await llm_reasoning.generate_reasoning(
        message=message,
        verdict=final_verdict,
        confidence=combined_confidence,
        red_flags=rule_results['red_flags']
    )
    
    reasons = llm_result['reasons'] if llm_result['reasons'] else rule_results['red_flags'][:3]
    if not reasons:
        if final_verdict == "Legitimate":
            reasons = ["No suspicious patterns detected", "Message appears genuine", "No red flags identified"]
        else:
            reasons = ["Suspicious patterns detected", "Requires verification", "Exercise caution"]
    
    result = AnalysisResult(
        message=message,
        verdict=final_verdict,
        confidence=combined_confidence,
        reasons=reasons,
        safety_advice=llm_result['safety_advice'],
        red_flags=rule_results['red_flags'],
        suspicious_urls=rule_results['suspicious_urls'],
        explanation=llm_result.get('explanation')
    )
    
    db = get_db()
    doc = result.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    await db.analyses.insert_one(doc)
    
    return result

@router.get("/history", response_model=List[HistoryResponse])
async def get_history(limit: int = 50, search: str = None):
    """Get analysis history with optional search"""
    db = get_db()
    
    query = {}
    if search:
        query['message'] = {'$regex': search, '$options': 'i'}
    
    analyses = await db.analyses.find(query, {"_id": 0}).sort('timestamp', -1).limit(limit).to_list(limit)
    
    for analysis in analyses:
        if isinstance(analysis['timestamp'], str):
            analysis['timestamp'] = datetime.fromisoformat(analysis['timestamp'])
    
    return analyses

@router.get("/export")
async def export_history(format: str = "csv"):
    """Export analysis history"""
    db = get_db()
    analyses = await db.analyses.find({}, {"_id": 0}).sort('timestamp', -1).to_list(1000)
    
    if format == "csv":
        csv_lines = ["ID,Timestamp,Message,Verdict,Confidence,Red Flags"]
        for analysis in analyses:
            timestamp = analysis.get('timestamp', '')
            if isinstance(timestamp, datetime):
                timestamp = timestamp.isoformat()
            message = analysis.get('message', '').replace(',', ';').replace('\n', ' ')[:100]
            verdict = analysis.get('verdict', '')
            confidence = analysis.get('confidence', 0)
            red_flags = '; '.join(analysis.get('red_flags', []))[:100]
            csv_lines.append(f"{analysis.get('id', '')},{timestamp},{message},{verdict},{confidence:.2f},{red_flags}")
        
        return {"format": "csv", "data": "\n".join(csv_lines)}
    
    return {"format": "json", "data": analyses}
