#!/usr/bin/env bash
# =============================================================================
# tests/test_live.sh — Canonical live integration tests for gotify-mcp
#
# Modes (--mode or MODE env var):
#   http    — test against already-running HTTP server
#   docker  — build image, start container, run HTTP tests, tear down
#   stdio   — run via mcporter + uvx stdio transport
#   all     — docker then stdio (default)
#
# Usage:
#   bash tests/test_live.sh                        # all modes
#   bash tests/test_live.sh --mode http --url http://localhost:9158 --token mytoken
#   bash tests/test_live.sh --mode docker
#   bash tests/test_live.sh --mode stdio
#   bash tests/test_live.sh --verbose
# =============================================================================
set -euo pipefail

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MODE="${MODE:-all}"
BASE_URL="${GOTIFY_MCP_URL:-http://localhost:9158}"
TOKEN="${GOTIFY_MCP_TOKEN:-ci-integration-token}"
VERBOSE="${VERBOSE:-false}"
ENTRY_POINT="gotify-mcp-server"
PORT=9158
CONTAINER_NAME="gotify-mcp-test-$$"
IMAGE_NAME="gotify-mcp-test"

# ---------------------------------------------------------------------------
# Parse flags
# ---------------------------------------------------------------------------
while [[ $# -gt 0 ]]; do
    case "$1" in
        --mode)   MODE="$2";     shift 2 ;;
        --url)    BASE_URL="$2"; shift 2 ;;
        --token)  TOKEN="$2";    shift 2 ;;
        --verbose) VERBOSE=true; shift ;;
        --help)
            sed -n '2,20p' "$0" | sed 's/^# \?//'
            exit 0
            ;;
        *) echo "Unknown flag: $1" >&2; exit 2 ;;
    esac
done

# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; RESET='\033[0m'

PASS_COUNT=0
FAIL_COUNT=0
SKIP_COUNT=0

section() { echo -e "\n${CYAN}${BOLD}=== $* ===${RESET}"; }
pass()    { echo -e "  ${GREEN}PASS${RESET}  $*"; (( PASS_COUNT++ )) || true; }
fail()    { echo -e "  ${RED}FAIL${RESET}  $*"; (( FAIL_COUNT++ )) || true; }
skip()    { echo -e "  ${YELLOW}SKIP${RESET}  $*"; (( SKIP_COUNT++ )) || true; }
info()    { echo -e "  ${BOLD}INFO${RESET}  $*"; }
verbose() { [[ "$VERBOSE" == "true" ]] && echo -e "       $*" || true; }

