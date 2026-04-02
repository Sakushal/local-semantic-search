import os
import psycopg2
from sentence_transformers import SentenceTransformer

# 1. SETUP - Exact same as your main.py
print("--- Starting Direct Test ---")
print("Loading Model (please wait)...")
model = SentenceTransformer('all-MiniLM-L6-v2')

DB_PARAMS = {
    "dbname": "insurance_vault",
    "user": "admin",
    "password": "your_secure_password",
    "host": "localhost",
    "port": "5432"
}

def test_everything():
    try:
        # 2. TEST DATABASE CONNECTION
        print("Connecting to Docker Database...")
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()
        print("✅ Database Connected!")

        # 3. TEST INDEXING (Check if table exists)
        cur.execute("SELECT count(*) FROM information_schema.tables WHERE table_name = 'policy_chunks';")
        if cur.fetchone()[0] == 0:
            print("⚠️ Table 'policy_chunks' does not exist yet. Run your index tool.")
        else:
            cur.execute("SELECT count(*) FROM policy_chunks;")
            print(f"✅ Found {cur.fetchone()[0]} rows in the database.")

        # 4. TEST SEARCH
        query = "accidental death"
        print(f"Testing Search for: '{query}'...")
        vector = model.encode(query).tolist()
        
        cur.execute("""
            SELECT filename, content 
            FROM policy_chunks 
            ORDER BY embedding <=> %s::vector 
            LIMIT 1;
        """, (vector,))
        
        result = cur.fetchone()
        if result:
            print(f"✅ Search Success! Found in: {result[0]}")
            print(f"Content Snippet: {result[1][:100]}...")
        else:
            print("❌ Search returned no results. Database might be empty.")

        cur.close()
        conn.close()

    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    test_everything()