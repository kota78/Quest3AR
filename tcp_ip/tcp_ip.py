import socket

PORT=50001
HOST='0.0.0.0'

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(1)
    print("Waiting for connection...")

    conn, addr = server_socket.accept()
    print("Connected by", addr)

    while True:
        data = conn.recv(1024)
        if not data:
            break
        print("Received:", data.decode('utf-8'))

    conn.close()

if __name__ == "__main__":
    start_server()
