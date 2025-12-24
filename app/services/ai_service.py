import httpx
import json
from typing import Tuple, List, Optional
from app.models.schemas import AIConfig, WhyStep
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def get_default_ai_config() -> AIConfig:
    """دریافت تنظیمات پیش‌فرض AI از .env"""
    return AIConfig(
        base_url=os.getenv("AI_BASE_URL", "https://api.openai.com/v1"),
        api_key=os.getenv("AI_API_KEY", ""),
        model_id=os.getenv("AI_MODEL_ID", "gpt-3.5-turbo")
    )


def validate_openrouter_config(config: AIConfig) -> bool:
    """بررسی صحت تنظیمات OpenRouter"""
    if "openrouter" not in config.base_url.lower():
        return True
    
    # بررسی کلید API
    if not config.api_key or len(config.api_key) < 10:
        return False
    
    # بررسی مدل
    if not config.model_id:
        return False
    
    return True


def validate_api_key(api_key: str) -> bool:
    """بررسی صحت کلید API"""
    if not api_key:
        return False
    
    # بررسی اینکه کلید API واقعی باشد (نه مقدار پیش‌فرض)
    if api_key == "your_openai_api_key_here":
        return False
    
    # بررسی طول کلید
    if len(api_key) < 20:
        return False
    
    return True


def get_openrouter_headers(api_key: str) -> dict:
    """دریافت هدرهای مورد نیاز برای OpenRouter"""
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8000",
        "X-Title": "5 Whys Analyzer",
        "User-Agent": "5-Whys-Analyzer/1.0"
    }


