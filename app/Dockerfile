# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.12-bookworm

EXPOSE 8000

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install libpq-dev for psycopg2 python package
RUN apt-get update \
    && apt-get -y install libpq-dev gcc

# Install pip requirements
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

WORKDIR /app
COPY . /app

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

RUN chmod +X entrypoint.sh
ENTRYPOINT ["/bin/bash","entrypoint.sh"]
# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug

