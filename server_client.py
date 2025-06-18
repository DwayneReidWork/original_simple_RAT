import threading
import socket
import struct
import traceback
import os

from . import packet
from . import netcomm

class Client(threading.Thread):
    def __init__(self, client_sock: socket.socket, client_addr: tuple[str, int]):
        super().__init__(daemon=True)
        self.__client_sock = client_sock
        self.__client_addr = client_addr

    def run(self):
        
        while True:
            try:
                p_type_b = self.__client_sock.recv(1)
                if len(p_type_b) == 0:
                    raise Exception("Empty packet header received.")
                p_type = packet.PacketType(struct.unpack('!B', p_type_b)[0])
            except Exception as e:
                print('Failed to receive packet type')
                traceback.print_exc()
                break

            if p_type == packet.PacketType.PING:
                print('Received ping request')
                self.__client_sock.send(packet.PingPacket().pack())
                print('Sent ping reply')
            elif p_type == packet.PacketType.READ_FILE:
                base_dir = "C:\\Users\\Dreid\\Desktop\\RAT"

                filename_len = struct.unpack('!I', netcomm.recv_expected(self.__client_sock, struct.calcsize('!I')))[0]
                print('Received filename length of', filename_len)
                if filename_len <= 0:
                    # return error
                    if not netcomm.send_all(self.__client_sock, packet.ReadFileRespPacket(-1, b"").pack()):
                        print('Failed to send error response.')
                    break
                
                filename = netcomm.recv_expected(self.__client_sock, filename_len).decode().strip()
                print('Requested file:', filename)
                filepath = os.path.join(base_dir, filename)
                print('Full Requested Path:', filepath)
                if not os.path.exists(filepath):
                    print('File not found.')
                    if not netcomm.send_all(self.__client_sock, packet.ReadFileRespPacket(-2, b"File not found").pack()):
                        print('Failed to send error response.')
                        break
                    continue
                
                try:
                    with open(filepath, 'r') as fd:
                        contents = fd.read()
                except Exception as e:
                    print('Failed to open/read file:', filename)
                    traceback.print_exc()
                    if not netcomm.send_all(self.__client_sock, packet.ReadFileRespPacket(-3, b"Failed to read file.").pack()):
                        print('Failed to send error response.')
                        break
                    continue
                
                print('Contents:', contents)
                if not netcomm.send_all(self.__client_sock, packet.ReadFileRespPacket(0, contents.encode()).pack()):
                    print('Failed to send file contents.')
                    break
            else:
                print('Unimplemented type:', p_type)
                break
        
        try:
            self.__client_sock.shutdown(socket.SHUT_RDWR)
        except:
            pass
        self.__client_sock.close()
        self.__client_sock = None
        print(f'{self.__client_addr} disconnected.')