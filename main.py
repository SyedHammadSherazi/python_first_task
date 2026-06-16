from cli.commands import main as cli_main
from utils.logger import get_logger
from utils.error_handler import handle_error


logger = get_logger("automation_tool")


def main():
    try:
        logger.info("APPLICATION STARTED")

        cli_main()

        logger.info("APPLICATION COMPLETED")

    except KeyboardInterrupt:
        logger.info("APPLICATION STOPPED BY USER | CTRL+C")
        print()
        print("Application stopped by user.")

    except SystemExit:
        raise

    except Exception as error:
        handle_error(
            error=error,
            context="main.py",
            exit_on_error=False,
        )


if __name__ == "__main__":
    main()