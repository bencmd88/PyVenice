"""
Image generation, styles, and upscaling endpoints for Venice.ai API.
"""

import base64
from typing import Optional, List, Dict, Any, Union, Literal, BinaryIO
from pathlib import Path
from pydantic import BaseModel, Field, field_validator, model_validator

from .client import BaseResource, VeniceClient
from .models import Models


class GenerateImageRequest(BaseModel):
    """Request model for Venice image generation."""

    model: str
    prompt: str = Field(..., min_length=1, max_length=1500)

    # Optional parameters
    cfg_scale: Optional[float] = Field(
        None, gt=0, le=20, description="CFG scale parameter"
    )
    embed_exif_metadata: bool = False
    format: Literal["jpeg", "png", "webp"] = "webp"
    height: int = Field(1024, gt=0, le=1280)
    hide_watermark: bool = False
    lora_strength: Optional[int] = Field(None, ge=0, le=100)
    negative_prompt: Optional[str] = Field(None, max_length=1500)
    return_binary: bool = False
    safe_mode: bool = True
    seed: Optional[int] = Field(None, ge=-999999999, le=999999999)
    steps: int = Field(20, gt=0, le=30)
    style_preset: Optional[str] = None
    width: int = Field(1024, gt=0, le=1280)


class OpenAIImageRequest(BaseModel):
    """Request model for OpenAI-compatible image generation."""

    prompt: str = Field(..., min_length=1, max_length=1500)

    # Optional parameters
    model: str = "default"
    background: Optional[Literal["transparent", "opaque", "auto"]] = "auto"
    moderation: Literal["low", "auto"] = "auto"
    n: int = Field(1, ge=1, le=1)  # Venice only supports 1
    output_compression: Optional[int] = Field(None, ge=0, le=100)
    output_format: Literal["jpeg", "png", "webp"] = "png"
    quality: Optional[Literal["auto", "high", "medium", "low", "hd", "standard"]] = (
        "auto"
    )
    response_format: Literal["b64_json", "url"] = "b64_json"
    size: Optional[str] = "auto"
    style: Optional[Literal["vivid", "natural"]] = "natural"
    user: Optional[str] = None

    @field_validator("size")
    @classmethod
    def validate_size(cls, v):
        valid_sizes = {
            "auto",
            "256x256",
            "512x512",
            "1024x1024",
            "1536x1024",
            "1024x1536",
            "1792x1024",
            "1024x1792",
        }
        if v and v not in valid_sizes:
            raise ValueError(f"Invalid size. Must be one of: {valid_sizes}")
        return v


class UpscaleImageRequest(BaseModel):
    """Request model for image upscaling."""

    image: Union[str, bytes]  # Base64 string or binary data

    # Optional parameters
    enhance: Union[bool, Literal["true", "false"]] = False
    enhanceCreativity: float = Field(0.5, ge=0, le=1)
    enhancePrompt: Optional[str] = Field(None, max_length=1500)
    replication: float = Field(0.35, ge=0.1, le=1)
    scale: float = Field(2, ge=1, le=4)

    @model_validator(mode="after")
    def validate_enhance_with_scale(self):
        """Validate that enhance must be true when scale is 1."""
        if self.scale == 1 and not self.enhance:
            raise ValueError("enhance must be true when scale is 1")
        return self


class ImageGenerationResponse(BaseModel):
    """Response from image generation endpoints."""

    id: str
    images: List[str]  # Base64 encoded images
    request: Optional[Dict[str, Any]] = None
    timing: Optional[Dict[str, float]] = None


class OpenAIImageResponse(BaseModel):
    """OpenAI-compatible image generation response."""

    created: int
    data: List[Dict[str, str]]  # List of {"b64_json": "..." } or {"url": "..."}


