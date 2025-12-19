import re
from .. import config

class ThreadContentDeduplicator:
    def deduplicate(self, threads):
        for thread_id, messages in threads:
            self._process_thread(messages)

    def _process_thread(self, messages):
        shown_messages = []
        for content in messages:
            self._process_message(content, shown_messages)

    def _process_message(self, content, shown_messages):
        message_body = content.get('message', '')
        if not message_body:
            return
        lines = message_body.split('\n')
        filtered_lines = self._filter_lines(lines, shown_messages)
        cleaned_content = self._join_lines_strip_quotes(filtered_lines)
        if cleaned_content:
            shown_messages.append(cleaned_content)
        content['message'] = '\n'.join(filtered_lines)

    def _filter_lines(self, lines, shown_messages):
        filtered_lines = []
        i = 0
        while i < len(lines):
            line = lines[i]
            if self._is_separator_line(line):
                i = self._handle_separator(lines, i, shown_messages, filtered_lines)
            elif self._is_quote_line(line):
                self._handle_quote(line, shown_messages, filtered_lines)
                i += 1
            else:
                filtered_lines.append(line)
                i += 1
        return self._remove_empty_lines(filtered_lines)

    def _handle_separator(self, lines, current_index, shown_messages, filtered_lines):
        quoted_block, next_index = self._extract_quoted_block(lines, current_index)
        if quoted_block and not self._is_block_seen(quoted_block, shown_messages):
            self._append_range(filtered_lines, lines, current_index, next_index)
            return next_index
        else:
            return next_index

    def _extract_quoted_block(self, lines, current_index):
        quoted_block = []
        j = current_index + 1
        while j < len(lines) and not lines[j].strip():
            j += 1
        while j < len(lines) and self._is_quote_line(lines[j]):
            content = lines[j].strip()[1:].strip()
            if content:
                quoted_block.append(content)
            j += 1
        return quoted_block, j

    def _is_block_seen(self, block, shown_messages):
        if not block:
            return False
        block_text = self._normalize_text(' '.join(block))
        for shown in shown_messages:
            shown_norm = self._normalize_text(shown)
            if block_text in shown_norm or shown_norm in block_text:
                return True
        return False

    def _handle_quote(self, line, shown_messages, filtered_lines):
        content = line.strip()[1:].strip()
        if not self._is_content_seen(content, shown_messages):
            filtered_lines.append(line)

    def _is_content_seen(self, content, shown_messages):
        for shown in shown_messages:
            if content in shown or shown in content:
                return True
        return False

    def _is_separator_line(self, line):
        for pattern in config.SEPARATORS:
            if re.search(pattern, line, re.IGNORECASE):
                return True
        return False

    def _is_quote_line(self, line):
        return line.strip().startswith('>')

    def _normalize_text(self, text):
        return ' '.join(text.split())

    def _join_lines_strip_quotes(self, lines):
        return '\n'.join(lines).replace('>', '').strip()

    def _append_range(self, target, source, start, end):
        target.extend(source[start:end]) # Logic in original included blank lines check, simplified here but logic check:
        # Original: 
        # filtered_lines.append(line) [start]
        # for k in range(i + 1, j): if lines[k].strip(): filtered_lines.append(lines[k])
        # This implementation simplifies to extending range, but we might want to respect the 'if lines[k].strip()' logic if strictly needed.
        # Let's match original logic closer to be safe.
        pass # Actually implementation below

    def _handle_separator(self, lines, current_index, shown_messages, filtered_lines):
         # Redefining to correctly implement append logic matching original
        quoted_block, next_index = self._extract_quoted_block(lines, current_index)
        if quoted_block and not self._is_block_seen(quoted_block, shown_messages):
            filtered_lines.append(lines[current_index])
            for k in range(current_index + 1, next_index):
                 if lines[k].strip():
                     filtered_lines.append(lines[k])
            return next_index
        else:
            return next_index

    def _remove_empty_lines(self, lines):
        cleaned = []
        prev_empty = False
        for line in lines:
            is_empty = not line.strip()
            if is_empty:
                if not prev_empty:
                    cleaned.append(line)
                prev_empty = True
            else:
                cleaned.append(line)
                prev_empty = False
        return cleaned
