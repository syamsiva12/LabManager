import sys
from inventory import *
import threading
import logging
import os
import logging
from http_endpoint import SimpleRequestHandler

# Setting the Path
sys.path.append(r'D:/backup/PRO/')

# Define Object
stop_event = threading.Event()

# Configure the logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define function flow
def pipe():
        sql_connect()
        try:
                logger.info("Starting Engine...")
                data = get_dev_details()
                logger.info("Successfully fetched DB")
                ping_status, up_device = check_ping(data)  
                logger.info("Ping Status Recieved")
                logger.info("Initiate SSH connection....")
                val_json,layer_info = initiate_ssh(up_device)
                ping_status = json.dumps(ping_status)
                url = "http://192.168.0.97:5000/receive_data" 
                headers = {'Content-Type': 'application/json'}
                data_to_send = {'ping_status': ping_status, 'interface_status': val_json, 'layer_info': layer_info}
                response = requests.post(url, json=data_to_send, headers=headers)
                logger.info("Recieved 200OK")
                os.environ['state'] = 'IDLE'
                logger.info("Trigger lock set IDLE")
                # Set the shared variables
                
                logger.info("Releasing trigger state")
                SimpleRequestHandler.result = None
                SimpleRequestHandler.stop_event_flag = None
                
                return response
        except:
                logger.critical("Failed to send send data to flask server")
                os.environ['state'] = 'IDLE'
                logger.info("Released Trigger Lock")
                logger.info("Releasing trigger state")
                SimpleRequestHandler.result = None
                SimpleRequestHandler.stop_event_flag = None
                return True
            
# Define Runtime for engine
def engin(interval_seconds=0):
    stop_event = threading.Event()
    while not stop_event.is_set():
        pipe()
        break
    return 1
        
# Function For Start Engin
def start_engin():
    stop_event = threading.Event()
    engine_thread = threading.Thread(target=engin, args=(1,))
    engine_thread.start()
    return engine_thread, stop_event
    
# Function For Stop Engin   
def stop_engin(instance,stop_event):
    instance.stopped = True  
    instance.join()
    return 1
    