from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer
from pythonosc.udp_client import SimpleUDPClient

# Define a callback function to handle incoming OSC messages
def process_eeg_signal(address, *args):
    print(f"Received OSC message: {address} {args}")
    #This is where we process data using mne
    processed_data = args
    client = SimpleUDPClient('127.0.0.1', 5005)
    client.send_message('/PetalStream/eeg', processed_data)
    server_max.handle_request()

# Create a dispatcher and register the callback function
dispatcher = Dispatcher()
dispatcher.map("/PetalStream/eeg", process_eeg_signal)

# Create a server and start listening for incoming OSC messages
server_address = ("127.0.0.1", 1337)
server = BlockingOSCUDPServer(server_address, dispatcher)
client = SimpleUDPClient("127.0.0.1", 1337)
print("Listening for incoming OSC messages...")
# Use server.serve_forever() when streaming continuous eeg data


# Define a callback function to handle incoming OSC messages
def process_max_signal(address, *args):
    print(f"max Received OSC message: {address} {args}")
    

# Create a dispatcher and register the callback function
dispatcher_max = Dispatcher()
dispatcher.map("/PetalStream/eeg", process_max_signal)

# Create a server that represents the port max will use and start listening for incoming OSC messages
server_address_max = ("127.0.0.1", 5005)
server_max = BlockingOSCUDPServer(server_address_max, dispatcher_max)


# Create an OSC client object and send a message with address '/PetalStream/eeg'
client.send_message('/PetalStream/eeg', [10., 10, 0.1, 10, 0.2, 0.3, 0.4, .5, 0.6, 0.7])
server.handle_request()
print("Sent OSC message to /PetalStream/eeg")

"""
This script processes messages one at a time, we 
need to switch to process data continuously
"""