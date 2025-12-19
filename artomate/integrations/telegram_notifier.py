"""Telegram notification service for job status updates."""

import asyncio
from typing import Optional, Dict, Any
from datetime import datetime

from loguru import logger

from artomate.core.config import Config, get_config
from artomate.db.models import Job, JobState

# Lazy import to avoid dependency issues
try:
    from telegram import Bot
    from telegram.error import TelegramError
    TELEGRAM_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Telegram bot library not available: {e}")
    TELEGRAM_AVAILABLE = False
    Bot = None
    TelegramError = Exception


class TelegramNotifier:
    """Send notifications to Telegram when jobs complete/fail.

    Features:
    - Job completion notifications
    - Job failure notifications with error details
    - Rich formatting with emoji and statistics
    - Optional job summary with metrics

    Usage:
        notifier = TelegramNotifier()
        await notifier.notify_job_complete(job, results)
        await notifier.notify_job_failed(job, error)
    """

    def __init__(self, config: Optional[Config] = None):
        """Initialize Telegram notifier.

        Args:
            config: Application configuration
        """
        self.config = config or get_config()

        self.bot_token = self.config.telegram_bot_token
        self.chat_id = self.config.telegram_chat_id

        if not TELEGRAM_AVAILABLE:
            logger.warning("Telegram library not available. Notifications disabled.")
            self.bot = None
        elif not self.bot_token:
            logger.warning("Telegram bot token not configured. Notifications disabled.")
            self.bot = None
        else:
            self.bot = Bot(token=self.bot_token)

    def is_available(self) -> bool:
        """Check if Telegram notifications are available."""
        return self.bot is not None and self.chat_id is not None

    async def send_message(
        self,
        text: str,
        parse_mode: str = "Markdown",
    ) -> bool:
        """Send a message to Telegram.

        Args:
            text: Message text
            parse_mode: Parse mode (Markdown or HTML)

        Returns:
            True if sent successfully, False otherwise
        """
        if not self.is_available():
            logger.warning("Telegram not configured, skipping notification")
            return False

        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=text,
                parse_mode=parse_mode,
            )
            logger.info("✓ Sent Telegram notification")
            return True

        except TelegramError as e:
            logger.error(f"❌ Failed to send Telegram notification: {e}")
            return False

    async def notify_job_complete(
        self,
        job: Job,
        results: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Send notification when job completes successfully.

        Args:
            job: Completed job
            results: Job results dictionary

        Returns:
            True if sent successfully
        """
        if not results:
            results = {}

        # Calculate duration
        duration = "N/A"
        if job.started_at and job.completed_at:
            delta = job.completed_at - job.started_at
            minutes = int(delta.total_seconds() / 60)
            seconds = int(delta.total_seconds() % 60)
            duration = f"{minutes}m {seconds}s"

        # Build message
        message = f"""
✅ *Job Completed Successfully*

📋 *Job #{job.id}*
🎨 Theme: `{job.theme}`
🎭 Style: `{job.style}`
⏱ Duration: {duration}

📊 *Results:*
"""

        # Add statistics
        if "assets" in results:
            message += f"• Images: {len(results['assets'])}\n"
        if "products" in results:
            message += f"• Products: {len(results['products'])}\n"
        if "listings" in results:
            message += f"• Listings: {len(results['listings'])}\n"
        if "social_posts" in results:
            message += f"• Social Posts: {len(results['social_posts'])}\n"
        if "stock_submissions" in results:
            message += f"• Stock Submissions: {len(results['stock_submissions'])}\n"

        # Add timestamp
        message += f"\n🕐 Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        return await self.send_message(message)

    async def notify_job_failed(
        self,
        job: Job,
        error: str,
    ) -> bool:
        """Send notification when job fails.

        Args:
            job: Failed job
            error: Error message

        Returns:
            True if sent successfully
        """
        # Build message
        message = f"""
❌ *Job Failed*

📋 *Job #{job.id}*
🎨 Theme: `{job.theme}`
🎭 Style: `{job.style}`

⚠️ *Error:*
```
{error[:500]}
```

State when failed: `{job.state.value}`

🕐 Failed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

        return await self.send_message(message)

    async def notify_job_started(self, job: Job) -> bool:
        """Send notification when job starts.

        Args:
            job: Started job

        Returns:
            True if sent successfully
        """
        message = f"""
🚀 *Job Started*

📋 *Job #{job.id}*
🎨 Theme: `{job.theme}`
🎭 Style: `{job.style}`

🕐 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

        return await self.send_message(message)

    async def notify_job_progress(
        self,
        job: Job,
        step: str,
        progress: float,
    ) -> bool:
        """Send progress notification.

        Args:
            job: Job in progress
            step: Current step description
            progress: Progress percentage (0-1)

        Returns:
            True if sent successfully
        """
        progress_bar = self._create_progress_bar(progress)

        message = f"""
⏳ *Job Progress*

📋 *Job #{job.id}*
📍 Current step: {step}

{progress_bar} {int(progress * 100)}%
"""

        return await self.send_message(message)

    def _create_progress_bar(self, progress: float, length: int = 10) -> str:
        """Create a text-based progress bar.

        Args:
            progress: Progress (0-1)
            length: Bar length

        Returns:
            Progress bar string
        """
        filled = int(progress * length)
        bar = "█" * filled + "░" * (length - filled)
        return bar

    def notify_job_complete_sync(
        self,
        job: Job,
        results: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Synchronous wrapper for notify_job_complete.

        Args:
            job: Completed job
            results: Job results

        Returns:
            True if sent successfully
        """
        try:
            return asyncio.run(self.notify_job_complete(job, results))
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
            return False

    def notify_job_failed_sync(self, job: Job, error: str) -> bool:
        """Synchronous wrapper for notify_job_failed.

        Args:
            job: Failed job
            error: Error message

        Returns:
            True if sent successfully
        """
        try:
            return asyncio.run(self.notify_job_failed(job, error))
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
            return False

    def notify_job_started_sync(self, job: Job) -> bool:
        """Synchronous wrapper for notify_job_started.

        Args:
            job: Started job

        Returns:
            True if sent successfully
        """
        try:
            return asyncio.run(self.notify_job_started(job))
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
            return False


# Global notifier instance
_notifier: Optional[TelegramNotifier] = None


def get_telegram_notifier() -> TelegramNotifier:
    """Get or create global Telegram notifier instance."""
    global _notifier
    if _notifier is None:
        _notifier = TelegramNotifier()
    return _notifier


# Example usage:
# from artomate.integrations.telegram_notifier import get_telegram_notifier
#
# # Get notifier
# notifier = get_telegram_notifier()
#
# # Send notification (async)
# await notifier.notify_job_complete(job, results)
#
# # Send notification (sync)
# notifier.notify_job_complete_sync(job, results)
