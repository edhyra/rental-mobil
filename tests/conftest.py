import os

# Ensure the app uses in-memory services during tests
os.environ.setdefault("TESTING", "1")
