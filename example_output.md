---
File: `requirements.txt`

tabulate==0.9.0
pyperclip==1.9.0
token-count==0.2.1

---
File: `output.md`

---
File: `requirements.txt`

tabulate==0.9.0
pyperclip==1.9.0
token-count==0.2.1

---
File: `output.md`

---
File: `requirements.txt`

tabulate==0.9.0
pyperclip==1.9.0
token-count==0.2.1

---
File: `README.md`

# Code Promptify

Code-Promptify is a command-line utility for aggregating code repository contents into a single string based on include and exclude patterns. It also provides metadata information, such as token count and billable characters. It is designed to help you prepare prompts for large language models (LLMs). The output is written to a file and also copied to your clipboard automatically.

**Note**: To count tokens, this tool uses the OpenAI tiktoken tokenizer library and should give you accurate results for most GPT models. For other models (Gemini, Llama, Mistral, etc.) the token count may not be 100% precise but it will be a good approximation. That is because the exact token count depends on the specific tokenizer used by the model, which differs among models. 

See [example_output.md](example_output.md) for what the output looks like for this repo when running with default settings.

Example metadata output:

| Field                   | Value           |
|-------------------------|-----------------|
| Tokenizer               | openai/tiktoken |
| Token Count             | 4763            |
| Character Count         | 15695           |

## Features

- Aggregate file contents based on include and exclude patterns (glob strings)
- Automatically ignores virtual environment files
- Option to ignore empty files 
- Output results to a file and clipboard

## Installation using PIP
To install promptify, simply run:

```
pip install code-promptify
```

## Installation from Source 

To install Promptify, follow these steps:

1. Clone the repository:
   ```
   git clone https://github.com/vmehmeri/promptify.git
   cd promptify
   ```

2. Install the package and its dependencies:
   ```
   pip install -e . -r requirements.txt
   ```


## Usage

After installation, you can run Promptify using the following command:

```
promptify [args]
```


### Arguments
- `--include`: File patterns to include (default: `["*.py", "*.html", "*.js", "*.css", "*.json", "*.yaml", "*.txt", "*.md"]`)
- `--exclude`: File patterns to exclude (default: `["*.pyc", "*egg-info*", "*tmp*"]`)
- `--ignore-empty`: Flag to Ignore empty files (default: False)

### Examples

1. Use default settings:
   ```
   promptify
   ```

2. Include only Python and JavaScript files:
   ```
   promptify --include "*.py" "*.js"
   ```

3. Exclude test files and ignore empty files:
   ```
   promptify --exclude "*test*" --ignore-empty
   ```


## Output
See [example_output.md](example_output.md)

## Dependencies

- pyperclip
- tabulate
- token-count

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.



---
File: `example_output.md`

File: `requirements.txt`

tabulate==0.9.0
pyperclip==1.9.0
token-count==0.2.1

---
File: `setup.py`

```
from setuptools import setup, find_packages

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name="code-promptify",
    version="0.1",
    packages=find_packages(),
    install_requires=required,
    entry_points={
        "console_scripts": [
            "promptify=promptify.main:main",
        ],
    },
    author="Victor Dantas",
    author_email="vmehmeri@hotmail.com",
    description="A CLI utility for aggregating file contents",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/vmehmeri/code-promptify",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
```



---
File: `promptify/__init__.py`

```

```

---
File: `promptify/main.py`

```
#!/usr/bin/env python3

import os
import fnmatch
import pyperclip
import argparse

from tabulate import tabulate
from token_count import TokenCount


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

def get_metadata(content):
    token_count = TokenCount(model_name="gpt-3.5-turbo").num_tokens_from_string(content)
    char_count = sum(not chr.isspace() for chr in content)

    metadata = [["Tokenizer", "openai/tiktoken"],
                ["Token Count", token_count],
                ["Character Count", char_count]]
    
    return metadata



def main():
    parser = argparse.ArgumentParser(description="Aggregate file contents based on include and exclude patterns.")
    parser.add_argument('--include', nargs='+', default=["*.py", "*.html", "*.js", "*.css", "*.json", "*.yaml", "*.txt", "*.md"],
                        help="File patterns to include (default: %(default)s)")
    parser.add_argument('--exclude', nargs='+', default=["*.pyc", "*egg-info*", "*tmp*"],
                        help="File patterns to exclude (default: %(default)s)")
    parser.add_argument('--ignore-empty', action='store_true',
                        help="Ignore empty files (default: False)")

    args = parser.parse_args()

    output = aggregate_file_contents(args.include, args.exclude, args.ignore_empty)
    metadata = get_metadata(output)

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
```




