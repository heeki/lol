import logging


################################################################################
# utility class
################################################################################
class Util:
    @staticmethod
    def logger(name, file_local):
        _log = logging.getLogger(name)
        log_formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s '%(message)s'")

        # handler_file = logging.FileHandler(file_local)
        # handler_file.setFormatter(log_formatter)
        handler_console = logging.StreamHandler()
        handler_console.setFormatter(log_formatter)

        _log.setLevel(logging.WARNING)
        if len(_log.handlers) == 0:
            # _log.addHandler(handler_file)
            _log.addHandler(handler_console)

        return _log
