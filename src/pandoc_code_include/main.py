#!/bin/env python
import re
import os
import panflute as pan
PATTERN = r'snippet {id}\n((?:(?!snippet {id})[\s\S])*)'
DEBUG = os.environ.get("DEBUG", None)
if not DEBUG:
    pan.debug = lambda *args: None  # DEBUG


def action(elem: pan.Element, doc: pan.Doc):
    if not isinstance(elem, pan.CodeBlock):
        return
    path = elem.attributes.get("include", None)
    if path is None:
        return
    snippet = elem.attributes.get("snippet", None)
    is_keep_indent = True if "keep_indent" in elem.classes else False
    is_num = True if "numberLines" in elem.classes else False
    offset = elem.attributes.get("start", None) if is_num else None
    offset = int(offset) if offset else None
    kw = {
        'identifier': elem.identifier,
        'classes': elem.classes,
        'attributes': {**elem.attributes, 'custom-style': 'Numbered Code'},
    }
    with open(path, "r") as f:
        elem.text = text = f.read()
    if isinstance(snippet, str):
        codes: list[str] = []
        Range = re.search(r'L(\d+?).*?-?L?(\d*)', snippet)  # L(\d+?)C?(\d*)-?L?(\d*)C?(\d*)
        if Range:
            a, b = Range.groups()
            a = int(a)
            if a > 0:
                a = a - 1
            b = int(b) if b else a + 1
            Slice = slice(a, b)
            matches = [0]
        else:
            pattern = PATTERN.format(id=snippet)
            matches = re.finditer(pattern, text)
            pan.debug(doc.format, pattern)
        for _m in matches:
            if Range:
                lines = text.splitlines()[Slice]
            else:
                lines = _m.group(1).splitlines()[:-1]
                if not lines or not lines[0]:
                    continue

            if not is_keep_indent:
                min_dedent = float('inf')
                indents = re.findall(r'^[ \t]*', '\n'.join(lines))
                for idt in indents:
                    pan.debug('min_dedent', min_dedent, '\n'.join(lines))
                    min_dedent = min(min_dedent, len(idt))
                lines = [l[min_dedent:] for l in lines]
                pan.debug('min_dedent', min_dedent)
            pan.debug(_m, lines)
            if is_num:
                if Range:
                    start = a + 1
                else:
                    start = text[:_m.start()].count('\n') + 1
                pan.debug(start)
                _kw = {'start': start} if not offset else {'start': offset}
                codes.append(
                    pan.OrderedList(
                        *[pan.ListItem(
                            pan.Para(pan.Code(l, **kw))
                        ) for i, l in enumerate(lines)],
                        **_kw
                    )
                )
            else:
                codes.append('\n'.join(lines))
        if is_num:
            return pan.Div(*codes, **kw)
        else:
            elem.text = '\n'.join(codes)
    return elem


def main(doc=None):
    return pan.run_filter(action, doc=doc)


if __name__ == '__main__':
    main()
