#!/usr/bin/env python3
"""Run upgraded full-package / issue-code probes for audited certificates.

This worker consumes the frozen manual-audit upgrade target file. It executes a
small, issue-specific probe against each visible-passing candidate repository
listed in the audit record and writes PatchCourt-compatible probe results. It
does not read developer patches, hidden tests, FAIL_TO_PASS, PASS_TO_PASS, or
test_patch fields.
"""

from __future__ import print_function

import argparse
import datetime as _dt
import hashlib
import json
import os
import re
import glob
import shutil
import subprocess
import sys
import time


GOLD_FIELDS = set(["patch", "test_patch", "FAIL_TO_PASS", "PASS_TO_PASS"])
MAX_STREAM_CHARS = 4096


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


def read_json(path):
    with open(path, "r", encoding="utf-8-sig") as handle:
        value = json.load(handle)
    assert_no_gold(value, path)
    return value


def write_text(path, value):
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(value)


def shell_quote(value):
    return "'" + (value or "").replace("'", "'\"'\"'") + "'"


def write_json(path, value):
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")


def append_jsonl(path, value):
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(value, ensure_ascii=False, sort_keys=True) + "\n")


def truncate(value):
    if len(value or "") <= MAX_STREAM_CHARS:
        return value or "", False
    return (value or "")[:MAX_STREAM_CHARS], True


def stream_record(path, value):
    write_text(path, value or "")
    data = (value or "").encode("utf-8", "replace")
    return {"path": path, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def load_task_env_routes(path):
    if not path:
        return {}
    value = read_json(path)
    if value.get("gold_used") is not False:
        raise RuntimeError("task env map must carry gold_used=false")
    routes = value.get("routes", value)
    if not isinstance(routes, dict):
        raise RuntimeError("task env routes must be a dict")
    return routes


def task_route(routes, task_id):
    route = {}
    if isinstance(routes.get("*"), dict):
        route.update(routes["*"])
    if isinstance(routes.get(task_id), dict):
        route.update(routes[task_id])
    return route


def python_path(venv_dir):
    candidate = os.path.join(venv_dir, "bin", "python") if venv_dir else ""
    if candidate and os.path.exists(candidate):
        return candidate
    return sys.executable


def command_output(command, cwd, env, timeout):
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, cwd=cwd, env=env)
    out, err = proc.communicate(timeout=timeout)
    stdout = out.decode("utf-8", "replace")
    stderr = err.decode("utf-8", "replace")
    if proc.returncode != 0:
        raise RuntimeError("command failed (%s): %s%s" % (proc.returncode, stdout, stderr))
    return stdout.strip()


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


def write_pytest_version_file(candidate_repo):
    path = os.path.join(candidate_repo, "src", "_pytest", "_version.py")
    if not os.path.isdir(os.path.dirname(path)):
        return {"status": "skipped_missing_dir", "path": path}
    content = "version = '7.3.0+patchcourt'\nversion_tuple = (7, 3, 0)\n"
    write_text(path, content)
    return {"status": "ok", "path": path, "bytes": len(content.encode("utf-8"))}


def write_astropy_version_file(candidate_repo):
    package_dir = os.path.join(candidate_repo, "astropy")
    if not os.path.isdir(package_dir):
        return {"status": "skipped_missing_dir", "path": package_dir}
    path = os.path.join(package_dir, "_version.py")
    content = (
        "version = '0+patchcourt'\n"
        "__version__ = version\n"
        "githash = 'patchcourt'\n"
        "release = False\n"
        "debug = False\n"
    )
    write_text(path, content)
    compiler_path = os.path.join(package_dir, "utils", "_compiler.py")
    if os.path.isdir(os.path.dirname(compiler_path)):
        write_text(compiler_path, "def compiler_fixup(*args, **kwargs):\n    return None\n")
    return {
        "status": "ok",
        "path": path,
        "compiler_stub_path": compiler_path,
        "bytes": len(content.encode("utf-8")),
    }


def write_numpy_compat_sitecustomize(candidate_repo):
    path = os.path.join(candidate_repo, "sitecustomize.py")
    content = (
        "import numpy as _patchcourt_np\n"
        "for _name, _target in {\n"
        "    'product': 'prod',\n"
        "    'cumproduct': 'cumprod',\n"
        "    'round_': 'round',\n"
        "    'msort': 'sort',\n"
        "    'sometrue': 'any',\n"
        "    'alltrue': 'all',\n"
        "    'float_': 'float64',\n"
        "    'complex_': 'complex128',\n"
        "    'unicode_': 'str_',\n"
        "    'string_': 'bytes_',\n"
        "    'longfloat': 'longdouble',\n"
        "    'clongfloat': 'clongdouble',\n"
        "    'NaN': 'nan',\n"
        "    'Inf': 'inf',\n"
        "    'infty': 'inf',\n"
        "}.items():\n"
        "    if not hasattr(_patchcourt_np, _name) and hasattr(_patchcourt_np, _target):\n"
        "        setattr(_patchcourt_np, _name, getattr(_patchcourt_np, _target))\n"
        "if not hasattr(_patchcourt_np, 'asfarray'):\n"
        "    def _patchcourt_asfarray(a, dtype=float):\n"
        "        return _patchcourt_np.asarray(a, dtype=dtype)\n"
        "    _patchcourt_np.asfarray = _patchcourt_asfarray\n"
        "if not hasattr(_patchcourt_np, 'asscalar'):\n"
        "    _patchcourt_np.asscalar = lambda a: _patchcourt_np.asarray(a).item()\n"
        "if not hasattr(_patchcourt_np, 'obj2sctype'):\n"
        "    def _patchcourt_obj2sctype(obj, default=None):\n"
        "        try:\n"
        "            return _patchcourt_np.dtype(obj).type\n"
        "        except Exception:\n"
        "            return default\n"
        "    _patchcourt_np.obj2sctype = _patchcourt_obj2sctype\n"
        "if not hasattr(_patchcourt_np, 'issubsctype'):\n"
        "    _patchcourt_np.issubsctype = lambda arg1, arg2: _patchcourt_np.issubdtype(_patchcourt_np.dtype(arg1).type, arg2)\n"
        "if not hasattr(_patchcourt_np, 'find_common_type'):\n"
        "    _patchcourt_np.find_common_type = lambda array_types, scalar_types: _patchcourt_np.result_type(*(list(array_types) + list(scalar_types)))\n"
    )
    previous = ""
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8", errors="replace") as handle:
            previous = handle.read()
    if "asfarray" not in previous:
        write_text(path, previous + ("\n" if previous and not previous.endswith("\n") else "") + content)
    return {"status": "ok", "path": path, "bytes": len(content.encode("utf-8"))}


