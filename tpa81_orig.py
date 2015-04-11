'''
Created on Mar 23, 2012

@author: cclement
'''
import serial

def CheckPort(Port):
    ser= serial.Serial()
    ser.port=Port
    ser.baudrate=19200
    ser.parity = serial.PARITY_NONE
    ser.bytesize = 8
    ser.stopbits = serial.STOPBITS_TWO
    ser.xonxoff = 0
    ser.rtscts = 0
    ser.timeout = 500

    try:
        ser.open()
        ser.close()
        return True
    except:
        try:
            ser.close()
        except:
            pass
        return False

def TP81(Port, Address):
    output = []
    ser= serial.Serial()
    ser.port=Port
    ser.baudrate=19200
    ser.parity = serial.PARITY_NONE
    ser.bytesize = 8
    ser.stopbits = serial.STOPBITS_TWO
    ser.xonxoff = 0
    ser.rtscts = 0
    ser.timeout = 500
      
    try:
        ser.open()
        print(ser.isOpen())
        if ser.isOpen()==True:
            try:
                print('startwrite')
                sbuf = bytearray()
                sbuf.append(0x55)
                sbuf.append(Address)
                sbuf.append(0x00)
                sbuf.append(0x0A)
            
                ser.write(sbuf)
                print('stopwrite')
            except:
                print('sadness happened')
                output.append('Failed to write to TP81')
                try:
                    ser.close()
                except:
                    pass
                return output
                
            print('Got stuff!')
            Items = []
            for n in range(0,10):
                try:
                    f = ser.read(1).decode()
                except Exception as E:
                    print('Attempt {x} FAILED'.format(x=n))
                    print(type(E))
                print('Attempt {x}'.format(x=n))
                print(f)
                Items.append(f)
            # Items = ser.read(10).decode()
            Temperatures = []
            print(Temperatures)
            for i in Items:
                Temperatures.append( int(i.encode('hex'), 16))
            output.append("OK")
            output.append(Temperatures)   
            print('Seeking closure')
            try:
                ser.close()
                print('Closed')
            except:
                pass
            return output
    except:
        output.append("Failed to open port")
        try:
            ser.close()
        except:
            pass
        return output
    
def GenericWrite(Port, Address, Arguments):
    ser= serial.Serial()
    ser.port=Port
    ser.baudrate=19200
    ser.parity = serial.PARITY_NONE
    ser.bytesize = 8
    ser.stopbits = serial.STOPBITS_TWO
    ser.xonxoff = 0
    ser.rtscts = 0
    ser.timeout = 500
      
    try:
        ser.open()
        if ser.isOpen()==True:
            try:
                sbuf = bytearray()
                sbuf.append(0x55)
                sbuf.append(Address)
                for arg in Arguments:
                    sbuf.append(arg)
            
                ser.write(sbuf)
                return True
            except:
                try:
                    ser.close()
                except:
                    pass    
                return False
    except:
        return False


def GenericRead(Port, Address, Arguments, BytesToRead):
    output = []
    ser= serial.Serial()
    ser.port=Port
    ser.baudrate=19200
    ser.parity = serial.PARITY_NONE
    ser.bytesize = 8
    ser.stopbits = serial.STOPBITS_TWO
    ser.xonxoff = 0
    ser.rtscts = 0
    ser.timeout = 500
      
    try:
        ser.open()
        if ser.isOpen()==True:
            try:
                sbuf = bytearray()
                sbuf.append(0x55)
                sbuf.append(Address)
                for arg in Arguments:
                    sbuf.append(arg)
            
                ser.write(sbuf)
            except:
                output.append('Failed to write to Address')
                try:
                    ser.close()
                except:
                    pass
                return output
                
            Items = ser.read(BytesToRead).decode()
            ReadValues = []
            for i in Items:
                ReadValues.append(i)
            output.append("OK")
            output.append(ReadValues)   
            try:
                ser.close()
            except:
                pass
            return output
    except:
        output.append("Failed to open port")
        try:
            ser.close()
        except:
            pass
        return output
    pass

if __name__ == '__main__':
    print(CheckPort('/dev/ttyUSB0'))
    print(TP81('/dev/ttyUSB0', 0xd1))
