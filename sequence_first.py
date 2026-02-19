import time
from sensor_ctrl import read_sensor_data
from safety_ctrl import safety_check
from pwm_ctrl import pwm_control
from lcd_ctrl import update_lcd


def handle_startup_sequence(ctx) -> bool:
    """Perform startup procedure.  Returns True on success.

    The sequence initialises the LCD (if available), performs an initial
    measurement and safety check, and gradually ramps up the duty cycle
    while monitoring for safety faults.  If a fault is detected, the
    procedure displays an error message and aborts.
    """
    hw_lcd = ctx.hw_io.lcd
    state = ctx.state

    # Display initial message on LCD if available
    if hw_lcd and hw_lcd.alive:
        try:
            hw_lcd.write(0, "System Booting..") 
            hw_lcd.write(1, "Init Sensors")
        except Exception:
            pass

    # Perform initial sensor read and safety check
    read_sensor_data(ctx)
    safety_check(ctx)
    if state.safety.status == "shutdown":
        # Display error on LCD
        if hw_lcd and hw_lcd.alive:
            try:
                hw_lcd.write(0, f"B:{state.meas.b_voltage:4.1f}V")
                hw_lcd.write(1, "ERR:OVERVOLT")
            except Exception:
                pass
        return False

    # Ensure duty starts at zero
    state.mppts.c_step = 0
    pwm_control(ctx)

    # Ramp duty in stages; this mirrors the design document loosely
    stages = [
        (0, 5000, 500, 0.06),   # 0→5000 in steps of 500, 60 ms delay
        (5000, 10000, 500, 0.10),  # 5000→10000 in steps of 500, 100 ms delay
        (10000, 13000, 200, 0.09), # 10000→13000 in steps of 200, 90 ms delay
    ]
    for start, end, step, delay in stages:
        for duty in range(start, end + 1, step):
            state.mppts.c_step = duty
            pwm_control(ctx)
            read_sensor_data(ctx)
            safety_check(ctx)
            if state.safety.status == "shutdown":
                if hw_lcd and hw_lcd.alive:
                    try:
                        hw_lcd.write(0, f"B:{state.meas.b_voltage:4.1f}V")
                        hw_lcd.write(1, "ERR:OVERVOLT")
                    except Exception:
                        pass
                return False
            # Optionally update LCD with progress
            update_lcd(ctx)
            time.sleep_ms(int(delay * 1000))

    # Final delay to settle
    time.sleep(0.1)
    return True