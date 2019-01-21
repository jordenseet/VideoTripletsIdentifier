FROM ubuntu:bionic

RUN apt-get update \
    && apt-get install -y \
        python3-pip \
        python3-dev \
        libsm6 \
        libxrender1 \
        libxext6 \
    && rm -rf /var/cache/apt/*

WORKDIR /app
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r /app/requirements.txt

COPY . .
EXPOSE 5000
CMD ["python3", "/app/wsgi.py"]
