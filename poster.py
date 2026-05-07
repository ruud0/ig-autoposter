"""Publish Reels to Instagram via the Graph API."""

import time
import threading
import http.server
from pathlib import Path

import httpx

from config import IG_ACCESS_TOKEN, IG_USER_ID, GRAPH_API_BASE, NGROK_AUTH_TOKEN


class _FileServer:
    """Temporary HTTP server to serve a single video file."""

    def __init__(self, file_path: Path, port: int = 9876):
        self.file_path = file_path
        self.port = port
        self._server = None
        self._thread = None

    def start(self):
        parent = str(self.file_path.parent)

        handler = http.server.SimpleHTTPRequestHandler
        handler.directory = parent

        self._server = http.server.HTTPServer(("0.0.0.0", self.port), handler)
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()

    def stop(self):
        if self._server:
            self._server.shutdown()


def _get_public_url(file_path: Path, port: int = 9876) -> tuple[str, _FileServer, object]:
    """
    Start a local file server and tunnel it via ngrok to get a public URL.

    Returns (public_url, file_server, ngrok_tunnel).
    """
    server = _FileServer(file_path, port)
    server.start()

    from pyngrok import ngrok, conf

    if NGROK_AUTH_TOKEN:
        conf.get_default().auth_token = NGROK_AUTH_TOKEN

    tunnel = ngrok.connect(port, "http")
    public_url = tunnel.public_url
    if public_url.startswith("http://"):
        public_url = public_url.replace("http://", "https://", 1)

    video_url = f"{public_url}/{file_path.name}"
    return video_url, server, tunnel


def publish_reel(video_path: str | Path, caption: str) -> dict:
    """
    Upload and publish a Reel to Instagram.

    Returns the API response with the published media ID.
    """
    video_path = Path(video_path)
    if not video_path.exists():
        raise FileNotFoundError(f"Video not found: {video_path}")

    if not IG_ACCESS_TOKEN or not IG_USER_ID:
        raise ValueError(
            "IG_ACCESS_TOKEN and IG_USER_ID must be set in .env. "
            "See README for setup instructions."
        )

    video_url, server, tunnel = _get_public_url(video_path)

    try:
        with httpx.Client(timeout=120) as client:
            # Step 1: Create media container
            create_resp = client.post(
                f"{GRAPH_API_BASE}/{IG_USER_ID}/media",
                params={
                    "media_type": "REELS",
                    "video_url": video_url,
                    "caption": caption,
                    "access_token": IG_ACCESS_TOKEN,
                },
            )
            create_resp.raise_for_status()
            container_id = create_resp.json()["id"]
            print(f"Container created: {container_id}")

            # Step 2: Wait for processing
            for attempt in range(30):
                status_resp = client.get(
                    f"{GRAPH_API_BASE}/{container_id}",
                    params={
                        "fields": "status_code,status",
                        "access_token": IG_ACCESS_TOKEN,
                    },
                )
                status_resp.raise_for_status()
                status = status_resp.json()
                code = status.get("status_code", "")

                if code == "FINISHED":
                    print("Video processed.")
                    break
                elif code == "ERROR":
                    raise RuntimeError(f"Container processing failed: {status}")
                else:
                    print(f"Processing... ({code or 'IN_PROGRESS'}) [{attempt + 1}/30]")
                    time.sleep(10)
            else:
                raise TimeoutError("Video processing timed out after 5 minutes.")

            # Step 3: Publish
            publish_resp = client.post(
                f"{GRAPH_API_BASE}/{IG_USER_ID}/media_publish",
                params={
                    "creation_id": container_id,
                    "access_token": IG_ACCESS_TOKEN,
                },
            )
            publish_resp.raise_for_status()
            result = publish_resp.json()
            print(f"Published! Media ID: {result.get('id')}")
            return result

    finally:
        from pyngrok import ngrok
        ngrok.disconnect(tunnel.public_url)
        server.stop()


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python poster.py <video_path> [caption]")
        sys.exit(1)
    video = sys.argv[1]
    cap = sys.argv[2] if len(sys.argv) > 2 else "new heat"
    result = publish_reel(video, cap)
    print(result)
