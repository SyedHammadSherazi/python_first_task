def run_task(task_name):
    print(f"Running task: {task_name}")

    if task_name == "email":
        print("Email task started...")

    elif task_name == "report":
        print("Report task started...")

    elif task_name == "backup":
        print("Backup task started...")

    else:
        print(f"Unknown task: {task_name}")