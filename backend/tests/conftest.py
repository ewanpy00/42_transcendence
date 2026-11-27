import os

# Must be set before `app` is imported: settings are read at import time.
os.environ.setdefault("SECRET_KEY", "test-secret-key-that-is-long-enough-0123456789")
