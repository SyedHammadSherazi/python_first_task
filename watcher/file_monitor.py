import time
from pathlib import Path

from tasks.tasks_runner import run_task
from utils.logger import get_logger


logger = get_logger(__name__)

_last_processed_files = {}
DEBOUNCE_SECONDS = 3


def _log_file_event(event_type, file_path, action="detected", extra=None):
    """
    Central logger for file monitoring events.
    Har file event isi function se log hoga.
    """

    message = f"FILE EVENT | action={action} | event={event_type} | path={file_path}"

    if extra:
        message += f" | {extra}"

    logger.info(message)


def _should_skip_duplicate(file_path):
    """
    Watchdog aksar same file par multiple events fire karta hai.
    Example: created + modified.
    Is function se same file 3 seconds ke andar dobara process nahi hogi.
    """

    now = time.time()
    file_key = str(file_path)

    last_time = _last_processed_files.get(file_key, 0)

    if now - last_time < DEBOUNCE_SECONDS:
        _log_file_event(
            event_type="duplicate",
            file_path=file_path,
            action="skipped",
            extra=f"debounce_seconds={DEBOUNCE_SECONDS}",
        )
        return True

    _last_processed_files[file_key] = now
    return False


def _trigger_task(event_type, file_path, task_name):
    """
    File change par task trigger karega.
    New/modified/moved file ka path task ko pass hoga.
    Deleted file par task trigger nahi hoga.
    """

    file_path = str(file_path)

    _log_file_event(
        event_type=event_type,
        file_path=file_path,
        action="detected",
        extra=f"task={task_name}",
    )

    print(f"File event detected: {event_type}")
    print(f"Path: {file_path}")

    if event_type == "deleted":
        _log_file_event(
            event_type=event_type,
            file_path=file_path,
            action="task_not_triggered",
            extra="reason=file_deleted",
        )
        return

    if _should_skip_duplicate(file_path):
        return

    try:
        _log_file_event(
            event_type=event_type,
            file_path=file_path,
            action="task_trigger_started",
            extra=f"task={task_name}",
        )

        run_task(task_name, file_path=file_path)

        _log_file_event(
            event_type=event_type,
            file_path=file_path,
            action="task_trigger_completed",
            extra=f"task={task_name}",
        )

    except Exception as error:
        logger.exception(
            f"FILE EVENT | action=task_trigger_error | event={event_type} | "
            f"path={file_path} | task={task_name} | error={error}"
        )


def _get_files_snapshot(path, recursive=False):
    """
    Manual polling method ke liye files ka snapshot banata hai.
    """

    watch_path = Path(path)

    if recursive:
        files = watch_path.rglob("*")
    else:
        files = watch_path.glob("*")

    snapshot = {}

    for file_path in files:
        if file_path.is_file():
            try:
                stats = file_path.stat()
                snapshot[str(file_path)] = {
                    "modified_time": stats.st_mtime,
                    "size": stats.st_size,
                }
            except FileNotFoundError:
                continue

    return snapshot


def _start_polling_monitor(path, task_name="file", recursive=False, polling_interval=2):
    """
    Manual polling file monitor.
    """

    watch_path = Path(path)

    if not watch_path.exists():
        watch_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"FILE MONITOR | action=watch_path_created | path={watch_path}")

    logger.info(
        f"FILE MONITOR | action=started | method=polling | path={watch_path} | "
        f"task={task_name} | recursive={recursive} | polling_interval={polling_interval}"
    )

    print("File monitoring started.")
    print("Method: manual polling")
    print(f"Watching path: {watch_path}")
    print(f"Task on change: {task_name}")
    print(f"Polling interval: {polling_interval} seconds")
    print("Press CTRL+C to stop monitoring.")

    previous_snapshot = _get_files_snapshot(watch_path, recursive)

    try:
        while True:
            time.sleep(polling_interval)

            current_snapshot = _get_files_snapshot(watch_path, recursive)

            previous_files = set(previous_snapshot.keys())
            current_files = set(current_snapshot.keys())

            created_files = current_files - previous_files
            deleted_files = previous_files - current_files
            common_files = previous_files & current_files

            for file_path in created_files:
                _trigger_task("created", file_path, task_name)

            for file_path in deleted_files:
                _trigger_task("deleted", file_path, task_name)

            for file_path in common_files:
                old_data = previous_snapshot[file_path]
                new_data = current_snapshot[file_path]

                if (
                    old_data["modified_time"] != new_data["modified_time"]
                    or old_data["size"] != new_data["size"]
                ):
                    _trigger_task("modified", file_path, task_name)

            previous_snapshot = current_snapshot

    except KeyboardInterrupt:
        logger.info("FILE MONITOR | action=stop_requested | method=polling")
        print("Stopping file monitor...")

    finally:
        logger.info("FILE MONITOR | action=stopped | method=polling")
        print("File monitoring stopped.")


def _start_watchdog_monitor(path, task_name="file", recursive=False):
    """
    Watchdog based file monitor.
    """

    try:
        from watchdog.events import FileSystemEventHandler
        from watchdog.observers import Observer

    except ImportError:
        raise ImportError(
            "watchdog is not installed. Run: pip install watchdog "
            "or use --method polling"
        )

    class FileChangeHandler(FileSystemEventHandler):
        def on_created(self, event):
            if event.is_directory:
                return

            _trigger_task("created", event.src_path, task_name)

        def on_modified(self, event):
            if event.is_directory:
                return

            _trigger_task("modified", event.src_path, task_name)

        def on_deleted(self, event):
            if event.is_directory:
                return

            _trigger_task("deleted", event.src_path, task_name)

        def on_moved(self, event):
            if event.is_directory:
                return

            _trigger_task("moved", event.dest_path, task_name)

    watch_path = Path(path)

    if not watch_path.exists():
        watch_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"FILE MONITOR | action=watch_path_created | path={watch_path}")

    logger.info(
        f"FILE MONITOR | action=started | method=watchdog | path={watch_path} | "
        f"task={task_name} | recursive={recursive}"
    )

    event_handler = FileChangeHandler()

    observer = Observer()
    observer.schedule(
        event_handler,
        str(watch_path),
        recursive=recursive,
    )

    observer.start()

    print("File monitoring started.")
    print("Method: watchdog")
    print(f"Watching path: {watch_path}")
    print(f"Task on change: {task_name}")
    print("Press CTRL+C to stop monitoring.")

    try:
        while observer.is_alive():
            time.sleep(1)

    except KeyboardInterrupt:
        logger.info("FILE MONITOR | action=stop_requested | method=watchdog")
        print("Stopping file monitor...")

    finally:
        observer.stop()
        observer.join()

        logger.info("FILE MONITOR | action=stopped | method=watchdog")
        print("File monitoring stopped.")


def start_file_monitor(
    path="tasks/scripts",
    task_name="file",
    recursive=False,
    method="watchdog",
    polling_interval=2,
):
    """
    Main file monitor starter.
    Supported methods:
      1. watchdog
      2. polling
    """

    logger.info(
        f"FILE MONITOR | action=start_requested | method={method} | "
        f"path={path} | task={task_name}"
    )

    if method == "watchdog":
        _start_watchdog_monitor(
            path=path,
            task_name=task_name,
            recursive=recursive,
        )

    elif method == "polling":
        _start_polling_monitor(
            path=path,
            task_name=task_name,
            recursive=recursive,
            polling_interval=polling_interval,
        )

    else:
        logger.error(f"FILE MONITOR | action=start_failed | invalid_method={method}")
        raise ValueError("Invalid monitor method. Use 'watchdog' or 'polling'.")