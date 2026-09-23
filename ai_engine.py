import os
import glob
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import PromptTemplate


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(BASE_DIR, "data")
KNOWLEDGE_DIR = os.path.join(BASE_DIR, "knowledge")
CHROMA_DIR = os.path.join(BASE_DIR, "chroma_db")
DB_PATH = os.path.join(BASE_DIR, "AI_Data_Analyst.db")


# ============================================================
# GROQ API KEY
# ============================================================

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    try:
        import streamlit as st
        api_key = st.secrets["GROQ_API_KEY"]
    except Exception:
        pass


# ============================================================
# LLM
# ============================================================

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
    api_key=api_key
)


# ============================================================
# CREATE SQLITE DATABASE FROM CSV FILES
# ============================================================

def create_database():

    connection = sqlite3.connect(DB_PATH)

    csv_tables = {
        "customer": "customer_AI.csv",
        "products": "products_AI.csv",
        "orders": "orders_AI.csv",
        "order_items": "order_items_AI.csv",
        "employees": "employees_AI.csv",
        "departments": "departments_AI.csv"
    }

    for table_name, file_name in csv_tables.items():

        file_path = os.path.join(
            DATA_DIR,
            file_name
        )

        df = pd.read_csv(file_path)

        df.to_sql(
            table_name,
            connection,
            if_exists="replace",
            index=False
        )

    connection.commit()
    connection.close()


create_database()


# ============================================================
# CREATE VECTOR STORE
# ============================================================

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


def create_vectorstore():

    vectorstore = Chroma(
        collection_name="company_knowledge",
        persist_directory=CHROMA_DIR,
        embedding_function=embeddings
    )

    existing_documents = vectorstore.get()

    if len(existing_documents["ids"]) == 0:

        files = glob.glob(
            os.path.join(
                KNOWLEDGE_DIR,
                "*.txt"
            )
        )

        documents = []

        for file in files:

            loader = TextLoader(
                file,
                encoding="utf-8"
            )

            documents.extend(
                loader.load()
            )

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )

        chunks = splitter.split_documents(
            documents
        )

        if chunks:
            vectorstore.add_documents(
                chunks
            )

    return vectorstore


vectorstore = create_vectorstore()


retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={
        "k": 4
    }
)


# ============================================================
# DATABASE SCHEMA
# ============================================================

schema = """

Database: AI_Data_Analyst

Tables:

customer
- customer_id
- name
- city
- state
- signup_date
- segment

products
- product_id
- product_name
- category
- price
- cost

orders
- order_id
- customer_id
- order_date
- status

order_items
- order_item_id
- order_id
- product_id
- quantity

employees
- employee_id
- employee_name
- department_id
- job_role
- city
- hire_date
- salary

departments
- department_id
- department_name
- manager_name
- location
- annual_budget


Relationships:

customer.customer_id = orders.customer_id

orders.order_id = order_items.order_id

products.product_id = order_items.product_id

departments.department_id = employees.department_id

"""


# ============================================================
# SQL PROMPT
# ============================================================

sql_prompt = PromptTemplate(
    input_variables=[
        "question",
        "business_context"
    ],
    template="""

You are an expert SQL analyst.

Convert the user's question into a SQLite SQL query.

DATABASE SCHEMA:

{schema}

BUSINESS CONTEXT:

{business_context}

USER QUESTION:

{question}


RULES:

1. Use only the tables and columns present in the schema.

2. Do not invent tables or columns.

3. Use JOINs when required.

4. Generate valid SQLite SQL.

5. For date filtering use SQLite functions such as:
   strftime('%Y', order_date)

6. If the question asks for highest, lowest, top, bottom,
   most, or least, return all relevant groups ordered
   appropriately unless the user explicitly asks for a
   specific number.

7. Do not use:
   INSERT
   UPDATE
   DELETE
   DROP
   ALTER
   TRUNCATE

8. Only generate SELECT queries.

9. Return ONLY the SQL query.

10. Do not provide explanations.

SQL QUERY:

"""
)


# ============================================================
# CLEAN SQL
# ============================================================

def clean_sql(query):

    query = query.strip()

    if query.startswith("```sql"):
        query = query.replace(
            "```sql",
            "",
            1
        )

    if query.startswith("```"):
        query = query.replace(
            "```",
            "",
            1
        )

    if query.endswith("```"):
        query = query[:-3]

    return query.strip()


# ============================================================
# VALIDATE SQL
# ============================================================

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


# ============================================================
# EXECUTE SQL QUERY
# ============================================================

def execute_query(query):

    connection = sqlite3.connect(DB_PATH)

    try:

        cursor = connection.cursor()

        cursor.execute(query)

        columns = [
            column[0]
            for column in cursor.description
        ]

        rows = cursor.fetchall()

        result = [
            dict(zip(columns, row))
            for row in rows
        ]

        return result

    finally:

        connection.close()


# ============================================================
# SQL ANSWER PROMPT
# ============================================================

