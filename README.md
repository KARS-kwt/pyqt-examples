In the `scripts` folder

```bash
python -m venv env
```

Then activate the environment (command different based on terminal type)
```bash
env\Scripts\activate
```
or in a unix shell in Windows
```bash
source env/Scripts/activate
```

or on Mac/Linux
```bash
source env/bin/activate
```


And install requirements
```bash
pip install -r requirements.txt
```

## Qt GUI

Qt GUI (Using PySide or PyQt) is a very useful tool to get quick GUIs setup to interact with data coming from the robot.

| Example | Description |  Status |  
|---------|-------------|---------|
| 1       | Simple GUI  |✅      |
| 2       | Serial Connection Plotter |  To Be Tested  | 
| 3       | MQTT Connection Plotter   |  ✅  |
| 4       | OpenCV    | ✅ | 


## MQTT
Before using the mqtt pub/sub examples. A broker needs to be available. You can use online free brokers such as `broker.emqx.io` or run your own.

A simple mosquitto broker is available via docker container. cd to `mqtt/docker` and run
```
docker compose up
```