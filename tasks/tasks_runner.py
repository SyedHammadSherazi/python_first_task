from utils.logger import get_logger

logger = get_logger(__name__)


def run_task(task_name):
    logger.info(f"TASK STARTED | {task_name}")

    try:
        if task_name == "email":
            logger.info("Email task started...")
            print("Email task is running...")

        elif task_name == "report":
            logger.info("Report task started...")
            print("Report task is running...")

        elif task_name == "backup":
            logger.info("Backup task started...")
            print("Backup task is running...")

        else:
            raise ValueError(f"Unknown task: {task_name}")

        logger.info(f"TASK COMPLETED | {task_name}")

    except Exception as error:
        logger.exception(f"TASK ERROR | {task_name} | Error: {error}")
        print(f"Task failed: {error}")