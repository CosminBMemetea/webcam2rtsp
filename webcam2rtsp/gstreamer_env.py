import os
import platform
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Check:
    label: str
    ok: bool
    detail: str


def _prepend_env_path(name, value):
    if not value:
        return
    current = os.environ.get(name)
    parts = current.split(os.pathsep) if current else []
    if value not in parts:
        os.environ[name] = os.pathsep.join([value, *parts]) if current else value


def _set_env_if_missing(name, value):
    if value and not os.environ.get(name):
        os.environ[name] = value


def _existing_dir(*parts):
    path = Path(*parts)
    return str(path) if path.is_dir() else None


def _mac_homebrew_prefix():
    for prefix in (Path("/opt/homebrew"), Path("/usr/local")):
        if (prefix / "bin" / "gst-launch-1.0").exists() or (prefix / "lib" / "girepository-1.0").is_dir():
            return prefix
    brew = shutil.which("brew")
    if not brew:
        return None
    try:
        result = subprocess.run(
            [brew, "--prefix"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    prefix = Path(result.stdout.strip())
    return prefix if prefix.exists() else None


def _windows_gstreamer_root():
    env_names = (
        "GSTREAMER_1_0_ROOT_MSVC_X86_64",
        "GSTREAMER_1_0_ROOT_MINGW_X86_64",
        "GSTREAMER_1_0_ROOT_X86_64",
    )
    for name in env_names:
        value = os.environ.get(name)
        if value and Path(value).exists():
            return Path(value)

    candidates = (
        Path("C:/gstreamer/1.0/msvc_x86_64"),
        Path("C:/gstreamer/1.0/mingw_x86_64"),
    )
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def configure_gstreamer_environment():
    """Set common native GStreamer paths before importing gi."""
    os_name = platform.system().lower()

    if os_name == "darwin":
        prefix = _mac_homebrew_prefix()
        if not prefix:
            return
        _prepend_env_path("PATH", str(prefix / "bin"))
        _set_env_if_missing("DYLD_LIBRARY_PATH", str(prefix / "lib"))
        _set_env_if_missing("DYLD_FALLBACK_LIBRARY_PATH", str(prefix / "lib"))
        _set_env_if_missing("GI_TYPELIB_PATH", str(prefix / "lib" / "girepository-1.0"))
        _set_env_if_missing("GST_PLUGIN_PATH", str(prefix / "lib" / "gstreamer-1.0"))
        _set_env_if_missing("GST_PLUGIN_SYSTEM_PATH_1_0", str(prefix / "lib" / "gstreamer-1.0"))
        return

    if os_name == "windows":
        root = _windows_gstreamer_root()
        if not root:
            return
        _prepend_env_path("PATH", _existing_dir(root, "bin"))
        _set_env_if_missing("GI_TYPELIB_PATH", _existing_dir(root, "lib", "girepository-1.0"))
        _set_env_if_missing("GST_PLUGIN_PATH", _existing_dir(root, "lib", "gstreamer-1.0"))
        _set_env_if_missing("GST_PLUGIN_SYSTEM_PATH_1_0", _existing_dir(root, "lib", "gstreamer-1.0"))


def _file_check(label, path):
    path = Path(path)
    return Check(label, path.exists(), str(path))


def _command_check(command):
    found = shutil.which(command)
    return Check(command, bool(found), found or "not found on PATH")


def _python_import_check(module):
    script = f"import {module}; print('ok')"
    result = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        text=True,
        env=os.environ.copy(),
    )
    detail = "ok" if result.returncode == 0 else (result.stderr.strip() or result.stdout.strip())
    return Check(f"python import {module}", result.returncode == 0, detail)


def _gi_version_check(namespace):
    script = (
        "import gi\n"
        f"gi.require_version('{namespace}', '1.0')\n"
        "print('ok')\n"
    )
    result = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        text=True,
        env=os.environ.copy(),
    )
    detail = "ok" if result.returncode == 0 else (result.stderr.strip() or result.stdout.strip())
    return Check(f"GI typelib {namespace}-1.0", result.returncode == 0, detail)


