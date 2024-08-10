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

