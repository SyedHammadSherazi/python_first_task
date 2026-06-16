from utils.logger import get_logger
from tasks.file_task import FileTaskHandler

logger = get_logger(__name__)


TASK_HANDLERS = {
    "file": FileTaskHandler,
}


def run_task(task_name, **kwargs):
    logger.info(f"TASK RUNNER RECEIVED TASK | {task_name}")

    try:
        handler_class = TASK_HANDLERS.get(task_name)

        if not handler_class:
            raise ValueError(f"Unknown task: {task_name}")

        logger.info(f"TASK HANDLER FOUND | {task_name} | {handler_class.__name__}")

        handler = handler_class(**kwargs)
        result = handler.run()

        logger.info(f"TASK RUNNER COMPLETED TASK | {task_name}")

        return result

    except Exception as error:
        logger.exception(f"TASK RUNNER ERROR | {task_name} | Error: {error}")
        print(f"Task failed: {error}")