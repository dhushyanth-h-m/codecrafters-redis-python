import socket
import threading
from datetime import datetime, timedelta

def main():
    print("Logs from your program will appear here!")
    server_socket = socket.create_server(("localhost", 6379), reuse_port=True)

    def read_from_parts(parts):
         stack = []
         while part := next(parts):
             if part[0] == "*":
                 length = int(part[1::])
                 array = []
                 for i in range(length):
                     intermediate = read_from_parts(parts)
                     array.append(intermediate)
                 return array
             elif part[0] == "$":
                 bulk_length = int(part[1::])
                 if bulk_length == 1:
                     return None
                 bulk_string = next(parts)
                 return bulk_string
             else:
                 return Exception("Invalid protocol")
             
    last_recorded_time = None

    def start_expiry_timer(interval, last_recorded_time=None):
        global px

        current_time = datetime.now()
        if last_recorded_time is None:
            last_recorded_time = current_time
            return False, last_recorded_time

        elapsed_time = current_time - last_recorded_time
        if elapsed_time > timedelta(milliseconds=interval):
            last_recorded_time = current_time
            return True, last_recorded_time
        else:
            return False, last_recorded_time

    def handle_client(c):
            px = None
            foo = "$-1\r\n"
            last_recorded_time = None 
            while(True): # Keep the connection open and respond to PINGs with PONGs
                data = c.recv(1024)
                if not data:
                    break

                parts = iter(data.decode().split("\r\n"))

                commands = read_from_parts(parts)

                if commands[0].lower() == "ping":
                    response_data = b"+PONG\r\n"
                    c.sendall(response_data)
                elif commands[0].lower() == "echo" and len(commands) > 1:
                         response_data = f"+{commands[1]}\r\n".encode()
                         c.sendall(response_data)
                elif commands[0].lower() == "set":
                    response_data = b"+OK\r\n"
                    foo = commands[2]
                    print(commands)
                    print(len(commands))
                    if len(commands) > 3:
                        if commands[3].lower() == "px":
                             px = int(commands[4])
                             print("Set px", px)
                             start_expiry_timer(px)
                             print(commands[3])
                    print(foo)
                    c.sendall(response_data)
                if commands[0].lower() == "get":
                    if px is None:
                        print("No px set")
                        response_data = f"${len(foo)}\r\n{foo}\r\n".encode()    
                    else:
                        print("px set")
                        expired, last_recorded_time = start_expiry_timer(px, last_recorded_time)
                        if not expired:
                            response_data = f"${len(foo)}\r\n{foo}\r\n".encode()
                        else:
                            response_data = b"$-1\r\n"
                    c.sendall(response_data)
            c.close()
    
    while True:
        client_socket, addr = server_socket.accept() 
        print('Connection from', addr)
        client_thread = threading.Thread(target=handle_client, args=(client_socket,))
        client_thread.start()
        
if __name__ == "__main__":
    main()
