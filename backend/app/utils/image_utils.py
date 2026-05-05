"""
AgriVision AI — Image utilities.

Responsibilities:
  - Validate uploaded image files (type, size).
  - Resize / compress images before sending to external APIs.
  - Convert between bytes, base64, and PIL Image objects.
"""

import base64
import io
from fastapi import HTTPException, UploadFile

# Maximum allowed upload size (10 MB)
MAX_IMAGE_SIZE_BYTES = 10 * 1024 * 1024
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}


async def read_and_validate_image(upload: UploadFile) -> bytes:
    """
    Read an uploaded image file, validate its content-type and size, and return
    the raw bytes.

    Raises:
        HTTPException 415 if the content type is not allowed.
        HTTPException 413 if the image exceeds MAX_IMAGE_SIZE_BYTES.
    """
    content_type = upload.content_type or ""
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=415,
            detail=(
                f"Unsupported media type '{content_type}'. "
                f"Allowed: {', '.join(sorted(ALLOWED_CONTENT_TYPES))}"
            ),
        )
    data = await upload.read()
    if len(data) > MAX_IMAGE_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"Image too large. Maximum allowed size is {MAX_IMAGE_SIZE_BYTES // (1024*1024)} MB.",
        )
    return data


def bytes_to_base64(image_bytes: bytes) -> str:
    """Encode raw image bytes as a base64 string (without data-URL prefix)."""
    return base64.b64encode(image_bytes).decode("utf-8")


def base64_to_bytes(b64_string: str) -> bytes:
    """Decode a base64 string (with or without data-URL prefix) to raw bytes."""
    if "," in b64_string:
        _, b64_string = b64_string.split(",", 1)
    return base64.b64decode(b64_string)


def resize_image(
    image_bytes: bytes,
    max_width: int = 1024,
    max_height: int = 1024,
    quality: int = 85,
) -> bytes:
    """
    Resize an image so that neither dimension exceeds the given maximum,
    preserving aspect ratio. Returns JPEG bytes.

    Falls back to returning the original bytes if Pillow is not installed.
    """
    try:
        from PIL import Image

        img = Image.open(io.BytesIO(image_bytes))
        img.thumbnail((max_width, max_height), Image.LANCZOS)
        buf = io.BytesIO()
        img.convert("RGB").save(buf, format="JPEG", quality=quality)
        return buf.getvalue()
    except ImportError:
        return image_bytes
