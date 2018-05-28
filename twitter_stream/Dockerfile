FROM python:3.6.5-slim-jessie

COPY requirements.txt ./

RUN pip install -r requirements.txt

COPY datastore_client.py ./
COPY twitter_client.py ./
COPY twitter_stream_listeners.py ./
COPY twitter_stream_main.py ./

ENTRYPOINT ["python", "-u", "twitter_stream_main.py"]
CMD ["--help"]
