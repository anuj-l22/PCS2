import threading
import socket
import datetime
import os
import time

# Contribution by Abhinav is primarily for message sending and by Anuj is for file handling and sending
# Specific functions left uncommented have equal contributions by BOTH. Error handling implemented by Anuj , code implementation by Abhinav
# Help was taken to add these class and method docstrings by ChatGPT. Same holds in client
class Server(threading.Thread):
  """
  A simple chat server implementation using sockets.
  """

  def __init__(self, host, port):
    super().__init__()
    self.curr_connections = {}
    self.host = host
    self.port = port
  
  def start_server(self):
    """
    Start the server and listen for incoming connections.
    """
    self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self.server_socket.bind((self.host, self.port))
    self.server_socket.listen(5)
    print(f"Server listening on {self.host}:{self.port}")

    try:
      while True:
        client_socket, address = self.server_socket.accept()
        print(f"Accepted connection from {address}.")
        try:
          username = client_socket.recv(1024).decode("utf-8")
          self.curr_connections[client_socket] = {
           "address": address,
           "username": username,
           "last_active": datetime.datetime.now(),
                    }
          server_socket_thread = ServerSocket(client_socket, address, self)
          server_socket_thread.start()
        except Exception as e:
          print(f"Error receiving username from {address}: {str(e)}")
          client_socket.close()
    except Exception as e:
      print(f"Error accepting connections: {str(e)}")
    finally:
      self.server_socket.close()

  def sendAll(self, message, source):
    """
    Send a message to all connected clients except the source.
    """
    for client_socket in list(self.curr_connections):
     if client_socket != source:
        try:
          client_socket.sendall(message.encode("utf-8"))
        except Exception as e:
          print(
              f"Error sending message to {self.curr_connections[client_socket]['address']}: {str(e)}"
                  )
          self.remove_connection(client_socket)
  # Anuj
  def get_online_users(self):
    """
    Get a list of usernames of online users.
    """
    online_usernames = [
      conn["username"]
      for conn in self.curr_connections.values()
      if "username" in conn
      ]
    return "ONLINE_USERS:" + ",".join(online_usernames)

  # Abhinav
  def remove_connection(self, client_socket):
    """
    Remove a connection from the server.
    """
    if client_socket in self.curr_connections:
      print(
          f"Removing connection {self.curr_connections[client_socket]['address']}"
           )
      del self.curr_connections[client_socket]
      client_socket.close()

  # Anuj
  def check_inactive_connections(self):
    """
    Check for inactive connections and remove them.
    """
    while True:
      current_time = datetime.datetime.now()
      for client_socket in list(self.curr_connections):
        if (
            current_time - self.curr_connections[client_socket]["last_active"]
           ).seconds > 300:
          print(
               f"Closing inactive connection: {self.curr_connections[client_socket]['address']}"
               )
          self.remove_connection(client_socket)
      time.sleep(60)

  # Anuj
  def broadcast_file(self, source_socket, filename, file_data):
    """
    Broadcast a file to all clients except the source.
    """
    message = f"FILE:{filename}:{len(file_data)}".encode("utf-8")
    for client_socket in list(self.curr_connections):
      if client_socket != source_socket:
        try:
          client_socket.sendall(message)
          # Pause to ensure the client is ready to receive file data
          time.sleep(0.5)
          client_socket.sendall(file_data)
        except Exception as e:
          print(
               f"Error sending file to {self.curr_connections[client_socket]['address']}: {str(e)}"
               )
          self.remove_connection(client_socket)
  
  def run(self):
    threading.Thread(target=self.check_inactive_connections, daemon=True).start()
    self.start_server()


class ServerSocket(threading.Thread):
  """
  Handle individual client connections.
  """

  def __init__(self, server_socket, address, server):
    super().__init__()
    self.server_socket = server_socket
    self.address = address
    self.server = server

  # Anuj
  def handle_file_transfer(self, initial_msg):
    """
    Handle file transfer request from clients.
    """
    _, filename, filesize = initial_msg.split(":")
    filesize = int(filesize)
    file_data = b""  # Buffer to hold the file data in memory

    # Receive the file data in chunks and store in memory
    while filesize > 0:
      data = self.server_socket.recv(min(1024, filesize))
      if not data:
        break
      file_data += data
      filesize -= len(data)

    # Broadcast the file to all clients except the sender
    self.server.broadcast_file(self.server_socket, filename, file_data)

  def run(self):
    while True:
      try:
        message = self.server_socket.recv(1024).decode("utf-8")
        if message == "GET_ONLINE_USERS":
          users_info = self.server.get_online_users()
          self.server_socket.sendall(users_info.encode("utf-8"))
        elif message.startswith("FILE:"):
          self.handle_file_transfer(message)
        elif message == "QUIT":
          print(f"Client {self.address} requested to quit.")
          self.server.remove_connection(self.server_socket)
          break
        elif message:
          self.server.sendAll(message, self.server_socket)
        else:
          break
      except Exception as e:
        self.server.remove_connection(self.server_socket)
        print(f"Error with connection {self.address}: {str(e)}")
        break


def main():
  SERVER_HOST = "172.31.41.146"
  SERVER_PORT = 12345
  server = Server(SERVER_HOST, SERVER_PORT)
  server.start_server()


if __name__ == "__main__":
    main()
