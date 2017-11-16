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
    print("netcat.py -t 192.168.0.1 -p 5555 -l -u=c:\\target.exe")
    print("netcat.py -t 192.168.0.1 -p 5555 -l -e=\"cat /etc/passwd\"")
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
            execute = arg
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
main()
