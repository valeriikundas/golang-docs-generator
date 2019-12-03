def get_lines_above_that_start_with_comment_sign(source_code, i):
    doc = ""
    j = i - 1
    while j >= 0 and source_code[j].startswith("//"):
        doc = source_code[j] + doc
        j -= 1
    return doc


def get_lines_below_that_start_with_sign(source_code, i, sign):
    lines = ""
    j = i + 1
    while j < len(source_code):
        lines += source_code[j]
        if source_code[j].startswith(sign):
            break
        j += 1
    return lines


def mark_code(html_code):
    return f"<pre><code>{html_code}</code></pre>"
