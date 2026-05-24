import argparse
import sys

from .gstreamer_env import configure_gstreamer_environment, doctor_main, shell_exports


def positive_int(value):
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be greater than 0")
    return parsed


def build_parser():
    parser = argparse.ArgumentParser(
        description="Stream a local webcam over RTSP using GStreamer."
    )
    parser.add_argument(
        "--address",
        default="0.0.0.0",
        help="Address to bind the RTSP server to. Use 127.0.0.1 for local-only.",
    )
    parser.add_argument("--port", type=positive_int, default=8854, help="RTSP server port.")
    parser.add_argument(
        "--mount-point",
        default="/webcam1",
        help="RTSP mount path, for example /webcam1 or /camera/front.",
    )
    parser.add_argument(
        "--device",
        help=(
            "Camera selector. Linux expects a device path like /dev/video0; "
            "macOS and Windows expect a numeric device index."
        ),
    )
    parser.add_argument(
        "--source",
        help=(
            "Full GStreamer source element to use instead of the platform default, "
            'for example: "autovideosrc" or "dshowvideosrc device-name=Camera".'
        ),
    )
    parser.add_argument("--width", type=positive_int, default=640, help="Output video width.")
    parser.add_argument("--height", type=positive_int, default=480, help="Output video height.")
    parser.add_argument(
        "--framerate",
        type=positive_int,
        default=30,
        help="Output video framerate in frames per second.",
    )
    parser.add_argument(
        "--bitrate",
        type=positive_int,
        default=500,
        help="H.264 bitrate in kbit/s.",
    )
    parser.add_argument(
        "--doctor",
        action="store_true",
        help="Check GStreamer, PyGObject, and native library setup without starting a stream.",
    )
    parser.add_argument(
        "--print-env",
        action="store_true",
        help="Print detected shell exports for GStreamer and exit.",
    )
    return parser


def main():
    args = build_parser().parse_args()

    if args.print_env:
        for line in shell_exports():
            print(line)
        return

    if args.doctor:
        sys.exit(doctor_main())

    configure_gstreamer_environment()

    try:
        from .streamer import WebcamRTSPServer
    except ModuleNotFoundError as exc:
        if exc.name != "gi":
            raise
        print("Missing Python module: gi")
        print("PyGObject is a native dependency and is not installed for this Python.")
        print("Run: webcam2rtsp-doctor")
        print("Then follow the suggested install steps for your platform.")
        sys.exit(1)

    server = WebcamRTSPServer(
        address=args.address,
        port=args.port,
        mount_point=args.mount_point,
        device=args.device,
        source=args.source,
        width=args.width,
        height=args.height,
        framerate=args.framerate,
        bitrate=args.bitrate,
    )
    server.run()


def doctor():
    sys.exit(doctor_main())


if __name__ == "__main__":
    main()
