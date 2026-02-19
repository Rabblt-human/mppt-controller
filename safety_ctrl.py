"""Safety control module.

This module monitors measured values for over-current and over-voltage
conditions and updates a safety state accordingly.  If thresholds are
exceeded for several consecutive measurement cycles, the safety state
transitions to "shutdown", indicating that the PWM output should be
forced to zero and no further increases should occur.  If only a few
violations are observed, the status is set to "warning" to inhibit
duty increases but still allow decreases.

The thresholds and maximum consecutive violation count are defined in
``config``.  For simplicity, only battery voltage and panel current
are monitored here.  Future development may add additional safety
checks (e.g. battery under-voltage, temperature).
"""

import config


def safety_check(ctx) -> None:
    """Check measured values against safety thresholds and update state.

    Args:
        ctx: Context containing ``state`` with ``meas`` and
            ``safety`` attributes.

    Behavior:
        - Increments consecutive violation counters if the measured
          value exceeds the configured limit; resets counters when
          back within limits.
        - If either counter reaches or exceeds 3 (three consecutive
          violations), sets ``safety.status`` to "shutdown".
        - If any counter is non-zero but below the shutdown threshold,
          sets status to "warning".
        - Otherwise, sets status to "normal".
    """
    state = ctx.state
    meas = state.meas
    safety = state.safety

    # Over-current check (panel current)
    if meas.p_current > config.I_LIMIT:
        safety.overcurrent_count += 1
    else:
        safety.overcurrent_count = 0

    # Over-voltage check (battery voltage)
    if meas.b_voltage > config.BV_LIMIT:
        safety.overvoltage_count += 1
    else:
        safety.overvoltage_count = 0

    # Determine status based on counts
    # When either count reaches 3 or more, trigger shutdown
    if safety.overcurrent_count >= 3 or safety.overvoltage_count >= 3:
        safety.status = "shutdown"
    # Warning if any violations but not yet shutdown
    elif safety.overcurrent_count > 0 or safety.overvoltage_count > 0:
        safety.status = "warning"
    else:
        safety.status = "normal"