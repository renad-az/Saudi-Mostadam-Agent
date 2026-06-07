import os
import joblib
import pandas as pd
import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import base64
import pypdf

from agent import get_agent_response
from src.dashboard import show_dashboard

# --- دالة استخراج النص من ملف PDF ---
def extract_text_from_pdf(uploaded_file):
    reader = pypdf.PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"
    return text.strip()

# --- إعدادات الصفحة والهوية البصرية ---
st.set_page_config(
    page_title="Saudi Mostadam Agent - نظام مستدام السعودية",
    page_icon="🇸🇦",
    layout="wide"
)

# تخصيص المظهر (CSS) ليتناسب مع ألوان الاستدامة والذكاء الاصطناعي الفاخر
st.markdown("""
    <style>
    .main { background-color: #0a1628 !important; color: #ffffff; }
    [data-testid="stAppViewContainer"] {
        background-color: #0a1628 !important;
        background-image: radial-gradient(ellipse at top left, #0d2a1f 0%, #0a1628 50%, #060e1a 100%) !important;
    }
    [data-testid="stApp"] { background-color: #0a1628 !important; }
    [data-testid="stSidebar"] { background-color: #0d1f35 !important; }
    [data-testid="stMainBlockContainer"] {
        padding-top: 0rem !important;
        padding-bottom: 0.2rem !important;
        padding-left: 2.5rem !important;
        padding-right: 2.5rem !important;
    }
    [data-testid="stHeader"], .stDeployButton { display: none !important; }
    [data-testid="stImage"] img {
        max-height: 150px !important;
        object-fit: contain !important;
        margin-top: 0px !important;
        padding-top: 0px !important;
    }
    .stButton>button {
        background: linear-gradient(135deg, #00c896, #00adb5);
        color: #0a1628;
        border-radius: 25px;
        font-weight: bold;
        border: none;
        padding: 0.5rem 2rem;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #00ff87, #00d4aa);
        transform: translateY(-2px);
        box-shadow: 0 4px 20px rgba(0, 200, 150, 0.4);
    }
    h1, h2, h3 { color: #ffffff !important; font-family: 'Inter', sans-serif; }
    .modern-card {
        background: linear-gradient(145deg, #0d2040, #0a1a35);
        padding: 30px;
        border-radius: 20px;
        min-height: 220px;
        border: 1px solid rgba(0, 200, 150, 0.2);
        transition: transform 0.3s, border-color 0.3s;
    }
    .modern-card:hover {
        transform: translateY(-5px);
        border-color: rgba(0, 255, 135, 0.6);
        box-shadow: 0 8px 30px rgba(0, 200, 150, 0.15);
    }
    .card-icon { font-size: 30px; margin-bottom: 15px; display: block; }
    .card-title { color: #ffffff; font-size: 20px; font-weight: bold; margin-bottom: 10px; }
    .card-text { color: #8ba5c4; font-size: 14px; line-height: 1.6; }
    .pdf-loaded-badge {
        background: linear-gradient(135deg, #00c896, #00adb5);
        color: #0a1628;
        font-weight: bold;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 13px;
        display: inline-block;
        margin-bottom: 10px;
    }
    div[data-testid="stRadio"] > div {
        display: flex; flex-direction: row; gap: 10px;
        background-color: transparent !important;
    }
    div[data-testid="stRadio"] label {
        background-color: rgba(13, 32, 64, 0.8);
        color: #8ba5c4;
        padding: 8px 22px !important;
        border-radius: 50px !important;
        border: 1px solid rgba(0, 200, 150, 0.25) !important;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    div[data-testid="stRadio"] label div[data-testid="stMarkdownContainer"] p {
        font-size: 14px !important; font-weight: 500;
    }
    div[data-testid="stRadio"] label [data-testid="stWidgetCaption"] { display: none; }
    div[data-testid="stRadio"] [data-baseweb="radio"] > div:first-child { display: none !important; }
    div[data-testid="stRadio"] label:has(input:checked) {
        background: linear-gradient(135deg, #00c896, #00adb5) !important;
        color: #0a1628 !important;
        border: 1px solid transparent !important;
        font-weight: bold;
    }
    [data-testid="stChatMessageContainer"] { direction: rtl !important; }
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p {
        text-align: right !important; direction: rtl !important;
    }
    [data-testid="stChatInput"] textarea {
        direction: rtl !important;
        text-align: right !important;
        background-color: #0d2040 !important;
        border: 1px solid rgba(0, 200, 150, 0.3) !important;
        color: #ffffff !important;
        border-radius: 15px !important;
    }
    [data-testid="stChatMessage"] { flex-direction: row-reverse !important; }
    [data-testid="stSelectbox"] > div,
    [data-testid="stNumberInput"] input {
        background-color: #0d2040 !important;
        border: 1px solid rgba(0, 200, 150, 0.3) !important;
        color: #ffffff !important;
        border-radius: 10px !important;
    }
    [data-testid="metric-container"] {
        background-color: #0d2040 !important;
        border: 1px solid rgba(0, 200, 150, 0.2) !important;
        border-radius: 15px !important;
        padding: 15px !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- إدارة اللوقو والهوية البصرية ---
logo_path = "logo.png"
if not os.path.exists(logo_path):
    logo_path = os.path.join("Sec", "logo.png.png")

if os.path.exists(logo_path):
    col_space1, col_logo, col_space2 = st.columns([0.6, 4, 0.6])
    with col_logo:
        st.image(logo_path, use_container_width=True)
else:
    st.markdown("<h1 style='text-align: center; color: #00ff87; margin-bottom: 0px;'>🌱⚡ Saudi Mostadam Agent</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #8ba5c4; font-size: 18px; margin-top: 0px;'>نظام مستدام السعودية الذكي لإدارة الطاقة والامتثال</p>", unsafe_allow_html=True)

# --- جلب وإعداد البيانات ومسارات النماذج ---
INPUT_FILE = os.path.join("data", "processed", "agent_results.csv")
MODEL_FILE = os.path.join("models", "compliance_model.pkl")

if os.path.exists(INPUT_FILE):
    df_agent = pd.read_csv(INPUT_FILE)
else:
    # بيانات افتراضية متوافقة لضمان عمل الواجهة حتى في غياب الملف
    df_agent = pd.DataFrame({
        "PrimaryPropertyType": ["Office", "Hotel", "Warehouse", "Office", "School", "Hospital"],
        "PropertyGFATotal": [55000, 78000, 110000, 32000, 46000, 95000],
        "SiteEUI(kBtu/sf)": [72.1, 98.4, 42.0, 120.5, 58.2, 145.0],
        "SiteEnergyUse(kBtu)": [3965000, 7675200, 4620000, 3856000, 2677200, 13775000],
        "CO2_Emissions_kg": [14200, 29100, 10500, 24300, 9100, 48000],
        "SBC_Status": ["Compliant", "Non-Compliant", "Compliant", "Non-Compliant", "Compliant", "Non-Compliant"],
        "Risk_Level": ["Low Risk", "Medium Risk", "Low Risk", "High Risk", "Low Risk", "High Risk"],
        "Exceedance_Percentage": [0, 18, 0, 48, 0, 65],
        "Action_Priority": ["Monitor", "Action Recommended", "Monitor", "Urgent Action Required", "Monitor", "Urgent Action Required"],
        "Agent_Explanation": ["Compliant building.", "Medium risk. Optimize HVAC.", "Compliant.", "High risk. Immediate audit required.", "Compliant.", "Critical risk. Retrofitting needed."]
    })

# --- تهيئة الذاكرة المؤقتة لـ Session State ---
if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""
if "pdf_filename" not in st.session_state:
    st.session_state.pdf_filename = ""
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": (
            "أرحبِ يا هلا ومسهلا بك في مستشارك الذكي لنظام مستدام السعودية 🌱⚡\n"
            "البيانات وسجلات الاستهلاك قدامي وأمورنا زين الحمد لله.\n"
            "تقدري ترفعي ملف PDF لفاتورة طاقة أو تقرير مراجعة بيئية وأنا بحللها لك فوراً، سمّي وش بغيتي تسأليني عنه؟"
        )}
    ]

# --- قائمة التنقل العلوية المحدثة ---
st.markdown("<h4 style='color:#ffffff; margin-bottom:20px; font-weight:bold; font-size:28px;'>Unified Platform Interface</h4>", unsafe_allow_html=True)
tabs = ["Overview", "AI Chat Agent", "Smart Dashboard", "Predictive Engine", "Advanced Analytics"]
selected_tab = st.radio("Navigation Menu", tabs, horizontal=True, label_visibility="collapsed")
st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# 1. Overview Tab
# ==========================================
if selected_tab == "Overview":
    col_b1, col_b2, col_b3 = st.columns(3, gap="large")
    with col_b1:
        st.markdown("""
            <div class='modern-card'>
                <span class='card-icon' style='color:#00adb5;'>🤖</span>
                <div class='card-title'>Saudi Mostadam Agent</div>
                <div class='card-text'>Real-time conversational interface to query PDF bills, legal frameworks, and consumption metadata using Generative AI.</div>
            </div>""", unsafe_allow_html=True)
    with col_b2:
        st.markdown("""
            <div class='modern-card'>
                <span class='card-icon' style='color:#00ff87;'>📊</span>
                <div class='card-title'>Smart Dashboard</div>
                <div class='card-text'>Digitized PDF data and metrics visualized into immediate KPIs for Savings, Carbon Footprint, and Alerts.</div>
            </div>""", unsafe_allow_html=True)
    with col_b3:
        st.markdown("""
            <div class='modern-card'>
                <span class='card-icon' style='color:#00f2fe;'>🔮</span>
                <div class='card-title'>Predictive Engine</div>
                <div class='card-text'>Forecasting energy demand and compliance metrics using core Machine Learning Regression and Classification models.</div>
            </div>""", unsafe_allow_html=True)

# ==========================================
# 2. AI Chat Agent Tab
# ==========================================
elif selected_tab == "AI Chat Agent":
    st.subheader("🤖 Saudi Mostadam Conversational Agent")

    # واجهة رفع التقارير والفواتير
    uploaded_pdf = st.file_uploader(
        "📎 ارفع فاتورة الطاقة أو تقرير الامتثال للمنشأة (PDF)",
        type="pdf",
        help="سيتم استخراج البيانات والأنماط من الملف وتحليلها هندسياً في المحادثة"
    )

    # معالجة الملف واستخراج النصوص برمجياً
    if uploaded_pdf is not None and uploaded_pdf.name != st.session_state.pdf_filename:
        with st.spinner("⚙️ جاري استخراج البيانات وفحص مطابقتها للمواصفات..."):
            extracted = extract_text_from_pdf(uploaded_pdf)
        if extracted:
            st.session_state.pdf_text = extracted
            st.session_state.pdf_filename = uploaded_pdf.name
            confirm_msg = (
                f"✅ تم رفع وقراءة الملف **{uploaded_pdf.name}** بنجاح وجاهز للمطابقة.\n\n"
                f"يمكنك الآن سؤالي عن:\n"
                f"- حالة الامتثال الحالية والمستقبلية للكود السعودي للبناء (SBC)\n"
                f"- كفاءة استهلاك الطاقة ومكامن الهدر في المبنى\n"
                f"- البصمة الكربونية ومعدل انبعاثات الغازات\n"
                f"- الحلول والتوصيات الهندسية والإجرائية التصحيحية"
            )
            st.session_state.messages.append({"role": "assistant", "content": confirm_msg})
        else:
            st.warning("⚠️ لم يتم استخراج أي نصوص، يرجى التأكد من أن الملف نصي وليس ممسوحاً ضوئياً كصورة فقط.")

    # شارة الملف النشط
    if st.session_state.pdf_filename:
        st.markdown(
            f"<span class='pdf-loaded-badge'>📄 الملف المستهدف حالياً: {st.session_state.pdf_filename}</span>",
            unsafe_allow_html=True
        )
        if st.button("🗑️ إزالة الملف الحالي", key="clear_pdf"):
            st.session_state.pdf_text = ""
            st.session_state.pdf_filename = ""
            st.rerun()

    st.markdown("---")

    # عرض تدفق المحادثة بالاتجاه الصحيح RTL
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # معالجة مدخلات المستخدم والدمج الذكي مع سياق الـ PDF
    if user_input := st.chat_input("اسألي عن معايير الامتثال، كفاءة الاستهلاك، البصمة الكربونية..."):

        if st.session_state.pdf_text:
            enriched_input = (
                f"محتوى مستند المنشأة المرفوع ({st.session_state.pdf_filename}):\n"
                f"{st.session_state.pdf_text[:4000]}\n\n"
                f"سؤال المهندس/المستخدم: {user_input}"
            )
        else:
            enriched_input = user_input

        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        with st.chat_message("assistant"):
            with st.spinner("🔍 جاري التحليل وصياغة التوصيات الحصيفة..."):
                reply = get_agent_response(enriched_input, df_agent)
            st.write(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})

# ==========================================
# 3. Smart Dashboard Tab
# ==========================================
elif selected_tab == "Smart Dashboard":
    show_dashboard(df_agent)

# ==========================================
# 4. Predictive Engine Tab
# ==========================================
elif selected_tab == "Predictive Engine":
    st.subheader("🔮 Predictive Compliance Engine (SBC)")
    col_l, col_r = st.columns(2)
    with col_l:
        ptype = st.selectbox("Property Type", df_agent["PrimaryPropertyType"].unique())
        gfa = st.number_input("Property GFA (sf)", min_value=0, value=60000)
        eui = st.number_input("Site EUI (kBtu/sf)", min_value=0.0, value=80.0)
    with col_r:
        use = st.number_input("Total Energy Use (kBtu)", min_value=0, value=4000000)
        co2 = st.number_input("CO2 Emissions (kg)", min_value=0, value=18000)

    if st.button("Run ML Compliance Forecast"):
        input_data = pd.DataFrame([{
            "PrimaryPropertyType": ptype, "PropertyGFATotal": gfa,
            "SiteEUI(kBtu/sf)": eui, "SiteEnergyUse(kBtu)": use, "CO2_Emissions_kg": co2
        }])
        input_data = input_data.replace([np.inf, -np.inf], np.nan).fillna(0)
        is_empty_input = (eui == 0 or co2 == 0 or gfa == 0)
        is_excessive_load = (eui > 120 or co2 > 40000)

        # استدعاء نموذج تعلم الآلة
        if os.path.exists(MODEL_FILE):
            try:
                model = joblib.load(MODEL_FILE)
                prediction = model.predict(input_data)[0]
                res = "Compliant" if (prediction == "Compliant" or prediction == 0) and not is_empty_input and not is_excessive_load else "Non-Compliant"
            except Exception:
                res = "Non-Compliant"
        else:
            res = "Non-Compliant" if (is_empty_input or is_excessive_load) else "Compliant"

        if res == "Compliant":
            st.success(f"🎉 Model Forecast: **{res} (الملف مطابق للمعايير الوطنية)**")
        else:
            st.error(f"⚠️ Model Forecast: **{res} (تنبيه: يوجد خطر عدم امتثال للوائح)**")

# ==========================================
# 5. Advanced Analytics Tab
# ==========================================
elif selected_tab == "Advanced Analytics":
    st.subheader("📈 Statistical Analysis & Executive Reports")

    ch1, ch2 = st.columns(2)
    with ch1:
        st.write("#### Energy Intensity Distribution")
        f1 = px.bar(df_agent, x="PrimaryPropertyType", y="SiteEUI(kBtu/sf)", color="SBC_Status", barmode="group",
                    color_discrete_map={"Compliant": "#00ff87", "Non-Compliant": "#ff4b4b"}, template="plotly_dark")
        f1.update_layout(paper_bgcolor="#0d2040", plot_bgcolor="#0d2040")
        st.plotly_chart(f1, use_container_width=True)
    with ch2:
        st.write("#### Carbon Footprint Relative to Size")
        f2 = px.scatter(df_agent, x="PropertyGFATotal", y="CO2_Emissions_kg", size="SiteEUI(kBtu/sf)", color="Risk_Level",
                        color_discrete_map={"Low Risk": "#00ff87", "Medium Risk": "#00adb5", "High Risk": "#ff4b4b"}, template="plotly_dark")
        f2.update_layout(paper_bgcolor="#0d2040", plot_bgcolor="#0d2040")
        st.plotly_chart(f2, use_container_width=True)

    st.markdown("---")

    # إنتاج وتصدير المخططات الإحصائية كمستندات قابلة للتحميل
    fig, ax = plt.subplots(figsize=(6, 3))
    sns.countplot(data=df_agent, x="Action_Priority", palette=["#00ff87", "#00adb5", "#ff4b4b"], ax=ax)
    plt.title("Action Priority Distribution", color="black")
    fig.savefig("analytics_chart.png", bbox_inches="tight", dpi=150)
    plt.close(fig)

    with open("analytics_chart.png", "rb") as img_file:
        st.download_button(label="📥 Download Generated Analytics Chart (PNG)", data=img_file,
                           file_name="Mostadam_Priority_Dist.png", mime="image/png")

    st.subheader("📋 Executive Sustainability Report (PDF)")

    # دالة توليد التقارير التنفيذية بصيغة PDF ومطابقتها للمظهر العام للمنصة
    def generate_pdf_report():
        f1.write_image("temp_chart1.png", width=700, height=350, scale=2)
        f2.write_image("temp_chart2.png", width=700, height=350, scale=2)
        with open("temp_chart1.png", "rb") as f:
            c1_b64 = base64.b64encode(f.read()).decode('utf-8')
        with open("temp_chart2.png", "rb") as f:
            c2_b64 = base64.b64encode(f.read()).decode('utf-8')
        html_report = f"""<!DOCTYPE html><html><head><meta charset="UTF-8">
        <style>
            @page {{ size: a4; margin: 2cm; }}
            body {{ font-family: Helvetica, Arial, sans-serif; color: #ffffff; background: #0a1628; }}
            .title {{ color: #00c896; font-size: 24px; font-weight: bold; }}
            .section-title {{ color: #00ff87; font-size: 16px; font-weight: bold; border-left: 4px solid #00ff87; padding-left: 8px; }}
            .chart-box {{ background: #0d2040; border: 1px solid #1f3a5f; border-radius: 8px; padding: 10px; text-align: center; margin: 15px 0; }}
            .insights {{ background: rgba(0,200,150,0.04); border: 1px solid rgba(0,200,150,0.15); border-radius: 8px; padding: 15px; font-size: 13px; line-height: 1.6; }}
        </style></head><body>
        <div class="title">📋 Executive Analytics Report — Saudi Mostadam Agent</div>
        <p style="color:#8ba5c4;">Energy Intensity Metrics & SBC Compliance Audit</p>
        <div class="section-title">1. Energy Intensity Distribution</div>
        <div class="chart-box"><img src="data:image/png;base64,{c1_b64}" style="width:100%;"></div>
        <div class="insights"><strong>AI Insight:</strong> Hospitality and Healthcare assets record highest EUI intensity.</div>
        <div class="section-title">2. Carbon Footprint Relative to Size</div>
        <div class="chart-box"><img src="data:image/png;base64,{c2_b64}" style="width:100%;"></div>
        <div class="insights"><strong>AI Insight:</strong> Direct linear correlation between GFA and total CO2 emissions.</div>
        </body></html>"""
        from xhtml2pdf import pisa
        with open("Mostadam_Executive_Report.pdf", "w+b") as result_file:
            pisa.pisaDocument(html_report, dest=result_file)
        for f in ["temp_chart1.png", "temp_chart2.png"]:
            if os.path.exists(f): os.remove(f)

    try:
        generate_pdf_report()
        col_pdf1, col_pdf2 = st.columns([3, 1])
        with col_pdf1:
            st.info("📄 Executive Sustainability Report generated successfully under Saudi Mostadam Framework.")
        with col_pdf2:
            with open("Mostadam_Executive_Report.pdf", "rb") as pdf_file:
                st.download_button(label="📥 Download PDF Report", data=pdf_file,
                                   file_name="Mostadam_Sustainability_Report.pdf", mime="application/pdf")
    except Exception as e:
        st.error(f"⚠️ Error creating PDF: {str(e)}")