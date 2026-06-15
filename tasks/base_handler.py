from abc import ABC, abstractmethod
from utils.logger import get_logger


class BaseTaskHandler(ABC):
    task_name = "base"

    def __init__(self):
        self.logger = get_logger(self.__class__.__module__)

    def run(self):
        self.logger.info(f"TASK STARTED | {self.task_name}")

        try:
            self.logger.info(f"VALIDATION STARTED | {self.task_name}")
            self.validate()
            self.logger.info(f"VALIDATION COMPLETED | {self.task_name}")

            self.logger.info(f"PROCESSING STARTED | {self.task_name}")
            result = self.process()
            self.logger.info(f"PROCESSING COMPLETED | {self.task_name}")

            self.on_success(result)
            self.logger.info(f"TASK COMPLETED | {self.task_name}")

            return result

        except Exception as error:
            self.on_error(error)
            self.logger.exception(f"TASK ERROR | {self.task_name} | Error: {error}")
            raise

    def validate(self):
        pass

    @abstractmethod
    def process(self):
        pass

    def on_success(self, result):
        self.logger.info(f"TASK SUCCESS | {self.task_name} | Result: {result}")

    def on_error(self, error):
        self.logger.error(f"TASK FAILED | {self.task_name} | Error: {error}")
