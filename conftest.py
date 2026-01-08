import os
import tempfile
# pyright: reportUnusedImport=false

# This file is imported by pytest BEFORE test modules,
# so it’s the right place to set env vars needed at import time.

_tmpdir = tempfile.TemporaryDirectory()
os.environ["TASKS_DB_PATH"] = os.path.join(_tmpdir.name, "test_tasks.db")
