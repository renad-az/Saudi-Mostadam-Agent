import os
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

def get_agent_response(user_input: str, df_agent: pd.DataFrame) -> str:
    query = user_input.strip().lower()

    # --- ردود السلام ---
    greetings = ["السلام", "سلام", "عليكم", "هلا", "مرحبا", "مرحباً", "حياك", "صباح", "مساء"]
    if any(w in query for w in greetings) and "محتوى الملف" not in query:
        return (
            "وعليكم السلام ورحمة الله وبركاته، ويا هلا ومسهلا! ⚡\n"
            "أرحبِ في مستشار مستدام السعودية الذكي.\n"
            "لو عندك تقرير compliance أو ملف تبيني أحلله، ارفعيه وأنا حاضر."
        )

    # --- الحالات عالية الخطورة (بدون PDF) ---
    risk_keywords = ["خطورة", "عالي", "عالية", "urgent", "high risk"]
    if any(w in query for w in risk_keywords) and "محتوى الملف" not in query:
        high_risk = df_agent[df_agent["Action_Priority"] == "Urgent Action Required"]
        if not high_risk.empty:
            reply = f"🚨 **وجدت {len(high_risk)} منشأة وضعها حرج وبحاجة لإجراء عاجل:**\n\n"
            for _, row in high_risk.iterrows():
                reply += f"- **{row['PrimaryPropertyType']}** | EUI: `{row['SiteEUI(kBtu/sf)']}`\n"
            return reply
        return "✅ نظام المراقبة يشير: لا توجد مبانٍ في نطاق الخطورة العالية حالياً."

    # --- ملخص الامتثال (بدون PDF) ---
    status_keywords = ["حالة", "ملخص", "امتثال", "status", "summary", "كود"]
    if any(w in query for w in status_keywords) and "محتوى الملف" not in query:
        if "SBC_Status" in df_agent.columns:
            stats = df_agent["SBC_Status"].value_counts()
            return (
                f"📊 **ملخص الامتثال لكود البناء السعودي (SBC):**\n\n"
                f"- ✅ منشآت ممتثلة: `{stats.get('Compliant', 0)}`\n"
                f"- ⚠️ منشآت مخالفة: `{stats.get('Non-Compliant', 0)}`"
            )

    # --- إرسال لـ Gemini ---
    if not api_key:
        return (
            "❌ **مفتاح GEMINI_API_KEY غير موجود.**\n\n"
            "تأكدي من وجود ملف `.env` في مجلد المشروع وفيه:\n"
            "`GEMINI_API_KEY=your_key_here`"
        )

    v_total = len(df_agent)
    v_fail  = len(df_agent[df_agent['SBC_Status'].str.contains("Non-Compliant", na=False)]) if 'SBC_Status' in df_agent.columns else 0
    v_co2   = df_agent['CO2_Emissions_kg'].sum() if 'CO2_Emissions_kg' in df_agent.columns else 0
    has_pdf = "محتوى الملف" in user_input

    pdf_instruction = (
        "لديك بيانات من ملف مستخرج في النص أدناه. "
        "اقرأها بعناية واستخرج منها المعطيات وأجب على سؤال المستخدم بناءً عليها. "
        "اذكر الأرقام صراحةً في ردك وربطها بمعايير كفاءة الطاقة وكود البناء السعودي SBC.\n"
    ) if has_pdf else ""

    prompt_text = (
        f"أنت مستشار استدامة سعودي خبير في منصة مستدام السعودية (Saudi Mostadam). أجب بلهجة سعودية واضحة، لبقة واحترافية.\n"
        f"{pdf_instruction}"
        f"بيانات النظام الحالية: إجمالي المباني={v_total}، المنشآت المخالفة={v_fail}، إجمالي الانبعاثات={v_co2:.1f} كجم CO2.\n\n"
        f"{user_input}"
    )

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    payload = {"contents": [{"parts": [{"text": prompt_text}]}]}

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)

        if response.status_code == 200:
            data = response.json()
            candidates = data.get("candidates", [])
            if not candidates:
                return "⚠️ تعذر الحصول على نتائج مباشرة من وحدة الذكاء الاصطناعي."
            content = candidates[0].get("content", {})
            parts = content.get("parts", [])
            if not parts:
                return "⚠️ تم استلام محتوى فارغ من الخادم."
            text = parts[0].get("text", "")
            return text

        elif response.status_code == 400:
            return f"❌ خطأ في تكوين الطلب (400).\nالتفاصيل: {response.text[:150]}"
        elif response.status_code == 403:
            return "❌ خطأ 403: مفتاح التحقق غير مصرح له. يرجى مراجعة صلاحيات الحساب على Google AI Studio."
        elif response.status_code == 429:
            return "⚠️ تم تجاوز حد الطلبات المتزامنة، يرجى الانتظار قليلاً."
        else:
            return f"⚠️ خطأ غير معروف بالنظام {response.status_code}."

    except requests.exceptions.Timeout:
        return "⏱️ انتهت مهلة الاتصال بالخادم، يرجى المحاولة مجدداً."
    except requests.exceptions.ConnectionError:
        return "🌐 تعذّر الاتصال بالشبكة، تأكدي من اتصال الإنترنت."
    except Exception as e:
        return f"❌ خطأ غير متوقع في المعالجة: {type(e).__name__}"