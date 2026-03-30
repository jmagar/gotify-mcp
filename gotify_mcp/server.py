"""
MCP Server for Gotify
Implements the approved tool set from the design phase.
Built with FastMCP following best practices from gofastmcp.com
Transport: HTTP (streamable)
"""

import os
import sys
import logging
import logging.handlers
import httpx
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv

from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse

# --- Environment Loading ---
PACKAGE_DIR = Path(__file__).resolve().parent
REPO_ROOT = PACKAGE_DIR.parent
load_dotenv(dotenv_path=REPO_ROOT / ".env")

# --- Logging Setup ---
GOTIFY_LOG_LEVEL_STR = os.getenv("GOTIFY_LOG_LEVEL", os.getenv("LOG_LEVEL", "INFO")).upper()
NUMERIC_LOG_LEVEL = getattr(logging, GOTIFY_LOG_LEVEL_STR, logging.INFO)

logger = logging.getLogger("GotifyMCPServer")
logger.setLevel(NUMERIC_LOG_LEVEL)
logger.propagate = False

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(NUMERIC_LOG_LEVEL)
console_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
    logger.addHandler(console_handler)

logs_dir = REPO_ROOT / "logs"
logs_dir.mkdir(exist_ok=True)
log_file_path = logs_dir / "gotify_mcp.log"
file_handler = logging.handlers.RotatingFileHandler(
    log_file_path, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
)
file_handler.setLevel(NUMERIC_LOG_LEVEL)
file_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(lineno)d - %(message)s")
)
if not any(isinstance(h, logging.handlers.RotatingFileHandler) for h in logger.handlers):
    logger.addHandler(file_handler)

# --- Configuration ---
GOTIFY_URL = os.getenv("GOTIFY_URL")
GOTIFY_CLIENT_TOKEN = os.getenv("GOTIFY_CLIENT_TOKEN")
GOTIFY_MCP_TRANSPORT = os.getenv("GOTIFY_MCP_TRANSPORT", "http").lower()
GOTIFY_MCP_HOST = os.getenv("GOTIFY_MCP_HOST", "0.0.0.0")
GOTIFY_MCP_PORT = int(os.getenv("GOTIFY_MCP_PORT", "9158"))

if not GOTIFY_URL:
    logger.error("GOTIFY_URL must be set in the environment.")
    sys.exit(1)
if not GOTIFY_CLIENT_TOKEN:
    logger.warning("GOTIFY_CLIENT_TOKEN is not set. Management tools will fail.")

# --- FastMCP Server ---
mcp = FastMCP(
    name="Gotify MCP Server",
    instructions="""This server provides tools to interact with a Gotify instance.
You can send messages, manage applications, clients, and retrieve information like health and version.
For sending messages, an `app_token` is required per call.
For management tasks, a `GOTIFY_CLIENT_TOKEN` must be configured in the server's environment.""",
)

