from machine import PWM, Pin  # type: ignore
import config
from context.system_state import SystemState

def pwm_init(ctx) -> None:
    """Initialise PWM hardware.

    Left blank because ``PwmHardware`` handles initialisation.
    """
    return

def pwm_control(ctx) -> None:
    """Apply the current duty to the PWM hardware respecting safety status.

    Args:
        ctx: Context containing hardware and state.
    """
    state: SystemState = ctx.state
    pwm_hw: PwmHardware = ctx.hw_io.pwm
    safety = state.safety
    mppt = state.mppts

    target = mppt.c_step
    # Safety overrides
    if safety.status == "shutdown":
        target = 0
    elif safety.status == "warning" and target > state.pwms.applied_duty_u16:
        target = state.pwms.applied_duty_u16

    # Clamp target
    if target < config.MPPT_MIN_DUTY:
        target = config.MPPT_MIN_DUTY
    elif target > config.MPPT_MAX_DUTY:
        target = config.MPPT_MAX_DUTY

    # Apply to hardware and record applied value
    pwm_hw.set_duty_u16(int(target))
    state.pwms.applied_duty_u16 = int(target)



class PwmHardware:
    """
    PWMハードウェア担当。
    引数(ピン番号,周波数,デューティ比)をいれる
    - Pinの生成
    - PWMの生成
    - 周波数設定
    - duty_u16の適用
    をまとめた。
    """

    def __init__(self, pin_no: int, freq_hz: int, duty_u16_init: int = 0):
        self._pin_no = pin_no
        self._freq_hz = freq_hz
        self._pwm = PWM(Pin(pin_no))
        self._pwm.freq(freq_hz)
        self.set_duty_u16(duty_u16_init)

    @property   #この値は読み取り専用ということです。
    def pin_no(self) -> int:
        return self._pin_no

    @property   #この値は読み取り専用ということです。
    def freq_hz(self) -> int:
        return self._freq_hz

    def set_freq(self, freq_hz: int) -> None:
        """周波数を変更"""
        self._freq_hz = freq_hz
        self._pwm.freq(freq_hz)

    def set_duty_u16(self, duty_u16: int) -> None:
        """duty_u16(0..65535) を適用。範囲外は丸める。"""
        if duty_u16 < 0:
            duty_u16 = 0
        elif duty_u16 > 65535:
            duty_u16 = 65535
        self._pwm.duty_u16(duty_u16)

    def deinit(self) -> None:   #停止ボタン（未使用）
        """PWM停止"""
        try:
            self._pwm.deinit()
        except AttributeError:
            self.set_duty_u16(0)