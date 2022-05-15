import logging

from rich.console import Console
from rich.logging import RichHandler

sh = RichHandler(
    console=Console(force_terminal=True, log_time=False),
    level=logging.INFO,
    markup=True,
    log_time_format="[%X]",
    show_path=True,
    enable_link_path=False,
)


def log_stdout() -> logging.Logger:
    """
    Retrieve stdout logging object

    To use:
      log = LogClass().get_logger()

    """

    log = logging.getLogger("main_logger")
    log.setLevel(logging.DEBUG)
    if not log.handlers:
        log.addHandler(sh)
    return log


app_log = log_stdout()
