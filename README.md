<p align="center">
  <a href="https://weatherapp.crut0i.com">
    <img src="https://github.com/user-attachments/assets/10d7d70a-a8d2-4beb-92f9-b4c1c02f56c8" width="450" height="126" alt="Service logo" />
  </a>
</p>

&nbsp;

# 👾 Weather App

## 📝 Description

Simple weather application, written in FastAPI

Tech stack: fastapi, postgresql, redis, hashicorp vault, prometheus, promtail, loki, nginx

Main feautures:

- Saving user sessions & history to postgresql
- Modern UI with search autofill
- Restoring last search query
- Admin API: logs, search history by session_id
- Collecting logs by promtail, prometheus & loki
- Safe secrets storing with hashicorp vault

Todo:

- Fix bugs & improve UI
- Create admin dashboard
- Deploy in k8s

Structure

```tree
📦Weather App
 ┣ 📂.github <- github setup
 ┣ 📂bin <- entrypoint
 ┣ 📂config <- project config
 ┣ 📂docker <- docker files
 ┣ 📂scripts <- maintenance scripts
 ┣ 📂src <- project sources
 ┣ 📂tests <- functional / unit tests
 ┣ 📜.coveragerc <- code coverage setup
 ┣ 📜.dockerignore <- docker ignoring setup
 ┣ 📜.gitignore <- git ignoring setup
 ┣ 📜.pre-commit-config.yaml <- pre-commit hooks
 ┣ 📜pyproject.toml <- project env setup
 ┣ 📜README.md <- this readme
 ┗ 📜uv.lock <- package & project manager
```

Live demo available at: weatherapp.crut0i.com

## 🐳 Deploy with docker

### Docker compose

```yml
networks:
  weather-app-network:
    driver: bridge

services:
  weather-app:
    image: ghcr.io/crut0i/weatherapp
    container_name: weather-app
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    logging:
      driver: json-file
      options:
        tag: "{{.ImageName}}|{{.Name}}|{{.ImageFullID}}|{{.FullID}}"
    volumes:
      - ${APP_ENV_PATH}:/app/config/.env:ro
      - ${HYPERCORN_CONF_PATH}:/app/config/hypercorn.toml
    networks:
      - weather-app-network
    depends_on:
      - vault
      - redis
      - loki
      - promtail
      - prometheus
      - postgres

  nginx:
    image: nginx:alpine
    container_name: nginx
    restart: unless-stopped
    ports:
      - "${NGINX_PORT:-127.0.0.1:3000}:80"
    volumes:
      - ${NGINX_CONF_PATH}:/etc/nginx/nginx.conf
    networks:
      - weather-app-network
    depends_on:
      - weather-app

  postgres:
    image: postgres:alpine
    container_name: postgres
    restart: unless-stopped
    ports:
      - "${POSTGRES_PORT:-127.0.0.1:5432}:5432"
    environment:
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_DB=${POSTGRES_DB}
    networks:
      - weather-app-network

  vault:
    image: hashicorp/vault:latest
    container_name: vault
    restart: unless-stopped
    environment:
      VAULT_ADDR: "${VAULT_ADDR:-http://127.0.0.1:8200}"
      VAULT_API_ADDR: "${VAULT_API_ADDR:-http://127.0.0.1:8200}"
      VAULT_ADDRESS: "${VAULT_ADDRESS:-http://127.0.0.1:8200}"
    volumes:
      - ./logs:/vault/logs/:rw
      - ./data:/vault/data/:rw
      - ./config:/vault/config/:rw
      - ./certs:/certs/:rw
      - ./file:/vault/file/:rw
      - ${VAULT_CONFIG_PATH}:/vault/config/config.hcl
    cap_add:
      - IPC_LOCK
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "5"
    ports:
      - "${VAULT_PORT:-127.0.0.1:8200}:8200"
      - "${VAULT_PORT_CLUSTER:-127.0.0.1:8201}:8201"
    networks:
      - weather-app-network
    entrypoint: vault server -config /vault/config/config.hcl

  redis:
    image: redis:alpine
    container_name: redis
    restart: unless-stopped
    ports:
      - "${REDIS_PORT:-127.0.0.1:6379}:6379"
    networks:
      - weather-app-network

  loki:
    image: grafana/loki:latest
    container_name: loki
    restart: unless-stopped
    ports:
      - "${LOKI_PORT:-127.0.0.1:3100}:3100"
    networks:
      - weather-app-network

  promtail:
    image: grafana/promtail:latest
    container_name: promtail
    restart: unless-stopped
    privileged: true
    volumes:
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
      - /var/run/docker.sock:/var/run/docker.sock
      - ${PROMTAIL_CONFIG_PATH}:/etc/promtail/config.yml
    ports:
      - "${PROMTAIL_PORT:-127.0.0.1:9080}:9080"
    networks:
      - weather-app-network
    command: -config.file=/etc/promtail/config.yml

  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    restart: unless-stopped
    volumes:
      - prometheusdata:/prometheus
      - ${PROMETHEUS_CONFIG_PATH}:/etc/prometheus/prometheus.yml
    ports:
      - "${PROMETHEUS_PORT:-127.0.0.1:9090}:9090"
    networks:
      - weather-app-network

volumes:
  prometheusdata:
```

## 🔒 **Secure Cloning**

To securely clone this repository, you can use HTTPS or SSH

### Cloning with HTTPS

```bash
git clone https://github.com/crut0i/WeatherApp.git
```

### Cloning with SSH

```bash
git clone git@github.com:crut0i/WeatherApp.git
```

------

> [!WARNING]
> Project using open-source weather API: open-meteo.com
