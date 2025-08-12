import pandas as pd

class FeatureEngineer:
    def __init__(self, data):
        if not isinstance(data, pd.DataFrame):
            raise TypeError("Input must be a pandas DataFrame.")
        self.df = data.copy()

    def add_all_features(self):
        print("Adding all technical features...")
        self.calculate_smas()
        self.calculate_macd()
        self.calculate_rsi()
        self.calculate_additional_features()
        self.df.dropna(inplace=True) # Drop NaNs created by indicators
        print("Features added successfully.")
        return self.get_data()

    def get_data(self):
        return self.df.copy()
    def calculate_smas(self, short_window=50, long_window=200):
        """Calculates the Simple Moving Average"""
        self.df['SMA_50'] = self.df['Close'].rolling(window=50, min_periods=1).mean()
        self.df['SMA_200'] = self.df['Close'].rolling(window=200, min_periods=1).mean()
        print("Calculated the SMA's")

    def calculate_macd(self, short_window=12, long_window=26, signal_window=9):
        """Calculates the MACD"""
        self.df['EMA_12'] = self.df['Close'].ewm(span=short_window, adjust=False).mean()
        self.df['EMA_26'] = self.df['Close'].ewm(span=long_window, adjust=False).mean()
        self.df['MACD'] = self.df['EMA_12'] - self.df['EMA_26']
        self.df['MACD_Signal'] = self.df['MACD'].ewm(span=signal_window, adjust=False).mean()
        self.df['MACD_Histogram'] = self.df['MACD'] - self.df['MACD_Signal']
        print("Calculated MACD")

    def calculate_rsi(self, window=14):
        """Calculates the RSI"""
        delta = self.df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        loss = loss.replace(0, 1e-10)
        rs = gain / loss
        self.df['RSI'] = 100 - (100 / (1 + rs))
        self.df['RSI'] = self.df['RSI'].clip(lower=0, upper=100)
        print("Calculated the RSI")

    def calculate_additional_features(self):
        """Calculate additional technical features"""
        # Price momentum features
        self.df['Price_Change'] = self.df['Close'].pct_change()
        self.df['Price_Change_3d'] = self.df['Close'].pct_change(3)
        self.df['Price_Change_5d'] = self.df['Close'].pct_change(5)
        
        # Volatility
        self.df['Volatility_10d'] = self.df['Price_Change'].rolling(10).std()
        
        # Volume features
        self.df['Volume_SMA_10'] = self.df['Volume'].rolling(10).mean()
        self.df['Volume_Ratio'] = self.df['Volume'] / self.df['Volume_SMA_10']
        
        # Price position features
        self.df['High_Low_Ratio'] = self.df['High'] / self.df['Low']
        self.df['Close_to_High'] = self.df['Close'] / self.df['High']
        self.df['Close_to_Low'] = self.df['Close'] / self.df['Low']
        
        # Moving average ratios
        self.df['Price_to_SMA50'] = self.df['Close'] / self.df['SMA_50']
        self.df['Price_to_SMA200'] = self.df['Close'] / self.df['SMA_200']
        self.df['SMA50_to_SMA200'] = self.df['SMA_50'] / self.df['SMA_200']
        
        print("Calculated additional technical features")