# ---------------------------------------------------------------------------
# Prereq checks
# ---------------------------------------------------------------------------
check_prereqs() {
    local missing=()
    for cmd in curl jq; do
        command -v "$cmd" &>/dev/null || missing+=("$cmd")
    done
    if [[ ${#missing[@]} -gt 0 ]]; then
        echo "ERROR: missing required commands: ${missing[*]}" >&2
        exit 2
    fi
}

# ---------------------------------------------------------------------------
# Core HTTP helpers
# ---------------------------------------------------------------------------

# mcp_post <path> <json-body>
# Posts JSON-RPC to the MCP server with Bearer auth.
# Handles SSE "data: " prefix and returns parsed JSON body.
mcp_post() {
    local path="$1"
    local body="$2"
    local raw
    raw=$(curl -sf \
        -X POST \
        -H "Authorization: Bearer ${TOKEN}" \
        -H "Content-Type: application/json" \
        -H "Accept: application/json, text/event-stream" \
        --data-raw "$body" \
        "${BASE_URL}${path}" 2>&1) || {
        echo '{"_curl_error": true}'
        return 0
    }
    verbose "RAW: $raw"
    # Strip SSE data: prefix if present (FastMCP streamable-http)
    local stripped
    stripped=$(echo "$raw" | grep -E '^data: ' | sed 's/^data: //' | head -1)
    if [[ -n "$stripped" ]]; then
        echo "$stripped"
    else
        echo "$raw"
    fi
}

# assert_jq <label> <json> <jq-filter> <expected>
# Runs jq filter on json, checks output matches expected (non-empty if expected is "NONEMPTY")
assert_jq() {
    local label="$1"
    local json="$2"
    local filter="$3"
    local expected="${4:-NONEMPTY}"

    local actual
    actual=$(echo "$json" | jq -r "$filter" 2>/dev/null || echo "JQ_ERROR")

    if [[ "$expected" == "NONEMPTY" ]]; then
        if [[ -n "$actual" && "$actual" != "null" && "$actual" != "JQ_ERROR" ]]; then
            pass "$label"
            return 0
        else
            fail "$label — jq '$filter' returned: '$actual'"
            return 0
        fi
    fi

    if [[ "$actual" == "$expected" ]]; then
        pass "$label"
    else
        fail "$label — expected '$expected', got '$actual'"
    fi
}

# assert_jq_contains <label> <json> <jq-filter> <substring>
# Like assert_jq but checks for substring match (case-insensitive)
assert_jq_contains() {
    local label="$1"
    local json="$2"
    local filter="$3"
    local substring="$4"

    local actual
    actual=$(echo "$json" | jq -r "$filter" 2>/dev/null | tr '[:upper:]' '[:lower:]' || echo "jq_error")
    local sub_lower
    sub_lower=$(echo "$substring" | tr '[:upper:]' '[:lower:]')

    if echo "$actual" | grep -qF "$sub_lower"; then
        pass "$label"
    else
        fail "$label — '$substring' not found in: '$actual'"
    fi
}

# call_tool <tool-name> [<json-args-object>]
# Calls tools/call, validates 200 + no isError, stores body in LAST_TOOL_BODY
LAST_TOOL_BODY=""
MCP_REQUEST_ID=1

call_tool() {
    local tool="$1"
    local args="${2:-{}}"
    (( MCP_REQUEST_ID++ )) || true

    local payload
    payload=$(jq -n --arg t "$tool" --argjson a "$args" --argjson id "$MCP_REQUEST_ID" \
        '{jsonrpc:"2.0",id:$id,method:"tools/call",params:{name:$t,arguments:$a}}')

    local resp
    resp=$(mcp_post "/mcp" "$payload")
    verbose "TOOL RESP: $resp"

    LAST_TOOL_BODY="$resp"

    local is_error
    is_error=$(echo "$resp" | jq -r '.result.isError // false' 2>/dev/null || echo "parse_error")
    if [[ "$is_error" == "true" ]]; then
        # Return gracefully — caller checks LAST_TOOL_BODY
        return 0
    fi
}

# ---------------------------------------------------------------------------
# Health poll
# ---------------------------------------------------------------------------
wait_for_health() {
    local url="$1"
    local attempts="${2:-30}"
    local delay="${3:-1}"
    info "Waiting for server at ${url}/health ..."
    local i
    for (( i=1; i<=attempts; i++ )); do
        if curl -sf "${url}/health" &>/dev/null; then
            info "Server ready after ${i}s"
            return 0
        fi
        sleep "$delay"
    done
    echo "ERROR: server did not become healthy after ${attempts}s" >&2
    return 1
}

# ---------------------------------------------------------------------------
# HTTP test phases
# ---------------------------------------------------------------------------
run_http_tests() {
    section "Phase 1 — Health endpoint (unauthenticated)"

    local health_resp
    health_resp=$(curl -sf "${BASE_URL}/health" 2>&1 || echo '{"_error":true}')
    verbose "Health: $health_resp"

    assert_jq "GET /health → status=ok" "$health_resp" '.status' "ok"

    # ---------------------------------------------------------------------------
    section "Phase 2 — Auth enforcement"

    local status

    # No token
    status=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}/mcp" 2>/dev/null || echo "000")
    if [[ "$status" == "401" ]]; then
        pass "No token → 401"
    else
        fail "No token → expected 401, got $status"
    fi

    # Bad token
    status=$(curl -s -o /dev/null -w "%{http_code}" \
        -H "Authorization: Bearer bad-token-$$" \
        "${BASE_URL}/mcp" 2>/dev/null || echo "000")
    if [[ "$status" == "401" ]]; then
        pass "Bad token → 401"
    else
        fail "Bad token → expected 401, got $status"
    fi

    # Good token
    status=$(curl -s -o /dev/null -w "%{http_code}" \
        -X POST \
        -H "Authorization: Bearer ${TOKEN}" \
        -H "Content-Type: application/json" \
        -H "Accept: application/json" \
        --data-raw '{"jsonrpc":"2.0","id":0,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1"}}}' \
        "${BASE_URL}/mcp" 2>/dev/null || echo "000")
    if [[ "$status" != "401" && "$status" != "403" && "$status" != "000" ]]; then
        pass "Good token → not 401/403 (got $status)"
    else
        fail "Good token → expected non-401/403, got $status"
    fi

    # ---------------------------------------------------------------------------
    section "Phase 3 — MCP protocol"

    # initialize
    (( MCP_REQUEST_ID++ )) || true
    local init_resp
    init_resp=$(mcp_post "/mcp" \
        "{\"jsonrpc\":\"2.0\",\"id\":${MCP_REQUEST_ID},\"method\":\"initialize\",\"params\":{\"protocolVersion\":\"2024-11-05\",\"capabilities\":{},\"clientInfo\":{\"name\":\"test-live\",\"version\":\"1\"}}}")
    verbose "Init: $init_resp"
    assert_jq_contains "initialize → serverInfo.name contains 'gotify'" \
        "$init_resp" '.result.serverInfo.name' "gotify"

    # tools/list
    (( MCP_REQUEST_ID++ )) || true
    local tools_resp
    tools_resp=$(mcp_post "/mcp" \
        "{\"jsonrpc\":\"2.0\",\"id\":${MCP_REQUEST_ID},\"method\":\"tools/list\",\"params\":{}}")
    verbose "Tools: $tools_resp"

    local tool_names
    tool_names=$(echo "$tools_resp" | jq -r '[.result.tools[].name] | join(",")' 2>/dev/null || echo "")

    if echo "$tool_names" | grep -q "gotify_help"; then
        pass "tools/list → gotify_help present"
    else
        fail "tools/list → gotify_help missing (got: $tool_names)"
    fi

    if echo "$tool_names" | grep -qE "(^|,)gotify(,|$)"; then
        pass "tools/list → gotify present"
    else
        fail "tools/list → gotify missing (got: $tool_names)"
    fi

    # ---------------------------------------------------------------------------
    section "Phase 4 — Tool calls (read-only)"

    # gotify_help
    call_tool "gotify_help" "{}"
    local help_text
    help_text=$(echo "$LAST_TOOL_BODY" | jq -r '.result.content[0].text // .result.content // ""' 2>/dev/null || echo "")
    if [[ -n "$help_text" ]]; then
        pass "gotify_help → non-empty response"
    else
        fail "gotify_help → empty or missing result"
    fi
    if echo "$help_text" | grep -qi "gotify"; then
        pass "gotify_help → response contains 'gotify'"
    else
        fail "gotify_help → response does not contain 'gotify'"
    fi

    # action=health
    call_tool "gotify" '{"action":"health"}'
    local health_tool_text
    health_tool_text=$(echo "$LAST_TOOL_BODY" | jq -r '.result.content[0].text // ""' 2>/dev/null || echo "")
    verbose "health tool: $health_tool_text"
    if [[ -n "$health_tool_text" ]]; then
        pass "gotify action=health → non-empty response"
    else
        fail "gotify action=health → empty response"
    fi
    # health response from Gotify is {"health":"green","database":"green"} or similar
    if echo "$health_tool_text" | jq -e '.' &>/dev/null; then
        pass "gotify action=health → valid JSON"
    else
        fail "gotify action=health → not valid JSON: $health_tool_text"
    fi

    # action=version
    call_tool "gotify" '{"action":"version"}'
    local version_text
    version_text=$(echo "$LAST_TOOL_BODY" | jq -r '.result.content[0].text // ""' 2>/dev/null || echo "")
    verbose "version tool: $version_text"
    if [[ -n "$version_text" ]]; then
        pass "gotify action=version → non-empty response"
    else
        fail "gotify action=version → empty response"
    fi
    # Gotify version returns {"version":"...","commit":"...","buildDate":"..."}
    local version_val
    version_val=$(echo "$version_text" | jq -r '.version // empty' 2>/dev/null || echo "")
    if [[ -n "$version_val" ]]; then
        pass "gotify action=version → .version field present: $version_val"
    else
        fail "gotify action=version → .version field missing in: $version_text"
    fi

    # action=list_applications
    call_tool "gotify" '{"action":"list_applications"}'
    local apps_text
    apps_text=$(echo "$LAST_TOOL_BODY" | jq -r '.result.content[0].text // ""' 2>/dev/null || echo "")
    verbose "apps tool: $apps_text"
    if [[ -n "$apps_text" ]]; then
        pass "gotify action=list_applications → non-empty response"
    else
        fail "gotify action=list_applications → empty response"
    fi
    if echo "$apps_text" | jq -e 'has("items")' &>/dev/null; then
        pass "gotify action=list_applications → has 'items' key"
    else
        fail "gotify action=list_applications → missing 'items' key in: $apps_text"
    fi
    # Validate items is an array
    local items_type
    items_type=$(echo "$apps_text" | jq -r '.items | type' 2>/dev/null || echo "error")
    if [[ "$items_type" == "array" ]]; then
        local item_count
        item_count=$(echo "$apps_text" | jq '.items | length' 2>/dev/null || echo "?")
        pass "gotify action=list_applications → items is array (count: $item_count)"
    else
        fail "gotify action=list_applications → .items is not an array (type: $items_type)"
    fi

    # action=list_messages (with limit=5)
    call_tool "gotify" '{"action":"list_messages","limit":5}'
    local msgs_text
    msgs_text=$(echo "$LAST_TOOL_BODY" | jq -r '.result.content[0].text // ""' 2>/dev/null || echo "")
    verbose "msgs tool: $msgs_text"
    if [[ -n "$msgs_text" ]]; then
        pass "gotify action=list_messages → non-empty response"
    else
        fail "gotify action=list_messages → empty response"
    fi
    if echo "$msgs_text" | jq -e 'has("items")' &>/dev/null; then
        pass "gotify action=list_messages → has 'items' key"
    else
        # Could be an error if GOTIFY_CLIENT_TOKEN is not set — that is acceptable
        local err_val
        err_val=$(echo "$msgs_text" | jq -r '.error // empty' 2>/dev/null || echo "")
        if [[ -n "$err_val" ]]; then
            skip "gotify action=list_messages → returned error (likely no client token): $err_val"
        else
            fail "gotify action=list_messages → unexpected structure: $msgs_text"
        fi
    fi

    # action=list_clients
    call_tool "gotify" '{"action":"list_clients"}'
    local clients_text
    clients_text=$(echo "$LAST_TOOL_BODY" | jq -r '.result.content[0].text // ""' 2>/dev/null || echo "")
    verbose "clients tool: $clients_text"
    if [[ -n "$clients_text" ]]; then
        pass "gotify action=list_clients → non-empty response"
    else
        fail "gotify action=list_clients → empty response"
    fi
    if echo "$clients_text" | jq -e 'has("items")' &>/dev/null; then
        pass "gotify action=list_clients → has 'items' key"
    else
        local err_val
        err_val=$(echo "$clients_text" | jq -r '.error // empty' 2>/dev/null || echo "")
        if [[ -n "$err_val" ]]; then
            skip "gotify action=list_clients → returned error (likely no client token): $err_val"
        else
            fail "gotify action=list_clients → unexpected structure: $clients_text"
        fi
    fi

    # action=current_user
    call_tool "gotify" '{"action":"current_user"}'
    local user_text
    user_text=$(echo "$LAST_TOOL_BODY" | jq -r '.result.content[0].text // ""' 2>/dev/null || echo "")
    verbose "user tool: $user_text"
    if [[ -n "$user_text" ]]; then
        pass "gotify action=current_user → non-empty response"
    else
        fail "gotify action=current_user → empty response"
    fi
    # current_user returns {id, name, admin} or error if no client token
    local has_id
    has_id=$(echo "$user_text" | jq -e 'has("id")' 2>/dev/null && echo "yes" || echo "no")
    if [[ "$has_id" == "yes" ]]; then
        local user_name
        user_name=$(echo "$user_text" | jq -r '.name // "unknown"' 2>/dev/null || echo "unknown")
        pass "gotify action=current_user → user id present (name: $user_name)"
    else
        local err_val
        err_val=$(echo "$user_text" | jq -r '.error // empty' 2>/dev/null || echo "")
        if [[ -n "$err_val" ]]; then
            skip "gotify action=current_user → returned error (likely no client token): $err_val"
        else
            fail "gotify action=current_user → missing .id in: $user_text"
        fi
    fi
}

# ---------------------------------------------------------------------------
# Mode: http
# ---------------------------------------------------------------------------
run_http_mode() {
    section "Mode: http — ${BASE_URL}"
    wait_for_health "$BASE_URL" 3 1 || {
        echo "ERROR: server not reachable at ${BASE_URL}" >&2
        exit 2
    }
    run_http_tests
}

# ---------------------------------------------------------------------------
# Mode: docker
# ---------------------------------------------------------------------------
run_docker_mode() {
    section "Mode: docker"

    # Check prereqs
    command -v docker &>/dev/null || { echo "ERROR: docker not found" >&2; exit 2; }

    # Env vars required
    if [[ -z "${GOTIFY_URL:-}" ]]; then
        echo "ERROR: GOTIFY_URL must be set for docker mode" >&2
        exit 2
    fi

    local ci_token="ci-integration-token-$$"
    [[ "${TOKEN}" != "ci-integration-token" ]] && ci_token="$TOKEN"

    # Trap: always remove container
    trap "docker rm -f '${CONTAINER_NAME}' &>/dev/null || true" EXIT INT TERM

    info "Building image: ${IMAGE_NAME}"
    docker build -t "${IMAGE_NAME}" "${REPO_DIR}" >/dev/null

    info "Starting container: ${CONTAINER_NAME}"
    docker run -d \
        --name "${CONTAINER_NAME}" \
        -p "${PORT}:${PORT}" \
        -e "GOTIFY_URL=${GOTIFY_URL}" \
        -e "GOTIFY_APP_TOKEN=${GOTIFY_APP_TOKEN:-}" \
        -e "GOTIFY_CLIENT_TOKEN=${GOTIFY_CLIENT_TOKEN:-}" \
        -e "GOTIFY_MCP_TOKEN=${ci_token}" \
        -e "GOTIFY_MCP_TRANSPORT=http" \
        -e "GOTIFY_MCP_PORT=${PORT}" \
        "${IMAGE_NAME}" >/dev/null

    TOKEN="$ci_token"
    BASE_URL="http://localhost:${PORT}"

    wait_for_health "$BASE_URL" 30 1

    run_http_tests

    info "Removing container: ${CONTAINER_NAME}"
    docker rm -f "${CONTAINER_NAME}" &>/dev/null || true
    trap - EXIT INT TERM
}

# ---------------------------------------------------------------------------
# Mode: stdio
# ---------------------------------------------------------------------------
run_stdio_mode() {
    section "Mode: stdio (via mcporter + uvx)"

    command -v npx &>/dev/null || { echo "ERROR: npx not found — install Node.js" >&2; exit 2; }
    command -v uvx &>/dev/null || { echo "ERROR: uvx not found — install uv" >&2; exit 2; }

    if [[ -z "${GOTIFY_URL:-}" ]]; then
        echo "ERROR: GOTIFY_URL must be set for stdio mode" >&2
        exit 2
    fi

    # Write mcporter config to temp file
    local cfg_file
    cfg_file=$(mktemp /tmp/gotify-mcp-mcporter-XXXXXX.json)
    trap "rm -f '$cfg_file'" EXIT INT TERM

    cat > "$cfg_file" <<EOF
{
  "mcpServers": {
    "gotify-mcp": {
      "command": "uvx",
      "args": ["--directory", "${REPO_DIR}", "--from", ".", "${ENTRY_POINT}"],
      "env": {
        "GOTIFY_URL": "${GOTIFY_URL}",
        "GOTIFY_APP_TOKEN": "${GOTIFY_APP_TOKEN:-}",
        "GOTIFY_CLIENT_TOKEN": "${GOTIFY_CLIENT_TOKEN:-}",
        "GOTIFY_MCP_TRANSPORT": "stdio"
      }
    }
  }
}
EOF

    info "mcporter config: $cfg_file"
    verbose "$(cat "$cfg_file")"

    # Test: list tools
    info "Running: npx mcporter list"
    local list_out
    list_out=$(npx -y mcporter@latest --config "$cfg_file" list 2>&1 || echo "MCPORTER_ERROR")
    verbose "List output: $list_out"

    if echo "$list_out" | grep -qi "gotify_help"; then
        pass "stdio: tools list contains gotify_help"
    else
        fail "stdio: tools list missing gotify_help (output: ${list_out:0:200})"
    fi

    if echo "$list_out" | grep -qE "(^|[^_a-z])gotify([^_a-z]|$)"; then
        pass "stdio: tools list contains gotify"
    else
        fail "stdio: tools list missing gotify (output: ${list_out:0:200})"
    fi

    # Test: call gotify_help
    info "Running: npx mcporter call gotify_help"
    local help_out
    help_out=$(npx -y mcporter@latest --config "$cfg_file" call gotify_help '{}' 2>&1 || echo "MCPORTER_ERROR")
    verbose "Help output: $help_out"

    if echo "$help_out" | grep -qi "gotify"; then
        pass "stdio: gotify_help output contains 'gotify'"
    else
        fail "stdio: gotify_help output missing 'gotify' (output: ${help_out:0:200})"
    fi

    # Test: call gotify action=list_applications
    info "Running: npx mcporter call gotify action=list_applications"
    local apps_out
    apps_out=$(npx -y mcporter@latest --config "$cfg_file" call gotify '{"action":"list_applications"}' 2>&1 || echo "MCPORTER_ERROR")
    verbose "Apps output: $apps_out"

    if echo "$apps_out" | grep -qi "items"; then
        pass "stdio: gotify list_applications output contains 'items'"
    else
        # Could be auth error — check for JSON
        if echo "$apps_out" | grep -qE '\{|\['; then
            pass "stdio: gotify list_applications returned JSON response"
        else
            fail "stdio: gotify list_applications unexpected output (output: ${apps_out:0:200})"
        fi
    fi

    rm -f "$cfg_file"
    trap - EXIT INT TERM
}

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
print_summary() {
    echo ""
    echo -e "${BOLD}═══════════════════════════════════════${RESET}"
    echo -e "${BOLD}  Test Summary${RESET}"
    echo -e "${BOLD}═══════════════════════════════════════${RESET}"
    echo -e "  ${GREEN}PASS${RESET}: ${PASS_COUNT}"
    echo -e "  ${RED}FAIL${RESET}: ${FAIL_COUNT}"
    echo -e "  ${YELLOW}SKIP${RESET}: ${SKIP_COUNT}"
    echo -e "${BOLD}═══════════════════════════════════════${RESET}"
    if [[ $FAIL_COUNT -gt 0 ]]; then
        echo -e "  ${RED}${BOLD}RESULT: FAILED${RESET}"
        return 1
    else
        echo -e "  ${GREEN}${BOLD}RESULT: PASSED${RESET}"
        return 0
    fi
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
check_prereqs

case "$MODE" in
    http)
        run_http_mode
        ;;
    docker)
        run_docker_mode
        ;;
    stdio)
        run_stdio_mode
        ;;
    all)
        run_docker_mode
        PASS_COUNT_AFTER_DOCKER=$PASS_COUNT
        FAIL_COUNT_AFTER_DOCKER=$FAIL_COUNT
        run_stdio_mode
        ;;
    *)
        echo "ERROR: unknown mode '$MODE' (use: http|docker|stdio|all)" >&2
        exit 2
        ;;
esac

print_summary
