"""
Google Cloud Function to handle push notifications triggered by Pub/Sub events.

This function is triggered when a subscription is about to be charged.
It creates a notification in the notification service database and prepares
it for delivery to the frontend via SSE.
"""

import json
import logging
import os
import requests
from typing import Any, Dict
from google.cloud import pubsub_v1

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("notification-cloud-function")

# Get configuration from environment variables
NOTIFICATION_SERVICE_URL = os.environ.get(
    "NOTIFICATION_SERVICE_URL",
    "http://localhost:8000"  # Default for local testing
).rstrip("/")


def send_push_notification(event: Dict[str, Any], context: Any) -> None:
    """
    Cloud Function entry point triggered by Pub/Sub.
    
    Args:
        event: Pub/Sub event containing subscription due notification data
        context: Cloud Function context (unused but required)
    """
    try:
        # Decode Pub/Sub message
        if "data" in event:
            # Pub/Sub message format
            import base64
            message_data = base64.b64decode(event["data"]).decode("utf-8")
            payload = json.loads(message_data)
        else:
            # Direct JSON format (for testing)
            payload = event
        
        logger.info(f"Received Pub/Sub event: {json.dumps(payload)}")
        
        # Validate required fields
        required_fields = ["user_id", "subscription_id"]
        missing_fields = [field for field in required_fields if field not in payload]
        if missing_fields:
            raise ValueError(f"Missing required fields: {missing_fields}")
        
        # Extract payload data
        user_id = payload["user_id"]
        subscription_id = payload["subscription_id"]
        subscription_plan = payload.get("subscription_plan", "Subscription")
        billing_date = payload.get("billing_date", "")
        price = payload.get("price", "0.00")
        user_name = payload.get("user_name", "Subscriber")
        
        # Build notification payload
        notification_payload = {
            "user_id": user_id,
            "subscription_id": subscription_id,
            "subject": f"Upcoming Payment: {subscription_plan}",
            "body": (
                f"Hello {user_name},\n\n"
                f"Your subscription for {subscription_plan} is due on {billing_date}.\n"
                f"Amount: ${price}\n\n"
                "Please ensure your payment method is up to date."
            ),
            "notification_type": "push",
            "metadata": {
                "subscription_id": subscription_id,
                "user_id": user_id,
                "billing_date": billing_date,
                "price": price
            }
        }
        
        # Call notification service API to create notification
        notification_url = f"{NOTIFICATION_SERVICE_URL}/notifications"
        
        logger.info(f"Calling notification service: {notification_url}")
        
        response = requests.post(
            notification_url,
            json=notification_payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 201:
            notification_data = response.json()
            logger.info(
                f"Successfully created notification {notification_data.get('id')} "
                f"for user {user_id}, subscription {subscription_id}"
            )
        else:
            error_msg = f"Notification service returned {response.status_code}: {response.text}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
            
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Pub/Sub message: {str(e)}")
        raise
    except requests.RequestException as e:
        logger.error(f"Failed to call notification service: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in cloud function: {str(e)}")
        raise


# For local testing
if __name__ == "__main__":
    # Test event
    test_event = {
        "user_id": "test-user-123",
        "subscription_id": 1,
        "subscription_plan": "Netflix",
        "billing_date": "2024-01-15",
        "price": "15.99",
        "user_name": "Test User"
    }
    
    send_push_notification(test_event, None)

