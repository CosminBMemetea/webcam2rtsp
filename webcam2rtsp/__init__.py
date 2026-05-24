__version__ = "0.1.0"
__all__ = ["WebcamRTSPServer"]


def __getattr__(name):
    if name == "WebcamRTSPServer":
        from .streamer import WebcamRTSPServer

        return WebcamRTSPServer
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
