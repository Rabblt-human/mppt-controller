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
    handle_startup_sequence(ctx)

    while True:
        read_sensor_data(ctx)      # センサー読む
        safety_check(ctx)          # 安全確認
        mppt_control_step(ctx)     # MPPT制御します
        pwm_control(ctx)           # PWM制御します
        update_lcd(ctx)            # LCD更新します。
        time.sleep_ms(3)

main()

print("test")


