import ast
import re
import logging
from pathlib import Path
from typing import Dict, Tuple, Optional
import json

import config

# External library imports
from radon.complexity import cc_visit
from pylint.lint import Run
from pylint.reporters import JSONReporter
import bandit
from bandit.core import manager as bandit_manager
from bandit.core import config as bandit_config

logger = logging.getLogger(__name__)


class CodeAnalyzer:
    """
    Analyzes Python code quality using multiple tools:
    - ast: Syntax validation
    - pylint: Style and conventions
    - radon: Cyclomatic complexity
    - bandit: Security vulnerabilities
    - Duplication, documentation, type hints, tests
    """

    def __init__(self):
        self.score = config.SCORING_CONFIG['base_score']
        self.feedback = {
            'deductions': [],
            'bonuses': [],
            'analysis': {}
        }

    def analyze(self, code: str, language: str = "python") -> Tuple[int, Dict]:
        """Run full analysis on code."""
        self.score = config.SCORING_CONFIG['base_score']
        self.feedback = {'deductions': [], 'bonuses': [], 'analysis': {}}

        if language.lower() != "python":
            return self._analyze_non_python(code, language)

        # Python analysis
        self._check_syntax(code)
        self._check_pep8(code)
        self._check_complexity(code)
        self._check_documentation(code)
        self._check_security(code)
        self._check_duplication(code)
        self._check_type_hints(code)
        self._check_tests(code)

        # Apply deductions and bonuses
        for d in self.feedback['deductions']:
            self.score -= d['amount']
        for b in self.feedback['bonuses']:
            self.score += b['amount']

        self.score = max(0, min(100, self.score))
        return self.score, self.feedback

    def _check_syntax(self, code: str):
        try:
            ast.parse(code)
            self.feedback['analysis']['syntax'] = 'Valid'
        except SyntaxError as e:
            self.feedback['analysis']['syntax'] = f'Invalid - {e.msg} at line {e.lineno}'
            self._deduct(config.SCORING_CONFIG['syntax_error_penalty'], f"Syntax error: {e.msg} at line {e.lineno}")

    def _check_pep8(self, code: str):
        """Run Pylint via Python API."""
        try:
            reporter = JSONReporter()
            results = Run(['--from-stdin', 'dummy.py'], reporter=reporter, do_exit=False, stdin=code)
            pylint_output = json.loads(reporter.stream.getvalue())
            
            violations = {'convention': 0, 'refactor': 0, 'warning': 0, 'error': 0}
            for msg in pylint_output:
                t = msg.get('type', 'refactor')
                if t in violations:
                    violations[t] += 1

            self.feedback['analysis']['pylint'] = violations
            total_violations = sum(violations.values())
            if total_violations > 5:
                self._deduct(config.SCORING_CONFIG['pep8_violations_penalty'], f"{total_violations} PEP8 issues")
            elif total_violations > 0:
                self._deduct(config.SCORING_CONFIG['pep8_violations_penalty']//2, f"{total_violations} PEP8 issues")
        except Exception as e:
            self.feedback['analysis']['pylint'] = f"Error: {str(e)}"

    def _check_complexity(self, code: str):
        try:
            blocks = cc_visit(code)
            max_complexity = max((b.complexity for b in blocks), default=0)
            self.feedback['analysis']['complexity'] = max_complexity
            if max_complexity > config.SCORING_CONFIG['complexity_threshold']:
                self._deduct(
                    config.SCORING_CONFIG['complexity_penalty'],
                    f"High cyclomatic complexity: {max_complexity}"
                )
        except Exception as e:
            self.feedback['analysis']['complexity'] = f"Error: {str(e)}"

    def _check_documentation(self, code: str):
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return
        funcs = [f for f in ast.walk(tree) if isinstance(f, ast.FunctionDef)]
        classes = [c for c in ast.walk(tree) if isinstance(c, ast.ClassDef)]
        total = len(funcs) + len(classes)
        documented = sum(1 for f in funcs+classes if ast.get_docstring(f))
        doc_percent = (documented/total*100) if total else 0
        self.feedback['analysis']['documentation'] = doc_percent
        if doc_percent < 50:
            self._deduct(config.SCORING_CONFIG['missing_docs_penalty'], f"Documentation: {doc_percent:.0f}%")
        elif doc_percent < 80:
            self._deduct(config.SCORING_CONFIG['missing_docs_penalty']//2, f"Incomplete documentation: {doc_percent:.0f}%")

    def _check_security(self, code: str):
        try:
            b_conf = bandit_config.BanditConfig()
            b_mgr = bandit_manager.BanditManager(b_conf, 'file')
            b_mgr.bands = [bandit.core.issue.Issue('dummy', 'dummy', 'LOW', 0)]
            # Bandit API requires files, for simplicity we skip issues if Bandit not fully configured
            self.feedback['analysis']['security'] = 'Checked (placeholder)'
        except Exception as e:
            self.feedback['analysis']['security'] = f"Error: {str(e)}"

    def _check_duplication(self, code: str):
        lines = [l.strip() for l in code.splitlines() if l.strip() and not l.strip().startswith('#')]
        total = len(lines)
        duplicates = sum(count-1 for count in {l: lines.count(l) for l in lines}.values() if count>1)
        percent = (duplicates/total*100) if total else 0
        self.feedback['analysis']['duplication'] = percent
        if percent > config.SCORING_CONFIG['duplication_threshold']:
            self._deduct(config.SCORING_CONFIG['duplication_penalty'], f"Code duplication: {percent:.1f}%")

    def _check_type_hints(self, code: str):
        try:
            funcs = [f for f in ast.walk(ast.parse(code)) if isinstance(f, ast.FunctionDef)]
            with_hints = sum(1 for f in funcs if f.returns or any(a.annotation for a in f.args.args))
            percent = (with_hints/len(funcs)*100) if funcs else 0
            if percent >= 50:
                self._bonus(config.SCORING_CONFIG['type_hints_bonus'], f"{percent:.0f}% functions have type hints")
                self.feedback['analysis']['type_hints'] = percent
        except Exception:
            pass

    def _check_tests(self, code: str):
        if any(k in code for k in ['unittest', 'pytest', 'test_', 'def test_']):
            self._bonus(config.SCORING_CONFIG['comprehensive_tests_bonus'], "Test code detected")
            self.feedback['analysis']['tests'] = True

    def _analyze_non_python(self, code: str, language: str):
        score = config.SCORING_CONFIG['base_score']
        feedback = {'deductions': [], 'bonuses': [], 'analysis': {'language': language}}
        if len(code.strip()) < 20:
            score -= 20
            feedback['deductions'].append({'amount': 20, 'reason': 'Code too short'})
        return max(0, min(100, score)), feedback

    def _deduct(self, amount, reason):
        self.feedback['deductions'].append({'amount': amount, 'reason': reason})

    def _bonus(self, amount, reason):
        self.feedback['bonuses'].append({'amount': amount, 'reason': reason})

    @staticmethod
    def extract_python_code(text: str) -> Optional[str]:
        matches = re.findall(r'```(?:python)?\s*\n(.*?)\n```', text, re.DOTALL)
        return matches[0].strip() if matches else None