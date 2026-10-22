"""Markdown to and from the ProseMirror documents Substack's editor stores (`draft_body`, `body`, Note `bodyJson`).

Covers what agents write: headings, paragraphs, bullet and numbered lists, quotes, code blocks, rules,
images by URL, and inline bold, italic, strike, code and links. Node and mark names are the editor's,
as recorded from drafts typed in it (17.10.2026). Anything else Substack stores (buttons, embeds,
footnotes) comes back as its plain text.
"""

from __future__ import annotations

import re
from typing import Any

_INLINE = re.compile(
    r"(?P<code>`[^`]+`)"
    r"|(?P<image>!\[(?P<alt>[^\]]*)\]\((?P<src>[^)\s]+)\))"
    r"|(?P<link>\[(?P<label>[^\]]+)\]\((?P<href>[^)\s]+)\))"
    r"|(?P<strong>\*\*(?P<strong_text>.+?)\*\*|__(?P<strong_alt>.+?)__)"
    r"|(?P<strike>~~(?P<strike_text>.+?)~~)"
    r"|(?P<em>\*(?P<em_text>[^*\s][^*]*?)\*|_(?P<em_alt>[^_\s][^_]*?)_)"
)
_HEADING = re.compile(r"^(#{1,6})\s+(.*)$")
_BULLET = re.compile(r"^\s*[-*+]\s+(.*)$")
_NUMBERED = re.compile(r"^\s*\d+[.)]\s+(.*)$")
_IMAGE_LINE = re.compile(r"^!\[([^\]]*)\]\(([^)\s]+)\)$")
_RULE = re.compile(r"^\s*([-*_])(\s*\1){2,}\s*$")


def _text(text: str, marks: list[dict[str, Any]]) -> dict[str, Any]:
    node: dict[str, Any] = {"type": "text", "text": text}
    if marks:
        node["marks"] = marks
    return node


