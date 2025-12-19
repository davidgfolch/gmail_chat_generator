
import argparse
from src.processor import Processor

def main():
    parser = argparse.ArgumentParser(description='Fetch Gmail messages based on filters.')
    parser.add_argument('--start-date', required=False, help='Start date in YYYY-MM-DD format')
    parser.add_argument('--end-date', required=False, help='End date in YYYY-MM-DD format (optional, defaults to today)')
    parser.add_argument('--label', required=False, help='Label to filter by (e.g., INBOX)')
    args = parser.parse_args()
    app = Processor()
    # Case 1: Arguments provided via CLI
    if args.start_date and args.label:
        from datetime import datetime
        end_date = args.end_date
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        print(f"Running single task: Label={args.label}, Start={args.start_date}, End={end_date}")
        app.run(args.start_date, end_date, args.label)
    # Case 2: No arguments, running automation mode
    else:
        print("No arguments provided. Checking 'data/' directory for tasks...")
        from src.service.data_automation import get_automation_tasks, print_tasks_summary
        tasks = get_automation_tasks()
        if not tasks:
            print("No tasks found. Please provide arguments or populate 'data/*.txt'.")
            return
        print_tasks_summary(tasks)
        confirm = input("\nProceed with these tasks? (y/n): ").strip().lower()
        if confirm == 'y':
            for i, task in enumerate(tasks, 1):
                comment_display = f" | Comment: {task.get('comment')}" if task.get('comment') else ""
                print(f"\nExecuting Task {i}/{len(tasks)}: {task['label']} ({task['start_date']} to {task['end_date']}){comment_display}")
                app.run(task['start_date'], task['end_date'], task['label'], comment=task.get('comment'))
            print("\nAll tasks completed.")
        else:
            print("Operation cancelled.")

if __name__ == '__main__':
    main()
