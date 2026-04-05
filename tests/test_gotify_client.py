"""Unit tests for GotifyClient service layer.

All HTTP calls are mocked with unittest.mock — no network required.
"""

from __future__ import annotations

import json
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from gotify_mcp.services.gotify import GotifyClient, normalize_service_url

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_response(
    status_code: int = 200,
    body: Any = None,
    content: bytes | None = None,
) -> MagicMock:
    """Build a mock httpx.Response."""
    resp = MagicMock()
    resp.status_code = status_code
    resp.content = content if content is not None else json.dumps(body or {}).encode()
    resp.json = MagicMock(return_value=body or {})
    resp.text = json.dumps(body or {})

    if status_code >= 400:
        import httpx

        resp.raise_for_status = MagicMock(
            side_effect=httpx.HTTPStatusError(
                f"HTTP {status_code}",
                request=MagicMock(),
                response=resp,
            )
        )
    else:
        resp.raise_for_status = MagicMock(return_value=None)

    return resp


def _client(
    base_url: str = "http://gotify.test", client_token: str | None = "test-token"
) -> GotifyClient:
    return GotifyClient(base_url=base_url, client_token=client_token)


# ---------------------------------------------------------------------------
# normalize_service_url
# ---------------------------------------------------------------------------


class TestNormalizeServiceUrl:
    def test_non_docker_returns_url_unchanged(self) -> None:
        with patch("gotify_mcp.services.gotify.is_docker", return_value=False):
            result = normalize_service_url("http://localhost:8080")
        assert result == "http://localhost:8080"

    def test_docker_rewrites_localhost(self) -> None:
        with patch("gotify_mcp.services.gotify.is_docker", return_value=True):
            result = normalize_service_url("http://localhost:8080")
        assert "host.docker.internal" in result
        assert "8080" in result

    def test_docker_rewrites_127_0_0_1(self) -> None:
        with patch("gotify_mcp.services.gotify.is_docker", return_value=True):
            result = normalize_service_url("http://127.0.0.1:9000")
        assert "host.docker.internal" in result

    def test_docker_leaves_external_url_unchanged(self) -> None:
        with patch("gotify_mcp.services.gotify.is_docker", return_value=True):
            result = normalize_service_url("http://gotify.example.com")
        assert result == "http://gotify.example.com"


# ---------------------------------------------------------------------------
# GotifyClient.request — token handling
# ---------------------------------------------------------------------------


class TestGotifyClientRequest:
    @pytest.mark.asyncio
    async def test_returns_error_when_no_token(self) -> None:
        client = _client(client_token=None)
        result = await client.request("GET", "application", token=None)
        assert "error" in result
        assert result.get("errorCode") == 401

    @pytest.mark.asyncio
    async def test_uses_explicit_token_over_client_token(self) -> None:
        client = _client(client_token="default-token")
        resp = _make_response(200, {"ok": True})
        mock_http = AsyncMock()
        mock_http.__aenter__ = AsyncMock(return_value=mock_http)
        mock_http.__aexit__ = AsyncMock(return_value=None)
        mock_http.request = AsyncMock(return_value=resp)

        with patch("gotify_mcp.services.gotify.httpx.AsyncClient", return_value=mock_http):
            await client.request("GET", "application", token="explicit-token")

        call_kwargs = mock_http.request.call_args
        assert call_kwargs.kwargs["headers"]["X-Gotify-Key"] == "explicit-token"

    @pytest.mark.asyncio
    async def test_http_status_error_returns_error_dict(self) -> None:
        client = _client()
        error_body = {"error": "Forbidden", "errorCode": 403, "errorDescription": "No access"}
        resp = _make_response(403, error_body)
        mock_http = AsyncMock()
        mock_http.__aenter__ = AsyncMock(return_value=mock_http)
        mock_http.__aexit__ = AsyncMock(return_value=None)
        mock_http.request = AsyncMock(return_value=resp)

        with patch("gotify_mcp.services.gotify.httpx.AsyncClient", return_value=mock_http):
            result = await client.request("GET", "application")

        assert "error" in result
        assert result["errorCode"] == 403

    @pytest.mark.asyncio
    async def test_204_no_content_returns_success(self) -> None:
        client = _client()
        resp = _make_response(204, body=None, content=b"")
        mock_http = AsyncMock()
        mock_http.__aenter__ = AsyncMock(return_value=mock_http)
        mock_http.__aexit__ = AsyncMock(return_value=None)
        mock_http.request = AsyncMock(return_value=resp)

        with patch("gotify_mcp.services.gotify.httpx.AsyncClient", return_value=mock_http):
            result = await client.request("DELETE", "message/1")

        assert result.get("status") == "success"

    @pytest.mark.asyncio
    async def test_request_error_returns_error_dict(self) -> None:
        import httpx

        client = _client()
        mock_http = AsyncMock()
        mock_http.__aenter__ = AsyncMock(return_value=mock_http)
        mock_http.__aexit__ = AsyncMock(return_value=None)
        mock_http.request = AsyncMock(side_effect=httpx.RequestError("connection refused"))

        with patch("gotify_mcp.services.gotify.httpx.AsyncClient", return_value=mock_http):
            result = await client.request("GET", "application")

        assert result.get("error") == "RequestError"
        assert result.get("errorCode") == 500


