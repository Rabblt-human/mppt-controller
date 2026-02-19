#--------------------------------------
#ハードウェア仕様
P_VOLT_RT = 25          # ソーラーパネル分圧比
P_CURRENT = 5           # ソーラーパネル電流電圧比率
P_CURRENT_REV = 0.000   # ソーラーパネル電流補正値

B_VOLT_RT = 25          # バッテリー分圧比

#--------------------------------------
# safety
I_LIMIT =   100 #時間足りずこの値で実装
BV_LIMIT = 15            # バッテリー電圧上限

#--------------------------------------
#PWMのPin番号
ADC_PIN_BATTERY = 26  # バッテリー電圧
ADC_PIN_PANEL_V = 27  # パネル電圧
ADC_PIN_PANEL_I = 28  # パネル電流

#--------------------------------------
#PWMのPin番号
PWM_PIN = 21            # PWMの出力PIN

#PWM系の定数
PWM_FREQ_HZ = 30000     # PWMの周波数
PWM_MAX = 65535         # 分解能
PWM_DUTY_U16_INIT = 0   # 初期デューティ

#--------------------------------------
# MPPT
# MPPT 制御パラメータ。
# duty の最小/最大値は PWM_MAX に対する割合で設定する。例えば 20%〜85% の範囲で探索する。
# ステップ幅 MPPT_STEP は duty の増減量であり、制御周期ごとに duty が変化する幅を決める。

MPPT_MIN_RATIO = 0.2
MPPT_MAX_RATIO = 0.85
# ユニット 0..65535 での境界値
MPPT_MIN_DUTY = int(PWM_MAX * MPPT_MIN_RATIO)
MPPT_MAX_DUTY = int(PWM_MAX * MPPT_MAX_RATIO)
# ヒルクライムステップ幅（最小〜最大範囲から任意に調整）
MPPT_STEP = 200

#--------------------------------------
# LEDのPin番号
LED_PIN_ONBOARD = "LED"  # 基板上LED

LED_PIN_RED = 14         # 赤LED
LED_PIN_GREEN = 15       # 緑LED

#--------------------------------------
# LCD
LCD_I2C_NO  = 0     #バス番号
LCD_SDA_PIN = 0     #SDA
LCD_SCL_PIN = 1     #SCL
LCD_ADDR    = 0x3C  #スレイブアドレス
