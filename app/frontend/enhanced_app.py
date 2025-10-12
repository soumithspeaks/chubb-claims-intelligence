import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
import sys
import os
from pathlib import Path

# Add the parent directory to system path
sys.path.append(str(Path(__file__).parent.parent))

from core.fraud_detector import FraudDetector
from core.damage_detector import DamageDetector

class InsuranceClaimApp:
    def __init__(self):
        self.fraud_detector = FraudDetector()
        self.damage_detector = DamageDetector()
        self.setup_page()
        
    def setup_page(self):
        st.set_page_config(
            page_title="Smart Insurance Claims Analyzer",
            page_icon="🔍",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        st.title("Smart Insurance Claims Analyzer")
        st.sidebar.title("Navigation")
        self.page = st.sidebar.radio(
            "Choose a page",
            ["Home", "Claim Analysis", "Damage Assessment", "Analytics Dashboard"]
        )
        
    def run(self):
        if self.page == "Home":
            self.show_home()
        elif self.page == "Claim Analysis":
            self.show_claim_analysis()
        elif self.page == "Damage Assessment":
            self.show_damage_assessment()
        elif self.page == "Analytics Dashboard":
            self.show_analytics()
            
    def show_home(self):
        st.header("Welcome to Smart Insurance Claims Analyzer")
        st.write("""
        This advanced system helps insurance companies detect fraudulent claims and assess vehicle damage using state-of-the-art AI technology.
        
        ### Key Features:
        - 🕵️‍♂️ Advanced Fraud Detection
        - 🚗 Automated Damage Assessment
        - 📊 Real-time Analytics
        - 💡 Smart Recommendations
        
        ### Getting Started
        1. Navigate to 'Claim Analysis' to analyze a new claim
        2. Use 'Damage Assessment' to analyze vehicle damage photos
        3. View trends and insights in the 'Analytics Dashboard'
        """)
        
    def show_claim_analysis(self):
        st.header("Claim Analysis")
        
        with st.form("claim_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                claim_amount = st.number_input("Claim Amount ($)", min_value=0.0)
                vehicle_price = st.number_input("Vehicle Price ($)", min_value=0.0)
                vehicle_age = st.number_input("Vehicle Age (years)", min_value=0)
                policy_duration = st.number_input("Policy Duration (days)", min_value=0)
                
            with col2:
                previous_claims = st.number_input("Previous Claims Count", min_value=0)
                time_to_report = st.number_input("Time to Report (days)", min_value=0)
                claim_time = st.date_input("Claim Date")
                required_docs = st.multiselect(
                    "Required Documents",
                    ["Police Report", "Medical Report", "Witness Statement", "Photos"],
                    default=[]
                )
            
            submit = st.form_submit_button("Analyze Claim")
            
            if submit:
                claim_data = {
                    'ClaimAmount': claim_amount,
                    'VehiclePrice': vehicle_price,
                    'VehicleAge': vehicle_age,
                    'PolicyDuration': policy_duration,
                    'previous_claims_count': previous_claims,
                    'time_to_report': time_to_report,
                    'claim_time': claim_time.strftime('%Y-%m-%d'),
                    'required_documents': {doc: doc in required_docs for doc in ["Police Report", "Medical Report", "Witness Statement", "Photos"]}
                }
                
                result = self.fraud_detector.detect_fraud(claim_data)
                
                self.display_fraud_analysis(result)
                
    def display_fraud_analysis(self, result):
        risk_level = result['risk_level'].upper()
        color = {
            'LOW': 'green',
            'MODERATE': 'yellow',
            'HIGH': 'orange',
            'CRITICAL': 'red'
        }[risk_level]
        
        st.markdown(f"### Risk Level: :{color}[{risk_level}]")
        st.markdown(f"**Fraud Probability**: {result['fraud_probability']:.2%}")
        
        # Display analysis
        st.subheader("Analysis")
        st.write(result['analysis']['summary'])
        
        # Display findings and recommendations in columns
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Key Findings")
            for finding in result['analysis']['findings']:
                st.write(f"• {finding}")
                
        with col2:
            st.subheader("Recommendations")
            for rec in result['analysis']['recommendations']:
                st.write(f"• {rec}")
                
        # Display risk factors
        st.subheader("Risk Factors")
        risk_data = pd.DataFrame({
            'Category': list(result['risk_factors'].keys()),
            'Risk Score': list(result['risk_factors'].values())
        })
        st.bar_chart(risk_data.set_index('Category'))
        
    def show_damage_assessment(self):
        st.header("Vehicle Damage Assessment")
        
        uploaded_file = st.file_uploader("Upload vehicle image", type=['png', 'jpg', 'jpeg'])
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_column_width=True)
            
            if st.button("Analyze Damage"):
                with st.spinner("Analyzing damage..."):
                    damage_result = self.damage_detector.detect_damage(image)
                    
                    if damage_result['damages_detected']:
                        st.success("Damage Analysis Complete")
                        
                        # Display detected damages
                        st.subheader("Detected Damages")
                        for damage in damage_result['damages']:
                            st.write(f"• {damage['type']}: {damage['confidence']:.1%} confidence")
                            
                        # Display cost estimate
                        st.subheader("Cost Estimate")
                        st.write(f"Estimated repair cost: ${damage_result['estimated_cost']:,.2f}")
                        
                        # Display annotated image
                        st.image(damage_result['annotated_image'], caption="Analyzed Image", use_column_width=True)
                    else:
                        st.info("No significant damage detected")
                        
    def show_analytics(self):
        st.header("Analytics Dashboard")
        
        # Placeholder data - in a real app, this would come from a database
        data = {
            'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            'Claims': [120, 150, 130, 140, 160, 180],
            'Fraudulent': [12, 15, 13, 14, 16, 18],
            'Amount': [250000, 300000, 280000, 290000, 310000, 350000]
        }
        df = pd.DataFrame(data)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Claims Trend")
            st.line_chart(df.set_index('Month')['Claims'])
            
        with col2:
            st.subheader("Fraud Rate")
            fraud_rate = (df['Fraudulent'] / df['Claims'] * 100).round(1)
            st.line_chart(pd.DataFrame({'Fraud %': fraud_rate}).set_index(df['Month']))
            
        st.subheader("Total Claims Amount")
        st.bar_chart(df.set_index('Month')['Amount'])
        
        # Add some key metrics
        st.subheader("Key Metrics")
        metric1, metric2, metric3, metric4 = st.columns(4)
        
        with metric1:
            st.metric("Total Claims", f"{df['Claims'].sum():,}")
        with metric2:
            st.metric("Fraud Detected", f"{df['Fraudulent'].sum():,}")
        with metric3:
            st.metric("Average Claim", f"${df['Amount'].mean()/df['Claims'].mean():,.2f}")
        with metric4:
            st.metric("Fraud Rate", f"{(df['Fraudulent'].sum()/df['Claims'].sum()*100):.1f}%")

if __name__ == "__main__":
    app = InsuranceClaimApp()
    app.run()
