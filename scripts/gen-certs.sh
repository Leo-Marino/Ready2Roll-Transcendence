#!/usr/bin/env bash
set -euo pipefail

HOST_IP="${PUBLIC_HOST_IP:-$(hostname -I | awk '{print $1}')}"
HOST_NAME="${PUBLIC_HOSTNAME:-$(hostname -f 2>/dev/null || hostname)}"
CA_DIR=.certs-ca            # gitignored, never mounted into a container
VAULT_DIR=srcs/vault/tls
WAF_DIR=srcs/waf/certs
mkdir -p "$CA_DIR" "$VAULT_DIR" "$WAF_DIR"

# One CA, created once
if [ ! -f "$CA_DIR/ca.key" ]; then
  openssl genrsa -out "$CA_DIR/ca.key" 4096
  openssl req -x509 -new -key "$CA_DIR/ca.key" -sha256 -days 365 \
    -subj "/CN=Ready2Roll Dev CA" \
    -addext "basicConstraints=critical,CA:TRUE" -out "$CA_DIR/ca.crt"
fi
cp "$CA_DIR/ca.crt" "$VAULT_DIR/ca.crt"   # Vault Agent trusts this

issue() {  # issue <name> <outdir> <CN> <SAN list>
  openssl genrsa -out "$2/$1.key" 2048
  openssl req -new -key "$2/$1.key" -subj "/CN=$3" -out "$2/$1.csr"
  printf "subjectAltName=%s\nextendedKeyUsage=serverAuth\n" "$4" > "$2/$1.ext"
  openssl x509 -req -in "$2/$1.csr" -CA "$CA_DIR/ca.crt" -CAkey "$CA_DIR/ca.key" \
    -CAcreateserial -days 365 -sha256 -extfile "$2/$1.ext" -out "$2/$1.crt"
  rm -f "$2/$1.csr" "$2/$1.ext"
  chmod 644 "$2/$1.crt" "$2/$1.key"
}

# Vault: reached only as https://vault:8200 inside Docker, or localhost via exec
issue vault  "$VAULT_DIR" vault        "DNS:vault,DNS:localhost,IP:127.0.0.1"
# WAF: the names/addresses browsers will actually use
issue server "$WAF_DIR"   "$HOST_NAME" "DNS:localhost,DNS:$HOST_NAME,IP:127.0.0.1,IP:$HOST_IP"

echo "WAF cert covers: localhost, $HOST_NAME, $HOST_IP"