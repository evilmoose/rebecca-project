import os
import json
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

# Connect to the database
def connect_db():
    try:
        conn = psycopg.connect(**DB_PARAMS, row_factory=dict_row)
        print(f"DEBUG: Connected to database... {conn}")
        return conn
    except psycopg.OperationalError as e:
        print(f"Database connection error: {e}")
        raise

def fetch_one(query, params):
    conn = connect_db()
    try:
        with conn.cursor() as cursor:
            print(f"DEBUG: Executing query: {query} with params: {params}")
            cursor.execute(query, params)
            result = cursor.fetchone()
            if result:
                print(f"DEBUG: Result: {result}")
                return result
            else:
                print("DEBUG: No results found.")
                return None
    finally:
        conn.close()

# General utility to fetch all rows from a query
def fetch_all(query, params):
    conn = connect_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            results = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in results]
    finally:
        conn.close()

# Fetch all conversations, ordered by timestamp
def fetch_conversations(limit=10):
    query = 'SELECT * FROM conversations ORDER BY timestamp DESC LIMIT %s'
    params = (limit,)
    return fetch_all(query, params)[::-1]  # Reverse for chronological order if needed

# Fetch conversations for a specific user
def fetch_user_conversations(user_id, limit=10):
    query = """
    SELECT prompt, response, metadata
    FROM conversations
    WHERE user_id = %s
    ORDER BY timestamp DESC
    LIMIT %s
    """
    params = (user_id, limit)
    return fetch_all(query, params)


# Store a conversation in the database
def store_conversations(user_id, role, prompt=None, response=None, metadata=None):
    """
    Store a conversation in the database and generate embeddings for it.
    """
    conn = connect_db()
    try:
        with connect_db() as conn:
            cursor = conn.cursor()

            # Default to empty JSON for metadata
            metadata = json.dumps(metadata or '{}')

            # Insert conversation into `conversations` table
            cursor.execute("""
                INSERT INTO conversations (user_id, role, prompt, response, metadata)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id;
            """, (user_id, role, prompt, response, metadata))
            conversation_id = cursor.fetchone()["id"]

            # Generate embeddings for the prompt and response
            for role, content in [('user', prompt), ('assistant', response)]:
                if content:
                    try:
                        print(f"DEBUG: Generating embedding for role '{role}' with content: {content}")
                        embedding_response = embeddings("nomic-embed-text:latest", content)

                        # Access the embedding directly
                        embedding = embedding_response.embedding  # Assuming the attribute is `embedding`
                        print(f"DEBUG: Retrieved embedding: {embedding[:10]}...")  # Print the first 10 values for debugging

                        # Insert embedding into the database
                        cursor.execute("""
                            INSERT INTO conversations_embeddings (id, embedding)
                            VALUES (%s, %s::vector)
                        """, (conversation_id, embedding))
                    except Exception as e:
                        print(f"ERROR: Embedding generation failed for role '{role}' with content '{content}': {e}")
                        continue

            conn.commit()
            print(f"DEBUG: Successfully stored conversation and embeddings for Conversation ID {conversation_id}")
    except Exception as e:
        print(f"ERROR: Failed to store conversation or generate embeddings: {e}")
    finally:
        conn.close()

# Example utility to delete a conversation (optional)
def delete_conversation(conversation_id):
    conn = connect_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute('DELETE FROM conversations WHERE id = %s', (conversation_id,))
        conn.commit()
    finally:
        conn.close()

# Example utility to update a conversation (optional)
def update_conversation(conversation_id, response=None, metadata=None):
    conn = connect_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                '''
                UPDATE conversations
                SET response = COALESCE(%s, response),
                    metadata = COALESCE(%s, metadata)
                WHERE id = %s
                ''',
                (response, json.dumps(metadata) if metadata else None, conversation_id)
            )
        conn.commit()
    finally:
        conn.close()

def get_user_id_from_username(username):
    query = "SELECT id FROM users WHERE username = %s"
    params = (username,)
    result = fetch_one(query, params)
    print(f"DEBUG: Result from fetch_one... {result}")
    return result['id'] if result else None

def find_similar_conversations(embedding_vector):
    """
    Find the most similar conversations to the provided embedding vector.
    """
    try:
        with connect_db() as conn:
            cursor = conn.cursor()

            # Explicitly cast the embedding_vector to the `vector` type
            query = """
                SELECT id, embedding <-> %s::vector AS similarity_score
                FROM conversations_embeddings
                ORDER BY similarity_score ASC
                LIMIT 5;
            """
            cursor.execute(query, (embedding_vector,))
            results = cursor.fetchall()

        print(f"DEBUG: Found similar conversations: \n{results}")
        return results
    except Exception as e:
        print(f"ERROR: Failed to find similar conversations: {e}")
        return []
