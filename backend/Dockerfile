FROM python:3.13-alpine

WORKDIR /app

RUN apk add --no-cache tor
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN mkdir -p /app/data

RUN systemctl enable --now tor.service

ENTRYPOINT [ "python", "main.py" ]
