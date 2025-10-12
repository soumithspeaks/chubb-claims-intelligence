import gradio as gr
from pathlib import Path
import sys
import json

# Add the parent directory to system path
sys.path.append(str(Path(__file__).parent.parent))

from core.fraud_detector import FraudDetector
from core.damage_detector import DamageDetector

class InsuranceClaimAnalyzer:
    def __init__(self):
        self.fraud_detector = FraudDetector()
        self.damage_detector = DamageDetector()
        
    def analyze_claim(self, claim_amount, vehicle_price, vehicle_age, policy_duration, 
                     previous_claims, time_to_report, claim_date, documents):
        """Process claim information and detect potential fraud"""
        claim_data = {
            'ClaimAmount': float(claim_amount),
            'VehiclePrice': float(vehicle_price),
            'VehicleAge': float(vehicle_age),
            'PolicyDuration': float(policy_duration),
            'previous_claims_count': int(previous_claims),
            'time_to_report': float(time_to_report),
            'claim_time': claim_date,
            'required_documents': {
                'Police Report': 'Police Report' in documents,
                'Medical Report': 'Medical Report' in documents,
                'Witness Statement': 'Witness Statement' in documents,
                'Photos': 'Photos' in documents
            }
        }
        
        result = self.fraud_detector.detect_fraud(claim_data)
        
        # Format results for display
        risk_level = result['risk_level'].upper()
        fraud_prob = f"{result['fraud_probability']:.1%}"
        
        findings = "\n".join([f"• {finding}" for finding in result['analysis']['findings']])
        recommendations = "\n".join([f"• {rec}" for rec in result['analysis']['recommendations']])
        
        # Create risk factors visualization data
        risk_data = []
        for category, score in result['risk_factors'].items():
            category_name = category.replace('_', ' ').title()
            risk_data.append({
                'Category': category_name,
                'Score': score
            })
            
        return (
            f"Risk Level: {risk_level}",
            f"Fraud Probability: {fraud_prob}",
            result['analysis']['summary'],
            findings,
            recommendations,
            json.dumps(risk_data)  # For chart visualization
        )
    
    def analyze_damage(self, image):
        """Analyze vehicle damage from uploaded image"""
        if image is None:
            return "No image provided", None, None, None
            
        result = self.damage_detector.detect_damage(image)
        
        if not result['damages_detected']:
            return "No significant damage detected", None, None, None
            
        # Format damage detections
        damages_list = []
        for damage in result['damages']:
            confidence = f"{damage['confidence']:.1%}"
            severity = "High" if damage['severity'] > 0.7 else "Medium" if damage['severity'] > 0.4 else "Low"
            damages_list.append(f"• {damage['type'].title()}: {confidence} confidence (Severity: {severity})")
            
        damages_text = "\n".join(damages_list)
        
        # Format cost estimate
        cost_estimate = f"${result['estimated_cost']:,.2f}"
        
        return (
            "Damage Analysis Complete",
            damages_text,
            cost_estimate,
            result['annotated_image']
        )
    
    def create_ui(self):
        """Create the Gradio interface"""
        with gr.Blocks(title="Insurance Claims Analyzer", theme=gr.themes.Monochrome()) as app:
            gr.Markdown("""
            # Smart Insurance Claims Analyzer
            Advanced AI-powered system for fraud detection and damage assessment
            """)
            
            with gr.Tabs():
                # Claim Analysis Tab
                with gr.Tab("Claim Analysis"):
                    with gr.Row():
                        with gr.Column():
                            claim_amount = gr.Number(label="Claim Amount ($)", value=0)
                            vehicle_price = gr.Number(label="Vehicle Price ($)", value=0)
                            vehicle_age = gr.Number(label="Vehicle Age (years)", value=0)
                            policy_duration = gr.Number(label="Policy Duration (days)", value=0)
                            
                        with gr.Column():
                            previous_claims = gr.Number(label="Previous Claims Count", value=0)
                            time_to_report = gr.Number(label="Time to Report (days)", value=0)
                            claim_date = gr.Date(label="Claim Date")
                            documents = gr.CheckboxGroup(
                                choices=["Police Report", "Medical Report", "Witness Statement", "Photos"],
                                label="Required Documents"
                            )
                            
                    analyze_btn = gr.Button("Analyze Claim", variant="primary")
                    
                    with gr.Row():
                        risk_level = gr.Textbox(label="Risk Assessment")
                        fraud_prob = gr.Textbox(label="Fraud Probability")
                        
                    summary = gr.Textbox(label="Analysis Summary", lines=2)
                    
                    with gr.Row():
                        findings = gr.Textbox(label="Key Findings", lines=5)
                        recommendations = gr.Textbox(label="Recommendations", lines=5)
                        
                    risk_chart = gr.Plot(label="Risk Factors")
                
                # Damage Assessment Tab
                with gr.Tab("Damage Assessment"):
                    with gr.Row():
                        with gr.Column():
                            image_input = gr.Image(type="pil", label="Upload Vehicle Image")
                            analyze_damage_btn = gr.Button("Analyze Damage", variant="primary")
                            
                        with gr.Column():
                            status = gr.Textbox(label="Status")
                            damages = gr.Textbox(label="Detected Damages", lines=5)
                            cost = gr.Textbox(label="Estimated Repair Cost")
                            output_image = gr.Image(type="pil", label="Analyzed Image")
                
            # Connect interface components
            analyze_btn.click(
                fn=self.analyze_claim,
                inputs=[
                    claim_amount, vehicle_price, vehicle_age, policy_duration,
                    previous_claims, time_to_report, claim_date, documents
                ],
                outputs=[risk_level, fraud_prob, summary, findings, recommendations, risk_chart]
            )
            
            analyze_damage_btn.click(
                fn=self.analyze_damage,
                inputs=[image_input],
                outputs=[status, damages, cost, output_image]
            )
            
        return app

if __name__ == "__main__":
    analyzer = InsuranceClaimAnalyzer()
    app = analyzer.create_ui()
    app.launch(server_name="0.0.0.0", server_port=7860)