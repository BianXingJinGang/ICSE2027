#!/usr/bin/env python3
"""Python 3.6-compatible generic issue-code probe executor.

This stage extracts fenced Python snippets from public issue text and executes
them as observe-first probes on visible-passing candidate repositories. It is
gold-blind: it does not read developer patches, hidden tests, test_patch,
FAIL_TO_PASS, or PASS_TO_PASS.
"""

from __future__ import print_function

import argparse
import datetime as _dt
import hashlib
import json
import os
import re
import subprocess
import sys
import time


GOLD_FIELDS = set(["patch", "test_patch", "FAIL_TO_PASS", "PASS_TO_PASS"])
MAX_STREAM_CHARS = 4096
MAX_CODE_CHARS = 9000
PYTHON_LANGS = set(["python", "py", "python3", "python-repl", "pycon", ""])


def utc_now():
    return _dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def safe_id(value):
    return re.sub(r"[^A-Za-z0-9_.-]+", "__", value or "unknown")[:180]


def assert_no_gold(value, path):
    if isinstance(value, dict):
        leaked = sorted(GOLD_FIELDS.intersection(value.keys()))
        if leaked:
            raise RuntimeError("%s contains gold fields: %s" % (path, leaked))
        for key, child in value.items():
            assert_no_gold(child, "%s.%s" % (path, key))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            assert_no_gold(child, "%s[%s]" % (path, index))


def read_jsonl(path):
    records = []
    with open(path, "r", encoding="utf-8-sig") as handle:
        for line_no, line in enumerate(handle, 1):
            stripped = line.strip()
            if not stripped:
                continue
            record = json.loads(stripped)
            assert_no_gold(record, "%s:%s" % (path, line_no))
            if record.get("gold_used") is not False:
                raise RuntimeError("%s:%s must carry gold_used=false" % (path, line_no))
            records.append(record)
    return records


def read_json(path):
    with open(path, "r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def load_task_env_routes(path):
    if not path:
        return {}
    if not os.path.exists(path):
        raise RuntimeError("missing task env map: %s" % path)
    value = read_json(path)
    assert_no_gold(value, "task_env_map")
    if value.get("gold_used") is not False:
        raise RuntimeError("task env map must carry gold_used=false")
    routes = value.get("routes", value)
    if not isinstance(routes, dict):
        raise RuntimeError("task env map routes must be a dict")
    return routes


def task_route(task_routes, task_id):
    route = {}
    default_route = task_routes.get("*")
    if isinstance(default_route, dict):
        route.update(default_route)
    specific = task_routes.get(task_id)
    if isinstance(specific, dict):
        route.update(specific)
    return route


def route_venv_dir(default_venv_dir, route):
    return route.get("venv_dir") or default_venv_dir


def write_json(path, value):
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")


def write_text(path, value):
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(value)


def append_jsonl(path, value):
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(value, ensure_ascii=False, sort_keys=True) + "\n")


def read_text(path):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as handle:
            return handle.read()
    except IOError:
        return ""


def truncate_stream(value):
    if len(value) <= MAX_STREAM_CHARS:
        return value, False
    return value[:MAX_STREAM_CHARS], True


def stream_record(path, value):
    write_text(path, value)
    data = value.encode("utf-8", "replace")
    return {
        "path": path,
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
    }


def python_path(venv_dir):
    candidate = os.path.join(venv_dir, "bin", "python") if venv_dir else ""
    if candidate and os.path.exists(candidate):
        return candidate
    return sys.executable


def probe_env(venv_dir, gpu):
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    env["CUDA_VISIBLE_DEVICES"] = str(gpu)
    env["PYTHONPATH"] = "src:lib:."
    env["MPLBACKEND"] = "Agg"
    env["PYTHONWARNINGS"] = "ignore"
    if venv_dir:
        venv_bin = os.path.join(venv_dir, "bin")
        if os.path.isdir(venv_bin):
            env["PATH"] = venv_bin + os.pathsep + env.get("PATH", "")
    return env


def materialized_manifest(apply_queue_dir):
    path = os.path.join(apply_queue_dir, "materialized_candidate_manifest.jsonl")
    if os.path.exists(path):
        return read_jsonl(path)
    return []


def by_candidate_id(records):
    out = {}
    for record in records:
        candidate_id = record.get("candidate_id")
        if candidate_id:
            out[candidate_id] = record
    return out


def issue_path(candidate_meta):
    context_path = candidate_meta.get("context_path") or ""
    if not context_path:
        return ""
    return os.path.join(os.path.dirname(context_path), "issue.md")


def strip_doctest_prompts(code):
    lines = code.splitlines()
    prompt_count = len([line for line in lines if line.lstrip().startswith(">>>")])
    if not prompt_count:
        return code
    out = []
    for line in lines:
        stripped = line.lstrip()
        indent = line[: len(line) - len(stripped)]
        if stripped.startswith(">>> "):
            out.append(indent + stripped[4:])
        elif stripped == ">>>":
            out.append("")
        elif stripped.startswith("... "):
            out.append(indent + stripped[4:])
        elif stripped == "...":
            out.append("")
        elif stripped.startswith("#") or not stripped:
            out.append(line)
    return "\n".join(out) + "\n"


def looks_like_python(code):
    stripped = code.strip()
    if not stripped:
        return False
    if len(stripped) > MAX_CODE_CHARS:
        return False
    lowered = stripped.lower()
    reject = [
        "traceback (most recent call last)",
        "pip install ",
        "conda install ",
        "python setup.py",
        "git clone ",
        "$ ",
        ">>> pip ",
    ]
    if any(item in lowered for item in reject):
        return False
    signals = [
        r"\bimport\s+[A-Za-z_]",
        r"\bfrom\s+[A-Za-z_].*\bimport\b",
        r"\bdef\s+[A-Za-z_]",
        r"\bclass\s+[A-Za-z_]",
        r"\bprint\s*\(",
        r"\bassert\s+",
        r"=",
    ]
    return any(re.search(pattern, stripped) for pattern in signals)


