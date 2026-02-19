from config import ADC_PIN_BATTERY,ADC_PIN_PANEL_I,ADC_PIN_PANEL_V
from machine import ADC,Pin
import context.system_state as system_state
import context.system_buffer as system_buffer
import context.io_driver as io_driver


class Ctx:
    def __init__(self,state,buffer,hw_io):
        self.state  = state
        self.buffer = buffer
        self.hw_io  = hw_io


def first_create():
    state   =   system_state.SystemState.create_initial_state()
    buffer  =   system_buffer.MeasureBuffer()
    hw_io   =   io_driver.create_instance_hardware()

    ctx     =   Ctx(state,buffer,hw_io)

    return ctx
