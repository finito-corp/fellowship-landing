#!/usr/bin/env python3
from __future__ import annotations

import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


class ReferenceParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.references: list[str] = []
        self.ids: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        for key in ("id", "name"):
            if values.get(key):
                self.ids.add(str(values[key]))
        for key in ("href", "src"):
            if values.get(key):
                self.references.append(str(values[key]))


def _page_for_reference(root: Path, source: Path, path: str) -> Path:
    decoded = unquote(path)
    if decoded.startswith("/"):
        target = root / decoded.lstrip("/")
    else:
        target = source.parent / decoded
    if not decoded or decoded.endswith("/"):
        target = target / "index.html"
    return target.resolve()


def validate_site(root: Path) -> list[str]:
    root = root.resolve()
    errors: list[str] = []
    pages = sorted(root.rglob("*.html"))
    if not (root / "index.html").is_file():
        return ["missing index.html"]

    parsed: dict[Path, ReferenceParser] = {}
    for page in pages:
        parser = ReferenceParser()
        parser.feed(page.read_text(encoding="utf-8"))
        parsed[page.resolve()] = parser

    for page, parser in parsed.items():
        for reference in parser.references:
            split = urlsplit(reference)
            if split.scheme or split.netloc or reference.startswith(("mailto:", "tel:", "javascript:")):
                continue
            target = _page_for_reference(root, page, split.path)
            try:
                target.relative_to(root)
            except ValueError:
                errors.append(f"{page.relative_to(root)}: path escapes site: {reference}")
                continue
            if split.path and not target.exists():
                errors.append(f"{page.relative_to(root)}: missing {reference}")
                continue
            fragment_page = target if split.path else page
            if split.fragment and fragment_page.suffix == ".html" and fragment_page.exists():
                target_parser = parsed.get(fragment_page.resolve())
                if target_parser and split.fragment not in target_parser.ids:
                    errors.append(f"{page.relative_to(root)}: missing fragment {reference}")
    return errors


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    errors = validate_site(root)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print(f"static release validated: {len(list(root.rglob('*.html')))} pages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