---
File: `setup.py`

```
from setuptools import setup, find_packages

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name="code-promptify",
    version="0.2.0",
    packages=find_packages(),
    install_requires=required,
    entry_points={
        "console_scripts": [
            "promptify=promptify.main:main",
        ],
    },
    author="Victor Dantas",
    author_email="vmehmeri@hotmail.com",
    description="A CLI utility for aggregating file contents",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/vmehmeri/code-promptify",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
```

---
File: `promptify/__init__.py`

```
__version__ = "0.2.0"
```

---
File: `promptify/main.py`

```
#!/usr/bin/env python3

import os
import fnmatch
import pyperclip
import argparse

from tabulate import tabulate
from token_count import TokenCount


def aggregate_file_contents(include_files, exclude_files, ignore_empty_files=False):
    result = []
    current_dir = os.getcwd()

    files_included = []

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

                files_included.append(relative_path)
                result.append(f"---\nFile: `{relative_path}`\n")
                
                code_extensions = ['.py', '.json', '.js', '.html', '.css', '.java', '.cpp', '.c', '.h', '.yaml', '.yml']
                if any(file.endswith(ext) for ext in code_extensions):
                    result.append(f"```\n{content}\n```")
                else:
                    result.append(content)
                
                result.append("")  # Add an empty line between files

    return "\n".join(result), files_included

def get_metadata(content, files_included):
    token_count = TokenCount(model_name="gpt-3.5-turbo").num_tokens_from_string(content)
    char_count = sum(not chr.isspace() for chr in content)

    metadata = [["Tokenizer", "openai/tiktoken"],
                ["Token Count", token_count],
                ["Character Count", char_count],
                ["Files Included", ",".join(files_included)]]
    
    return metadata



def main():
    parser = argparse.ArgumentParser(description="Aggregate file contents based on include and exclude patterns.")
    parser.add_argument('--include', nargs='+', default=["*.py", "*.html", "*.js", "*.css", "*.json", "*.yaml", "*.txt", "*.md"],
                        help="File patterns to include (default: %(default)s)")
    parser.add_argument('--exclude', nargs='+', default=["*.pyc", "*egg-info*", "*tmp*"],
                        help="File patterns to exclude (default: %(default)s)")
    parser.add_argument('--ignore-empty', action='store_true',
                        help="Ignore empty files (default: False)")

    args = parser.parse_args()

    output, incl_files = aggregate_file_contents(args.include, args.exclude, args.ignore_empty)
    metadata = get_metadata(output, incl_files)

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
```

---
File: `build/lib/promptify/__init__.py`

```
__version__ = "0.2.0"
```

---
File: `build/lib/promptify/main.py`

```
#!/usr/bin/env python3

import os
import fnmatch
import pyperclip
import argparse

from tabulate import tabulate
from token_count import TokenCount


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

def get_metadata(content):
    token_count = TokenCount(model_name="gpt-3.5-turbo").num_tokens_from_string(content)
    char_count = sum(not chr.isspace() for chr in content)

    metadata = [["Tokenizer", "openai/tiktoken"],
                ["Token Count", token_count],
                ["Character Count", char_count]]
    
    return metadata



def main():
    parser = argparse.ArgumentParser(description="Aggregate file contents based on include and exclude patterns.")
    parser.add_argument('--include', nargs='+', default=["*.py", "*.html", "*.js", "*.css", "*.json", "*.yaml", "*.txt", "*.md"],
                        help="File patterns to include (default: %(default)s)")
    parser.add_argument('--exclude', nargs='+', default=["*.pyc", "*egg-info*", "*tmp*"],
                        help="File patterns to exclude (default: %(default)s)")
    parser.add_argument('--ignore-empty', action='store_true',
                        help="Ignore empty files (default: False)")

    args = parser.parse_args()

    output = aggregate_file_contents(args.include, args.exclude, args.ignore_empty)
    metadata = get_metadata(output)

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
```


---
File: `README.md`

# Code Promptify

