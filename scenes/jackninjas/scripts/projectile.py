class Projectile:
    def __init__(
        self, pos, velocity: float, timer: int = 0, variant="bullet", timeout=360
    ):

        self.pos = list(pos)
        self.velocity = velocity
        self.timer = timer
        self.variant = variant
        self.timeout = timeout
