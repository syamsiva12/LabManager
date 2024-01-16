import sys
from inventory import *
import threading
import logging

# Setting the Path
sys.path.append(r'D:/backup/PRO/')

# Define Object
stop_event = threading.Event()

# Configure the logger
logging.basicConfig(level=logging.DEBUG)
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
                return response
        except:
                logger.critical("Failed to send send data to flask server")
                return False
            
# Define Runtime for engine
def engin(interval_seconds):
    stop_event = threading.Event()
    while not stop_event.is_set():
        pipe()
        time.sleep(interval_seconds)
        
# Function For Start Engin
def start_engin(interval_seconds):
    stop_event = threading.Event()
    engine_thread = threading.Thread(target=engin, args=(interval_seconds,))
    engine_thread.start()
    return engine_thread
    
# Function For Stop Engin   
def stop_engin(instance):
    stop_event.set()   
    instance.join()
if __name__ == "__main__":
   instance = start_engin(8)
    