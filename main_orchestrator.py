# file: main_orchestrator.py
from core.data_provider import DataProvider
from core.feature_engineering import FeatureEngineer
from core.ml.pipeline import MLPipeline

# class Orchestrator:
#     def __init__(self, ticker:str, start_date:str, end_date:str):
#         # self.ticker = ticker
#         # self.start_date = start_date
#         # self.end_date = end_date
#         # self.final_df = None
#         # self.ml_results = None
#         # self.all_results=[]
#         self.ticker = ticker
#         self.start_date = start_date
#         self.end_date = end_date
#         self.final_df = None
#         self.ml_results = {}
#         self.all_results=[]



#     def execute(self):
#         print(f"\n===== Starting Analysis for {self.ticker} =====")
#         # 1. Fetch Data
#         provider = DataProvider(self.ticker, self.start_date, self.end_date)
#         if not provider.fetch_data():
#             return False
        
#         # 2. Add Features
#         engineer = FeatureEngineer(provider.get_data())
#         self.final_df = engineer.add_all_features()

#         # 3. Run ML Pipeline
#         ml_pipe = MLPipeline(self.final_df)
#         # if ml_pipe.prepare_data():
#         #     self.ml_results = ml_pipe.evaluate_models()
#         #     ml_pipe.train_final_model(model_name='Random Forest') # Let's default to RF for now
#         #     ml_pipe.save_model(f'trained_models/{self.ticker}_model.pkl')
#         # else:
#         #     print("Could not run ML Pipeline due to insufficient data.")
#         #     return False
        
#         # print(f"===== Analysis for {self.ticker} Complete =====")
#         # print("Final Model Performance Summary:", self.ml_results)
#         # return True
#         if ml_pipe.prepare_data():
#             ml_results = ml_pipe.evaluate_models()
#             # For the grid, we only need the latest prediction, not the full timeseries
#             latest_prediction = ml_pipe.train_and_predict_latest() 
#             latest_data = self.final_df.iloc[-1] # Get the most recent day's data
            
#             return {
#                 "ticker": self.ticker,
#                 "latest_close": latest_data.get('Close'),
#                 "rsi": latest_data.get('RSI'),
#                 "macd_signal": latest_data.get('MACD_Signal'),
#                 "predicted_next_close": latest_prediction,
#                 "model_performance": self.ml_results.get('Random Forest') # Just show one model's RMSE
#             }
#         return None

#     # The main execute method now loops through all tickers
#     def execute_comparison(self):
#         for ticker in self.tickers:
#             result = self.execute_for_ticker(ticker)
#             if result:
#                 self.all_results.append(result)
#         print(f"\n===== Comparison Analysis Complete =====")
#         return self.all_results


class Orchestrator:
    def __init__(self, ticker: str, start_date: str, end_date: str):
        self.ticker = ticker
        self.start_date = start_date
        self.end_date = end_date
        self.final_df = None
        self.ml_results = {}

    def execute(self):
        print(f"\n===== Starting Analysis for {self.ticker} =====")
        provider = DataProvider(self.ticker, self.start_date, self.end_date)
        if not provider.fetch_data():
            return None

        engineer = FeatureEngineer(provider.get_data())
        self.final_df = engineer.add_all_features()

        ml_pipe = MLPipeline(self.final_df)
        if not ml_pipe.prepare_data():
            return None

        self.ml_results = ml_pipe.evaluate_models() or {}
        latest_prediction = ml_pipe.train_and_predict_latest()
        latest_data = self.final_df.iloc[-1]

        return {
            "ticker": self.ticker,
            "latest_close": latest_data.get('Close'),
            "rsi": latest_data.get('RSI'),
            "macd_signal": latest_data.get('MACD_Signal'),
            "predicted_next_close": latest_prediction,
            "model_performance": self.ml_results.get('Random Forest', {})
        }
