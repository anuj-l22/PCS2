
# Chatroom Application

This repository contains the code for a chatroom application developed in Python. The application supports multiple client connections, allowing users to communicate through messages and share files in real-time.

## Prerequisites

Before you begin, ensure you have met the following requirements:
* Python 3.6 or higher is installed on your system.
* You are using a Linux, Windows, or macOS machine.

## Installation

Clone the repository to your local machine:

```bash
git clone https://github.com/anuj-l22/PCS2.git
cd PCS2
```

## Configuration

Before running the application, you need to configure the server's IP address and the port number. This information is crucial for the clients to connect to the server.

1. **Server IP Address**: 
   - Find your IP address using `ipconfig` (on Windows) or `ifconfig` (on Linux/Mac).
   - Update the `SERVER_HOST` variable in the `server.py` file with your IP address.

2. **Port Number**:
   - The default port number is set to `12345`. If this port is in use or you prefer a different one, you can change the `SERVER_PORT` variable in both the server and client scripts to an available port number.

## Running the Application

To run the chatroom application, follow these steps:

### Start the Server

Open a terminal and execute:

```bash
python server.py
```

This will start the server on the configured IP address and port. The server will listen for incoming client connections.

### Start a Client

Open another terminal or a terminal on a different machine and execute:

```bash
python client.py <server_ip_address> -p <server_port>
```

Replace `<server_ip_address>` with the server's IP address and `<server_port>` with the port number you configured in the server script.
Note that this -p actually needs to be written , not just a placeholder . This is generally provided as argument if port changed in server code
To quit the chatroom simply write quit in the command line
The client GUI will launch, prompting you to enter a username. After entering a username, you will be able to send messages and files to other connected users.

## Features

- **Real-time Messaging**: Send and receive messages instantly with other connected clients.
- **File Sharing**: Share files directly through the chat interface.
- **Multi-client Support**: Multiple users can connect and interact simultaneously.