def write_werkzeug_url_quote_sitecustomize(candidate_repo):
    path = os.path.join(candidate_repo, "sitecustomize.py")
    content = (
        "try:\n"
        "    import werkzeug.urls as _patchcourt_werkzeug_urls\n"
        "    from urllib.parse import quote as _patchcourt_quote\n"
        "    from urllib.parse import unquote as _patchcourt_unquote\n"
        "    if not hasattr(_patchcourt_werkzeug_urls, 'url_quote'):\n"
        "        _patchcourt_werkzeug_urls.url_quote = _patchcourt_quote\n"
        "    if not hasattr(_patchcourt_werkzeug_urls, 'url_unquote'):\n"
        "        _patchcourt_werkzeug_urls.url_unquote = _patchcourt_unquote\n"
        "except Exception:\n"
        "    pass\n"
    )
    previous = ""
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8", errors="replace") as handle:
            previous = handle.read()
    if "url_quote" not in previous:
        write_text(path, previous + ("\n" if previous and not previous.endswith("\n") else "") + content)
    return {"status": "ok", "path": path, "bytes": len(content.encode("utf-8"))}


def write_sklearn_import_stubs(candidate_repo):
    check_dir = os.path.join(candidate_repo, "sklearn", "__check_build")
    utils_dir = os.path.join(candidate_repo, "sklearn", "utils")
    if not os.path.isdir(check_dir) or not os.path.isdir(utils_dir):
        return {"status": "skipped_missing_dir", "check_dir": check_dir, "utils_dir": utils_dir}
    check_path = os.path.join(check_dir, "_check_build.py")
    murmur_path = os.path.join(utils_dir, "murmurhash.py")
    logistic_path = os.path.join(utils_dir, "_logistic_sigmoid.py")
    sparsefuncs_fast_path = os.path.join(utils_dir, "sparsefuncs_fast.py")
    random_path = os.path.join(utils_dir, "_random.py")
    hashing_path = os.path.join(candidate_repo, "sklearn", "feature_extraction", "_hashing.py")
    svmlight_path = os.path.join(candidate_repo, "sklearn", "datasets", "_svmlight_format.py")
    write_text(check_path, "def check_build():\n    return True\n")
    write_text(
        murmur_path,
        "def murmurhash3_32(key, seed=0, positive=False):\n"
        "    value = hash((key, seed)) & 0xFFFFFFFF\n"
        "    if positive:\n"
        "        return value\n"
        "    return value - 0x100000000 if value & 0x80000000 else value\n",
    )
    write_text(
        logistic_path,
        "import numpy as np\n\n"
        "def _log_logistic_sigmoid(n_samples, n_features, X, out):\n"
        "    out[:] = -np.logaddexp(0, -X)\n"
        "    return out\n",
    )
    write_text(
        sparsefuncs_fast_path,
        "import numpy as np\n\n"
        "def csr_row_norms(X):\n"
        "    if hasattr(X, 'multiply'):\n"
        "        return np.asarray(X.multiply(X).sum(axis=1)).ravel()\n"
        "    arr = np.asarray(X)\n"
        "    return np.sum(arr * arr, axis=1)\n\n"
        "def inplace_csr_row_normalize_l1(X):\n"
        "    return None\n\n"
        "def inplace_csr_row_normalize_l2(X):\n"
        "    return None\n\n"
        "def _dense(X):\n"
        "    return X.toarray() if hasattr(X, 'toarray') else np.asarray(X)\n\n"
        "def csr_mean_variance_axis0(X):\n"
        "    arr = _dense(X)\n"
        "    return np.mean(arr, axis=0), np.var(arr, axis=0)\n\n"
        "def csc_mean_variance_axis0(X):\n"
        "    arr = _dense(X)\n"
        "    return np.mean(arr, axis=0), np.var(arr, axis=0)\n\n"
        "def incr_mean_variance_axis0(X, last_mean, last_var, last_n):\n"
        "    arr = _dense(X)\n"
        "    n = arr.shape[0]\n"
        "    return np.mean(arr, axis=0), np.var(arr, axis=0), np.full(arr.shape[1], n)\n",
    )
    write_text(
        random_path,
        "import numpy as np\n\n"
        "def sample_without_replacement(n_population, n_samples, random_state=None, method='auto'):\n"
        "    rng = np.random.RandomState(random_state) if not hasattr(random_state, 'choice') else random_state\n"
        "    return rng.choice(n_population, size=n_samples, replace=False)\n",
    )
    if os.path.isdir(os.path.dirname(hashing_path)):
        write_text(
            hashing_path,
            "import numpy as np\n\n"
            "def transform(raw_X, n_features, dtype, alternate_sign=True):\n"
            "    indices = []\n"
            "    values = []\n"
            "    indptr = [0]\n"
            "    for row in raw_X:\n"
            "        for key, value in row:\n"
            "            column = hash(key) % int(n_features)\n"
            "            sign = -1 if alternate_sign and hash(('sign', key)) % 2 else 1\n"
            "            indices.append(column)\n"
            "            values.append(sign * value)\n"
            "        indptr.append(len(indices))\n"
            "    return (np.asarray(indices, dtype=np.int32), np.asarray(indptr, dtype=np.int32), np.asarray(values, dtype=dtype))\n",
        )
    if os.path.isdir(os.path.dirname(svmlight_path)):
        write_text(
            svmlight_path,
            "def _load_svmlight_file(*args, **kwargs):\n"
            "    raise NotImplementedError('PatchCourt import stub for probe collection')\n\n"
            "def _dump_svmlight_file(*args, **kwargs):\n"
            "    raise NotImplementedError('PatchCourt import stub for probe collection')\n",
        )
    return {
        "status": "ok",
        "check_build_path": check_path,
        "murmurhash_path": murmur_path,
        "logistic_sigmoid_path": logistic_path,
        "sparsefuncs_fast_path": sparsefuncs_fast_path,
        "random_path": random_path,
        "hashing_path": hashing_path,
        "svmlight_path": svmlight_path,
    }


