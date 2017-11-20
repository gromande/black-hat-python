import sys
import socket
import getopt
import threading
import subprocess

#define global variables
listen          = False
command         = False
upload          = False
execute         = ""
target          = ""
upload_dest     = ""
port            = 0

def usage():
    print("Netcat Tool\n")
    print("Usage: netcat.py -t <target_host> -p <target_port>")
    print("-l --listen              - listen on [host]:[port] for"
                                    " incoming connections")
    print("-e --execute=file_to_run - execute the given file upon"
                                    " receiving connection")
    print("-c --command             - initialize a command shell")
    print("-u --upload=destination  - upon receiving connection upload"
                                    " a file and write to [destination]")
    print("\n")
    print("Example: ")
    print("netcat.py -t 192.168.0.1 -p 5555 -l -c")
    print("netcat.py -t 192.168.0.1 -p 5555 -l -u c:\\target.exe")
    print("netcat.py -t 192.168.0.1 -p 5555 -l -e \"cat /etc/passwd\"")
    print("echo 'ABCDEFGHI' | ./netcat.py -t 192.168.0.1 -p 5555")
    sys.exit(0)

def main():
    global listen
    global command
    global upload
    global execute
    global target
    global upload_dest
    global port

    if not len(sys.argv[1:]):
        usage()

    #read the options
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hle:t:p:cu:", ["help", "listen",
            "execute", "target", "port", "command", "upload"])
    except getopt.GetoptError as err:
        print(str(err))
        usage()

    print("Options: " + str(opts))

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
        elif opt in ("-l", "--listen"):
            listen = True
        elif opt in ("-e", "--execute"):
            execute = str(arg)
        elif opt in ("-c", "--command"):
            command = True
        elif opt in ("-u", "--upload"):
            upload_dest = str(arg)
        elif opt in ("-t", "--target"):
            target = str(arg)
        elif opt in ("-p", "--port"):
            port = int(arg)
        else:
            assert False, "Unhandled Option"

    #if we are not listening, check data from stdin
    if not listen and len(target) and port > 0:
        #read in the buffer from the command line
        #this line will block so make sure to send CTRL-D
        #if you want to send data interactively
        buffer = sys.stdin.read()

        #send data off
        client_sender(buffer)
    elif listen:
        #we are going to listen and potentially do other things
        server_loop()
    else:
        assert False, "Invalid command"

def client_sender(buffer):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        #connect to target host
        client.connect((target, port))

        if len(buffer):
            print("Debug-> sending initial data: " + str(buffer))
            client.send(buffer.encode())

        while True:
            #now wait for data from target
            recv_len = 1
            response = ""

            while recv_len:
                print("Debug-> reading data")
                data = client.recv(4096)
                recv_len = len(data)
                response += data.decode()
                print("Debug-> data received. Length: " + str(recv_len))

                if recv_len < 4096:
                    break

            print("Response received: ", response)

            #wait for more input
            print("Degug-> asking for more input")
            buffer = input("")
            buffer += "\n"

            print("Debug-> sending new input: " + str(buffer))
            client.send(buffer.encode())
    except Exception as e:
        print("[*] Exception sending data: %s" % str(e))
    finally:
        client.close()

def server_loop():
    global target

    #if no target, listen on all interfaces
    if not len(target):
        target = "0.0.0.0"

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target, port))

    server.listen(5)

    while True:
        (client_socket, client_addr) = server.accept()

        #spin off a threat to handle our new client
        client_thread = threading.Thread(target=client_handler,
                                         args=(client_socket, ))
        client_thread.start()

def run_command(command):
    print("Debug-> running command: " + str(command))
    #trim the newline
    command = command.rstrip()

    #run the command and get the output back
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT,
                                         shell=True)
    except Exception as e:
        output = "Failed to execute command: %s. Exception: %s\r\n" % \
            (command, str(e))

    #send output back to client
    return output

def client_handler(client_socket):
    print("Debug-> handling client connection")
    global upload
    global execute
    global command

    #check for upload
    if len(upload_dest):
        print("Debug-> client wants to upload file")
        #read in all the bytes an upload to destination
        file_buffer = ""

        #keep reading data until none is available
        #while True:
        #    data = client_socket.recv(1024)
        #
        #    print("Debug-> read data: %s" % (data))
        #    if not data:
        #        break
        #    else:
        #        file_buffer += data.decode()

        file_buffer = client_socket.recv(1024)

        #now we take this bytes and try to write them out
        try:
            file_descriptor = open(upload_dest, "wb")
            file_descriptor.write(file_buffer)
            file_descriptor.close()

            #Acknowledge that we wrote the file out
            msg = "Successfully saved file to %s\r\n" % upload_dest
            client_socket.send(msg.encode())
        except Exception as e:
            msg = "Failed to save file to %s: %s\r\n" % (upload_dest, str(e))
            client_socket.send(msg.encode())

    #check for command execution
    if len(execute):
        print("Debug-> client wants to execute command")
        #run the command
        output = run_command(execute)

        #Error output can be a string or bytes
        client_socket.send(output)

    #now we check if a shell was requested
    if command:
        print("Debug-> client want to execute shell")
        #show a simple prompt
        client_socket.send("<BHP:#> ".encode())

        while True:
            #show a simple prompt
            #ERROR: sending prompt every time causes weird issues
            #print("Debug-> sending prompt")
            #client_socket.send("<BHP:#> ".encode())

            #now we receive until we see a linefeed
            cmd_buffer = ""
            while "\n" not in cmd_buffer:
                cmd_buffer += client_socket.recv(1024).decode()

            #send back the command output
            response = run_command(cmd_buffer)
            print("Debug-> sending back command response: " + str(response))
            client_socket.send(response)
main()
