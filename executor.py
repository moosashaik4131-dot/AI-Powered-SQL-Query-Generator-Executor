import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()
def run_query(sql, db_path="mysql+pymysql://root:Moosa%40123@localhost:3306/ecommerce"):
    engine = create_engine(db_path)
    with engine.connect() as conn:
        result = conn.execute(text(sql))
        rows = [dict(row._mapping) for row in result]
    return rows