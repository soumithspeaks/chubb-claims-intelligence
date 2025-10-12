import streamlit as st
import cv2
import numpy as np
from pathlib import Path
import sys
import os
from PIL import Image
import time
import joblib

# Configure page
st.set_page_config(
    page_title="Chubb Insurance Claims Analyzer",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
    <style>
    /* Main container styling */
    .main {
        background-color: #f8f9fa;
        padding: 2rem;
    }
    
    /* Header styling */
    .title-container {
        background-color: #004B87;
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    /* Card styling */
    .card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    
    /* Button styling */
    .stButton > button {
        background-color: #004B87;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        font-weight: bold;
        width: 100%;
    }
    
    .stButton > button:hover {
        background-color: #003666;
    }
    
    /* Risk level indicators */
    .risk-high {
        color: #dc3545;
        font-weight: bold;
        padding: 0.5rem;
        background-color: rgba(220, 53, 69, 0.1);
        border-radius: 5px;
    }
    
    .risk-medium {
        color: #ffc107;
        font-weight: bold;
        padding: 0.5rem;
        background-color: rgba(255, 193, 7, 0.1);
        border-radius: 5px;
    }
    
    .risk-low {
        color: #28a745;
        font-weight: bold;
        padding: 0.5rem;
        background-color: rgba(40, 167, 69, 0.1);
        border-radius: 5px;
    }
    
    /* Progress bar colors */
    .stProgress > div > div > div {
        background-color: #004B87;
    }
    </style>
""", unsafe_allow_html=True)

def analyze_damage(image):
    """Analyze damage in an image using OpenCV"""
    if isinstance(image, str):
        img = cv2.imread(image)
    else:
        img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Apply adaptive thresholding
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
    
    # Find contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Calculate damage severity based on contour area
    total_area = img.shape[0] * img.shape[1]
    damage_area = sum(cv2.contourArea(c) for c in contours)
    damage_ratio = damage_area / total_area
    
    # Draw contours on image
    img_with_contours = img.copy()
    cv2.drawContours(img_with_contours, contours, -1, (0, 0, 255), 2)
    
    return {
        'damage_ratio': damage_ratio,
        'severity': 'High' if damage_ratio > 0.3 else 'Medium' if damage_ratio > 0.1 else 'Low',
        'annotated_image': cv2.cvtColor(img_with_contours, cv2.COLOR_BGR2RGB)
    }

def main():
    # Header
    st.markdown("""
        <div class="title-container">
            <h1>🛡️ Chubb Insurance Claims Analyzer</h1>
            <p>Advanced AI-Powered Claims Analysis System</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Create two columns
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📸 Damage Assessment")
        
        # Image upload
        uploaded_file = st.file_uploader("Upload images of the damage", type=['png', 'jpg', 'jpeg'])
        
        if uploaded_file:
            image = Image.open(uploaded_file)
            
            # Show original and analyzed images side by side
            img_col1, img_col2 = st.columns(2)
            
            with img_col1:
                st.image(image, caption="Original Image", use_column_width=True)
            
            with img_col2:
                with st.spinner("Analyzing damage..."):
                    analysis = analyze_damage(image)
                    st.image(analysis['annotated_image'], caption="Damage Detection", use_column_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Claim Details Section
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📝 Claim Details")
        
        # Two columns for claim details
        det_col1, det_col2 = st.columns(2)
        
        with det_col1:
            incident_date = st.date_input("Date of Incident")
            claim_amount = st.number_input("Claim Amount ($)", min_value=0, value=1000)
            vehicle_make = st.selectbox("Vehicle Make", [
                "Toyota", "Honda", "Ford", "BMW", "Mercedes", "Other"
            ])
        
        with det_col2:
            incident_type = st.selectbox("Type of Incident", [
                "Collision", "Natural Disaster", "Theft", "Vandalism", "Other"
            ])
            location = st.text_input("Incident Location")
            police_report = st.checkbox("Police Report Filed")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        # Risk Assessment
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("🎯 Risk Assessment")
        
        if uploaded_file:
            with st.spinner("Calculating risk score..."):
                # Simulate risk calculation
                time.sleep(1)
                risk_score = np.random.random()
                
                # Display risk level
                risk_level = "high" if risk_score > 0.7 else "medium" if risk_score > 0.3 else "low"
                st.markdown(f"""
                    <div class="risk-{risk_level}">
                        Risk Level: {risk_level.upper()}
                    </div>
                """, unsafe_allow_html=True)
                
                # Risk metrics
                st.metric("Fraud Probability", f"{risk_score:.1%}")
                st.metric("Damage Severity", analysis['severity'])
                
                # Progress bars for different risk factors
                st.subheader("Risk Factors")
                st.progress(risk_score, "Overall Risk")
                st.progress(np.random.random(), "Historical Risk")
                st.progress(np.random.random(), "Behavioral Risk")
                
                # Recommendations
                st.subheader("📋 Recommendations")
                if risk_level == "high":
                    st.error("• Immediate investigation required\n• Schedule physical inspection\n• Request additional documentation")
                elif risk_level == "medium":
                    st.warning("• Additional verification needed\n• Review documentation\n• Consider inspection")
                else:
                    st.success("• Standard processing\n• Regular documentation sufficient")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Action buttons
        if uploaded_file:
            st.button("Generate Report")
            st.button("Schedule Inspection")
            st.download_button(
                label="Download Analysis",
                data="Analysis report data",
                file_name="claim_analysis.pdf",
                mime="application/pdf"
            )

if __name__ == "__main__":
    main()