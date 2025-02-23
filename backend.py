from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import psycopg2
import os
import json
import numpy as np
from sentence_transformers import SentenceTransformer
from psycopg2.extras import Json
import dotenv
import openai
import requests


app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# PostgreSQL Connection
dotenv.load_dotenv()

# OpenAI API Key
OPENAI_API_KEY = ""

conn = psycopg2.connect(
                database="",
                host="",
                user="",
                password="",
                port=,
            )

cursor = conn.cursor()

# Load Embedding Model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


# Translate text to ASL Gloss using GPT-4o
def translate_to_asl_gloss(text):
    prompt = f"""
    Here are some examples of translations from English text to ASL gloss:
    Examples:
    Apples ==> apple
    am ==> 
    and ==> 
    be ==>
    of ==>
    video ==> movie
    image ==> picture
    conversations ==> talk
    type of ==> type
    ? ==> question
    Watch ==> see

    Translate the following English text to ASL Gloss. 
    Follow ASL grammar order: object, then subject, then verb. 
    Remove words like IS and ARE that are not present in ASL. Replace I with ME. 
    Do not add classifiers. 
    All lowercase, don't capitalize the first letter.
    And surround it with tags <gloss> and </gloss>:
    {text}
    """

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4o",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
    result = response.json()
    gloss_text = result["choices"][0]["message"]["content"]

    gloss_list = extract_gloss_list(gloss_text)
    print("Extracted ASL Gloss:", gloss_list)
    return gloss_list


# Extract ASL Gloss words from GPT response
def extract_gloss_list(gloss_text):
    gloss_words = []
    start_tag = "<gloss>"
    end_tag = "</gloss>"

    if start_tag in gloss_text and end_tag in gloss_text:
        gloss_text = gloss_text.split(start_tag)[1].split(end_tag)[0]
        gloss_words = gloss_text.split()
    return gloss_words


@socketio.on("E-REQUEST-ANIMATION")
def handle_request_animation(data):
    """Client requests animation for a sentence"""

    text = data.strip()
    if not text:
        return


    words = translate_to_asl_gloss(text)

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
                database="",
                host="",
                user="",
                password="",
                port=,
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

@app.route("/transcribe", methods=["POST"])
def transcribe_audio():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    audio_file = request.files["file"]
    try:
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}"
        }
        files = {
            "file": (audio_file.filename, audio_file, audio_file.mimetype)
        }
        data = {
            "model": "whisper-1"
        }
        response = requests.post(
            "https://api.openai.com/v1/audio/transcriptions",
            headers=headers,
            files=files,
            data=data
        )
        result = response.json()
        text = result.get("text", "")
        print("Transcribed Text:", text)
        return jsonify({"text": text})
    except Exception as e:
        print("Transcription error:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    socketio.run(app, debug=True, host="0.0.0.0", port=5005)
