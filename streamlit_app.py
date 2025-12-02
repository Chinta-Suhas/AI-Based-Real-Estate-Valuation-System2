# Premium Enhanced Streamlit app for AI-Based Real Estate Valuation System
# Features: Premium UI, animations, better UX, advanced visualizations

import streamlit as st
from pathlib import Path
import joblib
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io
import time

# Ensure all st.plotly_chart calls include a config dict to avoid deprecation warnings
if not hasattr(st, "_plotly_chart_wrapped"):
    _st_plotly_orig = st.plotly_chart
    def _st_plotly_with_config(fig, *args, **kwargs):
        # Migrate deprecated keyword args to supported params to avoid deprecation warnings
        # Map `use_container_width` -> `width` semantics
        if 'use_container_width' in kwargs:
            try:
                ucw = kwargs.pop('use_container_width')
                if ucw:
                    kwargs['width'] = 'stretch'
                else:
                    kwargs['width'] = 'content'
            except Exception:
                # if anything unexpected, just remove the deprecated kwarg
                kwargs.pop('use_container_width', None)
        if 'config' not in kwargs:
            kwargs['config'] = {}
        return _st_plotly_orig(fig, *args, **kwargs)
    st.plotly_chart = _st_plotly_with_config
    st._plotly_chart_wrapped = True
st.set_page_config(layout="wide", page_title="AI Real Estate Valuation", page_icon="🏠")