def copy_installed_matplotlib_extensions(candidate_repo, venv_dir, timeout, gpu):
    target_dir = os.path.join(candidate_repo, "lib", "matplotlib")
    if not os.path.isdir(target_dir):
        return {"status": "skipped_missing_dir", "target_dir": target_dir}
    py = python_path(venv_dir)
    env = probe_env(venv_dir, gpu)
    env.pop("PYTHONPATH", None)
    site = command_output(
        "%s - <<'PY'\nimport matplotlib, os\nprint(os.path.dirname(matplotlib.__file__))\nPY" % shell_quote(py),
        "/tmp",
        env,
        timeout,
    )
    copied = []
    for source in sorted(glob.glob(os.path.join(site, "**", "*.so"), recursive=True)):
        rel = os.path.relpath(source, site)
        dest = os.path.join(target_dir, rel)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        if os.path.abspath(source) == os.path.abspath(dest):
            continue
        shutil.copy2(source, dest)
        copied.append(rel)
    version_source = os.path.join(site, "_version.py")
    version_dest = os.path.join(target_dir, "_version.py")
    if os.path.exists(version_source):
        shutil.copy2(version_source, version_dest)
        copied.append("_version.py")
    elif not os.path.exists(version_dest):
        write_text(version_dest, "version = '0+patchcourt'\n__version__ = version\n")
        copied.append("_version.py")
    return {"status": "ok", "source_site_package": site, "target_dir": target_dir, "copied": copied}


def run_pre_probe_steps(candidate_repo, route, venv_dir, args):
    results = []
    for step in route.get("pre_visible_steps") or route.get("pre_probe_steps") or []:
        started = time.time()
        try:
            if step == "write_pytest_version_file":
                result = write_pytest_version_file(candidate_repo)
            elif step == "write_astropy_version_file":
                result = write_astropy_version_file(candidate_repo)
            elif step == "write_numpy_compat_sitecustomize":
                result = write_numpy_compat_sitecustomize(candidate_repo)
            elif step == "write_werkzeug_url_quote_sitecustomize":
                result = write_werkzeug_url_quote_sitecustomize(candidate_repo)
            elif step == "write_sklearn_import_stubs":
                result = write_sklearn_import_stubs(candidate_repo)
            elif step == "copy_installed_matplotlib_extensions":
                result = copy_installed_matplotlib_extensions(candidate_repo, venv_dir, args.timeout_sec, args.gpu)
            else:
                result = {"status": "unknown_step", "step": step}
        except Exception as exc:
            result = {"status": "failed", "step": step, "error": repr(exc)}
        result.update({"step": step, "duration_sec": round(time.time() - started, 3), "created_at": utc_now()})
        results.append(result)
    return results


def normalize_stream(value, candidate_repo, snapshot_run_dir):
    normalized = value or ""
    for old, new in [(candidate_repo or "", "<CANDIDATE_REPO>"), (snapshot_run_dir or "", "<SNAPSHOT_RUN_DIR>")]:
        if old:
            normalized = normalized.replace(old, new)
    normalized = re.sub(r"0x[0-9A-Fa-f]+", "0xADDR", normalized)
    normalized = re.sub(
        r"<REMOTE_ROOT>/runs/[^ \n\r\t:]+/candidate_apply_queues/[^ \n\r\t:]+/candidates/[^ \n\r\t:]+/repo",
        "<CANDIDATE_REPO>",
        normalized,
    )
    return normalized


def split_semicolon(value):
    return [item for item in (value or "").split(";") if item]


def semicolon_value_for(record, field, candidate_id, default=""):
    ids = split_semicolon(record.get("candidate_ids"))
    values = split_semicolon(record.get(field))
    if not ids or not values:
        return default
    try:
        index = ids.index(candidate_id)
    except ValueError:
        return default
    if index >= len(values):
        return default
    return values[index]


def parse_bool_text(value, default=False):
    if value is None or value == "":
        return default
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def source_from_candidate_id(candidate_id):
    parts = (candidate_id or "").split("::")
    if len(parts) >= 2:
        return parts[1]
    return "unknown"


def is_model_candidate(candidate_id):
    return source_from_candidate_id(candidate_id) != "noop_control"


