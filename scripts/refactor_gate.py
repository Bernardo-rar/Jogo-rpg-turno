"""TDD Refactor Gate - Full analysis script."""
import ast
import os


class CleanCodeAnalyzer(ast.NodeVisitor):
    def __init__(self, filepath):
        self.filepath = filepath
        self.issues = []
        self.fn_metrics = []

    def _rel(self):
        base = os.getcwd().replace("\\", "/") + "/"
        return self.filepath.replace(base, "")

    def _fn_body_lines(self, node):
        if not (node.end_lineno and node.lineno):
            return 0
        total = node.end_lineno - node.lineno + 1
        if (node.body and isinstance(node.body[0], ast.Expr)
                and isinstance(node.body[0].value, ast.Constant)
                and isinstance(node.body[0].value.value, str)):
            doc = node.body[0]
            if doc.end_lineno:
                total -= (doc.end_lineno - doc.lineno + 1)
        return total

    def _count_params(self, node):
        args = node.args
        params = [a.arg for a in args.args if a.arg not in ("self", "cls")]
        params += [a.arg for a in args.kwonlyargs]
        return params

    def _check_nesting(self, node, depth):
        max_d = depth
        for child in ast.iter_child_nodes(node):
            nesting_types = (ast.If, ast.For, ast.While, ast.With,
                             ast.Try, ast.ExceptHandler)
            if isinstance(child, nesting_types):
                max_d = max(max_d, self._check_nesting(child, depth + 1))
            else:
                max_d = max(max_d, self._check_nesting(child, depth))
        return max_d

    def visit_FunctionDef(self, node):
        rel = self._rel()
        length = self._fn_body_lines(node)
        params = self._count_params(node)
        nesting = self._check_nesting(node, 0)

        if length > 30:
            self.issues.append(("CRITICAL", f"{rel}:{node.lineno}",
                f'Function "{node.name}" has {length} lines (max 20)'))
        elif length > 20:
            self.issues.append(("HIGH", f"{rel}:{node.lineno}",
                f'Function "{node.name}" has {length} lines (max 20)'))

        if len(params) > 5:
            self.issues.append(("CRITICAL", f"{rel}:{node.lineno}",
                f'Function "{node.name}" has {len(params)} params (max 3): {params}'))
        elif len(params) > 3:
            self.issues.append(("HIGH", f"{rel}:{node.lineno}",
                f'Function "{node.name}" has {len(params)} params (max 3): {params}'))

        if nesting > 4:
            self.issues.append(("CRITICAL", f"{rel}:{node.lineno}",
                f'Function "{node.name}" nesting depth {nesting} (max 3)'))
        elif nesting > 3:
            self.issues.append(("HIGH", f"{rel}:{node.lineno}",
                f'Function "{node.name}" nesting depth {nesting} (max 3)'))

        self.fn_metrics.append({
            "fn": node.name, "lines": length,
            "params": len(params), "nesting": nesting
        })
        self.generic_visit(node)

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_ClassDef(self, node):
        rel = self._rel()
        if node.end_lineno and node.lineno:
            length = node.end_lineno - node.lineno + 1
            if length > 300:
                self.issues.append(("CRITICAL", f"{rel}:{node.lineno}",
                    f'Class "{node.name}" has {length} lines (max 200)'))
            elif length > 200:
                self.issues.append(("HIGH", f"{rel}:{node.lineno}",
                    f'Class "{node.name}" has {length} lines (max 200)'))

        methods = []
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                is_prop = any(
                    isinstance(d, ast.Name) and d.id == "property"
                    for d in (item.decorator_list or [])
                )
                is_dunder = (item.name.startswith("__")
                             and item.name.endswith("__"))
                if not is_prop and not is_dunder:
                    methods.append(item.name)

        if len(methods) > 15:
            self.issues.append(("CRITICAL", f"{rel}:{node.lineno}",
                f'Class "{node.name}" has {len(methods)} methods (max 10)'))
        elif len(methods) > 10:
            self.issues.append(("HIGH", f"{rel}:{node.lineno}",
                f'Class "{node.name}" has {len(methods)} methods (max 10): {methods}'))
        self.generic_visit(node)


