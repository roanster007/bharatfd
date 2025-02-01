# Use a Python 3.7 Alpine image as base
FROM python:3.10-alpine

# Set environment variable to ensure that Python output is sent straight to the terminal
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apk add --update --no-cache postgresql-client jpeg-dev \
    && apk add --update --no-cache --virtual .tmp-build-deps \
    gcc libc-dev linux-headers postgresql-dev musl-dev zlib zlib-dev \
    && pip install --upgrade pip

# Copy requirements file and install Python dependencies
COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

# Remove build dependencies to keep the image slim
RUN apk del .tmp-build-deps

# Copy the entire content of the current directory (bharatfd/) into the /bharatfd directory inside the container
COPY . /bharatfd/

# Set the working directory to /bharatfd inside the container
WORKDIR /bharatfd

# Expose port 8000 to access the app externally
EXPOSE 8000
