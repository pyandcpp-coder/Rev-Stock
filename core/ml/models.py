from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor

def get_models():
    models ={
        'Linear Regression': LinearRegression(), 
        'Random Forest': RandomForestRegressor(n_estimators=100,max_depth=10,random_state=42,n_jobs=-1), 
        'XGBoost': XGBRegressor(objective='reg:squarederror', n_estimators=100, random_state=42),
    }
    return models