"""Unit tests for the Billing module."""

import pytest
import httpx
import respx

from pyvenice.billing import Billing
from pyvenice.client import VeniceClient
from pyvenice.exceptions import InvalidRequestError


@pytest.mark.unit
class TestBilling:
    """Test Billing class functionality."""
    
    def test_billing_init(self, client):
        """Test Billing initialization."""
        billing = Billing(client)
        assert billing.client == client
    
    @respx.mock
    def test_get_usage_basic(self, respx_mock, client):
        """Test basic usage retrieval."""
        mock_response = {
            "data": [
                {
                    "date": "2024-01-01",
                    "total_cost": 1.50,
                    "total_tokens": 1000,
                    "vcu_used": 150
                }
            ],
            "has_more": False,
            "object": "list"
        }
        
        respx_mock.get("https://api.venice.ai/api/v1/billing/usage").mock(
            return_value=httpx.Response(200, json=mock_response)
        )
        
        billing = Billing(client)
        response = billing.get_usage()
        
        assert response["object"] == "list"
        assert len(response["data"]) == 1
        assert response["data"][0]["date"] == "2024-01-01"
        assert response["data"][0]["total_cost"] == 1.50
        assert response["has_more"] is False
    
    @respx.mock
    def test_get_usage_with_date_range(self, respx_mock, client):
        """Test usage retrieval with date range."""
        mock_response = {
            "data": [
                {
                    "date": "2024-01-01",
                    "total_cost": 1.50,
                    "total_tokens": 1000,
                    "vcu_used": 150
                },
                {
                    "date": "2024-01-02",
                    "total_cost": 2.00,
                    "total_tokens": 1500,
                    "vcu_used": 200
                }
            ],
            "has_more": False,
            "object": "list"
        }
        
        respx_mock.get("https://api.venice.ai/api/v1/billing/usage").mock(
            return_value=httpx.Response(200, json=mock_response)
        )
        
        billing = Billing(client)
        response = billing.get_usage(
            start_date="2024-01-01",
            end_date="2024-01-02"
        )
        
        # Verify request was made with correct parameters
        request = respx_mock.calls[0].request
        assert "start_date=2024-01-01" in str(request.url)
        assert "end_date=2024-01-02" in str(request.url)
        
        assert len(response["data"]) == 2
        assert response["data"][0]["date"] == "2024-01-01"
        assert response["data"][1]["date"] == "2024-01-02"
    
    @respx.mock
    def test_get_usage_with_pagination(self, respx_mock, client):
        """Test usage retrieval with pagination."""
        mock_response = {
            "data": [
                {
                    "date": "2024-01-01",
                    "total_cost": 1.50,
                    "total_tokens": 1000,
                    "vcu_used": 150
                }
            ],
            "has_more": True,
            "object": "list"
        }
        
        respx_mock.get("https://api.venice.ai/api/v1/billing/usage").mock(
            return_value=httpx.Response(200, json=mock_response)
        )
        
        billing = Billing(client)
        response = billing.get_usage(
            limit=10,
            after="some_cursor"
        )
        
        # Verify request was made with correct parameters
        request = respx_mock.calls[0].request
        assert "limit=10" in str(request.url)
        assert "after=some_cursor" in str(request.url)
        
        assert response["has_more"] is True
    
    @pytest.mark.asyncio
    @respx.mock
    async def test_get_usage_async(self, respx_mock, client):
        """Test async usage retrieval."""
        mock_response = {
            "data": [
                {
                    "date": "2024-01-01",
                    "total_cost": 1.50,
                    "total_tokens": 1000,
                    "vcu_used": 150
                }
            ],
            "has_more": False,
            "object": "list"
        }
        
        respx_mock.get("https://api.venice.ai/api/v1/billing/usage").mock(
            return_value=httpx.Response(200, json=mock_response)
        )
        
        billing = Billing(client)
        response = await billing.get_usage_async()
        
        assert response["object"] == "list"
        assert len(response["data"]) == 1


@pytest.mark.unit
class TestErrorHandling:
    """Test error handling in billing."""
    
    @respx.mock
    def test_unauthorized_error(self, respx_mock, client):
        """Test error when unauthorized."""
        error_response = {
            "error": "Unauthorized access to billing data"
        }
        respx_mock.get("https://api.venice.ai/api/v1/billing/usage").mock(
            return_value=httpx.Response(401, json=error_response)
        )
        
        billing = Billing(client)
        with pytest.raises(Exception):  # Will be AuthenticationError
            billing.get_usage()
    
    @respx.mock
    def test_invalid_date_format_error(self, respx_mock, client):
        """Test error when invalid date format."""
        error_response = {
            "error": "Invalid date format",
            "details": {"start_date": {"_errors": ["Date must be in YYYY-MM-DD format"]}}
        }
        respx_mock.get("https://api.venice.ai/api/v1/billing/usage").mock(
            return_value=httpx.Response(400, json=error_response)
        )
        
        billing = Billing(client)
        with pytest.raises(InvalidRequestError):
            billing.get_usage(start_date="invalid-date")


@pytest.mark.integration
class TestBillingIntegration:
    """Integration tests for Billing (requires API key)."""
    
    def test_real_usage_retrieval(self, skip_if_no_api_key, integration_api_key):
        """Test real usage data retrieval."""
        client = VeniceClient(api_key=integration_api_key)
        billing = Billing(client)
        
        response = billing.get_usage(limit=5)
        
        assert "object" in response
        assert "data" in response
        assert "has_more" in response
        assert isinstance(response["data"], list)
        
        # If there's data, check its structure
        if response["data"]:
            usage_item = response["data"][0]
            assert "date" in usage_item
            assert "total_cost" in usage_item or "vcu_used" in usage_item