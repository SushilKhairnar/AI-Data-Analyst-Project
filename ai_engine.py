import os
import glob
import pyodbc

from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import matplotlib.pyplot as plt
from langchain_core.prompts import PromptTemplate

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
    api_key=api_key
)

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vectorstore = Chroma(
    collection_name="company_knowledge",
    persist_directory="chroma_db",
    embedding_function=embeddings
)

retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 4}
)

connection = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=HP;"
    "DATABASE=AI_Data_Analyst;"
    "Trusted_Connection=yes;"
)

def execute_query(query):
    cursor = connection.cursor()
    cursor.execute(query)
    columns = [column[0] for column in cursor.description]
    rows = cursor.fetchall()
    result = [
        dict(zip(columns, row))
        for row in rows
    ]
    return result

sql_schema = """
Database: AI_Data_Analyst

Table: customer
Columns:
- customer_id
- name
- city
- state
- signup_date
- segment

Table: products
Columns:
- product_id
- product_name
- category
- price
- cost

Table: orders
Columns:
- order_id
- customer_id
- order_date
- status

Table: order_items
Columns:
- order_item_id
- order_id
- product_id
- quantity

Table: employees
Columns:
- employee_id
- employee_name
- department_id
- job_role
- city
- hire_date
- salary

Table: departments
Columns:
- department_id
- department_name
- manager_name
- location
- annual_budget

Relationships:
- customer.customer_id = orders.customer_id
- orders.order_id = order_items.order_id
- products.product_id = order_items.product_id
- departments.department_id = employees.department_id
"""

sql_prompt = PromptTemplate(
    template="""
You are an AI Data Analyst for ABC Retail Pvt. Ltd.

Your task is to convert the user's question into a SQL Server query.

Use only the tables and columns provided in the database schema.

Database Schema:
{schema}

Business Context:
{business_context}

Rules:
1. Generate SQL Server syntax.
2. Use only the tables and columns from the schema.
3. Use JOINs when data is required from multiple tables.
4. Use the Business Context when the question depends on a company-specific definition, policy, or rule.
5. Do not make up table names or column names.
6. Return only the SQL query.
7. Do not include explanations.
8. Do not use INSERT, UPDATE, DELETE, DROP, ALTER, or TRUNCATE.
9. If the user asks for the highest, lowest, top, bottom, most, or least value across categories or groups, return all relevant groups ordered by the requested metric instead of using TOP 1 or TOP N, unless the user explicitly asks for a specific number of results.

User Question:
{question}

SQL Query:
""",
    input_variables=["schema", "business_context", "question"]
)

answer_prompt = PromptTemplate(
    template="""
You are an AI Data Analyst for ABC Retail Pvt. Ltd.

Answer the user's question using the SQL result provided below.

User Question:
{question}

SQL Query:
{sql}

SQL Result:
{result}

Rules:
1. Give a clear and concise answer.
2. Use only the SQL result.
3. Do not make up any information.
4. Do not explain the SQL query unless necessary.
5. If the result is a number, explain what that number represents.

Answer:
""",
    input_variables=["question", "sql", "result"]
)

def clean_sql(query):

    query = query.strip()

    if query.startswith("```sql"):
        query = query.replace("```sql", "", 1)

    if query.endswith("```"):
        query = query[:-3]

    return query.strip()

def validate_sql(query):

    query = query.strip().lower()

    forbidden_keywords = [
        "insert",
        "update",
        "delete",
        "drop",
        "alter",
        "truncate"
    ]

    if not query.startswith("select"):
        return False

    for keyword in forbidden_keywords:
        if keyword in query:
            return False

    return True


chart_prompt = PromptTemplate(
    template="""
You are a chart recommendation assistant for ABC Retail Pvt. Ltd.

Decide whether the user's question and SQL result should be visualized as a chart.

Choose only one option:

BAR
LINE
PIE
NONE

Rules:

BAR:
Use for comparisons between categories.
Examples:
- Revenue by category
- Employees by department
- Top 5 products

LINE:
Use for values changing over time.
Examples:
- Monthly revenue
- Yearly sales
- Monthly orders

PIE:
Use for part-to-whole distributions.
Examples:
- Customer segment distribution
- Order status distribution

NONE:
Use when a chart is not useful, especially for:
- Simple single numbers
- Policies
- Definitions
- Procedures
- Questions that are mainly textual

User Question:
{question}

SQL Result:
{result}

Return only one word:
BAR
LINE
PIE
NONE
""",
    input_variables=["question", "result"]
)


