from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uuid
from typing import Dict
from dotenv import load_dotenv
import os

from app.models.schemas import (
    StartAnalysisRequest, AnswerRequest,
    AnalysisSession, WhyStep, AnalysisStatus,
    NextQuestionResponse, FinalResultResponse, AIConfig
)
from app.services.ai_service import AIService

# Load environment variables
load_dotenv()

# Default AI configuration from .env
DEFAULT_AI_CONFIG = {
    "base_url": os.getenv("AI_BASE_URL", "https://api.openai.com/v1"),
    "api_key": os.getenv("AI_API_KEY", ""),
    "model_id": os.getenv("AI_MODEL_ID", "gpt-3.5-turbo")
}

app = FastAPI(
    title="5 Whys Root Cause Analyzer",
    description="سیستم ریشه‌یابی مشکلات با تکنیک 5 چرا",
    version="1.0.0"
)

# ذخیره موقت جلسات (در حافظه)
sessions: Dict[str, AnalysisSession] = {}

MAX_STEPS = 7  # حداکثر تعداد سوالات


@app.get("/")
async def root():
    """صفحه اصلی"""
    return FileResponse("static/index.html")


@app.post("/api/start", response_model=NextQuestionResponse)
async def start_analysis(request: StartAnalysisRequest):
    """شروع تحلیل جدید"""
    try:
        # ایجاد سرویس AI با استفاده از تنظیمات پیش‌فرض
        ai_service = AIService(get_default_ai_config())
        
        # تولید اولین سوال
        first_question = await ai_service.generate_first_why(request.problem)
        
        # ایجاد جلسه جدید
        session_id = str(uuid.uuid4())[:8]
        session = AnalysisSession(
            session_id=session_id,
            original_problem=request.problem,
            steps=[WhyStep(step_number=1, question=first_question)],
            current_step=1
        )
        
        sessions[session_id] = session
        
        return NextQuestionResponse(
            session_id=session_id,
            current_step=1,
            question=first_question,
            status=AnalysisStatus.IN_PROGRESS
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطا در اتصال به AI: {str(e)}")


def get_default_ai_config():
    """دریافت تنظیمات پیش‌فرض AI از .env"""
    return AIConfig(
        base_url=DEFAULT_AI_CONFIG["base_url"],
        api_key=DEFAULT_AI_CONFIG["api_key"],
        model_id=DEFAULT_AI_CONFIG["model_id"]
    )


@app.post("/api/answer")
async def submit_answer(request: AnswerRequest):
    """ارسال پاسخ و دریافت سوال بعدی"""
    
    session = sessions.get(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="جلسه یافت نشد")
    
    if session.status == AnalysisStatus.ROOT_FOUND:
        raise HTTPException(status_code=400, detail="تحلیل قبلاً تکمیل شده")
    
    try:
        # استفاده از تنظیمات پیش‌فرض به جای تنظیمات ارسال شده توسط کاربر
        ai_service = AIService(get_default_ai_config())
        
        # ذخیره پاسخ فعلی
        current_step_idx = session.current_step - 1
        session.steps[current_step_idx].answer = request.answer
        
        # بررسی و تولید سوال بعدی
        (
            is_valid,
            next_question,
            clarification,
            is_root_found,
            root_cause,
            recommendations
        ) = await ai_service.validate_and_generate_next(
            session.original_problem,
            session.steps,
            request.answer
        )
        
        # اگر پاسخ نامعتبر است
        if not is_valid or clarification:
            session.steps[current_step_idx].is_valid = False
            session.steps[current_step_idx].clarification_note = clarification
            session.status = AnalysisStatus.NEEDS_CLARIFICATION
            
            return NextQuestionResponse(
                session_id=session.session_id,
                current_step=session.current_step,
                question=session.steps[current_step_idx].question,
                status=AnalysisStatus.NEEDS_CLARIFICATION,
                needs_clarification=True,
                clarification_message=clarification or "لطفاً پاسخ واضح‌تری بدهید"
            )
        
        # اگر به ریشه رسیدیم
        if is_root_found or session.current_step >= MAX_STEPS:
            if not root_cause:
                root_cause, recommendations = await ai_service.generate_summary(
                    session.original_problem,
                    session.steps
                )
            
            session.status = AnalysisStatus.ROOT_FOUND
            session.root_cause = root_cause
            session.recommendations = recommendations
            
            return FinalResultResponse(
                session_id=session.session_id,
                original_problem=session.original_problem,
                steps=session.steps,
                root_cause=root_cause,
                recommendations=recommendations,
                total_steps=session.current_step
            )
        
        # ادامه با سوال بعدی
        session.current_step += 1
        session.steps.append(WhyStep(
            step_number=session.current_step,
            question=next_question
        ))
        
        return NextQuestionResponse(
            session_id=session.session_id,
            current_step=session.current_step,
            question=next_question,
            status=AnalysisStatus.IN_PROGRESS
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطا: {str(e)}")


@app.get("/api/session/{session_id}")
async def get_session(session_id: str):
    """دریافت وضعیت جلسه"""
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="جلسه یافت نشد")
    return session


@app.delete("/api/session/{session_id}")
async def delete_session(session_id: str):
    """حذف جلسه"""
    if session_id in sessions:
        del sessions[session_id]
        return {"message": "جلسه حذف شد"}
    raise HTTPException(status_code=404, detail="جلسه یافت نشد")


# Health check برای GitHub Actions
@app.get("/health")
async def health_check():
    return {"status": "healthy", "sessions_count": len(sessions)}