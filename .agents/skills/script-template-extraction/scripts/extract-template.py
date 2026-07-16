#!/usr/bin/env python3
"""Extract embedded template strings from a Python script into .template files.

Scans a Python script for top-level string assignments (e.g. TEMPLATE = \"\"\"...\"\"\"),
extracts each to a separate <name>.template file alongside the script, and rewrites
the script to read from the template at runtime.

Usage:
    python3 extract-template.py path/to/script.py [--dry-run] [--force]

Output:
    JSON list of {template_name, action} to stdout.
"""
import argparse
import ast
import json
import re
import shutil
import sys
from pathlib import Path


def extract_template_name(var_name: str, default_ext: str = ".template") -> str:
    """Derive a filename from the variable name."""
    name = var_name.lower().replace("_", "-")
    if name == "template":
        return f"content{default_ext}"
    return f"{name}{default_ext}"


def rewrite_script(content: str, replacements: list[tuple[str, str, str]]) -> str:
    """Rewrite the script to read templates from external files.

    replacements: list of (var_name, template_filename, original_value)
    Returns the modified script source.
    """
    lines = content.split("\n")
    result = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Check if this line starts a template assignment
        matched = False
        for var_name, tmpl_file, _ in replacements:
            # Match lines like: VAR_NAME = """...""" or VAR_NAME = '''...'''
            # We need to find the assignment start and skip the entire multi-line string
            stripped = line.strip()
            if stripped.startswith(f"{var_name} = ") or stripped == f"{var_name} =":
                # Check what follows the equals sign
                after_eq = stripped.split("=", 1)[1].strip() if "=" in stripped else ""

                if after_eq.startswith('"""') or after_eq.startswith("'''"):
                    # Single-line string assignment - skip this line
                    matched = True
                    break
                elif after_eq == '"""' or after_eq == "'''" or after_eq == "":
                    # Multi-line string - skip until closing delimiter
                    delim = after_eq if after_eq in ('"""', "'''") else (
                        '"""' if stripped.endswith('"""') else "'''"
                    )
                    if not delim:
                        # Check next line for delimiter
                        if i + 1 < len(lines) and (lines[i + 1].strip().startswith('"""') or lines[i + 1].strip().startswith("'''")):
                            delim = lines[i + 1].strip()[:3]
                            i += 1  # Skip the delimiter line too
                        else:
                            # Just skip the var name line
                            matched = True
                            break

                    # Find closing delimiter
                    j = i + 1
                    found_close = False
                    while j < len(lines):
                        if lines[j].strip().endswith(delim):
                            found_close = True
                            break
                        j += 1

                    if found_close:
                        i = j  # Skip to closing line
                        matched = True
                        break
                    else:
                        # No closing found, just skip this line
                        matched = True
                        break

        if matched:
            i += 1
            continue

        result.append(line)
        i += 1

    new_content = "\n".join(result)

    # Add TEMPLATE_PATH references and import
    for var_name, tmpl_file, _ in replacements:
        # Find where the variable was referenced and replace with TEMPLATE_PATH.read_text()
        # Pattern: replace `VAR_NAME` with `TEMPLATE_PATH.read_text()`
        # But only when it's used as a value reference, not in the assignment

        # Add TEMPLATE_PATH constant after imports
        last_import_line = -1
        for li, line in enumerate(new_content.split("\n")):
            if line.startswith("import ") or line.startswith("from "):
                last_import_line = li

        if last_import_line >= 0:
            lines_list = new_content.split("\n")
            tmpl_path_var = f"{var_name}_PATH"
            # Check if already added
            already = any(tmpl_path_var in line for line in lines_list)
            if not already:
                lines_list.insert(last_import_line + 1, "")
                lines_list.insert(last_import_line + 2, f"{tmpl_path_var} = Path(__file__).parent / \"{tmpl_file}\"")
                new_content = "\n".join(lines_list)

        # Replace references to the variable with read_text() call
        # Be careful not to replace in comments or strings
        new_content = re.sub(
            rf'\b{var_name}\b(?!_PATH)(?!["\'])',
            f"{tmpl_path_var}.read_text()",
            new_content,
        )

    # Ensure pathlib import
    if "from pathlib import Path" not in new_content and "import pathlib" not in new_content:
        # Find last import line
        lines_list = new_content.split("\n")
        insert_at = 0
        for li, line in enumerate(lines_list):
            if line.startswith("import ") or line.startswith("from "):
                insert_at = li + 1
        lines_list.insert(insert_at, "from pathlib import Path")
        new_content = "\n".join(lines_list)

    # Add template-path constants after the pathlib import
    if replacements:
        lines_list = new_content.split("\n")
        insert_at = 0
        for li, line in enumerate(lines_list):
            if "from pathlib import Path" in line or "import pathlib" in line:
                insert_at = li + 1
                break
        for var_name, tmpl_file, _ in replacements:
            tmpl_line = f"\n{var_name}_PATH = Path(__file__).parent / \"{tmpl_file}\""
            if f"{var_name}_PATH" not in new_content:
                lines_list.insert(insert_at, tmpl_line)
                insert_at += 1
        new_content = "\n".join(lines_list)

    return new_content