def shell_exports():
    configure_gstreamer_environment()
    os_name = platform.system().lower()

    if os_name == "darwin":
        prefix = _mac_homebrew_prefix()
        if not prefix:
            return []
        return [
            f'export PATH="{prefix / "bin"}:$PATH"',
            f'export DYLD_LIBRARY_PATH="{prefix / "lib"}"',
            f'export DYLD_FALLBACK_LIBRARY_PATH="{prefix / "lib"}"',
            f'export GI_TYPELIB_PATH="{prefix / "lib" / "girepository-1.0"}"',
            f'export GST_PLUGIN_PATH="{prefix / "lib" / "gstreamer-1.0"}"',
            f'export GST_PLUGIN_SYSTEM_PATH_1_0="{prefix / "lib" / "gstreamer-1.0"}"',
        ]

    if os_name == "windows":
        root = _windows_gstreamer_root()
        if not root:
            return []
        return [
            f'$env:PATH = "{root / "bin"};$env:PATH"',
            f'$env:GI_TYPELIB_PATH = "{root / "lib" / "girepository-1.0"}"',
            f'$env:GST_PLUGIN_PATH = "{root / "lib" / "gstreamer-1.0"}"',
            f'$env:GST_PLUGIN_SYSTEM_PATH_1_0 = "{root / "lib" / "gstreamer-1.0"}"',
        ]

    return []


def doctor_checks():
    configure_gstreamer_environment()
    os_name = platform.system().lower()
    checks = []

    if os_name == "darwin":
        prefix = _mac_homebrew_prefix() or Path("/opt/homebrew")
        checks.extend(
            [
                _command_check("brew"),
                _command_check("gst-launch-1.0"),
                _file_check("libglib", prefix / "lib" / "libglib-2.0.0.dylib"),
                _file_check("libgobject", prefix / "lib" / "libgobject-2.0.0.dylib"),
                _file_check("Gst typelib", prefix / "lib" / "girepository-1.0" / "Gst-1.0.typelib"),
                _file_check(
                    "GstRtspServer typelib",
                    prefix / "lib" / "girepository-1.0" / "GstRtspServer-1.0.typelib",
                ),
            ]
        )
    elif os_name == "windows":
        root = _windows_gstreamer_root() or Path("C:/gstreamer/1.0/msvc_x86_64")
        checks.extend(
            [
                _file_check("GStreamer bin", root / "bin"),
                _file_check("gstreamer dll", root / "bin" / "gstreamer-1.0-0.dll"),
                _file_check("Gst typelib", root / "lib" / "girepository-1.0" / "Gst-1.0.typelib"),
                _file_check(
                    "GstRtspServer typelib",
                    root / "lib" / "girepository-1.0" / "GstRtspServer-1.0.typelib",
                ),
            ]
        )
    else:
        checks.extend(
            [
                _command_check("gst-launch-1.0"),
                _command_check("gst-inspect-1.0"),
            ]
        )

    checks.extend(
        [
            _python_import_check("gi"),
            _gi_version_check("Gst"),
            _gi_version_check("GstRtspServer"),
        ]
    )
    return checks


def install_hint():
    os_name = platform.system().lower()
    if os_name == "darwin":
        return (
            "brew install gstreamer gst-plugins-base gst-plugins-good gst-libav "
            "gst-plugins-bad gst-plugins-ugly pygobject3\n"
            "python -m pip install --upgrade PyGObject"
        )
    if os_name == "windows":
        return "Install GStreamer MSVC runtime and development packages from https://gstreamer.freedesktop.org/download/"
    return (
        "Debian/Ubuntu: sudo apt install python3-gi python3-gst-1.0 "
        "gir1.2-gst-rtsp-server-1.0 gstreamer1.0-tools "
        "gstreamer1.0-plugins-base gstreamer1.0-plugins-good "
        "gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly\n"
        "Virtualenv users may also need: python -m pip install --upgrade PyGObject"
    )


def doctor_main():
    checks = doctor_checks()
    for check in checks:
        status = "ok" if check.ok else "missing"
        print(f"[{status}] {check.label}: {check.detail}")

    failed = [check for check in checks if not check.ok]
    if failed:
        print("\nSuggested install:")
        print(install_hint())

    exports = shell_exports()
    if exports:
        print("\nDetected environment exports:")
        for line in exports:
            print(line)

    return 1 if failed else 0
