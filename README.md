\# 🤖 AI Data Analyst Copilot



> \*\*An LLM-powered business analytics assistant that combines Natural Language SQL, RAG, intelligent query routing, and automated data visualization.\*\*



The \*\*AI Data Analyst Copilot\*\* allows users to ask business questions in natural language and receive answers from both \*\*structured business data\*\* and \*\*unstructured company knowledge\*\*.



Unlike a traditional document-based RAG chatbot, this system can intelligently determine whether a question requires \*\*SQL analysis, RAG retrieval, or both SQL + RAG\*\*.



\---



\## 🚀 Live Demo



🔗 \*\*Streamlit App:\*\* Add your deployed Streamlit URL here



🔗 \*\*GitHub Repository:\*\* https://github.com/SushilKhairnar/AI-Data-Analyst-Project



\---



\## 🎯 Project Objective



Business information is often stored in two different forms:



\* \*\*Structured data\*\* → customers, products, orders, employees, departments

\* \*\*Unstructured data\*\* → company policies, guidelines, business rules, and documentation



Traditional SQL systems work well with structured data, while traditional RAG systems work well with documents.



This project combines both approaches into a single \*\*AI-powered analytics assistant\*\*.



Users can simply ask questions in natural language instead of manually writing SQL queries or searching through company documents.



\---



\## 🧠 System Architecture



```text

&#x20;                        USER QUESTION

&#x20;                             │

&#x20;                             ▼

&#x20;                      ┌──────────────┐

&#x20;                      │   LLM Router │

&#x20;                      └──────┬───────┘

&#x20;                             │

&#x20;              ┌──────────────┼──────────────┐

&#x20;              │              │              │

&#x20;              ▼              ▼              ▼

&#x20;            SQL             RAG            BOTH

&#x20;              │              │              │

&#x20;              ▼              ▼              ▼

&#x20;          SQLite         ChromaDB      SQL + RAG

&#x20;              │              │              │

&#x20;              └──────────────┼──────────────┘

&#x20;                             ▼

&#x20;                        Groq LLM

&#x20;                             │

&#x20;                             ▼

&#x20;                      Final Answer

&#x20;                             │

&#x20;                             ▼

&#x20;                   Chart Generation

```



\---



\## 🔥 Key Features



\### 1. Natural Language → SQL



Users can ask analytical questions without writing SQL manually.



Example:



```text

How many customers do we have?

```



The system generates the appropriate SQL query, executes it against the SQLite database, and converts the result into a natural-language response.



\---



\### 2. RAG-Based Company Knowledge



The system retrieves relevant information from company knowledge documents.



Knowledge sources include:



\* Sales Policy

\* Refund Policy

\* Customer Segmentation

\* Product Catalog Rules

\* Employee Policy

\* Business Metrics

\* Company Guidelines



The documents are processed using:



```text

TXT Documents

&#x20;     ↓

Document Loader

&#x20;     ↓

Recursive Character Text Splitter

&#x20;     ↓

Hugging Face Embeddings

&#x20;     ↓

ChromaDB

&#x20;     ↓

Similarity Search

&#x20;     ↓

Relevant Context

&#x20;     ↓

Groq LLM

&#x20;     ↓

Answer

```



\---



\### 3. Intelligent SQL / RAG / BOTH Routing



The LLM determines the appropriate processing path for the user's question.



\#### SQL



Used for questions involving structured business data.



Example:



```text

How many orders were delivered?

```



\#### RAG



Used for questions involving company policies or business knowledge.



Example:



```text

What is the company's refund policy?

```



\#### BOTH



Used when the question requires both business data and company knowledge.



Example:



```text

Which customer segment generates the highest revenue,

and what does the company say about this segment?

```



This allows the application to combine \*\*database results with retrieved business context\*\*.



\---



\## 📊 Automated Data Visualization



For analytical questions, the system can determine whether a visualization is useful.



Supported chart types include:



\* Bar Chart

\* Line Chart

\* Pie Chart

\* No Chart



Example questions:



```text

How many customers are there in each segment?

```



```text

How many orders were placed in each year?

```



The system can generate an appropriate visualization from the query result.



\---



\## 🗄️ Data Layer



The project uses CSV datasets containing business information.



\### Structured Data



```text

data/

│

├── customer\_AI.csv

├── departments\_AI.csv

├── employees\_AI.csv

├── order\_items\_AI.csv

├── orders\_AI.csv

└── products\_AI.csv

```



These CSV files are loaded into a \*\*SQLite database\*\* for analytical querying.



\### Database Tables



```text

customer

products

orders

order\_items

employees

departments

```



\---



\## 📚 Knowledge Base



The RAG knowledge base contains:



```text

knowledge/

│

├── business\_metrics.txt

├── company\_guidelines.txt

├── customer\_segmentation.txt

├── employee\_policy.txt

├── product\_catalog\_rules.txt

├── refund\_policy.txt

└── sales\_policy.txt

```



These documents provide the business context required for policy and knowledge-based questions.



\---



\## 🤖 LLM



The project uses the \*\*Groq API\*\* with:



```text

Model: openai/gpt-oss-120b

Temperature: 0

```



The LLM is responsible for:



\* Query routing

\* SQL generation

\* Business-context analysis

\* Final answer generation

\* Chart-type selection



\---



\## 🔎 RAG Pipeline



