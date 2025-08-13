#!/usr/bin/env python3
"""
this script fixes common quality issues including:
- code formatting (black, isort, autopep8, autoflake)
- markdown formatting (line length, trailing whitespace)
- markdown link validation (internal and external)
- python code quality issues
- import organization
"""

import os
import re
import subprocess
import time
from pathlib import Path

import requests


class AutoFixer:

    def __init__(self):
        self.venv_path = "venv"
        self.fixes_applied = 0
        self.errors_encountered = 0
        self.link_report = {
            "total_links": 0,
            "internal_links": 0,
            "external_links": 0,
            "broken_internal": 0,
            "broken_external": 0,
            "broken_links": [],
        }

    def fix_python_code(self) -> bool:
        print("\n🐍 fixing python code...")
        python_files = list(Path(".").rglob("*.py"))
        python_files = [
            f
            for f in python_files
            if not any(
                part.startswith(".") or part in ["venv", "__pycache__", ".venv"]
                for part in f.parts
            )
        ]

        if not python_files:
            print("ℹ️  no python files found to fix")
            return True

        print(f"ℹ️  found {len(python_files)} Python files to fix")

        print("🔧 autoflake - removing unused imports...")
        if self._run_autoflake(python_files):
            self.fixes_applied += 1
            print("✅ autoflake completed")
        else:
            print("⚠️  autoflake had issues")

        print("🔧 autopep8 - fixing code style...")
        if self._run_autopep8(python_files):
            self.fixes_applied += 1
            print("✅ autopep8 completed")
        else:
            print("⚠️  autopep8 had issues")

        print("🔧 isort - organizing imports...")
        if self._run_isort(python_files):
            self.fixes_applied += 1
            print("✅ isort completed")
        else:
            print("⚠️  isort had issues")

        print("🔧 black - applying consistent formatting...")
        if self._run_black(python_files):
            self.fixes_applied += 1
            print("✅ black completed")
        else:
            print("⚠️  black had issues")
        return True

    def _run_autoflake(self, python_files: list[Path]) -> bool:
        try:
            for file_path in python_files:
                cmd = [
                    f"{self.venv_path}/bin/autoflake",
                    "--in-place",
                    "--remove-all-unused-imports",
                    "--remove-unused-variables",
                    str(file_path),
                ]
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    print(f"autoflake warning for {file_path}: {result.stderr}")
            return True
        except Exception as e:
            print(f"autoflake error: {e}")

    def _run_autopep8(self, python_files: list[Path]) -> bool:
        try:
            for file_path in python_files:
                cmd = [
                    f"{self.venv_path}/bin/autopep8",
                    "--in-place",
                    "--aggressive",
                    "--aggressive",
                    str(file_path),
                ]
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    print(f"autopep8 warning for {file_path}: {result.stderr}")
            return True
        except Exception as e:
            print(f"autopep8 error: {e}")

    def _run_isort(self, python_files: list[Path]) -> bool:
        try:
            for file_path in python_files:
                cmd = [f"{self.venv_path}/bin/isort", str(file_path)]
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    print(f"isort warning for {file_path}: {result.stderr}")
            return True
        except Exception as e:
            print(f"isort error: {e}")

    def _run_black(self, python_files: list[Path]) -> bool:
        try:
            import subprocess

            for file_path in python_files:
                cmd = [f"{self.venv_path}/bin/black", str(file_path)]
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    print(f"black warning for {file_path}: {result.stderr}")
            return True
        except Exception as e:
            print(f"black error: {e}")

    def fix_markdown_files(self) -> bool:
        print("\n📝 fixing markdown files...")
        markdown_files = list(Path(".").rglob("*.md"))
        markdown_files = [
            f
            for f in markdown_files
            if not any(
                part.startswith(".") or part in ["venv", "__pycache__", ".venv"]
                for part in f.parts
            )
        ]

        if not markdown_files:
            print("ℹ️  no markdown files found to fix")
            return True

        print(f"ℹ️  found {len(markdown_files)} markdown files to fix")

        print("🔗 checking markdown links...")
        self.check_markdown_links(markdown_files)
        self.fix_common_link_issues(markdown_files)

        for file_path in markdown_files:
            if self.fix_single_markdown_file(file_path):
                self.fixes_applied += 1
        return True

    def check_markdown_links(self, markdown_files: list[Path]) -> None:
        all_links = []

        for file_path in markdown_files:
            links = self.extract_links_from_markdown(file_path)
            for link in links:
                link["source_file"] = file_path
                all_links.append(link)

        if not all_links:
            print("ℹ️  no links found in markdown files")
            return

        self.link_report["total_links"] = len(all_links)
        print(f"ℹ️  found {len(all_links)} links to check")

        internal_links = [link for link in all_links if not link["is_external"]]
        self.link_report["internal_links"] = len(internal_links)
        if internal_links:
            print(f"🔍 checking {len(internal_links)} internal links...")
            self.check_internal_links(internal_links)

        external_links = [link for link in all_links if link["is_external"]]
        self.link_report["external_links"] = len(external_links)
        if external_links:
            print(f"🌐 checking {len(external_links)} external links...")
            self.check_external_links(external_links)

    def extract_links_from_markdown(self, file_path: Path) -> list[dict]:
        links = []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            link_pattern = r"\[([^\]]+)\]\(([^)]+)\)"
            matches = re.findall(link_pattern, content)

            for text, url in matches:
                is_external = url.startswith(("http://", "https://", "mailto:"))

                links.append(
                    {
                        "text": text.strip(),
                        "url": url.strip(),
                        "is_external": is_external,
                        "line_number": self.get_line_number_for_link(
                            content, text, url
                        ),
                    }
                )

        except Exception as e:
            print(f"❌ error reading {file_path}: {e}")

        return links

    def get_line_number_for_link(self, content: str, text: str, url: str) -> int:
        """Get the line number where a link appears"""
        lines = content.split("\n")
        for i, line in enumerate(lines, 1):
            if f"[{text}]({url})" in line:
                return i
        return 0

    def check_internal_links(self, internal_links: list[dict]) -> None:
        broken_links = []

        for link in internal_links:
            source_file = link["source_file"]
            url = link["url"]
            text = link["text"]
            line_num = link["line_number"]

            if url.startswith("../"):
                target_path = source_file.parent.parent / url[3:]
            elif url.startswith("./"):
                target_path = source_file.parent / url[2:]
            else:
                target_path = source_file.parent / url

            if not target_path.exists():
                broken_link_info = {
                    "source_file": source_file,
                    "text": text,
                    "url": url,
                    "line_number": line_num,
                    "target_path": target_path,
                    "issue": "File not found",
                    "type": "internal",
                }
                broken_links.append(broken_link_info)
                self.link_report["broken_links"].append(broken_link_info)

        self.link_report["broken_internal"] = len(broken_links)
        if broken_links:
            print(f"❌ found {len(broken_links)} broken internal links:")
            for link in broken_links:
                print(
                    f"  - {link['source_file']}:{link['line_number']} - '{link['text']}' -> {link['url']} ({link['issue']})"
                )
        else:
            print("✅ all internal links are valid")

    def check_external_links(self, external_links: list[dict]) -> None:
        broken_links = []
        checked_count = 0

        for link in external_links:
            url = link["url"]
            text = link["text"]
            source_file = link["source_file"]
            line_num = link["line_number"]

            try:
                time.sleep(0.1)

                response = requests.head(url, timeout=10, allow_redirects=True)
                checked_count += 1

                if response.status_code >= 400:
                    if (
                        response.status_code == 429
                        or response.status_code == 403
                        or response.status_code == 443
                    ):
                        if checked_count % 10 == 0:
                            print(
                                f"  checked {checked_count}/{len(external_links)} external links..."
                            )
                        continue

                    broken_link_info = {
                        "source_file": source_file,
                        "text": text,
                        "url": url,
                        "line_number": line_num,
                        "status_code": response.status_code,
                        "issue": f"HTTP {response.status_code}",
                        "type": "external",
                    }
                    broken_links.append(broken_link_info)
                    self.link_report["broken_links"].append(broken_link_info)

                if checked_count % 10 == 0:
                    print(
                        f"  checked {checked_count}/{len(external_links)} external links..."
                    )

            except requests.exceptions.RequestException as e:
                broken_link_info = {
                    "source_file": source_file,
                    "text": text,
                    "url": url,
                    "line_number": line_num,
                    "issue": f"Connection error: {str(e)}",
                    "type": "external",
                }
                broken_links.append(broken_link_info)
                self.link_report["broken_links"].append(broken_link_info)
            except Exception as e:
                broken_link_info = {
                    "source_file": source_file,
                    "text": text,
                    "url": url,
                    "line_number": line_num,
                    "issue": f"Error: {str(e)}",
                    "type": "external",
                }
                broken_links.append(broken_link_info)
                self.link_report["broken_links"].append(broken_link_info)

        self.link_report["broken_external"] = len(broken_links)
        if broken_links:
            print(f"❌ found {len(broken_links)} broken external links:")
            for link in broken_links:
                print(
                    f"  - {link['source_file']}:{link['line_number']} - '{link['text']}' -> {link['url']} ({link['issue']})"
                )
        else:
            print("✅ all external links are accessible")

        print(f"ℹ️  checked {checked_count} external links")

    def fix_common_link_issues(self, markdown_files: list[Path]) -> None:
        """Fix common link issues in markdown files"""
        print("🔧 fixing common link issues...")
        fixed_count = 0

        for file_path in markdown_files:
            if self.fix_links_in_file(file_path):
                fixed_count += 1

        if fixed_count > 0:
            print(f"✅ fixed links in {fixed_count} files")
            self.fixes_applied += 1
        else:
            print("ℹ️  no link issues found to fix")

    def fix_links_in_file(self, file_path: Path) -> bool:
        """Fix common link issues in a single markdown file"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            changes_made = False
            eth_pattern = r"([a-zA-Z0-9]+\.eth)"
            if re.search(eth_pattern, content):
                content = re.sub(eth_pattern, r"\1".replace(".eth", ""), content)
                changes_made = True

            double_space_pattern = r"\[([^\]]+)\]\(([^)]+)\)"

            def fix_spaces(match):
                text = match.group(1).strip()
                url = match.group(2).strip()
                if text != match.group(1) or url != match.group(2):
                    return f"[{text}]({url})"
                return match.group(0)

            new_content = re.sub(double_space_pattern, fix_spaces, content)
            if new_content != content:
                content = new_content
                changes_made = True

            if changes_made:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"  🔧 fixed links in {file_path}")
                return True

        except Exception as e:
            print(f"❌ error fixing links in {file_path}: {e}")

        return False

    def fix_single_markdown_file(self, file_path: Path) -> bool:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            lines.copy()
            fixed_lines = []
            changes_made = False
            in_code_block = False

            for _, line in enumerate(lines):
                line = line.rstrip()

                if not line.strip():
                    fixed_lines.append("\n")
                    continue

                if line.startswith("```"):
                    in_code_block = not in_code_block
                    fixed_lines.append(line + "\n")
                    continue

                if in_code_block:
                    fixed_lines.append(line + "\n")
                    continue

                if line.strip().startswith(("- ", "* ", "+ ", "1. ")):
                    if len(line) > 120:
                        broken_line = self._break_list_item(line)
                        if broken_line != line:
                            changes_made = True
                            print(f"  breaking long list item in {file_path}")
                        fixed_lines.append(broken_line + "\n")
                    else:
                        fixed_lines.append(line + "\n")
                    continue

                if len(line) > 120:
                    broken_lines = self.break_long_line(line)
                    if broken_lines != line:
                        changes_made = True
                        print(
                            f"  breaking long line in {file_path}: {len(line)} chars -> {len(broken_lines.split(chr(10))[0])} chars"
                        )

                    for broken_line in broken_lines.split("\n"):
                        if broken_line.strip():
                            fixed_lines.append(broken_line + "\n")
                        else:
                            fixed_lines.append("\n")
                else:
                    fixed_lines.append(line + "\n")

            if changes_made:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.writelines(fixed_lines)
                print(f"  ✅ fixed {file_path}")
                return True
            else:
                print(f"  ℹ️  no changes needed in {file_path}")

        except Exception as e:
            print(f"❌ error fixing {file_path}: {e}")
            self.errors_encountered += 1

    def break_long_line(self, line: str) -> str:
        if len(line) <= 120:
            return line

        if ". " in line:
            parts = line.split(". ")
            if len(parts[0]) <= 120:
                remaining = ". ".join(parts[1:])
                if len(remaining) <= 120:
                    return parts[0] + ". " + remaining
                else:
                    broken_remaining = self._break_at_words(remaining)
                    return parts[0] + ".\n" + broken_remaining
        return self._break_at_words(line)

    def _break_at_words(self, line: str) -> str:
        words = line.split()
        result = []
        current_line = ""

        for word in words:
            if current_line and len(current_line + " " + word) > 120:
                if current_line:
                    result.append(current_line)
                current_line = word
            else:
                if current_line:
                    current_line += " " + word
                else:
                    current_line = word

        if current_line:
            result.append(current_line)

        return "\n".join(result)

    def _break_list_item(self, line: str) -> str:
        marker_end = 0
        for i, char in enumerate(line):
            if char in "-*+" or (char.isdigit() and line[i + 1 : i + 3] == ". "):
                marker_end = line.find(" ", i)
                if marker_end == -1:
                    marker_end = len(line)
                break

        if marker_end == 0:
            return self.break_long_line(line)

        marker = line[: marker_end + 1]
        content = line[marker_end + 1 :]

        if len(content) <= 120 - len(marker):
            return line

        broken_content = self._break_at_words(content)
        if "\n" in broken_content:
            indent = " " * len(marker)
            lines = broken_content.split("\n")
            result = [marker + lines[0]]
            for continuation_line in lines[1:]:
                result.append(indent + continuation_line)
            return "\n".join(result)

        return line

    def fix_trailing_whitespace(self) -> bool:
        print("\n🧹 fixing trailing whitespace...")

        text_extensions = {".py", ".md", ".txt", ".rst", ".yml", ".yaml", ".json"}
        files_fixed = 0

        for root, dirs, files in os.walk("."):
            dirs[:] = [
                d
                for d in dirs
                if not d.startswith(".")
                and d not in ["venv", "__pycache__", ".venv", "node_modules"]
            ]

            for file in files:
                if any(file.endswith(ext) for ext in text_extensions):
                    file_path = os.path.join(root, file)
                    if self.fix_file_trailing_whitespace(file_path):
                        files_fixed += 1

        if files_fixed > 0:
            self.fixes_applied += 1
            print(f"ℹ️  fixed trailing whitespace in {files_fixed} files")
        return True

    def fix_file_trailing_whitespace(self, file_path: str) -> bool:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            original_lines = lines.copy()
            fixed_lines = []

            for line in lines:
                fixed_line = line.rstrip() + "\n"
                fixed_lines.append(fixed_line)

            if fixed_lines != original_lines:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.writelines(fixed_lines)
                print(f"ℹ️  fixed trailing whitespace in {file_path}")
                return True

        except Exception as e:
            print(f"warning: could not fix {file_path}: {e}")

    def run_all_fixes(self) -> bool:
        print("🚀 starting auto-fix process...")
        success = True
        success &= self.fix_trailing_whitespace()
        success &= self.fix_python_code()
        success &= self.fix_markdown_files()
        return success

    def print_summary(self):
        print("\n" + "=" * 50)
        print("🎯 AUTO-FIX SUMMARY")
        print("=" * 50)
        print(f"✅ fixes applied: {self.fixes_applied}")
        print(f"❌ errors encountered: {self.errors_encountered}")

        if self.link_report["total_links"] > 0:
            print("\n🔗 LINK CHECK SUMMARY")
            print("-" * 30)
            print(f"📊 total links found: {self.link_report['total_links']}")
            print(f"🔍 internal links: {self.link_report['internal_links']}")
            print(f"🌐 external links: {self.link_report['external_links']}")
            print(f"❌ broken internal: {self.link_report['broken_internal']}")
            print(f"❌ broken external: {self.link_report['broken_external']}")

            if self.link_report["broken_links"]:
                print(f"\n⚠️  broken links found:")
                for link in self.link_report["broken_links"]:
                    print(
                        f"  - {link['source_file']}:{link['line_number']} - '{link['text']}' -> {link['url']} ({link['issue']})"
                    )

        if (
            self.errors_encountered == 0
            and self.link_report["broken_internal"] == 0
            and self.link_report["broken_external"] == 0
        ):
            print("\n🎉 all fixes completed successfully and all links are working!")
        elif self.errors_encountered == 0:
            print(f"\n✅ all fixes completed successfully!")
            print(
                f"⚠️  but {self.link_report['broken_internal'] + self.link_report['broken_external']} broken links were found"
            )
        else:
            print(f"\n⚠️  {self.errors_encountered} errors occurred during fixing")


def main():
    fixer = AutoFixer()
    fixer.run_all_fixes()
    fixer.print_summary()


if __name__ == "__main__":
    main()
