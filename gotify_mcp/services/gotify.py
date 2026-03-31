"""
Gotify API service layer — thin wrapper around the Gotify REST API.
All HTTP calls live here; the MCP tool handler stays thin.
"""

from __future__ import annotations

import re
import os
import logging
from typing import Any

import httpx

logger = logging.getLogger("GotifyMCPServer")


# ---------------------------------------------------------------------------
# URL normalization
# ---------------------------------------------------------------------------


def is_docker() -> bool:
    """Detect if running inside a Docker container."""
    return os.path.exists("/.dockerenv") or os.environ.get(
        "RUNNING_IN_DOCKER", ""
    ).lower() in (
        "true",
        "1",
    )


def normalize_service_url(url: str) -> str:
    """Normalize upstream Gotify URL for the deployment context.

    When running inside Docker, localhost/127.0.0.1 refer to the container
    itself — rewrite them to host.docker.internal so the container can reach
    the host-side Gotify server.
    """
    if not is_docker():
        return url
    return re.sub(
        r"https?://(localhost|127\.0\.0\.1)(:\d+)?",
        lambda m: f"http://host.docker.internal{m.group(2) or ''}",
        url,
    )


# ---------------------------------------------------------------------------
# Low-level HTTP client
# ---------------------------------------------------------------------------


