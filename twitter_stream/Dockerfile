FROM python:3

COPY requirements.txt ./

RUN pip install -r requirements.txt

ADD twitter_client.py ./
ADD twitter_stream_listeners.py ./
ADD twitter_stream_main.py ./

ENTRYPOINT ["python", "twitter_stream_main.py"]
CMD ["--help"]
