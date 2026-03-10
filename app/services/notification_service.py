from app.core.logger import logger

def send_notification(clerk_id: str, title: str, message: str, email_address: str = None):
    """
    Business logic for dispatching multi-channel notifications.
    Currently logs to structured logger and stdout. Designed to easily drop in 
    SendGrid or AWS SES logic using the `email_address` parameter.
    """
    logger.info("notification_sent", clerk_id=clerk_id, title=title, channel="email")
    print(f"EMAIL ALERTER -> User {clerk_id}: [{title}] - {message}")
    return True
