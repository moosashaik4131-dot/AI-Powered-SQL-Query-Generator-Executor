import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from dotenv import load_dotenv
 
from llm_query import generate_sql
from safety import is_safe_query
from executor import run_query
 
load_dotenv()
 
app = Flask(__name__, static_folder="static")
CORS(app)
 
SYSTEM_DBS = {"information_schema", "mysql", "performance_schema", "sys"}
 
 
def get_base_url():
    """Returns the connection URL with no specific database selected,
    so we can connect to the MySQL server itself and list databases."""
    url = make_url(os.getenv("DB_URL"))
    return url.set(database=None)
 
 
def get_db_url(database_name):
    """Returns a full connection URL pointed at a specific database."""
    url = make_url(os.getenv("DB_URL"))
    return url.set(database=database_name).render_as_string(hide_password=False)
 
 
@app.route("/")
def index():
    return app.send_static_file("index.html")
 
 
@app.route("/databases", methods=["GET"])
def list_databases():
    try:
        engine = create_engine(get_base_url())
        with engine.connect() as conn:
            result = conn.execute(text("SHOW DATABASES;"))
            all_dbs = [row[0] for row in result]
        user_dbs = [d for d in all_dbs if d not in SYSTEM_DBS]
        return jsonify({"databases": user_dbs})
    except Exception as e:
        return jsonify({"error": f"Could not list databases: {str(e)}"}), 500
 
 
@app.route("/query", methods=["POST"])
def query():
    data = request.get_json()
    question = data.get("question", "").strip()
    database = data.get("database", "").strip()
 
    if not database:
        return jsonify({"error": "Select a database first."}), 400
    if not question:
        return jsonify({"error": "Question is required."}), 400
 
    db_url = get_db_url(database)
 
    try:
        sql = generate_sql(question, db_path=db_url)
    except Exception as e:
        return jsonify({"error": f"LLM generation failed: {str(e)}. Is Ollama running?"}), 500
 
    safe, message = is_safe_query(sql)
    if not safe:
        return jsonify({"sql": sql, "error": message}), 400
 
    try:
        results = run_query(sql, db_path=db_url)
    except Exception as e:
        return jsonify({"sql": sql, "error": f"Execution failed: {str(e)}"}), 500
 
    return jsonify({"sql": sql, "results": results})
 
 
if __name__ == "__main__":
    app.run(debug=True, port=5000)
