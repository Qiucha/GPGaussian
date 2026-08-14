# 05 - Ignore rules, drop bytecode, fresh root commit

Type: task
Status: resolved
Blocked by: 02, 03, 04

## Question

(Nothing to decide beyond What besides first-party code ships in the GitHub-ready tree and the upstream-consume tickets.) Add a root `.gitignore` that keeps `data/`, `.trash/`, third-party clone dirs, bytecode, egg-info, and any local-only paths from that grilling off the published tree. Remove already-tracked `__pycache__/*.pyc`. Rewrite to a fresh root commit on `main` so GitHub never sees those blobs. Do not add a remote or push.

## Comments

`.gitignore` is in place (data, .trash, vendor, third_party, bytecode, egg-info, `.claude/`, root `issues/`, Paper_Writing, Dev Plan.md, digest/data, PDFs). The index is staged without those paths (215 publishable files; digest is only `index.html` / `app.js` / `style.css`).

A fresh root commit could not be written here: `commit.gpgsign` needs the passphrase for `~/.ssh/id_ed25519_signing`. Run this locally, then mark this ticket resolved:

```shell
git checkout --orphan github-ready-root
git commit -m "$(cat <<'EOF'
Start from a GitHub-ready root commit without local data or vendored clones.

Keep Phys4DGS sources, tests, agent docs, and digest dashboard code; leave checkpoints, .trash, vendor trees, and bytecode out of history.
EOF
)"
git branch -M main
```

Do not add a remote or push. If the index was reset, `git add -A` after confirming `.gitignore` still excludes the local-only paths.

## Answer

Done on `main` as a single root commit `8d2d74b` (“Start from a GitHub-ready root commit without local data or vendored clones.”). 216 tracked files; no `__pycache__`, `data/`, `vendor/`, `.trash/`, or other local-only paths. No remote. `.gitignore` as described in Comments.

