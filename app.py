import ast
import io
import tokenize
from flask import Flask, render_template, request

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 64 * 1024  # 64 KB source-code limit

CATEGORIES = {
    "beginner": {"label": "Beginner Error", "color": "green", "weight": 2},
    "intermediate": {"label": "Intermediate Error", "color": "yellow", "weight": 4},
    "core": {"label": "Core Programming Error", "color": "orange", "weight": 6},
    "critical": {"label": "Critical Error", "color": "red", "weight": 10},
}


def issue(category, title, message, line=None, suggestion=None, example=None):
    meta = CATEGORIES[category]
    return {
        "category": category,
        "category_label": meta["label"],
        "color": meta["color"],
        "title": title,
        "message": message,
        "line": line,
        "suggestion": suggestion,
        "example": example,
        "weight": meta["weight"],
    }


def analyze_code(source):
    """Analyze Python source with syntax parsing and a small set of teaching rules."""
    findings = []
    if not source.strip():
        return findings, "Enter some Python code first."

    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        syntax_finding = issue(
            "beginner",
            "Python syntax error",
            exc.msg or "Python could not parse this code.",
            exc.lineno,
            "Check indentation, brackets, colons, and spelling near the reported line.",
            "if score > 10:\n    print('Great job!')",
        )
        source_lines = source.splitlines()
        if exc.lineno and 1 <= exc.lineno <= len(source_lines):
            syntax_finding["source_line"] = source_lines[exc.lineno - 1]
        syntax_finding["steps"] = [
            "Start with the reported line number; Python stops parsing when it finds a syntax error.",
            "Check this line and the previous line for a missing colon, bracket, quote, or incorrect indentation.",
            "Use the example as a pattern, correct your own code, and click Analyze code again.",
        ]
        findings.append(syntax_finding)
        return findings, "Python could not analyze the rest of the program until the syntax error is fixed."

    # Lightweight, explainable checks; these are heuristics, not a complete bug detector.
    assigned_names = set()
    loaded_names = []
    function_names = {node.name for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
    class_names = {node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)}
    imported_names = set()
    builtins_names = set(dir(__builtins__)) if not isinstance(__builtins__, dict) else set(__builtins__.keys())

    for node in ast.walk(tree):
        if isinstance(node, (ast.Assign, ast.AnnAssign, ast.NamedExpr)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for target in targets:
                for child in ast.walk(target):
                    if isinstance(child, ast.Name):
                        assigned_names.add(child.id)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            assigned_names.add(node.name)
            for arg in node.args.posonlyargs + node.args.args + node.args.kwonlyargs:
                assigned_names.add(arg.arg)
            if node.args.vararg:
                assigned_names.add(node.args.vararg.arg)
            if node.args.kwarg:
                assigned_names.add(node.args.kwarg.arg)
        elif isinstance(node, ast.ClassDef):
            assigned_names.add(node.name)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            for alias in node.names:
                imported_names.add(alias.asname or alias.name.split(".")[0])
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            loaded_names.append(node)

    known = assigned_names | imported_names | function_names | class_names | builtins_names
    for node in loaded_names:
        if node.id not in known and node.id not in {"self", "cls"}:
            findings.append(issue(
                "intermediate",
                f"Possibly undefined name: {node.id}",
                f"'{node.id}' is used but no assignment or import for that name was found. It may be a typo or a missing variable.",
                getattr(node, "lineno", None),
                f"Define '{node.id}' before using it, or check whether its spelling and scope are correct.",
                f"{node.id} = ...  # assign an appropriate value before using it",
            ))
            known.add(node.id)  # avoid duplicate messages for the same name

    for node in ast.walk(tree):
        if isinstance(node, ast.Compare):
            for op in node.ops:
                if isinstance(op, (ast.Is, ast.IsNot)):
                    findings.append(issue(
                        "core",
                        "Identity comparison",
                        "Using 'is' or 'is not' for value comparison can be incorrect. Identity checks whether two references are the same object.",
                        getattr(node, "lineno", None),
                        "Use '==' or '!=' when comparing ordinary values. Keep 'is None' for None checks.",
                        "if answer == 42:\n    print('Correct')",
                    ))
                    break
        if isinstance(node, ast.ExceptHandler) and node.type is None:
            findings.append(issue(
                "core",
                "Bare except clause",
                "A bare 'except:' catches almost every exception, including exceptions that are usually best left unhandled.",
                getattr(node, "lineno", None),
                "Catch the specific exception you expect, such as ValueError or OSError.",
                "try:\n    number = int(text)\nexcept ValueError:\n    print('Enter a valid number')",
            ))
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "eval":
            findings.append(issue(
                "critical",
                "Use of eval()",
                "eval() executes a string as Python code. Using it with untrusted input can execute unwanted or dangerous operations.",
                getattr(node, "lineno", None),
                "Avoid eval() for user input. Use a safer parser or convert the expected data type directly.",
                "number = int(user_text)",
            ))

    # Simple token-based warning for suspicious assignment in a condition is intentionally omitted:
    # AST syntax differs by language and the app currently analyzes Python only.
    # Remove duplicate findings while preserving order.
    unique = []
    seen = set()
    for item in findings:
        key = (item["category"], item["title"], item["line"])
        if key not in seen:
            seen.add(key)
            unique.append(item)

    if not unique:
        summary = "No issues were detected by the current checks. This does not prove that the program is correct."
    else:
        summary = f"Found {len(unique)} possible issue(s). Review each suggestion; automated checks can miss bugs or flag valid code."
    return unique, summary


@app.route("/", methods=["GET", "POST"])
def index():
    code = ""
    findings = []
    summary = ""
    analyzed = False
    score = None

    if request.method == "POST":
        code = request.form.get("code", "")
        analyzed = True
        findings, summary = analyze_code(code)
        penalty = sum(item["weight"] for item in findings)
        score = max(0, 100 - penalty)

    stats = {
        "total": len(findings),
        "beginner": sum(1 for item in findings if item["category"] == "beginner"),
        "intermediate": sum(1 for item in findings if item["category"] == "intermediate"),
        "core": sum(1 for item in findings if item["category"] == "core"),
        "critical": sum(1 for item in findings if item["category"] == "critical"),
    }
    return render_template(
        "index.html", code=code, findings=findings, summary=summary,
        analyzed=analyzed, score=score, stats=stats
    )


@app.errorhandler(413)
def too_large(_error):
    return "The submitted code is too large. Please keep it under 64 KB.", 413


if __name__ == "__main__":
    # Debug mode is for local development only. Do not enable it in production.
    app.run(debug=True)
