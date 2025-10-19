import socket
import threading

TARGET_HOST = '127.0.0.1'
TARGET_PORT = 3306
LISTEN_HOST = '127.0.0.1'
LISTEN_PORT = 3307
BUFFER_SIZE = 65536


def forward(src: socket.socket, dst: socket.socket):
    try:
        while True:
            data = src.recv(BUFFER_SIZE)
            if not data:
                break
            dst.sendall(data)
    except Exception:
        pass
    finally:
        try:
            src.shutdown(socket.SHUT_RD)
        except Exception:
            pass
        try:
            dst.shutdown(socket.SHUT_WR)
        except Exception:
            pass


def handle_client(client_sock: socket.socket, client_addr):
    try:
        server_sock = socket.create_connection((TARGET_HOST, TARGET_PORT))
    except Exception:
        try:
            client_sock.close()
        except Exception:
            pass
        return

    t1 = threading.Thread(target=forward, args=(client_sock, server_sock), daemon=True)
    t2 = threading.Thread(target=forward, args=(server_sock, client_sock), daemon=True)
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    try:
        client_sock.close()
    except Exception:
        pass
    try:
        server_sock.close()
    except Exception:
        pass


def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((LISTEN_HOST, LISTEN_PORT))
    s.listen(128)
    print(f'Port proxy listening on {LISTEN_HOST}:{LISTEN_PORT} forwarding to {TARGET_HOST}:{TARGET_PORT}', flush=True)
    try:
        while True:
            client_sock, client_addr = s.accept()
            threading.Thread(target=handle_client, args=(client_sock, client_addr), daemon=True).start()
    except KeyboardInterrupt:
        pass
    finally:
        try:
            s.close()
        except Exception:
            pass


if __name__ == '__main__':
    main()