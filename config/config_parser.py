import json
from pathlib import Path

import yaml


ALLOWED_TASK_TYPES = ["python", "shell"]
ALLOWED_SCHEDULE_MODES = ["interval", "daily"]
ALLOWED_INTERVAL_UNITS = ["seconds", "minutes", "hours"]


def read_config(config_path):
    path = Path(config_path)

    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    if path.suffix == ".json":
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)

    if path.suffix in [".yaml", ".yml"]:
        with open(path, "r", encoding="utf-8") as file:
            return yaml.safe_load(file)

    raise ValueError("Unsupported config file type. Use .json, .yaml, or .yml")


def validate_config(config_data):
    if not isinstance(config_data, dict):
        raise ValueError("Config must be an object/dictionary.")

    if "tasks" not in config_data:
        raise ValueError("Missing required field: tasks")

    if not isinstance(config_data["tasks"], list):
        raise ValueError("Field 'tasks' must be a list.")

    for index, task in enumerate(config_data["tasks"], start=1):
        validate_task(task, index)

    return True


def validate_task(task, index):
    required_fields = ["name", "type", "schedule", "file_path"]

    for field in required_fields:
        if field not in task:
            raise ValueError(f"Task #{index} is missing required field: {field}")

    if not task["name"]:
        raise ValueError(f"Task #{index}: name cannot be empty.")

    if task["type"] not in ALLOWED_TASK_TYPES:
        raise ValueError(
            f"Task '{task['name']}': invalid type '{task['type']}'. "
            f"Allowed types: {ALLOWED_TASK_TYPES}"
        )

    if not isinstance(task["schedule"], dict):
        raise ValueError(f"Task '{task['name']}': schedule must be an object.")

    validate_schedule(task["name"], task["schedule"])

    file_path = Path(task["file_path"])
    if not file_path.exists():
        raise ValueError(
            f"Task '{task['name']}': file_path does not exist: {task['file_path']}"
        )


def validate_schedule(task_name, schedule):
    if "mode" not in schedule:
        raise ValueError(f"Task '{task_name}': schedule is missing field: mode")

    mode = schedule["mode"]

    if mode not in ALLOWED_SCHEDULE_MODES:
        raise ValueError(
            f"Task '{task_name}': invalid schedule mode '{mode}'. "
            f"Allowed modes: {ALLOWED_SCHEDULE_MODES}"
        )

    if mode == "interval":
        if "every" not in schedule:
            raise ValueError(f"Task '{task_name}': interval schedule missing 'every'.")

        if "unit" not in schedule:
            raise ValueError(f"Task '{task_name}': interval schedule missing 'unit'.")

        if not isinstance(schedule["every"], int) or schedule["every"] <= 0:
            raise ValueError(
                f"Task '{task_name}': 'every' must be a positive integer."
            )

        if schedule["unit"] not in ALLOWED_INTERVAL_UNITS:
            raise ValueError(
                f"Task '{task_name}': invalid unit '{schedule['unit']}'. "
                f"Allowed units: {ALLOWED_INTERVAL_UNITS}"
            )

    if mode == "daily":
        if "time" not in schedule:
            raise ValueError(f"Task '{task_name}': daily schedule missing 'time'.")

        time_value = schedule["time"]

        if not isinstance(time_value, str) or len(time_value) != 5 or ":" not in time_value:
            raise ValueError(
                f"Task '{task_name}': daily time must be in HH:MM format."
            )


def load_config(config_path):
    config_data = read_config(config_path)
    validate_config(config_data)
    return config_data


def get_task_by_name(task_name, config_path):
    config_data = load_config(config_path)

    for task in config_data["tasks"]:
        if task["name"] == task_name:
            return task

    raise ValueError(f"Task not found in config: {task_name}")