# file: core/ml/pipeline.py (Corrected Version)

import pandas as pd
import numpy as np
from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error
from .models import get_models
import joblib
import os

class MLPipeline:
    def __init__(self, data):
        if not isinstance(data, pd.DataFrame):
            raise TypeError("Input Data must be a pandas DataFrame")
        self.df = data.copy()
        self.scaler = StandardScaler()
        self.models = get_models()
        self.results = {}
        self.final_model = None

    def prepare_data(self, prediction_days=1):
        # This method is already correct. No changes needed here.
        base_features = [
            'Open', 'High', 'Low', 'Close', 'Volume', 'SMA_50', 'SMA_200', 'MACD', 
            'MACD_Signal', 'MACD_Histogram', 'RSI', 'Price_Change', 'Price_Change_3d', 
            'Price_Change_5d', 'Volatility_10d', 'Volume_Ratio', 'High_Low_Ratio',
            'Close_to_High', 'Close_to_Low', 'Price_to_SMA50', 'Price_to_SMA200', 'SMA50_to_SMA200'
        ]
        for feature in base_features:
            if feature in self.df.columns:
                self.df[f'{feature}_lag1'] = self.df[feature].shift(1)
        self.df['Future_Close'] = self.df['Close'].shift(-prediction_days)
        feature_columns = [f'{f}_lag1' for f in base_features if f'{f}_lag1' in self.df.columns]
        self.df.dropna(inplace=True)
        if len(self.df) < 50: # Reduced for smaller datasets
            print("Not enough data after cleaning!")
            return False
        self.X = self.df[feature_columns]
        self.y_price = self.df['Future_Close'] # We will use this for regression
        print(f"ML data prepared: {len(self.X)} samples.")
        return True
    
    def evaluate_models(self):
        print("Evaluating Models with TimeSeriesSplit...")
        tscv = TimeSeriesSplit(n_splits=5)

        for name, model in self.models.items():
            print(f"--- Evaluating {name} ---")
            rmse_scores = []

            # --- FIX STARTS HERE ---
            # The loop logic was incorrect. This is the corrected version.
            for train_idx, test_idx in tscv.split(self.X):
                X_train, X_test = self.X.iloc[train_idx], self.X.iloc[test_idx]
                y_train, y_test = self.y_price.iloc[train_idx], self.y_price.iloc[test_idx]

                # Scaling and training must happen INSIDE the loop for each fold
                X_train_scaled = self.scaler.fit_transform(X_train)
                X_test_scaled = self.scaler.transform(X_test)
                
                model.fit(X_train_scaled, y_train)
                preds = model.predict(X_test_scaled)
                rmse_scores.append(np.sqrt(mean_squared_error(y_test, preds)))
            # --- FIX ENDS HERE ---
            
            self.results[name] = {'RMSE': np.mean(rmse_scores), 'RMSE_std': np.std(rmse_scores)}
            print(f"  Average RMSE: {self.results[name]['RMSE']:.2f} (+/- {self.results[name]['RMSE_std']:.2f})")
        return self.results

    def train_final_model(self, model_name='XGBoost'):
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not found")
        
        print(f"Training final model ({model_name}) on all data...")
        self.final_model = self.models[model_name]
        
        # Use the correct target variable 'y_price'
        X_scaled = self.scaler.fit_transform(self.X)
        self.final_model.fit(X_scaled, self.y_price)
        
        print("Final model trained.")
        return self.final_model
    
    def save_model(self, path='trained_models/model.pkl'):
        if self.final_model:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(path), exist_ok=True)
            joblib.dump({'model': self.final_model, 'scaler': self.scaler}, path)
            print(f"Model saved to {path}")