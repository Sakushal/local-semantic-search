import os
import sys
import logging
import psycopg2
from mcp.server.fastmcp import FastMCP
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer

# 1. LOGGING SETUP - Directs to stderr so it doesn't break the MCP protocol
logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger("insurance-mcp")

# 2. GLOBAL MODEL VARIABLE (Starts as None for fast startup)
_model = None

def get_model():
    """Lazy-loads the AI model only when a tool is actually called."""
    global _model
    if _model is None:
        logger.info("CRITICAL: Loading AI model into system memory (all-MiniLM-L6-v2)...")
        try:
            _model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("SUCCESS: AI model is hot and ready.")
        except Exception as e:
            logger.error(f"FATAL: Model failed to load: {e}")
            raise e
    return _model

# Initialize FastMCP - matches your config name
mcp = FastMCP("insurance-intelligence")

# Database parameters - pointing to your Docker container via localhost
DB_PARAMS = {
    "dbname": "insurance_vault",
    "user": "admin",
    "password": "your_secure_password",
    "host": os.getenv("DB_HOST", "localhost"),
    "port": "5432"
}

@mcp.tool()
def search_policies(query: str):
    """Semantic search to find relevant insurance clauses from the database."""
    try:
        # Load model and vectorize
        model = get_model()
        query_vector = model.encode(query).tolist()
        
        with psycopg2.connect(**DB_PARAMS) as conn:
            with conn.cursor() as cur:
                # Ordering by Cosine Distance (<=>)
                cur.execute("""
                    SELECT filename, content 
                    FROM policy_chunks 
                    ORDER BY embedding <=> %s::vector 
                    LIMIT 3;
                """, (query_vector,))
                results = cur.fetchall()
        
        if not results:
            return "No matching clauses found. Have you run 'index_policies' yet?"
            
        return "\n\n".join([f"Source: {r[0]}\nContent: {r[1]}" for r in results])
    except Exception as e:
        return f"Search error: {str(e)}"

@mcp.tool()
def index_policies(pdf_directory: str = None):
    """Scans the policies folder and indexes them into the Postgres vector database."""
    raw_path = pdf_directory or os.getenv("PDF_PATH", "D:/______-insurance-ai/policies")
    path = raw_path.replace("\\", "/")
    
    try:
        if not os.path.exists(path):
            return f"Error: The path {path} does not exist on your machine."

        model = get_model()

        with psycopg2.connect(**DB_PARAMS) as conn:
            with conn.cursor() as cur:
                cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS policy_chunks (
                        id SERIAL PRIMARY KEY, 
                        filename TEXT, 
                        content TEXT, 
                        embedding vector(384)
                    );
                """)
                
                files = [f for f in os.listdir(path) if f.endswith('.pdf')]
                if not files:
                    return f"No PDF files found in {path}"

                count = 0
                for filename in files:
                    full_path = os.path.join(path, filename)
                    reader = PdfReader(full_path)
                    for page in reader.pages:
                        text = page.extract_text()
                        if not text or not text.strip(): continue
                        
                        clean_text = text[:1000].replace('\x00', '') 
                        vector = model.encode(clean_text).tolist()
                        
                        cur.execute(
                            "INSERT INTO policy_chunks (filename, content, embedding) VALUES (%s, %s, %s)", 
                            (filename, clean_text, vector)
                        )
                        count += 1
            conn.commit()
        return f"SUCCESS: Indexed {len(files)} files ({count} pages) into the vault."
    except Exception as e:
        return f"Indexing Error: {str(e)}"

if __name__ == "__main__":
    mcp.run()