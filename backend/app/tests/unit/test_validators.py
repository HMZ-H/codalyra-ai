import pytest

from app.validators.python_validator import run_python_checks
from app.validators.javascript_validator import run_javascript_checks
from app.validators.golang_validator import run_golang_checks
from app.validators.security_validator import run_security_checks
from app.validators.detector import detect_languages, get_primary_language


class TestPythonValidator:
    def test_detects_print_statement(self):
        diff = "+++ b/app.py\n+print('debug')\n"
        findings = run_python_checks(diff)
        categories = [f["category"] for f in findings]
        assert "print-statement" in categories

    def test_detects_bare_except(self):
        diff = "+++ b/app.py\n+except:\n"
        findings = run_python_checks(diff)
        categories = [f["category"] for f in findings]
        assert "bare-except" in categories

    def test_ignores_non_python_files(self):
        diff = "+++ b/app.js\n+eval(x)\n"
        findings = run_python_checks(diff)
        assert len(findings) == 0

    def test_ignores_context_lines(self):
        diff = "+++ b/app.py\n result = eval(user_input)\n"
        findings = run_python_checks(diff)
        assert len(findings) == 0

    def test_clean_code_no_findings(self):
        diff = "+++ b/app.py\n+def hello():\n+    return 'world'\n"
        findings = run_python_checks(diff)
        assert len(findings) == 0


class TestJavaScriptValidator:
    def test_detects_eval(self):
        diff = "+++ b/app.js\n+eval(userInput)\n"
        findings = run_javascript_checks(diff)
        categories = [f["category"] for f in findings]
        assert "dangerous-eval" in categories

    def test_detects_innerHTML(self):
        diff = "+++ b/app.js\n+el.innerHTML = data\n"
        findings = run_javascript_checks(diff)
        categories = [f["category"] for f in findings]
        assert "xss-innerHTML" in categories

    def test_detects_var_usage(self):
        diff = "+++ b/app.js\n+var x = 5;\n"
        findings = run_javascript_checks(diff)
        categories = [f["category"] for f in findings]
        assert "var-usage" in categories

    def test_detects_loose_equality(self):
        diff = "+++ b/app.ts\n+if (a == b) {}\n"
        findings = run_javascript_checks(diff)
        categories = [f["category"] for f in findings]
        assert "loose-equality" in categories

    def test_detects_console_log(self):
        diff = "+++ b/app.tsx\n+console.log('debug')\n"
        findings = run_javascript_checks(diff)
        categories = [f["category"] for f in findings]
        assert "console-log" in categories

    def test_ignores_non_js_files(self):
        diff = "+++ b/app.py\n+eval(x)\n"
        findings = run_javascript_checks(diff)
        assert len(findings) == 0

    def test_handles_tsx_files(self):
        diff = "+++ b/Component.tsx\n+eval(x)\n"
        findings = run_javascript_checks(diff)
        assert len(findings) > 0


class TestGolangValidator:
    def test_detects_sql_concatenation(self):
        diff = "+++ b/main.go\n+db, _ := sql.Open(\"postgres\", dsn + userInput)\n"
        findings = run_golang_checks(diff)
        categories = [f["category"] for f in findings]
        assert "sql-concatenation" in categories

    def test_detects_fmt_print(self):
        diff = "+++ b/main.go\n+fmt.Println(\"debug\")\n"
        findings = run_golang_checks(diff)
        categories = [f["category"] for f in findings]
        assert "fmt-print" in categories

    def test_detects_panic(self):
        diff = "+++ b/main.go\n+panic(\"something went wrong\")\n"
        findings = run_golang_checks(diff)
        categories = [f["category"] for f in findings]
        assert "panic-usage" in categories

    def test_detects_hardcoded_secret(self):
        diff = '+++ b/main.go\n+password := "mysecretpassword123"\n'
        findings = run_golang_checks(diff)
        categories = [f["category"] for f in findings]
        assert "hardcoded-secret" in categories

    def test_ignores_non_go_files(self):
        diff = "+++ b/main.py\n+panic(x)\n"
        findings = run_golang_checks(diff)
        assert len(findings) == 0


class TestSecurityValidator:
    def test_detects_api_key(self):
        diff = "+++ b/config.py\n+API_KEY = 'sk-proj-abc123def456ghi789jkl012mno345pqr'\n"
        findings = run_security_checks(diff)
        severity_cats = [(f["severity"], f["category"]) for f in findings]
        assert any(s == "critical" for s, _ in severity_cats)

    def test_detects_eval(self):
        diff = "+++ b/app.py\n+result = eval(user_input)\n"
        findings = run_security_checks(diff)
        categories = [f["category"] for f in findings]
        assert "dangerous-eval" in categories


class TestLanguageDetector:
    def test_detect_python(self):
        diff = "+++ b/app.py\n+hello\n+++ b/utils.py\n+world\n"
        langs = detect_languages(diff)
        assert "python" in langs

    def test_detect_javascript(self):
        diff = "+++ b/app.js\n+hello\n+++ b/index.jsx\n+world\n"
        langs = detect_languages(diff)
        assert "javascript" in langs

    def test_detect_typescript(self):
        diff = "+++ b/app.ts\n+hello\n"
        langs = detect_languages(diff)
        assert "typescript" in langs

    def test_detect_go(self):
        diff = "+++ b/main.go\n+package main\n"
        langs = detect_languages(diff)
        assert "go" in langs

    def test_detect_multiple_languages(self):
        diff = "+++ b/app.py\n+x\n+++ b/main.go\n+y\n+++ b/index.js\n+z\n"
        langs = detect_languages(diff)
        assert len(langs) == 3
        assert set(langs) == {"python", "go", "javascript"}

    def test_sorted_by_count(self):
        diff = "+++ b/a.py\n+x\n+++ b/b.py\n+y\n+++ b/c.py\n+z\n+++ b/app.js\n+w\n"
        langs = detect_languages(diff)
        assert langs[0] == "python"

    def test_unknown_extension_ignored(self):
        diff = "+++ b/Makefile\n+all:\n"
        langs = detect_languages(diff)
        assert len(langs) == 0

    def test_get_primary_language(self):
        diff = "+++ b/app.py\n+x\n+++ b/utils.py\n+y\n"
        assert get_primary_language(diff) == "python"

    def test_get_primary_language_empty(self):
        assert get_primary_language("no diff here") is None
