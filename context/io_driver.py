from config import \
    PWM_PIN,PWM_FREQ_HZ,PWM_DUTY_U16_INIT,\
    LED_PIN_ONBOARD,LED_PIN_RED,LED_PIN_GREEN,\
    LCD_I2C_NO,LCD_SDA_PIN,LCD_SCL_PIN,LCD_ADDR
from pwm_ctrl import PwmHardware
from sensor_ctrl import AdcChannels
from lcd_ctrl import LCDManager
from machine import Pin

class HardwareIO:
    def __init__(self,pwm,adc,leds,lcd) -> None:
        self.pwm    = pwm
        self.adc    = adc 
        self.leds   = leds 
        self.lcd    = lcd

class Leds:
    """
    Ledのピンインスタンスを生成し保持するだけ
    """
    def __init__(self) -> None:
        self.onboard = Pin(LED_PIN_ONBOARD,Pin.OUT)
        self.led_red = Pin(LED_PIN_RED,Pin.OUT)
        self.led_green = Pin(LED_PIN_GREEN,Pin.OUT)


def create_instance_hardware():

    pwm   = PwmHardware(PWM_PIN,PWM_FREQ_HZ,PWM_DUTY_U16_INIT)
    adc   = AdcChannels()
    leds  = Leds()
    lcd   = LCDManager(LCD_I2C_NO,LCD_SDA_PIN,LCD_SCL_PIN,LCD_ADDR)

    hw_io = HardwareIO(pwm,adc,leds,lcd)
    return hw_io
