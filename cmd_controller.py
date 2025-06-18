import argparse
import cmd2
import ipaddress
import struct
import socket
 

from . import netcomm, packet

def ip_type(ip_str: str) -> ipaddress.IPv4Address:
    try:
        addr = ipaddress.IPv4Address(ip_str)
        return addr
    except:
        raise Exception(f'A valid host IPv4 is required; found: {ip_str}')
    
def port_type(port_str: str) -> int:
    port = int(port_str)
    if port < 0 or port > 65535:
        raise Exception('Port must be in range [1,65535]')
    return port


class CmdController(cmd2.Cmd):
    
    def __init__(self):
        super().__init__()
        self.sock = None

    def __recv_packet_type(self, expected_type: packet.PacketType = None) -> packet.PacketType | None:
        p_resp = self.sock.recv(1)
        try:
            p_type = packet.PacketType(struct.unpack('!B', p_resp)[0])
        except:
            return None

        if expected_type is not None and p_type != expected_type:
            return None
        return p_type

    connect_parser = cmd2.Cmd2ArgumentParser()
    connect_parser.add_argument('host', action='store', type=ip_type, help='Host to connect to')
    connect_parser.add_argument('port', action='store', type=port_type, help='Port to connect to')
    
    @cmd2.with_argparser(connect_parser)
    def do_connect(self, args):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((str(args.host), args.port))        
        print(f'Connected to {str(args.host)}:{args.port}')

    def do_disconnect(self, args):
        try:
            self.sock.shutdown(socket.SHUT_RDWR)
        except:
            pass
        self.sock.close()
        self.sock = None
        print('Disconnected.')

    def do_ping(self, args):
        if self.sock is None:
            raise Exception('Not connected.')
        
        self.sock.send(packet.PingPacket().pack())

        p_type = self.__recv_packet_type(packet.PacketType.PING)
        if p_type is None:
            print('Failed to receive ping response.')
            self.do_disconnect(args)
            return

        print('Ping successful')

    read_file_parser = cmd2.Cmd2ArgumentParser()
    read_file_parser.add_argument('file', type=str, action='store', help='The file to read')

    @cmd2.with_argparser(read_file_parser)
    def do_read_file(self, args):
        if self.sock is None:
            raise Exception('Not connected.')
        
        if not netcomm.send_all(self.sock, packet.ReadFilePacket(args.file).pack()):
            raise Exception('Error in sending filename.')
        
        p_type = self.__recv_packet_type(expected_type=packet.PacketType.READ_FILE_RESP)
        if p_type is None:
            raise Exception('Failed to receive read file response type.')
        
        status, resp_len = struct.unpack('!bI', netcomm.recv_expected(self.sock, struct.calcsize('!bI')))
        data = netcomm.recv_expected(self.sock, resp_len)

        if status == 0:
            print('File contents:')
            print(data.decode())
        else:
            print('Error occured:', status, ',', data.decode())