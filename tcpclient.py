import socket

target_host = "0.0.0.0"
target_port = 9999

#Create socket object
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#connect the client
client.connect((target_host, target_port))

#Send some data
client.send("Hello".encode())

#Receive some data
response = client.recv(4096)

print(response)
