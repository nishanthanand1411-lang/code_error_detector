# Smart Code Learning Assistant

A beginner-friendly Flask web app that analyzes Python source code, explains selected issues in plain language, offers correction tips, and displays a simple learning score.

> **Tagline:** Not just finding errors, but teaching programmers how to fix them.

## Features

- Python syntax-error reporting with line numbers where available.
- Small set of rule-based checks for possibly undefined names, identity comparisons, bare `except:` clauses, and `eval()`.
- Color-coded Beginner, Intermediate, Core, and Critical categories.
- Beginner-friendly explanations and illustrative suggestions.
- A simple learning score based on weighted findings.
- Responsive interface, sample-code button, and clear-editor control.
- No execution of submitted source code.

## Technology stack

- Python and Flask
- Python `ast` module for parsing and selected static checks
- HTML, CSS, and JavaScript
- Jinja templates

## Run locally

1. Install Python 3.10 or later.
2. Clone the repository and enter its folder:

   ```bash
   git clone https://github.com/nishanthanand1411-lang/code_error_detector.git
   cd code_error_detector
   ```

3. Create and activate a virtual environment:

   **Windows PowerShell**
   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   **macOS/Linux**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

4. Install dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

5. Start the app:

   ```bash
   python app.py
   ```

6. Open `http://127.0.0.1:5000` in your browser.

## How it works

1. Paste Python code into the editor and submit it.
2. Flask receives the code and passes it to the analyzer.
3. Python's AST parser checks whether the code is syntactically valid.
4. If parsing succeeds, the app runs a small set of static-analysis heuristics.
5. Findings are categorized and returned with explanations and suggestions.
6. The page displays findings, category counts, and an application-defined learning score.

## Important limitations

This is an educational prototype, not a complete compiler, linter, or security scanner. It can miss bugs and may report false positives. Logical correctness usually depends on the program's intended behavior and test cases. The score is a simple weighted indicator, not a validated measure of programming ability.

Submitted code is analyzed but **not executed** by the application. Do not paste passwords, API keys, personal data, or confidential source code. The built-in Flask development server and debug mode are intended for local development only; use a production WSGI server and appropriate security controls before deployment.

## Project structure

```text
code_error_detector/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── templates/
│   └── index.html
└── static/
    ├── css/
    │   └── style.css
    └── js/
        └── script.js
```

## Future improvements

- Add more language-aware static analysis rules.
- Add unit and integration tests.
- Store analysis history with explicit privacy controls.
- Improve code editor diagnostics and line highlighting.
- Evaluate detection precision and recall against a labeled test set.
- Add optional AI-assisted explanations with suitable safeguards.

## License

No license has been selected yet. Add a `LICENSE` file before explicitly permitting reuse or redistribution.