# ---------------------------------------------------------------------------
# GotifyClient.send_message
# ---------------------------------------------------------------------------


class TestSendMessage:
    @pytest.mark.asyncio
    async def test_basic_send(self) -> None:
        client = _client()
        resp = _make_response(200, {"id": 1, "message": "hello"})
        mock_http = AsyncMock()
        mock_http.__aenter__ = AsyncMock(return_value=mock_http)
        mock_http.__aexit__ = AsyncMock(return_value=None)
        mock_http.request = AsyncMock(return_value=resp)

        with patch("gotify_mcp.services.gotify.httpx.AsyncClient", return_value=mock_http):
            result = await client.send_message(app_token="apptoken", message="hello")

        assert result.get("id") == 1

    @pytest.mark.asyncio
    async def test_send_with_all_fields(self) -> None:
        client = _client()
        resp = _make_response(200, {"id": 2})
        mock_http = AsyncMock()
        mock_http.__aenter__ = AsyncMock(return_value=mock_http)
        mock_http.__aexit__ = AsyncMock(return_value=None)
        mock_http.request = AsyncMock(return_value=resp)

        with patch("gotify_mcp.services.gotify.httpx.AsyncClient", return_value=mock_http):
            result = await client.send_message(
                app_token="apptoken",
                message="body",
                title="My Title",
                priority=5,
                extras={"client::display": {"contentType": "text/plain"}},
            )

        assert "error" not in result
        call_kwargs = mock_http.request.call_args
        payload = call_kwargs.kwargs["json"]
        assert payload["title"] == "My Title"
        assert payload["priority"] == 5
        assert "extras" in payload


# ---------------------------------------------------------------------------
# GotifyClient.list_messages
# ---------------------------------------------------------------------------


class TestListMessages:
    @pytest.mark.asyncio
    async def test_returns_items_from_messages_key(self) -> None:
        client = _client()
        raw = {
            "messages": [
                {"id": 1, "message": "hello", "title": ""},
                {"id": 2, "message": "world", "title": ""},
            ],
            "paging": {"size": 2},
        }
        resp = _make_response(200, raw)
        mock_http = AsyncMock()
        mock_http.__aenter__ = AsyncMock(return_value=mock_http)
        mock_http.__aexit__ = AsyncMock(return_value=None)
        mock_http.request = AsyncMock(return_value=resp)

        with patch("gotify_mcp.services.gotify.httpx.AsyncClient", return_value=mock_http):
            result = await client.list_messages()

        assert "items" in result
        assert len(result["items"]) == 2

    @pytest.mark.asyncio
    async def test_query_filter_applied(self) -> None:
        client = _client()
        raw = {
            "messages": [
                {"id": 1, "message": "error occurred", "title": ""},
                {"id": 2, "message": "all good", "title": ""},
            ],
            "paging": {"size": 2},
        }
        resp = _make_response(200, raw)
        mock_http = AsyncMock()
        mock_http.__aenter__ = AsyncMock(return_value=mock_http)
        mock_http.__aexit__ = AsyncMock(return_value=None)
        mock_http.request = AsyncMock(return_value=resp)

        with patch("gotify_mcp.services.gotify.httpx.AsyncClient", return_value=mock_http):
            result = await client.list_messages(query="error")

        assert len(result["items"]) == 1
        assert result["items"][0]["id"] == 1

    @pytest.mark.asyncio
    async def test_uses_app_specific_endpoint_when_app_id_given(self) -> None:
        client = _client()
        resp = _make_response(200, {"messages": [], "paging": {"size": 0}})
        mock_http = AsyncMock()
        mock_http.__aenter__ = AsyncMock(return_value=mock_http)
        mock_http.__aexit__ = AsyncMock(return_value=None)
        mock_http.request = AsyncMock(return_value=resp)

        with patch("gotify_mcp.services.gotify.httpx.AsyncClient", return_value=mock_http):
            await client.list_messages(app_id=42)

        call_args = mock_http.request.call_args
        assert "application/42/message" in call_args.args[1]

    @pytest.mark.asyncio
    async def test_propagates_error_from_request(self) -> None:
        client = _client(client_token=None)
        result = await client.list_messages()
        assert "error" in result


# ---------------------------------------------------------------------------
# GotifyClient.list_applications
# ---------------------------------------------------------------------------


