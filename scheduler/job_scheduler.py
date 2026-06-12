from pathlib import Path


STATE_FILE = Path(".scheduler_state")


def start_scheduler(interval=60):
    """
    Stub command for starting scheduler.
    Real background scheduling baad mein add karenge.
    """

    if STATE_FILE.exists():
        print("Scheduler is already running.")
        return

    STATE_FILE.write_text(f"running\ninterval={interval}")
    print(f"Scheduler started successfully.")
    print(f"Interval: {interval} seconds")


def stop_scheduler():
    """
    Stub command for stopping scheduler.
    """

    if not STATE_FILE.exists():
        print("Scheduler is not running.")
        return

    STATE_FILE.unlink()
    print("Scheduler stopped successfully.")


def get_scheduler_status():
    """
    Stub command for checking scheduler status.
    """

    if STATE_FILE.exists():
        content = STATE_FILE.read_text()
        print("Scheduler status: running")
        print(content)
    else:
        print("Scheduler status: stopped")