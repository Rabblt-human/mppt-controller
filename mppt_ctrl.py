"""MPPT control module.

This module implements a simple hill-climbing MPPT (Maximum Power Point
Tracking) algorithm.  At each control step, it compares the latest
measured panel power with the previous measurement stored in state
and adjusts the PWM duty (represented as ``c_step`` in the MpptState).

The algorithm increases or decreases the duty by a fixed step size
``config.MPPT_STEP``, and flips direction when the measured power
decreases compared to the last cycle.  Duty values are constrained
between ``config.MPPT_MIN_DUTY`` and ``config.MPPT_MAX_DUTY``.

The computed duty is stored in ``state.mppts.c_step``.  The actual
application of this duty to the PWM hardware is handled separately in
``pwm_ctrl.pwm_control``, which also respects safety overrides.
"""

import config


def mppt_control_step(ctx) -> None:
    """Perform a single MPPT control step.

    Args:
        ctx: Context containing ``state`` with measurement and MPPT
            state, and potentially ``safety`` state.  The function
            requires that ``state.meas`` and ``state.mppts`` exist.

    Behavior:
        - If the safety status is "shutdown", the MPPT algorithm is
          suspended and ``c_step`` is left unchanged (the duty will
          ultimately be forced to zero by PWM control).
        - Otherwise, compare the current panel power with the stored
          ``last_power``.  If the power has increased, continue to
          adjust the duty in the current ``direction``; if the power
          has decreased, invert the direction and adjust.
        - Update ``last_power`` with the current measured power.
        - Clamp ``c_step`` within the configured min/max duty range.
    """
    state = ctx.state
    safety = state.safety
    mppt = state.mppts
    meas = state.meas

    # Do not adjust duty when in shutdown; leave mppt.c_step as-is
    if safety.status == "shutdown":
        return

    current_power = meas.p_power

    # Compare with last power to decide direction
    if current_power > mppt.last_power:
        # Continue in same direction
        delta = config.MPPT_STEP * mppt.direction
    else:
        # Power decreased or unchanged; flip direction
        mppt.direction *= -1
        delta = config.MPPT_STEP * mppt.direction

    # Compute new duty
    new_duty = mppt.c_step + delta

    # Clamp to configured bounds
    if new_duty < config.MPPT_MIN_DUTY:
        new_duty = config.MPPT_MIN_DUTY
    elif new_duty > config.MPPT_MAX_DUTY:
        new_duty = config.MPPT_MAX_DUTY

    # Store results
    mppt.c_step = int(new_duty)
    mppt.last_power = current_power