# --- HTTP Client Utility ---
async def _request(
    method: str,
    endpoint: str,
    token: Optional[str] = None,
    params: Optional[Dict[str, Any]] = None,
    json_data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Make an authenticated HTTP request to the Gotify API."""
    actual_token = token if token else GOTIFY_CLIENT_TOKEN
    if not actual_token:
        msg = "No token provided. For create_message pass app_token; for others configure GOTIFY_CLIENT_TOKEN."
        logger.error(msg)
        return {"error": msg, "errorCode": 401, "errorDescription": "Authentication token missing."}

    url = f"{GOTIFY_URL.rstrip('/')}/{endpoint.lstrip('/')}"
    headers = {"X-Gotify-Key": actual_token}

    async with httpx.AsyncClient(timeout=20.0) as client:
        try:
            response = await client.request(method, url, params=params, json=json_data, headers=headers)
            response.raise_for_status()
            if response.status_code == 204 or not response.content:
                return {"status": "success", "message": "Operation successful."}
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code} for {method} {url}: {e.response.text}")
            try:
                err = e.response.json()
            except Exception:
                err = {"errorDescription": e.response.text}
            return {
                "error": err.get("error", f"HTTP {e.response.status_code}"),
                "errorCode": err.get("errorCode", e.response.status_code),
                "errorDescription": err.get("errorDescription", "Failed to call Gotify API."),
            }
        except httpx.RequestError as e:
            logger.error(f"Request error for {method} {url}: {e}")
            return {"error": "RequestError", "errorCode": 500, "errorDescription": str(e)}


# --- Tools ---

@mcp.tool()
async def create_message(
    app_token: str,
    message: str,
    title: Optional[str] = None,
    priority: Optional[int] = None,
    extras: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Send a message via a Gotify application token. app_token is required per-call."""
    payload: Dict[str, Any] = {"message": message}
    if title:
        payload["title"] = title
    if priority is not None:
        payload["priority"] = priority
    if extras:
        payload["extras"] = extras
    return await _request("POST", "message", token=app_token, json_data=payload)


@mcp.tool()
async def get_messages(limit: Optional[int] = 100, since: Optional[int] = None) -> Dict[str, Any]:
    """Retrieve messages. limit: 1-200 (default 100). since: return messages with ID less than this."""
    params: Dict[str, Any] = {}
    if limit is not None:
        params["limit"] = limit
    if since is not None:
        params["since"] = since
    return await _request("GET", "message", params=params)


@mcp.tool()
async def delete_message(message_id: int) -> Dict[str, Any]:
    """Delete a specific message by ID."""
    return await _request("DELETE", f"message/{message_id}")


@mcp.tool()
async def delete_all_messages() -> Dict[str, Any]:
    """Delete all messages across all applications."""
    return await _request("DELETE", "message")


@mcp.tool()
async def get_applications() -> Dict[str, Any]:
    """Retrieve all applications."""
    return await _request("GET", "application")


@mcp.tool()
async def create_application(
    name: str,
    description: Optional[str] = None,
    default_priority: Optional[int] = None,
) -> Dict[str, Any]:
    """Create a new application."""
    payload: Dict[str, Any] = {"name": name}
    if description:
        payload["description"] = description
    if default_priority is not None:
        payload["defaultPriority"] = default_priority
    return await _request("POST", "application", json_data=payload)


@mcp.tool()
async def update_application(
    app_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None,
    default_priority: Optional[int] = None,
) -> Dict[str, Any]:
    """Update an existing application."""
    payload: Dict[str, Any] = {}
    if name:
        payload["name"] = name
    if description:
        payload["description"] = description
    if default_priority is not None:
        payload["defaultPriority"] = default_priority
    if not payload:
        return {"error": "NoUpdateFields", "errorCode": 400, "errorDescription": "No fields provided to update."}
    return await _request("PUT", f"application/{app_id}", json_data=payload)


@mcp.tool()
async def delete_application(app_id: int) -> Dict[str, Any]:
    """Delete an application by ID."""
    return await _request("DELETE", f"application/{app_id}")


@mcp.tool()
async def get_clients() -> Dict[str, Any]:
    """Retrieve all clients."""
    return await _request("GET", "client")


@mcp.tool()
async def create_client(name: str) -> Dict[str, Any]:
    """Create a new client."""
    return await _request("POST", "client", json_data={"name": name})


@mcp.tool()
async def get_health() -> Dict[str, Any]:
    """Check Gotify server health (no auth required)."""
    url = f"{GOTIFY_URL.rstrip('/')}/health"
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}


@mcp.tool()
async def get_version() -> Dict[str, Any]:
    """Retrieve Gotify server version (no auth required)."""
    url = f"{GOTIFY_URL.rstrip('/')}/version"
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}


# --- Resources ---

@mcp.resource(uri="gotify://application/{app_id}/messages")
async def application_messages(
    app_id: int,
    limit: Optional[int] = 100,
    since_id: Optional[int] = None,
) -> Dict[str, Any]:
    """Messages for a specific application."""
    params: Dict[str, Any] = {}
    if limit is not None:
        params["limit"] = limit
    if since_id is not None:
        params["since"] = since_id
    return await _request("GET", f"application/{app_id}/message", params=params)


@mcp.resource(uri="gotify://currentuser")
async def current_user_info() -> Dict[str, Any]:
    """Current authenticated user details (via GOTIFY_CLIENT_TOKEN)."""
    return await _request("GET", "current/user")


# --- Health check for monitoring ---

@mcp.custom_route("/health", methods=["GET"])
async def mcp_server_health(request: Request) -> JSONResponse:
    """MCP server health check — also probes the Gotify backend."""
    if not GOTIFY_URL:
        return JSONResponse(
            {"status": "error", "service_accessible": False, "reason": "GOTIFY_URL not configured."},
            status_code=500,
        )
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{GOTIFY_URL.rstrip('/')}/health")
            if response.status_code == 200:
                return JSONResponse({"status": "ok", "service_accessible": True})
            return JSONResponse(
                {"status": "error", "service_accessible": False, "reason": f"HTTP {response.status_code}"},
                status_code=503,
            )
    except httpx.RequestError as e:
        return JSONResponse(
            {"status": "error", "service_accessible": False, "reason": str(e)},
            status_code=503,
        )


# --- Entry point ---

def main() -> None:
    logger.info(f"Starting Gotify MCP Server — transport: {GOTIFY_MCP_TRANSPORT}")
    if GOTIFY_MCP_TRANSPORT == "stdio":
        mcp.run()
    elif GOTIFY_MCP_TRANSPORT == "sse":
        mcp.run(transport="sse", host=GOTIFY_MCP_HOST, port=GOTIFY_MCP_PORT, path="/mcp")
    elif GOTIFY_MCP_TRANSPORT == "http":
        mcp.run(
            transport="http",
            host=GOTIFY_MCP_HOST,
            port=GOTIFY_MCP_PORT,
            path="/mcp",
            log_level=GOTIFY_LOG_LEVEL_STR.lower(),
        )
    else:
        logger.error(f"Invalid GOTIFY_MCP_TRANSPORT: '{GOTIFY_MCP_TRANSPORT}'. Defaulting to stdio.")
        mcp.run()


if __name__ == "__main__":
    main()
