from sqlalchemy import create_engine, Column, Integer, String, Float, Date, MetaData, UniqueConstraint
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "postgresql://myuser:1234@localhost/stock_db"

engine= create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False,autoflush=False,bind=engine)
Base = declarative_base()

Base = declarative_base()

class StockPrice(Base):
    __tablename__ = 'stock_prices'
    id = Column(Integer, primary_key=True, index=True)
    
    # --- ADD nullable=False TO THESE COLUMNS ---
    ticker = Column(String, index=True, nullable=False)
    date = Column(Date, index=True, nullable=False)
    
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Integer)
    __table_args__ = (UniqueConstraint('ticker', 'date', name='_ticker_date_uc'),)


# A function to be called from our CLI to create the table
def init_db():
    print("Initializing database...")
    Base.metadata.create_all(bind=engine)
    print("Database initialized.")