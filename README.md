# webcam2rtsp

`webcam2rtsp` streams a local laptop or USB webcam over RTSP using Python and
GStreamer. It supports Linux, macOS, and Windows when the matching GStreamer
camera source plugin is installed.

Default stream URL:

```text
rtsp://<computer-ip>:8854/webcam1
```

## Features

- RTSP server with configurable bind address, port, and mount path
- Platform defaults for Linux, macOS, and Windows webcams
- Configurable camera device, resolution, framerate, and H.264 bitrate
- Custom GStreamer source support for unusual camera drivers
- Compatible with VLC, FFplay, and other RTSP clients

## Install GStreamer

### macOS

```bash
brew install gstreamer gst-plugins-base gst-plugins-good gst-libav gst-plugins-bad gst-plugins-ugly pygobject3
```

If Python cannot find the GStreamer libraries, export these variables:

```bash
webcam2rtsp --print-env
```

The command detects `/opt/homebrew` on Apple Silicon Macs and `/usr/local` on
Intel Macs. It prints values like `PATH`, `DYLD_LIBRARY_PATH`,
`GI_TYPELIB_PATH`, `GST_PLUGIN_PATH`, and `GST_PLUGIN_SYSTEM_PATH_1_0` only when
those paths exist.

### Linux

Debian/Ubuntu:

```bash
sudo apt update
sudo apt install -y python3-gi python3-gst-1.0 gir1.2-gst-rtsp-server-1.0 \
  gstreamer1.0-tools gstreamer1.0-plugins-base gstreamer1.0-plugins-good \
  gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly
```

Fedora:

```bash
sudo dnf install -y python3-gobject gstreamer1 gstreamer1-plugins-base \
  gstreamer1-plugins-good gstreamer1-plugins-bad-free gstreamer1-plugins-ugly \
  gstreamer1-rtsp-server
```

### Windows

Install the GStreamer MSVC runtime and development packages from:

```text
https://gstreamer.freedesktop.org/download/
```

During install, include the base, good, bad, ugly, libav, and RTSP server
components. Add GStreamer's `bin` directory to `PATH`, for example:

```powershell
$env:PATH += ";C:\gstreamer\1.0\msvc_x86_64\bin"
```

## Install webcam2rtsp

After installing GStreamer for your operating system:

```bash
python -m pip install webcam2rtsp
```

Verify the native GStreamer setup:

```bash
webcam2rtsp-doctor
```

On macOS and Windows, `webcam2rtsp` automatically detects common GStreamer
install paths before importing PyGObject. If your shell still needs the same
values permanently, print them with:

```bash
webcam2rtsp --print-env
```

Then add the printed lines to your shell profile, such as `~/.zshrc` on macOS.

For local development from this repository:

```bash
git clone https://github.com/cosminmemetea/webcam2rtsp.git
cd webcam2rtsp
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -e .
```

Local development can run the same checks with:

```bash
python -m webcam2rtsp --doctor
python -m webcam2rtsp --print-env
```

## Run

Use the default webcam:

```bash
python -m webcam2rtsp
```

Open the stream from another machine on the same network:

```text
rtsp://<computer-ip>:8854/webcam1
```

Local test with FFplay:

```bash
ffplay rtsp://127.0.0.1:8854/webcam1
```

## Configuration

```bash
python -m webcam2rtsp \
  --address 0.0.0.0 \
  --port 8554 \
  --mount-point /camera \
  --device /dev/video2 \
  --width 1280 \
  --height 720 \
  --framerate 30 \
  --bitrate 2500
```

Device examples:

```bash
# Linux
python -m webcam2rtsp --device /dev/video0

# macOS
python -m webcam2rtsp --device 0

# Windows
python -m webcam2rtsp --device 0
```

Use a custom GStreamer source when the default source is not right for your
camera:

```bash
python -m webcam2rtsp --source "autovideosrc"
python -m webcam2rtsp --source "dshowvideosrc device-name=\"Integrated Camera\""
```

Available options:

```bash
python -m webcam2rtsp --help
```

## Publish to PyPI

Build the package:

```bash
python -m pip install --upgrade build twine
python -m build
```

Check the package metadata:

```bash
python -m twine check dist/*
```

Upload to TestPyPI first:

```bash
python -m twine upload --repository testpypi dist/*
```

Upload to PyPI when the TestPyPI package installs correctly:

```bash
python -m twine upload dist/*
```

## Platform Defaults

- Linux: `v4l2src device="/dev/video0"`
- macOS: `avfvideosrc device-index=0`
- Windows: `mfvideosrc device-index=0`

## License

MIT