answer_prompt = PromptTemplate(
    input_variables=[
        "question",
        "result"
    ],
    template="""

You are a data analyst.

Answer the user's question using ONLY the SQL result.

USER QUESTION:

{question}

SQL RESULT:

{result}

RULES:

1. Give a clear and concise answer.

2. Do not invent information.

3. Do not mention SQL unless necessary.

4. If multiple rows are present, summarize them clearly.

5. Use the values from the result exactly.

ANSWER:

"""
)


# ============================================================
# CHART DECISION PROMPT
# ============================================================

chart_prompt = PromptTemplate(
    input_variables=[
        "question",
        "result"
    ],
    template="""

You are a data visualization expert.

Decide whether the SQL result should be displayed
as a chart.

USER QUESTION:

{question}

SQL RESULT:

{result}


Choose ONLY one option:

BAR
LINE
PIE
NONE


Guidelines:

BAR:
Use for category comparisons.

LINE:
Use for time-based trends.

PIE:
Use for simple percentage/proportion comparisons.

NONE:
Use when a chart is not useful.

Return ONLY:

BAR

or

LINE

or

PIE

or

NONE

"""
)


# ============================================================
# DECIDE CHART
# ============================================================

def decide_chart(question, result):

    prompt = chart_prompt.format(
        question=question,
        result=result
    )

    response = llm.invoke(prompt)

    chart_type = response.content.strip().upper()

    if chart_type not in [
        "BAR",
        "LINE",
        "PIE",
        "NONE"
    ]:
        chart_type = "NONE"

    return chart_type


# ============================================================
# CREATE CHART
# ============================================================

def create_chart(
    data,
    x_column,
    y_column,
    chart_type
):

    df = pd.DataFrame(data)

    if df.empty:
        return None

    plt.figure(
        figsize=(10, 6)
    )

    if chart_type == "bar":

        plt.bar(
            df[x_column].astype(str),
            df[y_column]
        )

        plt.xlabel(x_column)
        plt.ylabel(y_column)
        plt.xticks(rotation=45)

    elif chart_type == "line":

        plt.plot(
            df[x_column].astype(str),
            df[y_column],
            marker="o"
        )

        plt.xlabel(x_column)
        plt.ylabel(y_column)
        plt.xticks(rotation=45)

    elif chart_type == "pie":

        plt.pie(
            df[y_column],
            labels=df[x_column].astype(str),
            autopct="%1.1f%%"
        )

    else:

        plt.close()

        return None

    plt.title(
        f"{y_column} by {x_column}"
    )

    plt.tight_layout()

    chart_path = os.path.join(
        BASE_DIR,
        "chart.png"
    )

    plt.savefig(
        chart_path
    )

    plt.close()

    return chart_path


# ============================================================
# GENERATE CHART
# ============================================================

def generate_chart(
    result,
    chart_type
):

    if not result:
        return None

    if chart_type == "NONE":
        return None

    columns = list(
        result[0].keys()
    )

    # --------------------------------------------------------
    # TWO COLUMNS
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # THREE COLUMNS
    # Example:
    # year | month | total_sales
    # --------------------------------------------------------

    elif len(columns) == 3:

        if (
            "year" in columns
            and
            "month" in columns
        ):

            for row in result:

                row["period"] = (
                    f"{row['year']}-"
                    f"{int(row['month']):02d}"
                )

            value_columns = [
                column
                for column in columns
                if column not in [
                    "year",
                    "month"
                ]
            ]

            if len(value_columns) == 1:

                chart_path = create_chart(
                    result,
                    "period",
                    value_columns[0],
                    "line"
                )

                return chart_path

        return None

    return None


# ============================================================
# ASK SQL QUESTION
# ============================================================

def ask_sql_question(
    question,
    business_context=""
):

    prompt = sql_prompt.format(
        schema=schema,
        business_context=business_context,
        question=question
    )

    response = llm.invoke(prompt)

    generated_sql = clean_sql(
        response.content
    )

    if not validate_sql(
        generated_sql
    ):

        return {
            "answer": "Unable to generate a valid SQL query.",
            "result": [],
            "chart_type": "NONE",
            "chart_path": None
        }

    try:

        result = execute_query(
            generated_sql
        )

    except Exception as e:

        return {
            "answer": f"SQL execution failed: {str(e)}",
            "result": [],
            "chart_type": "NONE",
            "chart_path": None
        }

    answer = llm.invoke(
        answer_prompt.format(
            question=question,
            result=result
        )
    )

    chart_type = decide_chart(
        question,
        result
    )

    chart_path = generate_chart(
        result,
        chart_type
    )

    return {
        "answer": answer.content,
        "result": result,
        "chart_type": chart_type,
        "chart_path": chart_path
    }


# ============================================================
# RAG PROMPT
# ============================================================

rag_prompt = PromptTemplate(
    input_variables=[
        "context",
        "question"
    ],
    template="""

You are a company knowledge assistant.

Answer the user's question using ONLY the provided
company knowledge base.

COMPANY KNOWLEDGE:

{context}

USER QUESTION:

{question}


RULES:

1. Use only the provided context.

2. Do not invent information.

3. Do not use outside knowledge.

4. If the answer is not present in the context,
   respond exactly:

I don't have enough information in the company knowledge base.

5. Give a clear and concise answer.


ANSWER:

"""
)


