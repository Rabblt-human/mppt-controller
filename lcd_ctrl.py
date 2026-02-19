import time
import so1602a

class LCDManager:
    """
    LCDを安全に扱うラッパ。
    - 生成と初期化を行う
    - 失敗しても例外を外に出さない
    - 一過性エラーから復帰を試す
    """
    def __init__(self, i2c_no, sda_pin, scl_pin, addr, retry_ms=5000):
        self._cfg = (i2c_no, sda_pin, scl_pin, addr)
        self._lcd = None
        self._retry_ms = retry_ms
        self._next_retry = 0
        self._init_lcd()

    @property
    def alive(self) -> bool:
        return self._lcd is not None

    def _init_lcd(self) -> bool:
        try:
            lcd = so1602a.LCD(*self._cfg)
            lcd.clear()
            lcd.home()
            lcd.on()
            self._lcd = lcd
            return True
        except Exception:
            self._lcd = None
            return False

    def _maybe_retry(self):
        if self._lcd is not None:
            return
        now = time.ticks_ms()
        if time.ticks_diff(now, self._next_retry) >= 0:
            self._init_lcd()
            self._next_retry = time.ticks_add(now, self._retry_ms)

    def write(self, line: int, text) -> None:
        self._maybe_retry()
        if self._lcd is None:
            return
        try:
            self._lcd.write(line, text)
        except Exception:
            self._lcd = None
            self._next_retry = time.ticks_add(time.ticks_ms(), self._retry_ms)

def update_lcd(ctx):
    """Update the LCD with current measurements and MPPT status.

    Displays panel voltage/current, battery voltage and duty along with
    safety status.  If the LCD is not initialised or not alive, the
    function does nothing.
    """
    hw_lcd = ctx.hw_io.lcd
    state = ctx.state

    if hw_lcd is None or not hw_lcd.alive:
        return
    meas = state.meas
    mppt = state.mppts
    safety = state.safety

    # Format lines to fit 16 characters
    line0 = f"P:{meas.p_voltage:5.1f}V I:{meas.p_current:4.1f}A"
    line1 = f"B:{meas.b_voltage:5.1f}V D:{mppt.c_step:5d}"
    # Show safety status prefix if not normal
    if safety.status == "warning":
        line1 = "WARN " + line1[-11:]
    elif safety.status == "shutdown":
        line1 = "STOP " + line1[-11:]

    try:
        hw_lcd.write(0, line0[:16])
        hw_lcd.write(1, line1[:16])
    except Exception:
        # Fail silently on LCD errors
        pass