def extract_fenced_code(issue_text, max_probes):
    probes = []
    pattern = re.compile(r"```([A-Za-z0-9_.+-]*)[^\n]*\n(.*?)```", re.DOTALL)
    for index, match in enumerate(pattern.finditer(issue_text or "")):
        lang = (match.group(1) or "").strip().lower()
        raw = match.group(2) or ""
        if lang not in PYTHON_LANGS and lang not in ("", "text"):
            continue
        code = strip_doctest_prompts(raw).strip() + "\n"
        if not looks_like_python(code):
            continue
        digest = hashlib.sha256(code.encode("utf-8", "replace")).hexdigest()[:12]
        probes.append(
            {
                "probe_id": "issue-codeblock-%02d-%s" % (index, digest),
                "description": "Execute fenced Python issue reproducer code block %d." % index,
                "code": code,
                "language": lang or "unlabeled",
                "code_block_index": index,
                "code_sha256": hashlib.sha256(code.encode("utf-8", "replace")).hexdigest(),
                "probe_generation_strategy": "issue_fenced_code_block",
            }
        )
        if max_probes and len(probes) >= max_probes:
            break
    return probes


def missing_attribute(issue_text):
    patterns = [
        r"has no attribute ['\"]([A-Za-z_][A-Za-z0-9_]*)['\"]",
        r"attribute ['`]([A-Za-z_][A-Za-z0-9_]*)['`]",
    ]
    for pattern in patterns:
        match = re.search(pattern, issue_text or "")
        if match:
            return match.group(1)
    return ""


