
import base64
from datetime import datetime
from email.utils import parsedate_to_datetime
from bs4 import BeautifulSoup
from .email_body_cleaner import EmailBodyCleaner
from .thread_deduplicator import ThreadContentDeduplicator

class EmailProcessor:
    def __init__(self):
        self.body_cleaner = EmailBodyCleaner()
        self.deduplicator = ThreadContentDeduplicator()

    def process_threads(self, raw_messages):
        all_messages = [self._extract_content(msg) for msg in raw_messages]
        threads = self._group_by_thread(all_messages)
        return self._sort_threads(threads)

    def deduplicate_thread_content(self, threads):
        self.deduplicator.deduplicate(threads)

    def _extract_content(self, message_resource):
        payload = message_resource.get('payload', {})
        headers = payload.get('headers', [])
        sender = self._get_header(headers, 'from', "Unknown Sender")
        date = self._get_header(headers, 'date', "Unknown Date")
        subject = self._get_header(headers, 'subject', "No Subject")
        body = self._extract_body(payload)
        clean_message = self.body_cleaner.clean(body, sender)
        return {
            'sender': sender,
            'date': date,
            'subject': subject,
            'message': clean_message,
            'threadId': message_resource.get('threadId', ''),
            'timestamp': self._parse_date(date)
        }

    def _get_header(self, headers, name, default):
        return next((h['value'] for h in headers if h['name'].lower() == name), default)

    def _extract_body(self, payload):
        if 'parts' in payload:
            return self._extract_from_parts(payload['parts'])
        return self._extract_from_payload(payload)

    def _extract_from_parts(self, parts):
        for part in parts:
            if part['mimeType'] == 'text/plain':
                data = part['body'].get('data')
                if data:
                    return base64.urlsafe_b64decode(data).decode()
        for part in parts:
            if part['mimeType'] == 'text/html':
                data = part['body'].get('data')
                if data:
                    return self._parse_html(data)
        return ""

    def _extract_from_payload(self, payload):
        if payload.get('mimeType') == 'text/plain':
            data = payload['body'].get('data')
            if data:
                return base64.urlsafe_b64decode(data).decode()
        return ""

    def _parse_html(self, data):
        html_content = base64.urlsafe_b64decode(data).decode()
        soup = BeautifulSoup(html_content, 'html.parser')
        return soup.get_text()

    def _parse_date(self, date_str):
        if date_str != "Unknown Date":
            return parsedate_to_datetime(date_str)
        return datetime.min

    def _group_by_thread(self, messages):
        from collections import defaultdict
        threads = defaultdict(list)
        for content in messages:
            threads[content['threadId']].append(content)
        return threads

    def _sort_threads(self, threads_dict):
        for thread_id in threads_dict:
            threads_dict[thread_id].sort(key=lambda x: x['timestamp'])
        return sorted(threads_dict.items(), key=lambda item: item[1][0]['timestamp'])
