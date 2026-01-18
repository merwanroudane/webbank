"""
╔══════════════════════════════════════════════════════════════════════════════╗
║     🌍 لوحة القيادة الاقتصادية الذكية - World Bank AI Dashboard              ║
║                                                                              ║
║     من إعداد: الدكتور مروان رودان                                            ║
║     Dr. Marwan Roudan                                                        ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import pandas as pd
import numpy as np
import requests
import json
import re
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from io import BytesIO
from datetime import datetime
import tempfile
import base64

# Google Gemini SDK
try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

# Model Configuration - Gemini 3.0 Flash Preview
GEMINI_MODEL_NAME = "gemini-3-flash-preview"

# ═══════════════════════════════════════════════════════════════════════════════
# 1. إعدادات الصفحة والتصميم المتقدم
# ═══════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="لوحة القيادة الاقتصادية | د. مروان رودان",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS مخصص بألوان دافئة - الشريط الجانبي على اليمين مع ألوان مرئية
st.markdown("""
<style>
    /* استيراد خط عربي جميل */
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700;800&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700&display=swap');
    
    * {
        font-family: 'Cairo', 'Tajawal', sans-serif;
    }
    
    /* الخلفية والألوان الأساسية - ألوان دافئة فاتحة */
    .stApp {
        background: linear-gradient(135deg, #FFF8E7 0%, #FDF5E6 50%, #FAEBD7 100%);
    }
    
    /* ═══════════════════════════════════════════════════════════════════════════
       نقل الشريط الجانبي إلى اليمين
       ═══════════════════════════════════════════════════════════════════════════ */
    
    section[data-testid="stSidebar"] {
        right: 0;
        left: auto !important;
        background: linear-gradient(180deg, #F5E6D3 0%, #EDE0D0 100%);
        border-left: 3px solid #D4AF37;
        border-right: none;
    }
    
    section[data-testid="stSidebar"] > div {
        right: 0;
        left: auto !important;
    }
    
    /* تعديل المحتوى الرئيسي */
    .main .block-container {
        padding-right: 1rem;
        padding-left: 1rem;
    }
    
    /* ═══════════════════════════════════════════════════════════════════════════
       تصحيح ألوان الشريط الجانبي - كل النصوص مرئية
       ═══════════════════════════════════════════════════════════════════════════ */
    
    /* عناوين الشريط الجانبي */
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] h4 {
        color: #8B7355 !important;
    }
    
    /* النصوص العادية في الشريط الجانبي */
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] div {
        color: #5D4E37 !important;
    }
    
    /* تسميات الحقول في الشريط الجانبي */
    section[data-testid="stSidebar"] .stTextInput label,
    section[data-testid="stSidebar"] .stTextArea label,
    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] .stMultiSelect label,
    section[data-testid="stSidebar"] .stCheckbox label,
    section[data-testid="stSidebar"] .stRadio label {
        color: #5D4E37 !important;
        font-weight: 600 !important;
    }
    
    /* حقول الإدخال في الشريط الجانبي */
    section[data-testid="stSidebar"] .stTextInput input,
    section[data-testid="stSidebar"] .stTextArea textarea {
        background-color: #FFFEF9 !important;
        border: 2px solid #D4AF37 !important;
        border-radius: 10px !important;
        color: #5D4E37 !important;
    }
    
    section[data-testid="stSidebar"] .stTextInput input::placeholder,
    section[data-testid="stSidebar"] .stTextArea textarea::placeholder {
        color: #A89880 !important;
    }
    
    /* القوائم المنسدلة في الشريط الجانبي */
    section[data-testid="stSidebar"] .stSelectbox > div > div {
        background-color: #FFFEF9 !important;
        border: 2px solid #D4AF37 !important;
        border-radius: 10px !important;
    }
    
    section[data-testid="stSidebar"] .stSelectbox > div > div > div {
        color: #5D4E37 !important;
    }
    
    /* خانات الاختيار في الشريط الجانبي */
    section[data-testid="stSidebar"] .stCheckbox label span {
        color: #5D4E37 !important;
    }
    
    /* Markdown في الشريط الجانبي */
    section[data-testid="stSidebar"] .stMarkdown,
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown span,
    section[data-testid="stSidebar"] .stMarkdown li {
        color: #5D4E37 !important;
    }
    
    /* ═══════════════════════════════════════════════════════════════════════════
       تصميم العنوان الرئيسي
       ═══════════════════════════════════════════════════════════════════════════ */
    
    .main-header {
        background: linear-gradient(135deg, #D4AF37 0%, #F4E4BA 50%, #D4AF37 100%);
        padding: 25px;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 8px 32px rgba(212, 175, 55, 0.4);
        border: 3px solid #996515;
    }
    
    .main-header h1 {
        color: #5D4E37;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
    }
    
    .main-header p {
        color: #6B5B45;
        font-size: 1.2em;
        margin-top: 10px;
        font-weight: 500;
    }
    
    /* ═══════════════════════════════════════════════════════════════════════════
       بطاقات المؤشرات
       ═══════════════════════════════════════════════════════════════════════════ */
    
    .metric-card {
        background: linear-gradient(145deg, #FFFEF9, #FFF8E7);
        padding: 25px;
        border-radius: 16px;
        box-shadow: 0 8px 25px rgba(212, 175, 55, 0.2);
        border: 2px solid #D4AF37;
        transition: all 0.3s ease;
        margin-bottom: 15px;
        text-align: center;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(212, 175, 55, 0.3);
    }
    
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #996515;
        margin: 0;
    }
    
    .metric-label {
        font-size: 0.95rem;
        color: #5D4E37;
        margin-top: 5px;
    }
    
    /* ═══════════════════════════════════════════════════════════════════════════
       الأزرار
       ═══════════════════════════════════════════════════════════════════════════ */
    
    .stButton > button {
        background: linear-gradient(135deg, #D4AF37 0%, #B8960C 100%);
        color: #FFFFFF;
        border: none;
        border-radius: 12px;
        padding: 12px 30px;
        font-weight: 700;
        font-size: 1.1em;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(212, 175, 55, 0.4);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #E5C158 0%, #D4AF37 100%);
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(212, 175, 55, 0.6);
    }
    
    /* ═══════════════════════════════════════════════════════════════════════════
       التبويبات
       ═══════════════════════════════════════════════════════════════════════════ */
    
    .stTabs [data-baseweb="tab-list"] {
        background-color: #F5E6D3;
        border-radius: 15px;
        padding: 8px;
        gap: 10px;
        border: 2px solid #D4AF37;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: #5D4E37 !important;
        border-radius: 10px;
        padding: 10px 20px;
        background-color: #FFF8E7;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #D4AF37 0%, #B8960C 100%) !important;
        color: #FFFFFF !important;
    }
    
    /* ═══════════════════════════════════════════════════════════════════════════
       القوائم المنسدلة - الصفحة الرئيسية
       ═══════════════════════════════════════════════════════════════════════════ */
    
    .stSelectbox > div > div {
        background-color: #FFFEF9 !important;
        border: 2px solid #D4AF37 !important;
        border-radius: 10px !important;
    }
    
    .stSelectbox > div > div > div {
        color: #5D4E37 !important;
    }
    
    .stSelectbox label {
        color: #5D4E37 !important;
    }
    
    /* قائمة الخيارات المنسدلة */
    [data-baseweb="menu"] {
        background-color: #FFFEF9 !important;
        border: 2px solid #D4AF37 !important;
    }
    
    [data-baseweb="menu"] li {
        color: #5D4E37 !important;
        background-color: #FFFEF9 !important;
    }
    
    [data-baseweb="menu"] li:hover {
        background-color: #F4E4BA !important;
        color: #5D4E37 !important;
    }
    
    [data-baseweb="select"] > div {
        background-color: #FFFEF9 !important;
        border-color: #D4AF37 !important;
    }
    
    [data-baseweb="select"] span {
        color: #5D4E37 !important;
    }
    
    [data-baseweb="popover"] {
        background-color: #FFFEF9 !important;
    }
    
    /* ═══════════════════════════════════════════════════════════════════════════
       MultiSelect
       ═══════════════════════════════════════════════════════════════════════════ */
    
    .stMultiSelect > div > div {
        background-color: #FFFEF9 !important;
        border: 2px solid #D4AF37 !important;
        border-radius: 10px !important;
    }
    
    .stMultiSelect > div > div > div {
        color: #5D4E37 !important;
    }
    
    .stMultiSelect label {
        color: #5D4E37 !important;
    }
    
    /* ═══════════════════════════════════════════════════════════════════════════
       حقول الإدخال
       ═══════════════════════════════════════════════════════════════════════════ */
    
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background-color: #FFFEF9 !important;
        border: 2px solid #D4AF37 !important;
        border-radius: 10px !important;
        color: #5D4E37 !important;
    }
    
    .stTextInput > div > div > input::placeholder,
    .stTextArea > div > div > textarea::placeholder {
        color: #A89880 !important;
    }
    
    .stTextInput label,
    .stTextArea label {
        color: #5D4E37 !important;
    }
    
    /* ═══════════════════════════════════════════════════════════════════════════
       خانات الاختيار والأزرار الراديوية
       ═══════════════════════════════════════════════════════════════════════════ */
    
    .stCheckbox label {
        color: #5D4E37 !important;
    }
    
    .stCheckbox label span {
        color: #5D4E37 !important;
    }
    
    .stRadio > div {
        color: #5D4E37 !important;
    }
    
    .stRadio label {
        color: #5D4E37 !important;
    }
    
    .stRadio label span {
        color: #5D4E37 !important;
    }
    
    /* ═══════════════════════════════════════════════════════════════════════════
       Slider
       ═══════════════════════════════════════════════════════════════════════════ */
    
    .stSlider label {
        color: #5D4E37 !important;
    }
    
    .stSlider > div > div {
        color: #5D4E37 !important;
    }
    
    /* ═══════════════════════════════════════════════════════════════════════════
       الجداول
       ═══════════════════════════════════════════════════════════════════════════ */
    
    .stDataFrame {
        border: 2px solid #D4AF37;
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 5px 20px rgba(212, 175, 55, 0.1);
    }
    
    /* ═══════════════════════════════════════════════════════════════════════════
       التنبيهات
       ═══════════════════════════════════════════════════════════════════════════ */
    
    .stSuccess {
        background-color: #F0FFF0 !important;
        border-left: 5px solid #D4AF37 !important;
        color: #5D4E37 !important;
    }
    
    .stInfo {
        background-color: #FFF8E7 !important;
        border-left: 5px solid #D4AF37 !important;
        color: #5D4E37 !important;
    }
    
    .stWarning {
        background-color: #FFFACD !important;
        border-left: 5px solid #FFD700 !important;
        color: #5D4E37 !important;
    }
    
    .stError {
        background-color: #FFE4E1 !important;
        border-left: 5px solid #CD5C5C !important;
        color: #8B4513 !important;
    }
    
    /* ═══════════════════════════════════════════════════════════════════════════
       التوسيعات (Expander)
       ═══════════════════════════════════════════════════════════════════════════ */
    
    .stExpander {
        background-color: #FFF8E7;
        border: 2px solid #D4AF37;
        border-radius: 12px;
    }
    
    .stExpander > div > div > div > div {
        color: #996515 !important;
    }
    
    /* ═══════════════════════════════════════════════════════════════════════════
       العناوين والنصوص
       ═══════════════════════════════════════════════════════════════════════════ */
    
    h1, h2, h3 {
        color: #996515 !important;
    }
    
    p, li, span {
        color: #5D4E37;
    }
    
    label {
        color: #5D4E37 !important;
    }
    
    /* ═══════════════════════════════════════════════════════════════════════════
       Footer
       ═══════════════════════════════════════════════════════════════════════════ */
    
    .footer {
        background: linear-gradient(135deg, #D4AF37 0%, #F4E4BA 50%, #D4AF37 100%);
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        margin-top: 40px;
        border: 3px solid #996515;
    }
    
    .footer p {
        color: #5D4E37;
        margin: 5px 0;
        font-weight: 600;
    }
    
    /* ═══════════════════════════════════════════════════════════════════════════
       Chat Container
       ═══════════════════════════════════════════════════════════════════════════ */
    
    .chat-container {
        background: linear-gradient(145deg, #FFFEF9 0%, #FFF8E7 100%);
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 8px 25px rgba(212, 175, 55, 0.15);
        border: 2px solid #D4AF37;
        margin: 20px 0;
    }
    
    .ai-response {
        background: linear-gradient(145deg, #FFF8E7 0%, #F4E4BA 100%);
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        border-left: 4px solid #D4AF37;
        color: #5D4E37;
    }
    
    .user-message {
        background: linear-gradient(145deg, #5D4E37 0%, #8B7355 100%);
        color: #FFF8E7;
        border-radius: 12px;
        padding: 15px 20px;
        margin: 10px 0;
        text-align: right;
    }
    
    /* ═══════════════════════════════════════════════════════════════════════════
       Report Section
       ═══════════════════════════════════════════════════════════════════════════ */
    
    .report-section {
        background: #FFFFFF;
        padding: 30px;
        border-radius: 16px;
        box-shadow: 0 5px 25px rgba(212, 175, 55, 0.15);
        margin: 20px 0;
        border-top: 4px solid #D4AF37;
    }
    
    /* ═══════════════════════════════════════════════════════════════════════════
       إخفاء عناصر Streamlit الافتراضية
       ═══════════════════════════════════════════════════════════════════════════ */
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Download buttons */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #D4AF37 0%, #B8960C 100%);
        color: #FFFFFF;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        color: #996515 !important;
        font-size: 2.2em !important;
        font-weight: 700 !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #5D4E37 !important;
    }
    
    /* Widget Labels */
    div[data-testid="stWidgetLabel"] {
        color: #5D4E37 !important;
    }
    
    div[data-testid="stWidgetLabel"] p {
        color: #5D4E37 !important;
    }
    
    /* Markdown Container */
    div[data-testid="stMarkdownContainer"] p {
        color: #5D4E37 !important;
    }
    
    div[data-testid="stMarkdownContainer"] li {
        color: #5D4E37 !important;
    }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# 2. جلب جميع المؤشرات والدول من API البنك الدولي
# ═══════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=86400, show_spinner=False)
def fetch_all_indicators_from_api():
    """
    جلب جميع المؤشرات المتاحة من البنك الدولي (أكثر من 16,000 مؤشر)
    """
    try:
        url = "https://api.worldbank.org/v2/indicator"
        params = {"format": "json", "per_page": 20000}
        response = requests.get(url, params=params, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 1 and data[1]:
                indicators = []
                for item in data[1]:
                    indicators.append({
                        "code": item.get("id", ""),
                        "name": item.get("name", ""),
                        "source": item.get("source", {}).get("value", "") if item.get("source") else ""
                    })
                return pd.DataFrame(indicators)
        return pd.DataFrame()
    except Exception as e:
        print(f"Error fetching indicators: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=86400, show_spinner=False)
def fetch_all_countries_from_api():
    """
    جلب جميع الدول والمناطق من البنك الدولي (أكثر من 300 دولة)
    """
    try:
        url = "https://api.worldbank.org/v2/country"
        params = {"format": "json", "per_page": 500}
        response = requests.get(url, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 1 and data[1]:
                countries = []
                for item in data[1]:
                    region_value = item.get("region", {}).get("value", "") if item.get("region") else ""
                    income_value = item.get("incomeLevel", {}).get("value", "") if item.get("incomeLevel") else ""
                    countries.append({
                        "code": item.get("id", ""),
                        "name": item.get("name", ""),
                        "region": region_value,
                        "incomeLevel": income_value
                    })
                return pd.DataFrame(countries)
        return pd.DataFrame()
    except Exception as e:
        print(f"Error fetching countries: {e}")
        return pd.DataFrame()


# ═══════════════════════════════════════════════════════════════════════════════
# 3. قاعدة بيانات المؤشرات الاقتصادية الشاملة (Fallback)
# ═══════════════════════════════════════════════════════════════════════════════

INDICATORS_DATABASE = {
    # المؤشرات الاقتصادية الرئيسية
    "الناتج المحلي الإجمالي": {"code": "NY.GDP.MKTP.CD", "name_en": "GDP (current US$)", "category": "اقتصادي"},
    "الناتج المحلي": {"code": "NY.GDP.MKTP.CD", "name_en": "GDP", "category": "اقتصادي"},
    "GDP": {"code": "NY.GDP.MKTP.CD", "name_en": "GDP", "category": "اقتصادي"},
    "نمو الناتج المحلي": {"code": "NY.GDP.MKTP.KD.ZG", "name_en": "GDP Growth", "category": "اقتصادي"},
    "GDP Growth": {"code": "NY.GDP.MKTP.KD.ZG", "name_en": "GDP Growth %", "category": "اقتصادي"},
    "الناتج المحلي للفرد": {"code": "NY.GDP.PCAP.CD", "name_en": "GDP per Capita", "category": "اقتصادي"},
    "GDP per Capita": {"code": "NY.GDP.PCAP.CD", "name_en": "GDP per Capita", "category": "اقتصادي"},
    
    # التجارة الخارجية
    "الصادرات": {"code": "NE.EXP.GNFS.CD", "name_en": "Exports (current US$)", "category": "تجارة"},
    "Exports": {"code": "NE.EXP.GNFS.CD", "name_en": "Exports", "category": "تجارة"},
    "صادرات": {"code": "NE.EXP.GNFS.CD", "name_en": "Exports", "category": "تجارة"},
    "الواردات": {"code": "NE.IMP.GNFS.CD", "name_en": "Imports (current US$)", "category": "تجارة"},
    "Imports": {"code": "NE.IMP.GNFS.CD", "name_en": "Imports", "category": "تجارة"},
    "واردات": {"code": "NE.IMP.GNFS.CD", "name_en": "Imports", "category": "تجارة"},
    "الميزان التجاري": {"code": "NE.RSB.GNFS.CD", "name_en": "Trade Balance", "category": "تجارة"},
    "نسبة الصادرات من الناتج": {"code": "NE.EXP.GNFS.ZS", "name_en": "Exports % of GDP", "category": "تجارة"},
    "نسبة الواردات من الناتج": {"code": "NE.IMP.GNFS.ZS", "name_en": "Imports % of GDP", "category": "تجارة"},
    
    # التضخم والأسعار
    "التضخم": {"code": "FP.CPI.TOTL.ZG", "name_en": "Inflation (CPI)", "category": "أسعار"},
    "Inflation": {"code": "FP.CPI.TOTL.ZG", "name_en": "Inflation", "category": "أسعار"},
    "معدل التضخم": {"code": "FP.CPI.TOTL.ZG", "name_en": "Inflation Rate", "category": "أسعار"},
    "مؤشر أسعار المستهلك": {"code": "FP.CPI.TOTL", "name_en": "Consumer Price Index", "category": "أسعار"},
    
    # سوق العمل
    "البطالة": {"code": "SL.UEM.TOTL.ZS", "name_en": "Unemployment Rate", "category": "عمل"},
    "Unemployment": {"code": "SL.UEM.TOTL.ZS", "name_en": "Unemployment", "category": "عمل"},
    "معدل البطالة": {"code": "SL.UEM.TOTL.ZS", "name_en": "Unemployment Rate", "category": "عمل"},
    "بطالة الشباب": {"code": "SL.UEM.1524.ZS", "name_en": "Youth Unemployment", "category": "عمل"},
    "القوى العاملة": {"code": "SL.TLF.TOTL.IN", "name_en": "Labor Force", "category": "عمل"},
    
    # السكان
    "السكان": {"code": "SP.POP.TOTL", "name_en": "Population", "category": "سكان"},
    "Population": {"code": "SP.POP.TOTL", "name_en": "Population", "category": "سكان"},
    "نمو السكان": {"code": "SP.POP.GROW", "name_en": "Population Growth", "category": "سكان"},
    "الكثافة السكانية": {"code": "EN.POP.DNST", "name_en": "Population Density", "category": "سكان"},
    "متوسط العمر": {"code": "SP.DYN.LE00.IN", "name_en": "Life Expectancy", "category": "سكان"},
    
    # المالية العامة
    "الدين العام": {"code": "GC.DOD.TOTL.GD.ZS", "name_en": "Government Debt % GDP", "category": "مالية"},
    "الإيرادات الحكومية": {"code": "GC.REV.XGRT.GD.ZS", "name_en": "Government Revenue % GDP", "category": "مالية"},
    "النفقات الحكومية": {"code": "GC.XPN.TOTL.GD.ZS", "name_en": "Government Expenditure % GDP", "category": "مالية"},
    
    # الاستثمار
    "الاستثمار الأجنبي": {"code": "BX.KLT.DINV.CD.WD", "name_en": "FDI Inflows", "category": "استثمار"},
    "FDI": {"code": "BX.KLT.DINV.CD.WD", "name_en": "Foreign Direct Investment", "category": "استثمار"},
    "إجمالي الاستثمار": {"code": "NE.GDI.TOTL.ZS", "name_en": "Gross Capital Formation % GDP", "category": "استثمار"},
    
    # القطاع المصرفي
    "الائتمان المحلي": {"code": "FS.AST.DOMS.GD.ZS", "name_en": "Domestic Credit % GDP", "category": "بنوك"},
    "سعر الفائدة": {"code": "FR.INR.RINR", "name_en": "Real Interest Rate", "category": "بنوك"},
    
    # التعليم والصحة
    "الإنفاق على التعليم": {"code": "SE.XPD.TOTL.GD.ZS", "name_en": "Education Expenditure % GDP", "category": "اجتماعي"},
    "الإنفاق على الصحة": {"code": "SH.XPD.CHEX.GD.ZS", "name_en": "Health Expenditure % GDP", "category": "اجتماعي"},
    "معدل الالتحاق بالتعليم": {"code": "SE.PRM.ENRR", "name_en": "School Enrollment Rate", "category": "اجتماعي"},
    
    # الطاقة والبيئة
    "استهلاك الطاقة": {"code": "EG.USE.PCAP.KG.OE", "name_en": "Energy Use per Capita", "category": "طاقة"},
    "انبعاثات CO2": {"code": "EN.ATM.CO2E.PC", "name_en": "CO2 Emissions per Capita", "category": "بيئة"},
    "الطاقة المتجددة": {"code": "EG.FEC.RNEW.ZS", "name_en": "Renewable Energy %", "category": "طاقة"},
}

# قاعدة بيانات الدول
COUNTRIES_DATABASE = {
    # الدول العربية
    "الجزائر": "DZA", "Algeria": "DZA", "جزائر": "DZA",
    "المغرب": "MAR", "Morocco": "MAR", "مغرب": "MAR",
    "تونس": "TUN", "Tunisia": "TUN",
    "مصر": "EGY", "Egypt": "EGY",
    "السعودية": "SAU", "Saudi Arabia": "SAU", "المملكة العربية السعودية": "SAU",
    "الإمارات": "ARE", "UAE": "ARE", "الامارات": "ARE",
    "الكويت": "KWT", "Kuwait": "KWT",
    "قطر": "QAT", "Qatar": "QAT",
    "البحرين": "BHR", "Bahrain": "BHR",
    "عمان": "OMN", "Oman": "OMN",
    "العراق": "IRQ", "Iraq": "IRQ",
    "الأردن": "JOR", "Jordan": "JOR",
    "لبنان": "LBN", "Lebanon": "LBN",
    "سوريا": "SYR", "Syria": "SYR",
    "فلسطين": "PSE", "Palestine": "PSE",
    "اليمن": "YEM", "Yemen": "YEM",
    "ليبيا": "LBY", "Libya": "LBY",
    "السودان": "SDN", "Sudan": "SDN",
    "موريتانيا": "MRT", "Mauritania": "MRT",
    
    # الدول الكبرى
    "أمريكا": "USA", "الولايات المتحدة": "USA", "USA": "USA", "United States": "USA",
    "الصين": "CHN", "China": "CHN",
    "ألمانيا": "DEU", "Germany": "DEU",
    "فرنسا": "FRA", "France": "FRA",
    "بريطانيا": "GBR", "UK": "GBR", "United Kingdom": "GBR",
    "اليابان": "JPN", "Japan": "JPN",
    "الهند": "IND", "India": "IND",
    "روسيا": "RUS", "Russia": "RUS",
    "البرازيل": "BRA", "Brazil": "BRA",
    "كندا": "CAN", "Canada": "CAN",
    "أستراليا": "AUS", "Australia": "AUS",
    "إيطاليا": "ITA", "Italy": "ITA",
    "إسبانيا": "ESP", "Spain": "ESP",
    "كوريا الجنوبية": "KOR", "South Korea": "KOR",
    "تركيا": "TUR", "Turkey": "TUR",
    "المكسيك": "MEX", "Mexico": "MEX",
    "إندونيسيا": "IDN", "Indonesia": "IDN",
    "جنوب أفريقيا": "ZAF", "South Africa": "ZAF",
    "نيجيريا": "NGA", "Nigeria": "NGA",
    # دول إضافية
    "تنزانيا": "TZA", "Tanzania": "TZA",
    "كينيا": "KEN", "Kenya": "KEN",
    "إثيوبيا": "ETH", "Ethiopia": "ETH",
    "غانا": "GHA", "Ghana": "GHA",
    "المغرب": "MAR", "Morocco": "MAR",
    "باكستان": "PAK", "Pakistan": "PAK",
    "بنغلاديش": "BGD", "Bangladesh": "BGD",
    "فيتنام": "VNM", "Vietnam": "VNM",
    "تايلاند": "THA", "Thailand": "THA",
    "ماليزيا": "MYS", "Malaysia": "MYS",
    "سنغافورة": "SGP", "Singapore": "SGP",
    "الفلبين": "PHL", "Philippines": "PHL",
    "بولندا": "POL", "Poland": "POL",
    "هولندا": "NLD", "Netherlands": "NLD",
    "بلجيكا": "BEL", "Belgium": "BEL",
    "السويد": "SWE", "Sweden": "SWE",
    "النرويج": "NOR", "Norway": "NOR",
    "الدنمارك": "DNK", "Denmark": "DNK",
    "سويسرا": "CHE", "Switzerland": "CHE",
    "النمسا": "AUT", "Austria": "AUT",
    "اليونان": "GRC", "Greece": "GRC",
    "البرتغال": "PRT", "Portugal": "PRT",
    "التشيك": "CZE", "Czech": "CZE", "Czechia": "CZE",
    "رومانيا": "ROU", "Romania": "ROU",
    "أوكرانيا": "UKR", "Ukraine": "UKR",
    "تشيلي": "CHL", "Chile": "CHL",
    "كولومبيا": "COL", "Colombia": "COL",
    "بيرو": "PER", "Peru": "PER",
    "فنزويلا": "VEN", "Venezuela": "VEN",
    "نيوزيلندا": "NZL", "New Zealand": "NZL",
    "إيران": "IRN", "Iran": "IRN",
    "أفغانستان": "AFG", "Afghanistan": "AFG",
}

# ═══════════════════════════════════════════════════════════════════════════════
# 3. البحث المحلي الذكي (بدون API)
# ═══════════════════════════════════════════════════════════════════════════════

def smart_local_search(query):
    """
    بحث محلي ذكي يفهم الطلبات البسيطة بدون الحاجة لـ API
    مثال: "الصادرات في تنزانيا" أو "GDP Tanzania 2015-2020"
    """
    
    query_lower = query.lower()
    query_parts = query.replace(",", " ").replace("،", " ").replace("و", " ").split()
    
    found_countries = []
    found_indicators = []
    start_year = 2010
    end_year = 2023
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 1. البحث عن الدول
    # ═══════════════════════════════════════════════════════════════════════════
    
    # قاموس موسع للدول (عربي + إنجليزي + أكواد) - أكثر من 200 دولة
    country_aliases = {
        # ═══════════════════════════════════════════════════════════════════════
        # الدول العربية
        # ═══════════════════════════════════════════════════════════════════════
        "الجزائر": "DZA", "جزائر": "DZA", "algeria": "DZA", "dza": "DZA",
        "المغرب": "MAR", "مغرب": "MAR", "morocco": "MAR", "mar": "MAR",
        "تونس": "TUN", "tunisia": "TUN", "tun": "TUN",
        "مصر": "EGY", "egypt": "EGY", "egy": "EGY",
        "السعودية": "SAU", "سعودية": "SAU", "saudi": "SAU", "saudi arabia": "SAU", "sau": "SAU",
        "الإمارات": "ARE", "امارات": "ARE", "الامارات": "ARE", "uae": "ARE", "emirates": "ARE", "are": "ARE",
        "الكويت": "KWT", "كويت": "KWT", "kuwait": "KWT", "kwt": "KWT",
        "قطر": "QAT", "qatar": "QAT", "qat": "QAT",
        "البحرين": "BHR", "بحرين": "BHR", "bahrain": "BHR", "bhr": "BHR",
        "عمان": "OMN", "oman": "OMN", "omn": "OMN",
        "العراق": "IRQ", "عراق": "IRQ", "iraq": "IRQ", "irq": "IRQ",
        "الأردن": "JOR", "اردن": "JOR", "jordan": "JOR", "jor": "JOR",
        "لبنان": "LBN", "lebanon": "LBN", "lbn": "LBN",
        "سوريا": "SYR", "syria": "SYR", "syr": "SYR",
        "فلسطين": "PSE", "palestine": "PSE", "pse": "PSE",
        "اليمن": "YEM", "يمن": "YEM", "yemen": "YEM", "yem": "YEM",
        "ليبيا": "LBY", "libya": "LBY", "lby": "LBY",
        "السودان": "SDN", "سودان": "SDN", "sudan": "SDN", "sdn": "SDN",
        "موريتانيا": "MRT", "mauritania": "MRT", "mrt": "MRT",
        "الصومال": "SOM", "صومال": "SOM", "somalia": "SOM", "som": "SOM",
        "جيبوتي": "DJI", "djibouti": "DJI", "dji": "DJI",
        "جزر القمر": "COM", "comoros": "COM", "com": "COM",
        
        # ═══════════════════════════════════════════════════════════════════════
        # أفريقيا (جنوب الصحراء)
        # ═══════════════════════════════════════════════════════════════════════
        "جنوب افريقيا": "ZAF", "جنوب أفريقيا": "ZAF", "south africa": "ZAF", "zaf": "ZAF",
        "نيجيريا": "NGA", "nigeria": "NGA", "nga": "NGA",
        "تنزانيا": "TZA", "tanzania": "TZA", "tza": "TZA",
        "كينيا": "KEN", "kenya": "KEN", "ken": "KEN",
        "إثيوبيا": "ETH", "اثيوبيا": "ETH", "ethiopia": "ETH", "eth": "ETH",
        "غانا": "GHA", "ghana": "GHA", "gha": "GHA",
        "أوغندا": "UGA", "اوغندا": "UGA", "uganda": "UGA", "uga": "UGA",
        "موزمبيق": "MOZ", "mozambique": "MOZ", "moz": "MOZ",
        "أنغولا": "AGO", "انغولا": "AGO", "angola": "AGO", "ago": "AGO",
        "الكاميرون": "CMR", "cameroon": "CMR", "cmr": "CMR",
        "كوت ديفوار": "CIV", "ساحل العاج": "CIV", "ivory coast": "CIV", "cote d'ivoire": "CIV", "civ": "CIV",
        "السنغال": "SEN", "senegal": "SEN", "sen": "SEN",
        "زيمبابوي": "ZWE", "zimbabwe": "ZWE", "zwe": "ZWE",
        "زامبيا": "ZMB", "zambia": "ZMB", "zmb": "ZMB",
        "رواندا": "RWA", "rwanda": "RWA", "rwa": "RWA",
        "الكونغو": "COD", "كونغو": "COD", "congo": "COD", "drc": "COD", "cod": "COD",
        "مدغشقر": "MDG", "madagascar": "MDG", "mdg": "MDG",
        "مالي": "MLI", "mali": "MLI", "mli": "MLI",
        "بوركينا فاسو": "BFA", "burkina faso": "BFA", "bfa": "BFA",
        "النيجر": "NER", "niger": "NER", "ner": "NER",
        "تشاد": "TCD", "chad": "TCD", "tcd": "TCD",
        "بنين": "BEN", "benin": "BEN", "ben": "BEN",
        "توغو": "TGO", "togo": "TGO", "tgo": "TGO",
        "موريشيوس": "MUS", "mauritius": "MUS", "mus": "MUS",
        "بوتسوانا": "BWA", "botswana": "BWA", "bwa": "BWA",
        "ناميبيا": "NAM", "namibia": "NAM", "nam": "NAM",
        
        # ═══════════════════════════════════════════════════════════════════════
        # آسيا
        # ═══════════════════════════════════════════════════════════════════════
        "الصين": "CHN", "صين": "CHN", "china": "CHN", "chn": "CHN",
        "الهند": "IND", "هند": "IND", "india": "IND", "ind": "IND",
        "اليابان": "JPN", "يابان": "JPN", "japan": "JPN", "jpn": "JPN",
        "كوريا": "KOR", "كوريا الجنوبية": "KOR", "south korea": "KOR", "korea": "KOR", "kor": "KOR",
        "كوريا الشمالية": "PRK", "north korea": "PRK", "prk": "PRK",
        "إندونيسيا": "IDN", "اندونيسيا": "IDN", "indonesia": "IDN", "idn": "IDN",
        "باكستان": "PAK", "pakistan": "PAK", "pak": "PAK",
        "بنغلاديش": "BGD", "bangladesh": "BGD", "bgd": "BGD",
        "فيتنام": "VNM", "vietnam": "VNM", "vnm": "VNM",
        "تايلاند": "THA", "thailand": "THA", "tha": "THA",
        "ماليزيا": "MYS", "malaysia": "MYS", "mys": "MYS",
        "سنغافورة": "SGP", "singapore": "SGP", "sgp": "SGP",
        "الفلبين": "PHL", "فلبين": "PHL", "philippines": "PHL", "phl": "PHL",
        "ميانمار": "MMR", "بورما": "MMR", "myanmar": "MMR", "burma": "MMR", "mmr": "MMR",
        "سريلانكا": "LKA", "sri lanka": "LKA", "lka": "LKA",
        "نيبال": "NPL", "nepal": "NPL", "npl": "NPL",
        "كمبوديا": "KHM", "cambodia": "KHM", "khm": "KHM",
        "لاوس": "LAO", "laos": "LAO", "lao": "LAO",
        "منغوليا": "MNG", "mongolia": "MNG", "mng": "MNG",
        "تايوان": "TWN", "taiwan": "TWN", "twn": "TWN",
        "هونغ كونغ": "HKG", "hong kong": "HKG", "hkg": "HKG",
        "ماكاو": "MAC", "macau": "MAC", "mac": "MAC",
        "أفغانستان": "AFG", "افغانستان": "AFG", "afghanistan": "AFG", "afg": "AFG",
        "كازاخستان": "KAZ", "kazakhstan": "KAZ", "kaz": "KAZ",
        "أوزبكستان": "UZB", "uzbekistan": "UZB", "uzb": "UZB",
        "تركمانستان": "TKM", "turkmenistan": "TKM", "tkm": "TKM",
        "طاجيكستان": "TJK", "tajikistan": "TJK", "tjk": "TJK",
        "قيرغيزستان": "KGZ", "kyrgyzstan": "KGZ", "kgz": "KGZ",
        "أذربيجان": "AZE", "azerbaijan": "AZE", "aze": "AZE",
        "جورجيا": "GEO", "georgia": "GEO", "geo": "GEO",
        "أرمينيا": "ARM", "armenia": "ARM", "arm": "ARM",
        
        # ═══════════════════════════════════════════════════════════════════════
        # الشرق الأوسط
        # ═══════════════════════════════════════════════════════════════════════
        "إيران": "IRN", "ايران": "IRN", "iran": "IRN", "irn": "IRN",
        "تركيا": "TUR", "turkey": "TUR", "turkiye": "TUR", "tur": "TUR",
        "إسرائيل": "ISR", "اسرائيل": "ISR", "israel": "ISR", "isr": "ISR",
        "قبرص": "CYP", "cyprus": "CYP", "cyp": "CYP",
        
        # ═══════════════════════════════════════════════════════════════════════
        # أوروبا
        # ═══════════════════════════════════════════════════════════════════════
        "ألمانيا": "DEU", "المانيا": "DEU", "germany": "DEU", "deu": "DEU",
        "فرنسا": "FRA", "france": "FRA", "fra": "FRA",
        "بريطانيا": "GBR", "المملكة المتحدة": "GBR", "uk": "GBR", "britain": "GBR", "united kingdom": "GBR", "gbr": "GBR",
        "إيطاليا": "ITA", "ايطاليا": "ITA", "italy": "ITA", "ita": "ITA",
        "إسبانيا": "ESP", "اسبانيا": "ESP", "spain": "ESP", "esp": "ESP",
        "هولندا": "NLD", "netherlands": "NLD", "holland": "NLD", "nld": "NLD",
        "بلجيكا": "BEL", "belgium": "BEL", "bel": "BEL",
        "السويد": "SWE", "sweden": "SWE", "swe": "SWE",
        "النرويج": "NOR", "norway": "NOR", "nor": "NOR",
        "الدنمارك": "DNK", "denmark": "DNK", "dnk": "DNK",
        "فنلندا": "FIN", "finland": "FIN", "fin": "FIN",
        "سويسرا": "CHE", "switzerland": "CHE", "che": "CHE",
        "النمسا": "AUT", "austria": "AUT", "aut": "AUT",
        "البرتغال": "PRT", "portugal": "PRT", "prt": "PRT",
        "اليونان": "GRC", "greece": "GRC", "grc": "GRC",
        "بولندا": "POL", "poland": "POL", "pol": "POL",
        "التشيك": "CZE", "czech": "CZE", "czechia": "CZE", "cze": "CZE",
        "رومانيا": "ROU", "romania": "ROU", "rou": "ROU",
        "المجر": "HUN", "hungary": "HUN", "hun": "HUN",
        "بلغاريا": "BGR", "bulgaria": "BGR", "bgr": "BGR",
        "أوكرانيا": "UKR", "اوكرانيا": "UKR", "ukraine": "UKR", "ukr": "UKR",
        "روسيا": "RUS", "russia": "RUS", "rus": "RUS",
        "بيلاروسيا": "BLR", "belarus": "BLR", "blr": "BLR",
        "أيرلندا": "IRL", "ايرلندا": "IRL", "ireland": "IRL", "irl": "IRL",
        "سلوفاكيا": "SVK", "slovakia": "SVK", "svk": "SVK",
        "سلوفينيا": "SVN", "slovenia": "SVN", "svn": "SVN",
        "كرواتيا": "HRV", "croatia": "HRV", "hrv": "HRV",
        "صربيا": "SRB", "serbia": "SRB", "srb": "SRB",
        "ألبانيا": "ALB", "albania": "ALB", "alb": "ALB",
        "مقدونيا": "MKD", "macedonia": "MKD", "mkd": "MKD",
        "البوسنة": "BIH", "bosnia": "BIH", "bih": "BIH",
        "الجبل الأسود": "MNE", "montenegro": "MNE", "mne": "MNE",
        "لاتفيا": "LVA", "latvia": "LVA", "lva": "LVA",
        "ليتوانيا": "LTU", "lithuania": "LTU", "ltu": "LTU",
        "إستونيا": "EST", "estonia": "EST", "est": "EST",
        "لوكسمبورغ": "LUX", "luxembourg": "LUX", "lux": "LUX",
        "مالطا": "MLT", "malta": "MLT", "mlt": "MLT",
        "أيسلندا": "ISL", "iceland": "ISL", "isl": "ISL",
        
        # ═══════════════════════════════════════════════════════════════════════
        # الأمريكتان
        # ═══════════════════════════════════════════════════════════════════════
        "أمريكا": "USA", "امريكا": "USA", "الولايات المتحدة": "USA", "usa": "USA", "america": "USA", "united states": "USA", "us": "USA",
        "كندا": "CAN", "canada": "CAN", "can": "CAN",
        "المكسيك": "MEX", "مكسيك": "MEX", "mexico": "MEX", "mex": "MEX",
        "البرازيل": "BRA", "برازيل": "BRA", "brazil": "BRA", "bra": "BRA",
        "الأرجنتين": "ARG", "ارجنتين": "ARG", "argentina": "ARG", "arg": "ARG",
        "كولومبيا": "COL", "colombia": "COL", "col": "COL",
        "تشيلي": "CHL", "chile": "CHL", "chl": "CHL",
        "بيرو": "PER", "peru": "PER", "per": "PER",
        "فنزويلا": "VEN", "venezuela": "VEN", "ven": "VEN",
        "الإكوادور": "ECU", "ecuador": "ECU", "ecu": "ECU",
        "بوليفيا": "BOL", "bolivia": "BOL", "bol": "BOL",
        "باراغواي": "PRY", "paraguay": "PRY", "pry": "PRY",
        "أوروغواي": "URY", "uruguay": "URY", "ury": "URY",
        "كوبا": "CUB", "cuba": "CUB", "cub": "CUB",
        "جامايكا": "JAM", "jamaica": "JAM", "jam": "JAM",
        "بنما": "PAN", "panama": "PAN", "pan": "PAN",
        "كوستاريكا": "CRI", "costa rica": "CRI", "cri": "CRI",
        "غواتيمالا": "GTM", "guatemala": "GTM", "gtm": "GTM",
        "هندوراس": "HND", "honduras": "HND", "hnd": "HND",
        "السلفادور": "SLV", "el salvador": "SLV", "slv": "SLV",
        "نيكاراغوا": "NIC", "nicaragua": "NIC", "nic": "NIC",
        "جمهورية الدومينيكان": "DOM", "dominican republic": "DOM", "dom": "DOM",
        "هايتي": "HTI", "haiti": "HTI", "hti": "HTI",
        "ترينيداد": "TTO", "trinidad": "TTO", "tto": "TTO",
        
        # ═══════════════════════════════════════════════════════════════════════
        # أوقيانوسيا
        # ═══════════════════════════════════════════════════════════════════════
        "أستراليا": "AUS", "استراليا": "AUS", "australia": "AUS", "aus": "AUS",
        "نيوزيلندا": "NZL", "new zealand": "NZL", "nzl": "NZL",
        "بابوا غينيا": "PNG", "papua new guinea": "PNG", "png": "PNG",
        "فيجي": "FJI", "fiji": "FJI", "fji": "FJI",
    }
    
    # مجموعات الدول الموسعة
    country_groups = {
        # العربية
        "الدول العربية": ["DZA", "MAR", "TUN", "EGY", "SAU", "ARE", "KWT", "QAT", "BHR", "OMN", "IRQ", "JOR", "LBN", "SYR", "PSE", "YEM", "LBY", "SDN", "MRT"],
        "العربية": ["DZA", "MAR", "TUN", "EGY", "SAU", "ARE", "KWT", "QAT", "BHR", "OMN", "IRQ", "JOR", "LBN"],
        "arab": ["DZA", "MAR", "TUN", "EGY", "SAU", "ARE", "KWT", "QAT", "BHR", "OMN", "IRQ", "JOR", "LBN"],
        "arab countries": ["DZA", "MAR", "TUN", "EGY", "SAU", "ARE", "KWT", "QAT", "BHR", "OMN", "IRQ", "JOR", "LBN"],
        # الخليج
        "الخليج": ["SAU", "ARE", "KWT", "QAT", "BHR", "OMN"],
        "خليج": ["SAU", "ARE", "KWT", "QAT", "BHR", "OMN"],
        "دول الخليج": ["SAU", "ARE", "KWT", "QAT", "BHR", "OMN"],
        "gulf": ["SAU", "ARE", "KWT", "QAT", "BHR", "OMN"],
        "gcc": ["SAU", "ARE", "KWT", "QAT", "BHR", "OMN"],
        "gulf countries": ["SAU", "ARE", "KWT", "QAT", "BHR", "OMN"],
        # شمال أفريقيا
        "المغرب العربي": ["DZA", "MAR", "TUN", "LBY", "MRT"],
        "شمال افريقيا": ["DZA", "MAR", "TUN", "LBY", "EGY"],
        "شمال أفريقيا": ["DZA", "MAR", "TUN", "LBY", "EGY"],
        "north africa": ["DZA", "MAR", "TUN", "LBY", "EGY"],
        "maghreb": ["DZA", "MAR", "TUN", "LBY", "MRT"],
        # أفريقيا
        "أفريقيا": ["DZA", "EGY", "NGA", "ZAF", "KEN", "ETH", "TZA", "GHA", "MAR"],
        "افريقيا": ["DZA", "EGY", "NGA", "ZAF", "KEN", "ETH", "TZA", "GHA", "MAR"],
        "africa": ["DZA", "EGY", "NGA", "ZAF", "KEN", "ETH", "TZA", "GHA", "MAR"],
        "african countries": ["DZA", "EGY", "NGA", "ZAF", "KEN", "ETH", "TZA", "GHA", "MAR"],
        "sub-saharan africa": ["NGA", "ZAF", "KEN", "ETH", "TZA", "GHA", "UGA", "SEN", "CIV"],
        # مجموعات اقتصادية
        "g7": ["USA", "GBR", "FRA", "DEU", "ITA", "CAN", "JPN"],
        "g20": ["USA", "CHN", "JPN", "DEU", "GBR", "FRA", "ITA", "BRA", "IND", "RUS", "AUS", "KOR", "MEX", "IDN", "SAU", "TUR", "ARG", "ZAF"],
        "brics": ["BRA", "RUS", "IND", "CHN", "ZAF"],
        "brics+": ["BRA", "RUS", "IND", "CHN", "ZAF", "EGY", "ETH", "IRN", "SAU", "ARE"],
        # آسيا
        "آسيا": ["CHN", "JPN", "KOR", "IND", "IDN", "THA", "MYS", "SGP", "VNM", "PHL"],
        "اسيا": ["CHN", "JPN", "KOR", "IND", "IDN", "THA", "MYS", "SGP", "VNM", "PHL"],
        "asia": ["CHN", "JPN", "KOR", "IND", "IDN", "THA", "MYS", "SGP", "VNM", "PHL"],
        "asian countries": ["CHN", "JPN", "KOR", "IND", "IDN", "THA", "MYS", "SGP", "VNM", "PHL"],
        "southeast asia": ["IDN", "THA", "MYS", "SGP", "VNM", "PHL", "MMR", "KHM", "LAO"],
        "asean": ["IDN", "THA", "MYS", "SGP", "VNM", "PHL", "MMR", "KHM", "LAO", "BRN"],
        # أوروبا
        "أوروبا": ["DEU", "FRA", "GBR", "ITA", "ESP", "NLD", "BEL", "POL", "SWE", "AUT"],
        "اوروبا": ["DEU", "FRA", "GBR", "ITA", "ESP", "NLD", "BEL", "POL", "SWE", "AUT"],
        "europe": ["DEU", "FRA", "GBR", "ITA", "ESP", "NLD", "BEL", "POL", "SWE", "AUT"],
        "european union": ["DEU", "FRA", "ITA", "ESP", "NLD", "BEL", "POL", "SWE", "AUT", "GRC", "PRT", "IRL"],
        "eu": ["DEU", "FRA", "ITA", "ESP", "NLD", "BEL", "POL", "SWE", "AUT", "GRC", "PRT", "IRL"],
        # أمريكا اللاتينية
        "أمريكا اللاتينية": ["BRA", "MEX", "ARG", "COL", "CHL", "PER", "VEN", "ECU"],
        "امريكا اللاتينية": ["BRA", "MEX", "ARG", "COL", "CHL", "PER", "VEN", "ECU"],
        "latin america": ["BRA", "MEX", "ARG", "COL", "CHL", "PER", "VEN", "ECU"],
        "south america": ["BRA", "ARG", "COL", "CHL", "PER", "VEN", "ECU", "BOL", "PRY", "URY"],
        # الدول الكبرى
        "الدول الكبرى": ["USA", "CHN", "DEU", "JPN", "GBR", "FRA", "IND"],
        "major economies": ["USA", "CHN", "DEU", "JPN", "GBR", "FRA", "IND"],
        "largest economies": ["USA", "CHN", "DEU", "JPN", "GBR", "FRA", "IND", "BRA", "ITA", "CAN"],
        # النمور الآسيوية
        "النمور الآسيوية": ["KOR", "SGP", "HKG", "TWN"],
        "asian tigers": ["KOR", "SGP", "HKG", "TWN"],
        # الأسواق الناشئة
        "الأسواق الناشئة": ["CHN", "IND", "BRA", "RUS", "MEX", "IDN", "TUR", "ZAF"],
        "emerging markets": ["CHN", "IND", "BRA", "RUS", "MEX", "IDN", "TUR", "ZAF"],
    }
    
    # البحث عن مجموعات أولاً
    for group_name, group_codes in country_groups.items():
        if group_name in query_lower:
            found_countries.extend(group_codes)
    
    # البحث عن الدول الفردية
    for alias, code in country_aliases.items():
        if alias in query_lower and code not in found_countries:
            found_countries.append(code)
    
    # البحث في أجزاء الطلب
    for part in query_parts:
        part_lower = part.lower().strip()
        if part_lower in country_aliases and country_aliases[part_lower] not in found_countries:
            found_countries.append(country_aliases[part_lower])
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 2. البحث عن المؤشرات - قاموس موسع
    # ═══════════════════════════════════════════════════════════════════════════
    
    indicator_aliases = {
        # ═══════════════════════════════════════════════════════════════════════
        # الناتج المحلي الإجمالي GDP
        # ═══════════════════════════════════════════════════════════════════════
        "الناتج المحلي": {"code": "NY.GDP.MKTP.CD", "name": "الناتج المحلي الإجمالي (USD)"},
        "الناتج المحلي الإجمالي": {"code": "NY.GDP.MKTP.CD", "name": "الناتج المحلي الإجمالي (USD)"},
        "الناتج": {"code": "NY.GDP.MKTP.CD", "name": "الناتج المحلي الإجمالي"},
        "ناتج محلي": {"code": "NY.GDP.MKTP.CD", "name": "الناتج المحلي الإجمالي"},
        "ناتج": {"code": "NY.GDP.MKTP.CD", "name": "الناتج المحلي الإجمالي"},
        "gdp": {"code": "NY.GDP.MKTP.CD", "name": "GDP (current US$)"},
        "gross domestic product": {"code": "NY.GDP.MKTP.CD", "name": "GDP"},
        # نمو الناتج المحلي
        "نمو الناتج المحلي": {"code": "NY.GDP.MKTP.KD.ZG", "name": "نمو الناتج المحلي (%)"},
        "نمو الناتج": {"code": "NY.GDP.MKTP.KD.ZG", "name": "نمو الناتج المحلي (%)"},
        "النمو الاقتصادي": {"code": "NY.GDP.MKTP.KD.ZG", "name": "النمو الاقتصادي (%)"},
        "معدل النمو": {"code": "NY.GDP.MKTP.KD.ZG", "name": "معدل النمو (%)"},
        "النمو": {"code": "NY.GDP.MKTP.KD.ZG", "name": "نمو الناتج المحلي"},
        "نمو": {"code": "NY.GDP.MKTP.KD.ZG", "name": "نمو الناتج المحلي"},
        "gdp growth": {"code": "NY.GDP.MKTP.KD.ZG", "name": "GDP Growth (%)"},
        "growth": {"code": "NY.GDP.MKTP.KD.ZG", "name": "GDP Growth"},
        "economic growth": {"code": "NY.GDP.MKTP.KD.ZG", "name": "Economic Growth"},
        # الناتج للفرد
        "الناتج المحلي للفرد": {"code": "NY.GDP.PCAP.CD", "name": "الناتج المحلي للفرد (USD)"},
        "الناتج للفرد": {"code": "NY.GDP.PCAP.CD", "name": "الناتج المحلي للفرد"},
        "دخل الفرد": {"code": "NY.GDP.PCAP.CD", "name": "دخل الفرد"},
        "للفرد": {"code": "NY.GDP.PCAP.CD", "name": "الناتج المحلي للفرد"},
        "gdp per capita": {"code": "NY.GDP.PCAP.CD", "name": "GDP per Capita"},
        "per capita": {"code": "NY.GDP.PCAP.CD", "name": "GDP per Capita"},
        "income per capita": {"code": "NY.GDP.PCAP.CD", "name": "Income per Capita"},
        
        # ═══════════════════════════════════════════════════════════════════════
        # التجارة الخارجية Trade
        # ═══════════════════════════════════════════════════════════════════════
        "الصادرات": {"code": "NE.EXP.GNFS.CD", "name": "الصادرات (USD)"},
        "صادرات": {"code": "NE.EXP.GNFS.CD", "name": "الصادرات"},
        "التصدير": {"code": "NE.EXP.GNFS.CD", "name": "الصادرات"},
        "exports": {"code": "NE.EXP.GNFS.CD", "name": "Exports (current US$)"},
        "export": {"code": "NE.EXP.GNFS.CD", "name": "Exports"},
        "الواردات": {"code": "NE.IMP.GNFS.CD", "name": "الواردات (USD)"},
        "واردات": {"code": "NE.IMP.GNFS.CD", "name": "الواردات"},
        "الاستيراد": {"code": "NE.IMP.GNFS.CD", "name": "الواردات"},
        "imports": {"code": "NE.IMP.GNFS.CD", "name": "Imports (current US$)"},
        "import": {"code": "NE.IMP.GNFS.CD", "name": "Imports"},
        "الميزان التجاري": {"code": "NE.RSB.GNFS.CD", "name": "الميزان التجاري"},
        "ميزان تجاري": {"code": "NE.RSB.GNFS.CD", "name": "الميزان التجاري"},
        "trade balance": {"code": "NE.RSB.GNFS.CD", "name": "Trade Balance"},
        "التجارة": {"code": "NE.TRD.GNFS.ZS", "name": "التجارة (% من الناتج)"},
        "حجم التجارة": {"code": "NE.TRD.GNFS.ZS", "name": "حجم التجارة"},
        "trade": {"code": "NE.TRD.GNFS.ZS", "name": "Trade (% of GDP)"},
        # نسب التجارة
        "نسبة الصادرات": {"code": "NE.EXP.GNFS.ZS", "name": "الصادرات (% من الناتج)"},
        "exports percent": {"code": "NE.EXP.GNFS.ZS", "name": "Exports (% of GDP)"},
        "نسبة الواردات": {"code": "NE.IMP.GNFS.ZS", "name": "الواردات (% من الناتج)"},
        "imports percent": {"code": "NE.IMP.GNFS.ZS", "name": "Imports (% of GDP)"},
        
        # ═══════════════════════════════════════════════════════════════════════
        # التضخم والأسعار Inflation
        # ═══════════════════════════════════════════════════════════════════════
        "التضخم": {"code": "FP.CPI.TOTL.ZG", "name": "معدل التضخم (%)"},
        "تضخم": {"code": "FP.CPI.TOTL.ZG", "name": "معدل التضخم"},
        "معدل التضخم": {"code": "FP.CPI.TOTL.ZG", "name": "معدل التضخم (%)"},
        "نسبة التضخم": {"code": "FP.CPI.TOTL.ZG", "name": "نسبة التضخم"},
        "inflation": {"code": "FP.CPI.TOTL.ZG", "name": "Inflation Rate (%)"},
        "inflation rate": {"code": "FP.CPI.TOTL.ZG", "name": "Inflation Rate"},
        "cpi": {"code": "FP.CPI.TOTL.ZG", "name": "Consumer Price Index"},
        "الأسعار": {"code": "FP.CPI.TOTL.ZG", "name": "معدل التضخم"},
        "اسعار": {"code": "FP.CPI.TOTL.ZG", "name": "معدل التضخم"},
        "مؤشر الأسعار": {"code": "FP.CPI.TOTL", "name": "مؤشر أسعار المستهلك"},
        "consumer prices": {"code": "FP.CPI.TOTL", "name": "Consumer Price Index"},
        
        # ═══════════════════════════════════════════════════════════════════════
        # البطالة وسوق العمل Unemployment
        # ═══════════════════════════════════════════════════════════════════════
        "البطالة": {"code": "SL.UEM.TOTL.ZS", "name": "معدل البطالة (%)"},
        "بطالة": {"code": "SL.UEM.TOTL.ZS", "name": "معدل البطالة"},
        "معدل البطالة": {"code": "SL.UEM.TOTL.ZS", "name": "معدل البطالة (%)"},
        "نسبة البطالة": {"code": "SL.UEM.TOTL.ZS", "name": "نسبة البطالة"},
        "unemployment": {"code": "SL.UEM.TOTL.ZS", "name": "Unemployment Rate (%)"},
        "unemployment rate": {"code": "SL.UEM.TOTL.ZS", "name": "Unemployment Rate"},
        "jobless": {"code": "SL.UEM.TOTL.ZS", "name": "Unemployment"},
        "بطالة الشباب": {"code": "SL.UEM.1524.ZS", "name": "بطالة الشباب (%)"},
        "youth unemployment": {"code": "SL.UEM.1524.ZS", "name": "Youth Unemployment (%)"},
        "القوى العاملة": {"code": "SL.TLF.TOTL.IN", "name": "إجمالي القوى العاملة"},
        "قوى عاملة": {"code": "SL.TLF.TOTL.IN", "name": "القوى العاملة"},
        "labor force": {"code": "SL.TLF.TOTL.IN", "name": "Labor Force"},
        "labour force": {"code": "SL.TLF.TOTL.IN", "name": "Labor Force"},
        "workforce": {"code": "SL.TLF.TOTL.IN", "name": "Workforce"},
        
        # ═══════════════════════════════════════════════════════════════════════
        # السكان Population
        # ═══════════════════════════════════════════════════════════════════════
        "السكان": {"code": "SP.POP.TOTL", "name": "إجمالي السكان"},
        "سكان": {"code": "SP.POP.TOTL", "name": "إجمالي السكان"},
        "عدد السكان": {"code": "SP.POP.TOTL", "name": "عدد السكان"},
        "تعداد السكان": {"code": "SP.POP.TOTL", "name": "تعداد السكان"},
        "population": {"code": "SP.POP.TOTL", "name": "Total Population"},
        "نمو السكان": {"code": "SP.POP.GROW", "name": "نمو السكان (%)"},
        "معدل نمو السكان": {"code": "SP.POP.GROW", "name": "معدل نمو السكان"},
        "population growth": {"code": "SP.POP.GROW", "name": "Population Growth (%)"},
        "الكثافة السكانية": {"code": "EN.POP.DNST", "name": "الكثافة السكانية"},
        "كثافة سكانية": {"code": "EN.POP.DNST", "name": "الكثافة السكانية"},
        "population density": {"code": "EN.POP.DNST", "name": "Population Density"},
        "العمر المتوقع": {"code": "SP.DYN.LE00.IN", "name": "متوسط العمر المتوقع"},
        "متوسط العمر": {"code": "SP.DYN.LE00.IN", "name": "متوسط العمر المتوقع"},
        "life expectancy": {"code": "SP.DYN.LE00.IN", "name": "Life Expectancy"},
        
        # ═══════════════════════════════════════════════════════════════════════
        # الاستثمار Investment
        # ═══════════════════════════════════════════════════════════════════════
        "الاستثمار الأجنبي": {"code": "BX.KLT.DINV.CD.WD", "name": "الاستثمار الأجنبي المباشر (USD)"},
        "الاستثمار الاجنبي": {"code": "BX.KLT.DINV.CD.WD", "name": "الاستثمار الأجنبي المباشر"},
        "استثمار أجنبي": {"code": "BX.KLT.DINV.CD.WD", "name": "الاستثمار الأجنبي"},
        "الاستثمار": {"code": "BX.KLT.DINV.CD.WD", "name": "الاستثمار الأجنبي"},
        "استثمار": {"code": "BX.KLT.DINV.CD.WD", "name": "الاستثمار الأجنبي"},
        "fdi": {"code": "BX.KLT.DINV.CD.WD", "name": "FDI Inflows (USD)"},
        "foreign direct investment": {"code": "BX.KLT.DINV.CD.WD", "name": "FDI"},
        "foreign investment": {"code": "BX.KLT.DINV.CD.WD", "name": "Foreign Investment"},
        "investment": {"code": "BX.KLT.DINV.CD.WD", "name": "Investment"},
        "تكوين رأس المال": {"code": "NE.GDI.TOTL.ZS", "name": "تكوين رأس المال (% من الناتج)"},
        "gross capital formation": {"code": "NE.GDI.TOTL.ZS", "name": "Gross Capital Formation"},
        
        # ═══════════════════════════════════════════════════════════════════════
        # المالية العامة Government Finance
        # ═══════════════════════════════════════════════════════════════════════
        "الدين الحكومي": {"code": "GC.DOD.TOTL.GD.ZS", "name": "الدين الحكومي (% من الناتج)"},
        "الدين العام": {"code": "GC.DOD.TOTL.GD.ZS", "name": "الدين العام (% من الناتج)"},
        "الدين": {"code": "GC.DOD.TOTL.GD.ZS", "name": "الدين الحكومي"},
        "دين": {"code": "GC.DOD.TOTL.GD.ZS", "name": "الدين الحكومي"},
        "debt": {"code": "GC.DOD.TOTL.GD.ZS", "name": "Government Debt (% of GDP)"},
        "government debt": {"code": "GC.DOD.TOTL.GD.ZS", "name": "Government Debt"},
        "public debt": {"code": "GC.DOD.TOTL.GD.ZS", "name": "Public Debt"},
        "الإيرادات الحكومية": {"code": "GC.REV.XGRT.GD.ZS", "name": "الإيرادات (% من الناتج)"},
        "إيرادات الحكومة": {"code": "GC.REV.XGRT.GD.ZS", "name": "الإيرادات الحكومية"},
        "government revenue": {"code": "GC.REV.XGRT.GD.ZS", "name": "Government Revenue"},
        "النفقات الحكومية": {"code": "GC.XPN.TOTL.GD.ZS", "name": "النفقات (% من الناتج)"},
        "إنفاق الحكومة": {"code": "GC.XPN.TOTL.GD.ZS", "name": "النفقات الحكومية"},
        "government expenditure": {"code": "GC.XPN.TOTL.GD.ZS", "name": "Government Expenditure"},
        "government spending": {"code": "GC.XPN.TOTL.GD.ZS", "name": "Government Spending"},
        
        # ═══════════════════════════════════════════════════════════════════════
        # التعليم Education
        # ═══════════════════════════════════════════════════════════════════════
        "الإنفاق على التعليم": {"code": "SE.XPD.TOTL.GD.ZS", "name": "الإنفاق على التعليم (% من الناتج)"},
        "الانفاق على التعليم": {"code": "SE.XPD.TOTL.GD.ZS", "name": "الإنفاق على التعليم"},
        "ميزانية التعليم": {"code": "SE.XPD.TOTL.GD.ZS", "name": "ميزانية التعليم"},
        "التعليم": {"code": "SE.XPD.TOTL.GD.ZS", "name": "الإنفاق على التعليم"},
        "تعليم": {"code": "SE.XPD.TOTL.GD.ZS", "name": "الإنفاق على التعليم"},
        "education": {"code": "SE.XPD.TOTL.GD.ZS", "name": "Education Expenditure (% of GDP)"},
        "education spending": {"code": "SE.XPD.TOTL.GD.ZS", "name": "Education Spending"},
        "الالتحاق بالتعليم": {"code": "SE.PRM.ENRR", "name": "معدل الالتحاق بالتعليم الابتدائي"},
        "school enrollment": {"code": "SE.PRM.ENRR", "name": "School Enrollment Rate"},
        
        # ═══════════════════════════════════════════════════════════════════════
        # الصحة Health
        # ═══════════════════════════════════════════════════════════════════════
        "الإنفاق على الصحة": {"code": "SH.XPD.CHEX.GD.ZS", "name": "الإنفاق على الصحة (% من الناتج)"},
        "الانفاق على الصحة": {"code": "SH.XPD.CHEX.GD.ZS", "name": "الإنفاق على الصحة"},
        "ميزانية الصحة": {"code": "SH.XPD.CHEX.GD.ZS", "name": "ميزانية الصحة"},
        "الصحة": {"code": "SH.XPD.CHEX.GD.ZS", "name": "الإنفاق على الصحة"},
        "صحة": {"code": "SH.XPD.CHEX.GD.ZS", "name": "الإنفاق على الصحة"},
        "health": {"code": "SH.XPD.CHEX.GD.ZS", "name": "Health Expenditure (% of GDP)"},
        "health spending": {"code": "SH.XPD.CHEX.GD.ZS", "name": "Health Spending"},
        "healthcare": {"code": "SH.XPD.CHEX.GD.ZS", "name": "Healthcare"},
        "وفيات الرضع": {"code": "SP.DYN.IMRT.IN", "name": "معدل وفيات الرضع"},
        "infant mortality": {"code": "SP.DYN.IMRT.IN", "name": "Infant Mortality Rate"},
        
        # ═══════════════════════════════════════════════════════════════════════
        # الطاقة Energy
        # ═══════════════════════════════════════════════════════════════════════
        "استهلاك الطاقة": {"code": "EG.USE.PCAP.KG.OE", "name": "استهلاك الطاقة للفرد"},
        "الطاقة": {"code": "EG.USE.PCAP.KG.OE", "name": "استهلاك الطاقة للفرد"},
        "طاقة": {"code": "EG.USE.PCAP.KG.OE", "name": "استهلاك الطاقة"},
        "energy": {"code": "EG.USE.PCAP.KG.OE", "name": "Energy Use per Capita"},
        "energy consumption": {"code": "EG.USE.PCAP.KG.OE", "name": "Energy Consumption"},
        "الطاقة المتجددة": {"code": "EG.FEC.RNEW.ZS", "name": "الطاقة المتجددة (%)"},
        "renewable energy": {"code": "EG.FEC.RNEW.ZS", "name": "Renewable Energy (%)"},
        "الكهرباء": {"code": "EG.ELC.ACCS.ZS", "name": "الوصول للكهرباء (%)"},
        "electricity": {"code": "EG.ELC.ACCS.ZS", "name": "Access to Electricity (%)"},
        
        # ═══════════════════════════════════════════════════════════════════════
        # البيئة Environment
        # ═══════════════════════════════════════════════════════════════════════
        "انبعاثات CO2": {"code": "EN.ATM.CO2E.PC", "name": "انبعاثات CO2 للفرد (طن)"},
        "الانبعاثات": {"code": "EN.ATM.CO2E.PC", "name": "انبعاثات CO2"},
        "co2": {"code": "EN.ATM.CO2E.PC", "name": "CO2 Emissions per Capita"},
        "carbon emissions": {"code": "EN.ATM.CO2E.PC", "name": "Carbon Emissions"},
        "emissions": {"code": "EN.ATM.CO2E.PC", "name": "CO2 Emissions"},
        "الغابات": {"code": "AG.LND.FRST.ZS", "name": "مساحة الغابات (%)"},
        "forest": {"code": "AG.LND.FRST.ZS", "name": "Forest Area (%)"},
        
        # ═══════════════════════════════════════════════════════════════════════
        # القطاع المالي والبنكي Financial
        # ═══════════════════════════════════════════════════════════════════════
        "سعر الصرف": {"code": "PA.NUS.FCRF", "name": "سعر الصرف الرسمي"},
        "الصرف": {"code": "PA.NUS.FCRF", "name": "سعر الصرف"},
        "exchange rate": {"code": "PA.NUS.FCRF", "name": "Official Exchange Rate"},
        "currency": {"code": "PA.NUS.FCRF", "name": "Exchange Rate"},
        "سعر الفائدة": {"code": "FR.INR.RINR", "name": "سعر الفائدة الحقيقي (%)"},
        "الفائدة": {"code": "FR.INR.RINR", "name": "سعر الفائدة"},
        "interest rate": {"code": "FR.INR.RINR", "name": "Real Interest Rate (%)"},
        "الائتمان المحلي": {"code": "FS.AST.DOMS.GD.ZS", "name": "الائتمان المحلي (% من الناتج)"},
        "domestic credit": {"code": "FS.AST.DOMS.GD.ZS", "name": "Domestic Credit (% of GDP)"},
        "التحويلات المالية": {"code": "BX.TRF.PWKR.CD.DT", "name": "تحويلات العاملين (USD)"},
        "remittances": {"code": "BX.TRF.PWKR.CD.DT", "name": "Personal Remittances"},
        
        # ═══════════════════════════════════════════════════════════════════════
        # الزراعة Agriculture
        # ═══════════════════════════════════════════════════════════════════════
        "الزراعة": {"code": "NV.AGR.TOTL.ZS", "name": "الزراعة (% من الناتج)"},
        "زراعة": {"code": "NV.AGR.TOTL.ZS", "name": "الزراعة"},
        "agriculture": {"code": "NV.AGR.TOTL.ZS", "name": "Agriculture (% of GDP)"},
        "farming": {"code": "NV.AGR.TOTL.ZS", "name": "Agriculture"},
        "الأراضي الزراعية": {"code": "AG.LND.ARBL.ZS", "name": "الأراضي الزراعية (%)"},
        "agricultural land": {"code": "AG.LND.ARBL.ZS", "name": "Agricultural Land (%)"},
        
        # ═══════════════════════════════════════════════════════════════════════
        # الصناعة Industry
        # ═══════════════════════════════════════════════════════════════════════
        "الصناعة": {"code": "NV.IND.TOTL.ZS", "name": "الصناعة (% من الناتج)"},
        "صناعة": {"code": "NV.IND.TOTL.ZS", "name": "الصناعة"},
        "industry": {"code": "NV.IND.TOTL.ZS", "name": "Industry (% of GDP)"},
        "manufacturing": {"code": "NV.IND.MANF.ZS", "name": "Manufacturing (% of GDP)"},
        "التصنيع": {"code": "NV.IND.MANF.ZS", "name": "التصنيع (% من الناتج)"},
        
        # ═══════════════════════════════════════════════════════════════════════
        # الخدمات Services
        # ═══════════════════════════════════════════════════════════════════════
        "الخدمات": {"code": "NV.SRV.TOTL.ZS", "name": "الخدمات (% من الناتج)"},
        "خدمات": {"code": "NV.SRV.TOTL.ZS", "name": "الخدمات"},
        "services": {"code": "NV.SRV.TOTL.ZS", "name": "Services (% of GDP)"},
        
        # ═══════════════════════════════════════════════════════════════════════
        # السياحة Tourism
        # ═══════════════════════════════════════════════════════════════════════
        "السياحة": {"code": "ST.INT.RCPT.CD", "name": "إيرادات السياحة (USD)"},
        "سياحة": {"code": "ST.INT.RCPT.CD", "name": "إيرادات السياحة"},
        "tourism": {"code": "ST.INT.RCPT.CD", "name": "Tourism Receipts"},
        "السياح": {"code": "ST.INT.ARVL", "name": "عدد السياح الوافدين"},
        "tourists": {"code": "ST.INT.ARVL", "name": "International Tourism Arrivals"},
        
        # ═══════════════════════════════════════════════════════════════════════
        # التكنولوجيا والإنترنت Technology
        # ═══════════════════════════════════════════════════════════════════════
        "الإنترنت": {"code": "IT.NET.USER.ZS", "name": "مستخدمو الإنترنت (%)"},
        "انترنت": {"code": "IT.NET.USER.ZS", "name": "مستخدمو الإنترنت"},
        "internet": {"code": "IT.NET.USER.ZS", "name": "Internet Users (%)"},
        "الهاتف المحمول": {"code": "IT.CEL.SETS.P2", "name": "اشتراكات الهاتف المحمول"},
        "mobile": {"code": "IT.CEL.SETS.P2", "name": "Mobile Subscriptions"},
        "البحث والتطوير": {"code": "GB.XPD.RSDV.GD.ZS", "name": "الإنفاق على البحث والتطوير"},
        "r&d": {"code": "GB.XPD.RSDV.GD.ZS", "name": "R&D Expenditure (% of GDP)"},
        "research": {"code": "GB.XPD.RSDV.GD.ZS", "name": "Research & Development"},
        
        # ═══════════════════════════════════════════════════════════════════════
        # الفقر Poverty
        # ═══════════════════════════════════════════════════════════════════════
        "الفقر": {"code": "SI.POV.DDAY", "name": "نسبة الفقر (%)"},
        "فقر": {"code": "SI.POV.DDAY", "name": "نسبة الفقر"},
        "poverty": {"code": "SI.POV.DDAY", "name": "Poverty Rate (%)"},
        "poverty rate": {"code": "SI.POV.DDAY", "name": "Poverty Headcount Ratio"},
        "معامل جيني": {"code": "SI.POV.GINI", "name": "معامل جيني"},
        "gini": {"code": "SI.POV.GINI", "name": "Gini Index"},
        "inequality": {"code": "SI.POV.GINI", "name": "Inequality"},
        
        # ═══════════════════════════════════════════════════════════════════════
        # التنمية البشرية Human Development
        # ═══════════════════════════════════════════════════════════════════════
        "معدل الخصوبة": {"code": "SP.DYN.TFRT.IN", "name": "معدل الخصوبة"},
        "fertility": {"code": "SP.DYN.TFRT.IN", "name": "Fertility Rate"},
        "معدل الوفاة": {"code": "SP.DYN.CDRT.IN", "name": "معدل الوفاة"},
        "mortality": {"code": "SP.DYN.CDRT.IN", "name": "Mortality Rate"},
        "معدل المواليد": {"code": "SP.DYN.CBRT.IN", "name": "معدل المواليد"},
        "birth rate": {"code": "SP.DYN.CBRT.IN", "name": "Birth Rate"},
    }
    
    # البحث عن المؤشرات في النص
    for alias, indicator_data in indicator_aliases.items():
        if alias in query_lower:
            # تجنب التكرار
            if not any(ind['code'] == indicator_data['code'] for ind in found_indicators):
                found_indicators.append(indicator_data)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 3. استخراج السنوات
    # ═══════════════════════════════════════════════════════════════════════════
    
    # البحث عن نمط السنوات (2010-2023 أو من 2010 إلى 2023)
    year_patterns = [
        r'(\d{4})\s*[-–]\s*(\d{4})',  # 2010-2023
        r'من\s*(\d{4})\s*(?:إلى|الى|ل)\s*(\d{4})',  # من 2010 إلى 2023
        r'from\s*(\d{4})\s*to\s*(\d{4})',  # from 2010 to 2023
        r'(\d{4})\s*(?:إلى|الى|to)\s*(\d{4})',  # 2010 إلى 2023
    ]
    
    for pattern in year_patterns:
        match = re.search(pattern, query)
        if match:
            start_year = int(match.group(1))
            end_year = int(match.group(2))
            break
    
    # البحث عن سنة واحدة
    if start_year == 2010 and end_year == 2023:
        single_year = re.search(r'\b(19\d{2}|20\d{2})\b', query)
        if single_year:
            year = int(single_year.group(1))
            start_year = year - 5
            end_year = year + 5
            if end_year > 2023:
                end_year = 2023
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 4. القيم الافتراضية إذا لم يتم العثور على شيء
    # ═══════════════════════════════════════════════════════════════════════════
    
    # إذا لم يتم العثور على مؤشرات، أضف الناتج المحلي كافتراضي
    if not found_indicators:
        found_indicators = [{"code": "NY.GDP.MKTP.CD", "name": "الناتج المحلي الإجمالي"}]
    
    # إذا لم يتم العثور على دول، ارجع None
    if not found_countries:
        return None
    
    # إزالة التكرارات مع الحفاظ على الترتيب
    found_countries = list(dict.fromkeys(found_countries))
    
    return {
        "countries": found_countries,
        "indicators": found_indicators,
        "start": start_year,
        "end": end_year
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 4. تهيئة Gemini Client - Gemini 3.0 Flash Preview
# ═══════════════════════════════════════════════════════════════════════════════

def configure_gemini(api_key):
    """Configure Gemini 3.0 Flash Preview API with new SDK"""
    if not GENAI_AVAILABLE:
        return None, False, "❌ مكتبة google-genai غير مثبتة. قم بتثبيتها:\npip install google-genai"
    
    try:
        # إنشاء العميل باستخدام SDK الجديد
        client = genai.Client(api_key=api_key)
        
        # اختبار الاتصال
        response = client.models.generate_content(
            model=GEMINI_MODEL_NAME,
            contents="مرحبا"
        )
        
        return client, True, "✅ تم الاتصال بنجاح!"
    except Exception as e:
        error_msg = str(e)
        if "API_KEY" in error_msg.upper() or "INVALID" in error_msg.upper():
            return None, False, "❌ مفتاح API غير صالح. احصل على مفتاح من:\nhttps://aistudio.google.com/apikey"
        return None, False, f"❌ خطأ في تكوين Gemini: {error_msg}"

# ═══════════════════════════════════════════════════════════════════════════════
# 4. محلل الطلبات الذكي باستخدام Gemini
# ═══════════════════════════════════════════════════════════════════════════════

def parse_query_with_ai(client, query):
    """تحليل طلب المستخدم باستخدام Gemini لاستخراج المؤشرات والدول"""
    
    # إنشاء قائمة المؤشرات المتاحة
    indicators_list = "\n".join([f"- {k}: {v['code']} ({v['name_en']})" for k, v in INDICATORS_DATABASE.items()])
    countries_list = "\n".join([f"- {k}: {v}" for k, v in COUNTRIES_DATABASE.items()])
    
    prompt = f"""
أنت خبير في تحليل البيانات الاقتصادية من البنك الدولي. مهمتك تحليل طلب المستخدم واستخراج المعلومات المطلوبة بدقة.

═══════════════════════════════════════
طلب المستخدم:
"{query}"
═══════════════════════════════════════

قاعدة بيانات المؤشرات المتاحة:
{indicators_list}

قاعدة بيانات الدول المتاحة:
{countries_list}

═══════════════════════════════════════
التعليمات:
1. استخرج الدول المذكورة وحولها إلى أكواد ISO-3 (مثل DZA للجزائر)
2. استخرج المؤشرات المطلوبة وحولها إلى الأكواد الصحيحة
3. حدد الفترة الزمنية (إذا لم تذكر، استخدم 2010-2023)
4. إذا ذكر "الدول العربية" أضف: DZA, MAR, TUN, EGY, SAU, ARE
5. إذا ذكر "دول الخليج" أضف: SAU, ARE, KWT, QAT, BHR, OMN

أهم أكواد المؤشرات (استخدمها بالضبط):
- الناتج المحلي GDP: NY.GDP.MKTP.CD
- الصادرات Exports: NE.EXP.GNFS.CD
- الواردات Imports: NE.IMP.GNFS.CD
- التضخم Inflation: FP.CPI.TOTL.ZG
- البطالة Unemployment: SL.UEM.TOTL.ZS
- السكان Population: SP.POP.TOTL
- نمو الناتج GDP Growth: NY.GDP.MKTP.KD.ZG
- الاستثمار الأجنبي FDI: BX.KLT.DINV.CD.WD

═══════════════════════════════════════

أرجع JSON فقط بهذا الشكل (بدون أي نص إضافي):
{{
    "countries": ["DZA", "MAR"],
    "indicators": [
        {{"code": "NY.GDP.MKTP.CD", "name": "الناتج المحلي الإجمالي"}},
        {{"code": "NE.EXP.GNFS.CD", "name": "الصادرات"}}
    ],
    "start": 2010,
    "end": 2023
}}
"""

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.1,
                max_output_tokens=2000
            )
        )
        
        if not response.text:
            return None
            
        # تنظيف الاستجابة
        clean_text = response.text.strip()
        clean_text = re.sub(r"```json\s*", "", clean_text)
        clean_text = re.sub(r"```\s*", "", clean_text)
        clean_text = clean_text.strip()
        
        # محاولة استخراج JSON
        json_match = re.search(r'\{[\s\S]*\}', clean_text)
        if json_match:
            clean_text = json_match.group()
        
        parsed = json.loads(clean_text)
        return parsed
        
    except json.JSONDecodeError as e:
        st.error(f"❌ خطأ في تحليل JSON: {e}")
        return None
    except Exception as e:
        st.error(f"❌ خطأ في تحليل الطلب: {e}")
        return None

# ═══════════════════════════════════════════════════════════════════════════════
# 5. جلب البيانات من البنك الدولي
# ═══════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_world_bank_data(countries, indicators, start_year, end_year):
    """جلب البيانات من API البنك الدولي"""
    
    all_data = []
    country_str = ";".join([c.strip() for c in countries])
    
    progress_container = st.container()
    
    with progress_container:
        progress_bar = st.progress(0)
        status_text = st.empty()
    
    for i, ind in enumerate(indicators):
        code = ind['code']
        name = ind['name']
        
        status_text.markdown(f"📥 **جاري جلب:** {name}...")
        progress_bar.progress((i + 1) / len(indicators))
        
        url = f"https://api.worldbank.org/v2/country/{country_str}/indicator/{code}"
        params = {
            "date": f"{start_year}:{end_year}",
            "format": "json",
            "per_page": 10000
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code != 200:
                continue
            
            data = response.json()
            
            if isinstance(data, list) and len(data) > 1 and data[1]:
                for item in data[1]:
                    if item.get('value') is not None:
                        iso_code = item.get('countryiso3code', '')
                        if not iso_code:
                            iso_code = item.get('country', {}).get('id', '')
                        
                        all_data.append({
                            "الدولة": item['country']['value'],
                            "CountryCode": iso_code,
                            "السنة": int(item['date']),
                            "المؤشر": name,
                            "القيمة": float(item['value'])
                        })
                        
        except Exception as e:
            print(f"Error fetching {name}: {e}")
            continue
    
    progress_bar.empty()
    status_text.empty()
    
    if not all_data:
        return pd.DataFrame()
    
    df_long = pd.DataFrame(all_data)
    
    # تحويل إلى صيغة واسعة
    try:
        df_wide = df_long.pivot_table(
            index=['الدولة', 'CountryCode', 'السنة'],
            columns='المؤشر',
            values='القيمة',
            aggfunc='first'
        ).reset_index()
        
        return df_wide
        
    except Exception:
        return df_long

# ═══════════════════════════════════════════════════════════════════════════════
# 6. إنشاء التقرير التحليلي بالذكاء الاصطناعي
# ═══════════════════════════════════════════════════════════════════════════════

def generate_ai_analysis(client, df, countries, indicators, query_type="full"):
    """توليد تحليل شامل باستخدام Gemini"""
    
    # إعداد ملخص البيانات
    stats_summary = df.describe().to_string()
    
    # حساب بعض الإحصائيات المهمة
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    numeric_cols = [c for c in numeric_cols if c != 'السنة']
    
    growth_analysis = ""
    if len(numeric_cols) > 0 and 'السنة' in df.columns:
        for col in numeric_cols[:5]:  # أول 5 مؤشرات
            try:
                first_val = df.groupby('الدولة')[col].first().mean()
                last_val = df.groupby('الدولة')[col].last().mean()
                if first_val > 0:
                    growth = ((last_val - first_val) / first_val) * 100
                    growth_analysis += f"\n- {col}: نمو {growth:.1f}%"
            except:
                pass
    
    prompt = f"""
أنت محلل اقتصادي خبير. اكتب تقريراً تحليلياً شاملاً ومهنياً باللغة العربية.

═══════════════════════════════════════
البيانات المتاحة:
- الدول: {', '.join(countries)}
- المؤشرات: {', '.join([i['name'] for i in indicators])}
- الفترة: من {df['السنة'].min()} إلى {df['السنة'].max()}
- عدد السجلات: {len(df)}

الإحصائيات الوصفية:
{stats_summary}

تحليل النمو:
{growth_analysis}
═══════════════════════════════════════

اكتب تقريراً يتضمن:

1. **الملخص التنفيذي** (3-4 جمل)
   - أهم النتائج والاستنتاجات

2. **تحليل الاتجاهات العامة**
   - كيف تطورت المؤشرات عبر الزمن؟
   - ما هي الأنماط الملاحظة؟

3. **المقارنة بين الدول** (إذا كان هناك أكثر من دولة)
   - أي الدول أفضل أداءً؟
   - ما هي الفجوات؟

4. **تحليل العلاقات**
   - هل هناك علاقة بين المؤشرات المختلفة؟
   - مثلاً: هل زيادة الصادرات رفعت الناتج المحلي؟

5. **التوقعات والتوصيات**
   - ما هو الاتجاه المتوقع؟
   - ما هي التوصيات للسياسات الاقتصادية؟

استخدم أرقاماً ونسباً محددة من البيانات. اكتب بأسلوب أكاديمي ومهني.
"""

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.7,
                max_output_tokens=4000
            )
        )
        return response.text if response.text else "تعذر توليد التقرير."
        
    except Exception as e:
        return f"خطأ في توليد التقرير: {e}"

# ═══════════════════════════════════════════════════════════════════════════════
# 7. الدردشة التفاعلية مع البيانات
# ═══════════════════════════════════════════════════════════════════════════════

def chat_with_data(client, df, user_question, chat_history):
    """محادثة تفاعلية حول البيانات"""
    
    # تحضير سياق البيانات
    data_summary = f"""
البيانات المتاحة:
- الدول: {', '.join(df['الدولة'].unique())}
- الأعمدة: {', '.join(df.columns.tolist())}
- الفترة: {df['السنة'].min()} - {df['السنة'].max()}
- عدد السجلات: {len(df)}

إحصائيات مختصرة:
{df.describe().to_string()[:2000]}
"""
    
    # بناء سياق المحادثة
    history_context = "\n".join([f"المستخدم: {h['user']}\nالمساعد: {h['assistant']}" for h in chat_history[-5:]])
    
    prompt = f"""
أنت مساعد تحليل بيانات اقتصادية ذكي. أجب على سؤال المستخدم بناءً على البيانات المتاحة.

{data_summary}

المحادثة السابقة:
{history_context}

سؤال المستخدم الحالي: {user_question}

أجب بشكل مختصر ومفيد. استخدم أرقاماً محددة من البيانات عند الإمكان.
إذا طُلب منك إجراء حسابات، قم بها بدقة.
"""

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.5,
                max_output_tokens=1500
            )
        )
        return response.text if response.text else "عذراً، لم أستطع الإجابة."
        
    except Exception as e:
        return f"خطأ: {e}"

# ═══════════════════════════════════════════════════════════════════════════════
# 8. إنشاء الرسوم البيانية الاحترافية
# ═══════════════════════════════════════════════════════════════════════════════

def create_professional_charts(df, chart_type="line"):
    """إنشاء رسوم بيانية احترافية بألوان دافئة"""
    
    # لوحة ألوان دافئة ذهبية
    warm_colors = [
        '#D4AF37', '#B8960C', '#996515', '#CD853F', 
        '#8B7355', '#A0522D', '#D2691E', '#E8C872',
        '#C17F59', '#6B5B45', '#5D4E37', '#DEB887'
    ]
    
    numeric_cols = [c for c in df.columns if c not in ['الدولة', 'CountryCode', 'السنة']]
    charts = []
    
    for col in numeric_cols:
        if chart_type == "line":
            fig = px.line(
                df, 
                x='السنة', 
                y=col, 
                color='الدولة',
                markers=True,
                title=f"📈 تطور {col} عبر الزمن",
                color_discrete_sequence=warm_colors
            )
        elif chart_type == "bar":
            fig = px.bar(
                df, 
                x='السنة', 
                y=col, 
                color='الدولة',
                barmode='group',
                title=f"📊 مقارنة {col}",
                color_discrete_sequence=warm_colors
            )
        elif chart_type == "area":
            fig = px.area(
                df, 
                x='السنة', 
                y=col, 
                color='الدولة',
                title=f"📈 {col} (مخطط مساحي)",
                color_discrete_sequence=warm_colors
            )
        
        # تنسيق الرسم
        fig.update_layout(
            font=dict(family="Cairo, Arial", size=14, color='#5D4E37'),
            title=dict(font=dict(size=18, color='#996515')),
            paper_bgcolor='rgba(255, 248, 231, 0.8)',
            plot_bgcolor='rgba(255, 254, 249, 0.9)',
            legend=dict(
                bgcolor='rgba(255, 248, 231, 0.8)',
                bordercolor='#D4AF37',
                borderwidth=1
            ),
            xaxis=dict(
                gridcolor='rgba(212, 175, 55, 0.3)',
                title=dict(font=dict(color='#5D4E37'))
            ),
            yaxis=dict(
                gridcolor='rgba(212, 175, 55, 0.3)',
                title=dict(font=dict(color='#5D4E37'))
            ),
            hoverlabel=dict(
                bgcolor='#5D4E37',
                font_size=14,
                font_family="Cairo"
            )
        )
        
        charts.append((col, fig))
    
    return charts

def create_correlation_heatmap(df):
    """إنشاء خريطة حرارية للارتباطات"""
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    numeric_cols = [c for c in numeric_cols if c != 'السنة']
    
    if len(numeric_cols) < 2:
        return None
    
    corr_matrix = df[numeric_cols].corr()
    
    fig = px.imshow(
        corr_matrix,
        text_auto='.2f',
        aspect='auto',
        color_continuous_scale=['#5D4E37', '#FFF8E7', '#D4AF37'],
        title='🔥 مصفوفة الارتباط بين المؤشرات'
    )
    
    fig.update_layout(
        font=dict(family="Cairo, Arial", size=12, color='#5D4E37'),
        paper_bgcolor='rgba(255, 248, 231, 0.8)',
        title=dict(font=dict(size=18, color='#996515'))
    )
    
    return fig

def create_map_chart(df, indicator_col):
    """إنشاء خريطة جغرافية"""
    
    if 'CountryCode' not in df.columns or indicator_col not in df.columns:
        return None
    
    # أحدث سنة
    latest_year = df['السنة'].max()
    df_latest = df[df['السنة'] == latest_year]
    
    fig = px.choropleth(
        df_latest,
        locations='CountryCode',
        color=indicator_col,
        hover_name='الدولة',
        color_continuous_scale=['#FFF8E7', '#D4AF37', '#996515'],
        title=f'🗺️ خريطة {indicator_col} ({latest_year})'
    )
    
    fig.update_layout(
        font=dict(family="Cairo, Arial", color='#5D4E37'),
        paper_bgcolor='rgba(255, 248, 231, 0.8)',
        geo=dict(
            bgcolor='rgba(255, 248, 231, 0.5)',
            showframe=False
        )
    )
    
    return fig

# ═══════════════════════════════════════════════════════════════════════════════
# 9. تصدير التقارير والبيانات
# ═══════════════════════════════════════════════════════════════════════════════

def generate_html_report(df, analysis_text, charts_data):
    """إنشاء تقرير HTML احترافي"""
    
    html_template = f"""
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تقرير التحليل الاقتصادي | د. مروان رودان</title>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Cairo', sans-serif;
            background: linear-gradient(135deg, #FFF8E7 0%, #FDF5E6 100%);
            color: #5D4E37;
            line-height: 1.8;
            padding: 40px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        .header {{
            background: linear-gradient(135deg, #D4AF37 0%, #F4E4BA 50%, #D4AF37 100%);
            padding: 40px;
            border-radius: 20px;
            text-align: center;
            margin-bottom: 40px;
            box-shadow: 0 8px 32px rgba(212, 175, 55, 0.4);
            border: 3px solid #996515;
        }}
        
        .header h1 {{
            color: #5D4E37;
            font-size: 2.5rem;
            margin-bottom: 10px;
        }}
        
        .header p {{
            color: #6B5B45;
            font-size: 1.1rem;
        }}
        
        .section {{
            background: white;
            padding: 30px;
            border-radius: 16px;
            margin-bottom: 30px;
            box-shadow: 0 5px 25px rgba(212, 175, 55, 0.15);
            border-top: 4px solid #D4AF37;
        }}
        
        .section h2 {{
            color: #996515;
            font-size: 1.5rem;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #D4AF37;
        }}
        
        .analysis-content {{
            white-space: pre-wrap;
            text-align: justify;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        
        th, td {{
            padding: 12px;
            text-align: right;
            border-bottom: 1px solid #D4AF37;
        }}
        
        th {{
            background: linear-gradient(135deg, #D4AF37 0%, #B8960C 100%);
            color: white;
        }}
        
        tr:hover {{
            background: rgba(212, 175, 55, 0.1);
        }}
        
        .footer {{
            text-align: center;
            padding: 30px;
            color: #5D4E37;
            margin-top: 40px;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        
        .stat-card {{
            background: linear-gradient(145deg, #FFF8E7 0%, #F4E4BA 100%);
            padding: 20px;
            border-radius: 12px;
            text-align: center;
            border: 2px solid #D4AF37;
        }}
        
        .stat-value {{
            font-size: 2rem;
            font-weight: 700;
            color: #996515;
        }}
        
        .stat-label {{
            color: #5D4E37;
            font-size: 0.9rem;
        }}
        
        @media print {{
            body {{
                padding: 20px;
            }}
            .section {{
                break-inside: avoid;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌍 تقرير التحليل الاقتصادي</h1>
            <p>من إعداد: الدكتور مروان رودان</p>
            <p style="margin-top: 10px; font-size: 0.9rem;">تاريخ التقرير: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        </div>
        
        <div class="section">
            <h2>📊 ملخص البيانات</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value">{len(df)}</div>
                    <div class="stat-label">عدد السجلات</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{df['الدولة'].nunique() if 'الدولة' in df.columns else 'N/A'}</div>
                    <div class="stat-label">عدد الدول</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{df['السنة'].min() if 'السنة' in df.columns else 'N/A'} - {df['السنة'].max() if 'السنة' in df.columns else 'N/A'}</div>
                    <div class="stat-label">الفترة الزمنية</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{len([c for c in df.columns if c not in ['الدولة', 'CountryCode', 'السنة']])}</div>
                    <div class="stat-label">عدد المؤشرات</div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>📈 التحليل الاقتصادي</h2>
            <div class="analysis-content">{analysis_text}</div>
        </div>
        
        <div class="section">
            <h2>📋 البيانات الإحصائية</h2>
            {df.describe().to_html(classes='data-table')}
        </div>
        
        <div class="section">
            <h2>🔢 عينة من البيانات</h2>
            {df.head(20).to_html(classes='data-table', index=False)}
        </div>
        
        <div class="footer">
            <p>© {datetime.now().year} - تقرير من إعداد الدكتور مروان رودان</p>
            <p>World Bank Data Analysis Dashboard</p>
        </div>
    </div>
</body>
</html>
"""
    return html_template

def export_to_excel(df, analysis_text=""):
    """تصدير البيانات إلى Excel"""
    
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # البيانات الرئيسية
        df.to_excel(writer, sheet_name='البيانات', index=False)
        
        # الإحصائيات
        df.describe().to_excel(writer, sheet_name='الإحصائيات')
        
        # التحليل (إذا وجد)
        if analysis_text:
            analysis_df = pd.DataFrame({'التحليل': [analysis_text]})
            analysis_df.to_excel(writer, sheet_name='التحليل', index=False)
    
    return output.getvalue()

# ═══════════════════════════════════════════════════════════════════════════════
# 10. الواجهة الرئيسية
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """الدالة الرئيسية للتطبيق"""
    
    # العنوان الرئيسي
    st.markdown("""
    <div class="main-header">
        <h1>🌍 لوحة القيادة الاقتصادية الذكية</h1>
        <p>تحليل بيانات البنك الدولي باستخدام الذكاء الاصطناعي</p>
        <p style="font-size: 1rem; margin-top: 15px; font-weight: 700;">من إعداد: الدكتور مروان رودان</p>
    </div>
    """, unsafe_allow_html=True)
    
    # تهيئة Session State
    if 'df' not in st.session_state:
        st.session_state['df'] = None
    if 'parsed' not in st.session_state:
        st.session_state['parsed'] = None
    if 'analysis' not in st.session_state:
        st.session_state['analysis'] = None
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []
    if 'api_key' not in st.session_state:
        st.session_state['api_key'] = ""
    if 'client' not in st.session_state:
        st.session_state['client'] = None
    if 'gemini_configured' not in st.session_state:
        st.session_state['gemini_configured'] = False
    
    # ═══════════════════════════════════════════════════════════════════════════
    # الشريط الجانبي (على اليمين)
    # ═══════════════════════════════════════════════════════════════════════════
    
    with st.sidebar:
        st.markdown("## ⚙️ الإعدادات")
        
        st.markdown("---")
        
        # إدخال مفتاح API
        st.markdown("### 🔑 مفتاح API")
        api_key = st.text_input(
            "أدخل مفتاح Gemini API:",
            type="password",
            value=st.session_state.get('api_key', ''),
            help="احصل على مفتاح API من: https://aistudio.google.com/apikey"
        )
        
        if api_key and api_key != st.session_state.get('api_key', ''):
            st.session_state['api_key'] = api_key
            
            if GENAI_AVAILABLE:
                client, success, message = configure_gemini(api_key)
                if success:
                    st.session_state['client'] = client
                    st.session_state['gemini_configured'] = True
                    st.success(message)
                else:
                    st.session_state['gemini_configured'] = False
                    st.error(message)
            else:
                st.error("❌ مكتبة google-genai غير مثبتة")
        
        st.markdown("---")
        
        # ═══════════════════════════════════════════════════════════════════════
        # 🔍 البحث السريع - يعمل بدون API!
        # ═══════════════════════════════════════════════════════════════════════
        
        st.markdown("### 🔍 البحث السريع")
        st.markdown("**اكتب ما تريد بكل بساطة:**")
        
        query = st.text_input(
            "🔎 ابحث هنا:",
            value="",
            placeholder="مثال: الصادرات في تنزانيا أو GDP Algeria",
            help="اكتب اسم الدولة والمؤشر الذي تريده"
        )
        
        # أمثلة قابلة للنقر
        st.markdown("#### 💡 جرب هذه الأمثلة (انقر للتطبيق):")
        
        examples_col1, examples_col2 = st.columns(2)
        
        with examples_col1:
            if st.button("📊 صادرات تنزانيا", use_container_width=True, key="ex1"):
                st.session_state['search_query'] = "الصادرات في تنزانيا"
            if st.button("💰 GDP مصر", use_container_width=True, key="ex2"):
                st.session_state['search_query'] = "الناتج المحلي مصر"
            if st.button("📈 تضخم الجزائر", use_container_width=True, key="ex3"):
                st.session_state['search_query'] = "التضخم في الجزائر 2010-2023"
            if st.button("👥 سكان السعودية", use_container_width=True, key="ex4"):
                st.session_state['search_query'] = "السكان في السعودية"
        
        with examples_col2:
            if st.button("🌍 دول الخليج", use_container_width=True, key="ex5"):
                st.session_state['search_query'] = "الناتج المحلي والتضخم لدول الخليج"
            if st.button("🇲🇦 المغرب العربي", use_container_width=True, key="ex6"):
                st.session_state['search_query'] = "الصادرات والواردات للجزائر والمغرب وتونس"
            if st.button("💹 BRICS", use_container_width=True, key="ex7"):
                st.session_state['search_query'] = "GDP growth BRICS countries"
            if st.button("🏦 بطالة كينيا", use_container_width=True, key="ex8"):
                st.session_state['search_query'] = "البطالة في كينيا"
        
        # تطبيق المثال المختار
        if 'search_query' in st.session_state and st.session_state['search_query']:
            query = st.session_state['search_query']
            st.session_state['search_query'] = ""  # مسح بعد الاستخدام
        
        st.markdown("---")
        
        # زر البحث
        search_button = st.button(
            "🚀 ابحث الآن",
            type="primary",
            use_container_width=True
        )
        
        st.markdown("---")
        
        # ═══════════════════════════════════════════════════════════════════════
        # مفتاح API (اختياري للميزات المتقدمة)
        # ═══════════════════════════════════════════════════════════════════════
        
        with st.expander("🔑 مفتاح API (اختياري للتقارير الذكية)", expanded=False):
            api_key = st.text_input(
                "مفتاح Gemini API:",
                type="password",
                value=st.session_state.get('api_key', ''),
                help="للتقارير والدردشة الذكية فقط - البحث يعمل بدونه!"
            )
            
            if api_key and api_key != st.session_state.get('api_key', ''):
                st.session_state['api_key'] = api_key
                
                if GENAI_AVAILABLE:
                    client, success, message = configure_gemini(api_key)
                    if success:
                        st.session_state['client'] = client
                        st.session_state['gemini_configured'] = True
                        st.success(message)
                    else:
                        st.session_state['gemini_configured'] = False
                        st.error(message)
        
        st.markdown("---")
        
        # خيارات الرسوم البيانية
        st.markdown("### 📊 خيارات العرض")
        chart_type = st.selectbox(
            "نوع الرسم البياني:",
            ["خطي", "أعمدة", "مساحي"],
            index=0
        )
        chart_type_map = {"خطي": "line", "أعمدة": "bar", "مساحي": "area"}
        
        show_map = st.checkbox("عرض الخريطة الجغرافية", value=True)
        show_correlation = st.checkbox("عرض مصفوفة الارتباط", value=True)
        
        st.markdown("---")
        
        # معلومات إضافية
        st.markdown("""
        <div style="text-align: center; padding: 15px; background: linear-gradient(145deg, #FFF8E7, #F4E4BA); border-radius: 10px; border: 2px solid #D4AF37;">
            <p style="color: #5D4E37; font-size: 0.9rem; margin: 0;">
                📚 المصدر: البنك الدولي<br>
                🔍 البحث يعمل بدون API!<br>
                👨‍💼 د. مروان رودان
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # معالجة الطلب - البحث المحلي الذكي + API كخيار إضافي
    # ═══════════════════════════════════════════════════════════════════════════
    
    if search_button and query:
        # أولاً: محاولة البحث المحلي الذكي (بدون API)
        parsed = smart_local_search(query)
        
        # إذا فشل البحث المحلي ولدينا API، نستخدم Gemini
        if not parsed and st.session_state.get('gemini_configured'):
            client = st.session_state.get('client')
            if client:
                with st.spinner("🤖 جاري تحليل طلبك بالذكاء الاصطناعي..."):
                    parsed = parse_query_with_ai(client, query)
        
        # التحقق من النتائج
        if not parsed or not parsed.get('countries'):
            st.error("""
            ❌ لم يتم العثور على دولة في طلبك!
            
            **جرب كتابة اسم الدولة بوضوح، مثل:**
            - الصادرات في تنزانيا
            - GDP مصر
            - التضخم الجزائر 2010-2023
            - exports Tanzania
            """)
            st.stop()
        
        if not parsed.get('indicators'):
            # إضافة مؤشر افتراضي
            parsed['indicators'] = [{"code": "NY.GDP.MKTP.CD", "name": "الناتج المحلي الإجمالي"}]
        
        # عرض ما تم فهمه
        with st.expander("✅ ما تم فهمه من طلبك", expanded=True):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**🌍 الدول:**")
                for c in parsed['countries']:
                    st.markdown(f"- `{c}`")
            
            with col2:
                st.markdown("**📊 المؤشرات:**")
                for ind in parsed['indicators']:
                    name = ind.get('name', ind.get('code', ''))
                    code = ind.get('code', '')
                    st.markdown(f"- {name} (`{code}`)")
            
            with col3:
                st.markdown("**📅 الفترة:**")
                st.markdown(f"من **{parsed.get('start', 2010)}** إلى **{parsed.get('end', 2023)}**")
        
        # جلب البيانات من البنك الدولي
        with st.spinner("📥 جاري جلب البيانات من البنك الدولي..."):
            df = fetch_world_bank_data(
                parsed['countries'],
                parsed['indicators'],
                parsed.get('start', 2010),
                parsed.get('end', 2023)
            )
        
        if df.empty:
            st.error("❌ لا توجد بيانات متاحة. جرب تغيير الفترة الزمنية أو المؤشرات.")
            st.stop()
        
        # حفظ في Session State
        st.session_state['df'] = df
        st.session_state['parsed'] = parsed
        
        st.success(f"✅ تم جلب {len(df):,} سجل بنجاح!")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # عرض البيانات والتحليلات
    # ═══════════════════════════════════════════════════════════════════════════
    
    if st.session_state.get('df') is not None and not st.session_state['df'].empty:
        df = st.session_state['df']
        parsed = st.session_state['parsed']
        
        # بطاقات المؤشرات الرئيسية
        st.markdown("### 📈 نظرة عامة")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <p class="metric-value">{len(df):,}</p>
                <p class="metric-label">📊 إجمالي السجلات</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <p class="metric-value">{df['الدولة'].nunique()}</p>
                <p class="metric-label">🌍 عدد الدول</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            indicators_count = len([c for c in df.columns if c not in ['الدولة', 'CountryCode', 'السنة']])
            st.markdown(f"""
            <div class="metric-card">
                <p class="metric-value">{indicators_count}</p>
                <p class="metric-label">📉 عدد المؤشرات</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <p class="metric-value">{df['السنة'].min()} - {df['السنة'].max()}</p>
                <p class="metric-label">📅 الفترة الزمنية</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # التبويبات الرئيسية
        tabs = st.tabs([
            "📈 الرسوم البيانية",
            "🗺️ الخرائط",
            "🔢 البيانات",
            "🔥 التحليل الإحصائي",
            "📝 التقرير الذكي",
            "💬 الدردشة التفاعلية",
            "💾 التصدير"
        ])
        
        # ═══════════════════════════════════════════════════════════════════════
        # تبويب 1: الرسوم البيانية
        # ═══════════════════════════════════════════════════════════════════════
        
        with tabs[0]:
            st.markdown("### 📈 الرسوم البيانية التفاعلية")
            
            chart_type_selected = chart_type_map.get(chart_type, "line")
            charts = create_professional_charts(df, chart_type_selected)
            
            for col_name, fig in charts:
                st.plotly_chart(fig, use_container_width=True)
                st.markdown("---")
        
        # ═══════════════════════════════════════════════════════════════════════
        # تبويب 2: الخرائط
        # ═══════════════════════════════════════════════════════════════════════
        
        with tabs[1]:
            st.markdown("### 🗺️ الخرائط الجغرافية")
            
            numeric_cols = [c for c in df.columns if c not in ['الدولة', 'CountryCode', 'السنة']]
            
            if numeric_cols and show_map:
                selected_indicator = st.selectbox(
                    "اختر المؤشر للخريطة:",
                    numeric_cols
                )
                
                map_fig = create_map_chart(df, selected_indicator)
                if map_fig:
                    st.plotly_chart(map_fig, use_container_width=True)
                else:
                    st.info("لا يمكن عرض الخريطة (تأكد من وجود أكواد الدول)")
            else:
                st.info("لا توجد بيانات كافية للخريطة")
        
        # ═══════════════════════════════════════════════════════════════════════
        # تبويب 3: البيانات
        # ═══════════════════════════════════════════════════════════════════════
        
        with tabs[2]:
            st.markdown("### 🔢 البيانات الخام")
            
            # فلترة
            col1, col2 = st.columns(2)
            
            with col1:
                selected_countries = st.multiselect(
                    "فلترة حسب الدولة:",
                    options=df['الدولة'].unique().tolist(),
                    default=df['الدولة'].unique().tolist()
                )
            
            with col2:
                year_range = st.slider(
                    "نطاق السنوات:",
                    min_value=int(df['السنة'].min()),
                    max_value=int(df['السنة'].max()),
                    value=(int(df['السنة'].min()), int(df['السنة'].max()))
                )
            
            # تطبيق الفلترة
            filtered_df = df[
                (df['الدولة'].isin(selected_countries)) &
                (df['السنة'] >= year_range[0]) &
                (df['السنة'] <= year_range[1])
            ]
            
            st.dataframe(filtered_df, use_container_width=True, height=400)
            
            # الإحصائيات
            st.markdown("### 📊 الإحصائيات الوصفية")
            st.dataframe(filtered_df.describe(), use_container_width=True)
        
        # ═══════════════════════════════════════════════════════════════════════
        # تبويب 4: التحليل الإحصائي
        # ═══════════════════════════════════════════════════════════════════════
        
        with tabs[3]:
            st.markdown("### 🔥 التحليل الإحصائي المتقدم")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # مصفوفة الارتباط
                if show_correlation:
                    corr_fig = create_correlation_heatmap(df)
                    if corr_fig:
                        st.plotly_chart(corr_fig, use_container_width=True)
            
            with col2:
                # تحليل الاتجاه
                numeric_cols = [c for c in df.columns if c not in ['الدولة', 'CountryCode', 'السنة']]
                
                if numeric_cols:
                    trend_indicator = st.selectbox(
                        "اختر مؤشراً لتحليل الاتجاه:",
                        numeric_cols
                    )
                    
                    fig_trend = px.scatter(
                        df,
                        x='السنة',
                        y=trend_indicator,
                        color='الدولة',
                        trendline='ols',
                        title=f'📈 خط الاتجاه لـ {trend_indicator}',
                        color_discrete_sequence=['#D4AF37', '#B8960C', '#996515', '#8B7355', '#5D4E37']
                    )
                    
                    fig_trend.update_layout(
                        font=dict(family="Cairo, Arial", color='#5D4E37'),
                        paper_bgcolor='rgba(255, 248, 231, 0.8)',
                        plot_bgcolor='rgba(255, 254, 249, 0.9)'
                    )
                    
                    st.plotly_chart(fig_trend, use_container_width=True)
        
        # ═══════════════════════════════════════════════════════════════════════
        # تبويب 5: التقرير الذكي
        # ═══════════════════════════════════════════════════════════════════════
        
        with tabs[4]:
            st.markdown("### 📝 التقرير التحليلي الذكي")
            
            if st.button("✨ توليد تقرير ذكي بالذكاء الاصطناعي", type="primary", use_container_width=True):
                if not st.session_state.get('gemini_configured'):
                    st.error("⚠️ يرجى إدخال مفتاح API")
                else:
                    client = st.session_state.get('client')
                    
                    if client:
                        with st.spinner("🤖 جاري كتابة التقرير بالذكاء الاصطناعي..."):
                            analysis = generate_ai_analysis(
                                client,
                                df,
                                parsed['countries'],
                                parsed['indicators']
                            )
                            st.session_state['analysis'] = analysis
            
            # عرض التقرير
            if st.session_state.get('analysis'):
                st.markdown("""
                <div class="report-section">
                """, unsafe_allow_html=True)
                
                st.markdown(st.session_state['analysis'])
                
                st.markdown("</div>", unsafe_allow_html=True)
        
        # ═══════════════════════════════════════════════════════════════════════
        # تبويب 6: الدردشة التفاعلية
        # ═══════════════════════════════════════════════════════════════════════
        
        with tabs[5]:
            st.markdown("### 💬 الدردشة التفاعلية مع البيانات")
            st.markdown("اسأل أي سؤال عن البيانات وسيجيبك الذكاء الاصطناعي!")
            
            # عرض المحادثات السابقة
            for chat in st.session_state.get('chat_history', []):
                st.markdown(f"""
                <div class="user-message">👤 {chat['user']}</div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="ai-response">🤖 {chat['assistant']}</div>
                """, unsafe_allow_html=True)
            
            # إدخال السؤال
            user_question = st.text_input(
                "اكتب سؤالك:",
                placeholder="مثال: ما هي الدولة الأعلى في الناتج المحلي؟"
            )
            
            col1, col2 = st.columns([4, 1])
            
            with col1:
                if st.button("📤 إرسال", use_container_width=True):
                    if user_question and st.session_state.get('gemini_configured'):
                        client = st.session_state.get('client')
                        
                        if client:
                            with st.spinner("🤔 جاري التفكير..."):
                                response = chat_with_data(
                                    client,
                                    df,
                                    user_question,
                                    st.session_state.get('chat_history', [])
                                )
                                
                                st.session_state['chat_history'].append({
                                    'user': user_question,
                                    'assistant': response
                                })
                                
                                st.rerun()
            
            with col2:
                if st.button("🗑️ مسح", use_container_width=True):
                    st.session_state['chat_history'] = []
                    st.rerun()
        
        # ═══════════════════════════════════════════════════════════════════════
        # تبويب 7: التصدير
        # ═══════════════════════════════════════════════════════════════════════
        
        with tabs[6]:
            st.markdown("### 💾 تصدير البيانات والتقارير")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 📊 تصدير البيانات")
                
                # Excel
                excel_data = export_to_excel(df, st.session_state.get('analysis', ''))
                st.download_button(
                    label="📥 تحميل Excel",
                    data=excel_data,
                    file_name=f"economic_data_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
                
                # CSV
                csv_data = df.to_csv(index=False).encode('utf-8-sig')
                st.download_button(
                    label="📥 تحميل CSV",
                    data=csv_data,
                    file_name=f"economic_data_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            with col2:
                st.markdown("#### 📝 تصدير التقارير")
                
                # HTML Report
                if st.session_state.get('analysis'):
                    html_report = generate_html_report(
                        df,
                        st.session_state['analysis'],
                        None
                    )
                    
                    st.download_button(
                        label="📥 تحميل التقرير (HTML)",
                        data=html_report,
                        file_name=f"economic_report_{datetime.now().strftime('%Y%m%d')}.html",
                        mime="text/html",
                        use_container_width=True
                    )
                else:
                    st.info("قم بتوليد التقرير الذكي أولاً من تبويب 'التقرير الذكي'")
                
                # JSON
                json_data = df.to_json(orient='records', force_ascii=False)
                st.download_button(
                    label="📥 تحميل JSON",
                    data=json_data,
                    file_name=f"economic_data_{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json",
                    use_container_width=True
                )
    
    else:
        # رسالة ترحيبية
        st.markdown("""
        <div style="text-align: center; padding: 60px 20px; background: linear-gradient(145deg, #FFFEF9, #FFF8E7); border-radius: 20px; border: 2px solid #D4AF37; margin: 20px 0;">
            <h2 style="color: #996515;">👋 مرحباً بك في لوحة القيادة الاقتصادية</h2>
            <p style="color: #5D4E37; font-size: 1.2rem; margin: 20px 0;">
                استخدم الشريط الجانبي (على اليمين) للبدء:
            </p>
            <ol style="text-align: right; max-width: 500px; margin: 0 auto; color: #5D4E37; font-size: 1.1rem;">
                <li style="margin: 10px 0;">أدخل مفتاح Google Gemini API</li>
                <li style="margin: 10px 0;">اكتب طلبك بالعربية (مثل: الناتج المحلي للجزائر)</li>
                <li style="margin: 10px 0;">اضغط على "تحليل وجلب البيانات"</li>
            </ol>
            <p style="color: #D4AF37; margin-top: 30px; font-weight: 600;">
                💡 يمكنك استخدام الأمثلة السريعة في الشريط الجانبي
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
    <div class="footer">
        <p style="font-size: 1.3rem; font-weight: 700;">🌍 لوحة القيادة الاقتصادية الذكية</p>
        <p style="font-size: 1.1rem;">من إعداد: الدكتور مروان رودان</p>
        <p style="font-size: 0.9rem; margin-top: 10px;">مصدر البيانات: البنك الدولي</p>
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# تشغيل التطبيق
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    main()
