import sys, os, io, tempfile


class captured_stdout:
    def __init__(self):
        self.old_stdout = None
        self.fnull = None

    def __enter__(self):
        self.F = tempfile.NamedTemporaryFile()
        try:
            self.old_error = os.dup(sys.stderr.fileno())
            os.dup2(self.F.fileno(), sys.stderr.fileno())
        except (AttributeError, io.UnsupportedOperation):
            self.old_error = None
        return self.F

    def __exit__(self, exc_type, exc_value, traceback):
        if self.old_error is not None:
            os.dup2(self.old_error, sys.stderr.fileno())

        self.F.close()