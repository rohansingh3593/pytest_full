import fcntl
class LockFile:
    def __init__(self, name, logger):
        self.name = name
        self.fd = None
        self.logger = logger

    def __enter__(self):
        self.fd = open(self.name, 'w')
        fcntl.flock(self.fd, fcntl.LOCK_EX)
        self.logger.debug('acquired lock on %s', self.name)
    def __exit__(self, type, value, traceback):
        self.logger.debug('releasing lock on %s', self.name)
        fcntl.flock(self.fd, fcntl.LOCK_UN)

