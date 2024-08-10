#!/usr/bin/env python3

import os
import fnmatch
import pyperclip
import argparse

from tabulate import tabulate
from vertexai.generative_models import GenerativeModel

_supported_models = ['gemini-1.5-flash', 'gemini-1.5-pro']

def aggregate_file_contents(include_files, exclude_files, ignore_empty_files=False):
    result = []
    current_dir = os.getcwd()

    for root, dirs, files in os.walk(current_dir):
        if 'pyvenv.cfg' in files:
            dirs[:] = []
            continue

        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, current_dir)

            if any(fnmatch.fnmatch(relative_path, pattern) for pattern in include_files) and \
               not any(fnmatch.fnmatch(relative_path, pattern) for pattern in exclude_files):
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                except UnicodeDecodeError:
                    print(f"Warning: Unable to read {relative_path} as UTF-8. Skipping.")
                    continue

                if ignore_empty_files and not content.strip():
                    continue

                result.append(f"---\nFile: `{relative_path}`\n")
                
                code_extensions = ['.py', '.json', '.js', '.html', '.css', '.java', '.cpp', '.c', '.h', '.yaml', '.yml']
                if any(file.endswith(ext) for ext in code_extensions):
                    result.append(f"```\n{content}\n```")
                else:
                    result.append(content)
                
                result.append("")  # Add an empty line between files

    return "\n".join(result)

def get_metadata(model_name, content):
    if model_name not in _supported_models:
        raise ValueError("Model not supported. Supported models are 'gemini-1.5-flash' and 'gemini-1.5-pro'.")
    
    model_response = GenerativeModel(model_name).count_tokens(content)

    metadata = [["Model", model_name],
                ["Token Count", model_response.total_tokens],
                ["Billable Character Count", model_response.total_billable_characters]]
    
    return metadata



def main():
    parser = argparse.ArgumentParser(description="Aggregate file contents based on include and exclude patterns.")
    parser.add_argument('--model', default="gemini-1.5-flash",
                        help="Generative model to use (default: %(default)s)")
    parser.add_argument('--include', nargs='+', default=["*.py", "*.html", "*.js", "*.css", "*.json", "*.yaml", "*.txt", "*.md"],
                        help="File patterns to include (default: %(default)s)")
    parser.add_argument('--exclude', nargs='+', default=["*.pyc", "*egg-info*", "*tmp*"],
                        help="File patterns to exclude (default: %(default)s)")
    parser.add_argument('--ignore-empty', action='store_true',
                        help="Ignore empty files (default: False)")

    args = parser.parse_args()

    output = aggregate_file_contents(args.include, args.exclude, args.ignore_empty)
    metadata = get_metadata(args.model, output)

    print(tabulate(metadata))

    try:
        with open("output.md", "w", encoding="utf-8") as f:
            f.write(output)
        
        print("Output written to output.md")
    except Exception as e:
        print(f"Failed to write to file: {str(e)}")

    try:
        pyperclip.copy(output)
        spam = pyperclip.paste()
        print("Contents copied to clipboard")
    except Exception as e:
        print(f"Failed to copy contents to clipboard: {str(e)}")

if __name__ == "__main__":
    main()