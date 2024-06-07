import socket
import struct

# Constants for message types
MESSAGE_TYPE_REQUEST_SUBSCRIPTION = 0
MESSAGE_TYPE_REQUEST = 1
MESSAGE_TYPE_ERROR = 2
MESSAGE_TYPE_OK = 3
MESSAGE_TYPE_FULL_NAME = 4

# Function to send a message with header
def send_message(client_socket, message_type, am, message):
    message_length = len(message)
    header = struct.pack('!HHI', message_type, am, message_length)
    client_socket.sendall(header + message.encode())

# Function to receive a message with header
def receive_message(client_socket):
    header = client_socket.recv(8)
    if not header:
        return None, None, None
    message_type, am, message_length = struct.unpack('!HHI', header)
    message = client_socket.recv(message_length).decode()
    return message_type, am, message

# Function to send full name with header
def send_full_name_message(client_socket, am, first_name, last_name, fathers_name):
    first_name_bytes = first_name.encode('utf-8')
    last_name_bytes = last_name.encode('utf-8')
    fathers_name_bytes = fathers_name.encode('utf-8')

    first_name_length = len(first_name_bytes)
    last_name_length = len(last_name_bytes)
    fathers_name_length = len(fathers_name_bytes)

    # Padding to ensure 32-bit alignment
    padding1 = (4 - (first_name_length % 4)) % 4
    padding2 = (4 - (last_name_length % 4)) % 4
    padding3 = (4 - (fathers_name_length % 4)) % 4

    # Total length of the message
    message_length = 8 + 6 + first_name_length + padding1 + last_name_length + padding2 + fathers_name_length + padding3

    header = struct.pack('!HHI', MESSAGE_TYPE_FULL_NAME, am, message_length)
    lengths = struct.pack('!HHH', first_name_length, last_name_length, fathers_name_length)

    message = header + lengths + first_name_bytes + b'\x00' * padding1 + last_name_bytes + b'\x00' * padding2 + fathers_name_bytes + b'\x00' * padding3

    client_socket.sendall(message)

def main():
    server_address = ("localhost", 54541)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(server_address)

    # Client identification
    am = input("Enter your identification (AM): ")
    am_int = int(am)
    send_message(client_socket, MESSAGE_TYPE_REQUEST_SUBSCRIPTION, am_int, "Request Subscription")

    # Receive and send information requests
    while True:
        message_type, am, request = receive_message(client_socket)
        if message_type == MESSAGE_TYPE_OK:
            print("Subscription successful!")
            break
        elif message_type == MESSAGE_TYPE_ERROR:
            print("Server:", request)
            if request != "Previous information needed":
                info = input("Enter {}: ".format(request))
                send_message(client_socket, MESSAGE_TYPE_REQUEST, am, info)
        elif message_type == MESSAGE_TYPE_REQUEST:
            print("Server request:", request)
            if request == "Full Name":
                first_name = input("Enter First Name: ")
                last_name = input("Enter Last Name: ")
                fathers_name = input("Enter Father's Name: ")
                send_full_name_message(client_socket, am, first_name, last_name, fathers_name)
            else:
                info = input("Enter {}: ".format(request))
                send_message(client_socket, MESSAGE_TYPE_REQUEST, am, info)

if __name__ == "__main__":
    main()
