"""Sensor control module.

This module reads raw ADC values from the hardware, applies trimming
and conversion to obtain physical quantities (panel voltage, panel
current, battery voltage), updates the system state with these values,
computes derived power, and stores a history of recent measurements.

The measurement procedure follows the design document:

* Panel voltage (PV) and battery voltage (BV) are sampled 26 times.
  The samples are sorted, the lowest 5 and highest 5 values are
  discarded to reduce noise (trimmed mean), and the remaining 16
  values are averaged.  The averaged raw value is scaled by a factor
  to convert to volts.
* Panel current (PI) is sampled 84 times.  The samples are sorted,
  the lowest 10 and highest 10 values are discarded, and the
  remaining 64 values are averaged.  The averaged raw value is
  scaled by a factor to convert to amperes.  A constant offset
  ``P_CURRENT_REV`` is subtracted to correct for sensor bias.

These sample counts and trimming parameters can be tuned; they are
chosen to reject outliers and noise in the ADC readings.
"""

from typing import List

import config


class AdcChannels:
    """
    センサー用ADCのPINインスタンスを生成して保持するだけのクラス

    Attributes:
        battery: ADC object for battery voltage
        panel_v: ADC object for panel voltage
        panel_i: ADC object for panel current
    """

    def __init__(self):
        from machine import ADC, Pin  # type: ignore
        self.battery = ADC(Pin(config.ADC_PIN_BATTERY))
        self.panel_v = ADC(Pin(config.ADC_PIN_PANEL_V))
        self.panel_i = ADC(Pin(config.ADC_PIN_PANEL_I))


def _trimmed_mean(buffer: List[int], drop_low: int, drop_high: int, shift: int) -> int:
    """Compute a trimmed mean of the sorted buffer.

    Args:
        buffer: List of raw ADC values.
        drop_low: Number of smallest values to drop.
        drop_high: Number of largest values to drop.
        shift: Right shift amount to divide the sum (equivalent to dividing by 2**shift).

    Returns:
        Averaged value as an integer.
    """
    # sort in-place
    buffer.sort()
    # sum the middle portion
    total = 0
    for i in range(drop_low, len(buffer) - drop_high):
        total += buffer[i]
    return total >> shift


def read_sensor_data(ctx) -> None:
    """Read ADC values, compute physical units and update system state.

    This function reads raw ADC samples from the hardware through
    ``ctx.hw_io.adc``, computes trimmed means to mitigate noise,
    converts them to volts and amps using factors derived from the
    hardware configuration, updates ``ctx.state.meas`` fields, and
    appends the current snapshot to the measurement history.

    Args:
        ctx: The context containing ``state``, ``buffer``, and ``hw_io``.
    """
    state = ctx.state
    meas = state.meas
    adc = ctx.hw_io.adc
    buffer = ctx.buffer

    # Precompute conversion factors. 3.3 V reference, scaled by resistor ratios.
    pv_factor = (3.3 * config.P_VOLT_RT) / 65535.0
    pi_factor = (3.3 * config.P_CURRENT) / 65535.0
    bv_factor = (3.3 * config.B_VOLT_RT) / 65535.0

    # Read panel voltage (26 samples, drop 5 low and 5 high) -> average of 16 values
    for i in range(26):
        buffer.pv_buffer[i] = adc.panel_v.read_u16()
    pv_avg = _trimmed_mean(buffer.pv_buffer, drop_low=5, drop_high=5, shift=4)  # divide by 16
    # Convert to volts
    meas.p_voltage = pv_avg * pv_factor

    # Read panel current (84 samples, drop 10 low and 10 high) -> average of 64 values
    for i in range(84):
        buffer.pi_buffer[i] = adc.panel_i.read_u16()
    pi_avg = _trimmed_mean(buffer.pi_buffer, drop_low=10, drop_high=10, shift=6)  # divide by 64
    # Convert to amps and subtract offset
    meas.p_current = (pi_avg * pi_factor) - config.P_CURRENT_REV
    if meas.p_current < 0:
        meas.p_current = 0.0  # clamp negative currents to zero

    # Read battery voltage (26 samples, drop 5 low and 5 high) -> average of 16 values
    for i in range(26):
        buffer.bv_buffer[i] = adc.battery.read_u16()
    bv_avg = _trimmed_mean(buffer.bv_buffer, drop_low=5, drop_high=5, shift=4)
    meas.b_voltage = bv_avg * bv_factor

    # Derived power
    meas.p_power = meas.p_voltage * meas.p_current

    # Push to history for MPPT or safety algorithms
    meas.push_history()