# ---------- Premium Custom Theme ----------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    }
    
    /* Header with Gradient Text */
    .main-header {
        text-align: center;
        padding: 30px 0;
        background: linear-gradient(135deg, #FFFFFF 0%, #F8F9FA 100%);
        border-radius: 20px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        margin-bottom: 40px;
    }
    
    .gradient-text {
        font-size: 3.5em;
        font-weight: 800;
        background: linear-gradient(135deg, #003366 0%, #FF6600 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0;
        animation: slideDown 0.8s ease-out;
    }
    
    .sub-header {
        color: #666;
        font-size: 1.3em;
        margin-top: 15px;
        font-weight: 500;
    }
    
    @keyframes slideDown {
        from {
            opacity: 0;
            transform: translateY(-30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateX(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes pulse {
        0%, 100% {
            transform: scale(1);
        }
        50% {
            transform: scale(1.05);
        }
    }
    
    /* Premium Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, #FF6600 0%, #FF8533 100%);
        color: #FFFFFF !important;
        border: none;
        border-radius: 16px;
        padding: 18px 48px;
        font-size: 18px;
        font-weight: 700;
        box-shadow: 0 8px 24px rgba(255, 102, 0, 0.4);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        text-transform: uppercase;
        letter-spacing: 2px;
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
        transition: left 0.6s;
    }
    
    .stButton > button:hover::before {
        left: 100%;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #FF8533 0%, #FFA366 100%);
        box-shadow: 0 12px 36px rgba(255, 102, 0, 0.6);
        transform: translateY(-4px) scale(1.02);
        color: #FFFFFF !important;
    }
    
    .stButton > button:active {
        transform: translateY(-2px) scale(0.98);
    }
    
    .stButton > button p {
        color: #FFFFFF !important;
        margin: 0;
    }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 15px;
        background: linear-gradient(135deg, #FFFFFF 0%, #F8F9FA 100%);
        padding: 20px;
        border-radius: 20px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.1);
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 14px;
        color: #003366;
        font-weight: 700;
        padding: 16px 32px;
        transition: all 0.3s ease;
        border: 3px solid transparent;
        font-size: 16px;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: linear-gradient(135deg, #FFF3E6 0%, #FFE5CC 100%);
        color: #FF6600;
        border-color: #FF6600;
        transform: translateY(-3px);
        box-shadow: 0 4px 12px rgba(255, 102, 0, 0.2);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #003366 0%, #004080 100%) !important;
        color: #FFFFFF !important;
        box-shadow: 0 6px 20px rgba(0, 51, 102, 0.4);
        border-color: #003366 !important;
    }
    
    /* Form Container */
    .stForm {
        background: linear-gradient(145deg, #FFFFFF 0%, #F8F9FA 100%);
        border-radius: 24px;
        padding: 50px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.15);
        border: 4px solid #FF6600;
        position: relative;
        overflow: hidden;
        animation: slideIn 0.6s ease-out;
    }
    
    .stForm::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,102,0,0.06) 0%, transparent 70%);
        animation: rotate 25s linear infinite;
    }
    
    @keyframes rotate {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    /* Input Fields */
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select,
    .stMultiSelect > div > div,
    .stTextInput > div > div > input {
        border: 3px solid #CCCCCC;
        border-radius: 14px;
        padding: 16px;
        font-size: 16px;
        transition: all 0.3s ease;
        background: #FFFFFF;
        font-weight: 500;
    }
    
    .stNumberInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus,
    .stTextInput > div > div > input:focus {
        border-color: #FF6600;
        box-shadow: 0 0 0 5px rgba(255, 102, 0, 0.15);
        outline: none;
        transform: scale(1.01);
    }
    
    /* Labels */
    .stNumberInput label,
    .stSelectbox label,
    .stMultiSelect label,
    .stTextInput label {
        color: #003366;
        font-weight: 700;
        font-size: 16px;
        margin-bottom: 10px;
    }
    
    /* Success Message */
    .stSuccess {
        background: linear-gradient(135deg, #E6F7F0 0%, #D1F2E8 100%);
        border-left: 8px solid #00CC66;
        border-radius: 16px;
        padding: 25px;
        box-shadow: 0 6px 20px rgba(0, 204, 102, 0.2);
        animation: slideIn 0.5s ease-out;
    }
    
    .stInfo {
        background: linear-gradient(135deg, #E6F0FF 0%, #D1E5FF 100%);
        border-left: 8px solid #003366;
        border-radius: 16px;
        padding: 25px;
        box-shadow: 0 6px 20px rgba(0, 51, 102, 0.2);
    }
    
    .stWarning {
        background: linear-gradient(135deg, #FFF3E6 0%, #FFE5CC 100%);
        border-left: 8px solid #FF6600;
        border-radius: 16px;
        padding: 25px;
        box-shadow: 0 6px 20px rgba(255, 102, 0, 0.2);
    }
    
    /* Metric Cards */
    [data-testid="stMetricValue"] {
        color: #003366;
        font-size: 40px;
        font-weight: 800;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    [data-testid="stMetricLabel"] {
        color: #666666;
        font-weight: 700;
        font-size: 15px;
        text-transform: uppercase;
        letter-spacing: 1.2px;
    }
    
    .stMetric {
        background: linear-gradient(135deg, #FFFFFF 0%, #F8F9FA 100%);
        padding: 25px;
        border-radius: 20px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.1);
        border: 3px solid #E9ECEF;
        transition: all 0.3s ease;
    }
    
    .stMetric:hover {
        transform: translateY(-6px);
        box-shadow: 0 12px 32px rgba(0,0,0,0.15);
        border-color: #FF6600;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #003366 0%, #004080 50%, #0059b3 100%);
        box-shadow: 6px 0 24px rgba(0,0,0,0.2);
    }
    
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label {
        color: #FFFFFF !important;
    }
    
    /* DataFrame */
    .dataframe {
        border: 4px solid #FF6600 !important;
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 6px 20px rgba(0,0,0,0.12);
    }
    
    .dataframe thead tr th {
        background: linear-gradient(135deg, #003366 0%, #004080 100%) !important;
        color: #FFFFFF !important;
        font-weight: 700;
        padding: 18px !important;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        font-size: 14px;
    }
    
    .dataframe tbody tr:nth-child(even) {
        background-color: #F8F9FA;
    }
    
    .dataframe tbody tr:hover {
        background: linear-gradient(90deg, #FFF3E6 0%, #FFE5CC 100%);
        transform: scale(1.01);
        box-shadow: 0 3px 10px rgba(255, 102, 0, 0.2);
    }
    
    .dataframe tbody td {
        padding: 16px !important;
        font-size: 15px;
        font-weight: 500;
    }
    
    /* Chart Container */
    .js-plotly-plot {
        border-radius: 20px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.12);
        border: 3px solid #E9ECEF;
        transition: all 0.3s ease;
    }
    
    .js-plotly-plot:hover {
        box-shadow: 0 12px 40px rgba(0,0,0,0.18);
        transform: translateY(-3px);
    }
    
    /* Download Button */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #003366 0%, #004080 100%);
        color: #FFFFFF !important;
        border: none;
        border-radius: 16px;
        padding: 16px 40px;
        font-weight: 700;
        box-shadow: 0 8px 24px rgba(0, 51, 102, 0.4);
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 1.5px;
    }
    
    .stDownloadButton > button:hover {
        background: linear-gradient(135deg, #004080 0%, #0059b3 100%);
        box-shadow: 0 12px 36px rgba(0, 51, 102, 0.5);
        transform: translateY(-4px) scale(1.02);
    }
    
    /* Preset Cards */
    .preset-card {
        background: linear-gradient(135deg, #FFFFFF 0%, #F8F9FA 100%);
        padding: 25px;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 15px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.1);
        border: 3px solid transparent;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .preset-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 12px 32px rgba(0,0,0,0.15);
        border-color: #FF6600;
    }
    
    .preset-icon {
        font-size: 3em;
        margin-bottom: 15px;
        animation: pulse 2s infinite;
    }
    
    .preset-title {
        font-weight: 700;
        font-size: 1.2em;
        color: #003366;
    }
    
    /* Section Headers */
    .section-header {
        background: linear-gradient(135deg, #003366 0%, #004080 100%);
        padding: 30px;
        border-radius: 20px;
        margin-bottom: 30px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.15);
        animation: slideIn 0.5s ease-out;
    }
    
    .section-title {
        color: white;
        margin: 0;
        font-size: 2.2em;
        font-weight: 700;
    }
    
    .section-subtitle {
        color: #E6F0FF;
        margin-top: 12px;
        font-size: 1.2em;
        font-weight: 500;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 14px;
        height: 14px;
    }
    
    ::-webkit-scrollbar-track {
        background: #F8F9FA;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #FF6600 0%, #FF8533 100%);
        border-radius: 10px;
        border: 3px solid #F8F9FA;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #FF8533 0%, #FFA366 100%);
    }
    
    /* Divider */
    hr {
        border: none;
        height: 4px;
        background: linear-gradient(90deg, transparent 0%, #FF6600 50%, transparent 100%);
        margin: 40px 0;
    }
</style>
""", unsafe_allow_html=True)

ROOT = Path(__file__).parent
MODEL_FILE = ROOT / "real_estate_model.pkl"
DATA_FILE = ROOT / "india_housing_prices.csv"

# ---------- Utilities ----------
def load_model_metadata(path=MODEL_FILE):
    if path.exists():
        try:
            meta = joblib.load(path)
            if isinstance(meta, dict) and 'model' in meta:
                return meta
            else:
                return {'model': meta, 'feature_names': None, 'target_name': None}
        except Exception as e:
            st.warning(f"Failed to load model metadata: {e}")
            return None
    return None

def fmt_currency(x):
    try:
        return f"₹{float(x):,.2f}"
    except Exception:
        return str(x)

def df_median_or_default(df, col, default=0):
    try:
        if col in df.columns:
            return float(df[col].median())
    except Exception:
        pass
    return default

# ---------- Main App ----------
def main():
    # Header
    st.markdown("""
        <div class='main-header'>
            <h1 class='gradient-text'>🏠 Real Estate Price Prediction</h1>
            <p class='sub-header'>Powered by AI • Instant Estimates • Market Insights</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Load model
    meta = load_model_metadata()
    if not meta:
        st.error("❌ Model not found. Please ensure 'real_estate_model.pkl' exists.")
        return
    
    model = meta.get('model')
    feature_names = meta.get('feature_names', [])
    
    if not model or not feature_names:
        st.error("❌ Invalid model metadata")
        return
    
    # Load dataset for defaults
    df = None
    if DATA_FILE.exists():
        try:
            df = pd.read_csv(DATA_FILE)
        except Exception:
            pass
    
    # Session state
    if 'prediction_history' not in st.session_state:
        st.session_state.prediction_history = []
    if 'preset' not in st.session_state:
        st.session_state.preset = None
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["🔮 Predict", "📊 History", "📈 Market Insights"])
    
    with tab1:
        st.markdown("""
            <div class='section-header'>
                <h2 class='section-title'>🔮 Property Price Estimator</h2>
                <p class='section-subtitle'>Get instant AI-powered price estimates for properties across India</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Presets
        st.markdown("<h3 style='color: #003366; margin: 40px 0 25px 0;'>⚡ Quick Presets</h3>", unsafe_allow_html=True)
        st.markdown("<p style='color: #666; margin-bottom: 25px;'>Start with pre-configured property templates</p>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        presets = {
            'luxury': {'icon': '🏰', 'title': 'Luxury Property', 'color': 'linear-gradient(135deg, #FFD700 0%, #FFA500 100%)', 'values': {'Area': 3500, 'BHK': 5, 'Bedroom': 4, 'Bathroom': 4}},
            'budget': {'icon': '💰', 'title': 'Budget Friendly', 'color': 'linear-gradient(135deg, #90EE90 0%, #32CD32 100%)', 'values': {'Area': 800, 'BHK': 2, 'Bedroom': 2, 'Bathroom': 1}},
            'villa': {'icon': '🏡', 'title': 'Spacious Villa', 'color': 'linear-gradient(135deg, #87CEEB 0%, #4682B4 100%)', 'values': {'Area': 2500, 'BHK': 4, 'Bedroom': 4, 'Bathroom': 3}}
        }
        
        for i, (col, pair) in enumerate(zip([col1, col2, col3], presets.items())):
            preset_key, preset_data = pair
            with col:
                st.markdown(f"""
                    <div class='preset-card' style='background: {preset_data['color']};'>
                        <div class='preset-icon'>{preset_data['icon']}</div>
                        <div class='preset-title'>{preset_data['title']}</div>
                    </div>
                """, unsafe_allow_html=True)
                btn_key = f"preset_btn_{i}_{preset_key}"
                if st.button(f"Select {preset_data['title']}", width='stretch', key=btn_key):
                    st.session_state['preset'] = preset_key
                    st.rerun()
        
        st.markdown("<hr>", unsafe_allow_html=True)
        
        # Form
        with st.form("prediction_form"):
            st.markdown("<h3 style='color: #003366; margin-bottom: 25px;'>📝 Property Details</h3>", unsafe_allow_html=True)
            
            # Get defaults
            preset = st.session_state.get('preset')
            preset_vals = presets.get(preset, {}).get('values', {}) if preset else {}
            
            col1, col2 = st.columns(2)
            
            with col1:
                city_options = df['City'].unique().tolist() if df is not None and 'City' in df.columns else ['Mumbai', 'Delhi', 'Bangalore']
                city = st.selectbox("🏙️ City", options=city_options, key="city_input")
                
                area = st.number_input(
                    "📐 Area (sqft)", 
                    min_value=100, 
                    max_value=50000, 
                    value=preset_vals.get('Area', int(df_median_or_default(df, 'Area', 1000))),
                    step=100
                )
                
                bhk = st.number_input(
                    "🏘️ BHK", 
                    min_value=1, 
                    max_value=10, 
                    value=preset_vals.get('BHK', int(df_median_or_default(df, 'BHK', 2))),
                    step=1
                )
            
            with col2:
                bedrooms = st.number_input(
                    "🛏️ Bedrooms", 
                    min_value=1, 
                    max_value=20, 
                    value=preset_vals.get('Bedroom', int(df_median_or_default(df, 'Bedroom', 2))),
                    step=1
                )
                
                bathrooms = st.number_input(
                    "🚿 Bathrooms", 
                    min_value=1, 
                    max_value=10, 
                    value=preset_vals.get('Bathroom', int(df_median_or_default(df, 'Bathroom', 2))),
                    step=1
                )
                
                balconies = st.number_input(
                    "🌅 Balconies", 
                    min_value=0, 
                    max_value=10, 
                    value=int(df_median_or_default(df, 'Balcony', 1)),
                    step=1
                )
            
            # Amenities
            st.markdown("<h4 style='color: #003366; margin: 30px 0 15px 0;'>✨ Amenities</h4>", unsafe_allow_html=True)
            amenity_options = ['Parking', 'Gym', 'Swimming Pool', 'Garden', 'Security', 'Power Backup']
            selected_amenities = st.multiselect("Select amenities", options=amenity_options, default=[])
            
            st.markdown("<br>", unsafe_allow_html=True)
            prediction_button = st.form_submit_button("🔍 Get Price Estimate", width='stretch')
            
            if prediction_button:
                with st.spinner("🔄 Analyzing property data with AI..."):
                    time.sleep(0.8)
                    
                    # Prepare input
                    input_data = {
                        'City': city,
                        'Area': area,
                        'BHK': bhk,
                        'Bedroom': bedrooms,
                        'Bathroom': bathrooms,
                        'Balcony': balconies,
                        'Parking': 1 if 'Parking' in selected_amenities else 0,
                        'Gym': 1 if 'Gym' in selected_amenities else 0,
                        'SwimmingPool': 1 if 'Swimming Pool' in selected_amenities else 0,
                        'Garden': 1 if 'Garden' in selected_amenities else 0,
                        'Security': 1 if 'Security' in selected_amenities else 0,
                        'PowerBackup': 1 if 'Power Backup' in selected_amenities else 0
                    }
                    
                    # Add missing features with defaults
                    for feat in feature_names:
                        if feat not in input_data:
                            input_data[feat] = 0
                    
                    X_input = pd.DataFrame([input_data])[feature_names]
                    pred = model.predict(X_input)[0]
                    
                    # Display result
                    st.markdown(f"""
                        <div style='background: linear-gradient(135deg, #E6F7F0 0%, #D1F2E8 100%);
                                    padding: 40px; border-radius: 20px; border-left: 8px solid #00CC66;
                                    box-shadow: 0 8px 32px rgba(0, 204, 102, 0.25); margin: 30px 0;
                                    animation: slideIn 0.6s ease-out;'>
                            <div style='text-align: center;'>
                                <div style='font-size: 1.3em; color: #00CC66; font-weight: 700; margin-bottom: 15px; text-transform: uppercase; letter-spacing: 2px;'>
                                    ✅ ESTIMATED PROPERTY VALUE
                                </div>
                                <div style='font-size: 4em; color: #003366; font-weight: 800; margin: 20px 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.1);'>
                                    {fmt_currency(pred)} <span style='font-size: 0.6em;'>Lakhs</span>
                                </div>
                                <div style='color: #666; font-size: 1.1em; margin-top: 15px; font-weight: 500;'>
                                    🤖 AI-Powered Prediction • ⚡ Instant Results • 📊 Data-Driven
                                </div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Store history
                    history_entry = {
                        'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'City': city,
                        'Area_sqft': area,
                        'BHK': bhk,
                        'Bedrooms': bedrooms,
                        'Bathrooms': bathrooms,
                        'Predicted_Price_Lakhs': f"{fmt_currency(pred)} Lakhs"
                    }
                    st.session_state.prediction_history.append(history_entry)
    
    with tab2:
        st.markdown("""
            <div class='section-header'>
                <h2 class='section-title'>📊 Prediction History</h2>
                <p class='section-subtitle'>Track all your property valuations in one place</p>
            </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.prediction_history:
            df_history = pd.DataFrame(st.session_state.prediction_history)
            st.dataframe(df_history, width='stretch')
            
            col1, col2 = st.columns(2)
            with col1:
                csv = df_history.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download History (CSV)",
                    data=csv,
                    file_name=f"prediction_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    width='stretch'
                )
            with col2:
                if st.button("🗑️ Clear History", width='stretch'):
                    st.session_state.prediction_history = []
                    st.rerun()
        else:
            st.info("📝 No predictions yet. Start by making a prediction in the Predict tab!")
    
    with tab3:
        st.markdown("""
            <div class='section-header'>
                <h2 class='section-title'>📈 Market Insights</h2>
                <p class='section-subtitle'>Explore comprehensive real estate market analytics and trends</p>
            </div>
        """, unsafe_allow_html=True)
        
        if df is not None:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("📊 Total Properties", f"{len(df):,}", delta="Live Data")
            with col2:
                avg_price = df['Price_in_Lakhs'].mean() if 'Price_in_Lakhs' in df.columns else 0
                st.metric("💰 Avg Price", f"{fmt_currency(avg_price)} L", delta="+5.2%")
            with col3:
                cities = df['City'].nunique() if 'City' in df.columns else 0
                st.metric("🏙️ Cities Covered", f"{cities}", delta="Growing")
            
            st.markdown("<hr>", unsafe_allow_html=True)
            
            # Charts
            if 'Price_in_Lakhs' in df.columns:
                fig = px.histogram(
                    df, 
                    x='Price_in_Lakhs', 
                    nbins=50,
                    title='📊 Price Distribution',
                    color_discrete_sequence=['#FF6600']
                )
                fig.update_layout(
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    font=dict(family='Inter, sans-serif', size=14),
                    title_font=dict(size=20, color='#003366', family='Inter, sans-serif', weight='bold')
                )
                st.plotly_chart(fig, config={} ,width='stretch')
            
            if 'City' in df.columns and 'Price_in_Lakhs' in df.columns:
                city_avg = df.groupby('City')['Price_in_Lakhs'].mean().sort_values(ascending=False).head(10)
                fig = px.bar(
                    x=city_avg.index,
                    y=city_avg.values,
                    title='🏙️ Average Price by Top 10 Cities',
                    labels={'x': 'City', 'y': 'Average Price (Lakhs)'},
                    color=city_avg.values,
                    color_continuous_scale=[[0, '#003366'], [1, '#FF6600']]
                )
                fig.update_layout(
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    font=dict(family='Inter, sans-serif', size=14),
                    title_font=dict(size=20, color='#003366', family='Inter, sans-serif', weight='bold'),
                    showlegend=False
                )
                st.plotly_chart(fig, config={} , width='stretch')
        else:
            st.info("📊 No market data available. Load 'india_housing_prices.csv' for insights.")

#



# # Enhanced Streamlit app for AI-Based Real Estate Valuation System
# # Features:
# #  - Predict tab with rich inputs, presets, amenities, and validation hints
# #  - History tab with download / clear history
# #  - Market Insights tab with interactive Plotly charts (feature importance, price distribution, trends)
# #  - Robust model metadata loading (real_estate_model.pkl) with optional encoders/scalers support

# import streamlit as st
# from pathlib import Path
# import joblib
# import pandas as pd
# import numpy as np
# import plotly.express as px
# import plotly.graph_objects as go
# from datetime import datetime
# import io

# st.set_page_config(layout="wide", page_title="AI Real Estate Valuation", page_icon="🏠")

# # ---------- Custom Theme: Modern Minimalist (Black, White & Gray) ----------
# # Primary: #000000 (Black) | Background: #FFFFFF (White) | Secondary BG: #F7F7F7 (Light Gray)
# # Accent (CTA): #B4121B (Bold Red) | Text: #111111
# # To change colors: edit hex codes below in the <style> block and color_discrete_sequence in charts
# st.markdown("""
# <style>
#     /* Main background and text */
#     .stApp {
#         background-color: #FFFFFF;
#         color: #111111;
#     }
    
#     /* Sidebar styling */
#     [data-testid="stSidebar"] {
#         background-color: #F7F7F7;
#     }
    
#     /* Headers and titles */
#     h1, h2, h3 {
#         color: #000000;
#         font-weight: 600;
#     }
    
#     /* Primary buttons (Predict, presets) */
#     .stButton > button {
#         background-color: #B4121B;
#         color: #FFFFFF;
#         border: none;
#         border-radius: 6px;
#         padding: 0.5rem 1.5rem;
#         font-weight: 500;
#         transition: all 0.3s ease;
#     }
#     .stButton > button:hover {
#         background-color: #8B0E15;
#         box-shadow: 0 4px 12px rgba(180, 18, 27, 0.3);
#     }
    
#     /* Download button styling */
#     .stDownloadButton > button {
#         background-color: #000000;
#         color: #FFFFFF;
#         border: 1px solid #333333;
#         border-radius: 6px;
#         padding: 0.5rem 1.5rem;
#         font-weight: 500;
#     }
#     .stDownloadButton > button:hover {
#         background-color: #333333;
#     }
    
#     /* Form containers and cards */
#     [data-testid="stForm"] {
#         background-color: #F7F7F7;
#         padding: 1.5rem;
#         border-radius: 8px;
#         border: 1px solid #E0E0E0;
#     }
    
#     /* Input fields */
#     .stTextInput > div > div > input,
#     .stNumberInput > div > div > input,
#     .stSelectbox > div > div > select {
#         border: 1px solid #CCCCCC;
#         border-radius: 4px;
#         background-color: #FFFFFF;
#     }
    
#     /* Success/Info boxes */
#     .stSuccess {
#         background-color: #F0FFF4;
#         border-left: 4px solid #48BB78;
#     }
#     .stInfo {
#         background-color: #EBF8FF;
#         border-left: 4px solid #4299E1;
#     }
    
#     /* Tabs styling */
#     .stTabs [data-baseweb="tab-list"] {
#         gap: 8px;
#         background-color: #F7F7F7;
#         padding: 0.5rem;
#         border-radius: 8px;
#     }
#     .stTabs [data-baseweb="tab"] {
#         background-color: #FFFFFF;
#         border-radius: 6px;
#         color: #111111;
#         font-weight: 500;
#     }
#     .stTabs [aria-selected="true"] {
#         background-color: #B4121B;
#         color: #FFFFFF;
#     }
# </style>
# """, unsafe_allow_html=True)

# ROOT = Path(__file__).parent
# MODEL_FILE = ROOT / "real_estate_model.pkl"   # metadata dict with 'model','feature_names','target_name','encoders','scalers' (optional)
# DATA_FILE = ROOT / "india_housing_prices.csv"  # optional dataset for visuals / defaults

# # ---------- Utilities ----------
# def load_model_metadata(path=MODEL_FILE):
#     if path.exists():
#         try:
#             meta = joblib.load(path)
#             if isinstance(meta, dict) and 'model' in meta:
#                 return meta
#             else:
#                 return {'model': meta, 'feature_names': None, 'target_name': None}
#         except Exception as e:
#             st.warning(f"Failed to load model metadata: {e}")
#             return None
#     return None

# def fmt_currency(x):
#     try:
#         return f"₹{float(x):,.2f}"
#     except Exception:
#         return str(x)

# def df_median_or_default(df, col, default=0):
#     try:
#         if col in df.columns:
#             return float(df[col].median())
#     except Exception:
#         pass
#     return default

# def safe_reindex_fill(X, feature_names):
#     if feature_names is None:
#         return X.fillna(0)
#     return X.reindex(columns=feature_names, fill_value=0).fillna(0)

# def encode_categoricals(X, encoders):
#     # encoders: dict mapping column -> fitted LabelEncoder (or similar with transform)
#     if not encoders:
#         return X
#     X = X.copy()
#     for col, enc in encoders.items():
#         if col in X.columns:
#             try:
#                 X[col] = enc.transform(X[col].astype(str))
#             except Exception:
#                 # fallback: try to map known classes to codes; unknown -> -1
#                 try:
#                     mapping = {c: i for i, c in enumerate(enc.classes_)}
#                     X[col] = X[col].map(mapping).fillna(-1)
#                 except Exception:
#                     pass
#     return X

# # ---------- Load model & dataset ----------
# meta = load_model_metadata()
# model = meta['model'] if meta else None
# feature_names = meta.get('feature_names') if meta else None
# target_name = meta.get('target_name') if meta else 'Price_in_Lakhs'
# encoders = meta.get('encoders') if meta else None
# scalers = meta.get('scalers') if meta else None

# df = None
# if DATA_FILE.exists():
#     try:
#         df = pd.read_csv(DATA_FILE)
#     except Exception as e:
#         st.warning(f"Failed to load dataset for visuals/defaults: {e}")
#         df = None

# # ---------- Session state ----------
# if 'pred_history' not in st.session_state:
#     st.session_state['pred_history'] = []  # list of dicts

# # ---------- Top header ----------
# st.markdown("""
# # 🏠 AI Real Estate Valuation System
# _Data-driven property price estimates with interactive visual insights_
# """)

# tabs = st.tabs(["Predict", "History", "Market Insights"])

# # ---------- PREDICT TAB ----------
# with tabs[0]:
#     col_main, col_side = st.columns([3, 1])
#     with col_main:
#         st.markdown("### Property Details")
#         with st.form("predict_form", clear_on_submit=False):
#             # If we have training feature names, try to present the most common ones
#             # Map friendly labels to internal features where possible
#             # Common expected features used in notebook
#             # Provide min/max/default hints from dataset if available
#             def hint_range(col):
#                 if df is not None and col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
#                     mn = float(df[col].min())
#                     mx = float(df[col].max())
#                     return mn, mx
#                 return None, None

#             # Location: State & City
#             if df is not None and 'State' in df.columns:
#                 states = sorted(df['State'].dropna().unique().tolist())
#                 state = st.selectbox("State", states, index=states.index(states[0]) if states else 0, help="Select the state where the property is located")
#             else:
#                 state = st.text_input("State", "", help="Enter state name (e.g., Maharashtra)")

#             if df is not None and 'City' in df.columns:
#                 cities = sorted(df['City'].dropna().unique().tolist())
#                 city = st.selectbox("City", cities, index=0, help="Select the city where the property is located")
#             else:
#                 city = st.text_input("City", "", help="Enter city / locality")

#             # Size (sq ft)
#             mn, mx = hint_range('Size_in_SqFt')
#             default_size = int(df_median_or_default(df, 'Size_in_SqFt', 1000))
#             if mn is not None:
#                 size = st.number_input("Size (Sq.Ft)", min_value=int(max(10, mn)), max_value=int(max(1000, mx)), value=default_size, step=10, help="Total built-up area in square feet")
#                 st.caption(f"Typical range: {int(mn)} - {int(mx)} sq.ft")
#             else:
#                 size = st.number_input("Size (Sq.Ft)", min_value=100, max_value=10000, value=default_size, step=10, help="Total built-up area in square feet")

#             # BHK
#             bhk_default = int(df_median_or_default(df, 'BHK', 2))
#             bhk = st.slider("BHK (Bedrooms)", 1, 10, bhk_default, help="Number of bedrooms (e.g., 1,2,3...)")

#             # Property type
#             prop_types = df['Property_Type'].dropna().unique().tolist() if (df is not None and 'Property_Type' in df.columns) else ['Apartment', 'Independent House', 'Villa']
#             prop_type = st.selectbox("Property Type", prop_types, index=0, help="Select property type")

#             # Furnished status
#             furn_options = df['Furnished_Status'].dropna().unique().tolist() if (df is not None and 'Furnished_Status' in df.columns) else ['Unfurnished', 'Semi-Furnished', 'Fully-Furnished']
#             furnished = st.selectbox("Furnished Status", furn_options, help="Furnishing level of the property")

#             # Floor info
#             floor_default = int(df_median_or_default(df, 'Floor_No', 1))
#             total_floors_default = int(df_median_or_default(df, 'Total_Floors', 5))
#             floor_no = st.number_input("Floor Number", min_value=0, max_value=200, value=floor_default, help="Floor number where the unit is located (1 = ground/first floor)")
#             total_floors = st.number_input("Total Floors in Building", min_value=1, max_value=200, value=total_floors_default, help="Total floors in the building")

#             # Year built / Age
#             year_default = int(df_median_or_default(df, 'Year_Built', 2015))
#             year_built = st.number_input("Year Built", min_value=1900, max_value=datetime.now().year, value=year_default, help="Year the property was constructed")
#             age = datetime.now().year - year_built

#             # Parking, Security
#             parking_opts = ['No', 'Yes'] if df is None or 'Parking_Space' not in df.columns else sorted(df['Parking_Space'].dropna().unique().tolist())
#             parking = st.selectbox("Parking Space", parking_opts, index=0, help="Is parking available?")
#             security_opts = ['No', 'Yes'] if df is None or 'Security' not in df.columns else sorted(df['Security'].dropna().unique().tolist())
#             security = st.selectbox("Security", security_opts, index=0, help="Security available in the building/complex?")

#             # Nearby facilities
#             nearby_schools_default = int(df_median_or_default(df, 'Nearby_Schools', 0))
#             nearby_hospitals_default = int(df_median_or_default(df, 'Nearby_Hospitals', 0))
#             nearby_schools = st.number_input("Nearby Schools (count)", min_value=0, max_value=100, value=nearby_schools_default, help="Number of schools near the property")
#             nearby_hospitals = st.number_input("Nearby Hospitals (count)", min_value=0, max_value=100, value=nearby_hospitals_default, help="Number of hospitals/clinics nearby")

#             # Amenities multi-select (if dataset contains amenities, else show common ones)
#             amenities_list = []
#             if df is not None and 'Amenities' in df.columns:
#                 # extract distinct amenity tokens
#                 try:
#                     tokens = df['Amenities'].dropna().astype(str).str.split(',').explode().str.strip()
#                     amenities_list = sorted(tokens.unique().tolist())
#                 except Exception:
#                     amenities_list = ['Swimming Pool', 'Gym', 'Park', 'Security', 'Power Backup', 'Lift', 'Club House', 'Intercom', 'Play Area', 'Visitor Parking']
#             else:
#                 amenities_list = ['Swimming Pool', 'Gym', 'Park', 'Security', 'Power Backup', 'Lift', 'Club House', 'Intercom', 'Play Area', 'Visitor Parking', 'Shopping Center']

#             chosen_amenities = st.multiselect("Amenities (select all that apply)", amenities_list, default=[], help="Select amenities available with the property")

#             # Hidden / derived features (Price_per_SqFt, Price_per_BHK, Area_per_BHK) left for model to compute or user can fill if desired
#             st.caption("Tip: If your model expects derived features (Price_per_SqFt, Area_per_BHK), the app will compute or attempt to align features automatically.")

#             predict_button = st.form_submit_button("Get Price Estimate")

#     # Right column: presets and quick examples
#     with col_side:
#         st.markdown("### ⚡ Quick Presets")
#         st.info("Try these sample presets to see typical estimates.")
#         presets = {
#             "Luxury Apartment - Mumbai": {
#                 "State": "Maharashtra", "City": "Mumbai", "Size_in_SqFt": 1500, "BHK": 3, "Property_Type": "Apartment", "Furnished_Status": "Fully-Furnished", "Floor_No": 12, "Total_Floors": 20, "Year_Built": 2018, "Parking_Space": "Yes", "Nearby_Schools": 5, "Nearby_Hospitals": 3, "Amenities": ["Swimming Pool", "Gym", "Security"]
#             },
#             "Budget Studio - Pune": {
#                 "State": "Maharashtra", "City": "Pune", "Size_in_SqFt": 420, "BHK": 1, "Property_Type": "Apartment", "Furnished_Status": "Semi-Furnished", "Floor_No": 2, "Total_Floors": 6, "Year_Built": 2012, "Parking_Space": "No", "Nearby_Schools": 2, "Nearby_Hospitals": 1, "Amenities": ["Lift", "Power Backup"]
#             },
#             "Spacious Villa - Bangalore": {
#                 "State": "Karnataka", "City": "Bengaluru", "Size_in_SqFt": 3200, "BHK": 4, "Property_Type": "Villa", "Furnished_Status": "Semi-Furnished", "Floor_No": 1, "Total_Floors": 2, "Year_Built": 2010, "Parking_Space": "Yes", "Nearby_Schools": 4, "Nearby_Hospitals": 2, "Amenities": ["Garden", "Security", "Parking"]
#             }
#         }
#         for name, p in presets.items():
#             if st.button(name):
#                 # apply preset values to the form by setting variables in session_state and reloading
#                 st.session_state['preset_values'] = p
#                 st.experimental_rerun()

#         st.markdown("---")
#         st.markdown("### ℹ️ Notes")
#         st.write("- Use presets if unsure about numeric encodings.")
#         st.write("- If the app warns about missing encoders, export encoders from training notebook and include them in model metadata.")

#     # Apply preset values if available (populate form defaults)
#     if 'preset_values' in st.session_state and st.session_state['preset_values']:
#         pv = st.session_state['preset_values']
#         # Note: Because Streamlit forms don't support programmatic set of widget values easily without session-state bindings,
#         # we keep a simple UX: after pressing preset button, the app reloads and users can press Predict (values will be visible if session-state bound).
#         # For full programmatic population, each widget must use st.session_state keys when created.

#     # Handle prediction
#     if predict_button:
#         # Build input dict matching model features where possible
#         input_row = {
#             'State': state,
#             'City': city,
#             'Size_in_SqFt': float(size),
#             'BHK': int(bhk),
#             'Property_Type': prop_type,
#             'Furnished_Status': furnished,
#             'Floor_No': int(floor_no),
#             'Total_Floors': int(total_floors),
#             'Year_Built': int(year_built),
#             'Age_of_Property': int(age),
#             'Parking_Space': parking,
#             'Security': security,
#             'Nearby_Schools': int(nearby_schools),
#             'Nearby_Hospitals': int(nearby_hospitals),
#             'Amenities': ",".join(chosen_amenities) if chosen_amenities else ""
#         }

#         X_pred = pd.DataFrame([input_row])

#         # If model expects derived columns, compute common ones
#         if 'Price_per_SqFt' in (feature_names or []) and 'Price_in_Lakhs' not in X_pred.columns:
#             # can't compute without price; leave missing
#             pass
#         if 'Area_per_BHK' in (feature_names or []):
#             try:
#                 X_pred['Area_per_BHK'] = X_pred['Size_in_SqFt'] / X_pred['BHK']
#             except Exception:
#                 X_pred['Area_per_BHK'] = 0

#         if 'Amenity_Count' in (feature_names or []):
#             X_pred['Amenity_Count'] = X_pred['Amenities'].apply(lambda x: len([t for t in x.split(',') if t.strip()]))


#         # Apply label encoders if present
#         if encoders:
#             try:
#                 X_pred = encode_categoricals(X_pred, encoders)
#             except Exception as e:
#                 st.warning(f"Failed to apply encoders: {e}")

#         # Ensure columns order and fill missing
#         X_eval = safe_reindex_fill(X_pred, feature_names)

#         if model is None:
#             st.error("Model not found. Export 'real_estate_model.pkl' from the training notebook to the app folder.")
#         else:
#             try:
#                 pred = model.predict(X_eval)[0]
#                 # display value with currency and explicit 'Lakhs' unit
#                 st.success(f"💰 Estimated Price: {fmt_currency(pred)} Lakhs")
#                 # Optional: show modest summary
#                 st.markdown("#### Prediction Summary")
#                 st.write(f"- Location: {city}, {state}")
#                 st.write(f"- Size: {size} sq.ft | {bhk} BHK | Floor {floor_no} of {total_floors}")
#                 st.write(f"- Amenities: {', '.join(chosen_amenities) if chosen_amenities else 'None'}")

#                 # Save into history
#                 hist_entry = input_row.copy()
#                 hist_entry.update({
#                     'Predicted_Price': float(pred),
#                     'Predicted_Price_Lakhs': f"{fmt_currency(pred)} Lakhs",
#                     'Predicted_At': datetime.now().isoformat()
#                 })
#                 st.session_state['pred_history'].insert(0, hist_entry)

#                 # Show feature importance snippet (if available)
#                 if hasattr(model, "feature_importances_") and feature_names:
#                     fi = np.array(model.feature_importances_)
#                     fig = px.bar(x=feature_names, y=fi, labels={'x': 'Feature', 'y': 'Importance'},
#                                  title="Model Feature Importances",
#                                  color_discrete_sequence=['#B4121B'])
#                     fig.update_layout(plot_bgcolor='#FFFFFF', paper_bgcolor='#F7F7F7')
#                     st.plotly_chart(fig, config={}, width='stretch')
#                 else:
#                     st.info("Feature importance not available for this model type.")
#             except Exception as e:
#                 st.error(f"Prediction failed: {e}")

# # ---------- HISTORY TAB ----------
# with tabs[1]:
#     st.markdown("### 🔁 Prediction History")
#     hist = pd.DataFrame(st.session_state['pred_history'])
#     if hist.empty:
#         st.info("No predictions made yet in this session. Use the Predict tab to estimate property prices.")
#     else:
#         st.dataframe(hist, width='stretch')
#         # Download CSV
#         csv = hist.to_csv(index=False).encode('utf-8')
#         st.download_button(label="Download history (CSV)", data=csv, file_name="prediction_history.csv", mime="text/csv")
#         if st.button("Clear history"):
#             st.session_state['pred_history'] = []
#             st.success("Prediction history cleared.")
#             st.experimental_rerun()

# # ---------- MARKET INSIGHTS TAB ----------
# with tabs[2]:
#     st.markdown("### 📊 Market Insights")
#     if df is None:
#         st.info("No dataset available for market insights. Place 'india_housing_prices.csv' in the app folder to enable charts.")
#     else:
#         # Price distribution
#         if target_name in df.columns:
#             fig1 = px.histogram(df, x=target_name, nbins=50, title="Price Distribution", 
#                                labels={target_name: "Price (Lakhs)"},
#                                color_discrete_sequence=['#B4121B'])
#             fig1.update_layout(bargap=0.05, plot_bgcolor='#FFFFFF', paper_bgcolor='#F7F7F7')
#             st.plotly_chart(fig1, config={}, width='stretch')
#         else:
#             st.info(f"Target column '{target_name}' not found in dataset; price distribution unavailable.")

#         # Market trends by year if possible
#         if 'Year_Built' in df.columns and target_name in df.columns:
#             # average price by Year_Built as proxy trend (not ideal but useful)
#             trend = df.groupby('Year_Built')[target_name].mean().reset_index().sort_values('Year_Built')
#             fig2 = px.line(trend, x='Year_Built', y=target_name, title='Average Price by Year Built', 
#                           labels={'Year_Built': 'Year Built', target_name: 'Avg Price (Lakhs)'},
#                           color_discrete_sequence=['#B4121B'])
#             fig2.update_layout(plot_bgcolor='#FFFFFF', paper_bgcolor='#F7F7F7')
#             st.plotly_chart(fig2, config={}, width='stretch')
#         elif 'Listing_Date' in df.columns and target_name in df.columns:
#             try:
#                 df['_dt'] = pd.to_datetime(df['Listing_Date'], errors='coerce').dt.to_period('M').dt.to_timestamp()
#                 trend = df.groupby('_dt')[target_name].mean().reset_index()
#                 fig2 = px.line(trend, x='_dt', y=target_name, title='Average Price Over Time', 
#                               labels={'_dt': 'Date', target_name: 'Avg Price (Lakhs)'},
#                               color_discrete_sequence=['#B4121B'])
#                 fig2.update_layout(plot_bgcolor='#FFFFFF', paper_bgcolor='#F7F7F7')
#                 st.plotly_chart(fig2,config={}, width='stretch')
#             except Exception:
#                 st.info("No usable date/time column for trend analysis.")
#         else:
#             # fallback: average price by city or state
#             if 'City' in df.columns and target_name in df.columns:
#                 city_avg = df.groupby('City')[target_name].mean().sort_values(ascending=False).head(12).reset_index()
#                 fig3 = px.bar(city_avg, x='City', y=target_name, title='Top Cities by Average Price', 
#                              labels={target_name: 'Avg Price (Lakhs)'},
#                              color_discrete_sequence=['#B4121B'])
#                 fig3.update_layout(plot_bgcolor='#FFFFFF', paper_bgcolor='#F7F7F7')
#                 st.plotly_chart(fig3, config={}, width='stretch')

#         # Feature importance (model-level)
#         st.markdown("#### Model Feature Importance (if available)")
#         if model is not None and hasattr(model, "feature_importances_") and feature_names:
#             fi = np.array(model.feature_importances_)
#             fi_df = pd.DataFrame({'feature': feature_names, 'importance': fi}).sort_values('importance', ascending=True)
#             fig4 = go.Figure(go.Bar(x=fi_df['importance'], y=fi_df['feature'], orientation='h',
#                                    marker=dict(color='#B4121B')))
#             fig4.update_layout(title="Feature Importances", xaxis_title="Importance",
#                               plot_bgcolor='#FFFFFF', paper_bgcolor='#F7F7F7')
#             st.plotly_chart(fig4,config={}, width='stretch')
#         else:
#             st.info("Feature importance not available for the current model. Consider using tree-based models (RandomForest/XGBoost) or export feature_importances_ in metadata.")

# # ---------- Footer / Help ----------
# st.markdown("---")
# st.markdown("Developed for the AI-Based Real Estate Valuation System • Ensure your trained model metadata file `real_estate_model.pkl` (joblib) is present in the app folder with keys: `model`, `feature_names`, `target_name`. Export encoders/scalers under `encoders`/`scalers` to preserve preprocessing at inference.")



# Premium Enhanced Streamlit app for AI-Based Real Estate Valuation System
# Features: Premium UI, animations, better UX, advanced visualizations

import streamlit as st
from pathlib import Path
import joblib
import pandas as pd
import numpy as np
import plotly.express as px #sos
import plotly.graph_objects as go
from datetime import datetime
import io
import time

st.set_page_config(layout="wide", page_title="AI Real Estate Valuation", page_icon="🏠")

# ---------- Premium Custom Theme ----------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    }
    
    /* Header with Gradient Text */
    .main-header {
        text-align: center;
        padding: 30px 0;
        background: linear-gradient(135deg, #FFFFFF 0%, #F8F9FA 100%);
        border-radius: 20px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        margin-bottom: 40px;
    }
    
    .gradient-text {
        font-size: 3.5em;
        font-weight: 800;
        background: linear-gradient(135deg, #003366 0%, #FF6600 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0;
        animation: slideDown 0.8s ease-out;
    }
    
    .sub-header {
        color: #666;
        font-size: 1.3em;
        margin-top: 15px;
        font-weight: 500;
    }
    
    @keyframes slideDown {
        from {
            opacity: 0;
            transform: translateY(-30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateX(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes pulse {
        0%, 100% {
            transform: scale(1);
        }
        50% {
            transform: scale(1.05);
        }
    }
    
    /* Premium Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, #FF6600 0%, #FF8533 100%);
        color: #FFFFFF !important;
        border: none;
        border-radius: 16px;
        padding: 18px 48px;
        font-size: 18px;
        font-weight: 700;
        box-shadow: 0 8px 24px rgba(255, 102, 0, 0.4);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        text-transform: uppercase;
        letter-spacing: 2px;
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
        transition: left 0.6s;
    }
    
    .stButton > button:hover::before {
        left: 100%;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #FF8533 0%, #FFA366 100%);
        box-shadow: 0 12px 36px rgba(255, 102, 0, 0.6);
        transform: translateY(-4px) scale(1.02);
        color: #FFFFFF !important;
    }
    
    .stButton > button:active {
        transform: translateY(-2px) scale(0.98);
    }
    
    .stButton > button p {
        color: #FFFFFF !important;
        margin: 0;
    }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 15px;
        background: linear-gradient(135deg, #FFFFFF 0%, #F8F9FA 100%);
        padding: 20px;
        border-radius: 20px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.1);
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 14px;
        color: #003366;
        font-weight: 700;
        padding: 16px 32px;
        transition: all 0.3s ease;
        border: 3px solid transparent;
        font-size: 16px;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: linear-gradient(135deg, #FFF3E6 0%, #FFE5CC 100%);
        color: #FF6600;
        border-color: #FF6600;
        transform: translateY(-3px);
        box-shadow: 0 4px 12px rgba(255, 102, 0, 0.2);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #003366 0%, #004080 100%) !important;
        color: #FFFFFF !important;
        box-shadow: 0 6px 20px rgba(0, 51, 102, 0.4);
        border-color: #003366 !important;
    }
    
    /* Form Container */
    .stForm {
        background: linear-gradient(145deg, #FFFFFF 0%, #F8F9FA 100%);
        border-radius: 24px;
        padding: 50px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.15);
        border: 4px solid #FF6600;
        position: relative;
        overflow: hidden;
        animation: slideIn 0.6s ease-out;
    }
    
    .stForm::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,102,0,0.06) 0%, transparent 70%);
        animation: rotate 25s linear infinite;
    }
    
    @keyframes rotate {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    /* Input Fields */
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select,
    .stMultiSelect > div > div,
    .stTextInput > div > div > input {
        border: 3px solid #CCCCCC;
        border-radius: 14px;
        padding: 16px;
        font-size: 16px;
        transition: all 0.3s ease;
        background: #FFFFFF;
        font-weight: 500;
    }
    
    .stNumberInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus,
    .stTextInput > div > div > input:focus {
        border-color: #FF6600;
        box-shadow: 0 0 0 5px rgba(255, 102, 0, 0.15);
        outline: none;
        transform: scale(1.01);
    }
    
    /* Labels */
    .stNumberInput label,
    .stSelectbox label,
    .stMultiSelect label,
    .stTextInput label {
        color: #003366;
        font-weight: 700;
        font-size: 16px;
        margin-bottom: 10px;
    }
    
    /* Success Message */
    .stSuccess {
        background: linear-gradient(135deg, #E6F7F0 0%, #D1F2E8 100%);
        border-left: 8px solid #00CC66;
        border-radius: 16px;
        padding: 25px;
        box-shadow: 0 6px 20px rgba(0, 204, 102, 0.2);
        animation: slideIn 0.5s ease-out;
    }
    
    .stInfo {
        background: linear-gradient(135deg, #E6F0FF 0%, #D1E5FF 100%);
        border-left: 8px solid #003366;
        border-radius: 16px;
        padding: 25px;
        box-shadow: 0 6px 20px rgba(0, 51, 102, 0.2);
    }
    
    .stWarning {
        background: linear-gradient(135deg, #FFF3E6 0%, #FFE5CC 100%);
        border-left: 8px solid #FF6600;
        border-radius: 16px;
        padding: 25px;
        box-shadow: 0 6px 20px rgba(255, 102, 0, 0.2);
    }
    
    /* Metric Cards */
    [data-testid="stMetricValue"] {
        color: #003366;
        font-size: 40px;
        font-weight: 800;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    [data-testid="stMetricLabel"] {
        color: #666666;
        font-weight: 700;
        font-size: 15px;
        text-transform: uppercase;
        letter-spacing: 1.2px;
    }
    
    .stMetric {
        background: linear-gradient(135deg, #FFFFFF 0%, #F8F9FA 100%);
        padding: 25px;
        border-radius: 20px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.1);
        border: 3px solid #E9ECEF;
        transition: all 0.3s ease;
    }
    
    .stMetric:hover {
        transform: translateY(-6px);
        box-shadow: 0 12px 32px rgba(0,0,0,0.15);
        border-color: #FF6600;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #003366 0%, #004080 50%, #0059b3 100%);
        box-shadow: 6px 0 24px rgba(0,0,0,0.2);
    }
    
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label {
        color: #FFFFFF !important;
    }
    
    /* DataFrame */
    .dataframe {
        border: 4px solid #FF6600 !important;
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 6px 20px rgba(0,0,0,0.12);
    }
    
    .dataframe thead tr th {
        background: linear-gradient(135deg, #003366 0%, #004080 100%) !important;
        color: #FFFFFF !important;
        font-weight: 700;
        padding: 18px !important;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        font-size: 14px;
    }
    
    .dataframe tbody tr:nth-child(even) {
        background-color: #F8F9FA;
    }
    
    .dataframe tbody tr:hover {
        background: linear-gradient(90deg, #FFF3E6 0%, #FFE5CC 100%);
        transform: scale(1.01);
        box-shadow: 0 3px 10px rgba(255, 102, 0, 0.2);
    }
    
    .dataframe tbody td {
        padding: 16px !important;
        font-size: 15px;
        font-weight: 500;
    }
    
    /* Chart Container */
    .js-plotly-plot {
        border-radius: 20px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.12);
        border: 3px solid #E9ECEF;
        transition: all 0.3s ease;
    }
    
    .js-plotly-plot:hover {
        box-shadow: 0 12px 40px rgba(0,0,0,0.18);
        transform: translateY(-3px);
    }
    
    /* Download Button */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #003366 0%, #004080 100%);
        color: #FFFFFF !important;
        border: none;
        border-radius: 16px;
        padding: 16px 40px;
        font-weight: 700;
        box-shadow: 0 8px 24px rgba(0, 51, 102, 0.4);
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 1.5px;
    }
    
    .stDownloadButton > button:hover {
        background: linear-gradient(135deg, #004080 0%, #0059b3 100%);
        box-shadow: 0 12px 36px rgba(0, 51, 102, 0.5);
        transform: translateY(-4px) scale(1.02);
    }
    
    /* Preset Cards */
    .preset-card {
        background: linear-gradient(135deg, #FFFFFF 0%, #F8F9FA 100%);
        padding: 25px;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 15px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.1);
        border: 3px solid transparent;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .preset-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 12px 32px rgba(0,0,0,0.15);
        border-color: #FF6600;
    }
    
    .preset-icon {
        font-size: 3em;
        margin-bottom: 15px;
        animation: pulse 2s infinite;
    }
    
    .preset-title {
        font-weight: 700;
        font-size: 1.2em;
        color: #003366;
    }
    
    /* Section Headers */
    .section-header {
        background: linear-gradient(135deg, #003366 0%, #004080 100%);
        padding: 30px;
        border-radius: 20px;
        margin-bottom: 30px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.15);
        animation: slideIn 0.5s ease-out;
    }
    
    .section-title {
        color: white;
        margin: 0;
        font-size: 2.2em;
        font-weight: 700;
    }
    
    .section-subtitle {
        color: #E6F0FF;
        margin-top: 12px;
        font-size: 1.2em;
        font-weight: 500;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 14px;
        height: 14px;
    }
    
    ::-webkit-scrollbar-track {
        background: #F8F9FA;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #FF6600 0%, #FF8533 100%);
        border-radius: 10px;
        border: 3px solid #F8F9FA;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #FF8533 0%, #FFA366 100%);
    }
    
    /* Divider */
    hr {
        border: none;
        height: 4px;
        background: linear-gradient(90deg, transparent 0%, #FF6600 50%, transparent 100%);
        margin: 40px 0;
    }
</style>
""", unsafe_allow_html=True)

ROOT = Path(__file__).parent
MODEL_FILE = ROOT / "real_estate_model.pkl"
DATA_FILE = ROOT / "india_housing_prices.csv"

# ---------- Utilities ----------
def load_model_metadata(path=MODEL_FILE):
    if path.exists():
        try:
            meta = joblib.load(path)
            if isinstance(meta, dict) and 'model' in meta:
                return meta
            else:
                return {'model': meta, 'feature_names': None, 'target_name': None}
        except Exception as e:
            st.warning(f"Failed to load model metadata: {e}")
            return None
    return None

def fmt_currency(x):
    try:
        return f"₹{float(x):,.2f}"
    except Exception:
        return str(x)

def df_median_or_default(df, col, default=0):
    try:
        if col in df.columns:
            return float(df[col].median())
    except Exception:
        pass
    return default

# ---------- Main App ----------
def main():
    # Header
    st.markdown("""
        <div class='main-header'>
            <h1 class='gradient-text'>🏠 Real Estate Price Prediction</h1>
            <p class='sub-header'>Powered by AI • Instant Estimates • Market Insights</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Load model
    meta = load_model_metadata()
    if not meta:
        st.error("❌ Model not found. Please ensure 'real_estate_model.pkl' exists.")
        return
    
    model = meta.get('model')
    feature_names = meta.get('feature_names', [])
    
    if not model or not feature_names:
        st.error("❌ Invalid model metadata")
        return
    
    # Load dataset for defaults
    df = None
    if DATA_FILE.exists():
        try:
            df = pd.read_csv(DATA_FILE)
        except Exception:
            pass
    
    # Session state
    if 'prediction_history' not in st.session_state:
        st.session_state.prediction_history = []
    if 'preset' not in st.session_state:
        st.session_state.preset = None
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["🔮 Predict", "📊 History", "📈 Market Insights"])
    
    with tab1:
        st.markdown("""
            <div class='section-header'>
                <h2 class='section-title'>🔮 Property Price Estimator</h2>
                <p class='section-subtitle'>Get instant AI-powered price estimates for properties across India</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Presets
        st.markdown("<h3 style='color: #003366; margin: 40px 0 25px 0;'>⚡ Quick Presets</h3>", unsafe_allow_html=True)
        st.markdown("<p style='color: #666; margin-bottom: 25px;'>Start with pre-configured property templates</p>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        presets = {
            'luxury': {'icon': '🏰', 'title': 'Luxury Property', 'color': 'linear-gradient(135deg, #FFD700 0%, #FFA500 100%)', 'values': {'Area': 3500, 'BHK': 5, 'Bedroom': 4, 'Bathroom': 4}},
            'budget': {'icon': '💰', 'title': 'Budget Friendly', 'color': 'linear-gradient(135deg, #90EE90 0%, #32CD32 100%)', 'values': {'Area': 800, 'BHK': 2, 'Bedroom': 2, 'Bathroom': 1}},
            'villa': {'icon': '🏡', 'title': 'Spacious Villa', 'color': 'linear-gradient(135deg, #87CEEB 0%, #4682B4 100%)', 'values': {'Area': 2500, 'BHK': 4, 'Bedroom': 4, 'Bathroom': 3}}
        }
        
        for col, (preset_key, preset_data) in zip([col1, col2, col3], presets.items()):
            with col:
                st.markdown(f"""
                    <div class='preset-card' style='background: {preset_data['color']};'>
                        <div class='preset-icon'>{preset_data['icon']}</div>
                        <div class='preset-title'>{preset_data['title']}</div>
                    </div>
                """, unsafe_allow_html=True)
                if st.button(f"Select {preset_data['title']}", width='stretch', key=f"{preset_key}_btn"):
                    st.session_state['preset'] = preset_key
                    st.rerun()
        
        st.markdown("<hr>", unsafe_allow_html=True)
        
        # Form
        with st.form("prediction_form"):
            st.markdown("<h3 style='color: #003366; margin-bottom: 25px;'>📝 Property Details</h3>", unsafe_allow_html=True)
            
            # Get defaults
            preset = st.session_state.get('preset')
            preset_vals = presets.get(preset, {}).get('values', {}) if preset else {}
            
            col1, col2 = st.columns(2)
            
            with col1:
                city_options = df['City'].unique().tolist() if df is not None and 'City' in df.columns else ['Mumbai', 'Delhi', 'Bangalore']
                city = st.selectbox("🏙️ City", options=city_options, key="city_input")
                
                area = st.number_input(
                    "📐 Area (sqft)", 
                    min_value=100, 
                    max_value=50000, 
                    value=preset_vals.get('Area', int(df_median_or_default(df, 'Area', 1000))),
                    step=100
                )
                
                bhk = st.number_input(
                    "🏘️ BHK", 
                    min_value=1, 
                    max_value=10, 
                    value=preset_vals.get('BHK', int(df_median_or_default(df, 'BHK', 2))),
                    step=1
                )
            
            with col2:
                bedrooms = st.number_input(
                    "🛏️ Bedrooms", 
                    min_value=1, 
                    max_value=20, 
                    value=preset_vals.get('Bedroom', int(df_median_or_default(df, 'Bedroom', 2))),
                    step=1
                )
                
                bathrooms = st.number_input(
                    "🚿 Bathrooms", 
                    min_value=1, 
                    max_value=10, 
                    value=preset_vals.get('Bathroom', int(df_median_or_default(df, 'Bathroom', 2))),
                    step=1
                )
                
                balconies = st.number_input(
                    "🌅 Balconies", 
                    min_value=0, 
                    max_value=10, 
                    value=int(df_median_or_default(df, 'Balcony', 1)),
                    step=1
                )
            
            # Amenities
            st.markdown("<h4 style='color: #003366; margin: 30px 0 15px 0;'>✨ Amenities</h4>", unsafe_allow_html=True)
            amenity_options = ['Parking', 'Gym', 'Swimming Pool', 'Garden', 'Security', 'Power Backup']
            selected_amenities = st.multiselect("Select amenities", options=amenity_options, default=[])
            
            st.markdown("<br>", unsafe_allow_html=True)
            prediction_button = st.form_submit_button("🔍 Get Price Estimate", width='stretch')
            
            if prediction_button:
                with st.spinner("🔄 Analyzing property data with AI..."):
                    time.sleep(0.8)
                    
                    # Prepare input
                    input_data = {
                        'City': city,
                        'Area': area,
                        'BHK': bhk,
                        'Bedroom': bedrooms,
                        'Bathroom': bathrooms,
                        'Balcony': balconies,
                        'Parking': 1 if 'Parking' in selected_amenities else 0,
                        'Gym': 1 if 'Gym' in selected_amenities else 0,
                        'SwimmingPool': 1 if 'Swimming Pool' in selected_amenities else 0,
                        'Garden': 1 if 'Garden' in selected_amenities else 0,
                        'Security': 1 if 'Security' in selected_amenities else 0,
                        'PowerBackup': 1 if 'Power Backup' in selected_amenities else 0
                    }
                    
                    # Add missing features with defaults
                    for feat in feature_names:
                        if feat not in input_data:
                            input_data[feat] = 0
                    
                    X_input = pd.DataFrame([input_data])[feature_names]
                    pred = model.predict(X_input)[0]
                    
                    # Display result
                    st.markdown(f"""
                        <div style='background: linear-gradient(135deg, #E6F7F0 0%, #D1F2E8 100%);
                                    padding: 40px; border-radius: 20px; border-left: 8px solid #00CC66;
                                    box-shadow: 0 8px 32px rgba(0, 204, 102, 0.25); margin: 30px 0;
                                    animation: slideIn 0.6s ease-out;'>
                            <div style='text-align: center;'>
                                <div style='font-size: 1.3em; color: #00CC66; font-weight: 700; margin-bottom: 15px; text-transform: uppercase; letter-spacing: 2px;'>
                                    ✅ ESTIMATED PROPERTY VALUE
                                </div>
                                <div style='font-size: 4em; color: #003366; font-weight: 800; margin: 20px 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.1);'>
                                    {fmt_currency(pred)} <span style='font-size: 0.6em;'>Lakhs</span>
                                </div>
                                <div style='color: #666; font-size: 1.1em; margin-top: 15px; font-weight: 500;'>
                                    🤖 AI-Powered Prediction • ⚡ Instant Results • 📊 Data-Driven
                                </div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Store history
                    history_entry = {
                        'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'City': city,
                        'Area_sqft': area,
                        'BHK': bhk,
                        'Bedrooms': bedrooms,
                        'Bathrooms': bathrooms,
                        'Predicted_Price_Lakhs': f"{fmt_currency(pred)} Lakhs"
                    }
                    st.session_state.prediction_history.append(history_entry)
    
    with tab2:
        st.markdown("""
            <div class='section-header'>
                <h2 class='section-title'>📊 Prediction History</h2>
                <p class='section-subtitle'>Track all your property valuations in one place</p>
            </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.prediction_history:
            df_history = pd.DataFrame(st.session_state.prediction_history)
            st.dataframe(df_history, width='stretch')
            
            col1, col2 = st.columns(2)
            with col1:
                csv = df_history.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download History (CSV)",
                    data=csv,
                    file_name=f"prediction_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    width='stretch'
                )
            with col2:
                if st.button("🗑️ Clear History", width='stretch'):
                    st.session_state.prediction_history = []
                    st.rerun()
        else:
            st.info("📝 No predictions yet. Start by making a prediction in the Predict tab!")
    
    with tab3:
        st.markdown("""
            <div class='section-header'>
                <h2 class='section-title'>📈 Market Insights</h2>
                <p class='section-subtitle'>Explore comprehensive real estate market analytics and trends</p>
            </div>
        """, unsafe_allow_html=True)
        
        if df is not None:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("📊 Total Properties", f"{len(df):,}", delta="Live Data")
            with col2:
                avg_price = df['Price_in_Lakhs'].mean() if 'Price_in_Lakhs' in df.columns else 0
                st.metric("💰 Avg Price", f"{fmt_currency(avg_price)} L", delta="+5.2%")
            with col3:
                cities = df['City'].nunique() if 'City' in df.columns else 0
                st.metric("🏙️ Cities Covered", f"{cities}", delta="Growing")
            
            st.markdown("<hr>", unsafe_allow_html=True)
            
            # Charts
            if 'Price_in_Lakhs' in df.columns:
                fig = px.histogram(
                    df, 
                    x='Price_in_Lakhs', 
                    nbins=50,
                    title='📊 Price Distribution',
                    color_discrete_sequence=['#FF6600']
                )
                fig.update_layout(
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    font=dict(family='Inter, sans-serif', size=14),
                    title_font=dict(size=20, color='#003366', family='Inter, sans-serif', weight='bold')
                )
                st.plotly_chart(fig, config={} ,width='stretch')
            
            if 'City' in df.columns and 'Price_in_Lakhs' in df.columns:
                city_avg = df.groupby('City')['Price_in_Lakhs'].mean().sort_values(ascending=False).head(10)
                fig = px.bar(
                    x=city_avg.index,
                    y=city_avg.values,
                    title='🏙️ Average Price by Top 10 Cities',
                    labels={'x': 'City', 'y': 'Average Price (Lakhs)'},
                    color=city_avg.values,
                    color_continuous_scale=[[0, '#003366'], [1, '#FF6600']]
                )
                fig.update_layout(
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    font=dict(family='Inter, sans-serif', size=14),
                    title_font=dict(size=20, color='#003366', family='Inter, sans-serif', weight='bold'),
                    showlegend=False
                )
                st.plotly_chart(fig, config={}, width='stretch')
        else:
            st.info("📊 No market data available. Load 'india_housing_prices.csv' for insights.")

if __name__ == "__main__":
    main()


