from github_stats_pages.logger import app_log as log


def test_log_stdout():
    log.info("This is a INFO message")
    log.warning("This is a WARNING message")
    log.error("This is a ERROR message")
    log.debug("This is a DEBUG message")
