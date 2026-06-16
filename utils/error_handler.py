from utils.logger import get_logger


logger = get_logger(__name__)


def handle_error(error, context="application", exit_on_error=False):
    """
    Central error handler.

    Error ko log karta hai aur user ko clean message show karta hai.
    """

    logger.exception(f"ERROR HANDLED | context={context} | Error: {error}")

    print()
    print("Something went wrong, but the application handled it safely.")
    print(f"Context: {context}")
    print(f"Error: {error}")
    print("Check logs/app.log for details.")

    if exit_on_error:
        raise SystemExit(1)