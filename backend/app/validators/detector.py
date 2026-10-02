import re
from collections import Counter

EXTENSION_MAP = {
    ".py": "python",
    ".pyw": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".mjs": "javascript",
    ".cjs": "javascript",
    ".go": "go",
    ".java": "java",
    ".rb": "ruby",
    ".rs": "rust",
    ".cpp": "cpp",
    ".cc": "cpp",
    ".cxx": "cpp",
    ".c": "c",
    ".h": "c",
    ".hpp": "cpp",
    ".cs": "csharp",
    ".php": "php",
    ".swift": "swift",
    ".kt": "kotlin",
    ".kts": "kotlin",
    ".scala": "scala",
    ".r": "r",
    ".R": "r",
}


def detect_languages(diff_content: str) -> list[str]:
    files = re.findall(r'\+\+\+ b/(.+)', diff_content)
    if not files:
        files = re.findall(r'\+\+\+ (.+)', diff_content)

    lang_counts = Counter()
    for filepath in files:
        ext = _get_extension(filepath)
        lang = EXTENSION_MAP.get(ext)
        if lang:
            lang_counts[lang] += 1

    return [lang for lang, _ in lang_counts.most_common()]


def get_primary_language(diff_content: str) -> str | None:
    langs = detect_languages(diff_content)
    return langs[0] if langs else None


def _get_extension(filepath: str) -> str:
    dot = filepath.rfind(".")
    if dot == -1:
        return ""
    return filepath[dot:]
