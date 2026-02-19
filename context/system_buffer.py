# buffer.py などに置く想定

class MeasureBuffer:
    """
    測定で使うメモリを確保しておくだけのクラス。
    """

    def __init__(self):
        # PI: 電流測定用バッファ
        self.pi_buffer = [0] * 84

        # PV: 太陽電池電圧測定用バッファ
        self.pv_buffer = [0] * 26

        # BV: バッテリ電圧測定用バッファ
        self.bv_buffer = [0] * 26
