# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.9-slim

EXPOSE 8080

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHON_VERSION=3.9 \
    PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=UTF-8 \
    LC_ALL=en_US.UTF-8 \
    LANG=en_US.UTF-8 \
    PIP_NO_CACHE_DIR=off

ENV SUMMARY='Platform for building and running Python $PYTHON_VERSION applications' \
    DESCRIPTION="Python $PYTHON_VERSION available as container is a base platform for \
building and running various Python $PYTHON_VERSION applications and frameworks. \
Python is an easy to learn, powerful programming language. It has efficient high-level \
data structures and a simple but effective approach to object-oriented programming. \
Python's elegant syntax and dynamic typing, together with its interpreted nature, \
make it an ideal language for scripting and rapid application development in many areas \
on most platforms.""

LABEL summary="$SUMMARY" \
      description="$DESCRIPTION" \
      responsible-party="Jason"

# Copy local code to the container image.
ENV APP_HOME /
WORKDIR $APP_HOME
COPY . /

#RUN pip install --upgrade pip && pip install -r requirements.txt

# Install production dependencies.
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "app.py" ]
