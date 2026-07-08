#!/usr/bin/env python3
"""Audit all skills under .agents/skills/ for cross-reference issues.

Scans every SKILL.md and AGENTS.md and reports:

1. **Duplicate sections**: skill names appearing in BOTH a Composition table
   (## Composition by Higher-Level Skills or ## Composition Rationale)
   AND a Related Skills list (## Related Skills).

2. **Missing AGENTS.md**: skill directories with a SKILL.md but no AGENTS.md.

3. **Missing YAML frontmatter**: skills whose SKILL.md does not start with
   `---` + YAML frontmatter block.

4. **Empty Related Skills sections**: skills whose ## Related Skills heading
   is followed by nothing (or only blank lines) before the next heading.

5. **Missing Related Skills sections**: skills that have a Composition table
   but no ## Related Skills section at all.

Usage:
    python3 scripts/audit-cross-refs.py [--skills-dir PATH] [--json] [--fix]

Exit code: 0 if no issues, 1 if issues found.
"""
import argparse
import json
import re
import sys
from pathlib import Path


def find_skill_dirs(root: Path) -> list[Path]:
    """Find all directories containing a SKILL.md file."""
    return sorted(p.parent for p in root.rglob("SKILL.md") if ".bak" not in str(p))


def read_skill(path: Path) -> dict:
    """Read a skill directory and extract structural info."""
    result = {
        "path": str(path),
        "name": path.name,
        "has_sk_md": False,
        "has_agents_md": False,
        "has_yaml_frontmatter": False,
        "composition_names": [],
        "related_names": [],
        "has_related_section": False,
        "related_is_empty": False,
        "composition_by_higher_names": [],
    }

    sk_md = path / "SKILL.md"
    agents_md = path / "AGENTS.md"

    if sk_md.exists():
        result["has_sk_md"] = True
        content = sk_md.read_text()

        # Check YAML frontmatter
        if content.startswith("---\n"):
            end = content.find("\n---\n", 4)
            if end > 0:
                result["has_yaml_frontmatter"] = True

        # Extract Composition sections
        comp_match = re.findall(
            r"## Composition by Higher-Level Skills\s*\n(.*?)(?:\n##|\Z)",
            content,
            re.DOTALL,
        )
        for block in comp_match:
            names = re.findall(r"`([a-z0-9-]+)`", block)
            result["composition_by_higher_names"].extend(names)

        comp_rationale = re.findall(
            r"## Composition Rationale\s*\n(.*?)(?:\n##|\Z)",
            content,
            re.DOTALL,
        )
        # In Composition Rationale, look for explicit composer/consumer references
        for block in comp_rationale:
            names = re.findall(r"`([a-z0-9-]+)`", block)
            result["composition_names"].extend(names)

        # Also check "## Called Composers / Base Skills" and "## Called Base Skills"
        called_sections = re.findall(
            r"## Called (?:Composers / Base Skills|Base Skills)\s*\n(.*?)(?:\n##|\Z)",
            content,
            re.DOTALL,
        )
        for block in called_sections:
            names = re.findall(r"`([a-z0-9-]+)`", block)
            result["composition_names"].extend(names)

        # Extract Related Skills section
        rs_match = re.search(
            r"## Related Skills\s*\n(.*?)(?:\n##|\Z)",
            content,
            re.DOTALL,
        )
        if rs_match:
            result["has_related_section"] = True
            related_block = rs_match.group(1).strip()
            if not related_block or all(
                line.strip() in ("", "---") for line in related_block.split("\n")
            ):
                result["related_is_empty"] = True
            else:
                # Extract skill names from bullets and table cells
                bullets = re.findall(r"`([a-z0-9-]+)`", related_block)
                result["related_names"] = bullets

    if agents_md.exists():
        result["has_agents_md"] = True

    return result


def audit_skills(skills_dir: Path) -> dict:
    """Run all audits and return issues."""
    issues = {
        "duplicate_in_composition_and_related": [],
        "missing_agents_md": [],
        "missing_yaml_frontmatter": [],
        "empty_related_sections": [],
        "missing_related_sections_with_composition": [],
    }

    for skill_dir in find_skill_dirs(skills_dir):
        info = read_skill(skill_dir)

        # 1. Duplicate in Composition + Related
        all_composition = list(
            set(info["composition_names"] + info["composition_by_higher_names"])
        )
        all_related = list(set(info["related_names"]))
        duplicates = [n for n in all_composition if n in all_related]
        if duplicates:
            issues["duplicate_in_composition_and_related"].append(
                {
                    "skill": info["name"],
                    "path": info["path"],
                    "duplicates": duplicates,
                }
            )

        # 2. Missing AGENTS.md
        if not info["has_agents_md"]:
            issues["missing_agents_md"].append(
                {"skill": info["name"], "path": info["path"]}
            )

        # 3. Missing YAML frontmatter
        if not info["has_yaml_frontmatter"]:
            issues["missing_yaml_frontmatter"].append(
                {"skill": info["name"], "path": info["path"]}
            )

        # 4. Empty Related Skills section
        if info["has_related_section"] and info["related_is_empty"]:
            issues["empty_related_sections"].append(
                {"skill": info["name"], "path": info["path"]}
            )

        # 5. Has Composition but missing Related Skills
        has_any_composition = bool(
            info["composition_names"]
            or info["composition_by_higher_names"]
        )
        if has_any_composition and not info["has_related_section"]:
            issues["missing_related_sections_with_composition"].append(
                {"skill": info["name"], "path": info["path"]}
            )

    return issues


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit skill library for cross-reference issues"
    )
    parser.add_argument(
        "--skills-dir",
        default=".agents/skills",
        help="Root directory for skills (default: .agents/skills)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON instead of human-readable report",
    )
    parser.add_argument(
        "--skill-names",
        nargs="+",
        help="Only report issues for skills matching these names",
    )
    args = parser.parse_args()

    skills_dir = Path(args.skills_dir).resolve()
    if not skills_dir.is_dir():
        skills_dir = Path.cwd() / args.skills_dir
    if not skills_dir.is_dir():
        print(f"ERROR: skills directory not found: {skills_dir}", file=sys.stderr)
        return 1

    issues = audit_skills(skills_dir)

    if args.skill_names:
        skill_set = set(args.skill_names)
        filtered = {}
        for category, items in issues.items():
            matched = [
                item for item in items if item.get("skill") in skill_set
            ]
            if matched:
                filtered[category] = matched
        issues = filtered

    if args.json:
        json.dump(issues, sys.stdout, indent=2)
    else:
        all_skills = find_skill_dirs(skills_dir)
        total = sum(len(v) for v in issues.values())
        total_all = sum(
            len(v) for v in audit_skills(skills_dir).values()
        )
        if args.skill_names:
            print(
                f"Audited: {len(all_skills)} skills in {skills_dir}"
                f" (filtered to {', '.join(args.skill_names)})"
            )
        else:
            print(f"Audited: {len(all_skills)} skills in {skills_dir}")
        print(f"Issues found: {total}{' (unfiltered: ' + str(total_all) + ')' if args.skill_names else ''}")
        print()

        for category, items in issues.items():
            label = category.replace("_", " ").title()
            if items:
                print(f"  [{len(items)}] {label}:")
                for item in items:
                    name = item["skill"]
                    if "duplicates" in item:
                        print(f"    - {name}: {', '.join(item['duplicates'])}")
                    else:
                        print(f"    - {name}")
            else:
                print(f"  [0] {label}: NONE")
            print()

    return 1 if any(issues.values()) else 0


if __name__ == "__main__":
    sys.exit(main())