def upgraded_probe(task_id):
    probes = {
        "marshmallow-code__marshmallow-1343": (
            "upgrade-fullpkg-marshmallow-nested-invalid-validate",
            "Validate an invalid nested payload through marshmallow Schema.validate.",
            "full_package_behavioral_probe",
            r'''
from marshmallow import Schema, fields, validates

class Bar(Schema):
    value = fields.String(required=True)

    @validates("value")
    def validate_value(self, value):
        return None

class Foo(Schema):
    bar = fields.Nested(Bar)

errors = Foo().validate({"bar": "not-a-dict"})
print("errors", errors)
assert "bar" in errors
''',
        ),
        "marshmallow-code__marshmallow-1359": (
            "upgrade-fullpkg-marshmallow-list-datetime-load",
            "Load a List(Nested(DateTime)) payload through marshmallow.",
            "full_package_behavioral_probe",
            r'''
from marshmallow import Schema, fields

class Event(Schema):
    when = fields.DateTime()

class Payload(Schema):
    events = fields.List(fields.Nested(Event))

schema = Payload()
loaded = schema.load({"events": [{"when": "2018-01-01T00:00:00+00:00"}]})
if isinstance(loaded, tuple):
    data, errors = loaded
elif hasattr(loaded, "data") and hasattr(loaded, "errors"):
    data, errors = loaded.data, loaded.errors
else:
    data, errors = loaded, {}
print("data_type", type(data).__name__)
print("errors", errors)
assert not errors
assert len(data["events"]) == 1
''',
        ),
        "pvlib__pvlib-python-1072": (
            "upgrade-fullpkg-pvlib-fuentes-tz-aware-index",
            "Run pvlib.temperature.fuentes on tz-aware pandas Series inputs.",
            "full_package_behavioral_probe",
            r'''
import pandas as pd
from pvlib.temperature import fuentes

index = pd.date_range("2019-01-01", freq="h", periods=3).tz_localize("UTC")
kwargs = {
    "poa_global": pd.Series(1000, index=index),
    "temp_air": pd.Series(20, index=index),
    "wind_speed": pd.Series(1, index=index),
    "noct_installed": 45,
}
result = fuentes(**kwargs)
print("result_len", len(result))
print("result_values", [round(float(x), 6) for x in result.values])
assert len(result) == 3
''',
        ),
        "pallets__flask-4992": (
            "upgrade-fullpkg-flask-config-from-file-mode",
            "Load a Flask config file through Config.from_file(mode='rb').",
            "full_package_behavioral_probe",
            r'''
import os
import tempfile
from flask import Flask

root = tempfile.mkdtemp(prefix="patchcourt_flask_config_")
path = os.path.join(root, "config.bin")
with open(path, "wb") as handle:
    handle.write(b"VALUE=1")

app = Flask(__name__)

def load(handle):
    data = handle.read()
    print("read_type", type(data).__name__)
    return {"VALUE": data == b"VALUE=1"}

loaded = app.config.from_file(path, load=load, mode="rb")
print("loaded", loaded)
print("value", app.config["VALUE"])
assert loaded is True
assert app.config["VALUE"] is True
''',
        ),
        "pallets__flask-5063": (
            "upgrade-fullpkg-flask-routes-subdomain-column",
            "Exercise the Flask routes CLI with a subdomain route.",
            "full_package_behavioral_probe",
            r'''
from flask import Flask

app = Flask(__name__, subdomain_matching=True)
app.config["SERVER_NAME"] = "example.test"

@app.route("/", subdomain="<tenant>")
def index(tenant):
    return tenant

runner = app.test_cli_runner()
result = runner.invoke(args=["routes"])
text = result.output
print("exit", result.exit_code)
print(text)
assert result.exit_code == 0
assert ("Subdomain" in text or "Domain" in text)
assert "<tenant>" in text or "tenant" in text
''',
        ),
        "psf__requests-2148": (
            "upgrade-fullpkg-requests-socket-error-wrapped",
            "Check Response.iter_content wraps low-level socket errors as requests.ConnectionError.",
            "full_package_behavioral_probe",
            r'''
import socket
from requests import ConnectionError, Response

class Raw:
    def stream(self, chunk_size, decode_content=True):
        raise socket.error("boom")

response = Response()
response.raw = Raw()
try:
    list(response.iter_content(chunk_size=1))
except ConnectionError as exc:
    print("wrapped", type(exc).__name__, exc)
else:
    raise AssertionError("socket.error was not wrapped")
''',
        ),
        "pydata__xarray-4094": (
            "upgrade-fullpkg-xarray-unstacked-dataset-drop-level-coord",
            "Run DataArray.to_unstacked_dataset and check the extracted level coordinate is not retained.",
            "full_package_behavioral_probe",
            r'''
import numpy as np
import pandas as pd
import xarray as xr

index = pd.MultiIndex.from_product([["a", "b"], [1, 2]], names=["letter", "number"])
array = xr.DataArray(np.arange(4), dims=("z",), coords={"z": index})
dataset = array.to_unstacked_dataset("z", level=0)
print("data_vars", sorted(map(str, dataset.data_vars)))
print("coords", sorted(map(str, dataset.coords)))
assert "letter" not in dataset.coords
assert set(map(str, dataset.data_vars)) == set(["a", "b"])
''',
        ),
        "pydata__xarray-5131": (
            "upgrade-fullpkg-xarray-groupby-repr-no-trailing-space",
            "Build a DataArray groupby object and check its repr has no trailing whitespace before the newline.",
            "full_package_behavioral_probe",
            r'''
import numpy as np
import xarray as xr

array = xr.DataArray(
    np.arange(4),
    dims=("x",),
    coords={"x": [0, 1, 2, 3], "label": ("x", ["a", "a", "b", "b"])},
    name="value",
)
text = repr(array.groupby("label"))
print("repr", repr(text))
assert "grouped over 'label'\n" in text or "grouped over 'label'" in text
assert " \n" not in text
''',
        ),
        "mwaskom__seaborn-2848": (
            "upgrade-fullpkg-seaborn-pairplot-hue-order-filter",
            "Execute seaborn.pairplot with a hue_order subset.",
            "full_package_behavioral_probe",
            r'''
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

df = pd.DataFrame({
    "x": [0, 1, 2, 3, 4, 5],
    "y": [0, 1, 4, 9, 16, 25],
    "label": ["a", "a", "b", "b", "c", "c"],
})
grid = sns.pairplot(df, hue="label", hue_order=["a", "b"])
print("hue_names", list(getattr(grid, "hue_names", []) or []))
assert list(getattr(grid, "hue_names", []) or []) == ["a", "b"]
plt.close("all")
''',
        ),
        "pylint-dev__pylint-6506": (
            "upgrade-fullpkg-pylint-unrecognized-option-no-traceback",
            "Run pylint with an unknown option and require a non-traceback diagnostic.",
            "full_package_behavioral_probe",
            r'''
import os
import subprocess
import sys
import tempfile

root = tempfile.mkdtemp(prefix="patchcourt_pylint_option_")
target = os.path.join(root, "sample.py")
with open(target, "w") as handle:
    handle.write("VALUE = 1\n")
proc = subprocess.Popen(
    [sys.executable, "-m", "pylint", "--patchcourt-not-an-option", target],
    cwd=root,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
)
out, err = proc.communicate(timeout=60)
text = out.decode("utf-8", "replace") + err.decode("utf-8", "replace")
print("exit", proc.returncode)
print(text)
assert proc.returncode != 0
assert "Traceback" not in text
assert "patchcourt-not-an-option" in text or "Unrecognized option" in text or "no such option" in text
''',
        ),
        "pylint-dev__pylint-7114": (
            "upgrade-fullpkg-pylint-namespace-no-missing-init",
            "Run pylint.expand_modules on an implicit namespace package.",
            "full_package_behavioral_probe",
            r'''
import os
import tempfile
from pylint.lint.expand_modules import expand_modules

root = tempfile.mkdtemp(prefix="patchcourt_pylint_ns_")
pkg = os.path.join(root, "pkg")
os.makedirs(pkg)
with open(os.path.join(pkg, "a.py"), "w") as handle:
    handle.write("A = 1\n")
with open(os.path.join(pkg, "b.py"), "w") as handle:
    handle.write("B = 2\n")
result, errors = expand_modules([pkg], [], [], [])
paths = [item.get("path", "") for item in result]
print("paths", paths)
print("errors", errors)
assert not errors
assert not any(path.endswith("__init__.py") for path in paths)
''',
        ),
        "pylint-dev__pylint-5859": (
            "upgrade-fullpkg-pylint-punctuation-note-tag",
            "Run pylint fixme detection with a punctuation-only notes tag.",
            "full_package_behavioral_probe",
            r'''
import os
import subprocess
import sys
import tempfile

root = tempfile.mkdtemp(prefix="patchcourt_pylint_notes_")
target = os.path.join(root, "sample.py")
with open(target, "w") as handle:
    handle.write("# ???: investigate this path\nVALUE = 1\n")
proc = subprocess.Popen(
    [sys.executable, "-m", "pylint", "--disable=all", "--enable=fixme", "--notes=???", target],
    cwd=root,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
)
out, err = proc.communicate(timeout=60)
text = out.decode("utf-8", "replace") + err.decode("utf-8", "replace")
print("exit", proc.returncode)
print(text)
assert "Traceback" not in text
assert "W0511" in text or "fixme" in text.lower()
''',
        ),
        "pylint-dev__pylint-7228": (
            "upgrade-fullpkg-pylint-regex-property-escape-no-traceback",
            "Run pylint with an unsupported unicode-property regexp and require a controlled diagnostic.",
            "full_package_behavioral_probe",
            r'''
import os
import subprocess
import sys
import tempfile

root = tempfile.mkdtemp(prefix="patchcourt_pylint_regex_")
target = os.path.join(root, "sample.py")
with open(target, "w") as handle:
    handle.write("def sample_name():\n    return 1\n")
proc = subprocess.Popen(
    [sys.executable, "-m", "pylint", "--disable=all", r"--function-rgx=[\p{Han}a-z_][\p{Han}a-z0-9_]{2,30}$", target],
    cwd=root,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
)
out, err = proc.communicate(timeout=60)
text = out.decode("utf-8", "replace") + err.decode("utf-8", "replace")
print("exit", proc.returncode)
print(text)
assert proc.returncode != 0
assert "Traceback" not in text
assert "function-rgx" in text or "bad escape" in text or "\\p" in text
''',
        ),
        "scikit-learn__scikit-learn-10508": (
            "upgrade-fullpkg-sklearn-labelencoder-empty-transform",
            "Execute the public LabelEncoder empty-list reproducer through sklearn.preprocessing.",
            "full_package_behavioral_probe",
            r'''
from sklearn.preprocessing import LabelEncoder

le = LabelEncoder()
le.fit(["a", "b"])
out = le.transform([])
print("empty_shape", getattr(out, "shape", None))
print("empty_size", getattr(out, "size", None))
assert getattr(out, "shape", None) == (0,)
assert getattr(out, "size", None) == 0
''',
        ),
        "matplotlib__matplotlib-24149": (
            "upgrade-fullpkg-matplotlib-bar-all-nan",
            "Execute the public ax.bar all-NaN reproducer through matplotlib.",
            "full_package_behavioral_probe",
            r'''
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

fig, ax = plt.subplots()
bars = ax.bar([np.nan], [np.nan])
fig.canvas.draw()
print("bar_count", len(bars))
print("bar_x", bars[0].get_x())
assert len(bars) == 1
plt.close(fig)
''',
        ),
        "pytest-dev__pytest-11148": (
            "upgrade-issuecode-pytest-importlib-namespace",
            "Run a namespace-package importlib-mode pytest reproducer.",
            "issue_codeblock_full_package",
            r'''
import os
import subprocess
import sys
import tempfile
import textwrap

root = tempfile.mkdtemp(prefix="patchcourt_pytest_importlib_")
pkg = os.path.join(root, "pmxbot")
tests = os.path.join(root, "tests", "unit")
os.makedirs(pkg)
os.makedirs(tests)
with open(os.path.join(pkg, "logging.py"), "w") as handle:
    handle.write("class Logger:\n    store = None\n")
with open(os.path.join(tests, "test_commands.py"), "w") as handle:
    handle.write(textwrap.dedent("""
        import sys
        import pmxbot.logging as logging

        def test_import_identity():
            assert sys.modules["pmxbot.logging"] is logging
    """))
cmd = [sys.executable, "-m", "pytest", "--import-mode=importlib", os.path.join(tests, "test_commands.py"), "-q"]
proc = subprocess.Popen(cmd, cwd=root, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
out, err = proc.communicate(timeout=60)
text = out.decode("utf-8", "replace") + err.decode("utf-8", "replace")
print(text)
assert proc.returncode == 0
''',
        ),
        "pytest-dev__pytest-8906": (
            "upgrade-issuecode-pytest-module-skip-message",
            "Run the module-level pytest.skip error-message reproducer.",
            "issue_codeblock_full_package",
            r'''
import os
import subprocess
import sys
import tempfile
import textwrap

root = tempfile.mkdtemp(prefix="patchcourt_pytest_skip_")
test_file = os.path.join(root, "test_module_skip.py")
with open(test_file, "w") as handle:
    handle.write(textwrap.dedent("""
        import pytest
        pytest.skip(msg="Requires Python >= 3.8")
        def test_never():
            assert False
    """))
proc = subprocess.Popen([sys.executable, "-m", "pytest", test_file, "-q"], cwd=root, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
out, err = proc.communicate(timeout=60)
text = out.decode("utf-8", "replace") + err.decode("utf-8", "replace")
print(text)
assert "allow_module_level=True" in text
''',
        ),
        "sympy__sympy-23117": (
            "upgrade-issuecode-sympy-empty-array",
            "Execute the public sympy Array([]) reproducer.",
            "issue_codeblock_full_package",
            r'''
from sympy import Array

a = Array([])
print("array", a)
print("shape", getattr(a, "shape", None))
assert getattr(a, "shape", None) == (0,)
''',
        ),
        "sympy__sympy-17655": (
            "upgrade-issuecode-sympy-point-left-scalar",
            "Execute the public Point left scalar multiplication reproducer.",
            "issue_codeblock_full_package",
            r'''
from sympy import geometry as ge
import sympy

point1 = ge.Point(0, 0)
point2 = ge.Point(1, 1)
result = point1 + sympy.sympify(2.0) * point2
print("result", result)
assert result == ge.Point(2.0, 2.0)
''',
        ),
        "django__django-16873": (
            "upgrade-fullpkg-django-join-autoescape-off",
            "Render the public join filter autoescape-off reproducer through Django templates.",
            "full_package_behavioral_probe",
            r'''
from django.template import Context, Engine

engine = Engine()
template = engine.from_string("{% autoescape off %}{{ some_list|join:some_var }}{% endautoescape %}")
some_list = ["<p>Hello World!</p>", "beta & me", "<script>Hi!</script>"]
some_var = "<br/>"
output = template.render(Context({"some_list": some_list, "some_var": some_var}))
expected = some_var.join(some_list)
print("output", output)
assert output == expected
''',
        ),
        "django__django-16255": (
            "upgrade-fullpkg-django-empty-sitemap-lastmod",
            "Execute empty Sitemap.get_latest_lastmod with callable lastmod.",
            "full_package_behavioral_probe",
            r'''
from django.contrib.sitemaps import Sitemap

class EmptySitemap(Sitemap):
    def items(self):
        return []
    def lastmod(self, item):
        return item

site = EmptySitemap()
result = site.get_latest_lastmod()
print("latest", result)
assert result is None
''',
        ),
        "mwaskom__seaborn-3010": (
            "upgrade-fullpkg-seaborn-polyfit-drop-missing-data",
            "Execute PolyFit on x/y data with missing rows and require finite fitted values.",
            "full_package_behavioral_probe",
            r'''
import numpy as np
import pandas as pd
from seaborn._stats.regression import PolyFit

class DirectGroupBy:
    def apply(self, data, func):
        return func(data)

data = pd.DataFrame({"x": [0.0, 1.0, np.nan, 3.0], "y": [1.0, 3.0, 5.0, np.nan]})
out = PolyFit(order=1, gridsize=5)(data, DirectGroupBy(), orient="x", scales={})
print(out)
assert len(out) == 5
assert np.isfinite(out["x"]).all()
assert np.isfinite(out["y"]).all()
''',
        ),
        "mwaskom__seaborn-3190": (
            "upgrade-fullpkg-seaborn-continuous-bool-interval",
            "Set up a continuous interval scale over boolean data without boolean subtraction.",
            "full_package_behavioral_probe",
            r'''
import pandas as pd
from seaborn._core.properties import IntervalProperty
from seaborn._core.scales import Continuous

data = pd.Series([True, False, False], name="flag")
scale = Continuous()._setup(data, IntervalProperty())
print("scale", type(scale).__name__)
print("pipeline_len", len(getattr(scale, "_pipeline", [])))
assert scale is not None
assert getattr(scale, "_pipeline", None)
''',
        ),
        "mwaskom__seaborn-3407": (
            "upgrade-fullpkg-seaborn-pairplot-multiindex",
            "Execute the public seaborn pairplot MultiIndex DataFrame reproducer.",
            "full_package_behavioral_probe",
            r'''
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

data = {
    ("A", "1"): np.random.RandomState(0).rand(8),
    ("A", "2"): np.random.RandomState(1).rand(8),
    ("B", "1"): np.random.RandomState(2).rand(8),
    ("B", "2"): np.random.RandomState(3).rand(8),
}
df = pd.DataFrame(data)
grid = sns.pairplot(df)
print("axes_shape", getattr(grid.axes, "shape", None))
assert grid is not None
plt.close("all")
''',
        ),
        "astropy__astropy-14365": (
            "upgrade-fullpkg-astropy-qdp-lowercase-read",
            "Execute the public lowercase QDP READ reproducer through astropy Table.read.",
            "full_package_behavioral_probe",
            r'''
import os
import tempfile
from astropy.table import Table

path = os.path.join(tempfile.mkdtemp(prefix="patchcourt_qdp_"), "test.qdp")
with open(path, "w") as handle:
    handle.write("read serr 1 2\n1 0.5 1 0.5\n")
table = Table.read(path, format="ascii.qdp")
print("columns", table.colnames)
print("rows", len(table))
assert len(table) == 1
''',
        ),
    }
    value = probes.get(task_id)
    if not value:
        return None
    probe_id, description, layer, code = value
    code = code.strip() + "\n"
    return {
        "probe_id": probe_id,
        "description": description,
        "probe_layer": layer,
        "code": code,
        "code_sha256": hashlib.sha256(code.encode("utf-8", "replace")).hexdigest(),
    }


