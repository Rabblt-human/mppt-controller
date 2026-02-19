from collections import deque


class SafetyState:
    """Safety status and counters for over-limit conditions.

    - status: One of "normal", "warning", or "shutdown".
    - overcurrent_count / overvoltage_count: Consecutive cycles exceeding limit.

    The safety module updates these counters and status based on measured values.
    """

    __slots__ = ("status", "overcurrent_count", "overvoltage_count")

    def __init__(self):
        # status begins in normal state
        self.status: str = "normal"
        # consecutive violation counters
        self.overcurrent_count: int = 0
        self.overvoltage_count: int = 0


class MeasurementSample:
    """測定値スナップショット（履歴用）"""
    __slots__ = ("p_voltage", "p_current", "b_voltage", "p_power")

    def __init__(self, p_voltage, p_current, b_voltage, p_power):
        self.p_voltage = float(p_voltage)
        self.p_current = float(p_current)
        self.b_voltage = float(b_voltage)
        self.p_power = float(p_power)


class Measurements:
    """測定値を入れておくだけのクラス。直近 HISTORY_LEN 件まで履歴保持。"""
    HISTORY_LEN = 5

    def __init__(self):
        self.p_voltage: float = 0.0
        self.p_current: float = 0.0
        self.b_voltage: float = 0.0
        self.p_power: float = 0.0

        # 直近 HISTORY_LEN 件の履歴（古いものから自動で捨てられる）
        self.history = deque((), maxlen=self.HISTORY_LEN)

    def snapshot(self) -> MeasurementSample:
        """現在値のスナップショットを作る"""
        return MeasurementSample(
            self.p_voltage,
            self.p_current,
            self.b_voltage,
            self.p_power,
        )

    def push_history(self) -> None:
        """現在値を履歴に積む（sensor.py だけが呼ぶ想定）"""
        self.history.append(self.snapshot())


class PwmState:
    """PWM の値を保持するだけのクラス（ログ/表示用）。

    書き込み権限:
      - pwm.py: PWM 適用時に更新してよい
    読み取り専用:
      - lcd.py, safety.py
    """
    def __init__(self):
        self.applied_duty_u16: int = 0


class MpptState:
    """MPPT 制御用の変数を入れているだけのクラス。

    PWM 制御より上位レイヤの制御なので PWM と混ぜないでください。

    書き込み権限:
      - mppt.py: 制御ステップごとに更新してよい
    読み取り専用:
      - pwm.py（必要なら duty 計算に使う）
    """
    def __init__(self):
        self.c_step: int = 0
        self.direction: int = 1
        # last measured power value used for hill climbing control
        self.last_power: float = 0.0


class SystemState:
    """
    このクラスは必ず Measurements / PwmState / MpptState を引数として受け取ること
    型判定はしないので差し替えは可能ですがインスタンスの渡し忘れは泡吹いて倒れます。
    """
    def __init__(self, meas, pwms, mppts, safety):
        if meas is None:
            raise ValueError("SystemState: meas is None")
        if pwms is None:
            raise ValueError("SystemState: pwms is None")
        if mppts is None:
            raise ValueError("SystemState: mppts is None")
        if safety is None:
            raise ValueError("SystemState: safety is None")

        self.meas = meas
        self.pwms = pwms
        self.mppts = mppts
        # SafetyState instance used by safety_ctrl
        self.safety = safety

    @classmethod
    def create_initial_state(cls):
        """初期設定用メソッド
        心の悪魔がここにメソッドを作れとささやいた。
        """
        return cls(
            meas=Measurements(),
            pwms=PwmState(),
            mppts=MpptState(),
            safety=SafetyState(),
        )
    