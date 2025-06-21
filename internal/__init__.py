
from internal.tasks.add_scheduler_runner import register_all_tasks

#threading.Thread(target=register_all_tasks, daemon=True).start()

register_all_tasks()



