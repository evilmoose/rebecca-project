import os
from dotenv import load_dotenv
import psycopg
from psycopg.rows import dict_row

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

# Insert sample conversations
cursor.execute(
    """
    INSERT INTO conversations (user_id, role, prompt, response, metadata)
    VALUES
        (1, 'user', 'Hi Rebecca, how are you?', '', '{"mood": "neutral"}'),  -- Set response to an empty string
        (1, 'assistant', '', 'I am doing well. How can I assist you today?', '{"mood": "neutral"}'),  -- Set prompt to an empty string
        (1, 'user', 'Tell me about space exploration.', '', '{"topic": "space"}'),
        (1, 'assistant', '', 'Space exploration is fascinating! Where would you like to start?', '{"topic": "space"}');
    """
)
conn.commit()

# Verify the data
cursor.execute("SELECT * FROM conversations;")
print(cursor.fetchall())

cursor.close()
conn.close()

