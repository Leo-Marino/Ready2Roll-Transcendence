#!/usr/bin/env bash
# Automates: keygen -> unseal -> enable -> loadsecrets
# Usage: ./vault-bootstrap.sh [all|init|unseal|enable|load]
# Idempotent: safe to re-run (e.g. after a container restart, only unseal happens).
set -euo pipefail

COMPOSE="${COMPOSE:-docker compose}"
INIT_FILE="${INIT_FILE:-secrets/vault-init.json}"    # contains unseal keys + root token. GITIGNORE IT.
SECRETS_FILE="${SECRETS_FILE:-./r2r-secrets.json}"
APPROLE_DIR="secrets/approle"
KEY_SHARES=5
KEY_THRESHOLD=2

command -v jq >/dev/null || { echo "jq is required (apt install jq / brew install jq)"; exit 1; }

# vault CLI inside the container, authenticated with the root token if we have one
v() {
  if [[ -f "$INIT_FILE" ]]; then
    $COMPOSE exec -T -e VAULT_TOKEN="$(jq -r .root_token "$INIT_FILE")" vault vault "$@"
  else
    $COMPOSE exec -T vault vault "$@"
  fi
}

# `vault status` exit codes: 0 = unsealed, 2 = sealed, 1 = error/unreachable
wait_for_vault() {
  echo "Waiting for Vault API..."
  for _ in $(seq 1 30); do
    set +e; $COMPOSE exec -T vault vault status >/dev/null 2>&1; rc=$?; set -e
    [[ $rc -ne 1 ]] && return 0
    sleep 2
  done
  echo "Vault did not become reachable in 60s"; exit 1
}

# `vault status` exits 2 when sealed, which pipefail would turn into a false negative.
# Capture the JSON first (ignoring the exit code), then query it.
vault_status() { $COMPOSE exec -T vault vault status -format=json 2>/dev/null || true; }
is_initialized() { [[ "$(vault_status | jq -r '.initialized')" == "true" ]]; }
is_sealed()      { [[ "$(vault_status | jq -r '.sealed')" == "true" ]]; }

do_init() {
  if is_initialized; then echo "[init] already initialized, skipping"; return; fi
  [[ -f "$INIT_FILE" ]] && { echo "[init] $INIT_FILE exists but Vault is uninitialized. Refusing to overwrite."; exit 1; }
  echo "[init] initializing ($KEY_SHARES shares, threshold $KEY_THRESHOLD)"
  mkdir -p "$(dirname "$INIT_FILE")"
  ( umask 077
    $COMPOSE exec -T vault vault operator init \
      -key-shares=$KEY_SHARES -key-threshold=$KEY_THRESHOLD -format=json > "$INIT_FILE" )
  echo "[init] keys + root token saved to $INIT_FILE (chmod 600)"
}

do_unseal() {
  [[ -f "$INIT_FILE" ]] || { echo "[unseal] $INIT_FILE missing, cannot unseal"; exit 1; }
  if ! is_sealed; then echo "[unseal] already unsealed"; return; fi
  for i in $(seq 0 $((KEY_THRESHOLD - 1))); do
    $COMPOSE exec -T vault vault operator unseal "$(jq -r ".unseal_keys_b64[$i]" "$INIT_FILE")" >/dev/null
  done
  echo "[unseal] done"
  $COMPOSE restart vault-agent
}

do_enable() {
  echo "[enable] audit device"
  v audit list -format=json | jq -e '."file/"' >/dev/null \
    || v audit enable file file_path=/vault/logs/audit.log

  echo "[enable] kv-v2 at r2r/"
  v secrets list -format=json | jq -e '."r2r/"' >/dev/null \
    || v secrets enable -path=r2r kv-v2

  echo "[enable] policy django-read"
  printf 'path "r2r/data/django" {\n  capabilities = ["read"]\n}\n' | v policy write django-read -

  echo "[enable] approle auth + role django"
  v auth list -format=json | jq -e '."approle/"' >/dev/null \
    || v auth enable approle
  v write auth/approle/role/django token_policies=django-read token_ttl=1h token_max_ttl=4h

  echo "[enable] writing role_id / secret_id to $APPROLE_DIR"
  mkdir -p "$APPROLE_DIR"
  ( umask 077
    v read -field=role_id auth/approle/role/django/role-id > "$APPROLE_DIR/role_id"
    v write -f -field=secret_id auth/approle/role/django/secret-id > "$APPROLE_DIR/secret_id" )

  # the agent needs these files, so restart it now that they exist
  $COMPOSE restart vault-agent
}

do_load() {
  [[ -f "$SECRETS_FILE" ]] || { echo "[load] $SECRETS_FILE not found"; exit 1; }
  v kv put r2r/django - < "$SECRETS_FILE"
  echo "[load] secrets loaded into r2r/django"
}

wait_for_vault
case "${1:-all}" in
  init)   do_init ;;
  unseal) do_unseal ;;
  enable) do_enable ;;
  load)   do_load ;;
  all)    do_init; do_unseal; do_enable; do_load ;;
  *) echo "Usage: $0 [all|init|unseal|enable|load]"; exit 1 ;;
esac