class TestListApplications:
    @pytest.mark.asyncio
    async def test_returns_wrapped_items(self) -> None:
        client = _client()
        raw_apps = [{"id": 1, "name": "app1"}, {"id": 2, "name": "app2"}]
        resp = _make_response(200, raw_apps)
        # The response.json() returns a list directly for /application
        resp.json = MagicMock(return_value=raw_apps)
        mock_http = AsyncMock()
        mock_http.__aenter__ = AsyncMock(return_value=mock_http)
        mock_http.__aexit__ = AsyncMock(return_value=None)
        mock_http.request = AsyncMock(return_value=resp)

        with patch("gotify_mcp.services.gotify.httpx.AsyncClient", return_value=mock_http):
            result = await client.list_applications()

        assert "items" in result
        assert len(result["items"]) == 2

    @pytest.mark.asyncio
    async def test_query_filters_by_name(self) -> None:
        client = _client()
        raw_apps = [{"id": 1, "name": "monitoring"}, {"id": 2, "name": "alerts"}]
        resp = _make_response(200, raw_apps)
        resp.json = MagicMock(return_value=raw_apps)
        mock_http = AsyncMock()
        mock_http.__aenter__ = AsyncMock(return_value=mock_http)
        mock_http.__aexit__ = AsyncMock(return_value=None)
        mock_http.request = AsyncMock(return_value=resp)

        with patch("gotify_mcp.services.gotify.httpx.AsyncClient", return_value=mock_http):
            result = await client.list_applications(query="monitor")

        assert len(result["items"]) == 1
        assert result["items"][0]["name"] == "monitoring"

    @pytest.mark.asyncio
    async def test_pagination_slices_results(self) -> None:
        client = _client()
        raw_apps = [{"id": i, "name": f"app{i}"} for i in range(10)]
        resp = _make_response(200, raw_apps)
        resp.json = MagicMock(return_value=raw_apps)
        mock_http = AsyncMock()
        mock_http.__aenter__ = AsyncMock(return_value=mock_http)
        mock_http.__aexit__ = AsyncMock(return_value=None)
        mock_http.request = AsyncMock(return_value=resp)

        with patch("gotify_mcp.services.gotify.httpx.AsyncClient", return_value=mock_http):
            result = await client.list_applications(offset=2, limit=3)

        assert len(result["items"]) == 3
        assert result["items"][0]["id"] == 2
        assert result["has_more"] is True


# ---------------------------------------------------------------------------
# GotifyClient.list_clients
# ---------------------------------------------------------------------------


class TestListClients:
    @pytest.mark.asyncio
    async def test_returns_wrapped_items(self) -> None:
        client = _client()
        raw_clients = [{"id": 1, "name": "cli1"}, {"id": 2, "name": "cli2"}]
        resp = _make_response(200, raw_clients)
        resp.json = MagicMock(return_value=raw_clients)
        mock_http = AsyncMock()
        mock_http.__aenter__ = AsyncMock(return_value=mock_http)
        mock_http.__aexit__ = AsyncMock(return_value=None)
        mock_http.request = AsyncMock(return_value=resp)

        with patch("gotify_mcp.services.gotify.httpx.AsyncClient", return_value=mock_http):
            result = await client.list_clients()

        assert "items" in result
        assert len(result["items"]) == 2


# ---------------------------------------------------------------------------
# GotifyClient.update_application — error on empty payload
# ---------------------------------------------------------------------------


class TestUpdateApplication:
    @pytest.mark.asyncio
    async def test_returns_error_when_no_fields_provided(self) -> None:
        client = _client()
        result = await client.update_application(app_id=1)
        assert "error" in result
        assert result["errorCode"] == 400


# ---------------------------------------------------------------------------
# GotifyClient.get_health / get_version — no-auth endpoints
# ---------------------------------------------------------------------------


class TestHealthAndVersion:
    @pytest.mark.asyncio
    async def test_get_health_success(self) -> None:
        client = _client()
        health_data = {"health": "green", "database": "green"}
        resp = _make_response(200, health_data)
        mock_http = AsyncMock()
        mock_http.__aenter__ = AsyncMock(return_value=mock_http)
        mock_http.__aexit__ = AsyncMock(return_value=None)
        mock_http.get = AsyncMock(return_value=resp)

        with patch("gotify_mcp.services.gotify.httpx.AsyncClient", return_value=mock_http):
            result = await client.get_health()

        assert result.get("health") == "green"

    @pytest.mark.asyncio
    async def test_get_health_returns_error_on_exception(self) -> None:
        client = _client()
        mock_http = AsyncMock()
        mock_http.__aenter__ = AsyncMock(return_value=mock_http)
        mock_http.__aexit__ = AsyncMock(return_value=None)
        mock_http.get = AsyncMock(side_effect=Exception("timeout"))

        with patch("gotify_mcp.services.gotify.httpx.AsyncClient", return_value=mock_http):
            result = await client.get_health()

        assert "error" in result

    @pytest.mark.asyncio
    async def test_get_version_success(self) -> None:
        client = _client()
        version_data = {"version": "2.4.0", "commit": "abc123", "buildDate": "2024-01-01"}
        resp = _make_response(200, version_data)
        mock_http = AsyncMock()
        mock_http.__aenter__ = AsyncMock(return_value=mock_http)
        mock_http.__aexit__ = AsyncMock(return_value=None)
        mock_http.get = AsyncMock(return_value=resp)

        with patch("gotify_mcp.services.gotify.httpx.AsyncClient", return_value=mock_http):
            result = await client.get_version()

        assert result.get("version") == "2.4.0"
