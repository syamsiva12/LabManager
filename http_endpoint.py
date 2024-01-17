import sys
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import logging
sys.path.append(r'D:/backup/PRO/')
from lib import engine
import os

# Setting logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Setting mutex lock
os.environ['state'] = 'IDLE'

class SimpleRequestHandler(BaseHTTPRequestHandler):
    result = None  # Shared result variable
    stop_event_flag = None  # Shared stop_event_flag variable
    
    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header("Access-Control-Allow-Headers", "X-Requested-With")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        # Get the length of the incoming data
        content_length = int(self.headers['Content-Length'])

        # Read the incoming data
        post_data = self.rfile.read(content_length)

        # Decode the JSON data
        data = json.loads(post_data.decode('utf-8'))
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

        # Check if the request path matches the desired endpoint for starting or stopping
        if self.path == '/start_trigger':
            if os.environ['state'] == 'LOCKED':
                logger.info("Trigger in locked state...")
                logger.info("Dropping the trigger")
                
                # Send a response
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()

                response_message = "Triggered started already please wait for completeion"
                self.wfile.write(json.dumps({'message': response_message}).encode('utf-8'))
            else:               
                # Include the custom response message directly in the response body
                logger.info("Trigger lock aquired")
                os.environ['state'] = 'LOCKED'
                response_message = "Triggered Successfully"
                self.wfile.write(json.dumps({'message': response_message}).encode('utf-8'))
                # Invoke your specific function to start the engine
                engine_thread, stop_event_flag = engine.start_engin()

                # Set the shared variables
                SimpleRequestHandler.result = engine_thread
                SimpleRequestHandler.stop_event_flag = stop_event_flag

                # Send a response
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()

                # Include the custom response message directly in the response body
                response_message = "Triggered Successfully"
                self.wfile.write(json.dumps({'message': response_message}).encode('utf-8'))

        elif self.path == '/stop_trigger':
            if SimpleRequestHandler.result is None or SimpleRequestHandler.stop_event_flag is None:
                # Send a 400 response indicating that do_POST_STOP is invoked before do_POST
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()

                # Include the custom response message directly in the response body
                response_message = "Cleanup any running instance & Clearing buffer"
                self.wfile.write(json.dumps({'message': response_message}).encode('utf-8'))
                
                # Raise an exception
                raise ValueError("No Trigger Detected...")
            else:

                # Invoke your specific function to stop the engine
                engine.stop_engin(SimpleRequestHandler.result, SimpleRequestHandler.stop_event_flag)

                # Send a response
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()

                # Include the custom response message directly in the response body
                response_message = "Stopped Successfully"
                self.wfile.write(json.dumps({'message': response_message}).encode('utf-8'))
                SimpleRequestHandler.result = None
                SimpleRequestHandler.stop_event_flag = None

        else:
            # Send a 404 response for unknown paths
            self.send_response(404)
            self.end_headers()

class ThreadedHTTPServer(ThreadingHTTPServer):
    pass

def run(server_class=ThreadedHTTPServer, handler_class=SimpleRequestHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting server on port {port}...')
    httpd.serve_forever()

if __name__ == '__main__':
    run()
