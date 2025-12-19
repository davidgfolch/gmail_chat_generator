import re
from .. import config

class EmailBodyCleaner:
    def clean(self, body, sender):
        if not body:
            return ""
        lines = body.splitlines()
        clean_lines = []
        found_separator = False
        for line in lines:
            if self._is_separator_line(line):
                if self._is_reply_from_same_sender(line, sender):
                    return self._join_lines(clean_lines)
                found_separator = True
                clean_lines.append(line)
            elif found_separator:
                clean_lines.append(line)
            else:
                clean_lines.append(line)
        return self._join_lines(clean_lines)

    def _is_separator_line(self, line):
        for separator in config.SEPARATORS:
            if re.search(separator, line, re.IGNORECASE):
                return True
        return False

    def _is_reply_from_same_sender(self, line, sender):
        sender_opt_1 = self._extract_sender_name(sender)
        sender_opt_2 = sender.strip().lower()
        line_lower = line.lower()
        return (sender_opt_1 and sender_opt_1 in line_lower) or (sender_opt_2 and sender_opt_2 in line_lower)

    def _extract_sender_name(self, sender):
        if '<' in sender:
            return sender.split('<')[0].strip().lower()
        return sender.strip().lower()

    def _join_lines(self, lines):
        return "\n".join(lines).strip()