def extract_templates(script_path: Path, dry_run: bool = False, force: bool = False) -> list[dict]:
    """Extract template strings from a Python script.

    Returns list of {template_name, action} dicts.
    """
    results = []
    original = script_path.read_text()

    try:
        tree = ast.parse(original)
    except SyntaxError as e:
        results.append({"error": f"Syntax error: {e}"})
        return results

    replacements = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if not isinstance(target, ast.Name):
                continue
            var_name = target.id

            # Skip common non-template variables
            if var_name in ("__all__", "__version__", "logger", "parser", "args"):
                continue
            if var_name.startswith("_") or var_name.isupper() is False:
                continue
            if not isinstance(node.value, (ast.Constant, ast.JoinedStr)):
                continue

            value = node.value
            if isinstance(value, ast.Constant) and isinstance(value.value, str):
                content = value.value
            elif isinstance(value, ast.JoinedStr):
                # f-strings - collect parts
                parts = []
                for v in value.values:
                    if isinstance(v, ast.Constant) and isinstance(v.value, str):
                        parts.append(v.value)
                    elif isinstance(v, ast.FormattedValue):
                        parts.append("{?}")
                    else:
                        parts.append("{?}")
                content = "".join(parts)
            else:
                continue

            # Heuristic: only extract if it looks like file content (multi-line, non-trivial)
            if len(content) < 50 and content.count("\n") < 3:
                continue

            if var_name.endswith("_TEMPLATE") or var_name.endswith("_TMPL"):
                tmpl_name = extract_template_name(var_name.replace("_TEMPLATE", "").replace("_TMPL", ""))
            elif var_name == "TEMPLATE":
                tmpl_name = "content.template"
            else:
                tmpl_name = extract_template_name(var_name)

            script_dir = script_path.parent
            tmpl_path = script_dir / tmpl_name

            if tmpl_path.exists() and not force:
                results.append({"template": tmpl_name, "var": var_name, "action": "skipped", "reason": "already exists"})
                continue

            if not dry_run:
                tmpl_path.write_text(content.lstrip("\n"))
                print(f"Wrote {tmpl_path}", file=sys.stderr)

            replacements.append((var_name, tmpl_name, content))
            results.append({"template": tmpl_name, "var": var_name, "action": "extracted", "size": len(content)})

    if replacements and not dry_run:
        new_source = rewrite_script(original, replacements)
        # Create backup
        backup_path = script_path.with_suffix(".py.bak")
        shutil.copy2(script_path, backup_path)
        script_path.write_text(new_source)
        print(f"Updated {script_path} (backup at {backup_path})", file=sys.stderr)
    elif replacements and dry_run:
        for var_name, tmpl_name, _ in replacements:
            results.append({"template": tmpl_name, "var": var_name, "action": "would_extract"})

    return results


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Extract embedded template strings from Python scripts into .template files"
    )
    parser.add_argument("script", nargs="+", help="Python script path(s) to process")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without writing")
    parser.add_argument("--force", action="store_true", help="Overwrite existing .template files")
    parser.add_argument("--recursive", action="store_true", help="Search directories recursively for .py files")
    args = parser.parse_args()

    all_results = []

    for path_str in args.script:
        path = Path(path_str).resolve()

        if args.recursive and path.is_dir():
            for py_file in sorted(path.rglob("*.py")):
                if "__pycache__" in str(py_file):
                    continue
                results = extract_templates(py_file, dry_run=args.dry_run, force=args.force)
                all_results.extend(results)
        elif path.is_file() and path.suffix == ".py":
            results = extract_templates(path, dry_run=args.dry_run, force=args.force)
            all_results.extend(results)
        else:
            all_results.append({"error": f"Not a Python file: {path}"})

    json.dump(all_results, sys.stdout, indent=2)
    return 0 if not any("error" in r for r in all_results) else 1


if __name__ == "__main__":
    sys.exit(main())
