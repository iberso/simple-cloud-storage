FROM python:3.6-stretch
WORKDIR /code

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r /code/requirements.txt

COPY . .
CMD ["nameko", "run", "--config", "config.yml", "service"]