Code-Promptify is a command-line utility for aggregating code repository contents into a single string based on include and exclude patterns. It also provides metadata information, such as token count and billable characters. It is designed to help you prepare prompts for large language models (LLMs). The output is written to a file and also copied to your clipboard automatically.

**Note**: To count tokens, this tool uses the OpenAI tiktoken tokenizer library and should give you accurate results for most GPT models. For other models (Gemini, Llama, Mistral, etc.) the token count may not be 100% precise but it will be a good approximation. That is because the exact token count depends on the specific tokenizer used by the model, which differs among models. 

See [example_output.md](example_output.md) for what the output looks like for this repo when running with default settings.

Example metadata output:

| Field                   | Value           |
|-------------------------|-----------------|
| Tokenizer               | openai/tiktoken |
| Token Count             | 4763            |
| Character Count         | 15695           |

## Features

- Aggregate file contents based on include and exclude patterns (glob strings)
- Automatically ignores virtual environment files
- Option to ignore empty files 
- Output results to a file and clipboard

## Installation using PIP
To install promptify, simply run:

```
pip install code-promptify
```

## Installation from Source 

To install Promptify, follow these steps:

1. Clone the repository:
   ```
   git clone https://github.com/vmehmeri/promptify.git
   cd promptify
   ```

2. Install the package and its dependencies:
   ```
   pip install -e . -r requirements.txt
   ```


## Usage

After installation, you can run Promptify using the following command:

```
promptify [args]
```


### Arguments
- `--include`: File patterns to include (default: `["*.py", "*.html", "*.js", "*.css", "*.json", "*.yaml", "*.txt", "*.md"]`)
- `--exclude`: File patterns to exclude (default: `["*.pyc", "*egg-info*", "*tmp*"]`)
- `--ignore-empty`: Flag to Ignore empty files (default: False)

### Examples

1. Use default settings:
   ```
   promptify
   ```

2. Include only Python and JavaScript files:
   ```
   promptify --include "*.py" "*.js"
   ```

3. Exclude test files and ignore empty files:
   ```
   promptify --exclude "*test*" --ignore-empty
   ```


## Output
See [example_output.md](example_output.md)

## Dependencies

- pyperclip
- tabulate
- token-count

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.



---
File: `example_output.md`

File: `requirements.txt`

tabulate==0.9.0
pyperclip==1.9.0
token-count==0.2.1

---
File: `setup.py`

```
from setuptools import setup, find_packages

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name="code-promptify",
    version="0.1",
    packages=find_packages(),
    install_requires=required,
    entry_points={
        "console_scripts": [
            "promptify=promptify.main:main",
        ],
    },
    author="Victor Dantas",
    author_email="vmehmeri@hotmail.com",
    description="A CLI utility for aggregating file contents",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/vmehmeri/code-promptify",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
```



---
File: `promptify/__init__.py`

```

```

---
File: `promptify/main.py`

```
#!/usr/bin/env python3

import os
import fnmatch
import pyperclip
import argparse

from tabulate import tabulate
from token_count import TokenCount


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

def get_metadata(content):
    token_count = TokenCount(model_name="gpt-3.5-turbo").num_tokens_from_string(content)
    char_count = sum(not chr.isspace() for chr in content)

    metadata = [["Tokenizer", "openai/tiktoken"],
                ["Token Count", token_count],
                ["Character Count", char_count]]
    
    return metadata



def main():
    parser = argparse.ArgumentParser(description="Aggregate file contents based on include and exclude patterns.")
    parser.add_argument('--include', nargs='+', default=["*.py", "*.html", "*.js", "*.css", "*.json", "*.yaml", "*.txt", "*.md"],
                        help="File patterns to include (default: %(default)s)")
    parser.add_argument('--exclude', nargs='+', default=["*.pyc", "*egg-info*", "*tmp*"],
                        help="File patterns to exclude (default: %(default)s)")
    parser.add_argument('--ignore-empty', action='store_true',
                        help="Ignore empty files (default: False)")

    args = parser.parse_args()

    output = aggregate_file_contents(args.include, args.exclude, args.ignore_empty)
    metadata = get_metadata(output)

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
```




---
File: `setup.py`

```
from setuptools import setup, find_packages

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name="code-promptify",
    version="0.2.0",
    packages=find_packages(),
    install_requires=required,
    entry_points={
        "console_scripts": [
            "promptify=promptify.main:main",
        ],
    },
    author="Victor Dantas",
    author_email="vmehmeri@hotmail.com",
    description="A CLI utility for aggregating file contents",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/vmehmeri/code-promptify",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
```

