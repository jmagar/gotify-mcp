# Git Hook Configuration

Git hooks for `gotify-mcp` plus the separate Claude Code session hooks used by the plugin.

## Git hooks

`gotify-mcp` uses `lefthook.yml` for commit-time checks:

```yaml
pre-commit:
  parallel: true
  commands:
    diff_check:
      run: git diff --check --cached
    yaml:
      glob: "*.{yml,yaml}"
      run: uv run python -c 'import sys, yaml; [yaml.safe_load(open(path, "r", encoding="utf-8")) for path in sys.argv[1:]]' {staged_files}
    lint:
      run: just lint
    format:
      run: just fmt
    skills:
      run: just validate-skills
    env_guard:
      run: bash bin/block-env-commits.sh
```

Install and run:

```bash
lefthook install
lefthook run pre-commit
```

## Claude Code session hooks

Claude Code plugin hooks remain defined in `hooks/hooks.json` and run automatically during Claude Code sessions.

## Related Docs

- [CICD.md](CICD.md) — same checks in CI
- [DEPLOY.md](DEPLOY.md) — Dockerfile conventions enforced by hooks
- [ENV.md](ENV.md) — environment variable patterns