class SolidAnalyzer(ast.NodeVisitor):
    def __init__(self, filepath):
        self.filepath = filepath
        self.issues = []

    def _rel(self):
        base = os.getcwd().replace("\\", "/") + "/"
        return self.filepath.replace(base, "")

    def visit_ExceptHandler(self, node):
        rel = self._rel()
        if node.type is None:
            self.issues.append(("HIGH", f"{rel}:{node.lineno}",
                "Bare except: clause (catch specific exception)"))
        elif isinstance(node.type, ast.Name) and node.type.id == "Exception":
            self.issues.append(("MEDIUM", f"{rel}:{node.lineno}",
                "Catches generic Exception"))
        self.generic_visit(node)

    def visit_Call(self, node):
        rel = self._rel()
        if isinstance(node.func, ast.Name) and node.func.id in ("eval", "exec"):
            self.issues.append(("CRITICAL", f"{rel}:{node.lineno}",
                f"Unsafe {node.func.id}() call"))
        self.generic_visit(node)


def check_layer_violations(filepath, source):
    base = os.getcwd().replace("\\", "/") + "/"
    rel = filepath.replace(base, "")
    issues = []
    if "/core/" in filepath:
        for i, line in enumerate(source.split("\n"), 1):
            stripped = line.strip()
            if ("from src.ui" in stripped or "import src.ui" in stripped
                    or "from ui" in stripped):
                issues.append(("CRITICAL", f"{rel}:{i}",
                    f"core/ imports from ui/: {stripped}"))
    return issues


def analyze_file(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            source = f.read()
        tree = ast.parse(source, filename=filepath)

        cc = CleanCodeAnalyzer(filepath)
        cc.visit(tree)

        sol = SolidAnalyzer(filepath)
        sol.visit(tree)

        layer = check_layer_violations(filepath, source)

        line_count = len(source.split("\n"))
        return cc.issues + sol.issues + layer, cc.fn_metrics, line_count
    except SyntaxError as e:
        return [("CRITICAL", filepath, f"SyntaxError: {e}")], [], 0


def main():
    all_issues = []
    notable_files = {}
    total_files = 0
    total_lines = 0

    for root, dirs, files in os.walk("src"):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for f in files:
            if f.endswith(".py") and f != "__init__.py":
                path = os.path.join(root, f).replace("\\", "/")
                issues, metrics, line_count = analyze_file(path)
                all_issues.extend(issues)
                total_files += 1
                total_lines += line_count

                if metrics:
                    largest_fn = max(
                        (m["lines"] for m in metrics), default=0)
                    max_params = max(
                        (m["params"] for m in metrics), default=0)
                    max_nesting = max(
                        (m["nesting"] for m in metrics), default=0)
                    if (largest_fn > 15 or max_params > 3
                            or max_nesting > 3):
                        notable_files[path] = {
                            "lines": line_count,
                            "largest_fn": largest_fn,
                            "max_params": max_params,
                            "max_nesting": max_nesting,
                        }

    sev_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    all_issues.sort(key=lambda x: (sev_order.get(x[0], 9), x[1]))

    counts = {}
    for sev, _, _ in all_issues:
        counts[sev] = counts.get(sev, 0) + 1

    print(f"FILES: {total_files}")
    print(f"LINES: {total_lines}")
    print(f"CRITICAL: {counts.get('CRITICAL', 0)}")
    print(f"HIGH: {counts.get('HIGH', 0)}")
    print(f"MEDIUM: {counts.get('MEDIUM', 0)}")
    print(f"LOW: {counts.get('LOW', 0)}")
    print()

    for sev, loc, msg in all_issues:
        print(f"[{sev}] {loc}: {msg}")

    if notable_files:
        print()
        print("=== FILES APPROACHING LIMITS ===")
        for f, m in sorted(notable_files.items()):
            print(f"  {f}: {m['lines']}L, largest_fn={m['largest_fn']}"
                  f", max_params={m['max_params']}"
                  f", max_nesting={m['max_nesting']}")


if __name__ == "__main__":
    main()
