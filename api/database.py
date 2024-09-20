from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os


# database session
SQLALCHEMY_DATABASE_URL = os.getenv('DB_CONNECTION_URL')
engine = create_engine('postgresql://pg-user:%3BBAN%40535pVGfCZbl@127.0.0.1:5432/postgres')#SQLALCHEMY_DATABASE_URL
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Define the Base class for models
Base = declarative_base()


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        raise
    finally:
        db.close()