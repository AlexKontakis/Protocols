import socket
import struct

# Constants for message types
MESSAGE_TYPE_REQUEST_SUBSCRIPTION = 0
MESSAGE_TYPE_REQUEST = 1
MESSAGE_TYPE_ERROR = 2
MESSAGE_TYPE_OK = 3

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

def main():
    server_address = ("localhost", 54541)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(server_address)

    # Client identification
    am = input("Enter your identification (AM): ")
    send_message(client_socket, MESSAGE_TYPE_REQUEST_SUBSCRIPTION, int(am), "Request Subscription")

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
            info = input("Enter {}: ".format(request))
            send_message(client_socket, MESSAGE_TYPE_REQUEST, am, info)

    client_socket.close()

if __name__ == "__main__":
    main()
