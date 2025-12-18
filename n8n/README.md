# n8n Integration

This directory contains example n8n workflows for orchestrating Artomate.

## Overview

**n8n's role:**
- Webhook routing (Telegram → Artomate)
- Cron scheduling (daily automation)
- Notifications (job status updates)
- Simple data transformations

**Python's role:**
- Core business logic
- Image generation
- Database operations
- Printify/Etsy APIs

## Setup

### 1. Install n8n

```bash
# Using npm
npm install -g n8n

# Or using Docker
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n
```

### 2. Start n8n

```bash
n8n start
```

Access at: http://localhost:5678

### 3. Import Workflows

In n8n UI:
1. Click "Workflows" → "Import from File"
2. Select workflows from `n8n/workflows/`
3. Configure credentials and webhook URLs

## Available Workflows

### 1. Telegram Bot → Create Job

**File:** `telegram-webhook.json`

**Flow:**
```
Telegram message → Parse command → HTTP Request (Artomate API) → Reply to Telegram
```

**Example usage:**
```
/create cat japandi wall-art
→ Creates job in Artomate
→ Replies: "✓ Created job 123"
```

### 2. Daily Automation

**File:** `daily-cron.json`

**Flow:**
```
Cron (3:00 AM) → HTTP Request (Artomate daily-cycle) → Wait for completion → Send notification
```

**Schedule:**
- Runs daily at 3:00 AM
- Creates 10 products
- Sends summary to Telegram

### 3. Job Status Monitor

**File:** `job-monitor.json`

**Flow:**
```
Polling (every 5 min) → Check job status → If changed → Send notification
```

**Monitors:**
- FAILED jobs → Alert
- DONE jobs → Success notification
- Stuck jobs (> 1 hour) → Warning

### 4. Webhook → Run Job

**File:** `webhook-run-job.json`

**Flow:**
```
Webhook trigger → Validate payload → HTTP Request (run job) → Return status
```

**Usage:**
```bash
curl -X POST http://localhost:5678/webhook/run-job \
  -H "Content-Type: application/json" \
  -d '{"job_id": 123}'
```

## Integration Patterns

### Pattern 1: n8n triggers Python

```
n8n (Cron/Webhook) → HTTP Request → Artomate CLI/API
```

Example:
```javascript
// n8n HTTP Request node
{
  "method": "POST",
  "url": "http://localhost:8000/api/jobs",
  "body": {
    "theme": "{{$json.theme}}",
    "style": "{{$json.style}}"
  }
}
```

### Pattern 2: Python notifies n8n

```
Artomate (job complete) → Webhook → n8n (send notification)
```

Example (Python):
```python
import requests

def notify_n8n(job_id: int, status: str):
    requests.post(
        "http://localhost:5678/webhook/artomate-status",
        json={"job_id": job_id, "status": status}
    )
```

### Pattern 3: Shared state (Redis)

```
n8n ← Redis → Artomate
```

Both read/write to shared Redis for coordination.

## Configuration

### Webhook URLs

Set in `.env`:

```bash
N8N_WEBHOOK_URL=http://localhost:5678/webhook/artomate
```

### Credentials

In n8n, configure:
- **Telegram Bot**: Bot token from @BotFather
- **HTTP Auth**: For Artomate API (if auth enabled)

## Common Workflows

### Create Job from Telegram

**User message:**
```
/create cat japandi wall-art
```

**n8n workflow:**
1. Telegram trigger receives message
2. Extract parameters using regex
3. Call Artomate API: `POST /api/jobs`
4. Reply to user with job ID

### Daily Product Generation

**n8n workflow:**
1. Cron triggers at 3:00 AM
2. HTTP Request: `POST /api/jobs/daily-cycle`
3. Python creates 10 jobs, processes them
4. Returns summary: `{"created": 10, "succeeded": 9, "failed": 1}`
5. Send Telegram notification

### Monitor & Alert

**n8n workflow:**
1. Interval trigger (every 5 minutes)
2. HTTP Request: `GET /api/jobs?state=failed`
3. If any failed jobs → Send alert
4. HTTP Request: `GET /api/jobs?state=stuck` (custom endpoint)
5. If any stuck jobs → Send warning

## Tips

1. **Use environment variables** in n8n for URLs/tokens
2. **Error handling**: Add "Error Trigger" nodes
3. **Rate limiting**: Space out API calls (Wait nodes)
4. **Idempotency**: Check job state before creating
5. **Logging**: Use Set nodes to log important data

## Troubleshooting

### Webhook not triggering

- Check n8n is running: http://localhost:5678
- Verify webhook URL in `.env`
- Check n8n execution log

### Jobs not creating

- Verify Artomate API is running
- Check API credentials
- Review n8n error output

### Telegram bot not responding

- Verify bot token in n8n credentials
- Check bot is started (@BotFather)
- Set webhook in Telegram: `/setWebhook`

## Next Steps

1. Import example workflows
2. Configure credentials
3. Test each workflow manually
4. Enable cron triggers
5. Monitor execution logs

## Advanced

### Custom Nodes

Create custom n8n nodes for Artomate:
- Artomate Job Create
- Artomate Job Run
- Artomate Export

### Workflow Templates

Share workflows:
- Export as JSON
- Commit to `n8n/workflows/`
- Document in this README

### Scaling

For production:
- Use n8n cloud or self-hosted with queue mode
- PostgreSQL backend for n8n
- Redis for distributed locking
