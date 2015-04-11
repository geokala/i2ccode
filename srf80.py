#! /usr/bin/env python
# Adapted from original code by CClement
from connection import py2c_conn


def srf80(i2c_device, i2c_address=0xe0, sonar_echos=1, uom='cm'):
    """
        Function for getting data from an SRF80 ultrasonic range finder.
        Also retrieves the firmware version of the device (tested with version
        10), and the light sensor level.

        Can retrieve up to 16 sonar_echos. These will be ordered from the
        closest to the furthest away.

        See http://www.robot-electronics.co.uk/htm/srf08tech.html for spec
        sheet (or the site itself under ultrasonic rangers to obtain one).

        Keyword arguments:
        i2c_device -- The device the srf80 can be accessed through, e.g.
                      /dev/ttyUSB0 if accessed through a USB-I2C converter.
        i2c_address -- I2C address of srf80.
        sonar_echos -- Number of echos to return. Max 16.
        uom -- Unit of measurement. Can be cm (centimeters), inches, or ms
               (milliseconds delay).

        Returns:
        Dict containing keys:
        firmware_version -- The version of the firmware on the srf80.
        light_level -- The light level sensed.
        unit_of_measurement -- The unit of measurement for returned distances.
        distances -- A list from nearest to furthest of echos detected.
    """
    units_of_measurement = {
        'cm': 0x51,
        'inches': 0x50,
        'ms': 0x52,
        }
    uom_code = units_of_measurement[uom]

    if sonar_echos > 16 or sonar_echos < 0:
        raise ValueError('sonar_echos must be between 0 and 16, inclusive.')

    conn = py2c_conn(device=i2c_device)

    set_uom = bytearray()
    # I2C start transmission (TODO: Find reference)
    set_uom.append(0x55)
    # I2C write address, should always be even (TODO: find reference)
    set_uom.append(i2c_address)
    # srf80 register to write to (0=command register)
    set_uom.append(0x00)
    # srf80 number of bytes to return
    # While we discard the return, not sending this resulted in no useful data
    # being returned in the later call
    set_uom.append(0x01)
    # srf80 code for which unit of measurement we want distances in
    set_uom.append(uom_code)

    conn.send_receive(
        bytes_to_send=set_uom,
        receive_bytes=1,
        )

    # Determine how many bytes we will want to read when retrieving data
    # We always need to get the first two bytes
    # Byte 1: Firmware version
    # Byte 2: Light sensor level
    byte_count = 2

    # Each distance reading (up to 16) takes up 2 bytes (big endian unsigned
    # integer)
    byte_count += sonar_echos * 2

    get_data = bytearray()
    # I2C start transmission (TODO: Find reference)
    get_data.append(0x55)
    # I2C read address, should always be write address + 1 (TODO: Find ref)
    get_data.append(i2c_address + 1)
    # srf80 register to write to (0=command register)
    get_data.append(0x00)
    # srf80 number of bytes to return
    get_data.append(byte_count)

    data = conn.send_receive(
        bytes_to_send=get_data,
        receive_bytes=byte_count,
        # Should only need 65ms on default settings
        read_delay=0.66,
        )

    data.reverse()

    # Firmware version and light level are returned first
    firmware_ver = data.pop()
    light_level = data.pop()

    # Each distance is 2 bytes- the high and then the low (big endian)
    distances = []
    for distance in range(0, sonar_echos):
        distance_high_byte = ord(data.pop())
        distance_low_byte = ord(data.pop())
        distance_high_byte *= 256
        distances.append(distance_high_byte + distance_low_byte)

    results = {
        'firmware_version': firmware_ver,
        'light_level': light_level,
        'unit_of_measurement': uom,
        'distances': distances,
        }
    return results


if __name__ == '__main__':
    result = srf80(
        i2c_device='/dev/ttyUSB0',
        i2c_address=0xe0,
        sonar_echos=16,
        uom='cm',
        )

    print('Firmware: {ver}'.format(ver=ord(result['firmware_version'])))
    print('Light level: {ver}'.format(ver=ord(result['light_level'])))
    print('Distances:')
    for distance in result['distances']:
        print('  {distance} {uom}'.format(distance=distance,
                                          uom=result['unit_of_measurement']))
