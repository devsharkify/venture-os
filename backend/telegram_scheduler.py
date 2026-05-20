"""Scheduler for Telegram bot — sends morning (6 AM IST) and evening (6 PM IST) reports."""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from datetime import datetime, timezone, timedelta
from routes.telegram_bot import scheduled_morning, scheduled_evening, send_error_alert, tg_send, _get_admin_chat_id
from routes.seo_agent import generate_seo_telegram_report
from routes.tech_agent import generate_perf_telegram_report, generate_performance_report
from database import logger

def ist_now():
    return datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)

async def main():
    logger.info("Telegram scheduler started")

    while True:
        now = ist_now()
        hour, minute = now.hour, now.minute

        # 6:00 AM IST — Morning report
        if hour == 6 and minute == 0:
            logger.info("Sending morning report...")
            try:
                await scheduled_morning()
            except Exception as e:
                logger.error(f"Morning report failed: {e}")
                await send_error_alert(f"Morning report failed: {e}")

        # 18:00 (6 PM) IST — Evening report + SEO + Perf reports
        if hour == 18 and minute == 0:
            logger.info("Sending evening report...")
            try:
                await scheduled_evening()
            except Exception as e:
                logger.error(f"Evening report failed: {e}")
                await send_error_alert(f"Evening report failed: {e}")

            # Send SEO report at 6 PM
            try:
                chat_id = await _get_admin_chat_id()
                if chat_id:
                    seo_text = await generate_seo_telegram_report()
                    await tg_send(chat_id, seo_text)
            except Exception as e:
                logger.error(f"SEO report failed: {e}")

            # Send Tech performance report at 6 PM
            try:
                chat_id = await _get_admin_chat_id()
                if chat_id:
                    await generate_performance_report()
                    perf_text = await generate_perf_telegram_report()
                    await tg_send(chat_id, perf_text)
            except Exception as e:
                logger.error(f"Perf report failed: {e}")

        # Sleep until next minute
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())
