from pydantic import BaseModel
from typing import Optional, Dict, List, Any


class JobResponse(BaseModel):
    job_id: str
    status: str
    message: Optional[str] = None


class StatusResponse(BaseModel):
    job_id: str
    status: str
    progress: Optional[int] = None
    message: Optional[str] = None


class CreativeSuiteResponse(BaseModel):
    job_id: str
    status: str
    personality: Optional[Dict[str, Any]] = None
    letter: Optional[Dict[str, Any]] = None
    caqi: Optional[Dict[str, Any]] = None
    html_files: Optional[Dict[str, str]] = None
    markdown_report: Optional[str] = None


class ScanResponse(BaseModel):
    job_id: str
    status: str
    findings: Optional[List[Dict[str, Any]]] = None
    metrics: Optional[Dict[str, Any]] = None
    duration_ms: Optional[int] = None


class OnboardingResponse(BaseModel):
    job_id: str
    status: str
    profile: Optional[Dict[str, Any]] = None
    html: Optional[str] = None
    markdown: Optional[str] = None


class ApiKeyResponse(BaseModel):
    key_id: str
    name: str
    created_at: str
    expires_at: Optional[str] = None
    rate_limit: int
    scopes: List[str]


class ApiKeyListResponse(BaseModel):
    keys: List[ApiKeyResponse]


class ConfigResponse(BaseModel):
    ignore_patterns: List[str]
    languages: List[str]
    rules: Dict[str, bool]
    thresholds: Dict[str, float]


class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: str
