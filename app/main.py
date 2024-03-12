import socket
import threading


def main():
    print("Logs from your program will appear here!")

    server_socket = socket.create_server(("localhost", 6379), reuse_port=True)

    def handle_client(c):
            while(True): # Keep the connection open and respond to PINGs with PONGs
                data = c.recv(1024)
                if not data:
                    break
                c.sendall(b"+PONG\r\n") 
            c.close()
    
    while True:
        client_socket, addr = server_socket.accept() # wait for client
        print('Connection from', addr)
        client_thread = threading.Thread(target=handle_client, args=(client_socket,))
        client_thread.start()
        
if __name__ == "__main__":
    main()
