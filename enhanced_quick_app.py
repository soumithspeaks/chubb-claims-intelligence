import streamlit as st
import sys
from pathlib import Path
import joblib
import os
from PIL import Image
import numpy as np
from datetime import datetime

# Add the project root to the path
sys.path.append(str(Path(__file__).parent))

# Page config
st.set_page_config(
    page_title="Chubb Insurance Claim Analyzer Pro",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom styling
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #004B87;
        color: white;
    }
    .risk-high {
        color: #ff4b4b;
        padding: 0.5rem;
        border-radius: 0.3rem;
        background: rgba(255, 75, 75, 0.1);
    }
    .risk-medium {
        color: #ffa600;
        padding: 0.5rem;
        border-radius: 0.3rem;
        background: rgba(255, 166, 0, 0.1);
    }
    .risk-low {
        color: #00cc00;
        padding: 0.5rem;
        border-radius: 0.3rem;
        background: rgba(0, 204, 0, 0.1);
    }
    </style>
""", unsafe_allow_html=True)

def load_models():
    """Load the ML models"""
    try:
        model_path = Path(__file__).parent.parent / 'models' / 'fraud_detector'
        fraud_model = joblib.load(model_path / 'model.joblib')
        scaler = joblib.load(model_path / 'scaler.joblib')
        threshold = joblib.load(model_path / 'optimal_threshold.joblib')
        return fraud_model, scaler, threshold
    except Exception as e:
        st.error(f"Error loading models: {str(e)}")
        return None, None, None

def analyze_claim(data, images=None):
    """Analyze the claim data"""
    fraud_model, scaler, threshold = load_models()
    
    if fraud_model is None:
        return {
            'risk_level': 'unknown',
            'fraud_probability': 0.5,
            'risk_factors': {
                'temporal_risk': 0.5,
                'financial_risk': 0.5,
                'behavioral_risk': 0.5
            }
        }
    
    # Mock analysis - replace with actual model inference
    risk_score = 0.3  # Example score
    
    return {
        'risk_level': 'low' if risk_score < 0.4 else 'moderate' if risk_score < 0.7 else 'high',
        'fraud_probability': risk_score,
        'risk_factors': {
            'temporal_risk': 0.3,
            'financial_risk': 0.4,
            'behavioral_risk': 0.2
        }
    }

def main():
    # Title
    st.title("🔍 Insurance Claim Analyzer Pro")
    
    # Two-column layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### Claim Details")
        
        # Core claim information
        incident_date = st.date_input("Incident Date", datetime.now())
        claim_amount = st.number_input("Claim Amount ($)", min_value=0, value=1000)
        
        # Detailed information
        col_a, col_b = st.columns(2)
        with col_a:
            claim_type = st.selectbox("Claim Type", [
                "Collision",
                "Theft",
                "Natural Disaster",
                "Vandalism",
                "Fire Damage"
            ])
            vehicle_make = st.selectbox("Vehicle Make", [
                "Toyota",
                "Honda",
                "Ford",
                "BMW",
                "Mercedes",
                "Other"
            ])
            police_report = st.checkbox("Police Report Filed")
        
        with col_b:
            location_type = st.selectbox("Location Type", [
                "Urban",
                "Suburban",
                "Rural",
                "Highway",
                "Parking"
            ])
            severity = st.select_slider("Incident Severity", 
                options=["Minor", "Moderate", "Severe", "Critical"])
            witnesses = st.checkbox("Witnesses Present")
        
        # Image upload
        st.markdown("### Damage Documentation")
        uploaded_files = st.file_uploader("Upload images of the damage", 
                                        accept_multiple_files=True,
                                        type=['png', 'jpg', 'jpeg'])
        
        if uploaded_files:
            st.image(uploaded_files)
    
    with col2:
        st.markdown("### Risk Analysis")
        
        if st.button("Analyze Claim", type="primary"):
            with st.spinner("Analyzing claim..."):
                # Prepare claim data
                claim_data = {
                    'incident_date': incident_date,
                    'claim_amount': claim_amount,
                    'claim_type': claim_type,
                    'vehicle_make': vehicle_make,
                    'police_report': police_report,
                    'location_type': location_type,
                    'severity': severity,
                    'witnesses': witnesses
                }
                
                # Get analysis results
                results = analyze_claim(claim_data, uploaded_files)
                
                # Display results
                risk_level = results['risk_level']
                risk_class = f"risk-{risk_level}"
                
                st.markdown(f"""
                    <div class="{risk_class}">
                        <h3>Risk Level: {risk_level.upper()}</h3>
                        <p>Fraud Probability: {results['fraud_probability']:.1%}</p>
                    </div>
                """, unsafe_allow_html=True)
                
                # Risk factors
                st.markdown("#### Risk Factors")
                risk_factors = results['risk_factors']
                
                st.progress(risk_factors['temporal_risk'])
                st.caption(f"Temporal Risk: {risk_factors['temporal_risk']:.1%}")
                
                st.progress(risk_factors['financial_risk'])
                st.caption(f"Financial Risk: {risk_factors['financial_risk']:.1%}")
                
                st.progress(risk_factors['behavioral_risk'])
                st.caption(f"Behavioral Risk: {risk_factors['behavioral_risk']:.1%}")
                
                # Recommendations
                st.markdown("#### Recommendations")
                if risk_level == 'high':
                    st.error("⚠️ Further investigation recommended")
                    st.markdown("- Request additional documentation\n- Schedule adjuster inspection\n- Verify police report details")
                elif risk_level == 'moderate':
                    st.warning("⚠️ Additional verification suggested")
                    st.markdown("- Review documentation completeness\n- Verify incident details")
                else:
                    st.success("✅ Claim appears regular")
                    st.markdown("- Process claim normally\n- Standard documentation sufficient")

if __name__ == "__main__":
    main()