class ImageGeneration(BaseResource):
    """
    Interface for Venice.ai image generation endpoints.

    Provides methods for:
    - Image generation (Venice and OpenAI compatible)
    - Style presets listing
    - Image upscaling and enhancement
    """

    def __init__(self, client: VeniceClient):
        super().__init__(client)
        self.models = Models(client)
        self._styles_cache: Optional[List[str]] = None

    def generate(
        self,
        prompt: str,
        model: str = "venice-sd35",
        *,
        negative_prompt: Optional[str] = None,
        width: int = 1024,
        height: int = 1024,
        steps: int = 20,
        cfg_scale: float = 7.5,
        seed: Optional[int] = None,
        style_preset: Optional[str] = None,
        format: Literal["jpeg", "png", "webp"] = "webp",
        safe_mode: bool = True,
        return_binary: bool = False,
        **kwargs,
    ) -> ImageGenerationResponse:
        """
        Generate an image using Venice's native API.

        Args:
            prompt: Text description of the desired image.
            model: Model to use for generation.
            negative_prompt: What should not be in the image.
            width: Image width (max 1280).
            height: Image height (max 1280).
            steps: Number of inference steps (max 30).
            cfg_scale: CFG scale parameter (0-20).
            seed: Random seed for reproducibility.
            style_preset: Style to apply (see list_styles()).
            format: Output format.
            safe_mode: Blur adult content if detected.
            return_binary: Return binary data instead of base64.
            **kwargs: Additional parameters.

        Returns:
            ImageGenerationResponse with generated images.
        """
        # Map model name if needed
        model = self.models.map_model_name(model)

        request = GenerateImageRequest(
            model=model,
            prompt=prompt,
            negative_prompt=negative_prompt,
            width=width,
            height=height,
            steps=steps,
            cfg_scale=cfg_scale,
            seed=seed,
            style_preset=style_preset,
            format=format,
            safe_mode=safe_mode,
            return_binary=return_binary,
            **kwargs,
        )

        response = self.client.post(
            "/image/generate", request.model_dump(exclude_none=True)
        )

        # Check response headers for content violations
        if hasattr(response, "headers"):
            if response.headers.get("x-venice-is-content-violation") == "true":
                print("Warning: Generated image violates content policy")
            if response.headers.get("x-venice-is-blurred") == "true":
                print("Warning: Generated image has been blurred due to adult content")

        return ImageGenerationResponse(**response)

    def generate_openai_style(
        self,
        prompt: str,
        *,
        model: str = "default",
        size: str = "1024x1024",
        quality: str = "auto",
        n: int = 1,
        response_format: Literal["b64_json", "url"] = "b64_json",
        **kwargs,
    ) -> OpenAIImageResponse:
        """
        Generate an image using OpenAI-compatible API.

        Args:
            prompt: Text description of the desired image.
            model: Model to use (defaults to Venice's default).
            size: Image size (e.g., "1024x1024").
            quality: Quality setting (ignored by Venice).
            n: Number of images (Venice only supports 1).
            response_format: Response format.
            **kwargs: Additional parameters.

        Returns:
            OpenAIImageResponse compatible with OpenAI clients.
        """
        request = OpenAIImageRequest(
            prompt=prompt,
            model=model,
            size=size,
            quality=quality,
            n=n,
            response_format=response_format,
            **kwargs,
        )

        response = self.client.post(
            "/images/generations", request.model_dump(exclude_none=True)
        )
        return OpenAIImageResponse(**response)

    async def generate_async(
        self, prompt: str, model: str = "venice-sd35", **kwargs
    ) -> ImageGenerationResponse:
        """Async version of generate()."""
        model = self.models.map_model_name(model)

        request = GenerateImageRequest(model=model, prompt=prompt, **kwargs)

        response = await self.client.post_async(
            "/image/generate", request.model_dump(exclude_none=True)
        )
        return ImageGenerationResponse(**response)

    def list_styles(self, force_refresh: bool = False) -> List[str]:
        """
        List available image style presets.

        Args:
            force_refresh: Force refresh of cached styles.

        Returns:
            List of available style names.
        """
        if not force_refresh and self._styles_cache is not None:
            return self._styles_cache

        response = self.client.get("/image/styles")
        self._styles_cache = response.get("data", [])
        return self._styles_cache

    def upscale(
        self,
        image: Union[str, bytes, Path, BinaryIO],
        *,
        scale: float = 2,
        enhance: bool = False,
        enhance_creativity: float = 0.5,
        enhance_prompt: Optional[str] = None,
        replication: float = 0.35,
    ) -> bytes:
        """
        Upscale or enhance an image.

        Args:
            image: Image to upscale (base64, bytes, file path, or file object).
            scale: Scale factor (1-4). Use 1 with enhance=True for enhancement only.
            enhance: Apply Venice's image enhancement.
            enhance_creativity: How much AI can change the image (0-1).
            enhance_prompt: Style to apply during enhancement.
            replication: Preserve lines/noise from original (0.1-1).

        Returns:
            Upscaled image as bytes.
        """
        # Convert image to base64 if needed
        if isinstance(image, Path):
            with open(image, "rb") as f:
                image = base64.b64encode(f.read()).decode()
        elif isinstance(image, BinaryIO):
            image = base64.b64encode(image.read()).decode()
        elif isinstance(image, bytes):
            image = base64.b64encode(image).decode()

        request = UpscaleImageRequest(
            image=image,
            scale=scale,
            enhance=enhance,
            enhanceCreativity=enhance_creativity,
            enhancePrompt=enhance_prompt,
            replication=replication,
        )

        # This endpoint returns binary data
        headers = {"Accept": "image/png"}
        response = self.client._request(
            "POST",
            "/image/upscale",
            data=request.model_dump(exclude_none=True),
            headers=headers,
            stream=True,
        )

        return response.content

    async def upscale_async(
        self, image: Union[str, bytes, Path, BinaryIO], **kwargs
    ) -> bytes:
        """Async version of upscale()."""
        # Convert image to base64 if needed
        if isinstance(image, Path):
            with open(image, "rb") as f:
                image = base64.b64encode(f.read()).decode()
        elif isinstance(image, BinaryIO):
            image = base64.b64encode(image.read()).decode()
        elif isinstance(image, bytes):
            image = base64.b64encode(image).decode()

        request = UpscaleImageRequest(image=image, **kwargs)

        headers = {"Accept": "image/png"}
        response = await self.client._request_async(
            "POST",
            "/image/upscale",
            data=request.model_dump(exclude_none=True),
            headers=headers,
            stream=True,
        )

        return response.content
