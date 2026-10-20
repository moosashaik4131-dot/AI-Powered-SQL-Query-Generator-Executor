import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect

load_dotenv()
def get_schema_description(db_path=None):
    if db_path is None:
        db_path = os.getenv("DB_URL")
    engine = create_engine(db_path)
    inspector = inspect(engine)
    
    lines = []

    for table_name in inspector.get_table_names():
        columns = inspector.get_columns(table_name)
        fks = inspector.get_foreign_keys(table_name)

        col_descs = [f"{col['name']} ({col['type']})" for col in columns]
        lines.append(f"Table: {table_name}")
        lines.append(f"  Columns: {', '.join(col_descs)}")

        if fks:
            for fk in fks:
                lines.append(f"  Foreign Key: {fk['constrained_columns']} -> "
                              f"{fk['referred_table']}.{fk['referred_columns']}")
        lines.append("")

    return "\n".join(lines)

if __name__ == "__main__":
    print(get_schema_description())