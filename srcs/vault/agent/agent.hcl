pid_file = "/tmp/agent.pid"

vault {
  address = "https://vault:8200"
  ca_cert = "/vault/tls/ca.crt"
}

auto_auth {
  method "approle" {
    config = {
      role_id_file_path                   = "/vault/approle/role_id"
      secret_id_file_path                 = "/vault/approle/secret_id"
      remove_secret_id_file_after_reading = false   # mount is read-only
    }
  }
}

# Django: every key stored in r2r/django
template {
  destination = "/vault/secrets/django.env"
  perms       = "0644"
  contents    = <<EOT
{{ with secret "r2r/data/django" }}{{ range $k, $v := .Data.data }}export {{ $k }}={{ $v | toJSON }}
{{ end }}{{ end }}
EOT
}

# MinIO: only its own two values, written to a separate volume
template {
  destination = "/vault/secrets-minio/minio.env"
  perms       = "0644"
  contents    = <<EOT
{{ with secret "r2r/data/django" }}export MINIO_USER={{ .Data.data.MINIO_USER | toJSON }}
export MINIO_PASSWORD={{ .Data.data.MINIO_PASSWORD | toJSON }}
{{ end }}
EOT
}
