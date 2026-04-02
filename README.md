\# Local Semantic Search Engine



A privacy-first document retrieval system built for local office environments. This tool uses vector embeddings to find relevant information in local documents without an internet connection.



\## 🚀 Key Features

\- \*\*100% Local:\*\* No data ever leaves the host machine.

\- \*\*Semantic Understanding:\*\* Uses `SentenceTransformers` to find documents by meaning, not just keywords.

\- \*\*Docker-Ready:\*\* One-command deployment for the database and search environment.



\## 🛠️ Technology Stack

\- \*\*Model:\*\* `all-MiniLM-L6-v2` (Sentence-Transformers)

\- \*\*Database:\*\* PostgreSQL with `pgvector`

\- \*\*Environment:\*\* Docker \& Docker-Compose



\## 📦 Setup Instructions

1\. \*\*Prepare Folders:\*\* Create a folder named `policies` and place your documents inside.

2\. \*\*Launch Database:\*\* 

```bash &#x20;  docker compose up -d    ```

3. \*\*Install Dependencies:\*\* 
```bash &#x20;  pip install -r mcp-server/requirements.txt  ```

4\. \*\*Run Search:\*\* 

```bash &#x20;  python mcp-server/direct\_test.py```







