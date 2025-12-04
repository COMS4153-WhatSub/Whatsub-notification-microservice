# Push Notification Cloud Function

This Google Cloud Function is triggered by Pub/Sub events when a subscription is about to be charged. It creates a push notification in the notification service database.

## Deployment

### Prerequisites
- Google Cloud SDK installed
- Project ID set: `gcloud config set project YOUR_PROJECT_ID`
- Pub/Sub topic created: `subscription-due-notifications`

### Deploy the Function

```bash
gcloud functions deploy send-push-notification \
  --gen2 \
  --runtime=python311 \
  --region=us-central1 \
  --source=. \
  --entry-point=send_push_notification \
  --trigger-topic=subscription-due-notifications \
  --set-env-vars=NOTIFICATION_SERVICE_URL=http://YOUR_COMPUTE_ENGINE_IP:8000 \
  --timeout=60s \
  --memory=256MB
```

### Environment Variables
- `NOTIFICATION_SERVICE_URL`: URL of the notification service running on Compute Engine

### Testing Locally

```bash
python main.py
```

### Pub/Sub Message Format

```json
{
  "user_id": "uuid-string",
  "subscription_id": 123,
  "subscription_plan": "Netflix",
  "billing_date": "2024-01-15",
  "price": "15.99",
  "user_name": "John Doe"
}
```

