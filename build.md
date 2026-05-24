# Build and Publish

This package is pure Python, but it depends on native GStreamer and PyGObject
being installed on the user's machine. Do not make `PyGObject` a hard
dependency in `pyproject.toml`; Windows users cannot reliably install it from
normal PyPI.

## 1. Clean

```bash
rm -rf dist build *.egg-info
```

## 2. Create a Publish Environment

```bash
python3 -m venv .venv-publish-test
source .venv-publish-test/bin/activate
python -m pip install --upgrade pip build twine
```

## 3. Build

```bash
python -m build
```

Expected output:

```text
dist/webcam2rtsp-0.1.0.tar.gz
dist/webcam2rtsp-0.1.0-py3-none-any.whl
```

## 4. Check Package Metadata

```bash
python -m twine check dist/*
```

## 5. Install The Wheel Locally

```bash
python -m venv /tmp/webcam2rtsp-test
source /tmp/webcam2rtsp-test/bin/activate
python -m pip install dist/*.whl
webcam2rtsp --help
webcam2rtsp-doctor
python -c "import webcam2rtsp; print(webcam2rtsp.__version__)"
```

On Debian/Ubuntu, test native `gi` with system packages visible:

```bash
python3 -m venv --system-site-packages /tmp/webcam2rtsp-linux-test
source /tmp/webcam2rtsp-linux-test/bin/activate
python -m pip install dist/*.whl
webcam2rtsp-doctor
```

## 6. Create PyPI API Tokens

In your browser:

1. Open `https://test.pypi.org/manage/account/token/`
2. Create a TestPyPI token.
3. Open `https://pypi.org/manage/account/token/`
4. Create a PyPI token.

Use `__token__` as the username when `twine` asks.
Use the token value, including the `pypi-` prefix, as the password.

## 7. Upload To TestPyPI First

```bash
python -m twine upload --repository testpypi dist/*
```

Test the upload:

```bash
python -m venv /tmp/webcam2rtsp-testpypi
source /tmp/webcam2rtsp-testpypi/bin/activate
python -m pip install --index-url https://test.pypi.org/simple/ --no-deps webcam2rtsp
webcam2rtsp --help
```

## 8. Upload To PyPI

Only do this after TestPyPI works:

```bash
python -m twine upload dist/*
```

Then test the public package:

```bash
python -m venv /tmp/webcam2rtsp-pypi
source /tmp/webcam2rtsp-pypi/bin/activate
python -m pip install webcam2rtsp
webcam2rtsp --help
webcam2rtsp-doctor
```

## macOS GStreamer Check

Print detected GStreamer shell exports:

```bash
webcam2rtsp --print-env
```

On macOS with Homebrew, the output should look similar to:

```bash
export PATH="/opt/homebrew/bin:$PATH"
export DYLD_LIBRARY_PATH="/opt/homebrew/lib"
export DYLD_FALLBACK_LIBRARY_PATH="/opt/homebrew/lib"
export GI_TYPELIB_PATH="/opt/homebrew/lib/girepository-1.0"
export GST_PLUGIN_PATH="/opt/homebrew/lib/gstreamer-1.0"
export GST_PLUGIN_SYSTEM_PATH_1_0="/opt/homebrew/lib/gstreamer-1.0"
```

Verify the expected macOS Homebrew files manually when needed:

```bash
ls -la /opt/homebrew/lib/libglib-2.0.0.dylib
ls -la /opt/homebrew/lib/libgobject-2.0.0.dylib
ls -la /opt/homebrew/lib/girepository-1.0/Gst-1.0.typelib
ls -la /opt/homebrew/lib/girepository-1.0/GstRtspServer-1.0.typelib
```
