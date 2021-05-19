import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL", "postgresql://yuzlykzozzaucx:43a5db07cb976e79c81e3a68964931b684ac0a1189f366f732675f1e76ddae1b@ec2-54-74-35-87.eu-west-1.compute.amazonaws.com:5432/dcp7445h489rkj")


engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