def template_active_probes(task_id, templates, issue_text):
    probes = []
    templates = set(templates or [])
    if "cached_eval_context_sensitive_key" in templates:
        code = r'''
import os
import sys
import textwrap
import types
from typing import Any, Dict

path = os.path.join(os.getcwd(), "src/_pytest/mark/evaluate.py")
text = open(path, encoding="utf-8", errors="replace").read()
start = text.index("def cached_eval")
end = text.index("\n\nclass ", start)
source = textwrap.dedent(text[start:end])

pytest_pkg = types.ModuleType("_pytest")
code_mod = types.ModuleType("_pytest._code")
code_mod.compile = compile
pytest_pkg._code = code_mod
sys.modules["_pytest"] = pytest_pkg
sys.modules["_pytest._code"] = code_mod

class Config:
    def __init__(self):
        self._store = {}

ns = {"Any": Any, "Config": Config, "Dict": Dict, "evalcache_key": object()}
exec(source, ns)
cached_eval = ns["cached_eval"]

config = Config()
print("first", cached_eval(config, "flag", {"flag": True}))
print("second", cached_eval(config, "flag", {"flag": False}))
'''
        probes.append(active_probe("cached-eval-context-key", code, "Exercise skipif/xfail cached_eval with two different globals."))
    if "flask_config_from_file_mode_parameter" in templates:
        code = r'''
import errno
import os
import tempfile
import textwrap
import typing as t

path = os.path.join(os.getcwd(), "src/flask/config.py")
text = open(path, encoding="utf-8", errors="replace").read()
start = text.index("    def from_file(")
end = text.index("\n    def from_mapping", start)
source = textwrap.dedent(text[start:end])

ns = {"os": os, "errno": errno, "t": t}
exec(source, ns)

root = tempfile.mkdtemp(prefix="patchcourt_flask_config_")
path = os.path.join(root, "config.bin")
with open(path, "wb") as handle:
    handle.write(b"VALUE=1")

class Config(dict):
    root_path = root

    def from_mapping(self, mapping=None, **kwargs):
        if mapping:
            for key, value in mapping.items():
                if key.isupper():
                    self[key] = value
        for key, value in kwargs.items():
            if key.isupper():
                self[key] = value
        return True

Config.from_file = ns["from_file"]
config = Config()

def load(handle):
    data = handle.read()
    print("read_type", type(data).__name__)
    return {"VALUE": data == b"VALUE=1"}

print("loaded", config.from_file("config.bin", load=load, mode="rb"))
print("value", config["VALUE"])
'''
        probes.append(active_probe("flask-from-file-mode", code, "Load a Flask config file through the mode parameter."))
    if "flask_routes_show_subdomain_column" in templates:
        code = r'''
import os

path = os.path.join(os.getcwd(), "src/flask/cli.py")
text = open(path, encoding="utf-8", errors="replace").read()
start = text.index("def routes_command(sort: str, all_methods: bool) -> None:")
end = text.index("\n\ncli = FlaskGroup", start)
function = text[start:end]
has_domain_header = '"Domain"' in function or '"Subdomain"' in function
uses_subdomain = "rule.subdomain" in function or "getattr(rule, 'host'" in function
formats_four_columns = "row.format(domain, rule.endpoint, methods, rule.rule)" in function
print("has_domain_header", has_domain_header)
print("uses_subdomain", uses_subdomain)
print("formats_four_columns", formats_four_columns)
assert has_domain_header
assert uses_subdomain
assert formats_four_columns
'''
        probes.append(active_probe("flask-routes-show-subdomain-column", code, "Check flask routes includes domain or subdomain information in the CLI table."))
    if "qdp_case_insensitive_command_parser" in templates:
        code = r'''
import os
import re
import textwrap

path = os.path.join(os.getcwd(), "astropy/io/ascii/qdp.py")
text = open(path, encoding="utf-8", errors="replace").read()
start = text.index("def _line_type")
end = text.index("\n\ndef _get_type_from_list_of_lines", start)
source = textwrap.dedent(text[start:end])
ns = {"re": re}
exec(source, ns)
_line_type = ns["_line_type"]

print("lower", _line_type("read serr 1 2"))
print("mixed", _line_type("Read Terr 1"))
'''
        probes.append(active_probe("qdp-lowercase-command", code, "Parse lower/mixed-case QDP READ commands."))
    if "labelencoder_empty_transform_guard" in templates:
        code = r'''
import os
import textwrap
import numpy as np

path = os.path.join(os.getcwd(), "sklearn/preprocessing/label.py")
text = open(path, encoding="utf-8", errors="replace").read()
start = text.index("    def transform(self, y):")
end = text.index("\n    def inverse_transform", start)
method_source = textwrap.indent(textwrap.dedent(text[start:end]), "    ")

def check_is_fitted(obj, attr):
    if not hasattr(obj, attr):
        raise AttributeError(attr)

def column_or_1d(y, warn=True):
    return np.ravel(np.asarray(y))

ns = {
    "np": np,
    "check_is_fitted": check_is_fitted,
    "column_or_1d": column_or_1d,
}
exec("class MiniLabelEncoder:\n" + method_source, ns)

encoder = ns["MiniLabelEncoder"]()
encoder.classes_ = np.array(["a", "b"])
result = encoder.transform([])
print("empty_len", len(result))
print("empty_list", list(result))
'''
        probes.append(active_probe("labelencoder-empty-transform", code, "Transform an empty list after fitting string labels."))
    if "missing_attribute_getattr_fallback" in templates:
        attr = missing_attribute(issue_text) or "_facecolors2d"
        code = r'''
import os
import textwrap

path = os.path.join(os.getcwd(), "lib/mpl_toolkits/mplot3d/art3d.py")
text = open(path, encoding="utf-8", errors="replace").read()
class_start = text.index("class Poly3DCollection")
start = text.index("    def get_facecolor(self):", class_start)
end = text.index("\n\n\ndef poly_collection_2d_to_3d", start)
method_source = textwrap.indent(textwrap.dedent(text[start:end]), "    ")

class PolyCollection:
    @staticmethod
    def get_facecolor(obj):
        return obj._facecolor3d

    @staticmethod
    def get_edgecolor(obj):
        return obj._edgecolor3d

ns = {"PolyCollection": PolyCollection}
exec("class MiniPoly3DCollection:\n" + method_source, ns)
poly = ns["MiniPoly3DCollection"]()
poly._facecolor3d = ("face3d",)
poly._edgecolor3d = ("edge3d",)
print("facecolor", poly.get_facecolor())
print("edgecolor", poly.get_edgecolor())
print("has_attr", hasattr(poly, "%s"))
''' % attr
        probes.append(active_probe("missing-attribute-fallback", code, "Exercise getter before the 2D color cache exists."))
    if "pytest_importlib_parent_preinsert" in templates:
        code = r'''
import importlib
import importlib.util
import os
import re
import sys
import tempfile
from enum import Enum
from pathlib import Path
from types import ModuleType
from typing import Dict, Union

path = os.path.join(os.getcwd(), "src/_pytest/pathlib.py")
text = open(path, encoding="utf-8", errors="replace").read()

def extract_function(name):
    start = text.index("def %s(" % name)
    match = re.search(r"\ndef [A-Za-z_]", text[start + 1:])
    end = start + 1 + match.start() if match else len(text)
    return text[start:end]

source = "\n\n".join([
    extract_function("module_name_from_path"),
    extract_function("insert_missing_modules"),
    extract_function("import_path"),
])

class ImportMode(Enum):
    prepend = "prepend"
    append = "append"
    importlib = "importlib"

class ImportPathMismatchError(ImportError):
    pass

def assert_never(value):
    raise AssertionError(value)

def resolve_package_path(path):
    return None

def _is_same(left, right):
    return os.path.samefile(left, right)

ns = {
    "Dict": Dict,
    "Enum": Enum,
    "ImportMode": ImportMode,
    "ImportPathMismatchError": ImportPathMismatchError,
    "ModuleType": ModuleType,
    "Path": Path,
    "Union": Union,
    "assert_never": assert_never,
    "importlib": importlib,
    "os": os,
    "resolve_package_path": resolve_package_path,
    "sys": sys,
}
exec(source, ns)

root = tempfile.mkdtemp(prefix="patchcourt_pytest_importlib_")
mod_path = Path(root) / "tests" / "unit" / "test_commands.py"
mod_path.parent.mkdir(parents=True)
mod_path.write_text(
    "import sys\n"
    "PARENT_SEEN = ('tests' in sys.modules, 'tests.unit' in sys.modules)\n",
    encoding="utf-8",
)
old_meta_path = sys.meta_path[:]
try:
    sys.meta_path = []
    mod = ns["import_path"](mod_path, mode=ImportMode.importlib, root=Path(root))
finally:
    sys.meta_path = old_meta_path
print("parent_seen", mod.PARENT_SEEN)
assert mod.PARENT_SEEN == (True, True)
'''
        probes.append(active_probe("pytest-importlib-parent-preinsert", code, "Import an importlib-mode test module whose parents must exist during execution."))
    if "pytest_skip_module_level_message_mentions_allow_flag" in templates:
        code = r'''
import os

path = os.path.join(os.getcwd(), "src/_pytest/python.py")
text = open(path, encoding="utf-8", errors="replace").read()
start = text.index("            raise self.CollectError(")
end = text.index("        self.config.pluginmanager.consider_module(mod)", start)
block = text[start:end]
mentions_allow_flag = "allow_module_level=True" in block
keeps_skip_guidance = "pytest.skip" in block
print("mentions_allow_module_level", mentions_allow_flag)
print("keeps_skip_guidance", keeps_skip_guidance)
assert mentions_allow_flag
assert keeps_skip_guidance
'''
        probes.append(active_probe("pytest-skip-module-message-allow-flag", code, "Check module-level pytest.skip guidance mentions allow_module_level=True."))
    if "pylint_namespace_package_no_missing_init" in templates:
        code = r'''
import os
import re
import sys
import tempfile
from typing import Pattern, Sequence

path = os.path.join(os.getcwd(), "pylint/lint/expand_modules.py")
text = open(path, encoding="utf-8", errors="replace").read()
start = text.index("def expand_modules(")
match = re.search(r"\ndef [A-Za-z_]", text[start + 1:])
end = start + 1 + match.start() if match else len(text)
source = text[start:end]

def _is_ignored_file(*args, **kwargs):
    return False

def _is_in_ignore_list_re(*args, **kwargs):
    return False

def get_python_path(value):
    return os.path.dirname(os.path.abspath(value))

def _modpath_from_file(file_path, is_namespace, path=None):
    return [os.path.splitext(os.path.basename(file_path))[0]]

class Modutils:
    @staticmethod
    def modpath_from_file(value, path=None):
        raise ImportError(value)

    @staticmethod
    def file_info_from_modpath(value, path=None):
        raise ImportError(value)

    @staticmethod
    def is_namespace(value):
        return False

    @staticmethod
    def is_directory(value):
        return False

    @staticmethod
    def get_module_files(dirname, ignore_list, list_all=False):
        return [
            os.path.join(dirname, "a.py"),
            os.path.join(dirname, "b.py"),
        ]

ns = {
    "ErrorDescriptionDict": dict,
    "ModuleDescriptionDict": dict,
    "Pattern": Pattern,
    "Sequence": Sequence,
    "_is_ignored_file": _is_ignored_file,
    "_is_in_ignore_list_re": _is_in_ignore_list_re,
    "_modpath_from_file": _modpath_from_file,
    "get_python_path": get_python_path,
    "modutils": Modutils,
    "os": os,
    "sys": sys,
}
exec(source, ns)

root = tempfile.mkdtemp(prefix="patchcourt_pylint_ns_")
pkg = os.path.join(root, "a")
os.makedirs(pkg)
open(os.path.join(pkg, "a.py"), "w").close()
open(os.path.join(pkg, "b.py"), "w").close()
result, errors = ns["expand_modules"]([pkg], [], [], [])
paths = [item["path"] for item in result]
print("paths", paths)
print("errors", errors)
assert not any(path.endswith("__init__.py") for path in paths)
'''
        probes.append(active_probe("pylint-namespace-no-missing-init", code, "Expand an implicit namespace package without scheduling a missing __init__.py."))
    if "sympy_point_left_scalar_multiplication" in templates:
        code = r'''
import os
import textwrap

path = os.path.join(os.getcwd(), "sympy/geometry/point.py")
text = open(path, encoding="utf-8", errors="replace").read()
start = text.index("    def __mul__(self, factor):")
end = text.index("\n    def __neg__(self):", start)
method_source = textwrap.indent(textwrap.dedent(text[start:end]), "    ")

def sympify(value):
    return value

def simplify(value):
    return value

ns = {"simplify": simplify, "sympify": sympify}
prefix = """
class Point:
    def __init__(self, *coords, **kwargs):
        if len(coords) == 1 and isinstance(coords[0], (list, tuple)):
            coords = tuple(coords[0])
        self.args = tuple(coords)
    def __repr__(self):
        return 'Point%s' % (self.args,)
"""
exec(prefix + method_source, ns)
Point = ns["Point"]
result = 2 * Point(1, 2)
print("left_mul", result)
assert result.args == (2, 4)
'''
        probes.append(active_probe("sympy-point-left-scalar-mul", code, "Multiply a geometry Point by a scalar on the left."))
    if "matplotlib_bar_all_nan_convert_dx" in templates:
        code = r'''
import os
import textwrap
import numpy as np

path = os.path.join(os.getcwd(), "lib/matplotlib/axes/_axes.py")
text = open(path, encoding="utf-8", errors="replace").read()
start = text.index("    def _convert_dx(dx, x0, xconv, convert):")
end = text.index("\n    @_preprocess_data", start)
method_source = textwrap.indent(textwrap.dedent(text[start:end]), "    ")

class Cbook:
    @staticmethod
    def _safe_first_finite(values):
        for value in values:
            try:
                if np.isfinite(value):
                    return value
            except TypeError:
                return value
        raise StopIteration

ns = {"cbook": Cbook, "np": np}
exec("class MiniAxes:\n" + method_source, ns)
result = ns["MiniAxes"]._convert_dx([np.nan], [np.nan], np.array([np.nan]), lambda value: np.asarray(value))
print("converted", result)
assert len(result) == 1
'''
        probes.append(active_probe("matplotlib-bar-all-nan-convert-dx", code, "Convert all-NaN bar dimensions without leaking StopIteration."))
    if "seaborn_pairplot_hue_order_filter" in templates:
        code = r'''
import os

path = os.path.join(os.getcwd(), "seaborn/axisgrid.py")
text = open(path, encoding="utf-8", errors="replace").read()
start = text.index("def pairplot(")
end = text.index("    # Set up the PairGrid", start)
setup_source = text[start:end]
has_filter = "hue_order is not None" in setup_source and ".isin" in setup_source
print("has_hue_order_filter", has_filter)
assert has_filter
'''
        probes.append(active_probe("seaborn-pairplot-hue-order-filter", code, "Check that pairplot filters rows outside a requested hue_order subset before PairGrid construction."))
    if "pylint_unrecognized_option_no_traceback" in templates:
        code = r'''
import os

path = os.path.join(os.getcwd(), "pylint/config/config_initialization.py")
text = open(path, encoding="utf-8", errors="replace").read()
start = text.index("    # Check if there are any options that we do not recognize")
end = text.index("    # Set the current module to configuration", start)
block = text[start:end]
raises_raw_unrecognized = "raise _UnrecognizedOptionError(options=unrecognized_options)" in block
has_non_traceback_exit = "sys.exit(32)" in block or "return []" in block or "parsed_args_list = []" in block
print("raises_raw_unrecognized", raises_raw_unrecognized)
print("has_non_traceback_exit", has_non_traceback_exit)
assert not raises_raw_unrecognized and has_non_traceback_exit
'''
        probes.append(active_probe("pylint-unrecognized-option-no-traceback", code, "Check that command-line unrecognized options do not re-raise the internal exception."))
    if "requests_socket_error_wrapped_connection_error" in templates:
        code = r'''
import os

path = os.path.join(os.getcwd(), "requests/models.py")
text = open(path, encoding="utf-8", errors="replace").read()
start = text.index("    def iter_content(self, chunk_size=1, decode_unicode=False):")
end = text.index("\n    def iter_lines", start)
method = text[start:end]
print("has_socket_import", "import socket" in text)
print("has_connection_error", "ConnectionError" in text)
print("wraps_socket_error", "socket.error" in method or "OSError" in method)
assert "import socket" in text
assert "ConnectionError" in text
assert "socket.error" in method or "OSError" in method
'''
        probes.append(active_probe("requests-socket-error-wrapped", code, "Check that response streaming wraps low-level socket errors in ConnectionError."))
    if "xarray_groupby_repr_no_trailing_space" in templates:
        code = r'''
import os

path = os.path.join(os.getcwd(), "xarray/core/groupby.py")
text = open(path, encoding="utf-8", errors="replace").read()
bad = 'grouped over {!r} \\n'
good = 'grouped over {!r}\\n'
print("bad_repr_template", bad in text)
print("good_repr_template", good in text)
assert bad not in text
assert good in text
'''
        probes.append(active_probe("xarray-groupby-repr-no-trailing-space", code, "Check DatasetGroupBy repr does not include trailing whitespace before newline."))
    if "xarray_to_unstacked_dataset_drop_level_coord" in templates:
        code = r'''
import os

path = os.path.join(os.getcwd(), "xarray/core/dataarray.py")
text = open(path, encoding="utf-8", errors="replace").read()
start = text.index("    def to_unstacked_dataset(self, dim, level=0):")
end = text.index("\n    def transpose", start)
method = text[start:end]
has_drop = ".drop_vars(variable_dim" in method or ".reset_coords(variable_dim" in method
print("drops_level_coord", has_drop)
assert has_drop
'''
        probes.append(active_probe("xarray-unstacked-dataset-drop-level-coord", code, "Check to_unstacked_dataset removes the stacked level coordinate from extracted variables."))
    if "django_join_filter_respects_autoescape_false" in templates:
        code = r'''
import os

path = os.path.join(os.getcwd(), "django/template/defaultfilters.py")
text = open(path, encoding="utf-8", errors="replace").read()
start = text.index("def join(value, arg, autoescape=True):")
end = text.index("\n\n@register.filter(is_safe=True)\ndef last", start)
method = text[start:end]
print("has_autoescape_else", "if autoescape else" in method)
assert "if autoescape else" in method
'''
        probes.append(active_probe("django-join-autoescape-false", code, "Check join filter does not force-escape the joiner when autoescape is false."))
    if "django_sitemap_empty_callable_lastmod" in templates:
        code = r'''
import os

path = os.path.join(os.getcwd(), "django/contrib/sitemaps/__init__.py")
text = open(path, encoding="utf-8", errors="replace").read()
start = text.index("    def get_latest_lastmod(self):")
end = text.index("\n    def _urls", start)
method = text[start:end]
print("catches_value_error", "ValueError" in method)
assert "ValueError" in method
'''
        probes.append(active_probe("django-sitemap-empty-callable-lastmod", code, "Check empty sitemap callable lastmod is handled like no latest timestamp."))
    if "django_choices_str_returns_value" in templates:
        code = r'''
import os

path = os.path.join(os.getcwd(), "django/db/models/enums.py")
text = open(path, encoding="utf-8", errors="replace").read()
start = text.index("class Choices(enum.Enum, metaclass=ChoicesMeta):")
end = text.index("\n\nclass IntegerChoices", start)
block = text[start:end]
print("choices_str_returns_value", "def __str__(self):" in block and "str(self.value)" in block)
assert "def __str__(self):" in block and "str(self.value)" in block
'''
        probes.append(active_probe("django-choices-str-returns-value", code, "Check Django Choices stringification preserves the concrete field value type."))
    if "pylint_notes_punctuation_tags" in templates:
        code = r'''
import os

path = os.path.join(os.getcwd(), "pylint/checkers/misc.py")
text = open(path, encoding="utf-8", errors="replace").read()
print("has_punctuation_boundary", "(?=\\s|:|$)" in text)
assert "(?=\\s|:|$)" in text
'''
        probes.append(active_probe("pylint-notes-punctuation-tags", code, "Check punctuation-only notes are not excluded by a word-boundary regex."))
    if "pylint_regex_property_escape_no_crash" in templates:
        code = r'''
import os

path = os.path.join(os.getcwd(), "pylint/config/argument.py")
text = open(path, encoding="utf-8", errors="replace").read()
start = text.index("def _regexp_csv_transfomer(value: str)")
end = text.index("\n\ndef _regexp_paths_csv_transfomer", start)
method = text[start:end]
print("sanitizes_property_escape", "\\\\p" in method and "re.sub" in method)
assert "\\\\p" in method and "re.sub" in method
'''
        probes.append(active_probe("pylint-regex-property-escape-no-crash", code, "Check regexp csv transformer neutralizes unsupported unicode property escapes."))
    if "pylint_msg_template_literal_braces" in templates:
        code = r'''
import os

path = os.path.join(os.getcwd(), "pylint/reporters/text.py")
text = open(path, encoding="utf-8", errors="replace").read()
start = text.index("    def on_set_current_module")
end = text.index("\n    def write_message", start)
method = text[start:end]
print("has_literal_brace_guard", "(?<!\\{)" in method and "(?!\\})" in method)
assert "(?<!\\{)" in method and "(?!\\})" in method
'''
        probes.append(active_probe("pylint-msg-template-literal-braces", code, "Check msg-template parsing ignores doubled literal braces."))
    if "seaborn_polyfit_drop_missing_data" in templates:
        code = r'''
import os

path = os.path.join(os.getcwd(), "seaborn/_stats/regression.py")
text = open(path, encoding="utf-8", errors="replace").read()
start = text.index("    def _fit_predict(self, data):")
end = text.index("\n    # TODO", start)
method = text[start:end]
print("drops_missing", ".dropna(" in method)
assert ".dropna(" in method
'''
        probes.append(active_probe("seaborn-polyfit-drop-missing-data", code, "Check PolyFit removes missing x/y rows before fitting."))
    if "seaborn_boolean_color_scale_object" in templates:
        code = r'''
import os

path = os.path.join(os.getcwd(), "seaborn/_core/scales.py")
text = open(path, encoding="utf-8", errors="replace").read()
start = text.index("    def _setup(")
end = text.index("\n    def _get_transform", start)
method = text[start:end]
print("bool_to_object", "dtype" in method and "bool" in method and "astype(object)" in method)
assert "dtype" in method and "bool" in method and "astype(object)" in method
'''
        probes.append(active_probe("seaborn-boolean-color-scale-object", code, "Check boolean semantic data is routed away from the continuous numeric scale path."))
    if "seaborn_pairplot_multiindex_columns" in templates:
        code = r'''
import os

path = os.path.join(os.getcwd(), "seaborn/axisgrid.py")
text = open(path, encoding="utf-8", errors="replace").read()
start = text.index("def pairplot(")
end = text.index("\n\ndef jointplot", start)
function = text[start:end]
print("handles_multiindex", "pd.MultiIndex" in function and "data.columns" in function)
assert "pd.MultiIndex" in function and "data.columns" in function
'''
        probes.append(active_probe("seaborn-pairplot-multiindex-columns", code, "Check pairplot normalizes MultiIndex columns before PairGrid indexing."))
    if "sphinx_napoleon_no_escape_trailing_underscore_attr" in templates:
        code = r'''
import os

path = os.path.join(os.getcwd(), "sphinx/ext/napoleon/docstring.py")
text = open(path, encoding="utf-8", errors="replace").read()
start = text.index("    def _escape_args_and_kwargs(self, name: str) -> str:")
end = text.index("\n    def _fix_field_desc", start)
method = text[start:end]
print("still_escapes_trailing_underscore", "name[:-1] + r'\\\\_'" in method)
assert "name[:-1] + r'\\\\_'" not in method
'''
        probes.append(active_probe("sphinx-napoleon-no-trailing-underscore-escape", code, "Check napoleon no longer over-escapes attribute names ending in underscore."))
    if "sphinx_napoleon_other_parameters_use_param" in templates:
        code = r'''
import os

path = os.path.join(os.getcwd(), "sphinx/ext/napoleon/docstring.py")
text = open(path, encoding="utf-8", errors="replace").read()
start = text.index("    def _parse_other_parameters_section(self, section: str)")
end = text.index("\n    def _parse_parameters_section", start)
method = text[start:end]
print("other_parameters_uses_param", "napoleon_use_param" in method and "_format_docutils_params" in method)
assert "napoleon_use_param" in method and "_format_docutils_params" in method
'''
        probes.append(active_probe("sphinx-napoleon-other-parameters-use-param", code, "Check napoleon_use_param also controls Other Parameters formatting."))
    if "sphinx_autosummary_members_filter_imported" in templates:
        code = r'''
import os

path = os.path.join(os.getcwd(), "sphinx/ext/autosummary/generate.py")
text = open(path, encoding="utf-8", errors="replace").read()
start = text.index("    if doc.objtype == 'module':")
end = text.index("    elif doc.objtype == 'class':", start)
block = text[start:end]
print("filters_imported_members", "if imported_members:" in block and "__module__" in block)
assert "if imported_members:" in block and "__module__" in block
'''
        probes.append(active_probe("sphinx-autosummary-members-filter-imported", code, "Check module template members obey autosummary_imported_members."))
    if "sympy_empty_array_shape_scan" in templates:
        code = r'''
import os

path = os.path.join(os.getcwd(), "sympy/tensor/array/ndim_array.py")
text = open(path, encoding="utf-8", errors="replace").read()
start = text.index("    def _scan_iterable_shape(cls, iterable):")
end = text.index("\n    @classmethod\n    def _handle_ndarray_creation_inputs", start)
method = text[start:end]
print("handles_empty_iterable", "if not pointer:" in method and "return [], (0,)" in method)
assert "if not pointer:" in method and "return [], (0,)" in method
'''
        probes.append(active_probe("sympy-empty-array-shape-scan", code, "Check empty iterable array construction has an explicit shape path."))
    if "sympy_mathml_indexed_printer" in templates:
        code = r'''
import os

path = os.path.join(os.getcwd(), "sympy/printing/mathml.py")
text = open(path, encoding="utf-8", errors="replace").read()
has_indexed_methods = text.count("def _print_Indexed") >= 2
has_selector = "selector" in text
has_msub = "msub" in text
print("has_indexed_methods", has_indexed_methods)
print("has_selector", has_selector)
print("has_msub", has_msub)
assert has_indexed_methods
assert has_selector
assert has_msub
'''
        probes.append(active_probe("sympy-mathml-indexed-printer", code, "Check MathML content and presentation printers handle Indexed objects directly."))
    return probes


