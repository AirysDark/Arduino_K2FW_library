from flask import Flask, request, jsonify
import requests

# ----------------------------
# Moonraker configuration
# ----------------------------

MOONRAKER_BASE = "http://localhost:7125"

MOONRAKER_UPLOAD_URL      = f"{MOONRAKER_BASE}/server/files/upload"
MOONRAKER_PRINT_START_URL = f"{MOONRAKER_BASE}/printer/print/start"

MOONRAKER_API_KEY = "50fe8a7106b44396a2b75edb6aa4cf2f"

# Moonraker "root" and subfolder
TARGET_ROOT = "gcodes"      # /home/airysdark/printer_data/gcodes
TARGET_DIR  = "SliceBeam"   # subfolder inside gcodes

HEADERS = {
    "X-Api-Key": MOONRAKER_API_KEY
}

app = Flask(__name__)


def _flag(name: str) -> bool:
    """Check octoprint-style boolean flags: 'true', '1', 'yes', 'on'."""
    v = request.form.get(name, "").strip().lower()
    return v in ("true", "1", "yes", "on")


@app.route("/api/files/local", methods=["GET", "POST"])
def api_files_local():
    # SliceBeam connectivity probe
    if request.method == "GET":
        return jsonify({"files": []}), 200

    if "file" not in request.files:
        return "No file field 'file' in request", 400

    file = request.files["file"]

    # We want: gcodes/SliceBeam/<filename>
    # So the *filename* we send to Moonraker must include the folder:
    #   "SliceBeam/..."
    moonraker_rel_path = f"{TARGET_DIR}/{file.filename}"
    want_print = _flag("print")

    print(f"[moonraker_bridge] Upload requested: {moonraker_rel_path} (print={want_print})")

    # IMPORTANT:
    #  - keep root=gcodes
    #  - DO NOT send 'path' here
    #  - put "SliceBeam/filename" into the multipart 'filename'
    params = {
        "root": TARGET_ROOT,
    }

    try:
        upload_resp = requests.post(
            MOONRAKER_UPLOAD_URL,
            params=params,
            files={
                "file": (
                    moonraker_rel_path,   # includes subfolder
                    file.stream,
                    "application/octet-stream",
                )
            },
            headers=HEADERS,
            timeout=120,
        )
    except Exception as e:
        print(f"[moonraker_bridge] ERROR talking to Moonraker during upload: {e}")
        return f"Error talking to Moonraker: {e}", 500

    if not upload_resp.ok:
        print(f"[moonraker_bridge] Upload FAILED: {upload_resp.status_code} {upload_resp.text}")
        return upload_resp.text, upload_resp.status_code

    print(f"[moonraker_bridge] Upload OK: stored under root '{TARGET_ROOT}' as '{moonraker_rel_path}'")

    # Auto-print if SliceBeam requested it
    if want_print:
        print(f"[moonraker_bridge] Auto-print requested, filename='{moonraker_rel_path}'")
        try:
            start_resp = requests.post(
                MOONRAKER_PRINT_START_URL,
                json={"filename": moonraker_rel_path},  # relative to virtual_sdcard_path (gcodes root)
                headers=HEADERS,
                timeout=30,
            )
            if not start_resp.ok:
                print(f"[moonraker_bridge] print/start → {start_resp.status_code} {start_resp.text}")
                return (
                    f"Uploaded but failed to start print: "
                    f"{start_resp.status_code} {start_resp.text}",
                    500,
                )
            else:
                print("[moonraker_bridge] print/start OK")
        except Exception as e:
            print(f"[moonraker_bridge] ERROR starting print: {e}")
            return f"Uploaded but error starting print: {e}", 500

    return upload_resp.text, upload_resp.status_code


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)