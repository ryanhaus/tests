from pymcuprog.backend import Backend, SessionConfig
from pymcuprog.toolconnection import ToolSerialConnection

sessionconfig = SessionConfig("attiny816")
transport = ToolSerialConnection(serialport="/dev/ttyUSB0", baudrate=57600)
backend = Backend()

backend.connect_to_tool(transport)

backend.start_session(sessionconfig)

device_id = backend.read_device_id()
print("ID: {0:06X}".format(int.from_bytes(device_id, byteorder="little")))
