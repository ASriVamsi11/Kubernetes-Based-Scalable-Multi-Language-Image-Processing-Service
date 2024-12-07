from flask import Flask, request, jsonify
from flask_cors import CORS
from google.cloud import storage
from pymongo import MongoClient
import pika
import json
import os
import uuid

app = Flask(__name__)
CORS(app)

host = "localhost"  # Hostname or IP address
port = 27017        # Port number
username = "admin"  # Root username
password = "secret" # Root password

# MongoDB configuration
MONGO_URI = f"mongodb://{username}:{password}@{host}:{port}/"
#MONGO_URI = "mongodb+srv://andavarapuvamsi3:qISi9R1HeApjKYlJ@dcscproject.puj7i.mongodb.net/"
client = MongoClient(MONGO_URI)
db = client.ocr_database
results_collection = db.results

# Google Cloud Storage configuration
#os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/asrivamsi11/dcsc_project/dcscproject-34b356ce3665.json"

GCS_BUCKET = "dcscprojectb1"
storage_client = storage.Client()

# RabbitMQ configuration
RABBITMQ_HOST = "localhost"

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    filename = file.filename
    local_path = f'/tmp/{filename}'
    file.save(local_path)

    languages = request.form.get('languages', 'eng')  # Default to English if no languages are provided
    print(f"Received languages: {languages}") 

    # Upload to Google Cloud Storage
    bucket = storage_client.bucket(GCS_BUCKET)
    blob = bucket.blob(filename)
    blob.upload_from_filename(local_path)

    task_id = str(uuid.uuid4())

    # Queue task in RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue='ocr_tasks')

    # languages = "eng+chi_sim+hin+spa"

    message = json.dumps({'task_id': task_id,'gcs_path': filename, 'languages': languages})
    channel.basic_publish(exchange='', routing_key='ocr_tasks', body=message)
    connection.close()

    return jsonify({'message': 'Task added to queue', 'task_id': task_id})

@app.route('/result/<task_id>', methods=['GET'])
def get_result(task_id):
    result = results_collection.find_one({'task_id' : task_id}, {'_id': 0})
    if not result:
        return jsonify({'error': 'Result not found'}),404
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
