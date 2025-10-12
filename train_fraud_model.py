import lightgbm
import pandas as pd
import numpy as np
from lightgbm import LGBMClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split, KFold, cross_val_score
from sklearn.metrics import classification_report, roc_auc_score, roc_curve
import joblib
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def preprocess_data(df):
    """
    Preprocess the fraud detection data
    """
    df = df.copy()
    
    # Create label encoders
    le_dict = {}
    categorical_cols = df.select_dtypes(include=['object']).columns
    
    # Encode categorical variables
    for col in categorical_cols:
        if col not in ['PolicyNumber', 'RepNumber']:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col].astype(str))
            le_dict[col] = le
    
    # Feature engineering
    if 'VehicleAge' in df.columns:
        df['VehicleAgeSquared'] = df['VehicleAge'] ** 2
    
    if 'ClaimAmount' in df.columns and 'VehiclePrice' in df.columns:
        df['ClaimAmountRatio'] = df['ClaimAmount'] / df['VehiclePrice'].clip(lower=1)
    
    if 'PolicyDuration' in df.columns:
        df['PolicyDurationMonths'] = df['PolicyDuration'] / 30
        df['IsNewPolicy'] = (df['PolicyDuration'] < 90).astype(int)
    
    if 'VehicleAge' in df.columns and 'ClaimAmount' in df.columns:
        df['AgeAmount_Interaction'] = df['VehicleAge'] * df['ClaimAmount']
    
    return df, le_dict

def find_optimal_threshold(y_true, y_pred_proba):
    """
    Find the optimal classification threshold using ROC curve
    """
    fpr, tpr, thresholds = roc_curve(y_true, y_pred_proba)
    optimal_idx = np.argmax(tpr - fpr)
    optimal_threshold = thresholds[optimal_idx]
    return optimal_threshold

def train_fraud_model():
    """
    Train and save the fraud detection model
    """
    try:
        logger.info("Starting fraud detection model training...")
        
        # Load data
        logger.info("Loading dataset...")
        df = pd.read_csv('c:/Users/anonymous/Downloads/fraud_oracle.csv')
        logger.info(f"Dataset shape: {df.shape}")
        
        # Check class distribution
        fraud_dist = df['FraudFound_P'].value_counts(normalize=True)
        logger.info("\nFraud Distribution:")
        logger.info(fraud_dist)
        
        # Preprocess data
        logger.info("\nPreprocessing data...")
        df_processed, le_dict = preprocess_data(df)
        
        # Split features and target
        X = df_processed.drop(['FraudFound_P', 'PolicyNumber', 'RepNumber'], axis=1)
        y = df_processed['FraudFound_P']
        
        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        X_scaled = pd.DataFrame(X_scaled, columns=X.columns)
        
        # Train/test split
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42, stratify=y
        )
        
        logger.info(f"Training set shape: {X_train.shape}")
        logger.info(f"Testing set shape: {X_test.shape}")
        
        # Define model with optimal parameters
        model = LGBMClassifier(
            n_estimators=1000,
            learning_rate=0.05,
            max_depth=7,
            num_leaves=31,
            class_weight='balanced',
            n_jobs=-1,
            random_state=42,
            boosting_type='goss',
            reg_alpha=0.1,
            reg_lambda=0.1
        )
        
        # Cross-validation
        logger.info("\nPerforming cross-validation...")
        cv = KFold(n_splits=5, shuffle=True, random_state=42)
        cv_scores = cross_val_score(
            model, X_train, y_train,
            cv=cv, scoring='roc_auc',
            n_jobs=-1
        )
        cv_scores = np.array(cv_scores)  # Ensure it's a numpy array
        
        logger.info(f"Cross-validation ROC-AUC scores: {cv_scores}")
        logger.info(f"Mean ROC-AUC: {np.mean(cv_scores):.3f} (+/- {np.std(cv_scores) * 2:.3f})")
        
        # Train final model
        logger.info("\nTraining final model...")
        eval_set = [(X_test, y_test)]
        model.fit(
            X_train, y_train,
            eval_set=eval_set,
            eval_metric=['auc', 'binary_logloss']
        )
        
        # Make predictions
        y_pred_proba = model.predict_proba(X_test)[:, 1]
        
        # Find optimal threshold
        optimal_threshold = find_optimal_threshold(y_test, y_pred_proba)
        y_pred = (y_pred_proba >= optimal_threshold).astype(int)
        
        # Print results
        logger.info(f"\nResults with optimal threshold ({optimal_threshold:.3f}):")
        logger.info("\n" + classification_report(y_test, y_pred))
        logger.info(f"\nROC-AUC Score: {roc_auc_score(y_test, y_pred_proba)}")
        
        # Save models and artifacts
        logger.info("\nSaving model and artifacts...")
        model_dir = Path('models/fraud_detector')
        model_dir.mkdir(parents=True, exist_ok=True)
        
        joblib.dump(model, model_dir / 'model.joblib')
        joblib.dump(scaler, model_dir / 'scaler.joblib')
        joblib.dump(le_dict, model_dir / 'label_encoders.joblib')
        joblib.dump(optimal_threshold, model_dir / 'optimal_threshold.joblib')
        
        # Save feature importance
        feature_imp = pd.DataFrame({
            'Feature': X.columns,
            'Importance': model.feature_importances_
        }).sort_values('Importance', ascending=False)
        
        feature_imp.to_csv(model_dir / 'feature_importance.csv', index=False)
        
        logger.info("Training completed successfully!")
        logger.info(f"Model and artifacts saved in: {model_dir}")
        
        return {
            'model': model,
            'scaler': scaler,
            'label_encoders': le_dict,
            'optimal_threshold': optimal_threshold,
            'feature_importance': feature_imp
        }
        
    except Exception as e:
        logger.error(f"Error during training: {str(e)}")
        raise

