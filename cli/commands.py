import argparse

from utils.logger import get_logger
from utils.error_handler import handle_error
from tasks.tasks_runner import run_task
from watcher.file_monitor import start_file_monitor
from scheduler.job_scheduler import (
    start_scheduler,
    stop_scheduler,
    get_scheduler_status,
)
from config.config_parser import load_config
from config.settings import APP_NAME, APP_VERSION


logger = get_logger(__name__)


def main():
    parser = argparse.ArgumentParser(
        prog=APP_NAME,
        description="A simple Python CLI tool to manage scheduled tasks.",
        epilog="""
Examples:
  python main.py start
  python main.py start --interval 10
  python main.py start --every-minutes 1
  python main.py start --daily-time 09:30
  python main.py start --every-minutes 5 --task-name file
  python main.py stop
  python main.py status
  python main.py watch --path tasks/scripts --task-name file
  python main.py run-task file
  python main.py run-task file --file-path tasks/scripts/sample.txt
  python main.py validate-config
  python main.py validate-config --config config/tasks.json
  python main.py --version

Description:
  start             Start the scheduler
  stop              Stop the scheduler
  status            Check scheduler status
  watch             Watch folder and trigger task on file changes
  run-task          Run a specific task manually
  validate-config   Validate JSON/YAML config file
""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"{APP_NAME} {APP_VERSION}",
        help="Show application version",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        title="Commands",
        description="Available commands",
        help="Use one of these commands",
    )

    start_parser = subparsers.add_parser(
        "start",
        help="Start the scheduler",
        description="Start the task scheduler with a given interval.",
    )

    start_parser.add_argument(
        "--interval",
        type=int,
        default=60,
        help="Scheduler interval in seconds. Default is 60 seconds.",
    )

    start_parser.add_argument(
        "--every-minutes",
        type=int,
        default=None,
        help="Run scheduler every X minutes. Example: --every-minutes 5",
    )

    start_parser.add_argument(
        "--daily-time",
        type=str,
        default=None,
        help="Run scheduler daily at specific time. Format: HH:MM. Example: --daily-time 09:30",
    )

    start_parser.add_argument(
        "--task-name",
        type=str,
        default="file",
        help="Task name to run in scheduler. Default: file",
    )

    start_parser.add_argument(
        "--config",
        type=str,
        default="config/tasks.json",
        help="Scheduler config file path. Default: config/tasks.json",
    )

    subparsers.add_parser(
        "stop",
        help="Stop the scheduler",
        description="Stop the currently running scheduler.",
    )

    subparsers.add_parser(
        "status",
        help="Check scheduler status",
        description="Check whether the scheduler is running or stopped.",
    )

    watch_parser = subparsers.add_parser(
        "watch",
        help="Monitor files and trigger task on file changes",
        description="Watch a folder for file changes and run a task automatically.",
    )

    watch_parser.add_argument(
        "--path",
        type=str,
        default="tasks/scripts",
        help="Folder path to watch. Default: tasks/scripts",
    )

    watch_parser.add_argument(
        "--task-name",
        type=str,
        default="file",
        help="Task name to run when file changes. Default: file",
    )

    watch_parser.add_argument(
        "--recursive",
        action="store_true",
        help="Watch subfolders also.",
    )

    watch_parser.add_argument(
        "--method",
        type=str,
        choices=["watchdog", "polling"],
        default="watchdog",
        help="File monitoring method. Options: watchdog, polling. Default: watchdog",
    )

    watch_parser.add_argument(
        "--polling-interval",
        type=int,
        default=2,
        help="Polling interval in seconds when using --method polling. Default: 2",
    )

    run_task_parser = subparsers.add_parser(
        "run-task",
        help="Run a specific task manually",
        description="Run a task manually by providing its task name.",
    )

    run_task_parser.add_argument(
        "task_name",
        help="Name of the task to run. Example: file",
    )

    run_task_parser.add_argument(
        "--file-path",
        type=str,
        default=None,
        help="Optional file path for file task. Example: --file-path tasks/scripts/sample.txt",
    )

    validate_parser = subparsers.add_parser(
        "validate-config",
        help="Validate JSON/YAML config file",
        description="Validate task config file and show clear errors.",
    )

    validate_parser.add_argument(
        "--config",
        default="config/tasks.json",
        help="Config file path. Default: config/tasks.json",
    )

    args = parser.parse_args()

    try:
        if args.command == "start":
            logger.info("COMMAND STARTED | start")

            start_scheduler(
                interval=args.interval,
                task_name=args.task_name,
                every_minutes=args.every_minutes,
                daily_time=args.daily_time,
                config_path=args.config,
            )

            logger.info("COMMAND COMPLETED | start")

        elif args.command == "stop":
            logger.info("COMMAND STARTED | stop")

            stop_scheduler()

            logger.info("COMMAND COMPLETED | stop")

        elif args.command == "status":
            logger.info("COMMAND STARTED | status")

            get_scheduler_status()

            logger.info("COMMAND COMPLETED | status")

        elif args.command == "watch":
            logger.info(
                f"COMMAND STARTED | watch | Path: {args.path} | "
                f"Task: {args.task_name} | Method: {args.method}"
            )

            start_file_monitor(
                path=args.path,
                task_name=args.task_name,
                recursive=args.recursive,
                method=args.method,
                polling_interval=args.polling_interval,
            )

            logger.info("COMMAND COMPLETED | watch")

        elif args.command == "run-task":
            logger.info(f"COMMAND STARTED | run-task | Task: {args.task_name}")

            task_kwargs = {}

            if args.file_path:
                task_kwargs["file_path"] = args.file_path

            run_task(args.task_name, **task_kwargs)

            logger.info(f"COMMAND COMPLETED | run-task | Task: {args.task_name}")

        elif args.command == "validate-config":
            logger.info(f"COMMAND STARTED | validate-config | File: {args.config}")

            config_data = load_config(args.config)

            print("Config is valid.")
            print(f"Total tasks found: {len(config_data['tasks'])}")

            logger.info(f"COMMAND COMPLETED | validate-config | File: {args.config}")

        else:
            parser.print_help()

    except Exception as error:
        command_name = getattr(args, "command", "unknown")

        handle_error(
            error=error,
            context=f"cli.commands:{command_name}",
            exit_on_error=False,
        )