# 5 Whys Root Cause Analyzer

تحلیلگر هوشمند ریشه‌یابی مشکلات با تکنیک 5 چرا

## 🚀 ویژگی‌های جدید

- **طراحی مدرن**: رابط کاربری به‌روزشده با گرادیان‌های مورب و انیمیشن‌های شناور
- **فونت فارسی**: استفاده از فونت Vazirmatn برای نمایش بهینه متن فارسی
- **تجربه کاربری بهبودیافته**: طراحی ریسپانسیو با افکت‌های hover و انتقال‌های نرم
- **پشتیبانی از چند مدل AI**: پشتیبانی از Liara AI، OpenRouter و مدل‌های محلی

## 🛠️ نصب و راه‌اندازی

### روش اول: Docker (توصیه شده)

1. **راه‌اندازی با Docker Compose**:
   ```bash
   docker-compose up -d
   ```
   
2. **راه‌اندازی تولید با Nginx**:
   ```bash
   docker-compose --profile production up -d
   ```

3. **دسترسی به اپلیکیشن**:
   - معمولی: http://localhost:8000
   - با Nginx: http://localhost

### روش دوم: محیط توسعه محلی

1. **نصب وابستگی‌ها**:
   ```bash
   pip install -r requirements.txt
   ```

2. **راه‌اندازی سرور**:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## ⚙️ پیکربندی

### تنظیمات محیطی

فایل `.env` را برای تنظیم سرویس AI مورد نظر ویرایش کنید:

```bash
# Liara AI (پیش‌فرض)
AI_BASE_URL=https://ai.liara.ir/api/68f7a6d4117eafa29010df94/v1
AI_API_KEY=your_api_key_here
AI_MODEL_ID=qwen/qwen3-32b

# OpenRouter
OPENROUTER_API_KEY=your_openrouter_key
OPENROUTER_MODEL=xiaomi/mimo-v2-flash:free

# OpenAI
AI_BASE_URL=https://api.openai.com/v1
AI_API_KEY=your_openai_key
AI_MODEL_ID=gpt-3.5-turbo
```

### مدل‌های پشتیبانی شده

- `qwen/qwen3-32b` (Liara AI)
- `gpt-3.5-turbo` (OpenAI)
- `gpt-4` (OpenAI)
- `claude-3-sonnet` (Anthropic)
- `gemini-pro` (Google)
- `xiaomi/mimo-v2-flash:free` (OpenRouter)

## 🐳 Docker

### ساخت تصویر

```bash
docker build -t 5whys-analyzer .
```

### اجرای کانتینر

```bash
docker run -p 8000:8000 \
  -e AI_BASE_URL=https://ai.liara.ir/api/68f7a6d4117eafa29010df94/v1 \
  -e AI_API_KEY=your_key \
  -e AI_MODEL_ID=qwen/qwen3-32b \
  5whys-analyzer
```

## ☁️ استقرار در Render

این پروژه برای استقرار در Render آماده است. فایل `render.yaml` شامل تنظیمات لازم می‌باشد.

### مراحل استقرار

1. ریپازیتوری را به Render متصل کنید
2. متغیرهای محیطی AI را در تنظیمات محیط Render تنظیم کنید
3. سرویس را استقرار دهید

## 📁 ساختار پروژه

```
5whys-analyzer/
├── app/
│   ├── main.py              # نقطه ورود اپلیکیشن
│   ├── models/
│   │   └── schemas.py       # اسکیمای Pydantic
│   └── services/
│       └── ai_service.py    # سرویس هوش مصنوعی
├── static/
│   ├── index.html           # صفحه اصلی
│   ├── css/
│   │   ├── input.css        # ورودی Tailwind
│   │   └── output.css       # خروجی Tailwind
│   └── js/                  # اسکریپت‌های جاوااسکریپت
├── Dockerfile              # Dockerfile اپلیکیشن
├── docker-compose.yml      # تنظیمات Docker Compose
├── nginx.conf              # پیکربندی Nginx
├── requirements.txt        # وابستگی‌های پایتون
├── .env                    # تنظیمات محیطی
└── README.md               # این فایل
```

## 🔧 توسعه

### استفاده از مدل‌های محلی

برای استفاده از مدل‌های محلی مانند Ollama:

```bash
# نصب Ollama
curl -fsSL https://ollama.com/install.sh | sh

# اجرای مدل
ollama run llama2

# تنظیم محیط
AI_BASE_URL=http://localhost:11434/api
AI_API_KEY=ollama
AI_MODEL_ID=llama2
```

## 🤝 مشارکت

برای مشارکت در این پروژه:

1. فورک کنید
2. شاخه جدید ایجاد کنید: `git checkout -b feature-name`
3. تغییرات خود را کامیت کنید: `git commit -am 'Add feature'`
4. شاخه خود را پوش کنید: `git push origin feature-name`
5. یک Pull Request ایجاد کنید

## 📄 مجوز

این پروژه تحت مجوز MIT منتشر شده است. برای اطلاعات بیشتر [LICENSE](LICENSE) را مشاهده کنید.

## 🙏 سازنده

طراحی و توسعه توسط [آراز شاه‌کرمی](https://araz.me)

🌐 [araz.me](https://araz.me) | 📧 [araz@araz.me](mailto:araz@araz.me)