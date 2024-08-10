---
File: `requirements.txt`

vertexai==1.60.0
tabulate==0.9.0
pyperclip==1.9.0

---
File: `output.md`

---
File: `requirements.txt`

vertexai==1.60.0
tabulate==0.9.0
pyperclip==1.9.0

---
File: `setup.py`

```
from setuptools import setup, find_packages

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name="promptify",
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
    url="https://github.com/vmehmeri/promptify",
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
    parser.add_argument('--exclude', nargs='+', default=["*.pyc","*tmp*"],
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
```

---
File: `example/hello.py`

```
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

if __name__ == '__main__':
    app.run(debug=True)

```

---
File: `example/utils.py/__init__.py`

```

```

---
File: `promptify.egg-info/SOURCES.txt`

LICENSE
README.md
setup.py
promptify/__init__.py
promptify/main.py
promptify.egg-info/PKG-INFO
promptify.egg-info/SOURCES.txt
promptify.egg-info/dependency_links.txt
promptify.egg-info/entry_points.txt
promptify.egg-info/requires.txt
promptify.egg-info/top_level.txt

---
File: `promptify.egg-info/entry_points.txt`

[console_scripts]
promptify = promptify.main:main


---
File: `promptify.egg-info/requires.txt`

vertexai==1.60.0
tabulate==0.9.0
pyperclip==1.9.0


---
File: `promptify.egg-info/top_level.txt`

promptify


---
File: `promptify.egg-info/dependency_links.txt`





---
File: `README.md`

# Code Promptify

Code-Promptify is a command-line utility for aggregating code repository contents into a single string based on include and exclude patterns. It also provides metadata information, such as token count and billable characters. It is designed to help you prepare prompts for large language models (LLMs). The output is written to a file and also copied to your clipboard automatically.

**Note**: Currently metadata is only provided based on using Gemini 1.5 Pro or Gemini 1.5 Flash models. That is because token count depends on the specific tokenizer used by the model, which differents among models, though not significantly. If you're using a different model, you can still obtain the token count using either model's tokenizer and you will get a decent approximation.

See [example_output.md](example_output.md) for what the output looks like for this repo when running with default settings.

Example metadata output:

| Field                   | Value           |
|-------------------------|-----------------|
| Model                   | gemini-1.5-flash|
| Token Count             | 16746           |
| Billable Character Count| 43197           |



## Features

- Aggregate file contents based on include and exclude patterns (glob strings)
- Automatically ignores virtual environment files
- Option to ignore empty files 
- Count tokens using Google's Vertex AI GenerativeModel
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

- `--model`: Generative model to use for token counting (default: "gemini-1.5-flash")
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

4. Use a different model for token counting:
   ```
   promptify --model "gemini-1.5-pro"
   ```

## Output
See [example_output.md](example_output.md)

## Dependencies

- pyperclip
- tabulate
- google-cloud-aiplatform (for accurate token counting for Gemini models)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.



---
File: `example_output.md`

---
File: `requirements.txt`

google-cloud-aiplatform==1.59.0
tabulate==0.9.0
pyperclip==1.9.0


---
File: `promptify.py`

```
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
    parser.add_argument('--exclude', nargs='+', default=["*test*", "*tmp*"],
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
```

---
File: `output.md`

---
File: `requirements.txt`

google-cloud-aiplatform==1.59.0
tabulate==0.9.0
pyperclip==1.9.0


---
File: `promptify.py`

```
import os
import fnmatch
import pyperclip

from tabulate import tabulate
from vertexai.generative_models import GenerativeModel


gemini_model = GenerativeModel("gemini-1.5-pro")

def aggregate_file_contents(include_files, exclude_files, ignore_empty_files=False):
    result = []
    current_dir = os.path.dirname(os.path.abspath(__file__))

    for root, dirs, files in os.walk(current_dir):
        # Check if pyvenv.cfg exists in the current directory. That indicates a pyenv environment dir.
        if 'pyvenv.cfg' in files:
            # Ignore entire directory
            dirs[:] = []
            print(f"Ignoring directory {root} (it seems to be a pyenv environment)")
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
                
                # Check if the file is a code file
                code_extensions = ['.py', '.json', '.js', '.html', '.css', '.java', '.cpp', '.c', '.h', '.yaml', '.yml']
                if any(file.endswith(ext) for ext in code_extensions):
                    result.append(f"```\n{content}\n```")
                else:
                    result.append(content)
                
                result.append("")  # Add an empty line between files

    return "\n".join(result)

# Example usage:
include_patterns = ["*.py", "*.html", "*.txt", "*.md"]
exclude_patterns = ["*test*", "*tmp*", "*.wav", ".venv/*"]

output = aggregate_file_contents(include_patterns, exclude_patterns)
response = gemini_model.count_tokens(output)

metadata = [["Token Count", response.total_tokens],
            ["Billable Character Count", response.total_billable_characters]]

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
```

---
File: `README.md`

# Promptify


### Example Output (on this Repo)
See [example_output.md](example_output.md)

---
File: `example_output.md`

---
File: `requirements.txt`

google-cloud-aiplatform==1.59.0
tabulate==0.9.0
pyperclip==1.9.0


---
File: `promptify.py`

