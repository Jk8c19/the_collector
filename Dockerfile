FROM python:3.8-slim-buster

ENV post_qty=1
ENV subreddit_flair=mobile
ENV logging_level=info

ADD collector.py /
ADD requirements.txt /

RUN pip install -r requirements.txt

CMD [ "python", "-u", "./collector.py" ]