def test_fraud_model():
    """
    Test the trained fraud detection model
    """
    try:
        logger.info("Testing fraud detection model...")
        
        # Load model and artifacts
        model_dir = Path('models/fraud_detector')
        model = joblib.load(model_dir / 'model.joblib')
        scaler = joblib.load(model_dir / 'scaler.joblib')
        le_dict = joblib.load(model_dir / 'label_encoders.joblib')
        optimal_threshold = joblib.load(model_dir / 'optimal_threshold.joblib')
        
        # Test cases
        test_cases = [
            {
                'name': 'Low Risk Claim',
                'data': {
                    'VehicleAge': 3,
                    'VehiclePrice': 25000,
                    'ClaimAmount': 2000,
                    'PolicyDuration': 365,
                    'PreviousClaims': 0,
                }
            },
            {
                'name': 'High Risk Claim',
                'data': {
                    'VehicleAge': 12,
                    'VehiclePrice': 15000,
                    'ClaimAmount': 20000,
                    'PolicyDuration': 30,
                    'PreviousClaims': 4,
                }
            }
        ]
        
        for test_case in test_cases:
            logger.info(f"\nTesting {test_case['name']}:")
            
            # Prepare test data
            test_data = pd.DataFrame([test_case['data']])
            
            # First add engineered features (before encoding)
            if 'VehicleAge' in test_data.columns:
                test_data['VehicleAgeSquared'] = test_data['VehicleAge'] ** 2
            
            if all(col in test_data.columns for col in ['ClaimAmount', 'VehiclePrice']):
                test_data['ClaimAmountRatio'] = test_data['ClaimAmount'] / test_data['VehiclePrice'].clip(lower=1)
            
            if 'PolicyDuration' in test_data.columns:
                test_data['PolicyDurationMonths'] = test_data['PolicyDuration'] / 30
                test_data['IsNewPolicy'] = (test_data['PolicyDuration'] < 90).astype(int)
            
            if all(col in test_data.columns for col in ['VehicleAge', 'ClaimAmount']):
                test_data['AgeAmount_Interaction'] = test_data['VehicleAge'] * test_data['ClaimAmount']
            
            # Get expected feature names from scaler
            expected_features = scaler.feature_names_in_
            
            # Create new dataframe with expected column names
            test_data_mapped = pd.DataFrame(columns=expected_features)
            
            # Map test data to expected feature names
            feature_mapping = {
                'VehicleAge': 'Age',
                'ClaimAmount': 'ClaimAmount',
                'VehiclePrice': 'VehiclePrice',
                'PolicyDuration': 'PolicyDuration',
                'PreviousClaims': 'PreviousClaims'
            }
            
            # Fill mapped columns
            for test_col, train_col in feature_mapping.items():
                if test_col in test_data.columns and train_col in expected_features:
                    test_data_mapped[train_col] = test_data[test_col]
            
            # Add default values for missing columns
            for feature in expected_features:
                if feature not in test_data_mapped.columns or test_data_mapped[feature].isna().all():
                    test_data_mapped[feature] = 0
            
            # Apply preprocessing for categorical variables
            for col, le in le_dict.items():
                if col in test_data_mapped.columns:
                    if test_data_mapped[col].dtype == 'object':
                        test_data_mapped[col] = le.transform(test_data_mapped[col].astype(str))
            
            # Add engineered features
            if 'Age' in test_data_mapped.columns:
                test_data_mapped['VehicleAgeSquared'] = test_data_mapped['Age'] ** 2
            
            if all(col in test_data_mapped.columns for col in ['ClaimAmount', 'VehiclePrice']):
                test_data_mapped['ClaimAmountRatio'] = test_data_mapped['ClaimAmount'] / test_data_mapped['VehiclePrice'].clip(lower=1)
            
            if 'PolicyDuration' in test_data_mapped.columns:
                test_data_mapped['PolicyDurationMonths'] = test_data_mapped['PolicyDuration'] / 30
                test_data_mapped['IsNewPolicy'] = (test_data_mapped['PolicyDuration'] < 90).astype(int)
            
            if all(col in test_data_mapped.columns for col in ['Age', 'ClaimAmount']):
                test_data_mapped['AgeAmount_Interaction'] = test_data_mapped['Age'] * test_data_mapped['ClaimAmount']
                
            # Ensure column order matches training data
            test_data_mapped = test_data_mapped[expected_features]

            # Scale features
            test_data_scaled = scaler.transform(test_data_mapped)
            
            # Get predictions
            fraud_prob = model.predict_proba(test_data_scaled)[:, 1][0]
            is_fraud = fraud_prob >= optimal_threshold
            
            logger.info(f"Fraud Probability: {fraud_prob:.2%}")
            logger.info(f"Is Fraud: {is_fraud}")
            logger.info(f"Risk Level: {'High' if fraud_prob > 0.7 else 'Medium' if fraud_prob > 0.4 else 'Low'}")
        
        logger.info("\nModel testing completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during testing: {str(e)}")
        raise

if __name__ == "__main__":
    # Train the model
    train_fraud_model()
    
    # Test the model
    test_fraud_model()

