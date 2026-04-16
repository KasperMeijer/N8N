from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import datetime
import uuid
import re
import httpx
import os

app = FastAPI()

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://audit:audit_password@audit_db:5432/audit_db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(String, unique=True, index=True)
    citizen_token = Column(String)
    request_data = Column(Text)
    ai_response = Column(Text)
    fairness_check = Column(Boolean)
    decision = Column(String)  # auto, manual, rejected
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic models
class RequestData(BaseModel):
    citizenId: str
    description: str
    severity: str  # low, medium, high
    consentAI: bool
    additionalData: dict = {}

class PseudonymizedData(BaseModel):
    token: str
    description: str
    severity: str
    age_group: str = "unknown"

class PolicyResponse(BaseModel):
    allowed: bool
    rules: list[str]

class AIResponse(BaseModel):
    proposal: str
    reasoning: str

class FairnessCheck(BaseModel):
    passed: bool
    flags: list[str]

class SubmitResponse(BaseModel):
    request_id: str
    status: str
    message: str

# Helper functions
def pseudonymize_citizen(citizen_id: str) -> str:
    # Simple hash for pseudonymization
    return str(hash(citizen_id) % 1000000).zfill(6)

def get_policy(severity: str) -> PolicyResponse:
    # Mock policy
    if severity == "high":
        return PolicyResponse(allowed=False, rules=["High severity requires manual review"])
    return PolicyResponse(allowed=True, rules=["Auto processing allowed"])

def call_ai_service(description: str) -> AIResponse:
    # Stub AI service
    if "urgent" in description.lower():
        proposal = "Immediate assistance required"
        reasoning = "Detected urgent keywords"
    else:
        proposal = "Standard support process"
        reasoning = "General case"
    return AIResponse(proposal=proposal, reasoning=reasoning)

def fairness_check(response: str) -> FairnessCheck:
    forbidden_terms = ["discriminatie", "bias", "unfair"]
    flags = [term for term in forbidden_terms if term in response.lower()]
    passed = len(flags) == 0
    return FairnessCheck(passed=passed, flags=flags)

def is_high_risk(severity: str, description: str) -> bool:
    return severity == "high" or len(description.split()) > 50  # Simple heuristic

# Endpoints
@app.post("/submit-request", response_model=SubmitResponse)
def submit_request(request: RequestData, db: Session = Depends(get_db)):
    if not request.consentAI:
        raise HTTPException(status_code=400, detail="AI consent required")

    # Minimalize data: remove PII
    minimized_data = {
        "description": request.description,
        "severity": request.severity,
        "additionalData": {k: v for k, v in request.additionalData.items() if not re.search(r'\b\d{9}\b', str(v))}  # Remove potential BSN-like
    }

    # Pseudonymize
    token = pseudonymize_citizen(request.citizenId)
    pseudo_data = PseudonymizedData(
        token=token,
        description=minimized_data["description"],
        severity=minimized_data["severity"]
    )

    # Get policy
    policy = get_policy(pseudo_data.severity)
    if not policy.allowed:
        decision = "rejected"
        message = "Request rejected due to policy"
    else:
        # Call AI
        ai_resp = call_ai_service(pseudo_data.description)

        # Fairness check
        fairness = fairness_check(ai_resp.proposal + ai_resp.reasoning)
        if not fairness.passed:
            decision = "manual"
            message = "Request flagged for fairness review"
        elif is_high_risk(pseudo_data.severity, pseudo_data.description):
            decision = "manual"
            message = "High risk request sent for manual review"
        else:
            decision = "auto"
            message = f"Auto processed: {ai_resp.proposal}"

    # Log to audit
    request_id = str(uuid.uuid4())
    audit_entry = AuditLog(
        request_id=request_id,
        citizen_token=token,
        request_data=str(minimized_data),
        ai_response=str(ai_resp.dict()) if 'ai_resp' in locals() else None,
        fairness_check=fairness.passed if 'fairness' in locals() else None,
        decision=decision
    )
    db.add(audit_entry)
    db.commit()

    return SubmitResponse(request_id=request_id, status=decision, message=message)

@app.get("/audit-logs")
def get_audit_logs(db: Session = Depends(get_db)):
    logs = db.query(AuditLog).all()
    return [{"id": log.id, "request_id": log.request_id, "decision": log.decision, "timestamp": log.timestamp} for log in logs]

# Existing endpoints (updated)
@app.post("/validate")
def validate(data: dict):
    if "consentAI" not in data or not data["consentAI"]:
        raise HTTPException(status_code=400, detail="Consent required")
    return {"status": "valid"}

@app.post("/pseudonymize")
def pseudonymize(data: dict):
    token = pseudonymize_citizen(data.get("citizenId", ""))
    return {"token": token}

@app.post("/policy")
def policy(data: dict):
    return get_policy(data.get("severity", "low")).dict()

@app.post("/fairness-check")
def fairness(data: dict):
    text = data.get("text", "")
    return fairness_check(text).dict()