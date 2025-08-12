# file: main_orchestrator.py
from core.data_provider import DataProvider
from core.feature_engineering import FeatureEngineer
from core.ml.pipeline import MLPipeline

class Orchestrator:
    def __init__(self, ticker, start_date, end_date):
        self.ticker = ticker
        self.start_date = start_date
        self.end_date = end_date
        self.final_df = None
        self.ml_results = None

    def execute(self):
        print(f"\n===== Starting Analysis for {self.ticker} =====")
        # 1. Fetch Data
        provider = DataProvider(self.ticker, self.start_date, self.end_date)
        if not provider.fetch_data():
            return False
        
        # 2. Add Features
        engineer = FeatureEngineer(provider.get_data())
        self.final_df = engineer.add_all_features()

        # 3. Run ML Pipeline
        ml_pipe = MLPipeline(self.final_df)
        if ml_pipe.prepare_data():
            self.ml_results = ml_pipe.evaluate_models()
            ml_pipe.train_final_model(model_name='Random Forest') # Let's default to RF for now
            ml_pipe.save_model(f'trained_models/{self.ticker}_model.pkl')
        else:
            print("Could not run ML Pipeline due to insufficient data.")
            return False
        
        print(f"===== Analysis for {self.ticker} Complete =====")
        print("Final Model Performance Summary:", self.ml_results)
        return True