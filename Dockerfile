FROM python:3.6

WORKDIR /app
COPY requirements.txt .
RUN pip3 install -r /app/requirements.txt

COPY . .
EXPOSE 5000
CMD ["python3", "/app/wsgi.py"]
