import socket
import struct
import os

def send_all(sock: socket.socket, data: bytes) -> bool:
    send_b = 0
    exp_len = len(data)
    while send_b < exp_len:
        try:
            send_b += sock.send(data[send_b:])
        except:
            return False
    return True

def recv_expected(sock: socket.socket, expected_len: int) -> bytes:
    recv_b = b''
    while len(recv_b) < expected_len:
        recv_b += sock.recv(expected_len - len(recv_b))
    return recv_b

