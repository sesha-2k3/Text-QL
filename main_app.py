from fastapi import FastAPI
from pydantic import BaseModel
import sqlite3
from openai import OpenAI
import os
import traceback

# --- Configure Ollama (OpenAI-compatible API) ---
os.environ["OPENAI_API_KEY"] = "none"
os.environ["OPENAI_BASE_URL"] = "http://localhost:11434/v1"
client = OpenAI()

app = FastAPI()

# --- Request model ---
class QueryRequest(BaseModel):
    question: str
    schema: str | None = None  # optional: schema info

# --- System Prompts ---
SQLCODER_PROMPT = """
You are an expert SQL query generator. 
You will be given:
- Database schema: table names, columns, data types, constraints, and sample values.
- Example queries (natural language + SQL).
- A user’s natural language question.

Your task:
1. Analyze the user’s request.
2. Use only the provided schema, column names, and metadata.
3. Generate the most accurate SQL query to answer the request.

Rules:
- Respond ONLY with SQL.
- Do not explain or add text outside of the SQL query.
- Use exact table and column names from the schema.
- Ensure queries run without syntax errors.
"""

ERROR_REASON_PROMPT = "You explain SQL errors clearly in plain language."

ERROR_FIX_PROMPT = """
You are a SQL fixer. Correct the broken SQL query based on the explanation.
Return ONLY valid SQL without backticks, comments, or extra text.
"""

# --- Agents ---
def sql_agent(question: str, schema: str | None = None) -> str:
    """Converts NL question to SQL using SQLCoder"""
    user_prompt = f"""
Schema:
{schema if schema else "(Schema not provided)"}

User question:
{question}
"""
    response = client.chat.completions.create(
        model="sqlcoder:7b",
        messages=[
            {"role": "system", "content": SQLCODER_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0
    )
    # Ollama may return `response['choices'][0]['message']['content']` or `response['response']`
    try:
        return response.choices[0].message.content.strip()
    except AttributeError:
        return response["response"].strip()

def error_reasoning_agent(sql: str, error_msg: str) -> str:
    """Explains why SQL failed"""
    response = client.chat.completions.create(
        model="sqlcoder:7b",
        messages=[
            {"role": "system", "content": ERROR_REASON_PROMPT},
            {"role": "user", "content": f"SQL: {sql}\nError: {error_msg}\nExplain the issue."}
        ],
        temperature=0.3
    )
    try:
        return response.choices[0].message.content.strip()
    except AttributeError:
        return response["response"].strip()

def error_fix_agent(sql: str, explanation: str) -> str:
    """Fixes SQL query based on error explanation"""
    response = client.chat.completions.create(
        model="sqlcoder:7b",
        messages=[
            {"role": "system", "content": ERROR_FIX_PROMPT},
            {"role": "user", "content": f"Original SQL: {sql}\nError Explanation: {explanation}\nFix the SQL."}
        ],
        temperature=0
    )
    try:
        return response.choices[0].message.content.strip()
    except AttributeError:
        return response["response"].strip()

# --- API Endpoint ---
@app.post("/query")
def handle_query(request: QueryRequest):
    try:
        question = request.question
        schema = request.schema
        sql = sql_agent(question, schema)

        # Connect to SQLite
        conn = sqlite3.connect("mydb.sqlite")
        cursor = conn.cursor()
        cursor.execute(sql)
        results = cursor.fetchall()
        conn.close()

        return {"sql": sql, "results": results}

    except Exception as e:
        # Capture original error
        error_msg = str(e)
        traceback.print_exc()  # prints full stack trace to console

        # Reason and fix
        explanation = error_reasoning_agent(sql, error_msg)
        fixed_sql = error_fix_agent(sql, explanation)

        try:
            conn = sqlite3.connect("mydb.sqlite")
            cursor = conn.cursor()
            cursor.execute(fixed_sql)
            results = cursor.fetchall()
            conn.close()
            return {
                "original_sql": sql,
                "error": error_msg,
                "explanation": explanation,
                "fixed_sql": fixed_sql,
                "results": results
            }
        except Exception as e2:
            return {
                "original_sql": sql,
                "error": error_msg,
                "explanation": explanation,
                "fixed_sql": fixed_sql,
                "fix_error": str(e2)
            }
