import re, os
from pathlib import Path
from typing import List, Tuple, Optional, Iterable

# ------------------------------------------------------------------
#  Low-level gitignore matcher (ported from CPython's pathlib/_gitignore.py)
# ------------------------------------------------------------------
class _GitIgnoreMatcher:
    __slots__ = ("_regex",)

    def __init__(self, pattern: str) -> None:
        self._regex = self._translate(pattern)

    @staticmethod
    def _translate(pat: str) -> re.Pattern[str]:
        """
        Translate a single gitignore pattern to a compiled regex.
        Handles
          - leading slash (anchored)
          - trailing slash (directory-only)
          - ** wildcards
        """
        original = pat

        # Directory-only marker
        dir_only = pat.endswith("/")
        if dir_only:
            pat = pat[:-1]

        # Anchored pattern?
        anchored = pat.startswith("/")
        if anchored:
            pat = pat[1:]

        # Split into name components
        parts = pat.split("/")
        regex_parts: List[str] = []
        for idx, part in enumerate(parts):
            if part == "**":
                if idx == 0:
                    # Leading **: we will prepend (?s:.*) later
                    continue
                # Internal **: match across directory levels
                regex_parts.append(r"(?:/.+?)*")
            else:
                # Ordinary wildcard translation
                part = re.escape(part)
                part = part.replace(r"\*", "[^/]*")
                part = part.replace(r"\?", "[^/]")
                regex_parts.append("/" + part)

        if anchored:
            # Anchored: path must start from root of pattern's scope
            tail = "".join(regex_parts)
            if tail.startswith("/"):
                tail = tail[1:]  # drop leading /
            regex = f"^{tail}"
        else:
            # Un-anchored: can match at any depth
            tail = "".join(regex_parts)
            if tail.startswith("/"):
                tail = tail[1:]
            regex = f"(?:^|.*/){tail}"

        if dir_only:
            regex += r"(?:/|$)"
        else:
            regex += r"(?:/.*)?$"

        # ** at start means "any prefix"
        if original.startswith("**/"):
            regex = rf"(?s:.*){regex}"
        elif original.startswith("**"):
            pass  # already handled

        return re.compile(regex)

    def __call__(self, path: str) -> bool:
        return bool(self._regex.match(path))


# ------------------------------------------------------------------
#  Public helpers
# ------------------------------------------------------------------
GitIgnorePatterns = List[Tuple[Path, _GitIgnoreMatcher]]

def is_ignored(abs_path: Path, patterns: GitIgnorePatterns) -> bool:
    """
    Decide whether *abs_path* (absolute) is ignored by *patterns*.
    Checks every .gitignore in scope, in the same order Git does
    (inner-most .gitignore wins).
    """
    # Make path relative to the root that was used in load_gitignore_patterns
    # We use POSIX separators to match git's internal format.
    parts: Tuple[str, ...] = abs_path.parts
    for scope_dir, matcher in reversed(patterns):
        try:
            rel = abs_path.relative_to(scope_dir)
        except ValueError:
            continue  # this .gitignore does not apply
        posix_rel = rel.as_posix()
        if matcher(posix_rel):
            return True
    return False

def load_gitignore_patterns(root_dir: Path) -> GitIgnorePatterns:
    """
    Walk *root_dir* **top-down** and collect .gitignore rules **only for
    directories that are not ignored by any parent .gitignore already loaded**.
    Returns a list of (scope_directory, matcher) pairs in the same order
    Git itself would apply them (parent rules first, then child ones).
    """
    patterns: GitIgnorePatterns = []
    # Map directory -> list of matchers that apply to it
    cache: dict[Path, List[Tuple[Path, _GitIgnoreMatcher]]] = {}

    for (dirpath, *_) in os.walk(root_dir, topdown=True):
        parent = Path(dirpath).resolve()

        # Build the list of parent matchers for this directory
        parent_matchers: List[Tuple[Path, _GitIgnoreMatcher]] = []
        for p in parent.parents:
            parent_matchers.extend(cache.get(p, []))
        cache[parent] = parent_matchers.copy()

        if parent == root_dir or not is_ignored(parent, patterns):
            # Directory is *not* ignored: read its .gitignore, if any
            gitignore = parent / ".gitignore"
            if gitignore.is_file():
                with gitignore.open(encoding="utf-8") as fh:
                    for raw in fh:
                        raw = raw.rstrip()
                        if not raw or raw.startswith("#"):
                            continue
                        matcher = _GitIgnoreMatcher(raw)
                        patterns.append((parent, matcher))
                        cache[parent].append((parent, matcher))
    return patterns

def walk_files(root: Path,
               gitignore_patterns,
               ignores: Optional[set[str]] = None
               ) -> Iterable[tuple[Path, str]]:
    """
    Yield (absolute_path, arcname) for every file that should be archived.
    Directories are skipped *before* their contents are visited.
    """
    if ignores is None:
        ignores = set()

    root = root.resolve()

    for dir_path, dir_names, file_names in os.walk(root, topdown=True):
        dir_path = Path(dir_path).resolve()

        # Skip if this directory (or any parent) is already ignored
        if any(p.is_relative_to(root) and p.relative_to(root).as_posix() in ignores for p in dir_path.parents):
            dir_names[:] = []          # do not descend further
            continue

        rel_dir = dir_path.relative_to(root).as_posix()

        # Check .gitignore rules for this directory itself
        if rel_dir and (rel_dir in ignores or is_ignored(dir_path, gitignore_patterns)):
            ignores.add(rel_dir)
            dir_names[:] = []          # prune the walk
            continue

        # Yield files that are *not* ignored
        for name in file_names:
            file_path = dir_path / name
            arcname = str(file_path.relative_to(root))

            if arcname in ignores or is_ignored(file_path, gitignore_patterns):
                continue

            yield file_path, arcname