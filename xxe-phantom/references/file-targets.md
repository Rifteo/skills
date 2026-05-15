# High-Value File Targets for XXE

## Linux / Unix — System

```
/etc/passwd                     User accounts (always try first — confirms LFI)
/etc/shadow                     Hashed passwords (root access only)
/etc/hosts                      Internal hostnames and IPs (network mapping)
/etc/hostname                   Server hostname
/etc/resolv.conf                DNS servers
/etc/os-release                 OS version
/etc/crontab                    Cron jobs (check for scheduled scripts)
/etc/cron.d/*                   Additional cron jobs
/etc/sudoers                    Sudo privileges
/etc/group                      Groups and members
/etc/ssh/sshd_config            SSH daemon configuration
/etc/nginx/nginx.conf           Nginx config (virtualhost names, upstream servers)
/etc/nginx/sites-enabled/*      Nginx virtual host configs
/etc/apache2/apache2.conf       Apache config
/etc/apache2/sites-enabled/*    Apache virtual host configs
/etc/httpd/conf/httpd.conf      Apache (RHEL/CentOS)
/etc/mysql/my.cnf               MySQL config (credentials, socket path)
/etc/postgresql/*/main/pg_hba.conf  PostgreSQL auth config
```

## Linux — Process / Runtime

```
/proc/self/environ              Environment variables (DB_PASSWORD, SECRET_KEY, etc.)
/proc/self/cmdline              Command that launched the process
/proc/self/cwd                  Symlink to working directory (reveals app path)
/proc/self/exe                  Symlink to the binary
/proc/self/fd/0                 stdin
/proc/self/maps                 Memory map (loaded libraries, paths)
/proc/net/tcp                   Open TCP connections (internal network ports)
/proc/net/fib_trie              Routing table (internal IPs)
```

## SSH Keys

```
/root/.ssh/id_rsa
/root/.ssh/id_ed25519
/root/.ssh/authorized_keys
/home/ubuntu/.ssh/id_rsa
/home/www-data/.ssh/id_rsa
/home/git/.ssh/id_rsa
/home/deploy/.ssh/id_rsa
```

## Application Configuration Files

### PHP / Laravel / Symfony
```
/var/www/html/.env
/var/www/html/config.php
/var/www/html/wp-config.php         WordPress DB credentials + secret keys
/var/www/html/configuration.php     Joomla DB credentials
/var/www/html/config/database.php
/app/.env
/app/config/database.php
/app/config/app.php
/app/storage/logs/laravel.log
```

### Python / Django / Flask
```
/app/settings.py
/app/config.py
/app/.env
/etc/uwsgi/apps-enabled/*.ini
/var/www/html/settings.py
```

### Java / Spring Boot
```
/app/application.properties
/app/application.yml
/opt/tomcat/conf/server.xml
/opt/tomcat/conf/web.xml
/opt/jboss/standalone/configuration/standalone.xml
/WEB-INF/web.xml
/WEB-INF/applicationContext.xml
```

### Node.js
```
/app/.env
/app/config.js
/app/config/default.json
/app/package.json                   (reveals dependencies and scripts)
```

### Ruby on Rails
```
/app/config/database.yml
/app/config/secrets.yml
/app/config/master.key
/app/.env
```

### .NET / ASP.NET
```
C:\inetpub\wwwroot\web.config
C:\Windows\Microsoft.NET\Framework\*\CONFIG\machine.config
C:\Users\Administrator\.ssh\id_rsa
```

## Cloud / Container Environments

```
# AWS EC2 instance metadata (via SSRF)
http://169.254.169.254/latest/meta-data/
http://169.254.169.254/latest/meta-data/iam/security-credentials/
http://169.254.169.254/latest/user-data/

# GCP (via SSRF, requires Metadata-Flavor: Google header)
http://metadata.google.internal/computeMetadata/v1/project/project-id
http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token

# Azure (via SSRF)
http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://management.azure.com/

# ECS task metadata
http://169.254.170.2/v2/metadata

# Kubernetes service account token (inside pod)
/var/run/secrets/kubernetes.io/serviceaccount/token
/var/run/secrets/kubernetes.io/serviceaccount/namespace
/var/run/secrets/kubernetes.io/serviceaccount/ca.crt
```

## Logs (may contain credentials, tokens, internal IPs)

```
/var/log/auth.log               SSH login attempts + sudo usage
/var/log/syslog
/var/log/apache2/access.log
/var/log/apache2/error.log
/var/log/nginx/access.log
/var/log/nginx/error.log
/var/log/mysql/error.log
/app/storage/logs/laravel.log
/tmp/startup.log
```

## Windows Targets

```
C:\Windows\win.ini
C:\Windows\System32\drivers\etc\hosts
C:\Windows\System32\drivers\etc\services
C:\Windows\repair\SAM                  Hashed Windows passwords (Shadow Copy)
C:\Windows\system32\config\SAM
C:\inetpub\wwwroot\web.config          ASP.NET app settings + DB connections
C:\inetpub\wwwroot\*.config
C:\Users\Administrator\Desktop\*.txt
C:\Users\Administrator\.ssh\id_rsa
C:\ProgramData\MySQL\MySQL Server *\my.ini
C:\xampp\mysql\bin\my.ini
C:\xampp\php\php.ini
C:\xampp\apache\conf\httpd.conf
```

## Docker / Container

```
/.dockerenv                         Confirms container environment
/etc/docker/daemon.json
/run/secrets/*                      Docker secrets
/proc/1/environ                     PID 1 env vars (init process — often has secrets)
/proc/1/cmdline                     Init command
```

## Interesting Directories (use PHP file:// with directory path)

```
# List directory (some parsers return directory listing when pointing to a dir)
file:///etc/
file:///var/www/html/
file:///app/
file:///tmp/
```

## Priority Order

1. `/etc/passwd` — always first (confirm LFI, find usernames)
2. `/proc/self/environ` — secrets in env vars (DB_PASSWORD, AWS_SECRET, etc.)
3. App `.env` or `config.php` — database URL + API keys
4. `/root/.ssh/id_rsa` or `/home/<user>/.ssh/id_rsa` — SSH access
5. App source code (`settings.py`, `database.yml`) — all secrets in one place
6. `/etc/shadow` — hashed passwords (crack offline)
7. `/var/log/*.log` — reconnaissance (may contain credentials sent in URLs)
