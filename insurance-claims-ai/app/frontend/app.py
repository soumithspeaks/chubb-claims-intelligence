import gradio as gr
import requests
from PIL import Image
import io

def analyze_damage(image):
    # Convert image to bytes
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    
    # Create file-like object for API request
    files = {'file': ('image.png', img_byte_arr, 'image/png')}
    
    # Send request to FastAPI backend
    response = requests.post('http://localhost:8000/analyze', files=files)
    result = response.json()
    
    # Format output
    return {
        "Damage Type": result['damage_assessment']['damage_type'],
        "Severity": f"{result['damage_assessment']['severity']:.2%}",
        "Estimated Cost": f"${result['cost_estimation']['total_cost']:.2f}",
        "Confidence": f"{result['cost_estimation']['confidence']:.2%}"
    }

# Create Gradio interface
interface = gr.Interface(
    fn=analyze_damage,
    inputs=gr.Image(type="pil"),
    outputs=gr.JSON(),
    title="Insurance Claims AI",
    description="Upload a car image to analyze damage and estimate repair costs."
)

if __name__ == "__main__":
    interface.launch()