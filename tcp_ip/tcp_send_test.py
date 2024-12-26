import socket
import time
import threading

PORT = 50001
HOST = "127.0.0.1"


def send_command(command):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(command.encode("utf-8"))
        print(f"Sent: {command}")


def listen_for_input():
    while True:
        user_input = (
            input("Press 's' to send 'start_move' or 'c' to send 'cancel': ")
            .strip()
            .lower()
        )
        if user_input == "s":
            send_command("move_to_sofa")
        elif user_input == "c":
            send_command("cancel")
        else:
            print("Invalid input. Press 's' or 'c'.")


if __name__ == "__main__":
    # Start listening for user input
    input_thread = threading.Thread(target=listen_for_input)
    input_thread.start()
    input_thread.join()