---
File: `promptify/__init__.py`

```
__version__ = "0.2.0"
```

---
File: `promptify/main.py`

```
#!/usr/bin/env python3

import os
import fnmatch
import pyperclip
import argparse

from tabulate import tabulate
from token_count import TokenCount
from collections import defaultdict


def aggregate_file_contents(include_files, exclude_files, ignore_empty_files=False):
    result = []
    current_dir = os.getcwd()

    files_included = []

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

                files_included.append(relative_path)
                result.append(f"---\nFile: `{relative_path}`\n")
                
                code_extensions = ['.py', '.json', '.js', '.html', '.css', '.java', '.cpp', '.c', '.h', '.yaml', '.yml']
                if any(file.endswith(ext) for ext in code_extensions):
                    result.append(f"```\n{content}\n```")
                else:
                    result.append(content)
                
                result.append("")  # Add an empty line between files

    return "\n".join(result), files_included

def get_metadata(content):
    token_count = TokenCount(model_name="gpt-3.5-turbo").num_tokens_from_string(content)
    char_count = sum(not chr.isspace() for chr in content)

    metadata = [["Tokenizer", "openai/tiktoken"],
                ["Token Count", token_count],
                ["Character Count", char_count]]
                
    
    return metadata

def print_directory_tree(file_paths):
    # Create a nested dictionary to represent the directory structure
    tree = defaultdict(lambda: defaultdict(dict))

    # Populate the tree structure
    for path in file_paths:
        parts = path.split(os.sep)
        current = tree
        for part in parts[:-1]:
            current = current[part]
        current[parts[-1]] = {}

    # Helper function to print the tree
    def print_tree(node, prefix="", is_last=True):
        for i, (name, subtree) in enumerate(sorted(node.items())):
            is_last_item = i == len(node) - 1
            print(f"{prefix}{'└── ' if is_last_item else '├── '}{name}")
            if subtree:
                print_tree(subtree, prefix + ("    " if is_last_item else "│   "), is_last_item)

    # Print the root directory
    root = list(tree.keys())[0]
    print(root)
    print_tree(tree[root])


def main():
    parser = argparse.ArgumentParser(description="Aggregate file contents based on include and exclude patterns.")
    parser.add_argument('--include', nargs='+', default=["*.py", "*.html", "*.js", "*.css", "*.json", "*.yaml", "*.txt", "*.md"],
                        help="File patterns to include (default: %(default)s)")
    parser.add_argument('--exclude', nargs='+', default=["*.pyc", "*egg-info*", "*tmp*"],
                        help="File patterns to exclude (default: %(default)s)")
    parser.add_argument('--ignore-empty', action='store_true',
                        help="Ignore empty files (default: False)")

    args = parser.parse_args()

    output, incl_files = aggregate_file_contents(args.include, args.exclude, args.ignore_empty)
    metadata = get_metadata(output)

    print(tabulate(metadata))
    print("Files included:")
    print(incl_files)
    #print_directory_tree(incl_files)


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
```

---
File: `build/lib/promptify/__init__.py`

```
__version__ = "0.2.0"
```

---
File: `build/lib/promptify/main.py`

```
#!/usr/bin/env python3

import os
import fnmatch
import pyperclip
import argparse

from tabulate import tabulate
from token_count import TokenCount


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

def get_metadata(content):
    token_count = TokenCount(model_name="gpt-3.5-turbo").num_tokens_from_string(content)
    char_count = sum(not chr.isspace() for chr in content)

    metadata = [["Tokenizer", "openai/tiktoken"],
                ["Token Count", token_count],
                ["Character Count", char_count]]
    
    return metadata



def main():
    parser = argparse.ArgumentParser(description="Aggregate file contents based on include and exclude patterns.")
    parser.add_argument('--include', nargs='+', default=["*.py", "*.html", "*.js", "*.css", "*.json", "*.yaml", "*.txt", "*.md"],
                        help="File patterns to include (default: %(default)s)")
    parser.add_argument('--exclude', nargs='+', default=["*.pyc", "*egg-info*", "*tmp*"],
                        help="File patterns to exclude (default: %(default)s)")
    parser.add_argument('--ignore-empty', action='store_true',
                        help="Ignore empty files (default: False)")

    args = parser.parse_args()

    output = aggregate_file_contents(args.include, args.exclude, args.ignore_empty)
    metadata = get_metadata(output)

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
```


