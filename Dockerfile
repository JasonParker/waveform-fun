FROM python:3.9.1-slim

#RUN mkdir -p /src
#WORKDIR /src

RUN git clone https://github.com/JasonParker/waveform-fun.git

RUN pip install --upgrade pip && pip install -r requirements.txt

CMD ["python", "./main.py" 
