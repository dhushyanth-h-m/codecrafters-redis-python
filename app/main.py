import socket
import threading

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
             

             

    def handle_client(c):
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
            c.close()
    
    while True:
        client_socket, addr = server_socket.accept() # wait for client
        print('Connection from', addr)
        client_thread = threading.Thread(target=handle_client, args=(client_socket,))
        client_thread.start()
        
if __name__ == "__main__":
    main()