# ============================================================
# ASK RAG QUESTION
# ============================================================

def ask_rag_question(question):

    documents = retriever.invoke(
        question
    )

    if not documents:

        return (
            "I don't have enough information "
            "in the company knowledge base."
        )

    context = "\n\n".join(
        [
            document.page_content
            for document in documents
        ]
    )

    prompt = rag_prompt.format(
        context=context,
        question=question
    )

    response = llm.invoke(
        prompt
    )

    return response.content


# ============================================================
# ROUTER PROMPT
# ============================================================

router_prompt = PromptTemplate(
    input_variables=[
        "question"
    ],
    template="""

You are a question router for an AI Data Analyst system.

Classify the user's question into exactly one category:

SQL
RAG
BOTH


SQL:

Use SQL when the question requires actual company
database information such as:

- counts
- sums
- averages
- filtering
- sorting
- grouping
- customers
- products
- orders
- employees
- departments
- managers
- prices
- costs
- revenue
- profit
- margins
- sales
- dates


RAG:

Use RAG when the question asks about company
policies, rules, definitions, guidelines, or procedures.


BOTH:

Use BOTH when the question requires:

1. Actual database data

AND

2. Company-specific knowledge or policy.


Examples:

How many customers do we have?
SQL

Who is the Sales manager?
SQL

Which product has the highest price-cost difference?
SQL

Which category has the highest revenue?
SQL

What is the refund policy?
RAG

What is the refund policy and how many refunded orders do we have?
BOTH

What does completed order mean and how many completed orders are there?
BOTH

How many completed orders were placed in 2025?
BOTH

What is the refund rate for Premium customers?
BOTH


USER QUESTION:

{question}


Return ONLY:

SQL

or

RAG

or

BOTH

"""
)


# ============================================================
# ROUTE QUESTION
# ============================================================

def route_question(question):

    prompt = router_prompt.format(
        question=question
    )

    response = llm.invoke(
        prompt
    )

    route = response.content.strip().upper()

    if route not in [
        "SQL",
        "RAG",
        "BOTH"
    ]:

        route = "SQL"

    return route


# ============================================================
# BOTH QUESTION
# ============================================================

def ask_both_question(question):

    # --------------------------------------------------------
    # Retrieve company knowledge
    # --------------------------------------------------------

    documents = retriever.invoke(
        question
    )

    context = "\n\n".join(
        [
            document.page_content
            for document in documents[:2]
        ]
    )


    # --------------------------------------------------------
    # Generate SQL using business context
    # --------------------------------------------------------

    prompt = sql_prompt.format(
        schema=schema,
        business_context=context,
        question=question
    )

    response = llm.invoke(
        prompt
    )

    generated_sql = clean_sql(
        response.content
    )


    # --------------------------------------------------------
    # Validate SQL
    # --------------------------------------------------------

    if not validate_sql(
        generated_sql
    ):

        return (
            "Unable to generate a valid SQL query."
        )


    # --------------------------------------------------------
    # Execute SQL
    # --------------------------------------------------------

    try:

        result = execute_query(
            generated_sql
        )

    except Exception as e:

        return (
            f"SQL execution failed: {str(e)}"
        )


    # --------------------------------------------------------
    # Limit result for LLM
    # --------------------------------------------------------

    result_for_llm = result[:20]


    # --------------------------------------------------------
    # Final BOTH answer
    # --------------------------------------------------------

    final_prompt = PromptTemplate(
        input_variables=[
            "context",
            "question",
            "result"
        ],
        template="""

You are an AI Data Analyst assistant.

Answer the user's question using BOTH:

1. Company knowledge
2. SQL database result


COMPANY KNOWLEDGE:

{context}


SQL RESULT:

{result}


USER QUESTION:

{question}


RULES:

1. Use only the provided company knowledge
   and SQL result.

2. Do not invent information.

3. Clearly combine the policy/definition with
   the actual data when required.

4. Give a concise and easy-to-understand answer.


ANSWER:

"""
    )

    prompt = final_prompt.format(
        context=context,
        question=question,
        result=result_for_llm
    )

    response = llm.invoke(
        prompt
    )

    return response.content


# ============================================================
# MAIN QUESTION FUNCTION
# ============================================================

def ask_question(question):

    route = route_question(
        question
    )

    # --------------------------------------------------------
    # SQL
    # --------------------------------------------------------

    if route == "SQL":

        data = ask_sql_question(
            question
        )

        return data


    # --------------------------------------------------------
    # RAG
    # --------------------------------------------------------

    elif route == "RAG":

        answer = ask_rag_question(
            question
        )

        return {
            "answer": answer,
            "result": [],
            "chart_type": "NONE",
            "chart_path": None
        }


    # --------------------------------------------------------
    # BOTH
    # --------------------------------------------------------

    elif route == "BOTH":

        answer = ask_both_question(
            question
        )

        return {
            "answer": answer,
            "result": [],
            "chart_type": "NONE",
            "chart_path": None
        }