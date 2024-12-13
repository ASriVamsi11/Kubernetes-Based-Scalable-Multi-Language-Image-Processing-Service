FROM python:3.10.12
WORKDIR /app
COPY . .
#RUN pip install --no-cache-dir -r requirements.txt
RUN pip install google-cloud-storage pymongo pika pillow pytesseract tesseract
CMD ["python", "worker.py"]