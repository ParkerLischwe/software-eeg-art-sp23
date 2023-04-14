from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer
from pythonosc.udp_client import SimpleUDPClient

# # Define a callback function to handle incoming OSC messages
# def process_eeg_signal(address, *args):
#     print(f"Received OSC message: {address} {args}")
#     #This is where we process data using mne
#     processed_data = args
#     client = SimpleUDPClient('127.0.0.1', 5005)
#     client.send_message('/PetalStream/eeg', processed_data)
#     # server_max.handle_request()
#     server_max.serve_forever()

# # Create a dispatcher and register the callback function
# dispatcher = Dispatcher()
# dispatcher.map("/PetalStream/eeg", process_eeg_signal)

# # Create a server and start listening for incoming OSC messages
# server_address = ("127.0.0.1", 1337)
# server = BlockingOSCUDPServer(server_address, dispatcher)
# client = SimpleUDPClient("127.0.0.1", 1337)
# print("Listening for incoming OSC messages...")
# # Use server.serve_forever() when streaming continuous eeg data

# server_max.serve_forever()


# # Create an OSC client object and send a message with address '/PetalStream/eeg'
# # Below the data needs to come in as a list, you may need to wrap the data in a list before sending for processing
# client.send_message('/PetalStream/eeg', [148, 1681510984, 0.966, 1887472, 0.586323, 922.851562, -951.660156, 809.570312, 754.882812, -87.890625])
# # server.handle_request()
# server.serve_forever()
# # print("Sent OSC message to /PetalStream/eeg")

"""
This script processes messages one at a time, we 
need to switch to process data continuously
Example datapoint: /PetalStream/eeg/ 148 1681510984 0.966 1887472 0.586323 922.851562 -951.660156 809.570312 754.882812 -87.890625
"""


# from pythonosc.dispatcher import Dispatcher
# from pythonosc.osc_server import BlockingOSCUDPServer

# Define a function to handle incoming OSC messages
# def handle_osc_message(address, *args):
#     # sample_id = args[0]
#     # unix_ts = args[1] + args[2]
#     # lsl_ts = args[3] + args[4]
#     # data = args[5:]
#     # print(
#     #     f'sample_id: {sample_id}, unix_ts: {unix_ts}, '
#     #     f'lsl_ts: {lsl_ts}, data: {data}'
#     # )
#     print(f"Received OSC message: {address} {args}")

# Create callback function so we know max got the message
def it_got_to_max(address, *args):
    print("Max data recieved: ", args)

# Create a dispatcher and register the callback function
dispatcher_max = Dispatcher()
dispatcher_max.map("/PetalStream/eeg", it_got_to_max)

# Create a server that represents the port max will use and start listening for incoming OSC messages
server_address_max = ("127.0.0.1", 5005)
server_max = BlockingOSCUDPServer(server_address_max, dispatcher_max)

# Define a callback function to handle incoming OSC messages
def process_eeg_signal(address, *args):
    sample_id = args[0]
    unix_ts = args[1] + args[2]
    lsl_ts = args[3] + args[4]
    data = args[5:]
    print(
        f'sample_id: {sample_id}, unix_ts: {unix_ts}, '
        f'lsl_ts: {lsl_ts}, data: {data}'
    )
    client = SimpleUDPClient('127.0.0.1', 5005)
    client.send_message('/PetalStream/eeg', data)
    # server_max.handle_request()
    server_max.serve_forever()
    # print(f"max Received OSC message: {address} {args}")

# Create a dispatcher object and register the callback function with it
dispatcher = Dispatcher()
dispatcher.map("/PetalStream/eeg", process_eeg_signal)

# Create a server object and start listening for OSC messages
server_address = ('localhost', 1337)
server = BlockingOSCUDPServer(server_address, dispatcher)
print(f"Listening for OSC messages on {server_address[0]}:{server_address[1]}...")
server.serve_forever()




