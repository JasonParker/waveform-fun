FROM python:3.9.1-slim

COPY requirements.txt ./
#RUN mkdir -p /src
#WORKDIR /src

RUN pip install --upgrade pip && pip install -r requirements.txt

CMD ["python", "./main.py" 
