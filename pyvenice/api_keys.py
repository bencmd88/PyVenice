"""
API keys management endpoints for Venice.ai API.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

from .client import BaseResource


class APIKeyInfo(BaseModel):
    """API key information."""

    key: str
    name: Optional[str] = None
    created: datetime
    last_used: Optional[datetime] = None
    permissions: List[str] = Field(default_factory=list)


class RateLimit(BaseModel):
    """Rate limit information."""

    limit: int
    remaining: int
    reset: datetime
    window: str


class RateLimitLog(BaseModel):
    """Rate limit log entry."""

    timestamp: datetime
    endpoint: str
    status_code: int
    tokens_used: Optional[int] = None
    rate_limit_hit: bool = False


class Web3KeyResponse(BaseModel):
    """Response from web3 key generation."""

    key: str
    address: str
    message: str


class APIKeys(BaseResource):
    """
    Interface for Venice.ai API key management endpoints.

    Provides methods to:
    - Get API key information
    - Check rate limits
    - View rate limit logs
    - Generate web3 keys
    """

    def get_info(self) -> Dict[str, Any]:
        """
        Get information about the current API key.

        Returns:
            Dictionary containing API key information.
        """
        return self.client.get("/api_keys")

    async def get_info_async(self) -> Dict[str, Any]:
        """Async version of get_info()."""
        return await self.client.get_async("/api_keys")

    def get_rate_limits(self) -> Dict[str, Any]:
        """
        Get current rate limit status.

        Returns:
            Dictionary containing rate limit information for different endpoints.
        """
        return self.client.get("/api_keys/rate_limits")

    async def get_rate_limits_async(self) -> Dict[str, Any]:
        """Async version of get_rate_limits()."""
        return await self.client.get_async("/api_keys/rate_limits")

    def get_rate_limit_log(
        self,
        limit: int = 100,
        offset: int = 0,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Get rate limit log entries.

        Args:
            limit: Maximum number of entries to return.
            offset: Number of entries to skip.
            start_date: Filter logs after this date.
            end_date: Filter logs before this date.

        Returns:
            Dictionary containing log entries and metadata.
        """
        params = {
            "limit": limit,
            "offset": offset,
        }

        if start_date:
            params["start_date"] = start_date.isoformat()
        if end_date:
            params["end_date"] = end_date.isoformat()

        return self.client.get("/api_keys/rate_limits/log", params=params)

    async def get_rate_limit_log_async(
        self,
        limit: int = 100,
        offset: int = 0,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Async version of get_rate_limit_log()."""
        params = {
            "limit": limit,
            "offset": offset,
        }

        if start_date:
            params["start_date"] = start_date.isoformat()
        if end_date:
            params["end_date"] = end_date.isoformat()

        return await self.client.get_async("/api_keys/rate_limits/log", params=params)

    def generate_web3_key(
        self,
        wallet_address: str,
        signature: str,
        message: str,
    ) -> Web3KeyResponse:
        """
        Generate a web3 API key.

        Args:
            wallet_address: Ethereum wallet address.
            signature: Signed message from the wallet.
            message: The message that was signed.

        Returns:
            Web3KeyResponse containing the generated key.
        """
        payload = {
            "wallet_address": wallet_address,
            "signature": signature,
            "message": message,
        }

        response = self.client.post("/api_keys/generate_web3_key", payload)
        return Web3KeyResponse(**response)

    async def generate_web3_key_async(
        self,
        wallet_address: str,
        signature: str,
        message: str,
    ) -> Web3KeyResponse:
        """Async version of generate_web3_key()."""
        payload = {
            "wallet_address": wallet_address,
            "signature": signature,
            "message": message,
        }

        response = await self.client.post_async("/api_keys/generate_web3_key", payload)
        return Web3KeyResponse(**response)
