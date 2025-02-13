#!/usr/bin/env python3

import os
import fnmatch
import pyperclip
import argparse
import re
import yaml

from tabulate import tabulate
from token_count import TokenCount
from collections import defaultdict

default_excludes = ["*.pyc", "*egg-info*", "*tmp*", ".DS_Store", ".env*"]


def aggregate_file_contents(
    include_files, exclude_files, ignore_empty_files=False, no_skip=False
):
    result = []
    current_dir = os.getcwd()

    files_included = []
    files_skipped = []

    for root, dirs, files in os.walk(current_dir):
        if "pyvenv.cfg" in files:
            dirs[:] = []
            continue

        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, current_dir)

            if any(
                fnmatch.fnmatch(relative_path, pattern) for pattern in include_files
            ) and not any(
                fnmatch.fnmatch(relative_path, pattern)
                for pattern in exclude_files + default_excludes
            ):

                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                except UnicodeDecodeError:
                    # print(f"Warning: Unable to read {relative_path} as UTF-8. Skipping.")
                    # files_skipped.append(relative_path + " (UnicodeDecodeError)")
                    continue

                if ignore_empty_files and not content.strip():
                    continue

                api_key_found, confidence = has_api_key(content)
                if api_key_found and confidence == "HIGH" and not no_skip:
                    files_skipped.append(
                        relative_path
                        + " (What is very likely to be an API key was found. Run with --no-skip option to ignore this and include the file)"
                    )
                    continue

                elif api_key_found and confidence != "HIGH":
                    print(
                        f"Caution: Is there potentially an API KEY in {relative_path}? A long string of alphanumeric characters was found."
                    )

                files_included.append(relative_path)
                result.append(f"---\nFile: `{relative_path}`\n")

                code_extensions = [
                    ".py",
                    ".json",
                    ".js",
                    ".html",
                    ".css",
                    ".java",
                    ".cpp",
                    ".c",
                    ".h",
                    ".yaml",
                    ".yml",
                ]
                if any(file.endswith(ext) for ext in code_extensions):
                    result.append(f"```\n{content}\n```")
                else:
                    result.append(content)

                result.append("")  # Add an empty line between files

    return "\n".join(result), files_included, files_skipped


def get_metadata(content):
    token_count = TokenCount(model_name="gpt-3.5-turbo").num_tokens_from_string(content)
    char_count = sum(not chr.isspace() for chr in content)

    metadata = [
        ["Tokenizer", "openai/tiktoken"],
        ["Token Count", token_count],
        ["Character Count", char_count],
    ]

    return metadata


def has_api_key(code):

    patterns = [
        # Service-specific patterns
        r"sk_[a-zA-Z0-9]{24,}",  # Stripe secret key
        r"rk_[a-zA-Z0-9]{24,}",  # Stripe restricted key
        r"[A-Za-z0-9_]{21}:[A-Za-z0-9_-]{40}",  # Twitter API key
        r"AIza[0-9A-Za-z-_]{35}",  # Google API key
        r"gh[pousr]_[A-Za-z0-9]{36}",  # GitHub tokens
        r"[0-9a-f]{32}-us[0-9]{1,2}",  # MailChimp API key
        r"xox[baprs]-[0-9]{12}-[0-9]{12}-[0-9a-zA-Z]{24}",  # Slack tokens
        r"aws[_-][a-zA-Z0-9]{20,}",  # AWS access key
        # Common environment variable patterns
        r"(?i)(api[_-]?key|api[_-]?secret|access[_-]?token|auth[_-]?token|client[_-]?secret)['\"]?\s*[:=]\s*['\"]([a-zA-Z0-9-_\.]{32,})['\"]",
        # Bearer token pattern
        r"bearer\s+[a-zA-Z0-9_\-\.]+",  # Bearer token (case insensitive)
    ]

    generic_patterns = [
        r"[a-zA-Z0-9]{32}",  # 32 character alphanumeric (e.g., MD5)
        r"[a-zA-Z0-9]{40}",  # 40 character alphanumeric (e.g., SHA1)
        r"[A-Za-z0-9-_]{64}",  # 64 character alphanumeric with dash/underscore
    ]

    # Make the check case-insensitive for better detection
    for pattern in patterns:
        if re.search(pattern, code, re.IGNORECASE):
            return True, "HIGH"

    for pattern in generic_patterns:
        if re.search(pattern, code, re.IGNORECASE):
            return True, "LOW"

    return False, ""


