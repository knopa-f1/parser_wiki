FROM python:3.12-slim

WORKDIR /parser_wiki

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && pip install -r requirements.txt

COPY . .

EXPOSE 8000
