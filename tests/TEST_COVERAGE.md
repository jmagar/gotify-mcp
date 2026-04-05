# Test Coverage — `tests/test_live.sh`

## 1. Overview

`tests/test_live.sh` is the canonical **live integration test suite** for the `gotify-mcp` MCP server.
It does not use mocks or fixtures — every test makes real HTTP or subprocess calls against a running
server that in turn communicates with a real Gotify instance.

| Dimension | Detail |
|-----------|--------|
| **Service under test** | [Gotify](https://gotify.net/) — self-hosted push notification server |
| **MCP server under test** | `gotify-mcp` (Python, FastMCP, entry point `gotify-mcp-server`) |
| **Transport protocols exercised** | Streamable-HTTP (FastMCP) and stdio (via `mcporter`) |
| **Test scope** | Read-only operations only — no write, delete, or send actions are invoked |
| **Script mode** | Bash, `set -euo pipefail`, color-coded output, running totals of PASS / FAIL / SKIP |

The script tests two layers simultaneously:
1. The MCP server itself (auth enforcement, JSON-RPC protocol, tool routing)
2. The underlying Gotify API responses (structure and field presence)

---

## 2. How to Run

### Prerequisites

The following binaries must be on `PATH` before any mode will start:

| Binary | Required by |
|--------|-------------|
| `curl` | All modes |
| `jq` | All modes |
| `docker` | `docker` and `all` modes |
| `npx` | `stdio` and `all` modes |
| `uvx` | `stdio` and `all` modes |

The script checks for `curl` and `jq` at startup via `check_prereqs()` and exits with code 2 if
either is missing. Docker, npx, and uvx are checked inline at the start of their respective mode
functions.

### Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `MODE` | `all` | Test mode selector (overridden by `--mode`) |
| `GOTIFY_MCP_URL` | `http://localhost:9158` | Base URL for `http` mode |
| `GOTIFY_MCP_TOKEN` | `ci-integration-token` | Bearer token to authenticate with the MCP server |
| `GOTIFY_URL` | _(none, required)_ | Upstream Gotify server URL (docker and stdio modes) |
| `GOTIFY_APP_TOKEN` | _(none, optional)_ | Gotify application token (passed to container/stdio) |
| `GOTIFY_CLIENT_TOKEN` | _(none, optional)_ | Gotify client token for user-scoped endpoints |
| `VERBOSE` | `false` | Print raw HTTP responses and tool payloads |

### Exact Commands

```bash
# Default: docker mode then stdio mode
bash tests/test_live.sh

# Test against an already-running server
bash tests/test_live.sh --mode http \
    --url http://localhost:9158 \
    --token mytoken

# Build image, run all HTTP tests, tear down container
GOTIFY_URL=http://gotify.internal \
GOTIFY_APP_TOKEN=app-tok \
GOTIFY_CLIENT_TOKEN=client-tok \
bash tests/test_live.sh --mode docker

# Spawn via mcporter + uvx (stdio transport)
GOTIFY_URL=http://gotify.internal \
GOTIFY_APP_TOKEN=app-tok \
GOTIFY_CLIENT_TOKEN=client-tok \
bash tests/test_live.sh --mode stdio

# Verbose output (prints raw curl/tool responses)
bash tests/test_live.sh --verbose

# Help text
bash tests/test_live.sh --help
```

Flag precedence: CLI flags (`--mode`, `--url`, `--token`) always override environment variables.

---

## 3. Test Phases (HTTP Mode)

All four phases are executed by `run_http_tests()`. They run sequentially in both `http` mode and
`docker` mode (after the container is healthy). Total test count across all phases: **up to 22
assertions** (some convert to SKIP depending on token availability).

### Phase 1 — Health Endpoint (Unauthenticated)

**Purpose:** Verify the `/health` endpoint is reachable without credentials and returns the expected
status payload. This confirms the server process is running and its health route is correctly
exposed without authentication.

| # | Test label | Assertion |
|---|-----------|-----------|
| 1 | `GET /health → status=ok` | `curl -sf <BASE_URL>/health` then `jq -r '.status'` must equal the string `"ok"` |

### Phase 2 — Auth Enforcement

**Purpose:** Verify the `/mcp` endpoint enforces Bearer token authentication. Three scenarios
are tested: absent token, wrong token, and correct token.

| # | Test label | HTTP method | Auth header | Expected HTTP code | PASS condition |
|---|-----------|-------------|-------------|-------------------|---------------|
| 2 | `No token → 401` | `GET /mcp` (no body) | None | `401` | `curl -s -o /dev/null -w "%{http_code}"` returns exactly `"401"` |
| 3 | `Bad token → 401` | `GET /mcp` (no body) | `Authorization: Bearer bad-token-<PID>` | `401` | Returns exactly `"401"` |
| 4 | `Good token → not 401/403` | `POST /mcp` with initialize body | `Authorization: Bearer <TOKEN>` | Any code except `401`, `403`, `000` | Code is not in the failure set |

For test 4, the request body is a valid JSON-RPC `initialize` call:
```json
{"jsonrpc":"2.0","id":0,"method":"initialize",
 "params":{"protocolVersion":"2024-11-05","capabilities":{},
           "clientInfo":{"name":"test","version":"1"}}}
```

### Phase 3 — MCP Protocol

**Purpose:** Verify the MCP server speaks valid JSON-RPC 2.0 over the streamable-HTTP transport:
server identity is correct, and the tool registry contains the expected tools.

| # | Test label | Method | Assertion | jq path | Expected value |
|---|-----------|--------|-----------|---------|----------------|
| 5 | `initialize → serverInfo.name contains 'gotify'` | `initialize` | `assert_jq_contains` | `.result.serverInfo.name` | Contains substring `"gotify"` (case-insensitive) |
| 6 | `tools/list → gotify_help present` | `tools/list` | `grep -q "gotify_help"` on joined names | `.result.tools[].name` joined by `,` | String contains `"gotify_help"` |
| 7 | `tools/list → gotify present` | `tools/list` | `grep -qE "(^|,)gotify(,|$)"` | `.result.tools[].name` joined by `,` | String contains standalone `"gotify"` (word-boundary regex, not just substring) |

Note on test 7: the regex `(^|,)gotify(,|$)` deliberately prevents `gotify_help` from satisfying
the check — it requires a tool named exactly `gotify` with no suffix.

The `initialize` request uses protocol version `"2024-11-05"` and client info
`{"name":"test-live","version":"1"}`.

### Phase 4 — Tool Calls (Read-Only)

**Purpose:** Exercise each exposed MCP tool via `tools/call`, validate the JSON-RPC envelope is
correct (no `isError`), and assert specific structural properties on the tool's text response.

All tool calls use `call_tool()`, which:
1. Builds the JSON-RPC payload with `jq -n`
2. POSTs to `/mcp` with Bearer auth via `mcp_post()`
3. Stores the full response in `$LAST_TOOL_BODY`
4. Checks `.result.isError` — if `true`, returns without failing so the caller can inspect the body

The text payload is extracted from the response with:
```bash
jq -r '.result.content[0].text // .result.content // ""'
```
or
```bash
jq -r '.result.content[0].text // ""'
```
depending on the tool.

---

## 4. Every Tool Tested

### Tool: `gotify_help`

**Arguments:** `{}`  
**Skipped:** Never skipped — no token required, always runs.

| # | Test label | Assertion | PASS condition | FAIL condition |
|---|-----------|-----------|----------------|----------------|
| 8 | `gotify_help → non-empty response` | `help_text` variable is non-empty | Variable has length > 0 | Variable is empty or jq failed |
| 9 | `gotify_help → response contains 'gotify'` | `grep -qi "gotify"` on `help_text` | Case-insensitive substring match | String does not contain "gotify" |

**What "correct operation" means:** The tool must return a non-empty string that references "gotify"
by name (i.e., it is recognizable help text about the gotify integration, not a generic placeholder
or error message).

---

### Tool: `gotify` with `action=health`

**Arguments:** `{"action":"health"}`  
**Skipped:** Never skipped.

| # | Test label | Assertion | PASS condition | FAIL condition |
|---|-----------|-----------|----------------|----------------|
| 10 | `gotify action=health → non-empty response` | `health_tool_text` is non-empty | Variable has length > 0 | Empty string |
| 11 | `gotify action=health → valid JSON` | `jq -e '.'` exits 0 on `health_tool_text` | jq parses successfully | jq exits non-zero |

**What "correct operation" means:** The Gotify `/health` API returns
`{"health":"green","database":"green"}` (or similar). The test confirms the MCP server passes this
JSON through as-is, verifiable by parsing it as valid JSON. The script comments explicitly document
this expected shape but does not assert the specific field values — any parseable JSON satisfies the
test.

---

### Tool: `gotify` with `action=version`

**Arguments:** `{"action":"version"}`  
**Skipped:** Never skipped.

| # | Test label | Assertion | jq path | PASS condition | FAIL condition |
|---|-----------|-----------|---------|----------------|----------------|
| 12 | `gotify action=version → non-empty response` | `version_text` is non-empty | — | Length > 0 | Empty |
| 13 | `gotify action=version → .version field present` | `jq -r '.version // empty'` | `.version` | Non-empty string (printed in pass message) | Empty or null |

**What "correct operation" means:** The Gotify version API returns
`{"version":"...","commit":"...","buildDate":"..."}`. This test proves the MCP server correctly
proxied the API response and the `.version` field survived intact. The actual version string is
printed in the PASS message for human verification.

---

### Tool: `gotify` with `action=list_applications`

**Arguments:** `{"action":"list_applications"}`  
**Skipped:** Never skipped.

| # | Test label | Assertion | jq path | PASS condition | FAIL condition |
|---|-----------|-----------|---------|----------------|----------------|
| 14 | `gotify action=list_applications → non-empty response` | `apps_text` is non-empty | — | Length > 0 | Empty |
| 15 | `gotify action=list_applications → has 'items' key` | `jq -e 'has("items")'` | root object | `jq` exits 0 (key exists) | Key absent |
| 16 | `gotify action=list_applications → items is array` | `jq -r '.items \| type'` | `.items` | String equals `"array"` | Any other type string |

When test 16 passes, the item count is printed in the PASS message (e.g., `items is array (count: 3)`).

**What "correct operation" means:** The response must be a JSON object with an `items` key whose
value is a JSON array. An empty array (`[]`) is acceptable and passes — the test is structural, not
content-based. This proves the MCP server correctly maps the Gotify paginated list response.

---

### Tool: `gotify` with `action=list_messages`

**Arguments:** `{"action":"list_messages","limit":5}`  
**Note:** This is the only tool call that passes a non-trivial argument (`limit`).

| # | Test label | Assertion | jq path | PASS condition | SKIP condition | FAIL condition |
|---|-----------|-----------|---------|----------------|----------------|----------------|
| 17 | `gotify action=list_messages → non-empty response` | `msgs_text` is non-empty | — | Length > 0 | — | Empty |
| 18 | `gotify action=list_messages → has 'items' key` | `jq -e 'has("items")'` | root object | Key exists | `.error` field is non-empty → SKIP with message | Key absent and no `.error` |

**SKIP rationale:** `list_messages` requires a Gotify **client token** (`GOTIFY_CLIENT_TOKEN`). If
this env var is not set, the MCP server returns a JSON error object with an `.error` field. The
script detects this and converts the failure to a SKIP with the message
`"gotify action=list_messages → returned error (likely no client token): <error>"`.

**What "correct operation" means (when token is available):** Returns an `items` array (possibly
empty) matching the paginated messages list from Gotify. The `limit=5` argument tests that the
MCP tool correctly passes parameters to the upstream API.

---

### Tool: `gotify` with `action=list_clients`

**Arguments:** `{"action":"list_clients"}`

| # | Test label | Assertion | jq path | PASS condition | SKIP condition | FAIL condition |
|---|-----------|-----------|---------|----------------|----------------|----------------|
| 19 | `gotify action=list_clients → non-empty response` | `clients_text` is non-empty | — | Length > 0 | — | Empty |
| 20 | `gotify action=list_clients → has 'items' key` | `jq -e 'has("items")'` | root object | Key exists | `.error` field is non-empty → SKIP | Key absent and no `.error` |

**SKIP rationale:** Same as `list_messages` — requires `GOTIFY_CLIENT_TOKEN`. The skip message
reads: `"gotify action=list_clients → returned error (likely no client token): <error>"`.

**What "correct operation" means (when token is available):** Returns an `items` array of
registered Gotify clients. An empty array is acceptable.

---

### Tool: `gotify` with `action=current_user`

**Arguments:** `{"action":"current_user"}`

| # | Test label | Assertion | jq path | PASS condition | SKIP condition | FAIL condition |
|---|-----------|-----------|---------|----------------|----------------|----------------|
| 21 | `gotify action=current_user → non-empty response` | `user_text` is non-empty | — | Length > 0 | — | Empty |
| 22 | `gotify action=current_user → user id present` | `jq -e 'has("id")'` exits 0 | `.id` | Key present; `.name` printed in PASS message | `.error` field non-empty → SKIP | `.id` absent and no `.error` |

**SKIP rationale:** Same client-token dependency. Skip message:
`"gotify action=current_user → returned error (likely no client token): <error>"`.

**What "correct operation" means (when token is available):** The Gotify user object has shape
`{"id":<int>,"name":"<string>","admin":<bool>}`. The test confirms the `id` field survived the
MCP round-trip. The username is printed in the PASS message for human verification.

---

## 5. Skipped Operations and Why

The following Gotify API operations are **never tested** by this script:

| Operation | Reason omitted |
|-----------|---------------|
| `send_message` / `create_message` | Write operation — would create real notifications |
| `delete_message` | Destructive — would permanently delete data |
| `create_application` | Write — would create a persistent app record |
| `update_application` | Write |
| `delete_application` | Destructive |
| `create_client` | Write |
| `delete_client` | Destructive |
| `create_user` | Write (admin) |
| `delete_user` | Destructive (admin) |
| `list_users` | Not tested (script focuses on common user-facing ops) |
| `delete_all_messages` | Extremely destructive — blanket exclusion |
| `list_plugins` | Not tested |

All skips are by design. The script header comments: _"read-only operations only"_. The SKIP
mechanism used in the script itself (`skip()` function) is reserved only for conditional skips due
to missing optional credentials (`GOTIFY_CLIENT_TOKEN`), not for intentionally omitted operations.

---

## 6. What "Proving Correct Operation" Means Per Tool

This table summarizes the minimum evidence required for a tool to be considered correctly operating.
"Structural correctness" means the MCP envelope and data shape are valid; "semantic correctness"
means the field values are meaningful.

| Tool + Action | Structural | Semantic |
|--------------|------------|---------|
| `gotify_help {}` | Non-empty string in `content[0].text` | String contains the word "gotify" |
| `gotify health` | `content[0].text` is parseable JSON | Any valid JSON (implicitly `{"health":...}`) |
| `gotify version` | `content[0].text` contains `.version` key | `.version` is non-empty string |
| `gotify list_applications` | `content[0].text` has `.items` key of type `array` | — (count logged, not asserted) |
| `gotify list_messages` | `content[0].text` has `.items` key | — |
| `gotify list_clients` | `content[0].text` has `.items` key | — |
| `gotify current_user` | `content[0].text` has `.id` key | `.name` logged but not asserted |

---

## 7. Authentication Tests

Phase 2 comprehensively covers authentication enforcement on `/mcp`:

| Scenario | Method | Headers | Expected | How measured |
|----------|--------|---------|----------|-------------|
| No Authorization header | `GET /mcp` | _(none)_ | HTTP 401 | `curl -s -o /dev/null -w "%{http_code}"` |
| Wrong bearer token | `GET /mcp` | `Authorization: Bearer bad-token-<PID>` | HTTP 401 | Same |
| Valid bearer token + initialize body | `POST /mcp` | `Authorization: Bearer <TOKEN>` + JSON-RPC body | Not 401, not 403, not 000 | Same |

The bad-token value is `bad-token-<PID>` (where `<PID>` is the shell's `$$`), making it unique per
run to avoid accidental cache hits.

The `/health` endpoint (Phase 1) is confirmed to be **unauthenticated** — it is hit with plain
`curl -sf` and no Authorization header, and is expected to succeed.

---

## 8. Docker Mode Specifics

`run_docker_mode()` manages the full container lifecycle.

### Required Environment Variables

`GOTIFY_URL` must be set. `GOTIFY_APP_TOKEN` and `GOTIFY_CLIENT_TOKEN` are optional but passed
through.

### Image Build

```bash
docker build -t gotify-mcp-test <REPO_DIR>
```

Output is suppressed (`>/dev/null`). The Dockerfile at the repo root is used. The image tag is
`gotify-mcp-test` (fixed name).

### Container Startup

```bash
docker run -d \
    --name gotify-mcp-test-<PID> \
    -p 9158:9158 \
    -e GOTIFY_URL=<value> \
    -e GOTIFY_APP_TOKEN=<value or empty> \
    -e GOTIFY_CLIENT_TOKEN=<value or empty> \
    -e GOTIFY_MCP_TOKEN=<ci_token> \
    -e GOTIFY_MCP_TRANSPORT=http \
    -e GOTIFY_MCP_PORT=9158 \
    gotify-mcp-test
```

Container name is `gotify-mcp-test-<PID>` (unique per run).

The MCP bearer token (`GOTIFY_MCP_TOKEN`) is derived as follows:
- If `$TOKEN` equals the default string `"ci-integration-token"`, a per-run token is generated:
  `"ci-integration-token-<PID>"`
- Otherwise, whatever was passed via `--token` or `GOTIFY_MCP_TOKEN` is reused

### Health Polling

`wait_for_health()` polls `<BASE_URL>/health` every 1 second for up to 30 attempts:
```bash
curl -sf http://localhost:9158/health
```
Success when curl exits 0 (HTTP 2xx response). If not healthy after 30 seconds, the script
prints an error and returns non-zero (which, due to `set -euo pipefail`, exits the script).

### Teardown

A `trap` is registered immediately after `docker run`:
```bash
trap "docker rm -f '${CONTAINER_NAME}' &>/dev/null || true" EXIT INT TERM
```
This guarantees container removal even on script failure or Ctrl-C. After `run_http_tests`
completes normally, the container is removed explicitly and the trap is cleared:
```bash
docker rm -f "${CONTAINER_NAME}" &>/dev/null || true
trap - EXIT INT TERM
```

### Post-Build State

`$TOKEN` and `$BASE_URL` are overwritten to the container-specific values before calling
`run_http_tests`, so the HTTP test phases use the correct endpoint and auth token.

---

## 9. Stdio Mode Specifics

`run_stdio_mode()` exercises the server through the stdio MCP transport using
[mcporter](https://github.com/mcporter/mcporter) as the JSON-RPC bridge.

### Prerequisites

- `npx` (Node.js npm)
- `uvx` (Python uv tool runner)

### mcporter Config

A temporary JSON config file is written to `/tmp/gotify-mcp-mcporter-XXXXXX.json`:

```json
{
  "mcpServers": {
    "gotify-mcp": {
      "command": "uvx",
      "args": ["--directory", "<REPO_DIR>", "--from", ".", "gotify-mcp-server"],
      "env": {
        "GOTIFY_URL": "<GOTIFY_URL>",
        "GOTIFY_APP_TOKEN": "<GOTIFY_APP_TOKEN or empty>",
        "GOTIFY_CLIENT_TOKEN": "<GOTIFY_CLIENT_TOKEN or empty>",
        "GOTIFY_MCP_TRANSPORT": "stdio"
      }
    }
  }
}
```

Key details:
- `--directory <REPO_DIR>` pins uvx to the local repo source, not a published package
- `--from .` installs from the local `pyproject.toml`
- Entry point is `gotify-mcp-server` (defined in `pyproject.toml` under `[project.scripts]`)
- `GOTIFY_MCP_TRANSPORT=stdio` forces stdio transport (no HTTP server, no port)
- No `GOTIFY_MCP_TOKEN` in stdio env — not needed for stdio transport

The temp file is cleaned up via `trap "rm -f '$cfg_file'"` on EXIT, INT, and TERM.

### Subprocess Invocation

All stdio tests use `npx -y mcporter@latest`:
- `-y` suppresses the "proceed?" prompt
- `@latest` always fetches the current published version

### Stdio Tests

| # | Command | Test label | PASS condition | FAIL condition |
|---|---------|-----------|----------------|----------------|
| S1 | `npx mcporter list` | `stdio: tools list contains gotify_help` | Output contains `"gotify_help"` (case-insensitive) | Not found in output (first 200 chars shown) |
| S2 | `npx mcporter list` | `stdio: tools list contains gotify` | Output matches `(^|[^_a-z])gotify([^_a-z]|$)` (word-boundary regex) | Not found |
| S3 | `npx mcporter call gotify_help '{}'` | `stdio: gotify_help output contains 'gotify'` | Output contains `"gotify"` (case-insensitive) | Not found |
| S4 | `npx mcporter call gotify '{"action":"list_applications"}'` | `stdio: gotify list_applications output contains 'items'` | Output contains `"items"` (case-insensitive) OR output contains `{` or `[` | Output is neither |

Note on S2: the regex `(^|[^_a-z])gotify([^_a-z]|$)` is slightly different from the HTTP Phase 3
test (which uses `(^|,)gotify(,|$)`). The stdio version guards against word-embedded matches in
prose output rather than comma-separated tool names.

Note on S4: this test has a lenient fallback — if `"items"` is not present but the output looks
like JSON (contains `{` or `[`), the test still passes. This accommodates auth errors that return
a valid JSON error object.

The stdio mode does **not** run the full 22-assertion HTTP test suite. It runs only 4 targeted
assertions covering tool discovery and basic tool invocation.

---

## 10. Expected Output Format

### Per-Test Lines

Each test line is prefixed with a color-coded status tag:

```
  PASS  gotify action=version → .version field present: 2.4.0
  FAIL  gotify action=health → not valid JSON: <unexpected output>
  SKIP  gotify action=list_messages → returned error (likely no client token): 403
  INFO  Waiting for server at http://localhost:9158/health ...
```

- `PASS` = green
- `FAIL` = red
- `SKIP` = yellow
- `INFO` = bold white (informational, not counted)

### Section Banners

Phases and modes are announced with:
```
=== Phase 1 — Health endpoint (unauthenticated) ===
=== Mode: docker ===
```
(Cyan, bold)

### Summary Block

Printed at the end by `print_summary()`:

```
═══════════════════════════════════════
  Test Summary
═══════════════════════════════════════
  PASS: 19
  FAIL: 0
  SKIP: 3
═══════════════════════════════════════
  RESULT: PASSED
```

- Exit code 0 if `FAIL_COUNT == 0`
- Exit code 1 if `FAIL_COUNT > 0`

SKIP tests do not cause failure. A run with 0 PASSes and 0 FAILs (all SKIPs) is reported as PASSED.

### Verbose Mode

With `--verbose` or `VERBOSE=true`, each test additionally prints:
- `RAW:` — raw curl response before SSE stripping
- `TOOL RESP:` — parsed JSON response body from each `call_tool` invocation
- Per-tool labels like `health tool:`, `version tool:`, etc.

### SSE Stripping

The `mcp_post()` helper automatically handles FastMCP's streamable-HTTP transport, which may
return responses prefixed with `data: ` (SSE format). The helper strips this prefix:

```bash
stripped=$(echo "$raw" | grep -E '^data: ' | sed 's/^data: //' | head -1)
```

If no `data: ` lines are found, the raw response is used as-is. This means the script works
correctly whether FastMCP sends plain JSON or SSE-wrapped JSON.

### Interpreting Results

| Outcome | Meaning |
|---------|---------|
| All PASS | Server is correctly implementing all tested tool actions |
| FAIL on Phase 2 | Auth middleware is broken or not enforcing tokens |
| FAIL on Phase 3 initialize | Server name does not contain "gotify" — may be wrong server |
| FAIL on Phase 3 tools/list | `gotify_help` or `gotify` tool is missing from registry |
| FAIL on Phase 4 health/version | MCP server cannot reach the upstream Gotify instance |
| SKIP on list_messages/list_clients/current_user | `GOTIFY_CLIENT_TOKEN` not set — normal in CI without full credentials |
| FAIL on Phase 4 list_applications | Gotify app token invalid or `GOTIFY_URL` unreachable |
| FAIL in stdio mode | `uvx`/`mcporter` not installed, or stdio transport broken |
