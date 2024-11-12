import socket
import threading
import time
import kachaka_api

PORT = 50001
HOST = '0.0.0.0'
KACHAKA_IP='192.168.11.27'

client = kachaka_api.KachakaApiClient(KACHAKA_IP+":26400")

def process_command(conn, data):
    try:
        match data:
            case ["cancel"]:
             client.cancel_command()
             conn.sendall(f"Processed command: cancel".encode('utf-8'))
            case ["move", shelf, location]:
                 client.move_shelf("S01", "L01")
            case _:
                raise ValueError(f"Unknown command: {data}")
    except Exception as e:
        conn.sendall(f"Error in process_command: {e}".encode('utf-8'))
        print(f"Error in process_command: {e}")
    finally:
        conn.close()
        print("Connection closed by thread.")


def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(1)
    print("Waiting for connection...")

    while True:
        conn, addr = server_socket.accept()
        print("Connected by", addr)
        # Start a new thread to handle the connection
        threading.Thread(target=handle_connection, args=(conn,)).start()

def handle_connection(conn):
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            data_str = data.decode('utf-8')
            print("Received:", data_str)

            # Start a new thread to process the received command
            threading.Thread(target=process_command, args=(conn, data_str)).start()
    except Exception as e:
        print(f"An error occurred in handle_connection: {e}")
    finally:
        conn.close()
        print("Connection closed by main loop.")

if __name__ == "__main__":
    start_server()
