import socket

def ping():
    s = socket.socket()
    s.connect(("example.com", 80))
    s.send(b"GET / HTTP/1.0\r\n\r\n")
    return s.recv(1024)

if __name__ == "__main__":
    print(ping())