def decide_chart(question, result):

    final_prompt = chart_prompt.format(
        question=question,
        result=result
    )
    response = llm.invoke(final_prompt)
    chart_type = response.content.strip().upper()
    return chart_type


def create_chart(data, x_column, y_column, chart_type="bar"):

    x_values = [row[x_column] for row in data]
    y_values = [float(row[y_column]) for row in data]

    if chart_type == "bar":
        plt.bar(x_values, y_values)

    elif chart_type == "line":
        plt.plot(x_values, y_values, marker="o")

    elif chart_type == "pie":
        plt.pie(
            y_values,
            labels=x_values,
            autopct="%1.1f%%"
        )

    else:
        return None

    plt.xlabel(x_column)
    plt.ylabel(y_column)
    plt.title(f"{y_column} by {x_column}")
    plt.xticks(rotation=45)
    plt.tight_layout()

    chart_path = "chart.png"

    plt.savefig(chart_path)
    plt.close()

    return chart_path

def generate_chart(question, result):
    chart_type = decide_chart(question, result)
    if chart_type == "NONE":
        return None
    columns = list(result[0].keys())
    if len(columns) == 2:
        x_column = columns[0]
        y_column = columns[1]
        chart_path = create_chart(
            result,
            x_column,
            y_column,
            chart_type.lower()
        )
        return chart_path
    elif len(columns) == 3:
        if "year" in columns and "month" in columns:
            for row in result:
                row["period"] = f"{row['year']}-{row['month']:02d}"
            chart_path = create_chart(
                result,
                "period",
                columns[2],
                "line"
            )
            return chart_path
        return None
    return None


def ask_sql_question(question, business_context=""):

    print("1. Generating SQL...")

    # Generate SQL
    final_prompt = sql_prompt.format(
        schema=sql_schema,
        business_context=business_context,
        question=question
    )

    response = llm.invoke(final_prompt)
    generated_sql = clean_sql(response.content)

    print("2. SQL generated")
    print("Generated SQL:")
    print(generated_sql)

    # Validate SQL
    if not validate_sql(generated_sql):
        return {
            "answer": "The generated SQL query is not safe.",
            "result": [],
            "chart_type": "NONE",
            "chart_path": None
        }

    print("3. Executing SQL...")

    # Execute SQL
    try:
        result = execute_query(generated_sql)
    except Exception as e:
        return {
            "answer": f"SQL execution failed: {str(e)}",
            "result": [],
            "chart_type": "NONE",
            "chart_path": None
        }

    print("4. SQL executed")
    print("SQL Result:")
    print(result)

    # Limit rows only for the final LLM answer
    if len(result) > 20:
        result_for_llm = result[:20]
    else:
        result_for_llm = result

    # Generate final answer
    final_answer_prompt = answer_prompt.format(
        question=question,
        sql=generated_sql,
        result=result_for_llm
    )

    print("5. Generating final answer...")
    answer = llm.invoke(final_answer_prompt)

    print("6. Final answer generated")

    # Decide chart
    print("7. Deciding chart...")
    chart_type = decide_chart(question, result)

    print("8. Chart decision:", chart_type)
    # Generate chart
    chart_path = generate_chart(question, result)

    print("9. Chart generated:", chart_path)
    return {
        "answer": answer.content,
        "result": result,
        "chart_type": chart_type,
        "chart_path": chart_path
    }


def ask_rag_question(question):

    # 1. Retrieve relevant company knowledge
    results = retriever.invoke(question)

    # 2. Create context from retrieved documents
    context = "\n\n".join(
        doc.page_content
        for doc in results
    )

    # 3. Generate final answer using LLM
    final_prompt = prompt.format(
        context=context,
        question=question
    )

    response = llm.invoke(final_prompt)
    return response.content

