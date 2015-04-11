# Adapted from original code by CClement
import serial
import time


class serial_conn(object):
    """
        Class providing an i2c connection.
    """
    def __init__(self,
                 device,
                 baudrate=19200,
                 parity=serial.PARITY_NONE,
                 bytesize=8,
                 stopbits=serial.STOPBITS_TWO,
                 xonxoff=0,
                 rtscts=0,
                 timeout=500):
        """
            Initialise i2c connection object.

            Keyword arguments:
            device -- Path to device for i2c connection, e.g. /dev/ttyUSB0 if
                      USB-I2C adapter is used.
            baudrate -- Baud rate for serial connection.
            parity -- Parity bits for serial connection.
            bytesize -- Byte size for serial connection.
            stopbits -- Stop bits for serial connection.
            xonxoff -- XON/XOFF setting for serial connection.
            rtscts -- RTS/CTS setting for serial connection.
            timeout -- Timeout for serial connection.
        """
        self.conn = serial.Serial()
        self.conn.port = device
        self.conn.baudrate = baudrate
        self.conn.parity = parity
        self.conn.bytesize = bytesize
        self.conn.stopbits = stopbits
        self.conn.xonxoff = xonxoff
        self.conn.rtscts = rtscts
        self.conn.timeout = timeout

    # TODO: Set a timeout by parameter
    def send_receive(bytes_to_send, receive_bytes, read_delay=0):
        """
            Send the given bytes and wait for specified byte count to be
            returned from the write address.

            Note that this has a very long timeout.

            Keyword arguments:
            bytes_to_send -- The bytes to be sent.
            receive_bytes -- Number of bytes to receive. Will take a long time
                             then time out with an exception if not enough
                             bytes are returned.
            read_delay -- How long to wait in seconds after writing before
                          reading.

            Returns:
            List of bytes received.
        """
        # Ensure we've got a clean connection
        self.conn.close()
        self.conn.open()

        # TODO: Error checking code, when we know the exceptions
        # TODO: Check bytes_to_send it bytearray
        self.conn.write(bytes_to_send)

        time.sleep(read_delay)

        result = self.conn.read(receive_bytes)

        self.conn.close()

        return result
