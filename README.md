# AI-Powered SQL Query Generator & Executor

Ask a database questions in plain English. The app turns the question into SQL using a local LLM (via Ollama), validates it for safety, runs it against a MySQL database you pick, and shows the results — all through a browser UI.

## Features

- **Natural language → SQL** using a local LLM (Llama 3.2 via Ollama) — no API keys, no data leaves your machine
- **Dynamic schema awareness** — the model is shown your actual table/column structure, so it isn't hardcoded to one schema
- **Multi-database support** — lists every database on your MySQL server and lets you pick which one to query
- **Safety layer** — blocks anything that isn't a SELECT statement before it ever touches your database
- **Query history** — past questions are saved locally and can be rerun with one click
- **Clean, custom-built frontend** — no framework, just HTML/CSS/JS talking to a Flask API

## Tech Stack

| Layer | Tool |
|---|---|
| LLM | Ollama (Llama 3.2, local) |
| Backend | Flask, SQLAlchemy |
| Database | MySQL |
| Frontend | HTML / CSS / JavaScript |
| Safety validation | sqlparse |

## Architecture

```
Browser (index.html)
   │  POST /query { question, database }
   ▼
Flask (app.py)
   │
   ├─► schema_utils.py  → reads live table/column structure from MySQL
   ├─► llm_query.py      → builds prompt (schema + question) → sends to Ollama
   ├─► safety.py          → rejects anything that isn't a SELECT
   └─► executor.py         → runs the validated SQL, returns rows
```

## Setup

1. Install and start [Ollama](https://ollama.com), then pull a model:
   ```bash
   ollama pull llama3.2
   ```

2. Clone the repo and install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file with your MySQL connection string:
   ```
   DB_URL="mysql+pymysql://root:yourpassword@localhost:3306/ecommerce"
   ```
   (URL-encode special characters in your password — e.g. `@` becomes `%40`)

4. Seed a sample database (optional, for demoing):
   ```bash
   python db_setup.py
   ```

5. Run the app:
   ```bash
   python app.py
   ```
   Open `http://localhost:5000`, click **List databases**, pick one, and start asking questions.

## Example questions

- "How many customers are there?"
- "What are the top 5 most expensive products?"
- "Show total revenue per product category"
- "Which city has the most customers?"

---

## Interview Talking Points

**"Walk me through how it works."**
The frontend sends the user's question and chosen database to a Flask endpoint. The backend pulls that database's live schema (table names, columns, foreign keys) via SQLAlchemy's inspector, builds a prompt combining that schema with a few-shot example set, and sends it to a local LLM through Ollama. The model returns SQL, which gets validated — only SELECT statements are allowed, and a keyword blocklist catches anything destructive — before being executed and returned as JSON.

**"Why a local model instead of an API like OpenAI/Claude?"**
Cost and privacy — it runs entirely offline with no per-query API cost, and the database schema and data never leave the machine. The trade-off is reliability: a 3B-parameter local model is more prone to malformed or off-format SQL than a frontier hosted model, which is exactly why the safety-validation layer exists as a hard requirement, not just a nice-to-have.

**"What was the hardest part to get right?"**
Two things: getting the LLM to reliably output *only* raw SQL with no explanation or markdown wrapping (solved with strict prompt instructions plus a cleanup regex as a safety net), and handling a dynamic schema so the tool isn't hardcoded to one database — the schema-extraction step runs fresh on every request, so picking a different database in the UI actually changes what the model is told about.

**"How do you handle unsafe queries?"**
Multiple layers: the prompt itself instructs SELECT-only output; `sqlparse` checks the statement type before execution; a keyword blocklist catches INSERT/UPDATE/DELETE/DROP/ALTER even if they slip through; and the DB connection itself never needs write access for this feature. Defense in depth rather than trusting the model's output alone.

**"What would you improve with more time?"**
- Row-count/result-size limits and query timeouts to prevent runaway queries on large tables
- A retry step that re-prompts the model with a stricter format if the first SQL fails to parse
- Switching between local (Ollama) and hosted (Claude/GPT) generation at runtime, so the same tool can trade off cost/privacy vs. reliability
- Read-only DB credentials enforced at the MySQL user level, not just in application code, as a second line of defense

**"Why build the frontend by hand instead of using a framework like React?"**
The UI is a single page with one core interaction loop (pick a database, ask a question, see results) — no client-side routing, no complex state to manage. Plain HTML/CSS/JS keeps it framework-free and fast to load, and it's a deliberate choice I can defend rather than a default. If the app grew multiple views or more complex state, React would be the right call.