async def test_openrouter_connection(api_key: str, base_url: str, model_id: str) -> bool:
    """تست اتصال به OpenRouter"""
    import httpx
    
    headers = get_openrouter_headers(api_key)
    payload = {
        "model": model_id,
        "messages": [{"role": "user", "content": "test"}],
        "max_tokens": 1
    }
    
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                f"{base_url}/chat/completions",
                headers=headers,
                json=payload
            )
            print(f"OpenRouter test response: {response.status_code}")
            print(f"OpenRouter test response text: {response.text}")
            
            # بررسی کدهای وضعیت مختلف
            if response.status_code == 200:
                return True
            elif response.status_code == 401:
                print("OpenRouter 401 error: Authentication failed")
                return False
            elif response.status_code == 400:
                print("OpenRouter 400 error: Bad request")
                return False
            elif response.status_code == 429:
                print("OpenRouter 429 error: Rate limit exceeded")
                return False
            else:
                print(f"OpenRouter unexpected status: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"OpenRouter test failed: {e}")
        return False


def get_openrouter_model_list() -> list:
    """دریافت لیست مدل‌های OpenRouter"""
    return [
        "openai/gpt-3.5-turbo",
        "openai/gpt-4",
        "anthropic/claude-3-sonnet",
        "google/gemini-pro",
        "xiaomi/mimo-v2-flash:free"
    ]


class AIService:
    """سرویس ارتباط با AI"""
    
    def __init__(self, config: AIConfig):
        self.base_url = config.base_url.rstrip('/')
        self.api_key = config.api_key
        self.model_id = config.model_id
        self.timeout = 30.0
    
    async def _call_ai(self, messages: list) -> str:
        """فراخوانی API هوش مصنوعی"""
        # بررسی صحت کلید API
        if not validate_api_key(self.api_key):
            raise Exception("کلید API نامعتبر است. لطفاً یک کلید API معتبر وارد کنید.")
        
        # برای OpenRouter از هدرهای خاص استفاده می‌کنیم
        if "openrouter" in self.base_url.lower():
            headers = get_openrouter_headers(self.api_key)
        else:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        
        payload = {
            "model": self.model_id,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        # برای OpenRouter ممکن است نیاز به تنظیمات اضافی باشد
        if "openrouter" in self.base_url.lower():
            # برخی مدل‌های OpenRouter ممکن است نیاز به تنظیمات خاص داشته باشند
            pass
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload
            )
            
            # برای خطاهای احتمالی OpenRouter
            if response.status_code == 401:
                print(f"OpenRouter 401 error: {response.text}")
                raise Exception("خطای احراز هویت OpenRouter. لطفاً کلید API را بررسی کنید.")
            elif response.status_code == 400:
                error_data = response.json()
                print(f"OpenRouter 400 error: {error_data}")
                raise Exception(f"درخواست نامعتبر به OpenRouter: {error_data.get('error', {}).get('message', 'Unknown error')}")
            elif response.status_code == 429:
                print(f"OpenRouter 429 error: {response.text}")
                raise Exception("محدودیت نرخ درخواست به OpenRouter. لطفاً کمی صبر کنید.")
            
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
    
    async def generate_first_why(self, problem: str) -> str:
        """تولید اولین سوال چرا"""
        messages = [
            {
                "role": "system",
                "content": """شما یک متخصص تحلیل ریشه‌ای مشکلات با تکنیک 5 Whys هستید.
                
وظیفه شما:
1. مشکل را بررسی کنید
2. اولین سوال "چرا" را بپرسید که به ریشه مشکل نزدیک‌تر شود
3. سوال باید واضح، مشخص و قابل پاسخ باشد

فقط سوال را بنویسید، بدون توضیح اضافی."""
            },
            {
                "role": "user",
                "content": f"مشکل: {problem}\n\nاولین سوال چرا را بپرس:"
            }
        ]
        
        return await self._call_ai(messages)
    
    async def validate_and_generate_next(
        self, 
        problem: str, 
        steps: List[WhyStep], 
        current_answer: str
    ) -> Tuple[bool, str, Optional[str], bool, Optional[str], Optional[List[str]]]:
        """
        بررسی پاسخ و تولید سوال بعدی
        
        Returns:
            - is_valid: آیا پاسخ معتبر است
            - next_question_or_message: سوال بعدی یا پیام توضیحی
            - clarification: در صورت نیاز به توضیح بیشتر
            - is_root_found: آیا به ریشه رسیدیم
            - root_cause: علت ریشه‌ای (اگر پیدا شد)
            - recommendations: پیشنهادات (اگر ریشه پیدا شد)
        """
        
        # ساخت تاریخچه مکالمه
        history = "\n".join([
            f"سوال {s.step_number}: {s.question}\nپاسخ {s.step_number}: {s.answer}"
            for s in steps if s.answer
        ])
        
        current_step = len(steps) + 1
        last_question = steps[-1].question if steps else "سوال اولیه"
        
        messages = [
            {
                "role": "system",
                "content": """شما متخصص تحلیل 5 Whys هستید.

وظایف شما:
1. بررسی کنید پاسخ کاربر منطقی و مرتبط با سوال است
2. تشخیص دهید آیا به ریشه اصلی مشکل رسیده‌ایم
3. اگر پاسخ نامناسب است، درخواست توضیح بیشتر کنید
4. اگر به ریشه نرسیده‌ایم، سوال چرای بعدی را بپرسید

پاسخ را به فرمت JSON بدهید:
{
    "is_valid": true/false,
    "needs_clarification": true/false,
    "clarification_message": "پیام توضیحی اگر نیاز است",
    "is_root_found": true/false,
    "next_question": "سوال بعدی اگر ریشه پیدا نشده",
    "root_cause": "علت ریشه‌ای اگر پیدا شد",
    "recommendations": ["پیشنهاد 1", "پیشنهاد 2"] // اگر ریشه پیدا شد
}"""
            },
            {
                "role": "user",
                "content": f"""مشکل اصلی: {problem}

تاریخچه:
{history}

سوال فعلی (مرحله {current_step}): {last_question}
پاسخ کاربر: {current_answer}

تحلیل کن و پاسخ JSON بده:"""
            }
        ]
        
        response = await self._call_ai(messages)
        
        # پارس کردن JSON
        try:
            # پیدا کردن JSON در پاسخ
            start = response.find('{')
            end = response.rfind('}') + 1
            json_str = response[start:end]
            data = json.loads(json_str)
            
            return (
                data.get("is_valid", True),
                data.get("next_question", ""),
                data.get("clarification_message"),
                data.get("is_root_found", False),
                data.get("root_cause"),
                data.get("recommendations", [])
            )
        except (json.JSONDecodeError, ValueError):
            # اگر JSON معتبر نبود، سوال ساده بپرس
            return (True, f"چرا {current_answer}?", None, False, None, None)
    
    async def generate_summary(
        self, 
        problem: str, 
        steps: List[WhyStep]
    ) -> Tuple[str, List[str]]:
        """تولید خلاصه و پیشنهادات نهایی"""
        
        history = "\n".join([
            f"چرا {s.step_number}: {s.question}\nپاسخ: {s.answer}"
            for s in steps if s.answer
        ])
        
        messages = [
            {
                "role": "system",
                "content": """بر اساس تحلیل 5 Whys انجام شده:
1. علت ریشه‌ای را مشخص کن
2. 3-5 پیشنهاد عملی برای حل ارائه بده

پاسخ JSON:
{
    "root_cause": "علت ریشه‌ای",
    "recommendations": ["پیشنهاد 1", "پیشنهاد 2", ...]
}"""
            },
            {
                "role": "user",
                "content": f"مشکل: {problem}\n\nتحلیل:\n{history}"
            }
        ]
        
        response = await self._call_ai(messages)
        
        try:
            start = response.find('{')
            end = response.rfind('}') + 1
            data = json.loads(response[start:end])
            return data["root_cause"], data["recommendations"]
        except:
            return "نیاز به بررسی بیشتر", ["تحلیل را با جزئیات بیشتر تکرار کنید"]