---
File: `README.md`

# Code Promptify

Code-Promptify is a command-line utility for aggregating code repository contents into a single string based on include and exclude patterns. It also provides metadata information, such as token count and billable characters. It is designed to help you prepare prompts for large language models (LLMs). The output is written to a file and also copied to your clipboard automatically.

**Note**: To count tokens, this tool uses the OpenAI tiktoken tokenizer library and should give you accurate results for most GPT models. For other models (Gemini, Llama, Mistral, etc.) the token count may not be 100% precise but it will be a good approximation. That is because the exact token count depends on the specific tokenizer used by the model, which differs among models. 

See [example_output.md](example_output.md) for what the output looks like for this repo when running with default settings.

Example metadata output:

| Field                   | Value           |
|-------------------------|-----------------|
| Tokenizer               | openai/tiktoken |
| Token Count             | 4763            |
| Character Count         | 15695           |

## Features

- Aggregate file contents based on include and exclude patterns (glob strings)
- Automatically ignores virtual environment files
- Option to ignore empty files 
- Output results to a file and clipboard

## Installation using PIP
To install promptify, simply run:

```
pip install code-promptify
```

## Installation from Source 

To install Promptify, follow these steps:

1. Clone the repository:
   ```
   git clone https://github.com/vmehmeri/promptify.git
   cd promptify
   ```

2. Install the package and its dependencies:
   ```
   pip install -e . -r requirements.txt
   ```


## Usage

After installation, you can run Promptify using the following command:

```
promptify [args]
```


### Arguments
- `--include`: File patterns to include (default: `["*.py", "*.html", "*.js", "*.css", "*.json", "*.yaml", "*.txt", "*.md"]`)
- `--exclude`: File patterns to exclude (default: `["*.pyc", "*egg-info*", "*tmp*"]`)
- `--ignore-empty`: Flag to Ignore empty files (default: False)

### Examples

1. Use default settings:
   ```
   promptify
   ```

2. Include only Python and JavaScript files:
   ```
   promptify --include "*.py" "*.js"
   ```

3. Exclude test files and ignore empty files:
   ```
   promptify --exclude "*test*" --ignore-empty
   ```


## Output
See [example_output.md](example_output.md)

## Dependencies

- pyperclip
- tabulate
- token-count

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.



---
File: `example_output.md`

File: `requirements.txt`

tabulate==0.9.0
pyperclip==1.9.0
token-count==0.2.1

---
File: `setup.py`

```
from setuptools import setup, find_packages

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name="code-promptify",
    version="0.1",
    packages=find_packages(),
    install_requires=required,
    entry_points={
        "console_scripts": [
            "promptify=promptify.main:main",
        ],
    },
    author="Victor Dantas",
    author_email="vmehmeri@hotmail.com",
    description="A CLI utility for aggregating file contents",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/vmehmeri/code-promptify",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
```



---
File: `promptify/__init__.py`

```

```

---
File: `promptify/main.py`

```
#!/usr/bin/env python3

import os
import fnmatch
import pyperclip
import argparse

from tabulate import tabulate
from token_count import TokenCount


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

def get_metadata(content):
    token_count = TokenCount(model_name="gpt-3.5-turbo").num_tokens_from_string(content)
    char_count = sum(not chr.isspace() for chr in content)

    metadata = [["Tokenizer", "openai/tiktoken"],
                ["Token Count", token_count],
                ["Character Count", char_count]]
    
    return metadata



def main():
    parser = argparse.ArgumentParser(description="Aggregate file contents based on include and exclude patterns.")
    parser.add_argument('--include', nargs='+', default=["*.py", "*.html", "*.js", "*.css", "*.json", "*.yaml", "*.txt", "*.md"],
                        help="File patterns to include (default: %(default)s)")
    parser.add_argument('--exclude', nargs='+', default=["*.pyc", "*egg-info*", "*tmp*"],
                        help="File patterns to exclude (default: %(default)s)")
    parser.add_argument('--ignore-empty', action='store_true',
                        help="Ignore empty files (default: False)")

    args = parser.parse_args()

    output = aggregate_file_contents(args.include, args.exclude, args.ignore_empty)
    metadata = get_metadata(output)

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
```




