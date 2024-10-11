import socket

def get_ip_address():
    # Get the local hostname
    hostname = socket.gethostname()
    # Get the IP address of the hostname
    ip_address = socket.gethostbyname(hostname)
    return ip_address

if __name__ == "__main__":
    ip_address = get_ip_address()
    print(f"Your IP address is: {ip_address}")
