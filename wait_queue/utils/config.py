import os

## REDIS connection
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))



## REDIS
TTL_EXPIRE = 30
TOKEN_WAIT = "wait"
TOKEN_ACTIVE = "active"
WAIT_QUEUE_KEY = "wait_queue"
TOKEN_PREFIX = "token:"
ACTIVE_SET_KEY = "active_tokens"
ACTIVE_COUNT_KEY = "active_count"

# REDIS rate_limit
RATE_PREFIX = "rate:"
RATE_LIMIT = 5
RATE_WINDOW = 10

ACTIVE_VALIDATE_INTERVAL = 5
WAIT_NOTIFY_INTERVAL = 5

MAX_ACTIVE_SET = 10