class GotifyClient:
    """Async HTTP client for the Gotify REST API."""

    def __init__(
        self, base_url: str, client_token: str | None, timeout: float = 20.0
    ) -> None:
        self.base_url = normalize_service_url(base_url.rstrip("/"))
        self.client_token = client_token
        self.timeout = timeout
        logger.info("GotifyClient initialised — base_url=%s", self.base_url)

    async def request(
        self,
        method: str,
        endpoint: str,
        token: str | None = None,
        params: dict[str, Any] | None = None,
        json_data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Authenticated HTTP request to the Gotify API."""
        actual_token = token if token else self.client_token
        if not actual_token:
            msg = (
                "No token provided. For send_message pass app_token; "
                "for management actions configure GOTIFY_CLIENT_TOKEN."
            )
            logger.error(msg)
            return {
                "error": msg,
                "errorCode": 401,
                "errorDescription": "Authentication token missing.",
            }

        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = {"X-Gotify-Key": actual_token}

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.request(
                    method, url, params=params, json=json_data, headers=headers
                )
                response.raise_for_status()
                if response.status_code == 204 or not response.content:
                    return {"status": "success", "message": "Operation successful."}
                return response.json()
            except httpx.HTTPStatusError as e:
                logger.error(
                    "HTTP error %s for %s %s: %s",
                    e.response.status_code,
                    method,
                    url,
                    e.response.text,
                )
                try:
                    err = e.response.json()
                except Exception:
                    err = {"errorDescription": e.response.text}
                return {
                    "error": err.get("error", f"HTTP {e.response.status_code}"),
                    "errorCode": err.get("errorCode", e.response.status_code),
                    "errorDescription": err.get(
                        "errorDescription", "Failed to call Gotify API."
                    ),
                }
            except httpx.RequestError as e:
                logger.error("Request error for %s %s: %s", method, url, e)
                return {
                    "error": "RequestError",
                    "errorCode": 500,
                    "errorDescription": str(e),
                }

    # ------------------------------------------------------------------
    # Messages
    # ------------------------------------------------------------------

    async def send_message(
        self,
        app_token: str,
        message: str,
        title: str | None = None,
        priority: int | None = None,
        extras: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Send a push notification via an application token."""
        payload: dict[str, Any] = {"message": message}
        if title:
            payload["title"] = title
        if priority is not None:
            payload["priority"] = priority
        if extras:
            payload["extras"] = extras
        return await self.request("POST", "message", token=app_token, json_data=payload)

    async def list_messages(
        self,
        app_id: int | None = None,
        offset: int = 0,
        limit: int = 50,
        sort_by: str = "id",
        sort_order: str = "desc",
        query: str = "",
    ) -> dict[str, Any]:
        """List messages with pagination and optional app filter."""
        endpoint = f"application/{app_id}/message" if app_id else "message"
        params: dict[str, Any] = {"limit": limit}
        # Gotify uses cursor-style pagination via `since` (message id).
        # We accept offset for API consistency but map it to limit-based slicing.
        if offset:
            params["since"] = offset
        raw = await self.request("GET", endpoint, params=params)
        if "error" in raw:
            return raw
        messages: list[dict[str, Any]] = raw.get("messages", [])
        total: int = raw.get("paging", {}).get("size", len(messages))

        # Client-side filter by query string (title or message body)
        if query:
            q = query.lower()
            messages = [
                m
                for m in messages
                if q in (m.get("message") or "").lower()
                or q in (m.get("title") or "").lower()
            ]

        # Sort
        reverse = sort_order.lower() == "desc"
        try:
            messages = sorted(
                messages, key=lambda m: m.get(sort_by, 0), reverse=reverse
            )
        except (TypeError, KeyError):
            pass

        return {
            "items": messages,
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": offset + limit < total,
        }

    async def delete_message(self, message_id: int) -> dict[str, Any]:
        return await self.request("DELETE", f"message/{message_id}")

    async def delete_all_messages(self) -> dict[str, Any]:
        return await self.request("DELETE", "message")

    # ------------------------------------------------------------------
    # Applications
    # ------------------------------------------------------------------

    async def list_applications(
        self,
        offset: int = 0,
        limit: int = 50,
        query: str = "",
    ) -> dict[str, Any]:
        raw = await self.request("GET", "application")
        if "error" in raw:
            return raw
        apps: list[dict[str, Any]] = raw if isinstance(raw, list) else []
        if query:
            q = query.lower()
            apps = [a for a in apps if q in (a.get("name") or "").lower()]
        total = len(apps)
        page = apps[offset : offset + limit]
        return {
            "items": page,
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": offset + limit < total,
        }

    async def create_application(
        self,
        name: str,
        description: str | None = None,
        default_priority: int | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {"name": name}
        if description:
            payload["description"] = description
        if default_priority is not None:
            payload["defaultPriority"] = default_priority
        return await self.request("POST", "application", json_data=payload)

    async def update_application(
        self,
        app_id: int,
        name: str | None = None,
        description: str | None = None,
        default_priority: int | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {}
        if name:
            payload["name"] = name
        if description:
            payload["description"] = description
        if default_priority is not None:
            payload["defaultPriority"] = default_priority
        if not payload:
            return {
                "error": "NoUpdateFields",
                "errorCode": 400,
                "errorDescription": "No fields provided to update.",
            }
        return await self.request("PUT", f"application/{app_id}", json_data=payload)

    async def delete_application(self, app_id: int) -> dict[str, Any]:
        return await self.request("DELETE", f"application/{app_id}")

    # ------------------------------------------------------------------
    # Clients
    # ------------------------------------------------------------------

    async def list_clients(
        self,
        offset: int = 0,
        limit: int = 50,
        query: str = "",
    ) -> dict[str, Any]:
        raw = await self.request("GET", "client")
        if "error" in raw:
            return raw
        clients: list[dict[str, Any]] = raw if isinstance(raw, list) else []
        if query:
            q = query.lower()
            clients = [c for c in clients if q in (c.get("name") or "").lower()]
        total = len(clients)
        page = clients[offset : offset + limit]
        return {
            "items": page,
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": offset + limit < total,
        }

    async def create_client(self, name: str) -> dict[str, Any]:
        return await self.request("POST", "client", json_data={"name": name})

    async def delete_client(self, client_id: int) -> dict[str, Any]:
        return await self.request("DELETE", f"client/{client_id}")

    # ------------------------------------------------------------------
    # Health / version
    # ------------------------------------------------------------------

    async def get_health(self) -> dict[str, Any]:
        """Check Gotify server health (no auth required)."""
        url = f"{self.base_url}/health"
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                return {"error": str(e)}

    async def get_version(self) -> dict[str, Any]:
        """Retrieve Gotify server version (no auth required)."""
        url = f"{self.base_url}/version"
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                return {"error": str(e)}

    async def get_current_user(self) -> dict[str, Any]:
        return await self.request("GET", "current/user")
