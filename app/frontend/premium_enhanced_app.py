import streamlit as st
import time
import datetime
from pathlib import Path
import sys
import cv2
from PIL import Image
import numpy as np

# Add the parent directory to system path
sys.path.append(str(Path(__file__).parent.parent))

from core.fraud_detector import FraudDetector
from core.damage_detector import DamageDetector

class PremiumInsuranceApp:
    def __init__(self):
        self.fraud_detector = FraudDetector()
        self.damage_detector = DamageDetector()
        self.setup_page()
        
    def setup_page(self):
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
            st.session_state.results = None
        
    def show_header(self):
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
        
    def analyze_claim(self, claim_data, uploaded_files):
        """Process claim and damage analysis"""
        fraud_result = self.fraud_detector.detect_fraud(claim_data)
        
        damage_results = []
        if uploaded_files:
            for file in uploaded_files:
                image = Image.open(file)
                damage_result = self.damage_detector.detect_damage(image)
                damage_results.append(damage_result)
        
        total_damage_cost = sum(result['estimated_cost'] for result in damage_results) if damage_results else 0
        
        # Calculate risk score (0-100)
        fraud_weight = 0.6
        damage_weight = 0.4
        
        fraud_score = fraud_result['fraud_probability'] * 100
        damage_score = (sum(result['total_severity'] * 100 for result in damage_results) / len(damage_results)) if damage_results else 0
        
        risk_score = int((fraud_score * fraud_weight) + (damage_score * damage_weight))
        
        return {
            'risk_score': risk_score,
            'fraud_result': fraud_result,
            'damage_results': damage_results,
            'total_damage_cost': total_damage_cost
        }
    
    def run(self):
        self.show_header()
        
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
            
            vehicle_price = st.number_input("Vehicle Price ($)",
                                          min_value=0,
                                          value=20000,
                                          step=1000,
                                          help="Enter the vehicle's market value")
            
            col_a, col_b = st.columns(2)
            with col_a:
                vehicle_age = st.number_input("Vehicle Age (years)",
                                            min_value=0,
                                            value=3,
                                            help="Enter the vehicle's age")
                
                policy_duration = st.number_input("Policy Duration (days)",
                                                min_value=0,
                                                value=365,
                                                help="Enter how long the policy has been active")
            
            with col_b:
                previous_claims = st.number_input("Previous Claims",
                                                min_value=0,
                                                value=0,
                                                help="Number of previous claims filed")
                
                time_to_report = st.number_input("Time to Report (days)",
                                               min_value=0,
                                               value=1,
                                               help="Days between incident and reporting")
            
            required_docs = st.multiselect(
                "Required Documents",
                ["Police Report", "Medical Report", "Witness Statement", "Photos"],
                default=["Police Report", "Photos"],
                help="Select all documents that have been provided"
            )
            
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
                
                # Actual processing
                claim_data = {
                    'ClaimAmount': claim_amount,
                    'VehiclePrice': vehicle_price,
                    'VehicleAge': vehicle_age,
                    'PolicyDuration': policy_duration,
                    'previous_claims_count': previous_claims,
                    'time_to_report': time_to_report,
                    'claim_time': datetime.datetime.now().strftime('%Y-%m-%d'),
                    'required_documents': {doc: doc in required_docs for doc in ["Police Report", "Medical Report", "Witness Statement", "Photos"]}
                }
                
                for i in range(100):
                    if i == 25:  # Start processing at 25%
                        st.session_state.results = self.analyze_claim(claim_data, uploaded_files)
                    
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
            
            if st.session_state.analysis_complete and st.session_state.results:
                results = st.session_state.results
                st.markdown("<div style='text-align: center; margin-bottom: 2rem;'>", unsafe_allow_html=True)
                
                # Risk Score
                risk_score = results['risk_score']
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
                    fraud_prob = results['fraud_result']['fraud_probability'] * 100
                    st.metric("Fraud Probability", f"{fraud_prob:.1f}%")
                with col_m2:
                    if results['damage_results']:
                        severity = "High" if risk_score > 70 else "Medium" if risk_score > 40 else "Low"
                        st.metric("Damage Severity", severity)
                
                # Detailed Analysis
                st.markdown("""
                    <div style='margin-top: 1.5rem;'>
                        <div style='font-weight: 600; margin-bottom: 0.5rem;'>Analysis Summary</div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Show fraud findings
                for finding in results['fraud_result']['analysis']['findings']:
                    st.markdown(f"- {finding}")
                
                # Show damage analysis if available
                if results['damage_results']:
                    st.markdown("### Damage Assessment")
                    total_cost = results['total_damage_cost']
                    st.markdown(f"Estimated Repair Cost: ${total_cost:,.2f}")
                    
                    for idx, damage_result in enumerate(results['damage_results']):
                        st.markdown(f"**Image {idx + 1}**")
                        for damage in damage_result['damages']:
                            st.markdown(f"- {damage['type'].title()}: {damage['confidence']:.1%} confidence")
                
                # Recommendation
                recommendation_color = "rgba(16, 185, 129, 0.1)" if risk_score < 40 else "rgba(245, 158, 11, 0.1)" if risk_score < 70 else "rgba(239, 68, 68, 0.1)"
                recommendation_border = "rgba(16, 185, 129, 0.3)" if risk_score < 40 else "rgba(245, 158, 11, 0.3)" if risk_score < 70 else "rgba(239, 68, 68, 0.3)"
                recommendation_text = "#10B981" if risk_score < 40 else "#F59E0B" if risk_score < 70 else "#EF4444"
                
                recommendation = "Proceed with claim processing" if risk_score < 40 else "Review required - escalate to senior adjuster" if risk_score < 70 else "High risk - detailed investigation required"
                
                st.markdown(f"""
                    <div style='background: {recommendation_color}; border: 1px solid {recommendation_border}; 
                                padding: 1rem; border-radius: 0.75rem; margin-top: 1rem;'>
                        <div style='font-weight: 600; color: {recommendation_text}; margin-bottom: 0.5rem;'>Recommendation</div>
                        <div style='color: white;'>{recommendation}</div>
                    </div>
                """, unsafe_allow_html=True)
                
                if st.button("New Analysis", use_container_width=True):
                    st.session_state.analysis_complete = False
                    st.session_state.results = None
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

if __name__ == "__main__":
    app = PremiumInsuranceApp()
    app.run()