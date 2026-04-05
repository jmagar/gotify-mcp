# MCP Elicitation

Interactive credential and configuration entry via the MCP elicitation protocol.

## What is elicitation

Elicitation is an MCP protocol capability that allows servers to request information from users interactively through the client. Instead of requiring pre-configured environment variables, the server can prompt the user for missing values at runtime.

## When to use

- **First-run setup** — server detects missing `GOTIFY_URL` or `GOTIFY_CLIENT_TOKEN` and prompts the user
- **Credential rotation** — user triggers a reconfiguration flow
- **Destructive operation confirmation** — gate dangerous actions behind explicit user acknowledgment

## Destructive operation confirmation

gotify-mcp uses a two-call confirmation pattern for operations that delete data.

### Flow

1. Client calls destructive action without `confirm=True`
2. Server returns: `"Destructive operation. Pass confirm=True to proceed."`
3. Client presents the warning to the user
4. User approves — client re-invokes with `confirm=True`
5. Server executes the destructive operation

### Destructive actions

- `delete_message`
- `delete_all_messages`
- `delete_application`
- `delete_client`

### YOLO mode

Skip confirmation prompts for automated pipelines:

```bash
ALLOW_DESTRUCTIVE=true
# or
ALLOW_YOLO=true
```

When set, destructive actions execute immediately without the two-call confirmation. Use only in CI or trusted automation contexts.

## Fallback for missing configuration

When required environment variables are missing, the server exits with a clear error message:

```
CRITICAL: GOTIFY_URL must be set in the environment.
```

```
CRITICAL: GOTIFY_MCP_TOKEN is not set.
Set GOTIFY_MCP_TOKEN to a secure random token, or set GOTIFY_MCP_NO_AUTH=true
to disable auth (only appropriate when secured at the network/proxy level).

Generate a token with: openssl rand -hex 32
```

This ensures the user always gets actionable guidance.

See also: [ENV](ENV.md) | [AUTH](AUTH.md) | [PATTERNS](PATTERNS.md)
