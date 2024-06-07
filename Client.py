import socket
import struct

# Constants for message types
MESSAGE_TYPE_REQUEST_SUBSCRIPTION = 0
MESSAGE_TYPE_REQUEST = 1
MESSAGE_TYPE_ERROR = 2
MESSAGE_TYPE_OK = 3
MESSAGE_TYPE_FULL_NAME = 4
MESSAGE_TYPE_PHONE_NUMBER = 5

# Function to send a message with header
def send_message(client_socket, message_type, am, message):
    message_length = len(message)
    header = struct.pack('!HHI', message_type, int(am), message_length)
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

    header = struct.pack('!HHI', MESSAGE_TYPE_FULL_NAME, int(am), message_length)
    lengths = struct.pack('!HHH', first_name_length, last_name_length, fathers_name_length)

    message = header + lengths + first_name_bytes + b'\x00' * padding1 + last_name_bytes + b'\x00' * padding2 + fathers_name_bytes + b'\x00' * padding3

    client_socket.sendall(message)

# Function to send phone number with header
def send_phone_number_message(client_socket, am, phone_number):
    phone_number_bytes = phone_number.encode('utf-8')
    padding = b'\x00' * 2  # 2 bytes of padding
    message_length = 18  # Without padding

    header = struct.pack('!HHI', MESSAGE_TYPE_PHONE_NUMBER, int(am), message_length)
    message = header + phone_number_bytes + padding

    client_socket.sendall(message)

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(("localhost", 54541))

    am = input("Enter AM: ")
    send_message(client_socket, MESSAGE_TYPE_REQUEST_SUBSCRIPTION, int(am), am)

    while True:
        message_type, am, request = receive_message(client_socket)
        if message_type == MESSAGE_TYPE_REQUEST:
            if request == "Full Name":
                first_name = input("Enter First Name: ")
                last_name = input("Enter Last Name: ")
                fathers_name = input("Enter Father's Name: ")
                send_full_name_message(client_socket, int(am), first_name, last_name, fathers_name)
            elif request == "Telephone Number":
                phone_number = input("Enter Phone Number: ")
                send_phone_number_message(client_socket, int(am), phone_number)
            else:
                response = input(f"Enter {request}: ")
                send_message(client_socket, MESSAGE_TYPE_REQUEST, int(am), response)
        elif message_type == MESSAGE_TYPE_ERROR:
            print("Error:", request)
            client_socket.close()
            break
        elif message_type == MESSAGE_TYPE_OK:
            print("Subscription successful!")
            client_socket.close()
            break

if __name__ == "__main__":
    main()
