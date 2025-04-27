#!/bin/env python
import re
import panflute as pan
PATTERN = r'snippet {id}\n((?:(?!snippet {id})[\s\S])*)'


def action(elem: pan.Element, doc: pan.Doc):
    if not isinstance(elem, pan.CodeBlock):
        return
    path = elem.attributes.get("include", None)
    if path is None:
        return
    snippet = elem.attributes.get("snippet", None)
    with open(path, "r") as f:
        elem.text = text = f.read()
    is_num = True if "numberLines" in elem.classes else False
    kw = {
        'identifier': elem.identifier,
        'classes': elem.classes,
        'attributes': elem.attributes,
    }
    if snippet is not None:
        codes: list[str] = []
        pattern = PATTERN.format(id=snippet)
        matches = re.finditer(pattern, text)
        pan.debug(doc.format, pattern)
        for m in matches:
            lines = m.group(1).splitlines()[:-1]
            if not lines or not lines[0]:
                continue
            start = text[:m.start()].count('\n') + 1
            pan.debug(m, lines)
            if is_num:
                pan.debug(start)
                codes.append(
                    pan.OrderedList(
                        *[pan.ListItem(
                            pan.CodeBlock(
                                l, **kw
                            )
                        ) for i, l in enumerate(lines)], start=start)
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
