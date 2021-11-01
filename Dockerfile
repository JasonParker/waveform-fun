FROM python:3.9.1-slim

RUN mkdir -p /src
WORKDIR /src

COPY requirements.txt /

RUN pip install --upgrade pip && pip install -r requirements.txt

CMD ["python", "./main.py" 
