FROM python:3-slim

# CSV Simulator
ADD CSV-simulator.py /
ADD measurements.csv /
ADD events.csv /
ADD alarms.csv /

# JSON Simulator
#ADD JSON-simulator.py /
#ADD measurements.json /
#ADD events.json /
#ADD alarms.json /

RUN pip install requests

CMD [ "python", "./CSV-simulator.py" ]
#CMD [ "python", "./JSON-simulator.py" ]
