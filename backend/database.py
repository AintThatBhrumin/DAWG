# backend/database.py
"""
SQLAlchemy engine and session setup.
Loads DATABASE_URL from .env using python-dotenv.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base
from dotenv import load_dotenv

load_dotenv()  # reads .env in backend/

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:504843@localhost:5432/invoice_db"
)

# Create engine (use future=True for 2.0 style)
engine = create_engine(DATABASE_URL, echo=False, future=True)

# Session factory (scoped for thread-safety)
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

# Base class for declarative models
Base = declarative_base()
