# Trimmed down to only support OV2640
import time as utime

import bitbangio
import board
import busio
import digitalio

from . import OV2640_reg

OV2640 = 0

MAX_FIFO_SIZE = 0x7FFFFF
ARDUCHIP_FRAMES = 0x01
ARDUCHIP_TIM = 0x03
VSYNC_LEVEL_MASK = 0x02
ARDUCHIP_TRIG = 0x41
CAP_DONE_MASK = 0x08

OV2640_160x120 = 0
OV2640_176x144 = 1
OV2640_320x240 = 2
OV2640_352x288 = 3
OV2640_640x480 = 4
OV2640_800x600 = 5
OV2640_1024x768 = 6
OV2640_1280x1024 = 7
OV2640_1600x1200 = 8

Advanced_AWB = 0
Simple_AWB = 1
Manual_day = 2
Manual_A = 3
Manual_cwf = 4
Manual_cloudy = 5


degree_180 = 0
degree_150 = 1
degree_120 = 2
degree_90 = 3
degree_60 = 4
degree_30 = 5
degree_0 = 6
degree30 = 7
degree60 = 8
degree90 = 9
degree120 = 10
degree150 = 11

Auto = 0
Sunny = 1
Cloudy = 2
Office = 3
Home = 4

Antique = 0
Bluish = 1
Greenish = 2
Reddish = 3
BW = 4
Negative = 5
BWnegative = 6
Normal = 7
Sepia = 8
Overexposure = 9
Solarize = 10
Blueish = 11
Yellowish = 12

Exposure_17_EV = 0
Exposure_13_EV = 1
Exposure_10_EV = 2
Exposure_07_EV = 3
Exposure_03_EV = 4
Exposure_default = 5
Exposure03_EV = 6
Exposure07_EV = 7
Exposure10_EV = 8
Exposure13_EV = 9
Exposure17_EV = 10

Auto_Sharpness_default = 0
Auto_Sharpness1 = 1
Auto_Sharpness2 = 2
Manual_Sharpnessoff = 3
Manual_Sharpness1 = 4
Manual_Sharpness2 = 5
Manual_Sharpness3 = 6
Manual_Sharpness4 = 7
Manual_Sharpness5 = 8

MIRROR = 0
FLIP = 1
MIRROR_FLIP = 2

Saturation4 = 0
Saturation3 = 1
Saturation2 = 2
Saturation1 = 3
Saturation0 = 4
Saturation_1 = 5
Saturation_2 = 6
Saturation_3 = 7
Saturation_4 = 8

Brightness4 = 0
Brightness3 = 1
Brightness2 = 2
Brightness1 = 3
Brightness0 = 4
Brightness_1 = 5
Brightness_2 = 6
Brightness_3 = 7
Brightness_4 = 8

Contrast4 = 0
Contrast3 = 1
Contrast2 = 2
Contrast1 = 3
Contrast0 = 4
Contrast_1 = 5
Contrast_2 = 6
Contrast_3 = 7
Contrast_4 = 8

Antique = 0
Bluish = 1
Greenish = 2
Reddish = 3
BW = 4
Negative = 5
BWnegative = 6
Normal = 7
Sepia = 8
Overexposure = 9
Solarize = 10
Blueish = 11
Yellowish = 12

high_quality = 0
default_quality = 1
low_quality = 2

Color_bar = 0
Color_square = 1
BW_square = 2
DLI = 3

BMP = 0
JPEG = 1
RAW = 2


