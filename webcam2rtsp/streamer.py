import platform
import gi

gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GstRtspServer, GLib


def _quote_gst_value(value):
    escaped = str(value).replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


class WebcamRTSPServer:
    def __init__(
        self,
        address="0.0.0.0",
        port=8854,
        mount_point="/webcam1",
        device=None,
        source=None,
        width=640,
        height=480,
        framerate=30,
        bitrate=500,
    ):
        Gst.init(None)

        self.address = address
        self.port = str(port)
        self.mount_point = self._normalize_mount_point(mount_point)
        self.device = device
        self.source = source
        self.width = width
        self.height = height
        self.framerate = framerate
        self.bitrate = bitrate

        self.server = GstRtspServer.RTSPServer()
        self.server.set_address(self.address)
        self.server.set_service(self.port)

        factory = GstRtspServer.RTSPMediaFactory()
        factory.set_launch(self._get_pipeline())
        factory.set_shared(True)

        self.server.get_mount_points().add_factory(self.mount_point, factory)
        self.server.attach(None)

        client_host = "<this-computer-ip>" if self.address in ("0.0.0.0", "::") else self.address
        print(f"[ok] RTSP stream at rtsp://{client_host}:{self.port}{self.mount_point}")

    @staticmethod
    def _normalize_mount_point(mount_point):
        if not mount_point:
            raise ValueError("mount_point cannot be empty")
        if not mount_point.startswith("/"):
            return f"/{mount_point}"
        return mount_point

    def _get_pipeline(self):
        source = self.source or self._get_default_source()

        pipeline = (
            f"{source} ! "
            f"video/x-raw,width={self.width},height={self.height},framerate={self.framerate}/1 ! "
            "videoconvert ! "
            f"x264enc tune=zerolatency bitrate={self.bitrate} speed-preset=superfast ! "
            "rtph264pay config-interval=1 name=pay0 pt=96"
        )
        print(f"[i] GStreamer pipeline:\n    {pipeline}")
        return pipeline

    def _get_default_source(self):
        os_name = platform.system().lower()

        if os_name == "darwin":
            device_index = 0 if self.device is None else int(self.device)
            return f"avfvideosrc device-index={device_index}"

        if os_name == "linux":
            device = self.device or "/dev/video0"
            return f"v4l2src device={_quote_gst_value(device)}"

        if os_name == "windows":
            device_index = 0 if self.device is None else int(self.device)
            return f"mfvideosrc device-index={device_index}"

        raise RuntimeError(
            f"Unsupported OS: {os_name}. Pass --source with a GStreamer video source element."
        )

    def run(self):
        loop = GLib.MainLoop()
        try:
            loop.run()
        except KeyboardInterrupt:
            print("[stopped] RTSP server stopped.")
