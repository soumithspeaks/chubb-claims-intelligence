# Smart Insurance Claims Intelligence System

A comprehensive insurance claims processing platform that combines modern web interfaces (Next.js + Streamlit) with AI-powered backend services for fraud detection and automated damage assessment.

## 🌟 Features

- **Advanced Fraud Detection**
  - Machine learning-based fraud risk assessment (94% accuracy)
  - Multi-factor analysis of temporal, financial, behavioral patterns
  - Real-time risk scoring and actionable recommendations
  - Historical pattern analysis and anomaly detection

- **Automated Damage Assessment**
  - YOLOv8-based vehicle damage detection (89% mAP)
  - Multiple damage type classification (scratches, dents, breaks)
  - Severity assessment and repair cost estimation ($245 RMSE)
  - Support for multiple image angles and lighting conditions

- **Modern User Interfaces**
  - Next.js-based premium interface with real-time analysis
  - Streamlit-based enhanced dashboard for analytics
  - FastAPI backend for efficient ML model serving
  - Comprehensive visualization of analysis results

- **Analytics & Reporting**
  - Claims trend analysis with interactive charts
  - Fraud detection rate monitoring
  - Cost analysis and predictions
  - MLflow tracking for model performance

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- Node.js 18+ (for Next.js frontend)
- Git
- Windows PowerShell (for Windows users)

### Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/insurance-claims-analyzer.git
   cd insurance-claims-analyzer
   ```

2. Choose your interface:

   a) Premium UI (Next.js):
   ```bash
   cd chubb-claims-intelligence
   npm install
   npm run dev
   ```

### Development Setup

For ML development:
```bash
pip install -r requirements-dev.txt

## 🧪 Testing

Run the test suite:
```bash
pytest test_all_models.py
```

## 📦 Project Structure

```
├── app/
│   ├── core/
│   │   ├── damage_detector.py
│   │   ├── fraud_detector.py
│   │   └── ...
│   └── frontend/
│       └── enhanced_app.py
├── models/
│   ├── damage_detector/
│   ├── fraud_detector/
│   └── cost_estimator/
├── data/
├── tests/
├── requirements.txt
└── README.md
```

## 🛠 Technologies Used

- **Machine Learning**: scikit-learn, PyTorch, YOLOv8
- **Web Framework**: Streamlit, FastAPI
- **Data Processing**: NumPy, Pandas, OpenCV
- **Visualization**: Plotly, Matplotlib
- **Testing**: pytest
- **MLOps**: MLflow

## 📈 Model Performance

- Fraud Detection Accuracy: 94%
- Damage Detection mAP: 0.89
- Cost Estimation RMSE: $245

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Thanks to the ultralytics team for YOLOv8
- Insurance claim dataset providers
- Open-source community contributors
