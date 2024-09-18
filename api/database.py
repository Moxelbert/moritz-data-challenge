from sqlalchemy import create_engine, inspect, text
import traceback
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os


# Define the database connection URL
SQLALCHEMY_DATABASE_URL = os.getenv('DB_CONNECTION_URL', 'postgresql://pg-user:%3BBAN%40535pVGfCZbl@/postgres?host=/cloudsql/data-case-moritz-opitz:europe-west3:moritz-challenge')
#SQLALCHEMY_DATABASE_URL = os.getenv('DB_CONNECTION_URL', 'postgresql://pg-user:%3BBAN%40535pVGfCZbl@127.0.0.1:5432/postgres')

# Create the SQLAlchemy engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Create a session maker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Define the Base class for models
Base = declarative_base()


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        # Run a simple query to validate the connection
        result = db.execute(text("SELECT * from users"))
        print("Connection test passed. Query result:", result.fetchone())

        yield db
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        raise
    finally:
        db.close()