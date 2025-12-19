import os
import glob

def get_automation_tasks(data_dir='data'):
    """
    Scans data directory for .txt files and parses them into tasks.
    """
    tasks = []
    if not os.path.exists(data_dir):
        return tasks
    files = glob.glob(os.path.join(data_dir, '*.txt'))
    for file_path in files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f if line.strip()]
            if not lines:
                continue
            _parse_tasks(lines, file_path, tasks)
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
    return tasks

def _parse_tasks(lines, file_path, tasks):
    label = lines[0]
    for line in lines[1:]:
        parts = line.split()
        _parse_task(parts, label, file_path, tasks)

def _parse_task(parts, label, file_path, tasks):
    if len(parts) >= 2:
        start_date = parts[0]
        end_date = parts[1]
        comment = " ".join(parts[2:]) if len(parts) > 2 else None
        tasks.append({
            'label': label,
            'start_date': start_date,
            'end_date': end_date,
            'comment': comment,
            'source': os.path.basename(file_path)
        })

def print_tasks_summary(tasks):
    """
    Prints a summary table of the tasks to be executed.
    """
    if not tasks:
        print("No tasks found in data files.")
        return
    print(f"\nFound {len(tasks)} tasks:")
    print("-" * 80)
    print(f"{'Label':<20} | {'Start Date':<12} | {'End Date':<12} | {'Comment':<20} | {'Source':<15}")
    print("-" * 80)
    for task in tasks:
        comment = task['comment'] or ""
        print(f"{task['label']:<20} | {task['start_date']:<12} | {task['end_date']:<12} | {comment:<20} | {task['source']:<15}")
    print("-" * 80)