def active_probe(name, code, description):
    digest = hashlib.sha256(code.encode("utf-8", "replace")).hexdigest()[:12]
    return {
        "probe_id": "template-active-%s-%s" % (safe_id(name), digest),
        "description": description,
        "code": code.strip() + "\n",
        "language": "python",
        "code_block_index": -1,
        "code_sha256": hashlib.sha256(code.encode("utf-8", "replace")).hexdigest(),
        "probe_generation_strategy": "template_active_patch_trial",
    }


def normalize_stream(value, candidate_repo, snapshot_run_dir):
    normalized = value or ""
    replacements = [
        (candidate_repo or "", "<CANDIDATE_REPO>"),
        (snapshot_run_dir or "", "<SNAPSHOT_RUN_DIR>"),
    ]
    for old, new in replacements:
        if old:
            normalized = normalized.replace(old, new)
    normalized = re.sub(r"0x[0-9A-Fa-f]+", "0xADDR", normalized)
    normalized = re.sub(
        r"<REMOTE_ROOT>/runs/[^ \n\r\t:]+/candidate_apply_queues/[^ \n\r\t:]+/candidates/[^ \n\r\t:]+/repo",
        "<CANDIDATE_REPO>",
        normalized,
    )
    return normalized


def artifact_paths(queue_dir, candidate, probe):
    artifact_dir = os.path.join(
        queue_dir,
        "probe_artifacts",
        safe_id(candidate.get("task_id")),
        safe_id(candidate.get("candidate_id")),
        safe_id(probe.get("probe_id")),
    )
    return {
        "dir": artifact_dir,
        "stdout": os.path.join(artifact_dir, "stdout.txt"),
        "stderr": os.path.join(artifact_dir, "stderr.txt"),
        "code": os.path.join(artifact_dir, "probe.py"),
        "result": os.path.join(artifact_dir, "result.json"),
    }