---
File: `setup.py`

```
from setuptools import setup, find_packages

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name="code-promptify",
    version="0.2.0",
    packages=find_packages(),
    install_requires=required,
    entry_points={
        "console_scripts": [
            "promptify=promptify.main:main",
        ],
    },
    author="Victor Dantas",
    author_email="vmehmeri@hotmail.com",
    description="A CLI utility for aggregating file contents",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/vmehmeri/code-promptify",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
```

---
File: `promptify/__init__.py`

```
__version__ = "0.2.0"
```

---
File: `promptify/main.py`

```
#!/usr/bin/env python3

import os
import fnmatch
import pyperclip
import argparse

from tabulate import tabulate
from token_count import TokenCount
from collections import defaultdict


def aggregate_file_contents(include_files, exclude_files, ignore_empty_files=False):
    result = []
    current_dir = os.getcwd()

    files_included = []

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

                files_included.append(relative_path)
                result.append(f"---\nFile: `{relative_path}`\n")
                
                code_extensions = ['.py', '.json', '.js', '.html', '.css', '.java', '.cpp', '.c', '.h', '.yaml', '.yml']
                if any(file.endswith(ext) for ext in code_extensions):
                    result.append(f"```\n{content}\n```")
                else:
                    result.append(content)
                
                result.append("")  # Add an empty line between files

    return "\n".join(result), files_included

def get_metadata(content):
    token_count = TokenCount(model_name="gpt-3.5-turbo").num_tokens_from_string(content)
    char_count = sum(not chr.isspace() for chr in content)

    metadata = [["Tokenizer", "openai/tiktoken"],
                ["Token Count", token_count],
                ["Character Count", char_count]]
                
    
    return metadata

def print_directory_tree(file_paths):
    def nested_dict():
        return defaultdict(nested_dict)

    tree = nested_dict()

    # Populate the tree structure
    for path in file_paths:
        parts = path.split('/')
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


def main():
    parser = argparse.ArgumentParser(description="Aggregate file contents based on include and exclude patterns.")
    parser.add_argument('--include', nargs='+', default=["*.py", "*.html", "*.js", "*.css", "*.json", "*.yaml", "*.txt", "*.md"],
                        help="File patterns to include (default: %(default)s)")
    parser.add_argument('--exclude', nargs='+', default=["*.pyc", "*egg-info*", "*tmp*"],
                        help="File patterns to exclude (default: %(default)s)")
    parser.add_argument('--ignore-empty', action='store_true',
                        help="Ignore empty files (default: False)")

    args = parser.parse_args()

    output, incl_files = aggregate_file_contents(args.include, args.exclude, args.ignore_empty)
    metadata = get_metadata(output)

    print(tabulate(metadata))
    print("Files included:")
    #print(incl_files)
    print_directory_tree(incl_files)


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
```

---
File: `build/lib/promptify/__init__.py`

```
__version__ = "0.2.0"
```

---
File: `build/lib/promptify/main.py`

```
#!/usr/bin/env python3

import os
import fnmatch
import pyperclip
import argparse

from tabulate import tabulate
from token_count import TokenCount


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

def get_metadata(content):
    token_count = TokenCount(model_name="gpt-3.5-turbo").num_tokens_from_string(content)
    char_count = sum(not chr.isspace() for chr in content)

    metadata = [["Tokenizer", "openai/tiktoken"],
                ["Token Count", token_count],
                ["Character Count", char_count]]
    
    return metadata



def main():
    parser = argparse.ArgumentParser(description="Aggregate file contents based on include and exclude patterns.")
    parser.add_argument('--include', nargs='+', default=["*.py", "*.html", "*.js", "*.css", "*.json", "*.yaml", "*.txt", "*.md"],
                        help="File patterns to include (default: %(default)s)")
    parser.add_argument('--exclude', nargs='+', default=["*.pyc", "*egg-info*", "*tmp*"],
                        help="File patterns to exclude (default: %(default)s)")
    parser.add_argument('--ignore-empty', action='store_true',
                        help="Ignore empty files (default: False)")

    args = parser.parse_args()

    output = aggregate_file_contents(args.include, args.exclude, args.ignore_empty)
    metadata = get_metadata(output)

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
```
