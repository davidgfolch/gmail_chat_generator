
import os
from datetime import datetime
from email.utils import parsedate_to_datetime
from .. import config
from .message_body_formatter import MessageBodyFormatter

class ReportFormatter:
    def __init__(self, output_dir=config.OUTPUT_DIR):
        self.output_dir = output_dir
        self.body_formatter = MessageBodyFormatter()

    def generate_report(self, start_date, end_date, label, threads, filename=None, comment=None):
        if not filename:
            start_formatted = start_date.replace('-', '')
            end_formatted = end_date.replace('-', '')
            label_safe = label.replace('/', '-').replace('\\', '-')
            base_filename_parts = [start_formatted, end_formatted, label_safe]
            if comment:
                comment_safe = comment.replace(' ', '_')
                base_filename_parts.append(comment_safe)
            base_filename = "-".join(base_filename_parts)
            filename = os.path.join(self.output_dir, f"{base_filename}.md")
        os.makedirs(self.output_dir, exist_ok=True)
        with open(filename, 'w', encoding='utf-8') as f:
            header = os.path.splitext(os.path.basename(filename))[0]
            f.write(f"# {header}\n")
            if comment:
                 f.write(f"### Comment: {comment}\n")
            f.write("\n")
            for thread_id, messages in threads:
                for content in messages:
                    self._write_message(f, content)
        return filename

    def _write_message(self, f, content):
        formatted_date = self._format_date(content)
        sender_name = self._format_sender(content.get('sender', ''))
        subject = content.get('subject', '').strip() or "(sin asunto)"
        message_body = content.get('message', '').strip() or "(sin cuerpo)"
        formatted_body = self.body_formatter.format_message_body(message_body)
        while formatted_body.endswith('<br>'):
            formatted_body = formatted_body[:-4]
        colored_date = f'<span style="color: {config.COLOR_DATE};">{formatted_date}</span>'
        colored_name = f'<span style="color: {config.COLOR_SENDER};">{sender_name}</span>'
        colored_subject = f'<span style="color: {config.COLOR_SUBJECT};">{subject}</span>'
        is_multiline = '<br>' in formatted_body or '\n' in formatted_body
        suffix = "<br>\n\n" if is_multiline else "<br>\n"
        f.write(f"{colored_date} {colored_name} {colored_subject}: {formatted_body}{suffix}")

    def _format_date(self, content):
        try:
            if isinstance(content['timestamp'], datetime):
                dt = content['timestamp']
            else:
                dt = parsedate_to_datetime(content['date'])
            return dt.strftime('%Y-%m-%d %H:%M')
        except:
            return content.get('date', '')

    def _format_sender(self, sender):
        if '<' in sender:
            return sender.split('<')[0].strip()
        return sender.strip()
