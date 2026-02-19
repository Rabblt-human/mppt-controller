import time
from context import factory_instance
from sequence_first import handle_startup_sequence
from sensor_ctrl import read_sensor_data
from safety_ctrl import safety_check
from mppt_ctrl import mppt_control_step
from pwm_ctrl import pwm_control
from lcd_ctrl import update_lcd


def main():
    ctx = factory_instance.first_create()
    started = handle_startup_sequence(ctx)

    if not started:
        while True:
            pwm_control(ctx)
            update_lcd(ctx)
            time.sleep_ms(100)

    while True:
        read_sensor_data(ctx)      # センサー読む
        safety_check(ctx)          # 安全確認
        mppt_control_step(ctx)     # MPPT制御します
        pwm_control(ctx)           # PWM制御します
        update_lcd(ctx)            # LCD更新します。
        time.sleep_ms(300)

main()
