
import os
import json
from datetime import datetime, timedelta
from . import config
from .service.gmail_client import GmailClient
from .service.email_processor import EmailProcessor
from .service.report_formatter import ReportFormatter

class Processor:
    def __init__(self, client=None, processor=None, formatter=None):
        self.client = client or GmailClient()
        self.processor = processor or EmailProcessor()
        self.formatter = formatter or ReportFormatter()
        
    def run(self, start_date_str, end_date_str, label, comment=None):
        """
        Executes the main logic of fetching emails and generating a report.
        """
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        all_messages_raw = []
        date = start_date
        while date <= end_date:
            day_messages = self._process_single_day(date, label)
            all_messages_raw.extend(day_messages)
            date += timedelta(days=1)
        self._process_and_generate_report(all_messages_raw, start_date_str, end_date_str, label, comment)

    def _process_single_day(self, date, label):
        process_date_str = date.strftime('%Y-%m-%d')
        print(f"Processing date: {process_date_str}")
        cache_filename = self._get_cache_filename(date, label)
        current_ids = self._get_gmail_ids_for_day(date, label)
        day_messages = self._load_cache(cache_filename)
        self._sync_cache(day_messages, current_ids, cache_filename, process_date_str)
        return day_messages

    def _get_cache_filename(self, date, label):
        date_formatted = date.strftime('%Y%m%d')
        label_safe = label.replace('/', '-').replace('\\', '-')
        base_filename = f"{date_formatted}-{label_safe}"
        os.makedirs(config.CACHE_DIR, exist_ok=True)
        return os.path.join(config.CACHE_DIR, f"{base_filename}.raw.json")

    def _get_gmail_ids_for_day(self, date, label):
        day_start_str = date.strftime('%Y/%m/%d')
        next_day = date + timedelta(days=1)
        day_end_str = next_day.strftime('%Y/%m/%d')
        query = f"after:{day_start_str} before:{day_end_str} label:{label}"
        current_messages_metadata = self.client.search_messages(query)
        return {msg['id'] for msg in current_messages_metadata}

    def _sync_cache(self, day_messages, current_ids, cache_filename, process_date_str):
        cached_ids = {msg['id'] for msg in day_messages}
        missing_ids = current_ids - cached_ids
        if missing_ids:
            print(f"Found {len(missing_ids)} new messages for {process_date_str}. Fetching details...")
            new_messages = self._fetch_missing_messages(missing_ids)
            day_messages.extend(new_messages)
            print(f"Updating cache for {process_date_str}. Total: {len(day_messages)}")
            self._save_cache(cache_filename, day_messages)
        else:
            print(f"Cache for {process_date_str} is up to date.")

    def _load_cache(self, filename):
        if os.path.exists(filename):
            print(f"Loading from cache: {filename}")
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = json.load(f)
                    print(f"Loaded {len(content)} messages from cache.")
                    return content
            except Exception as e:
                print(f"Error loading cache: {e}")
                return []
        return []

    def _save_cache(self, filename, data):
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving cache: {e}")

    def _fetch_missing_messages(self, missing_ids):
        new_messages = []
        for msg_id in missing_ids:
            msg_detail = self.client.get_message_detail(msg_id)
            if msg_detail:
                new_messages.append(msg_detail)
        return new_messages

    def _process_and_generate_report(self, messages, start_date, end_date, label, comment=None):
        try:
            # Group and sort
            sorted_threads = self.processor.process_threads(messages)
            # Deduplicate content
            self.processor.deduplicate_thread_content(sorted_threads)
            # Generate Report
            output_file = self.formatter.generate_report(start_date, end_date, label, sorted_threads, comment=comment)
            print(f"Output written to: {output_file}")
        except Exception as error:
            print(f'An error occurred processing messages: {error}')
            import traceback
            traceback.print_exc()
