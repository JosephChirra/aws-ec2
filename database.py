from sqlalchemy import create_engine

DATABASE_URL = (
    "postgresql://postgres:Danielchirra343@joseph-postgres-db.czu2scqkekna.ap-south-2.rds.amazonaws.com:5432/fastapi_db"
)

engine = create_engine(DATABASE_URL)

connection = engine.connect()

print("Connected Successfully")