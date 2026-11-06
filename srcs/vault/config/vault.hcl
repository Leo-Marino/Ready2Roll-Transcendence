ui            = false # Doesn’t serve the web UI. The API and CLI work as normal.
api_addr      = "https://vault:8200"
cluster_addr  = "https://vault:8201"
disable_mlock = true

storage "raft" {
  path    = "/vault/file" # Opens its built-in database at /vault/file
  node_id = "vault-1" # This node’s name in the Raft cluster
}

# Opens port 8200 for the API and loads vault.crt and vault.key
listener "tcp" {
  address         = "0.0.0.0:8200"
  cluster_address = "0.0.0.0:8201"
  tls_cert_file   = "/vault/tls/vault.crt"
  tls_key_file    = "/vault/tls/vault.key"
  tls_min_version = "tls12"
}
