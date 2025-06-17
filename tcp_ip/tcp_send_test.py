import socket
import threading
import time

PORT = 50001
HOST = "127.0.0.1"


def send_command(command):
    """Sends a command string to the configured host and port."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.sendall(command.encode("utf-8"))
            print(f"Sent: {command}")
    except ConnectionRefusedError:
        print(f"Error: Connection refused. Is the server running on {HOST}:{PORT}?")
    except Exception as e:
        print(f"An error occurred while sending command: {e}")


def listen_for_input():
    """Continuously listens for user input to send commands."""
    print("--- Command Sender ---")
    print("Press 's' to send 'move_to_sofa'")
    print("Press 'c' to send 'cancel'")
    print("Press 'q' to quit")
    print("----------------------")

    while True:
        user_input = input("Enter your choice: ").strip().lower()
        if user_input == "s":
            send_command("move_to_sofa")
        elif user_input == "c":
            send_command("cancel")
        elif user_input == "h":
            send_command("return_home")
        elif user_input == "q":
            print("Exiting command sender.")
            break
        else:
            print("Invalid input. Please press 's', 'c', or 'q'.")


if __name__ == "__main__":
    # Start a thread to listen for user input
    input_thread = threading.Thread(target=listen_for_input)
    input_thread.daemon = True  # Allows the thread to exit when the main program exits
    input_thread.start()

    # Keep the main thread alive to allow the input_thread to run
    while input_thread.is_alive():
        time.sleep(0.1)