def inline(text: str, marks: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    """Inline Markdown to text nodes with marks."""
    marks = marks or []
    nodes: list[dict[str, Any]] = []
    position = 0
    for match in _INLINE.finditer(text):
        if match.start() > position:
            nodes.append(_text(text[position : match.start()], marks))
        if match["code"]:
            nodes.append(_text(match["code"][1:-1], [*marks, {"type": "code"}]))
        elif match["image"]:
            nodes.extend(
                inline(match["alt"] or match["src"], [*marks, {"type": "link", "attrs": {"href": match["src"]}}])
            )
        elif match["link"]:
            nodes.extend(inline(match["label"], [*marks, {"type": "link", "attrs": {"href": match["href"]}}]))
        elif match["strong"]:
            nodes.extend(inline(match["strong_text"] or match["strong_alt"], [*marks, {"type": "strong"}]))
        elif match["strike"]:
            nodes.extend(inline(match["strike_text"], [*marks, {"type": "strikethrough"}]))
        else:
            nodes.extend(inline(match["em_text"] or match["em_alt"], [*marks, {"type": "em"}]))
        position = match.end()
    if position < len(text):
        nodes.append(_text(text[position:], marks))
    return [node for node in nodes if node.get("text")]


def _paragraph(text: str) -> dict[str, Any]:
    content = inline(text)
    return {"type": "paragraph", "content": content} if content else {"type": "paragraph"}


def _image(alt: str, src: str) -> dict[str, Any]:
    return {"type": "captionedImage", "content": [{"type": "image2", "attrs": {"src": src, "alt": alt or None}}]}


def _list(kind: str, items: list[str]) -> dict[str, Any]:
    node: dict[str, Any] = {
        "type": kind,
        "content": [{"type": "listItem", "content": [_paragraph(item)]} for item in items],
    }
    if kind == "orderedList":
        node["attrs"] = {"start": 1, "order": 1}
    return node


def to_doc(markdown: str) -> dict[str, Any]:
    """A Markdown text as a ProseMirror document."""
    lines = markdown.replace("\r\n", "\n").split("\n")
    blocks: list[dict[str, Any]] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        stripped = line.strip()
        if not stripped:
            index += 1
            continue
        if stripped.startswith("```"):
            code: list[str] = []
            index += 1
            while index < len(lines) and not lines[index].strip().startswith("```"):
                code.append(lines[index])
                index += 1
            index += 1
            text = "\n".join(code)
            blocks.append({"type": "code_block", "content": [_text(text, [])]} if text else {"type": "code_block"})
            continue
        if _RULE.match(stripped):
            blocks.append({"type": "horizontal_rule"})
            index += 1
            continue
        if heading := _HEADING.match(stripped):
            content = inline(heading[2].strip())
            blocks.append({"type": "heading", "attrs": {"level": len(heading[1])}, "content": content})
            index += 1
            continue
        if image := _IMAGE_LINE.match(stripped):
            blocks.append(_image(image[1], image[2]))
            index += 1
            continue
        for pattern, kind in ((_BULLET, "bulletList"), (_NUMBERED, "orderedList")):
            if pattern.match(line):
                items = []
                while index < len(lines) and (item := pattern.match(lines[index])):
                    items.append(item[1].strip())
                    index += 1
                blocks.append(_list(kind, items))
                break
        else:
            if stripped.startswith(">"):
                quoted = []
                while index < len(lines) and lines[index].strip().startswith(">"):
                    quoted.append(lines[index].strip()[1:].lstrip())
                    index += 1
                inner = to_doc("\n".join(quoted))["content"]
                blocks.append({"type": "blockquote", "content": inner or [{"type": "paragraph"}]})
                continue
            paragraph = [stripped]
            index += 1
            while index < len(lines) and lines[index].strip() and not _starts_block(lines[index]):
                paragraph.append(lines[index].strip())
                index += 1
            blocks.append(_paragraph(" ".join(paragraph)))
    return {"type": "doc", "content": blocks or [{"type": "paragraph"}]}


def _starts_block(line: str) -> bool:
    stripped = line.strip()
    return bool(
        stripped.startswith(("```", ">", "#"))
        or _BULLET.match(line)
        or _NUMBERED.match(line)
        or _IMAGE_LINE.match(stripped)
        or _RULE.match(stripped)
    )


def _marked(node: dict[str, Any]) -> str:
    text = node.get("text") or ""
    for mark in node.get("marks") or []:
        match mark.get("type"):
            case "strong":
                text = f"**{text}**"
            case "em":
                text = f"*{text}*"
            case "strikethrough":
                text = f"~~{text}~~"
            case "code":
                text = f"`{text}`"
            case "link":
                text = f"[{text}]({(mark.get('attrs') or {}).get('href', '')})"
    return text


def _inline_md(nodes: list[dict[str, Any]]) -> str:
    parts = []
    for node in nodes or []:
        if node.get("type") == "text":
            parts.append(_marked(node))
        elif node.get("type") == "hard_break":
            parts.append("\n")
        else:
            parts.append(_inline_md(node.get("content") or []))
    return "".join(parts)


def _block_md(node: dict[str, Any]) -> str:
    content = node.get("content") or []
    match node.get("type"):
        case "paragraph":
            return _inline_md(content)
        case "heading":
            return "#" * int((node.get("attrs") or {}).get("level") or 1) + " " + _inline_md(content)
        case "bulletList" | "bullet_list":
            return "\n".join(f"- {_block_md({'type': 'doc', 'content': item.get('content')})}" for item in content)
        case "orderedList" | "ordered_list":
            return "\n".join(
                f"{n}. {_block_md({'type': 'doc', 'content': item.get('content')})}"
                for n, item in enumerate(content, 1)
            )
        case "blockquote" | "pullquote":
            return "\n".join(f"> {line}" for line in _block_md({"type": "doc", "content": content}).split("\n"))
        case "code_block":
            return "```\n" + _inline_md(content) + "\n```"
        case "horizontal_rule":
            return "---"
        case "captionedImage" | "image2" | "image":
            image = (
                node
                if node.get("type") != "captionedImage"
                else next((child for child in content if child.get("type") in ("image2", "image")), {})
            )
            attrs = image.get("attrs") or {}
            return f"![{attrs.get('alt') or ''}]({attrs.get('src') or ''})" if attrs.get("src") else ""
        case _:
            blocks = [_block_md(child) for child in content if child.get("type") != "text"]
            return "\n\n".join(block for block in blocks if block) or _inline_md(content)


def to_markdown(doc: dict[str, Any]) -> str:
    """A ProseMirror document as Markdown."""
    blocks = [_block_md(node) for node in doc.get("content") or []]
    return "\n\n".join(block for block in blocks if block).strip()


# Notes have their own editor schema (recorded 17.10.2026): paragraphs only, marks `bold`, `italic` and `link`.
_NOTE_MARKS = {"strong": "bold", "em": "italic", "link": "link"}


def to_note_doc(markdown: str) -> dict[str, Any]:
    """A Note's text as its ProseMirror document: one paragraph per block, unsupported marks dropped."""
    paragraphs = []
    for block in re.split(r"\n\s*\n", markdown.replace("\r\n", "\n").strip()):
        nodes = []
        for node in inline(" ".join(line.strip() for line in block.split("\n"))):
            marks = [
                {**mark, "type": _NOTE_MARKS[mark["type"]]}
                for mark in node.get("marks") or []
                if mark["type"] in _NOTE_MARKS
            ]
            nodes.append(_text(node["text"], marks))
        paragraphs.append({"type": "paragraph", "content": nodes} if nodes else {"type": "paragraph"})
    return {"type": "doc", "attrs": {"schemaVersion": "v1", "title": None}, "content": paragraphs}
