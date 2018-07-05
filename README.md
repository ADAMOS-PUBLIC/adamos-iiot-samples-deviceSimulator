# Device Simulator

This is an ADAMOS device simulator written in Python. It simulates measurements, events and alarms defined in a CSV file. You can run the script either locally or upload it as a Docker container to the ADAMOS platform.

## Defining simulation values

The python script simulator.py reads 3 different CSV files for measurements, events and alarms. It reads each file line by line, creates the corresponding object on the ADAMOS platform and waits for the amount of time (in seconds) as specified in the last parameter of each line in the CSV files. If the simulator reaches the end of each CSV file it will start reading the file again from the beginning.

### Measurements CSV file

The simulator reads a file named `measurements.csv` (if available). The file must have the folllowing structure:

`MeasurementType,MeasurementFragment,Value,Unit,TimeToWait`

`MeasurementType`=Type of the measurement (string)
`MeasurementFragment`=Fragment of the measurement (string)
`Value`=Value of the measurement (float)
`Unit`=Unit of the measurement (string)
`TimeToWait`=Amount of time (in seconds) to wait after reading the line (float)

__Example:__
`c8y_Temperature,T,12.0,C,0`

### Events CSV file

The simulator reads a file named `events.csv` (if available). The file must have the folllowing structure:

`EventType,EventText,TimeToWait`

`EventType`=Type of the event (string)
`EventText`=Description of the event (string)
`TimeToWait`=Amount of time (in seconds) to wait after reading the line (float)

__Example:__
`TestEvent,Sensor was triggered,10`

### Alarms CSV file

The simulator reads a file named `alarms.csv` (if available). The file must have the folllowing structure:

`AlarmType,AlarmText,AlarmSeverity,AlarmStatus,TimeToWait`

`AlarmType`=Type of the alarm (string)
`AlarmText`=Description of the alarm (string)
`AlarmSeverity`=Severity of the alarm (WARNING, MINOR, MAJOR, CRITICAL)
`AlarmStatus`=Severity of the alarm (ACTIVE, ACKNOWLEDGED, CLEARED)
`TimeToWait`=Amount of time (in seconds) to wait after reading the line (float)

__Example:__
`TestAlarm,I am an alarm 1,MINOR,ACTIVE,2`

__Note:__
You can update the status of an alarm by providing the same AlarmType and the new status.

## How to run the script locally

To run the script locally you need to have python 3 installed
Additionally you need to set the following environment parameters:
`C8Y_BASEURL`=URL of your ADAMOS tenant (e.g. http://<tenant>.adamos-dev.com)
`C8Y_TENANT`=Name of your ADAMOS tenant
`C8Y_USER`=User in your ADAMOS tenant that has permissions to create devices, create measurements, create events, create alarms, read alarms, update alarms
`C8Y_PASSWORD`=Password of your ADAMOS user

Now you can simply run the script on the console: `python3 simulator.py`

## How to build the docker image

You need to have docker installed on your local computer.

Open a console and move to the directory where the Dockerfile is located.
Run: `docker build . -t simulator`

## How to run the docker image locally

To run the docker image locally you need a UNIX based operating system.

Open a new console.
Run: `docker run --rm -e C8Y_BASEURL=http://<tenant>.<host>.com -e C8Y_TENANT=<tenant> -e C8Y_USER=<username> -e C8Y_PASSWORD=<password> simulator`

__Note:__ Replace `tenant`, `host`, `username` and `password` with the correct values.

## How to upload the image to the ADAMOS platform

Open a new console.
Run: `docker save simulator > image.tar`

Now create a ZIP-file containing:
- the newly craeted `image.tar` and
- the `cumulocity.json` manifest

Next upload the container to ADAMOS:
1. Open a browser window and navigate to your ADAMOS tenant. Open the Administration application.
1. Navigate to "Own appliations"
1. Click on "Add application" and select "Upload microservice"
1. Select the ZIP-file you craeted earlier
1. Click on "Subscribe" when asked if you want to subscribe to the microservice.