```text

Company Documents

&#x20;      ↓

TextLoader

&#x20;      ↓

RecursiveCharacterTextSplitter

&#x20;      ↓

Hugging Face Embeddings

&#x20;      ↓

ChromaDB

&#x20;      ↓

Similarity Search

&#x20;      ↓

Top-K Relevant Chunks

&#x20;      ↓

Context + User Question

&#x20;      ↓

Groq LLM

&#x20;      ↓

Final Answer

```



\### Embedding Model



```text

sentence-transformers/all-MiniLM-L6-v2

```



\### Vector Database



```text

ChromaDB

```



\### Retrieval



```text

Similarity Search

Top-K = 4

```



\---



\## 🧮 SQL Query Pipeline



```text

User Question

&#x20;     ↓

LLM

&#x20;     ↓

SQL Query Generation

&#x20;     ↓

SQLite

&#x20;     ↓

Query Result

&#x20;     ↓

LLM

&#x20;     ↓

Natural Language Answer

&#x20;     ↓

Optional Visualization

```



The SQL generation process is restricted to analytical queries and does not allow destructive database operations.



\---



\## 🛠️ Tech Stack



\### Programming



\* Python

\* SQL



\### Data Analysis



\* Pandas

\* NumPy



\### Database



\* SQLite



\### Generative AI



\* Groq

\* LLM

\* LangChain



\### RAG



\* LangChain

\* Hugging Face Embeddings

\* ChromaDB

\* Recursive Character Text Splitter



\### Visualization



\* Matplotlib



\### Application



\* Streamlit



\### Development \& Deployment



\* Git

\* GitHub

\* Streamlit Community Cloud



\---



\## 📁 Project Structure



```text

AI-Data-Analyst-Project/

│

├── data/

│   ├── customer\_AI.csv

│   ├── departments\_AI.csv

│   ├── employees\_AI.csv

│   ├── order\_items\_AI.csv

│   ├── orders\_AI.csv

│   └── products\_AI.csv

│

├── knowledge/

│   ├── business\_metrics.txt

│   ├── company\_guidelines.txt

│   ├── customer\_segmentation.txt

│   ├── employee\_policy.txt

│   ├── product\_catalog\_rules.txt

│   ├── refund\_policy.txt

│   └── sales\_policy.txt

│

├── ai\_engine.py

├── frontend.py

├── app.py

├── AI\_data\_analytics.ipynb

├── AI\_data\_analysis\_project\_LLM\_SQL.sql

├── requirements.txt

├── .gitignore

└── README.md

```



\---



\## 💻 Local Installation



\### 1. Clone the repository



```bash

git clone https://github.com/SushilKhairnar/AI-Data-Analyst-Project.git

```



\### 2. Navigate to the project



```bash

cd AI-Data-Analyst-Project

```



\### 3. Create a virtual environment



```bash

python -m venv venv

```



\### 4. Activate the environment



Windows:



```bash

venv\\Scripts\\activate

```



\### 5. Install dependencies



```bash

pip install -r requirements.txt

```



\### 6. Configure the Groq API key



Create a `.env` file:



```text

GROQ\_API\_KEY=your\_groq\_api\_key

```



> \*\*Never commit your `.env` file or API key to GitHub.\*\*



\### 7. Run the application



```bash

streamlit run frontend.py

```



\---



\## 🧪 Example Questions



\### SQL Questions



```text

How many customers do we have?

```



```text

How many employees work in the company?

```



```text

How many orders were placed in 2025?

```



```text

Which product has the highest price?

```



```text

How many customers are there in each segment?

```



\### RAG Questions



```text

What is the company's refund policy?

```



```text

What are the customer segmentation rules?

```



```text

What are the company's sales policies?

```



\### SQL + RAG Questions



```text

Which customer segment generates the highest revenue,

and what does the company say about this segment?

```



```text

Which products have the highest sales,

and what are the relevant product catalog rules?

```



\---



\## 🛡️ Safety \& Reliability



The application includes safeguards such as:



\* SQL-only analytical queries

\* Prevention of destructive SQL operations

\* Context-based RAG responses

\* Fallback response when information is unavailable

\* Secure API-key management

\* Separate database connection for each SQL execution



RAG fallback:



```text

I don't have enough information in the company knowledge base.

```



\---



\## ☁️ Deployment



The application is deployed using \*\*Streamlit Community Cloud\*\*.



Deployment flow:



```text

GitHub Repository

&#x20;      ↓

Streamlit Community Cloud

&#x20;      ↓

frontend.py

&#x20;      ↓

ai\_engine.py

&#x20;      ↓

SQLite + ChromaDB

&#x20;      ↓

Groq LLM

&#x20;      ↓

AI Data Analyst Copilot

```



The Groq API key is stored securely using Streamlit Secrets rather than being committed to the repository.



\---



\## 📌 What I Learned



Through this project, I worked with:



\* Natural Language to SQL

\* SQL query generation using LLMs

\* RAG architecture

\* Vector databases

\* Embedding models

\* Semantic similarity search

\* LLM-based routing

\* Hybrid SQL + RAG workflows

\* Automated data visualization

\* Streamlit application development

\* Git/GitHub workflow

\* Cloud deployment

\* Secure API-key management



\---



\## 👨‍💻 Author



\*\*Sushil Khairnar\*\*



Aspiring Data Analyst | Data Scientist | Python | SQL | Power BI | Machine Learning | Generative AI



\---



⭐ If you find this project interesting, feel free to explore the repository and try the live application.



