import threading
import socket
import argparse
import os
import sys
import time
from tkinter import filedialog, Toplevel, Canvas, Button, messagebox
import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk
import datetime

# Contribution by Abhinav is primarily for message sending and by Anuj is for file handling and sending
# Specific functions left uncommented have equal contributions by BOTH
# Help was taken to add these class and method docstrings by ChatGPT. Same holds in server
class Send(threading.Thread):
    """
    This class is responsible for sending messages from the client to the server.
    It operates in its own thread to handle outgoing messages without blocking
    the main GUI.
    """

    def __init__(self, sock, name):
        super().__init__()
        self.sock = sock
        self.name = name

    # Abhinav
    def run(self):
        """
        Continuously prompts the user for input and sends it to the server.
        Typing 'quit' will close the connection and exit the application.
        """
        while True:
            message = input("{}: ".format(self.name))
            if message.lower() == "quit":
                self.sock.sendall("QUIT".encode("utf-8"))
                break
            else:
                self.sock.sendall(f"{self.name}: {message}".encode("utf-8"))
        self.sock.close()
        print("\nQuitting....")
        os._exit(0)


class Receive(threading.Thread):
    """
    This class handles receiving data from the server. It runs in its own thread
    to receive messages and files asynchronously from the server.
    """

    def __init__(self, sock, name, messages_widget, window):
        super().__init__()
        self.sock = sock
        self.name = name
        self.messages = messages_widget
        self.window = window

    # Anuj
    def receive_file(self, filename, filesize):
        """
        Receives a file in chunks and saves it to a local directory.
        """
        filesize = int(filesize)
        path = os.path.join("received_files", filename)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            while filesize > 0:
                data = self.sock.recv(min(1024, filesize))
                if not data:
                    break
                f.write(data)
                filesize -= len(data)

    def run(self):
        """
        Listens for messages or commands from the server, processes file
        reception, and updates the GUI with incoming messages.
        """
        while True:
            message = self.sock.recv(1024).decode("utf-8")
            if message.startswith("FILE:"):
                _, filename, filesize = message.split(":")
                self.messages.insert(tk.END, f"File received: {filename.strip()}")
                self.receive_file(filename.strip(), int(filesize.strip()))
            elif message:
                self.messages.insert(tk.END, message)
            else:
                print("\nDisconnected from the server")
                self.sock.close()
                break


