import socket
import struct

# Function to send a message with header
def send_message(client_socket, message_type, message):
    message_length = len(message)
    header = struct.pack('!I', message_length)
    client_socket.sendall(header)
    client_socket.sendall(message_type.encode())
    client_socket.sendall(message.encode())

# Function to receive a message with header
def receive_message(client_socket):
    header = client_socket.recv(4)
    if not header:
        return None, None
    message_length = struct.unpack('!I', header)[0]
    message_type = client_socket.recv(1).decode()
    message = client_socket.recv(message_length).decode()
    return message_type, message

def main():
    server_address = ("localhost", 54541)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(server_address)

    # Client identification
    am = input("Enter your identification (AM): ")
    send_message(client_socket, "I", am)

    # Receive and send information requests
    while True:
        message_type, request = receive_message(client_socket)
        if message_type == "O":
            print("Subscription successful!")
            break
        elif message_type == "E":
            print("Server error:", request)
            break
        else:
            print("Server request:", request)
            info = input("Enter {}: ".format(request))
            send_message(client_socket, "D", info)

    client_socket.close()

if __name__ == "__main__":
    main()