class ArducamClass(object):
    def __init__(self, Type):
        self.CameraMode = JPEG
        self.CameraType = Type
        self.SPI_CS = digitalio.DigitalInOut(board.GP5)
        self.SPI_CS.direction = digitalio.Direction.OUTPUT
        self.I2cAddress = 0x30
        self.spi = busio.SPI(clock=board.GP2, MOSI=board.GP3, MISO=board.GP4)

        for attempt in range(10):
            if self.spi.try_lock():
                break
            else:
                utime.sleep(0.1)

        self.spi.configure(baudrate=4000000, polarity=0, phase=0, bits=8)
        self.i2c = bitbangio.I2C(scl=board.GP9, sda=board.GP8, frequency=1000000)

        for attempt in range(10):
            if self.i2c.try_lock():
                break
            else:
                utime.sleep(0.1)

        print(self.i2c.scan())
        self.Spi_write(0x07, 0x80)
        utime.sleep(0.1)
        self.Spi_write(0x07, 0x00)
        utime.sleep(0.1)

    def Camera_Detection(self):
        while True:
            if self.CameraType == OV2640:
                self.I2cAddress = 0x30
                self.wrSensorReg8_8(0xFF, 0x01)
                id_h = self.rdSensorReg8_8(0x0A)
                id_l = self.rdSensorReg8_8(0x0B)
                if (id_h == 0x26) and ((id_l == 0x40) or (id_l == 0x42)):
                    print("CameraType is OV2640")
                    return True
                else:
                    print("Can't find OV2640 module")
                    return False

    def Set_Camera_mode(self, mode):
        self.CameraMode = mode

    def wrSensorReg16_8(self, addr, val):
        buffer = bytearray(3)
        buffer[0] = (addr >> 8) & 0xFF
        buffer[1] = addr & 0xFF
        buffer[2] = val
        self.iic_write(buffer)
        utime.sleep(0.003)

    def rdSensorReg16_8(self, addr):
        buffer = bytearray(2)
        rt = bytearray(1)
        buffer[0] = (addr >> 8) & 0xFF
        buffer[1] = addr & 0xFF
        self.iic_write(buffer)
        self.iic_readinto(rt)
        return rt[0]

    def wrSensorReg8_8(self, addr, val):
        buffer = bytearray(2)
        buffer[0] = addr
        buffer[1] = val
        self.iic_write(buffer)

    def iic_write(self, buf, *, start=0, end=None):
        if end is None:
            end = len(buf)
        self.i2c.writeto(self.I2cAddress, buf, start=start, end=end)

    def iic_readinto(self, buf, *, start=0, end=None):
        if end is None:
            end = len(buf)
        self.i2c.readfrom_into(self.I2cAddress, buf, start=start, end=end)

    def rdSensorReg8_8(self, addr):
        buffer = bytearray(1)
        buffer[0] = addr
        self.iic_write(buffer)
        self.iic_readinto(buffer)
        return buffer[0]

    def Spi_Test(self, max_retries=10):
        for attempt in range(max_retries):
            self.Spi_write(0x00, 0x56)
            value = self.Spi_read(0x00)
            if value[0] == 0x56:
                print("SPI interface OK")
                return True
            else:
                print(f"SPI interface Error (attempt {attempt + 1}/{max_retries})")
            utime.sleep(1)
        print("SPI test failed: Timeout after maximum retries.")
        return False

    def Camera_Init(self):
        if self.CameraType == OV2640:
            self.wrSensorReg8_8(0xFF, 0x01)
            self.wrSensorReg8_8(0x12, 0x80)
            utime.sleep(0.1)
            self.wrSensorRegs8_8(OV2640_reg.OV2640_JPEG_INIT)
            self.wrSensorRegs8_8(OV2640_reg.OV2640_YUV422)
            self.wrSensorRegs8_8(OV2640_reg.OV2640_JPEG)
            self.wrSensorReg8_8(0xFF, 0x01)
            self.wrSensorReg8_8(0x15, 0x00)
            self.wrSensorRegs8_8(OV2640_reg.OV2640_320x240_JPEG)
        else:
            pass

    def Spi_write(self, address, value):
        maskbits = 0x80
        buffer = bytearray(2)
        buffer[0] = address | maskbits
        buffer[1] = value
        self.SPI_CS_LOW()
        self.spi_write(buffer)
        self.SPI_CS_HIGH()

    def Spi_read(self, address):
        maskbits = 0x7F
        buffer = bytearray(1)
        buffer[0] = address & maskbits
        self.SPI_CS_LOW()
        self.spi_write(buffer)
        self.spi_readinto(buffer)
        self.SPI_CS_HIGH()
        return buffer

    def spi_write(self, buf, *, start=0, end=None):
        if end is None:
            end = len(buf)
        self.spi.write(buf, start=start, end=end)

    def spi_readinto(self, buf, *, start=0, end=None):
        if end is None:
            end = len(buf)
        self.spi.readinto(buf, start=start, end=end)

    def get_bit(self, addr, bit):
        value = self.Spi_read(addr)[0]
        return value & bit

    def SPI_CS_LOW(self):
        self.SPI_CS.value = False

    def SPI_CS_HIGH(self):
        self.SPI_CS.value = True

    def set_fifo_burst(self):
        buffer = bytearray(1)
        buffer[0] = 0x3C
        self.spi.write(buffer, start=0, end=1)

    def clear_fifo_flag(self):
        self.Spi_write(0x04, 0x01)

    def flush_fifo(self):
        self.Spi_write(0x04, 0x01)

    def start_capture(self):
        self.Spi_write(0x04, 0x02)

    def read_fifo_length(self):
        len1 = self.Spi_read(0x42)[0]
        len2 = self.Spi_read(0x43)[0]
        len3 = self.Spi_read(0x44)[0]
        len3 = len3 & 0x7F
        lenght = ((len3 << 16) | (len2 << 8) | (len1)) & 0x07FFFFF
        return lenght

    def wrSensorRegs8_8(self, reg_value):
        for data in reg_value:
            addr = data[0]
            val = data[1]
            if addr == 0xFF and val == 0xFF:
                return
            self.wrSensorReg8_8(addr, val)
            utime.sleep(0.001)

    def wrSensorRegs16_8(self, reg_value):
        for data in reg_value:
            addr = data[0]
            val = data[1]
            if addr == 0xFFFF and val == 0xFF:
                return
            self.wrSensorReg16_8(addr, val)

    def set_format(self, mode):
        if mode == BMP or mode == JPEG or mode == RAW:
            self.CameraMode = mode

    def set_bit(self, addr, bit):
        temp = self.Spi_read(addr)[0]
        self.Spi_write(addr, temp & (~bit))

    def OV2640_set_JPEG_size(self, size):
        if size == OV2640_160x120:
            self.wrSensorRegs8_8(OV2640_reg.OV2640_160x120_JPEG)
        elif size == OV2640_176x144:
            self.wrSensorRegs8_8(OV2640_reg.OV2640_176x144_JPEG)
        elif size == OV2640_320x240:
            self.wrSensorRegs8_8(OV2640_reg.OV2640_320x240_JPEG)
        elif size == OV2640_352x288:
            self.wrSensorRegs8_8(OV2640_reg.OV2640_352x288_JPEG)
        elif size == OV2640_640x480:
            self.wrSensorRegs8_8(OV2640_reg.OV2640_640x480_JPEG)
        elif size == OV2640_800x600:
            self.wrSensorRegs8_8(OV2640_reg.OV2640_800x600_JPEG)
        elif size == OV2640_1024x768:
            self.wrSensorRegs8_8(OV2640_reg.OV2640_1024x768_JPEG)
        elif size == OV2640_1280x1024:
            self.wrSensorRegs8_8(OV2640_reg.OV2640_1280x1024_JPEG)
        elif size == OV2640_1600x1200:
            self.wrSensorRegs8_8(OV2640_reg.OV2640_1600x1200_JPEG)
        else:
            self.wrSensorRegs8_8(OV2640_reg.OV2640_320x240_JPEG)

    def OV2640_set_Light_Mode(self, result):
        if result == Auto:
            self.wrSensorReg8_8(0xFF, 0x00)
            self.wrSensorReg8_8(0xC7, 0x00)
        elif result == Sunny:
            self.wrSensorReg8_8(0xFF, 0x00)
            self.wrSensorReg8_8(0xC7, 0x40)
            self.wrSensorReg8_8(0xCC, 0x5E)
            self.wrSensorReg8_8(0xCD, 0x41)
            self.wrSensorReg8_8(0xCE, 0x54)
        elif result == Cloudy:
            self.wrSensorReg8_8(0xFF, 0x00)
            self.wrSensorReg8_8(0xC7, 0x40)
            self.wrSensorReg8_8(0xCC, 0x65)
            self.wrSensorReg8_8(0xCD, 0x41)
            self.wrSensorReg8_8(0xCE, 0x4F)
        elif result == Office:
            self.wrSensorReg8_8(0xFF, 0x00)
            self.wrSensorReg8_8(0xC7, 0x40)
            self.wrSensorReg8_8(0xCC, 0x52)
            self.wrSensorReg8_8(0xCD, 0x41)
            self.wrSensorReg8_8(0xCE, 0x66)
        elif result == Home:
            self.wrSensorReg8_8(0xFF, 0x00)
            self.wrSensorReg8_8(0xC7, 0x40)
            self.wrSensorReg8_8(0xCC, 0x42)
            self.wrSensorReg8_8(0xCD, 0x3F)
            self.wrSensorReg8_8(0xCE, 0x71)
        else:
            self.wrSensorReg8_8(0xFF, 0x00)
            self.wrSensorReg8_8(0xC7, 0x00)

    def OV2640_set_Color_Saturation(self, Saturation):
        if Saturation == Saturation2:
            self.wrSensorReg8_8(0xFF, 0x00)
            self.wrSensorReg8_8(0x7C, 0x00)
            self.wrSensorReg8_8(0x7D, 0x02)
            self.wrSensorReg8_8(0x7C, 0x03)
            self.wrSensorReg8_8(0x7D, 0x68)
            self.wrSensorReg8_8(0x7D, 0x68)
        elif Saturation == Saturation1:
            self.wrSensorReg8_8(0xFF, 0x00)
            self.wrSensorReg8_8(0x7C, 0x00)
            self.wrSensorReg8_8(0x7D, 0x02)
            self.wrSensorReg8_8(0x7C, 0x03)
            self.wrSensorReg8_8(0x7D, 0x58)
            self.wrSensorReg8_8(0x7D, 0x58)
        elif Saturation == Saturation0:
            self.wrSensorReg8_8(0xFF, 0x00)
            self.wrSensorReg8_8(0x7C, 0x00)
            self.wrSensorReg8_8(0x7D, 0x02)
            self.wrSensorReg8_8(0x7C, 0x03)
            self.wrSensorReg8_8(0x7D, 0x48)
            self.wrSensorReg8_8(0x7D, 0x48)
        elif Saturation == Saturation_1:
            self.wrSensorReg8_8(0xFF, 0x00)
            self.wrSensorReg8_8(0x7C, 0x00)
            self.wrSensorReg8_8(0x7D, 0x02)
            self.wrSensorReg8_8(0x7C, 0x03)
            self.wrSensorReg8_8(0x7D, 0x38)
            self.wrSensorReg8_8(0x7D, 0x38)
        elif Saturation == Saturation_2:
            self.wrSensorReg8_8(0xFF, 0x00)
            self.wrSensorReg8_8(0x7C, 0x00)
            self.wrSensorReg8_8(0x7D, 0x02)
            self.wrSensorReg8_8(0x7C, 0x03)
            self.wrSensorReg8_8(0x7D, 0x28)
            self.wrSensorReg8_8(0x7D, 0x28)

    def OV2640_set_Brightness(self, Brightness):
        if Brightness == Brightness2:
            self.wrSensorReg8_8(0xFF, 0x00)
            self.wrSensorReg8_8(0x7C, 0x00)
            self.wrSensorReg8_8(0x7D, 0x04)
            self.wrSensorReg8_8(0x7C, 0x09)
            self.wrSensorReg8_8(0x7D, 0x40)
            self.wrSensorReg8_8(0x7D, 0x00)
        elif Brightness == Brightness1:
            self.wrSensorReg8_8(0xFF, 0x00)
            self.wrSensorReg8_8(0x7C, 0x00)
            self.wrSensorReg8_8(0x7D, 0x04)
            self.wrSensorReg8_8(0x7C, 0x09)
            self.wrSensorReg8_8(0x7D, 0x30)
            self.wrSensorReg8_8(0x7D, 0x00)
        elif Brightness == Brightness0:
            self.wrSensorReg8_8(0xFF, 0x00)
            self.wrSensorReg8_8(0x7C, 0x00)
            self.wrSensorReg8_8(0x7D, 0x04)
            self.wrSensorReg8_8(0x7C, 0x09)
            self.wrSensorReg8_8(0x7D, 0x20)
            self.wrSensorReg8_8(0x7D, 0x00)
        elif Brightness == Brightness_1:
            self.wrSensorReg8_8(0xFF, 0x00)
            self.wrSensorReg8_8(0x7C, 0x00)
            self.wrSensorReg8_8(0x7D, 0x04)
            self.wrSensorReg8_8(0x7C, 0x09)
            self.wrSensorReg8_8(0x7D, 0x10)
            self.wrSensorReg8_8(0x7D, 0x00)
        elif Brightness == Brightness_2:
            self.wrSensorReg8_8(0xFF, 0x00)
            self.wrSensorReg8_8(0x7C, 0x00)
            self.wrSensorReg8_8(0x7D, 0x04)
            self.wrSensorReg8_8(0x7C, 0x09)
            self.wrSensorReg8_8(0x7D, 0x00)
            self.wrSensorReg8_8(0x7D, 0x00)

    def OV2640_set_Contrast(self, Contrast):
        if Contrast == Contrast2:
            self.wrSensorReg8_8(0xFF, 0x00)
            self.wrSensorReg8_8(0x7C, 0x00)
            self.wrSensorReg8_8(0x7D, 0x04)
            self.wrSensorReg8_8(0x7C, 0x07)
            self.wrSensorReg8_8(0x7D, 0x20)
            self.wrSensorReg8_8(0x7D, 0x28)
            self.wrSensorReg8_8(0x7D, 0x0C)
            self.wrSensorReg8_8(0x7D, 0x06)
        elif Contrast == Contrast1:
            self.wrSensorReg8_8(0xFF, 0x00)
            self.wrSensorReg8_8(0x7C, 0x00)
            self.wrSensorReg8_8(0x7D, 0x04)
            self.wrSensorReg8_8(0x7C, 0x07)
            self.wrSensorReg8_8(0x7D, 0x20)
            self.wrSensorReg8_8(0x7D, 0x24)
            self.wrSensorReg8_8(0x7D, 0x16)
            self.wrSensorReg8_8(0x7D, 0x06)
        elif Contrast == Contrast0:
            self.wrSensorReg8_8(0xFF, 0x00)
            self.wrSensorReg8_8(0x7C, 0x00)
            self.wrSensorReg8_8(0x7D, 0x04)
            self.wrSensorReg8_8(0x7C, 0x07)
            self.wrSensorReg8_8(0x7D, 0x20)
            self.wrSensorReg8_8(0x7D, 0x20)
            self.wrSensorReg8_8(0x7D, 0x20)
            self.wrSensorReg8_8(0x7D, 0x06)
        elif Contrast == Contrast_1:
            self.wrSensorReg8_8(0xFF, 0x00)
            self.wrSensorReg8_8(0x7C, 0x00)
            self.wrSensorReg8_8(0x7D, 0x04)
            self.wrSensorReg8_8(0x7C, 0x07)
            self.wrSensorReg8_8(0x7D, 0x20)
            self.wrSensorReg8_8(0x7D, 0x20)
            self.wrSensorReg8_8(0x7D, 0x2A)
            self.wrSensorReg8_8(0x7D, 0x06)
        elif Contrast == Contrast_2:
            self.wrSensorReg8_8(0xFF, 0x00)
            self.wrSensorReg8_8(0x7C, 0x00)
            self.wrSensorReg8_8(0x7D, 0x04)
            self.wrSensorReg8_8(0x7C, 0x07)
            self.wrSensorReg8_8(0x7D, 0x20)
            self.wrSensorReg8_8(0x7D, 0x18)
            self.wrSensorReg8_8(0x7D, 0x34)
            self.wrSensorReg8_8(0x7D, 0x06)

    def OV2640_set_Special_effects(self, Special_effect):
        if Special_effect == Antique:
            self.wrSensorReg8_8(0xFF, 0x00)
            self.wrSensorReg8_8(0x7C, 0x00)
            self.wrSensorReg8_8(0x7D, 0x18)
            self.wrSensorReg8_8(0x7C, 0x05)
            self.wrSensorReg8_8(0x7D, 0x40)
            self.wrSensorReg8_8(0x7D, 0xA6)
        elif Special_effect == Bluish:
            self.wrSensorReg8_8(0xFF, 0x00)
            self.wrSensorReg8_8(0x7C, 0x00)
            self.wrSensorReg8_8(0x7D, 0x18)
            self.wrSensorReg8_8(0x7C, 0x05)
            self.wrSensorReg8_8(0x7D, 0xA0)
            self.wrSensorReg8_8(0x7D, 0x40)
        elif Special_effect == Greenish:
            self.wrSensorReg8_8(0xFF, 0x00)
            self.wrSensorReg8_8(0x7C, 0x00)
            self.wrSensorReg8_8(0x7D, 0x18)
            self.wrSensorReg8_8(0x7C, 0x05)
            self.wrSensorReg8_8(0x7D, 0x40)
            self.wrSensorReg8_8(0x7D, 0x40)
        elif Special_effect == Reddish:
            self.wrSensorReg8_8(0xFF, 0x00)
            self.wrSensorReg8_8(0x7C, 0x00)
            self.wrSensorReg8_8(0x7D, 0x18)
            self.wrSensorReg8_8(0x7C, 0x05)
            self.wrSensorReg8_8(0x7D, 0x40)
            self.wrSensorReg8_8(0x7D, 0xC0)
        elif Special_effect == BW:
            self.wrSensorReg8_8(0xFF, 0x00)
            self.wrSensorReg8_8(0x7C, 0x00)
            self.wrSensorReg8_8(0x7D, 0x18)
            self.wrSensorReg8_8(0x7C, 0x05)
            self.wrSensorReg8_8(0x7D, 0x80)
            self.wrSensorReg8_8(0x7D, 0x80)
        elif Special_effect == Negative:
            self.wrSensorReg8_8(0xFF, 0x00)
            self.wrSensorReg8_8(0x7C, 0x00)
            self.wrSensorReg8_8(0x7D, 0x40)
            self.wrSensorReg8_8(0x7C, 0x05)
            self.wrSensorReg8_8(0x7D, 0x80)
            self.wrSensorReg8_8(0x7D, 0x80)
        elif Special_effect == BWnegative:
            self.wrSensorReg8_8(0xFF, 0x00)
            self.wrSensorReg8_8(0x7C, 0x00)
            self.wrSensorReg8_8(0x7D, 0x58)
            self.wrSensorReg8_8(0x7C, 0x05)
            self.wrSensorReg8_8(0x7D, 0x80)
            self.wrSensorReg8_8(0x7D, 0x80)
        elif Special_effect == Normal:
            self.wrSensorReg8_8(0xFF, 0x00)
            self.wrSensorReg8_8(0x7C, 0x00)
            self.wrSensorReg8_8(0x7D, 0x00)
            self.wrSensorReg8_8(0x7C, 0x05)
            self.wrSensorReg8_8(0x7D, 0x80)
            self.wrSensorReg8_8(0x7D, 0x80)
