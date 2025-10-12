import streamlit as st
import time
import datetime
from pathlib import Path

# Configure page
st.set_page_config(
    page_title="CHUBB Claims Intelligence",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium UI styling
st.markdown("""
<style>
    /* Global theme */
    .stApp {
        background: linear-gradient(180deg, #0a0e27 0%, #1a1f3a 100%);
    }
    
    /* Header styling */
    .premium-header {
        background: linear-gradient(90deg, rgba(26,31,58,0.9) 0%, rgba(15,23,41,0.9) 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        border: 1px solid rgba(255,255,255,0.1);
        margin-bottom: 2rem;
        backdrop-filter: blur(10px);
    }
    
    /* Cards */
    .premium-card {
        background: linear-gradient(145deg, rgba(26,31,58,0.9) 0%, rgba(15,23,41,0.9) 100%);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 1rem;
        padding: 1.5rem;
        margin-bottom: 1rem;
        backdrop-filter: blur(10px);
    }
    
    /* Status indicators */
    .status-active {
        background: rgba(16, 185, 129, 0.1);
        border: 1px solid rgba(16, 185, 129, 0.3);
        color: #10B981;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.875rem;
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Input fields */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input {
        background-color: rgba(30, 41, 59, 0.5) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        color: white !important;
        padding: 0.75rem !important;
        border-radius: 0.5rem !important;
    }
    
    /* Select boxes */
    .stSelectbox > div > div {
        background-color: rgba(30, 41, 59, 0.5) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        color: white !important;
        padding: 0.25rem !important;
        border-radius: 0.5rem !important;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(90deg, #2563EB 0%, #1D4ED8 100%) !important;
        color: white !important;
        border: none !important;
        padding: 0.75rem 1.5rem !important;
        border-radius: 0.5rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(90deg, #1D4ED8 0%, #1E40AF 100%) !important;
        box-shadow: 0 4px 12px rgba(37,99,235,0.2) !important;
        transform: translateY(-1px) !important;
    }
    
    /* Progress bars */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #2563EB, #1D4ED8) !important;
    }
    
    /* Metrics */
    .css-1wivf9n {
        background: linear-gradient(145deg, rgba(26,31,58,0.9) 0%, rgba(15,23,41,0.9) 100%) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        padding: 1rem !important;
        border-radius: 0.75rem !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'processing' not in st.session_state:
    st.session_state.processing = False
    st.session_state.analysis_complete = False
    st.session_state.progress = 0
    st.session_state.stage = "Initializing"

# Premium Header
st.markdown("""
<div class='premium-header'>
    <div style='display: flex; align-items: center; justify-content: space-between;'>
        <div style='display: flex; align-items: center; gap: 1rem;'>
            <div style='background: linear-gradient(135deg, #E31837 0%, #C41230 100%); width: 3rem; height: 3rem; border-radius: 0.75rem; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 1.5rem;'>
                C
            </div>
            <div>
                <h1 style='margin: 0; font-size: 1.5rem; font-weight: 700;'>CHUBB</h1>
                <p style='margin: 0; font-size: 0.875rem; color: #94A3B8;'>Claims Intelligence Platform</p>
            </div>
        </div>
        <div class='status-active'>
            <span style='width: 0.5rem; height: 0.5rem; background: #10B981; border-radius: 50%; display: inline-block;'></span>
            AI System Active
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
    st.subheader("📋 Claim Information")
    
    claim_amount = st.number_input("Claim Amount ($)", 
                                 min_value=0, 
                                 value=5000, 
                                 step=100,
                                 help="Enter the total claim amount")
    
    claim_type = st.selectbox("Claim Type",
                            ["Collision", "Theft", "Natural Disaster", "Fire", "Vandalism"],
                            help="Select the type of claim")
    
    col_a, col_b = st.columns(2)
    with col_a:
        incident_date = st.date_input("Incident Date",
                                    datetime.datetime.now())
    with col_b:
        police_report = st.checkbox("Police Report Filed",
                                  help="Check if a police report was filed")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Image Upload Section
    st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
    st.subheader("📸 Damage Documentation")
    
    uploaded_files = st.file_uploader("Upload Images", 
                                    accept_multiple_files=True,
                                    type=['png', 'jpg', 'jpeg'])
    
    if uploaded_files:
        cols = st.columns(3)
        for idx, file in enumerate(uploaded_files):
            with cols[idx % 3]:
                st.image(file, caption=f"Image {idx + 1}")
    
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
    st.subheader("🔍 Analysis Controls")
    
    if not st.session_state.processing and not st.session_state.analysis_complete:
        if st.button("Begin Analysis", use_container_width=True):
            st.session_state.processing = True
            st.session_state.progress = 0
    
    if st.session_state.processing:
        st.markdown("""
            <div style='text-align: center; margin-bottom: 1rem;'>
                <div style='font-size: 1.25rem; font-weight: 600; margin-bottom: 0.5rem;'>Processing Claim</div>
                <div style='color: #94A3B8; font-size: 0.875rem;'>AI models analyzing data...</div>
            </div>
        """, unsafe_allow_html=True)
        
        progress_bar = st.progress(0)
        
        # Simulate processing
        for i in range(100):
            time.sleep(0.05)
            st.session_state.progress = i + 1
            progress_bar.progress(st.session_state.progress)
            
            if i < 20:
                st.session_state.stage = "Initializing AI Models..."
            elif i < 40:
                st.session_state.stage = "Analyzing Images..."
            elif i < 60:
                st.session_state.stage = "Detecting Fraud Patterns..."
            elif i < 80:
                st.session_state.stage = "Calculating Risk Score..."
            else:
                st.session_state.stage = "Finalizing Report..."
            
            status_placeholder = st.empty()
            status_placeholder.markdown(f"<div style='text-align: center; color: #94A3B8;'>{st.session_state.stage}</div>", unsafe_allow_html=True)
            
            if i == 99:
                st.session_state.processing = False
                st.session_state.analysis_complete = True
                st.experimental_rerun()
    
    if st.session_state.analysis_complete:
        st.markdown("<div style='text-align: center; margin-bottom: 2rem;'>", unsafe_allow_html=True)
        
        # Risk Score
        risk_score = 35  # Example score
        risk_level = "Low" if risk_score < 40 else "Medium" if risk_score < 70 else "High"
        risk_color = "#10B981" if risk_score < 40 else "#F59E0B" if risk_score < 70 else "#EF4444"
        
        st.markdown(f"""
            <div style='background: rgba(0,0,0,0.2); padding: 1.5rem; border-radius: 1rem; margin-bottom: 1rem;'>
                <div style='font-size: 0.875rem; color: #94A3B8; margin-bottom: 0.5rem;'>Risk Score</div>
                <div style='font-size: 2rem; font-weight: 700; color: {risk_color};'>{risk_score}%</div>
                <div style='font-size: 0.875rem; color: {risk_color};'>{risk_level} Risk</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Metrics
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.metric("Fraud Probability", "15%", "-5%")
        with col_m2:
            st.metric("Damage Severity", "Medium", "Verified")
        
        # Recommendation
        st.markdown(f"""
            <div style='background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); 
                        padding: 1rem; border-radius: 0.75rem; margin-top: 1rem;'>
                <div style='font-weight: 600; color: #10B981; margin-bottom: 0.5rem;'>Recommendation</div>
                <div style='color: white;'>Proceed with claim processing</div>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("New Analysis", use_container_width=True):
            st.session_state.analysis_complete = False
            st.experimental_rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # System Status Card
    st.markdown("""
        <div class='premium-card'>
            <h3 style='font-size: 1rem; font-weight: 600; margin-bottom: 1rem;'>System Status</h3>
            <div style='display: flex; justify-content: space-between; margin-bottom: 0.5rem;'>
                <span style='color: #94A3B8;'>AI Models</span>
                <span style='color: #10B981;'>Online</span>
            </div>
            <div style='display: flex; justify-content: space-between; margin-bottom: 0.5rem;'>
                <span style='color: #94A3B8;'>Analysis Engine</span>
                <span style='color: #10B981;'>Active</span>
            </div>
            <div style='display: flex; justify-content: space-between;'>
                <span style='color: #94A3B8;'>Database</span>
                <span style='color: #10B981;'>Connected</span>
            </div>
        </div>
    """, unsafe_allow_html=True)