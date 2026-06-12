import argparse

from tasks.tasks_runner import run_task
from scheduler.job_scheduler import (
    start_scheduler,
    stop_scheduler,
    get_scheduler_status,
)
from config.settings import APP_NAME, APP_VERSION


def main():
    parser = argparse.ArgumentParser(
        prog=APP_NAME,
        description="A simple Python CLI tool to manage scheduled tasks.",
        epilog="""
Examples:
  python main.py start
  python main.py start --interval 10
  python main.py stop
  python main.py status
  python main.py run-task email
  python main.py run-task report
  python main.py --version

Description:
  start       Start the scheduler
  stop        Stop the scheduler
  status      Check scheduler status
  run-task    Run a specific task manually
""",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"{APP_NAME} {APP_VERSION}",
        help="Show application version"
    )

    subparsers = parser.add_subparsers(
        dest="command",
        title="Commands",
        description="Available commands",
        help="Use one of these commands"
    )

    # Start command
    start_parser = subparsers.add_parser(
        "start",
        help="Start the scheduler",
        description="Start the task scheduler with a given interval.",
        epilog="""
Example:
  python main.py start
  python main.py start --interval 30
""",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    start_parser.add_argument(
        "--interval",
        type=int,
        default=60,
        help="Scheduler interval in seconds. Default is 60 seconds."
    )

    # Stop command
    subparsers.add_parser(
        "stop",
        help="Stop the scheduler",
        description="Stop the currently running scheduler."
    )

    # Status command
    subparsers.add_parser(
        "status",
        help="Check scheduler status",
        description="Check whether the scheduler is running or stopped."
    )

    # Run task command
    run_task_parser = subparsers.add_parser(
        "run-task",
        help="Run a specific task manually",
        description="Run a task manually by providing its task name.",
        epilog="""
Examples:
  python main.py run-task email
  python main.py run-task report
  python main.py run-task backup
""",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    run_task_parser.add_argument(
        "task_name",
        help="Name of the task to run. Example: email, report, backup"
    )

    args = parser.parse_args()

    if args.command == "start":
        start_scheduler(args.interval)

    elif args.command == "stop":
        stop_scheduler()

    elif args.command == "status":
        get_scheduler_status()

    elif args.command == "run-task":
        run_task(args.task_name)

    else:
        parser.print_help()