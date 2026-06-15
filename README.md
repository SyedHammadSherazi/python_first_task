# python_first_task





````markdown
# Python Task CLI

A simple Python CLI project for managing scheduled tasks.

## Project Structure

```text
python_first_task/
│
├── main.py
├── cli/
│   ├── __init__.py
│   └── commands.py
├── scheduler/
│   ├── __init__.py
│   └── job_scheduler.py
├── tasks/
│   ├── __init__.py
│   └── tasks_runner.py
├── config/
│   ├── __init__.py
│   └── settings.py
├── utils/
│   ├── __init__.py
│   └── helpers.py
├── requirements.txt
└── README.md
````

## Setup

Create virtual environment:

```bash
python -m venv venv
```

Activate virtual environment on Windows:

```bash
venv\Scripts\Activate
```

Install requirements:

```bash
pip install -r requirements.txt
```

## Usage

Show help:

```bash
python main.py --help
```

Show version:

```bash
python main.py --version
```

Start scheduler:

```bash
python main.py start
```

Start scheduler with custom interval:

```bash
python main.py start --interval 30
```

Check scheduler status:

```bash
python main.py status
```

Stop scheduler:

```bash
python main.py stop
```

Run task manually:

```bash
python main.py run-task email
```

Available example tasks:

```text
email
report
backup
```

## Commands

### start

Starts the scheduler.

```bash
python main.py start
```

With interval:

```bash
python main.py start --interval 10
```

### stop

Stops the scheduler.

```bash
python main.py stop
```

### status

Shows scheduler status.

```bash
python main.py status
```

### run-task

Runs a specific task manually.

```bash
python main.py run-task email
```

````

---

## 5. Final test commands

```powershell
python main.py --help
python main.py start --help
python main.py run-task --help
python main.py status
````
@'

## Task - 5: Task Handler Base + File Task

This project now includes an extensible task-handler architecture.

### Features Added

- Base task handler class added.
- File processing task handler added.
- Task runner updated to use handler-based architecture.
- File task validates and processes a sample text file.
- Every action is logged in `logs/app.log`.

### Files Added / Updated

```text
tasks/base_handler.py
tasks/file_task.py
tasks/tasks_runner.py
tasks/scripts/sample.txt

