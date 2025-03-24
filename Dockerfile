FROM python:3.9-slim

WORKDIR /app

COPY main.py /app/
COPY index.html /app/
COPY message.html /app/
COPY error.html /app/

RUN mkdir /app/static
COPY static/style.css /app/static/
COPY static/logo.png /app/static/

RUN pip install pymongo

CMD ["python", "main.py"]
