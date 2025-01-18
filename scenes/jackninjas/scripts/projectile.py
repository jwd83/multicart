class Projectile:
    def __init__(
        self,
        pos,
        velocity: float,
        timer: int = 0,
        variant="bullet",
        timeout=360,
        rotation=0,
        flip=False,
    ):

        self.pos = list(pos)
        self.velocity = velocity
        self.timer = timer
        self.variant = variant
        self.timeout = timeout
        self.rotation = rotation
        self.flip = flip

    def update(self):
        pass


class Boomerang(Projectile):
    def __init__(
        self,
        pos,
        velocity,
        timer=0,
        variant="boomerang",
        timeout=360,
        rotation=0,
        flip=False,
    ):
        super().__init__(pos, velocity, timer, variant, timeout, rotation, flip)
        self.v_step = 0.1 if velocity > 0 else -0.1

    def update(self):
        self.velocity -= self.v_step
        pass
