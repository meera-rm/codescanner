from pydantic import BaseModel
from typing import Optional, Dict, List


class CreativeSuiteRequest(BaseModel):
    directory_path: str
    analyses: List[str] = ["personality", "letter", "caqi"]


class ScanRequest(BaseModel):
    code: Optional[str] = None
    directory_path: Optional[str] = None
    language: str = "python"
    options: Dict[str, bool] = {
        "security": True,
        "quality_score": True,
        "code_smells": True,
        "doc_coverage": True,
        "complexity": True,
    }


class OnboardingRequest(BaseModel):
    directory_path: str
    tone: str = "neutral"
    include_creative_suite: bool = True
    format: str = "json"


class CreateApiKeyRequest(BaseModel):
    name: str
    expires_at: Optional[str] = None
    rate_limit: int = 100
    scopes: List[str] = ["scan", "onboarding", "creative-suite"]


class UpdateApiKeyRequest(BaseModel):
    name: Optional[str] = None
    expires_at: Optional[str] = None
    rate_limit: Optional[int] = None
    scopes: Optional[List[str]] = None


class ConfigUpdateRequest(BaseModel):
    ignore_patterns: Optional[List[str]] = None
    languages: Optional[List[str]] = None
    rules: Optional[Dict[str, bool]] = None
    thresholds: Optional[Dict[str, float]] = None
