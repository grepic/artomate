# Docker Deployment Guide

Complete guide for deploying Artomate using Docker and Docker Compose.

## Quick Start

```bash
# 1. Clone repository
git clone <repository-url>
cd artomate

# 2. Create .env file
cp .env.example .env
# Edit .env with your API keys

# 3. Start all services
docker-compose up -d

# 4. Check status
docker-compose ps

# 5. View logs
docker-compose logs -f
```

Access:
- API: http://localhost:8000
- UI: http://localhost:8501
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

## Services

The Docker Compose setup includes:

### Core Services

1. **db** (PostgreSQL) - Database
   - Port: 5432
   - Persistent volume: `postgres_data`

2. **redis** - Job queue
   - Port: 6379
   - Persistent volume: `redis_data`

3. **api** - FastAPI backend
   - Port: 8000
   - Depends on: db, redis

4. **worker** - RQ worker for background jobs
   - No exposed ports
   - Depends on: db, redis

5. **ui** - Streamlit UI
   - Port: 8501
   - Depends on: api

### Monitoring Services (Optional)

6. **prometheus** - Metrics collection
   - Port: 9090
   - Profile: monitoring

7. **grafana** - Metrics dashboards
   - Port: 3000
   - Profile: monitoring
   - Default login: admin/admin

## Common Commands

### Start services
```bash
# Start all core services
docker-compose up -d

# Start with monitoring
docker-compose --profile monitoring up -d

# Start specific service
docker-compose up -d api
```

### Stop services
```bash
# Stop all
docker-compose down

# Stop and remove volumes (WARNING: deletes data!)
docker-compose down -v
```

### View logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f worker

# Last 100 lines
docker-compose logs --tail=100 api
```

### Restart services
```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart api
```

### Scale workers
```bash
# Run 3 workers
docker-compose up -d --scale worker=3
```

### Execute commands
```bash
# Run migrations
docker-compose exec api alembic upgrade head

# Run CLI command
docker-compose exec api python -m artomate.cli.main validate

# Access shell
docker-compose exec api bash

# Access Python REPL
docker-compose exec api python
```

## Configuration

### Environment Variables

Edit `.env` file:

```env
# Required
OPENAI_API_KEY=sk-...
PRINTIFY_API_TOKEN=...
PRINTIFY_SHOP_ID=...

# Optional
ETSY_API_KEY=...
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...

# Database (auto-configured in docker-compose)
DATABASE_URL=postgresql://artomate:password@db:5432/artomate
REDIS_URL=redis://redis:6379

# Logging
LOG_LEVEL=INFO
```

### Volumes

Data is persisted in Docker volumes:

```bash
# List volumes
docker volume ls | grep artomate

# Inspect volume
docker volume inspect artomate_postgres_data

# Backup volume
docker run --rm -v artomate_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres-backup.tar.gz /data
```

## Database Migrations

```bash
# Create migration
docker-compose exec api alembic revision --autogenerate -m "Description"

# Apply migrations
docker-compose exec api alembic upgrade head

# Rollback
docker-compose exec api alembic downgrade -1

# View history
docker-compose exec api alembic history
```

## Monitoring Setup

### Start with Prometheus & Grafana

```bash
docker-compose --profile monitoring up -d
```

### Access Prometheus

1. Open http://localhost:9090
2. Query metrics:
   - `artomate_jobs_created_total`
   - `artomate_jobs_completed_total`
   - `rate(artomate_api_requests_total[5m])`

### Access Grafana

1. Open http://localhost:3000
2. Login: admin/admin
3. Add Prometheus data source:
   - URL: http://prometheus:9090
4. Import dashboard (or create custom)

## Production Deployment

### Security Checklist

- [ ] Change database password in docker-compose.yml
- [ ] Use secrets for API keys (Docker Swarm or Kubernetes)
- [ ] Enable HTTPS (use reverse proxy like Nginx)
- [ ] Restrict CORS origins in API
- [ ] Use Docker secrets instead of .env file
- [ ] Enable firewall rules
- [ ] Regular backups of volumes

### Use PostgreSQL in Production

The default setup uses PostgreSQL. For SQLite instead:

1. Edit `docker-compose.yml`:
   ```yaml
   environment:
     - DATABASE_URL=sqlite:///data/artomate.db
   ```

2. Remove dependency on `db` service

### Nginx Reverse Proxy Example

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;  # UI
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    location /api {
        proxy_pass http://localhost:8000;  # API
    }

    location /health {
        proxy_pass http://localhost:8000;
    }
}
```

## Troubleshooting

### Container won't start

```bash
# Check logs
docker-compose logs api

# Check service status
docker-compose ps

# Restart service
docker-compose restart api
```

### Database connection errors

```bash
# Check if database is running
docker-compose ps db

# Check database logs
docker-compose logs db

# Test connection
docker-compose exec api python -c "from artomate.db.database import get_db; get_db()"
```

### Redis connection errors

```bash
# Check if Redis is running
docker-compose ps redis

# Test connection
docker-compose exec redis redis-cli ping
```

### Permission errors

```bash
# Fix volume permissions
docker-compose exec api chown -R root:root /app/data
```

### Out of disk space

```bash
# Clean up Docker
docker system prune -a --volumes

# Remove old images
docker image prune -a
```

## Development vs Production

### Development

```yaml
# docker-compose.override.yml (auto-loaded)
version: '3.8'

services:
  api:
    command: uvicorn artomate.api.main:app --reload --host 0.0.0.0
    volumes:
      - .:/app  # Mount source code for hot reload
```

### Production

```bash
# Use production compose file
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## Backup & Restore

### Backup

```bash
# Backup database
docker-compose exec db pg_dump -U artomate artomate > backup.sql

# Backup volumes
docker run --rm -v artomate_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/data-backup.tar.gz /data
```

### Restore

```bash
# Restore database
docker-compose exec -T db psql -U artomate artomate < backup.sql

# Restore volumes
docker run --rm -v artomate_postgres_data:/data -v $(pwd):/backup alpine tar xzf /backup/data-backup.tar.gz -C /
```

## Health Checks

```bash
# API health
curl http://localhost:8000/health

# Liveness (for k8s)
curl http://localhost:8000/health/liveness

# Readiness (for k8s)
curl http://localhost:8000/health/readiness

# Metrics
curl http://localhost:8000/metrics
```

## Performance Tuning

### Scale Workers

```bash
# Run multiple workers for parallel processing
docker-compose up -d --scale worker=5
```

### Resource Limits

```yaml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 512M
```

### Database Tuning

```yaml
services:
  db:
    command: postgres -c shared_buffers=256MB -c max_connections=200
```

## Updates

```bash
# Pull latest code
git pull

# Rebuild images
docker-compose build

# Restart with new images
docker-compose up -d

# Run migrations
docker-compose exec api alembic upgrade head
```
