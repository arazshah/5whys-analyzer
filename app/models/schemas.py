from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class AnalysisStatus(str, Enum):
    IN_PROGRESS = "in_progress"
    NEEDS_CLARIFICATION = "needs_clarification"
    ROOT_FOUND = "root_found"
    MAX_DEPTH_REACHED = "max_depth_reached"


class AIConfig(BaseModel):
    """تنظیمات اتصال به AI"""
    base_url: str = Field(..., description="آدرس پایه API")
    api_key: str = Field(..., description="کلید API")
    model_id: str = Field(default="gpt-3.5-turbo", description="شناسه مدل")


class StartAnalysisRequest(BaseModel):
    """شروع تحلیل جدید"""
    problem: str = Field(..., min_length=10, description="توضیح مشکل اولیه")


class AnswerRequest(BaseModel):
    """پاسخ کاربر به سوال"""
    session_id: str
    answer: str = Field(..., min_length=3)


class WhyStep(BaseModel):
    """هر مرحله از تحلیل"""
    step_number: int
    question: str
    answer: Optional[str] = None
    is_valid: bool = True
    clarification_note: Optional[str] = None


class AnalysisSession(BaseModel):
    """جلسه تحلیل"""
    session_id: str
    original_problem: str
    steps: List[WhyStep] = []
    current_step: int = 1
    status: AnalysisStatus = AnalysisStatus.IN_PROGRESS
    root_cause: Optional[str] = None
    recommendations: Optional[List[str]] = None


class NextQuestionResponse(BaseModel):
    """پاسخ سیستم با سوال بعدی"""
    session_id: str
    current_step: int
    question: str
    status: AnalysisStatus
    needs_clarification: bool = False
    clarification_message: Optional[str] = None


class FinalResultResponse(BaseModel):
    """نتیجه نهایی تحلیل"""
    session_id: str
    original_problem: str
    steps: List[WhyStep]
    root_cause: str
    recommendations: List[str]
    total_steps: int