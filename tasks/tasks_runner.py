from utils.logger import get_logger
logger = get_logger(__name__)
def run_task(task_name):
    logger.info(f"Running task: {task_name}")

    if task_name == "email":
        logger.info("Email task started...")

    elif task_name == "report":
        logger.info("Report task started...")

    elif task_name == "backup":
        logger.info("Backup task started...")

    else:
        logger.warning(f"Unknown task: {task_name}")