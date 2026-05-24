# Build and Publish

Clean previous build output:

```bash
rm -rf dist build *.egg-info
```

Create a publish test environment:

```bash
python3 -m venv .venv-publish-test
source .venv-publish-test/bin/activate
python -m pip install --upgrade pip build twine
```

Build and check the package:

```bash
python -m build
python -m twine check dist/*
```

Install the built wheel in a clean environment:

```bash
python -m venv /tmp/webcam2rtsp-test
source /tmp/webcam2rtsp-test/bin/activate
pip install dist/*.whl
webcam2rtsp --help
webcam2rtsp-doctor
python -c "import webcam2rtsp; print(webcam2rtsp.__version__)"
```

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

Upload to TestPyPI:

```bash
python -m twine upload --repository testpypi dist/*
```

Upload to PyPI:

```bash
python -m twine upload dist/*
```
