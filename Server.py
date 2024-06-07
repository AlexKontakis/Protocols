import socket
import random
import struct

# Constants for message types
MESSAGE_TYPE_REQUEST_SUBSCRIPTION = 0
MESSAGE_TYPE_REQUEST = 1
MESSAGE_TYPE_ERROR = 2
MESSAGE_TYPE_OK = 3
MESSAGE_TYPE_FULL_NAME = 4

# Function to generate a random order of information requests
def generate_random_order():
    info_order = ["Full Name", "Corresponding Address", "Telephone Number"]
    random.shuffle(info_order)
    return info_order

# Function to validate AM
def validate_am(am):
    return len(am) == 5 and am.isdigit()

# Function to validate full name
def validate_full_name(first_name, last_name, fathers_name):
    return all([first_name.isalpha(), last_name.isalpha(), fathers_name.isalpha()])

# Function to validate phone number
def validate_phone_number(phone):
    return len(phone) == 10 and phone.isdigit()

# Function to validate address
def validate_address(address):
    parts = address.split(',')
    return len(parts) == 3 and all(part.strip() for part in parts)

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

# Function to receive a full name message with header
def receive_full_name_message(client_socket):
    header = client_socket.recv(8)
    if not header:
        return None, None, None
    message_type, am, message_length = struct.unpack('!HHI', header)
    remaining_bytes = message_length - 8

    # Read the lengths
    lengths = client_socket.recv(6)
    first_name_length, last_name_length, fathers_name_length = struct.unpack('!HHH', lengths)
    
    # Read the names with padding
    first_name = client_socket.recv(first_name_length).decode('utf-8')
    padding1 = (4 - (first_name_length % 4)) % 4
    client_socket.recv(padding1)  # Read and ignore the padding

    last_name = client_socket.recv(last_name_length).decode('utf-8')
    padding2 = (4 - (last_name_length % 4)) % 4
    client_socket.recv(padding2)  # Read and ignore the padding

    fathers_name = client_socket.recv(fathers_name_length).decode('utf-8')
    padding3 = (4 - (fathers_name_length % 4)) % 4
    client_socket.recv(padding3)  # Read and ignore the padding

    return message_type, am, (first_name, last_name, fathers_name)

# Function to handle client connections
def handle_client_connection(client_socket, client_address):
    print("Connection from:", client_address)
    
    # Receive client identification
    message_type, am, _ = receive_message(client_socket)
    am_str = str(am).zfill(5)
    if message_type != MESSAGE_TYPE_REQUEST_SUBSCRIPTION or not validate_am(am_str):
        send_message(client_socket, MESSAGE_TYPE_ERROR, am, "Invalid AM")
        client_socket.close()
        print("Error found: Invalid AM")
        return
    
    # Generate random order of information requests
    info_order = generate_random_order()
    
    # Request and validate information from client
    prev_info = None  # Initialize prev_info outside the loop
    for info in info_order:
        send_message(client_socket, MESSAGE_TYPE_REQUEST, am, info)
        if info == "Full Name":
            message_type, _, full_name_info = receive_full_name_message(client_socket)
            first_name, last_name, fathers_name = full_name_info
            if not validate_full_name(first_name, last_name, fathers_name):
                send_message(client_socket, MESSAGE_TYPE_ERROR, am, "Invalid Full Name")
                print("Error found: Invalid Full Name")
                client_socket.close()
                return
            else:
                print(f"Full Name received: {first_name} {last_name}, Father's Name: {fathers_name}")
        else:
            message_type, _, response = receive_message(client_socket)
            print(info + ":", response)

            # Validate client's response
            if info == "Telephone Number" and not validate_phone_number(response):
                send_message(client_socket, MESSAGE_TYPE_ERROR, am, "Invalid Phone Number")
                print("Error found: Invalid Phone Number")
                if prev_info:
                    send_message(client_socket, MESSAGE_TYPE_REQUEST, am, prev_info)
                    continue
                else:
                    client_socket.close()
                    return
            elif info == "Corresponding Address" and not validate_address(response):
                send_message(client_socket, MESSAGE_TYPE_ERROR, am, "Invalid Address")
                print("Error found: Invalid Address")
                if prev_info:
                    send_message(client_socket, MESSAGE_TYPE_REQUEST, am, prev_info)
                    continue
                else:
                    client_socket.close()
                    return

        prev_info = response  # Update prev_info with the current response


    # Send OK response and close connection
    send_message(client_socket, MESSAGE_TYPE_OK, am, "OK")
    client_socket.close()
    print("Connection closed with:", client_address)

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("localhost", 54541))
    server_socket.listen(5)

    print("Server listening on port 54541...")

    while True:
        client_socket, client_address = server_socket.accept()
        handle_client_connection(client_socket, client_address)

if __name__ == "__main__":
    main()
