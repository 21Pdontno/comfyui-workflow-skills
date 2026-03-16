#!/usr/bin/env python3
"""
ComfyUI Workflow Master - API Client
Python functions to interact with ComfyUI REST API.
"""

import urllib.request
import urllib.error
import urllib.parse
import json
import time
import os
import sys
from pathlib import Path
from typing import Optional

class ComfyUIClient:
    """Client for ComfyUI REST API."""

    def __init__(self, base_url="http://127.0.0.1:8188", timeout=300):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._prompt_id = None

    def _get(self, endpoint):
        url = f"{self.base_url}{endpoint}"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def _post(self, endpoint, data):
        url = f"{self.base_url}{endpoint}"
        body = json.dumps(data).encode("utf-8")
        req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            b = e.read().decode("utf-8", errors="replace")
            raise Exception(f"POST {url} failed ({e.code}): {b}") from e

    def _upload(self, endpoint, image_path, subfolder="", image_type="input"):
        url = f"{self.base_url}{endpoint}"
        filename = os.path.basename(image_path)
        mime_types = {".png":"image/png",".jpg":"image/jpeg",".jpeg":"image/jpeg",".webp":"image/webp"}
        ext = os.path.splitext(filename)[1].lower()
        mime = mime_types.get(ext, "application/octet-stream")
        boundary = "----ComfyUIBoundary7MA4YWxkTrZu0gW"
        with open(image_path, "rb") as f:
            file_data = f.read()
        body = (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="image"; filename="{filename}"\r\n'
            f"Content-Type: {mime}\r\n\r\n"
        ).encode("utf-8") + file_data + f"\r\n--{boundary}\r\n".encode("utf-8")
        body += (
            f'Content-Disposition: form-data; name="subfolder"\r\n\r\n{subfolder}\r\n'
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="type"\r\n\r\n{image_type}\r\n'
            f"--{boundary}--\r\n"
        ).encode("utf-8")
        req = urllib.request.Request(url, data=body, headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8"))

    # ─── System Info ────────────────────────────────────────────────

    def health_check(self):
        try:
            self._get("/system_stats")
            return True
        except:
            return False

    def get_system_stats(self):
        return self._get("/system_stats")

    def get_node_info(self):
        return self._get("/object_info")

    def get_models(self, folder):
        return self._get(f"/models/{folder}")

    def get_available_models_summary(self):
        folders = ["checkpoints","diffusion_models","loras","vae","text_encoders","controlnet","clip_vision","style_models","upscale_models"]
        summary = {}
        for f in folders:
            try:
                models = self.get_models(f)
                summary[f] = models if isinstance(models, list) else []
            except:
                summary[f] = []
        return summary

    # ─── Workflow Execution ─────────────────────────────────────────

    def queue_prompt(self, workflow):
        result = self._post("/prompt", {"prompt": workflow})
        self._prompt_id = result.get("prompt_id")
        return result

    def get_queue(self):
        return self._get("/queue")

    def get_history(self, prompt_id=None):
        return self._get(f"/history/{prompt_id}" if prompt_id else "/history")

    def interrupt(self):
        self._post("/interrupt", {})

    def clear_queue(self):
        try:
            self.interrupt()
        except:
            pass
        time.sleep(0.5)
        try:
            queue = self.get_queue()
            for item in queue.get("queue_pending", []):
                try:
                    self._post("/queue", {"delete": [item[1]]})
                except:
                    pass
        except:
            pass

    # ─── Image/File ─────────────────────────────────────────────────

    def upload_image(self, image_path, subfolder=""):
        return self._upload("/upload/image", image_path, subfolder)

    def view_image(self, filename, subfolder="", folder_type="output"):
        params = urllib.parse.urlencode({"filename":filename,"subfolder":subfolder,"type":folder_type})
        url = f"{self.base_url}/view?{params}"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.read()

    def save_image(self, filename, save_path, subfolder="", folder_type="output"):
        data = self.view_image(filename, subfolder, folder_type)
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        with open(save_path, "wb") as f:
            f.write(data)
        return save_path

    # ─── Execution Monitoring ───────────────────────────────────────

    def wait_for_completion(self, prompt_id=None, poll_interval=1.0, timeout=None):
        pid = prompt_id or self._prompt_id
        if not pid:
            raise ValueError("No prompt_id")
        start = time.time()
        while True:
            if timeout and (time.time() - start) > timeout:
                return {"status": "timeout", "outputs": {}, "errors": ["Execution timed out"]}
            history = self.get_history(pid)
            if pid in history:
                item = history[pid]
                status_info = item.get("status", {})
                outputs = item.get("outputs", {})
                if status_info.get("status_str") == "error":
                    errors = []
                    for msgs in status_info.get("messages", []):
                        for m in (msgs if isinstance(msgs, list) else []):
                            if len(m) >= 2:
                                errors.append(f"Node {m[0]}: {m[1]}")
                    return {"status": "error", "outputs": outputs, "errors": errors}
                if outputs or status_info.get("completed", False):
                    return {"status": "success", "outputs": outputs, "errors": []}
            time.sleep(poll_interval)

    def execute_workflow(self, workflow, timeout=None):
        result = self.queue_prompt(workflow)
        pid = result.get("prompt_id")
        node_errors = result.get("node_errors", {})
        if node_errors:
            errors = [f"Node {nid}: {err}" for nid, err in node_errors.items() if err]
            if errors:
                return {"status": "error", "outputs": {}, "errors": errors, "prompt_id": pid}
        completion = self.wait_for_completion(pid, timeout=timeout or self.timeout)
        completion["prompt_id"] = pid
        return completion

    def validate_workflow(self, workflow):
        try:
            result = self._post("/prompt", {"prompt": workflow, "check": True})
            if result.get("node_errors"):
                errors = [f"Node {nid}: {err}" for nid, err in result["node_errors"].items() if err]
                return {"valid": False, "error": "; ".join(errors)}
            return {"valid": True, "error": None}
        except Exception as e:
            return {"valid": False, "error": str(e)}

    def extract_output_images(self, result):
        images = []
        for node_id, output in result.get("outputs", {}).items():
            if "images" in output:
                images.append({"node_id": node_id, "images": output["images"]})
        return images

    def download_all_outputs(self, result, save_dir):
        saved = []
        for entry in self.extract_output_images(result):
            for img in entry["images"]:
                save_path = os.path.join(save_dir, img["filename"])
                self.save_image(img["filename"], save_path, img.get("subfolder", ""))
                saved.append(save_path)
        return saved


_client = None

def connect(base_url="http://127.0.0.1:8188"):
    global _client
    _client = ComfyUIClient(base_url)
    if not _client.health_check():
        raise ConnectionError(f"Cannot connect to ComfyUI at {base_url}")
    return _client

def get_client():
    global _client
    if _client is None:
        return connect()
    return _client

if __name__ == "__main__":
    c = connect()
    stats = c.get_system_stats()
    print(f"ComfyUI v{stats['system']['comfyui_version']} connected!")
    for f, items in c.get_available_models_summary().items():
        if items:
            print(f"  {f}: {len(items)} models")
