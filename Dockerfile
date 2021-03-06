FROM python:3

ENV post_qty=1
ENV logging_level=info

ADD collector.py /
ADD requirements.txt /

RUN pip install -r requirements.txt

CMD [ "python", "-u", "./collector.py" ]