```
import os
import fnmatch
import pyperclip

from tabulate import tabulate
from vertexai.generative_models import GenerativeModel

gemini_model = GenerativeModel("gemini-1.5-pro")

def aggregate_file_contents(include_files, exclude_files):
    result = []
    current_dir = os.path.dirname(os.path.abspath(__file__))

    for root, _, files in os.walk(current_dir):
        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, current_dir)

            if any(fnmatch.fnmatch(relative_path, pattern) for pattern in include_files) and \
               not any(fnmatch.fnmatch(relative_path, pattern) for pattern in exclude_files):
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                result.append(f"---\nFile: `{relative_path}`\n")
                
                # Check if the file is a code file
                code_extensions = ['.py', '.json', '.js', '.html', '.css', '.java', '.cpp', '.c', '.h', '.yaml', '.yml']
                if any(file.endswith(ext) for ext in code_extensions):
                    result.append(f"```\n{content}\n```")
                else:
                    result.append(content)
                
                result.append("")  # Add an empty line between files

    return "\n".join(result)

# Example usage:
include_patterns = ["*.py", "*.html", "*.txt", "*.md"]
exclude_patterns = ["*test*", "*tmp*", "*.wav", ".venv/*"]



output = aggregate_file_contents(include_patterns, exclude_patterns)
response = gemini_model.count_tokens(output)

metadata = [["Token Count",{response.total_tokens}],
        ["Billable Character Count",{response.total_billable_characters}]]

print(tabulate(metadata))

try:
    with open("output.md", "w", encoding="utf-8") as f:
        f.write(output)
    
    print("Output written to output.md")
except:
    print("Failed to write to file")

try:
    pyperclip.copy(output)
    spam = pyperclip.paste()
    print("Contents copied to clipboard")
except:
    print("Failed to copy contents to clipboard")




```

---
File: `example/hello.py`

```
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

if __name__ == '__main__':
    app.run(debug=True)

```

---
File: `example/utils.py/__init__.py`

```

```

---
File: `example/templates/index.html`

```
<!DOCTYPE html>
<html>
<head>
    <title>Hello, World!</title>
</head>
<body>
    <h1>Hello, World!</h1>
</body>
</html>

```


---
File: `example/hello.py`

```
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

if __name__ == '__main__':
    app.run(debug=True)

```

---
File: `example/utils.py/__init__.py`

```

```

---
File: `example/templates/index.html`

```
<!DOCTYPE html>
<html>
<head>
    <title>Hello, World!</title>
</head>
<body>
    <h1>Hello, World!</h1>
</body>
</html>

```


---
File: `README.md`

# Promptify


### Example Output (on this Repo)
See [example_output.md](example_output.md)

---
File: `example_output.md`

---
File: `requirements.txt`

google-cloud-aiplatform==1.59.0
tabulate==0.9.0
pyperclip==1.9.0


---
File: `promptify.py`

```
import os
import fnmatch
import pyperclip

from tabulate import tabulate
from vertexai.generative_models import GenerativeModel

gemini_model = GenerativeModel("gemini-1.5-pro")

def aggregate_file_contents(include_files, exclude_files):
    result = []
    current_dir = os.path.dirname(os.path.abspath(__file__))

    for root, _, files in os.walk(current_dir):
        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, current_dir)

            if any(fnmatch.fnmatch(relative_path, pattern) for pattern in include_files) and \
               not any(fnmatch.fnmatch(relative_path, pattern) for pattern in exclude_files):
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                result.append(f"---\nFile: `{relative_path}`\n")
                
                # Check if the file is a code file
                code_extensions = ['.py', '.json', '.js', '.html', '.css', '.java', '.cpp', '.c', '.h', '.yaml', '.yml']
                if any(file.endswith(ext) for ext in code_extensions):
                    result.append(f"```\n{content}\n```")
                else:
                    result.append(content)
                
                result.append("")  # Add an empty line between files

    return "\n".join(result)

# Example usage:
include_patterns = ["*.py", "*.html", "*.txt", "*.md"]
exclude_patterns = ["*test*", "*tmp*", "*.wav", ".venv/*"]



output = aggregate_file_contents(include_patterns, exclude_patterns)
response = gemini_model.count_tokens(output)

metadata = [["Token Count",{response.total_tokens}],
        ["Billable Character Count",{response.total_billable_characters}]]

print(tabulate(metadata))

try:
    with open("output.md", "w", encoding="utf-8") as f:
        f.write(output)
    
    print("Output written to output.md")
except:
    print("Failed to write to file")

try:
    pyperclip.copy(output)
    spam = pyperclip.paste()
    print("Contents copied to clipboard")
except:
    print("Failed to copy contents to clipboard")




```

---
File: `example/hello.py`

```
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

if __name__ == '__main__':
    app.run(debug=True)

```

---
File: `example/utils.py/__init__.py`

```

```

---
File: `example/templates/index.html`

```
<!DOCTYPE html>
<html>
<head>
    <title>Hello, World!</title>
</head>
<body>
    <h1>Hello, World!</h1>
</body>
</html>

```


---
File: `example/hello.py`

```
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

if __name__ == '__main__':
    app.run(debug=True)

```

---
File: `example/templates/index.html`

```
<!DOCTYPE html>
<html>
<head>
    <title>Hello, World!</title>
</head>
<body>
    <h1>Hello, World!</h1>
</body>
</html>

```


---
File: `setup.py`

```
from setuptools import setup, find_packages

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name="promptify",
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
    url="https://github.com/vmehmeri/promptify",
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
```

---
File: `example/hello.py`

```
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

if __name__ == '__main__':
    app.run(debug=True)

```

---
File: `example/utils.py/__init__.py`

```

```

---
File: `example/templates/index.html`

```
<!DOCTYPE html>
<html>
<head>
    <title>Hello, World!</title>
</head>
<body>
    <h1>Hello, World!</h1>
</body>
</html>

```
