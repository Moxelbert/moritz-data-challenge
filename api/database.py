from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os


# database session
SQLALCHEMY_DATABASE_URL = os.getenv('DB_CONNECTION_URL')
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Define the Base class for models
Base = declarative_base()


# dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        raise
    finally:
        db.close()