def print_directory_tree(file_paths):
    def nested_dict():
        return defaultdict(nested_dict)

    tree = nested_dict()

    # Populate the tree structure
    for path in file_paths:
        parts = path.split("/")
        current = tree
        for part in parts:
            current = current[part]

    # Helper function to print the tree
    def print_tree(node, name=".", prefix="", is_last=True):
        print(f"{prefix}{'└── ' if is_last else '├── '}{name}")
        prefix += "    " if is_last else "│   "

        if isinstance(node, defaultdict):
            items = sorted(node.items())
            for i, (child_name, child) in enumerate(items):
                is_last_item = i == len(items) - 1
                print_tree(child, child_name, prefix, is_last_item)

    # Print the tree
    print_tree(tree)


def save_profile(
    profile_name, include_patterns, exclude_patterns, ignore_empty, no_skip
):
    """Save the current configuration as a profile."""
    profile = {
        "include": include_patterns,
        "exclude": exclude_patterns,
        "ignore_empty": ignore_empty,
        "no_skip": no_skip,
    }

    # Create dir if it doesn't exist
    os.makedirs(".promptify", exist_ok=True)

    filename = f".promptify/{profile_name}.profile"
    try:
        with open(filename, "w") as f:
            yaml.dump(profile, f)
        print(f"Profile saved to {filename}")
    except Exception as e:
        print(f"Failed to save profile: {str(e)}")


def load_profile(profile_name):
    """Load configuration from a profile."""
    filename = f".promptify/{profile_name}.profile"
    try:
        with open(filename, "r") as f:
            profile = yaml.safe_load(f)
            print(f"Loaded profile from {filename}\n")
        return profile
    except FileNotFoundError:
        print(f"Profile {filename} not found")
        return None
    except Exception as e:
        print(f"Failed to load profile: {str(e)}")
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Aggregate file contents based on include and exclude patterns."
    )
    parser.add_argument(
        "--include",
        nargs="+",
        default=[
            "*.py",
            "*.html",
            "*.js",
            "*.css",
            "*.json",
            "*.yaml",
            "*.txt",
            "*.md",
        ],
        help="File patterns to include (default: %(default)s)",
    )
    parser.add_argument(
        "--exclude",
        nargs="+",
        default=["*.pyc", "*egg-info*", "*tmp*"],
        help="File patterns to exclude (default: %(default)s)",
    )
    parser.add_argument(
        "--output", type=str, help="Specify the output file name (optional)"
    )
    parser.add_argument(
        "--ignore-empty",
        action="store_true",
        help="Ignore empty files (default: False)",
    )
    parser.add_argument(
        "--no-skip",
        action="store_true",
        help="Will force the inclusion of files that are skipped due to API keys being found",
    )
    parser.add_argument(
        "--export-profile",
        type=str,
        metavar="PROFILE_NAME",
        help="Save current filters and options to a profile",
    )
    parser.add_argument(
        "--profile",
        type=str,
        metavar="PROFILE_NAME",
        help="Load filters and options from a profile",
    )

    args = parser.parse_args()

    # Handle profile loading
    if args.profile:
        profile = load_profile(args.profile)
        if profile:
            args.include = profile["include"]
            args.exclude = profile["exclude"]
            args.ignore_empty = profile["ignore_empty"]
            args.no_skip = profile["no_skip"]

        else:
            return -1

    output, incl_files, skipped_files = aggregate_file_contents(
        args.include, args.exclude, args.ignore_empty, args.no_skip
    )
    metadata = get_metadata(output)

    # Handle profile export
    if args.export_profile:
        save_profile(
            args.export_profile,
            args.include,
            args.exclude,
            args.ignore_empty,
            args.no_skip,
        )

    print(tabulate(metadata))
    print("Files included:")
    print_directory_tree(incl_files)

    if skipped_files:
        print("\nFiles skipped:")
        print_directory_tree(skipped_files)

    clipboard_success = False
    try:
        pyperclip.copy(output)
        pyperclip.paste()  # This line is just to verify the clipboard contents
        print("\nContents copied to clipboard")
        clipboard_success = True
    except Exception as e:
        print(f"\nFailed to copy contents to clipboard: {str(e)}")

    if args.output:
        try:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(output)
            print(f"\nOutput written to {args.output}")
        except Exception as e:
            print(f"\nFailed to write to file: {str(e)}")
    elif not clipboard_success:
        try:
            with open("output.promptify", "w", encoding="utf-8") as f:
                f.write(output)
            print("Output written to output.promptify")
        except Exception as e:
            print(f"\nFailed to write to file: {str(e)}")


if __name__ == "__main__":
    main()