def package_integrity_probe(task_id):
    if task_id.startswith("mwaskom__seaborn"):
        value = (
            "upgrade-fullpkg-integrity-seaborn-import-core",
            "Import seaborn and selected core modules as a full-package integrity check.",
            "full_package_integrity_probe",
            r'''
import seaborn as sns
from seaborn._core.scales import Continuous
from seaborn._stats.regression import PolyFit

print("seaborn", getattr(sns, "__version__", "unknown"))
print("continuous", Continuous.__name__)
print("polyfit", PolyFit.__name__)
''',
        )
    elif task_id.startswith("pallets__flask"):
        value = (
            "upgrade-fullpkg-integrity-flask-import-core",
            "Import Flask and construct a minimal app as a full-package integrity check.",
            "full_package_integrity_probe",
            r'''
from flask import Flask

app = Flask(__name__)
print("flask_app", app.name)
assert app is not None
''',
        )
    elif task_id.startswith("scikit-learn__scikit-learn"):
        value = (
            "upgrade-fullpkg-integrity-sklearn-preprocessing-import",
            "Import sklearn.preprocessing.LabelEncoder as a full-package integrity check.",
            "full_package_integrity_probe",
            r'''
from sklearn.preprocessing import LabelEncoder

print("label_encoder", LabelEncoder.__name__)
assert LabelEncoder is not None
''',
        )
    elif task_id.startswith("pylint-dev__pylint"):
        value = (
            "upgrade-fullpkg-integrity-pylint-import-core",
            "Import Pylint Run and expand_modules as a full-package integrity check.",
            "full_package_integrity_probe",
            r'''
from pylint.lint import Run
from pylint.lint.expand_modules import expand_modules

print("run", Run.__name__)
print("expand_modules", callable(expand_modules))
assert callable(expand_modules)
''',
        )
    elif task_id.startswith("pydata__xarray"):
        value = (
            "upgrade-fullpkg-integrity-xarray-import-core",
            "Import xarray and construct a small DataArray as a full-package integrity check.",
            "full_package_integrity_probe",
            r'''
import xarray as xr

array = xr.DataArray([1, 2], dims=("x",), name="value")
print("xarray", getattr(xr, "__version__", "unknown"))
print("dims", array.dims)
assert array.dims == ("x",)
''',
        )
    else:
        return None
    probe_id, description, layer, code = value
    code = code.strip() + "\n"
    return {
        "probe_id": probe_id,
        "description": description,
        "probe_layer": layer,
        "code": code,
        "code_sha256": hashlib.sha256(code.encode("utf-8", "replace")).hexdigest(),
    }


