FROM python:3-slim

ADD simulator.py /
ADD measurements.csv /
ADD events.csv /
ADD alarms.csv /

RUN pip install requests

CMD [ "python", "./simulator.py" ]