def run_probe(candidate, candidate_meta, probe, args, queue_dir):
    route = task_route(args.task_env_routes, candidate.get("task_id"))
    effective_venv_dir = route_venv_dir(args.venv_dir, route)
    artifacts = artifact_paths(queue_dir, candidate, probe)
    code = probe["code"].lstrip() + "\n"
    write_text(artifacts["code"], code)
    started = time.time()
    started_at = utc_now()
    timed_out = False
    try:
        proc = subprocess.Popen(
            [python_path(effective_venv_dir), "-"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=candidate.get("candidate_repo"),
            env=probe_env(effective_venv_dir, args.gpu),
        )
        try:
            out, err = proc.communicate(code.encode("utf-8"), timeout=args.timeout_sec)
            exit_code = proc.returncode
        except subprocess.TimeoutExpired:
            timed_out = True
            proc.kill()
            out, err = proc.communicate()
            exit_code = -124
    except Exception as exc:
        out, err = b"", repr(exc).encode("utf-8")
        exit_code = -1
    finished = time.time()
    stdout_full = out.decode("utf-8", "replace")
    stderr_full = err.decode("utf-8", "replace")
    normalized_stdout = normalize_stream(stdout_full, candidate.get("candidate_repo"), args.snapshot_run_dir)
    normalized_stderr = normalize_stream(stderr_full, candidate.get("candidate_repo"), args.snapshot_run_dir)
    stdout, stdout_truncated = truncate_stream(stdout_full)
    stderr, stderr_truncated = truncate_stream(stderr_full)
    stdout_artifact = stream_record(artifacts["stdout"], stdout_full)
    stderr_artifact = stream_record(artifacts["stderr"], stderr_full)
    if timed_out:
        outcome = "timeout"
    elif exit_code == 0:
        outcome = "pass"
    else:
        outcome = "fail"
    record = {
        "schema_version": "0.1",
        "queue_id": args.queue_id,
        "apply_queue_id": args.apply_queue_id,
        "probe_id": probe.get("probe_id"),
        "probe_description": probe.get("description"),
        "probe_generation_strategy": probe.get("probe_generation_strategy"),
        "probe_language": probe.get("language"),
        "probe_code_block_index": probe.get("code_block_index"),
        "probe_code_sha256": probe.get("code_sha256"),
        "task_id": candidate.get("task_id"),
        "repo": candidate.get("repo"),
        "candidate_id": candidate.get("candidate_id"),
        "candidate_source": candidate.get("candidate_source"),
        "candidate_repo": candidate.get("candidate_repo"),
        "candidate_semantic_template": candidate_meta.get("semantic_template") or "",
        "candidate_expected_behavior_change": bool(candidate_meta.get("expected_behavior_change")),
        "candidate_model_generated": bool(candidate_meta.get("model_generated")),
        "candidate_heuristic": bool(candidate_meta.get("heuristic_candidate")),
        "candidate_generation_backend": candidate_meta.get("generation_backend") or "",
        "task_environment_route": route,
        "effective_venv_dir": effective_venv_dir,
        "exit_code": exit_code,
        "outcome": outcome,
        "timed_out": timed_out,
        "duration_sec": round(finished - started, 3),
        "started_at": started_at,
        "finished_at": utc_now(),
        "stdout": stdout,
        "stderr": stderr,
        "normalized_stdout_sha256": hashlib.sha256(normalized_stdout.encode("utf-8", "replace")).hexdigest(),
        "normalized_stderr_sha256": hashlib.sha256(normalized_stderr.encode("utf-8", "replace")).hexdigest(),
        "stdout_truncated": stdout_truncated,
        "stderr_truncated": stderr_truncated,
        "stdout_artifact": stdout_artifact,
        "stderr_artifact": stderr_artifact,
        "probe_code_path": artifacts["code"],
        "gold_used": False,
    }
    record["behavior_hash"] = hashlib.sha256(
        (str(exit_code) + "\n" + normalized_stdout + "\n" + normalized_stderr).encode("utf-8", "replace")
    ).hexdigest()
    record["behavior_hash_basis"] = "exit_code_plus_path_normalized_stdout_stderr"
    write_json(artifacts["result"], record)
    return record


def selected_candidates(apply_results, visible_mode, include_nonsemantic):
    selected = []
    for candidate in apply_results:
        if candidate.get("apply_status") not in ("applied", "applied_noop"):
            continue
        visible = candidate.get("visible_summary") or {}
        if visible_mode == "strict" and not visible.get("strict_visible_pass"):
            continue
        if visible_mode == "compatible" and not visible.get("compatible_visible_pass"):
            continue
        if not include_nonsemantic and candidate.get("candidate_source") == "noop_control":
            continue
        selected.append(candidate)
    return selected


def probes_for_task(candidate, candidate_meta, max_probes, task_templates):
    path = issue_path(candidate_meta)
    issue_text = read_text(path) if path else ""
    probes = extract_fenced_code(issue_text, max_probes)
    probes.extend(template_active_probes(candidate.get("task_id"), task_templates, issue_text))
    return path, probes


def templates_by_task(manifest_records):
    out = {}
    for record in manifest_records:
        if not record.get("expected_behavior_change"):
            continue
        task_id = record.get("task_id")
        template = record.get("semantic_template")
        if not task_id or not template:
            continue
        out.setdefault(task_id, set()).add(template)
    return out


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot-run-dir", required=True)
    parser.add_argument("--apply-queue-id", required=True)
    parser.add_argument("--queue-id", required=True)
    parser.add_argument("--worker-id", type=int, required=True)
    parser.add_argument("--num-workers", type=int, default=4)
    parser.add_argument("--gpu", required=True)
    parser.add_argument("--timeout-sec", type=int, default=90)
    parser.add_argument("--venv-dir", default="")
    parser.add_argument("--task-env-map", default="")
    parser.add_argument("--visible-mode", choices=["strict", "compatible"], default="compatible")
    parser.add_argument("--max-probes-per-task", type=int, default=2)
    parser.add_argument("--exclude-nonsemantic", action="store_true")
    args = parser.parse_args(argv)
    args.task_env_routes = load_task_env_routes(args.task_env_map)

    os.environ["CUDA_VISIBLE_DEVICES"] = str(args.gpu)
    apply_queue_dir = os.path.join(args.snapshot_run_dir, "candidate_apply_queues", args.apply_queue_id)
    apply_results_path = os.path.join(apply_queue_dir, "candidate_apply_results.jsonl")
    apply_results = read_jsonl(apply_results_path)
    manifest_records = materialized_manifest(apply_queue_dir)
    manifest_by_id = by_candidate_id(manifest_records)
    task_templates = templates_by_task(manifest_records)
    candidates = selected_candidates(apply_results, args.visible_mode, not args.exclude_nonsemantic)
    assigned = [
        candidate for index, candidate in enumerate(candidates) if index % args.num_workers == args.worker_id
    ]
    queue_dir = os.path.join(args.snapshot_run_dir, "issue_probe_queues", args.queue_id)
    worker_dir = os.path.join(queue_dir, "workers", "worker_%02d_gpu_%s" % (args.worker_id, args.gpu))
    os.makedirs(worker_dir, exist_ok=True)
    summary = {
        "schema_version": "0.1",
        "queue_id": args.queue_id,
        "apply_queue_id": args.apply_queue_id,
        "snapshot_run_dir": args.snapshot_run_dir,
        "worker_id": args.worker_id,
        "num_workers": args.num_workers,
        "gpu": args.gpu,
        "visible_mode": args.visible_mode,
        "venv_dir": args.venv_dir,
        "task_env_map": args.task_env_map,
        "task_env_route_count": len(args.task_env_routes),
        "selected_candidate_count": len(candidates),
        "assigned_candidate_count": len(assigned),
        "max_probes_per_task": args.max_probes_per_task,
        "exclude_nonsemantic": args.exclude_nonsemantic,
        "started_at": utc_now(),
        "gold_used": False,
        "outcome_counts": {},
        "candidate_template_counts": {},
        "probe_count": 0,
        "candidate_without_probe_count": 0,
        "task_probe_counts": {},
    }
    task_probe_cache = {}
    for candidate in assigned:
        candidate_id = candidate.get("candidate_id")
        candidate_meta = manifest_by_id.get(candidate_id) or {}
        template = candidate_meta.get("semantic_template") or "none"
        summary["candidate_template_counts"][template] = summary["candidate_template_counts"].get(template, 0) + 1
        task_id = candidate.get("task_id")
        if task_id not in task_probe_cache:
            issue_file, probes = probes_for_task(
                candidate,
                candidate_meta,
                args.max_probes_per_task,
                task_templates.get(task_id, set()),
            )
            task_probe_cache[task_id] = (issue_file, probes)
            summary["task_probe_counts"][task_id] = len(probes)
        issue_file, probes = task_probe_cache[task_id]
        if not probes:
            summary["candidate_without_probe_count"] += 1
            continue
        for probe in probes:
            enriched_probe = dict(probe)
            enriched_probe["issue_path"] = issue_file
            result = run_probe(candidate, candidate_meta, enriched_probe, args, queue_dir)
            append_jsonl(os.path.join(worker_dir, "issue_probe_results.jsonl"), result)
            append_jsonl(os.path.join(queue_dir, "issue_probe_results.jsonl"), result)
            summary["probe_count"] += 1
            outcome = result.get("outcome") or "unknown"
            summary["outcome_counts"][outcome] = summary["outcome_counts"].get(outcome, 0) + 1
    summary["finished_at"] = utc_now()
    write_json(os.path.join(worker_dir, "generic_issue_probe_worker_summary.json"), summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