def qwen_issue_rescue_probe(task_id):
    """Focused issue probes for Qwen visible-pass tasks.

    This suite is append-only and intentionally narrow. It fixes a subprocess
    routing issue in earlier Pylint probes where child `python -m pylint`
    invocations ran from a temporary directory without an absolute candidate
    repository PYTHONPATH.
    """
    probes = {
        "pylint-dev__pylint-5859": (
            "qwen-rescue-pylint-punctuation-note-tag",
            "Run Pylint fixme detection with a punctuation-only notes tag using an absolute candidate PYTHONPATH.",
            "issue_codeblock_full_package",
            r'''
import os
import subprocess
import sys
import tempfile

candidate_repo = os.getcwd()
env = os.environ.copy()
env["PYTHONPATH"] = os.pathsep.join([
    candidate_repo,
    os.path.join(candidate_repo, "src"),
    os.path.join(candidate_repo, "lib"),
    env.get("PYTHONPATH", ""),
])

root = tempfile.mkdtemp(prefix="patchcourt_pylint_notes_abs_")
target = os.path.join(root, "sample.py")
with open(target, "w") as handle:
    handle.write("# ???: investigate this path\nVALUE = 1\n")
proc = subprocess.Popen(
    [sys.executable, "-m", "pylint", "--disable=all", "--enable=fixme", "--notes=???", target],
    cwd=root,
    env=env,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
)
out, err = proc.communicate(timeout=60)
text = out.decode("utf-8", "replace") + err.decode("utf-8", "replace")
print("exit", proc.returncode)
print(text)
assert "No module named pylint" not in text
assert "Traceback" not in text
assert "W0511" in text or "fixme" in text.lower()
''',
        ),
        "pylint-dev__pylint-7228": (
            "qwen-rescue-pylint-regex-property-escape-no-traceback",
            "Run Pylint with an unsupported unicode-property regexp using an absolute candidate PYTHONPATH.",
            "issue_codeblock_full_package",
            r'''
import os
import subprocess
import sys
import tempfile

candidate_repo = os.getcwd()
env = os.environ.copy()
env["PYTHONPATH"] = os.pathsep.join([
    candidate_repo,
    os.path.join(candidate_repo, "src"),
    os.path.join(candidate_repo, "lib"),
    env.get("PYTHONPATH", ""),
])

root = tempfile.mkdtemp(prefix="patchcourt_pylint_regex_abs_")
target = os.path.join(root, "sample.py")
with open(target, "w") as handle:
    handle.write("def sample_name():\n    return 1\n")
proc = subprocess.Popen(
    [sys.executable, "-m", "pylint", "--disable=all", r"--function-rgx=[\p{Han}a-z_][\p{Han}a-z0-9_]{2,30}$", target],
    cwd=root,
    env=env,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
)
out, err = proc.communicate(timeout=60)
text = out.decode("utf-8", "replace") + err.decode("utf-8", "replace")
print("exit", proc.returncode)
print(text)
assert "No module named pylint" not in text
assert proc.returncode != 0
assert "Traceback" not in text
assert "function-rgx" in text or "bad escape" in text or "\\p" in text
''',
        ),
    }
    value = probes.get(task_id)
    if not value:
        return None
    probe_id, description, layer, code = value
    code = code.strip() + "\n"
    return {
        "probe_id": probe_id,
        "description": description,
        "probe_layer": layer,
        "code": code,
        "code_sha256": hashlib.sha256(code.encode("utf-8", "replace")).hexdigest(),
    }


