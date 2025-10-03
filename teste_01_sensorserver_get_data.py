# 
# 
# accelerometer /sensor/connect?type=android.sensor.accelerometer
# gyroscope /sensor/connect?type=android.sensor.gyroscope


import websocket
import json


def on_message(ws, message):
    d = json.loads(message)
    # values = d['values']
    # acuracia = d['accuracy']
    # datet = d['timestamp']
    # x = values[0]
    # y = values[1]
    # z = values[2]
    # print("acuracia = ", acuracia,
    #       'timestamp = ', datet,
    #       "x = ", x,
    #       "y = ", y,
    #       "z = ", z )
    print (d)

def on_error(ws, error):
    print("error occurred ", error)
    
def on_close(ws, close_code, reason):
    print("connection closed : ", reason)
    
def on_open(ws):
    print("connected")
    

def connect(url):
    ws = websocket.WebSocketApp(url,
                              on_open=on_open,
                              on_message=on_message,
                              on_error=on_error,
                              on_close=on_close)

    ws.run_forever()
 

ip =  '192.168.0.20'
port = '8080'

# sensor = 'gyroscope'
sensor = 'orientation'

# type1 = 'accelerometer'
# type2 = 'gyroscope'

connect(f"ws://{ip}:{port}/sensor/connect?type=android.sensor.{sensor}") 

# get sensor data
# connect(
#     f'ws://{ip}:{port}/sensors/connect?types=["android.sensor.{type1}",'
#                                             f'"android.sensor.{type2}"]'
#     )


# # get gps data
# ws://<ip>:<port>/gps