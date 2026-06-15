import threading
import time
from pathlib import Path
from datetime import datetime, timedelta
from queue import Queue, Empty

from tasks.tasks_runner import run_task
from utils.logger import get_logger
from config.config_parser import load_config


logger = get_logger(__name__)

STATE_FILE = Path(".scheduler_state")
STOP_FILE = Path(".scheduler_stop")
DEFAULT_CONFIG_PATH = "config/tasks.json"

_stop_event = threading.Event()
_scheduler_thread = None
_worker_thread = None
_task_queue = Queue()


def _write_state(config_path):
    STATE_FILE.write_text(
        f"running\nmode=config\nconfig={config_path}\npid=cli-process",
        encoding="utf-8"
    )


def _cleanup_scheduler_files():
    if STATE_FILE.exists():
        STATE_FILE.unlink()

    if STOP_FILE.exists():
        STOP_FILE.unlink()

    logger.info("SCHEDULER CLEANUP COMPLETED")


def _request_stop_signal():
    STOP_FILE.write_text(
        f"stop_requested_at={datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        encoding="utf-8"
    )
    logger.info("SCHEDULER STOP SIGNAL CREATED")


def _stop_requested():
    return _stop_event.is_set() or STOP_FILE.exists() or not STATE_FILE.exists()


def _calculate_interval_seconds(every, unit):
    if unit == "seconds":
        return every

    if unit == "minutes":
        return every * 60

    if unit == "hours":
        return every * 60 * 60

    raise ValueError(f"Unsupported interval unit: {unit}")


def _parse_daily_time(daily_time):
    hour, minute = daily_time.split(":")
    return int(hour), int(minute)


def _get_next_daily_run(daily_time):
    hour, minute = _parse_daily_time(daily_time)
    now = datetime.now()

    next_run = now.replace(
        hour=hour,
        minute=minute,
        second=0,
        microsecond=0
    )

    if next_run <= now:
        next_run = next_run + timedelta(days=1)

    return next_run


def _worker_loop():
    logger.info("TASK QUEUE WORKER STARTED")

    while True:
        if _stop_requested():
            logger.info("TASK QUEUE WORKER STOP REQUEST DETECTED")
            break

        try:
            task_name = _task_queue.get(timeout=1)

            logger.info(f"TASK DEQUEUED | {task_name}")

            run_task(task_name)

            logger.info(f"QUEUED TASK COMPLETED | {task_name}")

            _task_queue.task_done()

        except Empty:
            continue

        except Exception as error:
            logger.exception(f"QUEUED TASK ERROR | Error: {error}")

    logger.info("TASK QUEUE WORKER STOPPED")


def _load_enabled_tasks(config_path):
    config_data = load_config(config_path)
    tasks = config_data.get("tasks", [])

    enabled_tasks = []

    for task in tasks:
        if task.get("enabled", True):
            enabled_tasks.append(task)

    logger.info(
        f"CONFIG TASKS LOADED | total={len(tasks)} | enabled={len(enabled_tasks)}"
    )

    return enabled_tasks


def _get_task_key(task, index):
    task_name = task.get("name", "unknown")
    schedule = task.get("schedule", {})
    mode = schedule.get("mode", "unknown")

    return f"{index}:{task_name}:{mode}"


def _scheduler_loop(config_path):
    logger.info(f"CONFIG SCHEDULER THREAD STARTED | config={config_path}")

    next_run_times = {}

    while not _stop_requested():
        try:
            enabled_tasks = _load_enabled_tasks(config_path)
            now = datetime.now()

            for index, task in enumerate(enabled_tasks):
                if _stop_requested():
                    logger.info("SCHEDULER STOP REQUEST DETECTED | stopping queue creation")
                    break

                task_name = task.get("name")
                schedule = task.get("schedule", {})
                mode = schedule.get("mode")
                task_key = _get_task_key(task, index)

                if mode == "interval":
                    every = schedule.get("every")
                    unit = schedule.get("unit")

                    interval_seconds = _calculate_interval_seconds(every, unit)

                    if task_key not in next_run_times:
                        next_run_times[task_key] = now

                    if now >= next_run_times[task_key]:
                        logger.info(
                            f"TASK QUEUED | {task_name} | schedule=every {every} {unit}"
                        )

                        _task_queue.put(task_name)

                        next_run_times[task_key] = now + timedelta(
                            seconds=interval_seconds
                        )

                elif mode == "daily":
                    daily_time = schedule.get("time")

                    if task_key not in next_run_times:
                        next_run_times[task_key] = _get_next_daily_run(daily_time)

                    if now >= next_run_times[task_key]:
                        logger.info(
                            f"TASK QUEUED | {task_name} | schedule=daily at {daily_time}"
                        )

                        _task_queue.put(task_name)

                        next_run_times[task_key] = next_run_times[task_key] + timedelta(days=1)

                else:
                    logger.warning(
                        f"CONFIG TASK SKIPPED | unknown schedule mode={mode} | task={task_name}"
                    )

        except Exception as error:
            logger.exception(f"CONFIG SCHEDULER LOOP ERROR | Error: {error}")

        time.sleep(1)

    logger.info("CONFIG SCHEDULER THREAD STOPPED")