prompt = PromptTemplate(
    template="""
You are an AI Data Analyst assistant for ABC Retail Pvt. Ltd.

Answer the user's question using only the provided context.

If the answer is not available in the context, say:
"I don't have enough information in the company knowledge base."

Do not make up information.

Context:
{context}

Question:
{question}

Answer:
""",
    input_variables=["context", "question"]
)


router_prompt = PromptTemplate(
    template="""
You are a question router for an AI Data Analyst system.

Classify the user's question into one of these categories:

SQL
RAG
BOTH

SQL:
Use SQL when the question can be answered using actual data
stored in the database.

Examples include:
- counts
- sums
- averages
- filtering
- sorting
- grouping
- employee information
- department information
- manager information
- customer information
- product information
- order information
- price and cost calculations
- revenue
- profit
- margins
- sales calculations

If the required information is available directly in the database,
use SQL even if the company knowledge base also contains information
about that topic.

RAG:
Use RAG when the question asks about company policies,
rules, definitions, guidelines, procedures, or other information
stored in the company knowledge documents, and no actual database
calculation or lookup is required.

BOTH:
Use BOTH only when the question requires BOTH:
1. actual database data, AND
2. company-specific knowledge, definitions, policies, rules, or guidelines.

Examples:

Question: How many customers do we have?
Category: SQL

Question: Who is the manager of the Sales department?
Category: SQL

Question: Which products have the highest difference between price and cost?
Category: SQL

Question: Which product category generated the highest revenue?
Category: SQL

Question: What is the refund policy?
Category: RAG

Question: What are the rules for processing refunds?
Category: RAG

Question: What is the refund policy and how many refunded orders do we have?
Category: BOTH

Question: How does the company define completed orders and how many completed orders are there?
Category: BOTH

Question: How many completed orders were there in 2025?
Category: BOTH

Question: What is the refund rate for Premium customers?
Category: BOTH

Return only one word:
SQL
RAG
BOTH

User Question:
{question}

Category:
""",
    input_variables=["question"]
)

def route_question(question):

    final_prompt = router_prompt.format(
        question=question
    )
    response = llm.invoke(final_prompt)
    route = response.content.strip().upper()
    return route

def ask_both_question(question):

    # 1. Retrieve relevant company knowledge
    results = retriever.invoke(question)
    results = results[:2]
    # 2. Create RAG context
    rag_context = "\n\n".join(
        doc.page_content
        for doc in results
    )

    # 3. Generate SQL using company knowledge
    final_prompt = sql_prompt.format(
        schema=sql_schema,
        business_context=rag_context,
        question=question
    )

    print("SQL PROMPT LENGTH:", len(final_prompt))
    response = llm.invoke(final_prompt)

    generated_sql = clean_sql(response.content)
    print("Generated SQL:")
    print(generated_sql)

    # 4. Validate SQL
    if not validate_sql(generated_sql):
        return "The generated SQL query is not safe."

    # 5. Execute SQL
    try:
        sql_result = execute_query(generated_sql)

    except Exception as e:
        return f"SQL execution failed: {str(e)}"

    if len(sql_result) > 20:
        sql_result_for_llm = sql_result[:20]
    else:
        sql_result_for_llm = sql_result

    # 6. Generate final answer using RAG + SQL result
    combined_prompt = f"""
You are an AI Data Analyst for ABC Retail Pvt. Ltd.

Answer the user's question using both the company knowledge base
and the SQL database result.

User Question:
{question}

Company Knowledge Base:
{rag_context}

SQL Database Result:
{sql_result_for_llm}

Rules:
1. Use only the information provided above.
2. Do not make up information.
3. Use the company knowledge base for definitions, policies, rules,
   and business terminology.
4. Use the SQL database result for actual numbers and data.
5. Give a clear and concise answer.
6. If the SQL result contains a number, use that exact number.
7. Do not mention the SQL query unless necessary.

Final Answer:
"""
    print("COMBINED PROMPT LENGTH:", len(combined_prompt))
    final_response = llm.invoke(combined_prompt)
    return final_response.content

def ask_question(question):
    route = route_question(question)
    print("Route:", route)

    if route == "SQL":
        return ask_sql_question(question)
    elif route == "RAG":
        return ask_rag_question(question)
    elif route == "BOTH":
        return ask_both_question(question)
    else:
        return "Unable to determine the question type."