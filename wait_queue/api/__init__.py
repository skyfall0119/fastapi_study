from .token import router as tokenR
from .ws import router as wsR
from .limiter import router as limiterR

routers = [tokenR, wsR, limiterR]