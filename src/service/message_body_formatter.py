import re
from .. import config


class MessageBodyFormatter:
    def is_separator_line(self, text):
        for pattern in config.SEPARATORS:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    def parse_citation_header(self, text):
        spanish_pattern = r"El\s+.*?\s+(\d+)\s+([a-z]{3})\.?\s+(\d{4})\s+(\d{1,2}:\d{2}),\s+(.*)\s+escribió:"
        match = re.search(spanish_pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            day, month_str, year, time, sender_raw = match.groups()
            months = {
                "ene": "01",
                "feb": "02",
                "mar": "03",
                "abr": "04",
                "may": "05",
                "jun": "06",
                "jul": "07",
                "ago": "08",
                "sep": "09",
                "oct": "10",
                "nov": "11",
                "dic": "12",
            }
            month = months.get(month_str.lower(), "01")
            sender_name = sender_raw.strip()
            if "<" in sender_name:
                sender_name = sender_name.split("<")[0].strip()
            parts = sender_name.split()
            final_parts = [part for part in parts if "@" not in part]
            if final_parts:
                sender_name = " ".join(final_parts)
            colored_time = f'<span style="color: {config.COLOR_DATE};">{time}</span>'
            colored_name = (
                f'<span style="color: {config.COLOR_SENDER};">{sender_name}</span>'
            )
            return f"{colored_time} {colored_name}"
        return text

    def format_message_body(self, message_body):
        lines = message_body.split("\n")
        reflowed_lines = self._reflow_lines(lines)
        formatted_parts = []
        in_quote_block = False
        for i, line in enumerate(reflowed_lines):
            is_quote = line.strip().startswith(">")
            is_separator = self.is_separator_line(line)
            next_is_separator = i < len(reflowed_lines) - 1 and self.is_separator_line(
                reflowed_lines[i + 1]
            )
            next_is_quote = i < len(reflowed_lines) - 1 and reflowed_lines[
                i + 1
            ].strip().startswith(">")
            if is_quote:
                in_quote_block = self._handle_quote_line(
                    line, is_separator, in_quote_block, formatted_parts
                )
            else:
                in_quote_block = self._handle_normal_line(
                    line,
                    is_separator,
                    next_is_quote,
                    next_is_separator,
                    in_quote_block,
                    formatted_parts,
                    i,
                    len(reflowed_lines),
                )
        result = "".join(formatted_parts)
        return self._strip_result(result)

    def _reflow_lines(self, lines):
        reflowed_lines = []
        for line in lines:
            if not reflowed_lines:
                reflowed_lines.append(line)
                continue
            last_line = reflowed_lines[-1]
            if self._is_text(last_line) and self._is_text(line):
                reflowed_lines[-1] = last_line.rstrip() + " " + line.strip()
            else:
                reflowed_lines.append(line)
        return reflowed_lines

    def _is_text(self, l):
        return (
            l.strip()
            and not l.strip().startswith(">")
            and not self.is_separator_line(l)
        )

    def _handle_quote_line(self, line, is_separator, in_quote_block, formatted_parts):
        if not in_quote_block:
            if not is_separator:
                formatted_parts.append("\n")
        if is_separator:
            formatted_line = self.parse_citation_header(line)
            formatted_parts.append(formatted_line)
        else:
            formatted_parts.append(line)
        formatted_parts.append("\n")
        return True

    def _handle_normal_line(
        self,
        line,
        is_separator,
        next_is_quote,
        next_is_separator,
        in_quote_block,
        formatted_parts,
        i,
        total_lines,
    ):
        if in_quote_block:
            formatted_parts.append("\n")
            in_quote_block = False
        if line.strip():
            if is_separator:
                header = self.parse_citation_header(line)
                if next_is_quote:
                    last_part = formatted_parts[-1] if formatted_parts else ""
                    prefix = (
                        ""
                        if last_part.endswith("\n\n")
                        else ("\n" if last_part.endswith("\n") else "\n\n")
                    )
                    formatted_parts.append(f"{prefix}> {header}")
                    in_quote_block = True
                else:
                    formatted_parts.append(header)
            else:
                formatted_parts.append(line)
            if i < total_lines - 1:
                if is_separator and next_is_quote:
                    formatted_parts.append("\n")
                elif next_is_separator:
                    formatted_parts.append("<br>")
                elif is_separator:
                    formatted_parts.append("\n")
                elif next_is_quote:
                    formatted_parts.append("\n")
                else:
                    formatted_parts.append("<br>")
        else:
            if not next_is_separator:
                if in_quote_block:
                    formatted_parts.append("\n")
                else:
                    formatted_parts.append("<br>")
        return in_quote_block

    def _strip_result(self, result):
        while (
            result.endswith("\n")
            or result.endswith("<br>")
            or result.strip().endswith(">")
        ):
            if result.endswith("\n"):
                result = result[:-1]
            elif result.endswith("<br>"):
                result = result[:-4]
            elif result.strip().endswith(">"):
                if result.rstrip().endswith("\n>"):
                    result = result.rstrip()[:-1]
                elif result.strip() == ">":
                    result = ""
                else:
                    break
            else:
                break
        return result
