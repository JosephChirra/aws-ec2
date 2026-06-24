from fastapi import FastAPI
from sqlalchemy import create_engine,text

app = FastAPI()

engine = create_engine("postgresql://postgres:Danielchirra343@joseph-postgres-db.czu2scqkekna.ap-south-2.rds.amazonaws.com:5432/fastapi_db")

@app.get("/users")
def get_users():

    with engine.connect() as conn:

        result = conn.execute(
            text("SELECT * FROM users")
        )

        return [dict(row._mapping) for row in result]