def artifact_paths(queue_dir, task_id, candidate_id, probe_id):
    artifact_dir = os.path.join(queue_dir, "probe_artifacts", safe_id(task_id), safe_id(candidate_id), safe_id(probe_id))
    return {
        "dir": artifact_dir,
        "stdout": os.path.join(artifact_dir, "stdout.txt"),
        "stderr": os.path.join(artifact_dir, "stderr.txt"),
        "code": os.path.join(artifact_dir, "probe.py"),
        "result": os.path.join(artifact_dir, "result.json"),
    }


def run_probe(record, candidate_id, candidate_repo, probe, args, queue_dir):
    route = task_route(args.task_env_routes, record.get("task_id"))
    effective_venv = route.get("venv_dir") or args.venv_dir
    pre_probe_results = run_pre_probe_steps(candidate_repo, route, effective_venv, args)
    artifacts = artifact_paths(queue_dir, record.get("task_id"), candidate_id, probe["probe_id"])
    write_text(artifacts["code"], probe["code"])
    started = time.time()
    timed_out = False
    try:
        proc = subprocess.Popen(
            [python_path(effective_venv), "-W", "ignore", "-"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=candidate_repo,
            env=probe_env(effective_venv, args.gpu),
        )
        try:
            out, err = proc.communicate(probe["code"].encode("utf-8"), timeout=args.timeout_sec)
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
    normalized_stdout = normalize_stream(stdout_full, candidate_repo, args.snapshot_run_dir)
    normalized_stderr = normalize_stream(stderr_full, candidate_repo, args.snapshot_run_dir)
    stdout, stdout_truncated = truncate(stdout_full)
    stderr, stderr_truncated = truncate(stderr_full)
    if timed_out:
        outcome = "timeout"
    elif exit_code == 0:
        outcome = "pass"
    else:
        outcome = "fail"
    source = semicolon_value_for(record, "candidate_sources", candidate_id, source_from_candidate_id(candidate_id))
    model_generated = parse_bool_text(
        semicolon_value_for(record, "candidate_model_generated_flags", candidate_id, ""),
        is_model_candidate(candidate_id),
    )
    heuristic = parse_bool_text(semicolon_value_for(record, "candidate_heuristic_flags", candidate_id, ""), False)
    expected_behavior_change = parse_bool_text(
        semicolon_value_for(record, "candidate_expected_behavior_change_flags", candidate_id, ""),
        source != "noop_control",
    )
    generation_backend = semicolon_value_for(
        record,
        "candidate_generation_backends",
        candidate_id,
        "codex_session_bootstrap" if model_generated else "noop_control",
    )
    semantic_template = semicolon_value_for(record, "candidate_semantic_templates", candidate_id, "")
    result = {
        "schema_version": "0.1",
        "queue_id": args.queue_id,
        "apply_queue_id": record.get("apply_queue_id"),
        "probe_id": probe.get("probe_id"),
        "probe_description": probe.get("description"),
        "probe_generation_strategy": "manual_audit_probe_upgrade",
        "probe_layer": probe.get("probe_layer"),
        "probe_language": "python",
        "probe_code_block_index": -1,
        "probe_code_sha256": probe.get("code_sha256"),
        "task_id": record.get("task_id"),
        "repo": record.get("repo"),
        "candidate_id": candidate_id,
        "candidate_source": source,
        "candidate_repo": candidate_repo,
        "candidate_semantic_template": semantic_template,
        "candidate_expected_behavior_change": expected_behavior_change,
        "candidate_model_generated": model_generated,
        "candidate_heuristic": heuristic,
        "candidate_generation_backend": generation_backend,
        "task_environment_route": route,
        "effective_venv_dir": effective_venv,
        "pre_probe_results": pre_probe_results,
        "exit_code": exit_code,
        "outcome": outcome,
        "timed_out": timed_out,
        "duration_sec": round(finished - started, 3),
        "started_at": utc_now(),
        "finished_at": utc_now(),
        "stdout": stdout,
        "stderr": stderr,
        "normalized_stdout_sha256": hashlib.sha256(normalized_stdout.encode("utf-8", "replace")).hexdigest(),
        "normalized_stderr_sha256": hashlib.sha256(normalized_stderr.encode("utf-8", "replace")).hexdigest(),
        "stdout_truncated": stdout_truncated,
        "stderr_truncated": stderr_truncated,
        "stdout_artifact": stream_record(artifacts["stdout"], stdout_full),
        "stderr_artifact": stream_record(artifacts["stderr"], stderr_full),
        "probe_code_path": artifacts["code"],
        "gold_used": False,
    }
    result["behavior_hash"] = hashlib.sha256(
        (str(exit_code) + "\n" + normalized_stdout + "\n" + normalized_stderr).encode("utf-8", "replace")
    ).hexdigest()
    result["behavior_hash_basis"] = "exit_code_plus_path_normalized_stdout_stderr"
    write_json(artifacts["result"], result)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot-run-dir", required=True)
    parser.add_argument("--upgrade-targets", required=True)
    parser.add_argument("--queue-id", required=True)
    parser.add_argument("--gpu", default="4")
    parser.add_argument("--timeout-sec", type=int, default=120)
    parser.add_argument("--venv-dir", default="")
    parser.add_argument("--task-env-map", default="")
    parser.add_argument(
        "--probe-suite",
        choices=["issue_upgrade", "package_integrity", "qwen_issue_rescue"],
        default="issue_upgrade",
    )
    args = parser.parse_args(argv)
    args.task_env_routes = load_task_env_routes(args.task_env_map)

    targets = read_json(args.upgrade_targets)
    queue_dir = os.path.join(args.snapshot_run_dir, "issue_probe_queues", args.queue_id)
    result_path = os.path.join(queue_dir, "issue_probe_results.jsonl")
    summary = {
        "schema_version": "0.1",
        "queue_id": args.queue_id,
        "snapshot_run_dir": args.snapshot_run_dir,
        "upgrade_targets": args.upgrade_targets,
        "target_count": len(targets),
        "venv_dir": args.venv_dir,
        "task_env_map": args.task_env_map,
        "timeout_sec": args.timeout_sec,
        "probe_suite": args.probe_suite,
        "gpu": args.gpu,
        "started_at": utc_now(),
        "gold_used": False,
        "task_counts": {},
        "outcome_counts": {},
        "probe_layers": {},
        "probe_result_count": 0,
    }
    for record in targets:
        task_id = record.get("task_id")
        if args.probe_suite == "package_integrity":
            probe = package_integrity_probe(task_id)
        elif args.probe_suite == "qwen_issue_rescue":
            probe = qwen_issue_rescue_probe(task_id)
        else:
            probe = upgraded_probe(task_id)
        if not probe:
            continue
        candidate_ids = split_semicolon(record.get("candidate_ids"))
        candidate_repos = split_semicolon(record.get("candidate_repos"))
        for candidate_id, candidate_repo in zip(candidate_ids, candidate_repos):
            result = run_probe(record, candidate_id, candidate_repo, probe, args, queue_dir)
            append_jsonl(result_path, result)
            summary["probe_result_count"] += 1
            summary["task_counts"][task_id] = summary["task_counts"].get(task_id, 0) + 1
            outcome = result.get("outcome") or "unknown"
            summary["outcome_counts"][outcome] = summary["outcome_counts"].get(outcome, 0) + 1
            layer = probe.get("probe_layer") or "unknown"
            summary["probe_layers"][layer] = summary["probe_layers"].get(layer, 0) + 1
    summary["finished_at"] = utc_now()
    summary["result_path"] = result_path
    write_json(os.path.join(queue_dir, "audit_probe_upgrade_summary.json"), summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
