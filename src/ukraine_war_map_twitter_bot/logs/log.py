import functools
import logging
from typing import Any, Callable, Dict, List, ParamSpec, TypeVar
from ..constants import LOGS_RELATIVE_PATH
    
class CustomFormatter(logging.Formatter):
    _FORMATTER_WITH_FUNC_NAME = logging.Formatter(
        "%(asctime)s %(levelname)s at %(funcName)s in %(module)s (%(lineno)d): %(message)s"
    )
    _FORMATTER_WOUT_FUNC_NAME = logging.Formatter(
        "%(asctime)s %(levelname)s: %(message)s"
    )

    def usesTime(self):
        return True

    def formatMessage(self, record):
        if record.funcName == "wrapper":
            return self._FORMATTER_WOUT_FUNC_NAME.formatMessage(record)
        else:
            return self._FORMATTER_WITH_FUNC_NAME.formatMessage(record)


def get_logger(name: str) -> logging.Logger:
    console_handler = logging.StreamHandler()
    file_handler = logging.FileHandler(LOGS_RELATIVE_PATH)

    console_handler.setLevel(logging.DEBUG)
    file_handler.setLevel(logging.DEBUG)
    
    formatter = CustomFormatter()
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


def log_fn_enter_and_exit(logger: logging.Logger, log_exit: bool = False):
    ParamTypes = ParamSpec("ParamTypes")
    ReturnType = TypeVar("ReturnType")

    def deco(fn: Callable[ParamTypes, ReturnType]):
        @functools.wraps(fn)
        def wrapper(*args: ParamTypes.args, **kwargs: ParamTypes.kwargs) -> ReturnType:
            args_shortened: List[str] = [str(arg)[:100] for arg in args]
            kwargs_shortened: Dict[str, str] = {str(k)[:100]: str(v)[:100] for k, v in kwargs.items()}
            
            logger.debug(f"Entered {fn.__name__} with args {args_shortened} and kwargs {kwargs_shortened}")
            result = fn(*args, **kwargs)
            if log_exit:
                logger.debug(
                    f"Exited {fn.__name__} with args {args} and kwargs {kwargs}"
                )
            return result

        return wrapper

    return deco