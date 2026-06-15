from pathlib import Path
from tasks.base_handler import BaseTaskHandler


class FileTaskHandler(BaseTaskHandler):
    task_name = "file"

    def __init__(self):
        super().__init__()
        self.file_path = Path("tasks/scripts/sample.txt")

    def validate(self):
        self.logger.info(f"CHECKING FILE PATH | {self.file_path}")

        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {self.file_path}")

        if not self.file_path.is_file():
            raise ValueError(f"Path is not a valid file: {self.file_path}")

        self.logger.info(f"FILE FOUND | {self.file_path}")

    def process(self):
        self.logger.info(f"READING FILE | {self.file_path}")

        content = self.file_path.read_text(encoding="utf-8")

        lines = content.splitlines()
        words = content.split()
        characters = len(content)

        result = {
            "file": str(self.file_path),
            "lines": len(lines),
            "words": len(words),
            "characters": characters,
        }

        self.logger.info(f"FILE PROCESSED | {result}")

        print("File processing completed successfully!")
        print(f"File: {self.file_path}")
        print(f"Lines: {result['lines']}")
        print(f"Words: {result['words']}")
        print(f"Characters: {result['characters']}")

        return result
