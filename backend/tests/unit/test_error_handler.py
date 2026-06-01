"""Unit tests for global exception handler and error response format."""
import pytest
from unittest.mock import MagicMock

from fastapi import HTTPException, status
from starlette.responses import JSONResponse

from app.core.exceptions import ErrorResponse, global_exception_handler


@pytest.fixture
def mock_request():
    return MagicMock()


class TestErrorResponse:
    def test_serialization_with_details(self):
        body = ErrorResponse(
            error="something went wrong",
            code="TEST_001",
            details={"field": "value"},
        )
        data = body.model_dump()
        assert data["error"] == "something went wrong"
        assert data["code"] == "TEST_001"
        assert data["details"] == {"field": "value"}

    def test_serialization_without_details(self):
        body = ErrorResponse(error="fail", code="TEST_002")
        data = body.model_dump()
        assert data["details"] is None

    def test_error_response_fields_present(self):
        body = ErrorResponse(error="e", code="c")
        assert hasattr(body, "error")
        assert hasattr(body, "code")
        assert hasattr(body, "details")


class TestGlobalExceptionHandlerHTTPException:
    @pytest.mark.asyncio
    async def test_http_exception_returns_correct_status(self, mock_request):
        exc = HTTPException(status_code=404, detail="Not found")
        response = await global_exception_handler(mock_request, exc)
        assert isinstance(response, JSONResponse)
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_http_exception_returns_error_body(self, mock_request):
        exc = HTTPException(status_code=404, detail="Not found")
        response = await global_exception_handler(mock_request, exc)
        body = response.body.decode() if isinstance(response.body, bytes) else response.body
        import json
        data = json.loads(body)
        assert data["error"] == "Not found"
        assert data["code"] == "HTTP_404"
        assert data["details"] is None

    @pytest.mark.asyncio
    async def test_http_exception_401(self, mock_request):
        exc = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
        response = await global_exception_handler(mock_request, exc)
        assert response.status_code == 401


class TestGlobalExceptionHandlerGenericException:
    @pytest.mark.asyncio
    async def test_generic_exception_returns_500(self, mock_request):
        exc = RuntimeError("unexpected failure")
        response = await global_exception_handler(mock_request, exc)
        assert isinstance(response, JSONResponse)
        assert response.status_code == 500

    @pytest.mark.asyncio
    async def test_generic_exception_returns_internal_error_body(self, mock_request):
        exc = ValueError("bad value")
        response = await global_exception_handler(mock_request, exc)
        import json
        body = json.loads(response.body.decode() if isinstance(response.body, bytes) else response.body)
        assert body["error"] == "Internal server error"
        assert body["code"] == "INTERNAL_ERROR"

    @pytest.mark.asyncio
    async def test_generic_exception_does_not_leak_details(self, mock_request):
        exc = RuntimeError("sensitive internal info")
        response = await global_exception_handler(mock_request, exc)
        import json
        body = json.loads(response.body.decode() if isinstance(response.body, bytes) else response.body)
        assert "sensitive" not in body["error"]
