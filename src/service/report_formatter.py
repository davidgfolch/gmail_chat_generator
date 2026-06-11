import os
import markdown as md_lib
from datetime import datetime
from email.utils import parsedate_to_datetime
from .. import config
from .message_body_formatter import MessageBodyFormatter


class ReportFormatter:
    def __init__(self, output_dir=config.OUTPUT_DIR):
        self.output_dir = output_dir
        self.body_formatter = MessageBodyFormatter()

    def generate_report(
        self, start_date, end_date, label, threads, filename=None, comment=None
    ):
        if not filename:
            start_formatted = start_date.replace("-", "")
            end_formatted = end_date.replace("-", "")
            label_safe = label.replace("/", "-").replace("\\", "-")
            base_filename_parts = [start_formatted, end_formatted, label_safe]
            if comment:
                comment_safe = comment.replace(" ", "_")
                base_filename_parts.append(comment_safe)
            base_filename = "-".join(base_filename_parts)
            filename = os.path.join(self.output_dir, f"{base_filename}.md")
        os.makedirs(self.output_dir, exist_ok=True)
        with open(filename, "w", encoding="utf-8") as f:
            header = os.path.splitext(os.path.basename(filename))[0]
            f.write(f"# {header}\n")
            if comment:
                f.write(f"### Comment: {comment}\n")
            f.write("\n")
            all_messages = sorted(
                [msg for _, msgs in threads for msg in msgs],
                key=lambda x: x["timestamp"],
            )
            last_date_str = None
            for content in all_messages:
                date_str = self._get_date_str(content)
                if date_str != last_date_str:
                    f.write(f"\n## {date_str}\n\n")
                    last_date_str = date_str
                self._write_message(f, content)
        return filename

    def convert_to_html(self, md_path):
        with open(md_path, "r", encoding="utf-8") as f:
            md_content = f.read()

        title = os.path.splitext(os.path.basename(md_path))[0]
        html_body = md_lib.markdown(md_content)

        css = """
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
                    sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background: #fff;
                color: #333;
                line-height: 1.6;
            }
            h1 {
                color: #222;
                border-bottom: 2px solid #eee;
                padding-bottom: 8px;
                font-size: 1.5em;
            }
            h2 {
                color: #555;
                margin-top: 28px;
                font-size: 1.2em;
                border-bottom: 1px solid #f0f0f0;
                padding-bottom: 4px;
            }
            h3 {
                color: #666;
                font-weight: normal;
                font-size: 1em;
            }
            blockquote {
                border-left: 3px solid #ddd;
                margin: 8px 0;
                padding: 4px 12px;
                color: #555;
                background: #f9f9f9;
            }
            img {
                max-width: 100%;
                height: auto;
                border-radius: 4px;
            }
            details {
                margin: 4px 0;
            }
        </style>
        """

        html = (
            "<!DOCTYPE html>\n"
            '<html lang="es">\n'
            "<head>\n"
            '<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            f"<title>{title}</title>\n"
            f"{css}\n"
            "</head>\n"
            "<body>\n"
            f"{html_body}\n"
            "</body>\n"
            "</html>"
        )

        html_path = md_path.replace(".md", ".html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html)

        return html_path

    def _write_message(self, f, content):
        formatted_date = self._format_date(content)
        sender_name = self._format_sender(content.get("sender", ""))
        subject = content.get("subject", "").strip() or "(sin asunto)"
        message_body = content.get("message", "").strip() or "(sin cuerpo)"
        formatted_body = self.body_formatter.format_message_body(message_body)
        while formatted_body.endswith("<br>"):
            formatted_body = formatted_body[:-4]
        colored_date = (
            f'<span style="color: {config.COLOR_DATE};">{formatted_date}</span>'
        )
        colored_name = (
            f'<span style="color: {config.COLOR_SENDER};">{sender_name}</span>'
        )
        colored_subject = (
            f'<span style="color: {config.COLOR_SUBJECT};">{subject}</span>'
        )
        is_multiline = "<br>" in formatted_body or "\n" in formatted_body
        suffix = "<br>\n\n" if is_multiline else "<br>\n"
        f.write(
            f"{colored_date} {colored_name} {colored_subject}: {formatted_body}{suffix}"
        )
        images = content.get("images", [])
        for img in images:
            self._write_image_thumbnail(f, img)

    def _write_image_thumbnail(self, f, img):
        img_path = img.get("path")
        if not img_path:
            return
        filename = img.get("filename", "image")
        size_kb = img.get("size", 0) // 1024
        f.write(
            f'<details style="margin: 4px 0;">\n'
            f'<summary style="cursor: pointer; color: #666;">'
            f"\U0001f5bc {filename} ({size_kb} KB)"
            f"</summary>\n"
            f'<img src="{img_path}" alt="{filename}" '
            f'style="max-width: 100%; height: auto; border-radius: 4px;">\n'
            f"</details>\n"
        )

    def _get_date_str(self, content):
        try:
            if isinstance(content["timestamp"], datetime):
                dt = content["timestamp"]
            else:
                dt = parsedate_to_datetime(content["date"])
            return dt.strftime("%Y-%m-%d")
        except:
            return content.get("date", "")

    def _format_date(self, content):
        try:
            if isinstance(content["timestamp"], datetime):
                dt = content["timestamp"]
            else:
                dt = parsedate_to_datetime(content["date"])
            return dt.strftime("%H:%M")
        except:
            return content.get("date", "")

    def _format_sender(self, sender):
        if "<" in sender:
            return sender.split("<")[0].strip()
        return sender.strip()
