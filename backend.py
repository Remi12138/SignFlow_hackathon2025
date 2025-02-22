from flask import Flask, request
from flask_socketio import SocketIO, emit
import psycopg2
import os
import json
import numpy as np
from sentence_transformers import SentenceTransformer
from psycopg2.extras import Json
import dotenv

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# PostgreSQL Connection
dotenv.load_dotenv()

conn = psycopg2.connect(
    database="asl",
    host="localhost",
    user="xxx",
    password=os.getenv("POSTGRES_PASSWORD"),
    port=5432,
)

cursor = conn.cursor()

# Load Embedding Model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

@socketio.on("E-REQUEST-ANIMATION")
def handle_request_animation(data):
    """Client requests animation for a sentence"""

    words = data.strip()
    if not words:
        return

    words = words.split()
    word_embeddings = [embedding_model.encode(word) for word in words]

    # SQL Query: Find best matching signs in one batch query
    query = """
        SELECT word, points, (embedding <=> %s) AS similarity 
        FROM sign 
        ORDER BY similarity ASC 
        LIMIT 1
    """
    
    animations = []

    # Fix: Ensure the connection is always open
    global conn, cursor
    try:
        if conn.closed:
            conn = psycopg2.connect(
                database="asl",
                host="localhost",
                user="postgres",
                password="yourpassword",
                port=5432,
            )
            cursor = conn.cursor()
    except Exception as e:
        print("Database connection error:", e)
        return
    
    for word, embedding in zip(words, word_embeddings):
        try:
            cursor.execute(query, (Json(embedding.tolist()),))
            result = cursor.fetchone()

            if result and (1 - result[2]) > 0.7:
                animations.append((word, result[1]))  # Store points
            else:
                animations.append((word, []))  # No matching word, return empty
        except psycopg2.Error as e:
            print("Query failed:", e)
            conn.rollback()
            continue  # Skip this word and try the next one

    emit("E-ANIMATION", animations)

if __name__ == "__main__":
    socketio.run(app, debug=True, host="0.0.0.0", port=5005)