class Client:
    """
    The main client class that sets up the network connection, handles user
    interactions, and initializes the GUI.
    """

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.name = None
        self.messages = None

    def start(self):
        """
        Connects to the server, prompts for user name, and sets up the GUI.
        """
        print(f"Connecting to {self.host}:{self.port}")
        self.sock.connect((self.host, self.port))
        self.name = input("Enter your username: ")
        self.sock.sendall(self.name.encode("utf-8"))
        print(f"Welcome to the chat {self.name}! Ready to send messages...")
        self.setup_gui()



    # Abhinav
    def send_message(self, textInput):
        """
        Sends a message to the server.
        """
        message = textInput.get()
        textInput.delete(0, tk.END)
        self.messages.insert(tk.END, f"{self.name}: {message}")
        self.sock.sendall(f"{self.name}: {message}".encode("utf-8"))

    # Anuj
    def request_online_users(self):
        """
        Requests a list of currently online users from the server.
        """
        self.sock.sendall("GET_ONLINE_USERS".encode("utf-8"))

    # Anuj
    def send_file(self):
        """
        Opens a file dialog for file selection and sends the chosen file to the server.
        """
        file_path = filedialog.askopenfilename()
        if file_path:
            filename = os.path.basename(file_path)
            filesize = os.path.getsize(file_path)
            try:
                self.sock.sendall(f"FILE:{filename}:{filesize}".encode("utf-8"))
                time.sleep(0.5)
                with open(file_path, "rb") as f:
                    bytes_read = f.read(1024)
                    while bytes_read:
                        self.sock.sendall(bytes_read)
                        bytes_read = f.read(1024)
                print(f"File {filename} sent successfully.")
            except Exception as e:
                print("Failed to send file:", e)

    def setup_gui(self):
        """
        Sets up the graphical user interface for the chatroom client using customtkinter.
        The GUI includes a list box for messages, text input for sending messages, and buttons
        for sending messages, sending files, and showing online users. It also includes an emoji
        picker for quick emoji access.
        """
        window = ctk.CTk()
        window.title("Chatroom")
        window.geometry("800x600")

        window._set_appearance_mode("dark")
        # Message display area
        fromMessage = ctk.CTkFrame(master=window, bg_color="#313131")
        scrollBar = ctk.CTkScrollbar(master=fromMessage, width=10)
        self.messages = tk.Listbox(
            master=fromMessage,
            yscrollcommand=scrollBar.set,
            bg="#313131",
            fg="#EEEEEE",
            font=("roboto", 16),
            selectbackground="#CA3E47",
            border=0,
            highlightthickness=0,
            activestyle="none",
        )
        self.messages.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollBar.pack(side=tk.RIGHT, fill=tk.Y)
        fromMessage.grid(row=0, column=0, columnspan=4, sticky="nsew")

        # Message input area
        fromEntry = ctk.CTkFrame(master=window, bg_color="#313131")
        textInput = ctk.CTkEntry(
            master=fromEntry,
            bg_color="#282424",
            fg_color="#313131",
            font=("roboto", 14),
            placeholder_text="Enter your message here.",
        )
        textInput.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        textInput.bind("<Return>", lambda event, ti=textInput: self.send_message(ti))

        # Send message button
        btnSend = ctk.CTkButton(
            master=window,
            text="Send",
            font=("roboto", 14),
            command=lambda: self.send_message(textInput),
            bg_color="#282424",
            fg_color="#313131",
            corner_radius=10,
            hover_color="#CA3E47",
            border_color="#545c5c",
            border_width=2,
        )
        btnSend.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        # Send file button
        btnSendFile = ctk.CTkButton(
            master=window,
            text="Send File",
            font=("roboto", 14),
            command=self.send_file,
            bg_color="#282424",
            fg_color="#313131",
            corner_radius=10,
            hover_color="#CA3E47",
            border_color="#545c5c",
            border_width=2,
        )
        btnSendFile.grid(row=1, column=2, padx=10, pady=10, sticky="ew")

        # Show online users button
        btnRequestUsers = ctk.CTkButton(
            master=window,
            text="Show Online Users",
            font=("roboto", 14),
            command=self.request_online_users,
            bg_color="#282424",
            fg_color="#313131",
            corner_radius=10,
            hover_color="#CA3E47",
            border_color="#545c5c",
            border_width=2,
        )
        btnRequestUsers.grid(row=1, column=3, padx=10, pady=10, sticky="ew")

        # Emoji picker
        emoji_picker_frame = ctk.CTkFrame(
            master=window, bg_color="#242424", fg_color="#242424"
        )



        emojis = ["😊", "👍", "👎", "😂", "❤️", "😎", "🎉", "🔥", "💯"]
        for emoji in emojis:
            btn_emoji = ctk.CTkButton(
                master=emoji_picker_frame,
                text=emoji,
                font=("roboto", 14),
                command=lambda e=emoji, ti=textInput: ti.insert(tk.END, e),
                bg_color="#282424",
                fg_color="#313131",
                corner_radius=10,
                hover_color="#CA3E47",
                border_color="#545c5c",
                border_width=2,
            )
            btn_emoji.pack(side=tk.LEFT, padx=5, pady=5)
        emoji_picker_frame.grid(row=3, column=0, columnspan=4, sticky="ew")

        fromEntry.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        window.rowconfigure(0, weight=1)
        window.columnconfigure(0, weight=1)

        send_thread = Send(self.sock, self.name)
        receive_thread = Receive(self.sock, self.name, self.messages, window)
        send_thread.start()
        receive_thread.start()

        window.mainloop()


def main(host, port):
    """
    Initializes the client application with specified host and port.
    """
    client = Client(host, port)
    client.start()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chatroom Client")
    parser.add_argument("host", help="Interface the server listens at")
    parser.add_argument(
        "-p", "--port", type=int, default=12345, help="TCP port the server listens at"
    )
    args = parser.parse_args()
    main(args.host, args.port)
