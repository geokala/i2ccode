'''
Created on Mar 23, 2012

@author: cclement
'''
import serial
import time


def TP81(Port, Address, sonar_objects=1, uom='cm'):
    units_of_measurement = {
        'cm': 0x51,
        'inches': 0x50,
        'ms': 0x52,
        }
    uom_code = units_of_measurement[uom]

    output = []
    ser = serial.Serial()
    ser.port = Port
    ser.baudrate = 19200
    ser.parity = serial.PARITY_NONE
    ser.bytesize = 8
    ser.stopbits = serial.STOPBITS_TWO
    ser.xonxoff = 0
    ser.rtscts = 0
    ser.timeout = 500

    try:
        ser.open()
        if ser.isOpen():
            try:
                sbuf = bytearray()
                sbuf.append(0x55)
                sbuf.append(Address)
                sbuf.append(0x00)
                sbuf.append(0x01)
                sbuf.append(uom_code)

                ser.write(sbuf)
            except:
                output.append('Failed to write to TP81')
                try:
                    ser.close()
                except:
                    pass
                return output

            # Eat the byte that's returned
            try:
                ser.read(1)
            except:
                pass

            # Each object is stored with a distance in [high byte, low byte]
            sonar_objects *= 2
            # First two values are ]firmware version, light level]
            read_vals = 2 + sonar_objects
            if read_vals > 36:
                raise ValueError('Can only read 16 sonar objects')
            try:
                time.sleep(0.5)
                sbuf = bytearray()
                sbuf.append(0x55)
                sbuf.append(Address + 1)
                sbuf.append(0x00)
                sbuf.append(read_vals)
                ser.write(sbuf)
                time.sleep(0.5)
            except Exception as e:
                output.append('Failed to write to TP81')
                output.append(e.message)
                try:
                    ser.close()
                except:
                    pass
                return output

            Items = []
            for n in range(0, read_vals):
                try:
                    f = ser.read(1)
                except Exception as E:
                    print('Attempt {x} FAILED'.format(x=n))
                    print(type(E))
                Items.append(f)
            # Items = ser.read(10).decode()

            data = Items
            data.reverse()
            firmware_ver = data.pop()
            light_level = data.pop()

            distances = []
            for distance in range(0, sonar_objects/2):
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

            try:
                ser.close()
            except:
                pass
            return results
    except Exception as e:
        output.append("Failed to open port")
        output.append(e.message)
        try:
            ser.close()
        except:
            pass
        return output

if __name__ == '__main__':
    result = TP81('/dev/ttyUSB0', 0xe0, sonar_objects=16, uom='cm')

    print('Firmware: {ver}'.format(ver=ord(result['firmware_version'])))
    print('Light level: {ver}'.format(ver=ord(result['light_level'])))
    print('Distances:')
    for distance in result['distances']:
        print('  {distance} {uom}'.format(distance=distance,
                                          uom=result['unit_of_measurement']))
