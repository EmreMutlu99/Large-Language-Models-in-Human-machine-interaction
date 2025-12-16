"""
Batch emotion detection on images using the OpenAI Vision-capable model.

- Reads images from ./images or ./tests/images
- Loads OPENAI_API_KEY from environment, .env, or interactive prompt
- Calls the OpenAI Responses API once per image
- Prints a per-file summary and raw JSON list

Outputs (per image):
{
  "filename": "<name>",
  "emotion_label": "<happy|sad|angry|surprised|fearful|disgusted|neutral|uncertain|unparsed>",
  "confidence": <0..1 float | optional>,
  "rationale": "<short visual cues or raw text>"
}
"""

import base64
import json
import os
from dataclasses import dataclass
from pathlib import Path
from getpass import getpass
from typing import Any

from openai import OpenAI


@dataclass(frozen=True)
class AppConfig:
    """Application configuration constants."""

    model_name: str = "gpt-5-mini"
    max_output_tokens: int = 300
    allowed_suffixes: frozenset[str] = frozenset({".png", ".jpg", ".jpeg", ".webp"})
    image_dir_candidates: tuple[Path, ...] = (
        Path("images"),
        Path("tests") / "images",
        Path.cwd() / "tests" / "images",
    )
    emotion_guidelines: str = (
        "Identify the dominant visible emotion of the person in the photo. "
        "Pick one label from ['happy','sad','angry','surprised','fearful','disgusted','neutral']. "
        "If you cannot tell, use 'uncertain'. Respond ONLY with JSON in the form "
        '{"emotion_label": <label>, "confidence": <0-1 float>, "rationale": <visual cues>}'
    )


def encode_image_bytes(path: Path) -> str:
    """Return base64-encoded file contents."""

    return base64.b64encode(path.read_bytes()).decode("utf-8")


def load_api_key_from_env_file() -> str | None:
    """Search for OPENAI_API_KEY inside .env-style files."""

    env_paths = (
        Path(".env"),
        Path("..") / ".env",
        Path("tests") / ".env",
        Path.cwd() / ".env",
        Path.cwd().parent / ".env",
    )
    for env_path in env_paths:
        if not env_path.exists():
            continue
        for raw_line in env_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("export "):
                line = line.split(" ", 1)[1].strip()
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            if key.strip() == "OPENAI_API_KEY":
                return value.strip().strip('"').strip("'")
    return None


def resolve_image_dir(config: AppConfig) -> Path:
    """Return the first existing directory containing test images."""

    image_dir = next((p for p in config.image_dir_candidates if p.exists()), None)
    if image_dir is None:
        raise FileNotFoundError(
            "Could not locate the images folder (expected at ./images or ./tests/images)."
        )
    return image_dir


def resolve_api_key() -> str:
    """Find an API key from env/.env or fallback to getpass."""

    api_key = os.environ.get("OPENAI_API_KEY") or load_api_key_from_env_file()
    if api_key:
        return api_key
    api_key = getpass("Enter OPENAI_API_KEY: ").strip()
    if not api_key:
        raise RuntimeError("An OpenAI API key is required to run this script.")
    return api_key


def build_data_url(image_path: Path) -> str:
    """Build a data URL for an image file."""

    suffix = image_path.suffix.lstrip(".").lower()
    payload = encode_image_bytes(image_path)
    return f"data:image/{suffix};base64,{payload}"


def safe_parse_model_json(output_text: str) -> dict[str, Any]:
    """Return parsed JSON or an 'unparsed' fallback."""

    try:
        parsed = json.loads(output_text)
        if isinstance(parsed, dict):
            return parsed
        return {"emotion_label": "unparsed", "rationale": output_text}
    except json.JSONDecodeError:
        return {"emotion_label": "unparsed", "rationale": output_text}


def detect_emotion_for_image(
    client: OpenAI, config: AppConfig, image_path: Path
) -> dict[str, Any]:
    """Call the model for a single image and return the parsed response."""

    data_url = build_data_url(image_path)
    response = client.responses.create(
        model=config.model_name,
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": f"{config.emotion_guidelines} File name: {image_path.name}",
                    },
                    {"type": "input_image", "image_url": data_url},
                ],
            }
        ],
        max_output_tokens=config.max_output_tokens,
    )
    output_text = getattr(response, "output_text", None)
    if output_text is None:
        output_text = json.dumps(response.model_dump(), ensure_ascii=False)
    parsed = safe_parse_model_json(output_text)
    parsed["filename"] = image_path.name
    return parsed


def list_images(config: AppConfig, image_dir: Path) -> list[Path]:
    """Return sorted list of supported image files."""

    images = [
        p
        for p in image_dir.iterdir()
        if p.is_file() and p.suffix.lower() in config.allowed_suffixes
    ]
    return sorted(images, key=lambda p: p.name)


def print_summary(results: list[dict[str, Any]]) -> None:
    """Print per-file emotion summaries."""

    print("Detected emotions:")
    for entry in results:
        filename = entry.get("filename", "<unknown>")
        emotion = entry.get("emotion_label", "unknown")
        conf = entry.get("confidence")
        conf_txt = ""
        if conf is not None:
            try:
                conf_txt = f" (confidence={float(conf):.2f})"
            except (TypeError, ValueError):
                conf_txt = f" (confidence={conf})"
        rationale = entry.get("rationale") or entry.get("raw_response", "")
        print(f"- {filename}: {emotion}{conf_txt} -> {rationale}")


def main() -> None:
    """Program entry point."""

    config = AppConfig()
    image_dir = resolve_image_dir(config)
    api_key = resolve_api_key()
    client = OpenAI(api_key=api_key)
    images = list_images(config, image_dir)

    results: list[dict[str, Any]] = []
    for image_path in images:
        results.append(detect_emotion_for_image(client, config, image_path))

    print_summary(results)
    print("Raw JSON response:")
    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
