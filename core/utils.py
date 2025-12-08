import math


def exp_lerp(current: float, target: float, speed: float, dt: float) -> float:
    # speed = "px/s"
    if speed <= 0.0:
        return target
    alpha = 1.0 - math.exp(-speed * dt)
    return current + (target - current) * alpha
