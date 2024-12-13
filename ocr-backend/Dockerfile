FROM python:3.10.12
WORKDIR /app
COPY . .
#RUN pip install --no-cache-dir -r requirements.txt
RUN pip install flask flask-pymongo flask_cors google-cloud-storage pika pillow pytesseract tesseract
CMD ["python", "app.py"]