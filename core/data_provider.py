import pandas as pd
import yfinance as yf
from sqlalchemy.orm import Session
from .database import SessionLocal, StockPrice 
from datetime import date, timedelta

class DataProvider:
    def __init__(self, ticker, start_date_str, end_date_str):
        self.ticker = ticker
        self.start_date = date.fromisoformat(start_date_str)
        self.end_date = date.fromisoformat(end_date_str)
        self.df = None

    def fetch_data(self):
        db: Session = SessionLocal()
        try:
            # 1. Find the latest date we have in the DB for this ticker
            latest_db_date_result = db.query(StockPrice.date)\
                .filter(StockPrice.ticker == self.ticker)\
                .order_by(StockPrice.date.desc()).first()

            # --- THE FIX IS HERE: Use an explicit, safe if/else block ---
            # This is much clearer and less prone to edge-case errors.
            if latest_db_date_result and latest_db_date_result[0]:
                # If we have a valid date, start fetching from the next day
                start_fetch = latest_db_date_result[0] + timedelta(days=1)
            else:
                # If there's no record or the date is somehow null, start from the beginning
                start_fetch = self.start_date
            
            if start_fetch <= self.end_date:
                print(f"Fetching new data for {self.ticker} from {start_fetch} to {self.end_date}...")
                new_df = yf.download(self.ticker, start=start_fetch, end=self.end_date)
                
                if not new_df.empty:
                    if len(new_df.columns.levels) > 1:
                        new_df.columns = new_df.columns.droplevel(1)
                    new_df.reset_index(inplace=True)
                    new_df.columns = [str(c).lower() for c in new_df.columns]
                    new_df['ticker'] = self.ticker
                    
                    records = new_df.to_dict(orient='records')
                    
                    from sqlalchemy.dialects.postgresql import insert
                    if records:
                        insert_stmt = insert(StockPrice).values(records)
                        do_nothing_stmt = insert_stmt.on_conflict_do_nothing(
                            index_elements=['ticker', 'date']
                        )
                        db.execute(do_nothing_stmt)
                        db.commit()
                        print(f"Upserted {len(records)} new records into the database.")

            print(f"Loading data for {self.ticker} from {self.start_date} to {self.end_date} from database...")
            query = db.query(StockPrice).filter(
                StockPrice.ticker == self.ticker,
                StockPrice.date.between(self.start_date, self.end_date)
            ).statement
            
            self.df = pd.read_sql(query, db.get_bind(), index_col='id')
            
            if self.df.empty:
                print(f"Warning: No data found for {self.ticker} in the database for the specified date range.")
                return False

            column_mapping = { 'date': 'Date', 'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume' }
            self.df.rename(columns=column_mapping, inplace=True)
            self.df['Date'] = pd.to_datetime(self.df['Date'])

            print("Data loaded from DB and standardized for analysis.")
            return True
        finally:
            db.close()

    def get_data(self):
        # We must return a copy, otherwise later modules can accidentally change the original
        return self.df.copy() if self.df is not None else pd.DataFrame()