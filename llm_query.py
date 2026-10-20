SYSTEM_PROMPT_TEMPLATE = """You are a SQL generation assistant. Convert the user's
natural language question into a single valid MYSQL SELECT query.

Database schema:
{schema}

Rules:
- Only generate SELECT statements. Never generate INSERT, UPDATE, DELETE, DROP, or ALTER.
- Return ONLY the raw SQL query. No explanations, no markdown code fences, no comments.
- Use table and column names exactly as given in the schema.
- If the question cannot be answered with the given schema, return: SELECT 'UNSUPPORTED_QUERY';

Examples:
Q: How many customers are there?
A: SELECT COUNT(*) FROM customers;

Q: What are the top 5 most expensive products?
A: SELECT name, price FROM products ORDER BY price DESC LIMIT 5;

Q: Show total revenue per product category.
A: SELECT p.category, SUM(p.price * oi.quantity) AS revenue
   FROM order_items oi
   JOIN products p ON oi.product_id = p.id
   GROUP BY p.category;
"""
import os
from dotenv import load_dotenv
import ollama
import re
from schema_utils import get_schema_description

load_dotenv()

def clean_sql_output(raw_text):
    # Strip markdown fences and any stray commentary the model adds
    cleaned = re.sub(r"```sql|```", "", raw_text).strip()
    # Some local models add a leading "A:" from the few-shot pattern — strip it
    cleaned = re.sub(r"^A:\s*", "", cleaned)
    cleaned = cleaned.rstrip(";") + ";"
    return cleaned

def generate_sql(question, db_path="mysql+pymysql://root:Moosa%40123@localhost:3306/ecommerce", model="llama3.1"):
    schema = get_schema_description(db_path)
    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(schema=schema)

    response = ollama.chat(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ]
    )

    raw_sql = response["message"]["content"]
    return clean_sql_output(raw_sql)

if __name__ == "__main__":
    q = "What are the top 3 cities by number of customers?"
    print(generate_sql(q))