def start_scheduler(
    interval=60,
    task_name="file",
    every_minutes=None,
    daily_time=None,
    config_path=DEFAULT_CONFIG_PATH
):
    """
    Start scheduler from config file and queue tasks.
    Graceful stop is linked with stop CLI through .scheduler_stop signal file.
    """

    global _scheduler_thread, _worker_thread

    if STATE_FILE.exists():
        print("Scheduler is already running.")
        logger.warning("SCHEDULER START FAILED | already running")
        return

    if STOP_FILE.exists():
        STOP_FILE.unlink()

    load_config(config_path)

    _stop_event.clear()
    _write_state(config_path)

    logger.info(f"SCHEDULER STARTED | mode=config | config={config_path}")

    _worker_thread = threading.Thread(
        target=_worker_loop,
        daemon=False
    )

    _scheduler_thread = threading.Thread(
        target=_scheduler_loop,
        args=(config_path,),
        daemon=False
    )

    _worker_thread.start()
    _scheduler_thread.start()

    print("Scheduler started successfully.")
    print("Mode: config queue")
    print(f"Config: {config_path}")
    print("Use 'python main.py stop' from another terminal to stop gracefully.")
    print("You can also press CTRL+C to stop.")

    try:
        while _scheduler_thread.is_alive():
            _scheduler_thread.join(timeout=1)

    except KeyboardInterrupt:
        logger.info("SCHEDULER STOP REQUESTED | CTRL+C")
        _stop_event.set()
        _request_stop_signal()

    finally:
        logger.info("SCHEDULER SHUTDOWN STARTED")

        _stop_event.set()

        if _scheduler_thread and _scheduler_thread.is_alive():
            _scheduler_thread.join(timeout=5)

        if _worker_thread and _worker_thread.is_alive():
            _worker_thread.join(timeout=5)

        _cleanup_scheduler_files()

        logger.info("SCHEDULER SHUTDOWN COMPLETED")
        print("Scheduler stopped gracefully.")


def stop_scheduler():
    """
    Request graceful scheduler stop from CLI.
    This does not force kill the scheduler.
    It creates a stop signal file that the running scheduler detects.
    """

    logger.info("SCHEDULER STOP REQUESTED | CLI")

    if not STATE_FILE.exists():
        if STOP_FILE.exists():
            STOP_FILE.unlink()

        logger.warning("SCHEDULER STOP FAILED | scheduler not running")
        print("Scheduler is not running.")
        return

    _request_stop_signal()
    _stop_event.set()

    print("Stop request sent. Waiting for scheduler to stop gracefully...")

    timeout_seconds = 15
    waited = 0

    while STATE_FILE.exists() and waited < timeout_seconds:
        time.sleep(1)
        waited += 1

    if STATE_FILE.exists():
        logger.warning("SCHEDULER STOP TIMEOUT | state file still exists")
        print("Stop request sent, but scheduler did not stop within timeout.")
        print("Check logs/app.log for details.")
    else:
        logger.info("SCHEDULER STOP COMPLETED | CLI")
        print("Scheduler stopped successfully.")


def get_scheduler_status():
    if STATE_FILE.exists():
        content = STATE_FILE.read_text(encoding="utf-8")
        logger.info("SCHEDULER STATUS CHECKED | running")
        print("Scheduler status: running")
        print(content)

        if STOP_FILE.exists():
            print("stop_requested=true")

        print(f"queue_size={_task_queue.qsize()}")
    else:
        logger.info("SCHEDULER STATUS CHECKED | stopped")
        print("Scheduler status: stopped")
