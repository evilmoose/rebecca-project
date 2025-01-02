import os
from dotenv import load_dotenv
import psycopg
from psycopg.rows import dict_row
from ollama import embeddings

# Load environment variables
load_dotenv()

# Database connection parameters
DB_PARAMS = {
    'dbname': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT')
}

# Database connection
conn = psycopg.connect(**DB_PARAMS, row_factory=dict_row)
cursor = conn.cursor()

# Fetch conversations without embeddings
cursor.execute("""
    SELECT id, prompt, response 
    FROM conversations
    WHERE id NOT IN (
        SELECT id 
        FROM conversations_embeddings
    )
""")
conversations = cursor.fetchall()

# Generate embeddings and insert into the embeddings table
for conversation in conversations:
    conversation_id = conversation['id']
    content = conversation['prompt'] or conversation['response']  # Use whichever is not None

    # Debugging output
    print(f"DEBUG: Processing Conversation ID {conversation_id} with Content: {content}")

    if not content or not isinstance(content, str):
        print(f"Skipping Conversation ID {conversation_id} due to invalid content.")
        continue

    try:
        # Generate embedding
        embedding_response = embeddings("nomic-embed-text:latest", content)
        print(f"DEBUG: Embedding Response: {embedding_response}")  # Debugging
        embedding = embedding_response["embedding"]

        # Insert embedding into `conversations_embeddings`
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO conversations_embeddings (id, embedding)
                VALUES (%s, %s)
                """,
                (conversation_id, embedding)
            )
        conn.commit()
        print(f"DEBUG: Successfully inserted embedding for Conversation ID {conversation_id}")

    except Exception as e:
        print(f"ERROR: Failed to process Conversation ID {conversation_id}: {e}")
        conn.rollback()  # Rollback the current transaction before continuing

# Close the connection
conn.close()
