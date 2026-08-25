"""
instagram_publisher.py - Autonomous Publishing & Staging Agent for @nextgadget.lab.
Supports direct Instagram Graph API carousel publishing, public CDN image uploading,
and Webhook / Staging fallback modes (Discord / Telegram / Local Output).
"""

import os
import json
import time
import logging
import requests
from typing import List, Dict, Any, Optional

logger = logging.getLogger("nextgadget_lab.publisher")


class InstagramPublisher:
    def __init__(
        self,
        account_id: Optional[str] = None,
        access_token: Optional[str] = None,
        imgbb_key: Optional[str] = None,
        discord_webhook: Optional[str] = None,
        telegram_token: Optional[str] = None,
        telegram_chat_id: Optional[str] = None
    ):
        self.account_id = account_id or os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID")
        self.access_token = access_token or os.getenv("INSTAGRAM_ACCESS_TOKEN")
        self.imgbb_key = imgbb_key or os.getenv("IMGBB_API_KEY")
        self.discord_webhook = discord_webhook or os.getenv("DISCORD_WEBHOOK_URL")
        self.telegram_token = telegram_token or os.getenv("TELEGRAM_BOT_TOKEN")
        self.telegram_chat_id = telegram_chat_id or os.getenv("TELEGRAM_CHAT_ID")
        self.graph_url = "https://graph.facebook.com/v18.0"

    def publish_carousel(
        self,
        slide_filepaths: List[str],
        caption: str,
        gadget: Dict[str, Any],
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Main entrypoint to publish or stage carousel post.
        1. If dry_run or missing Graph API credentials -> execute Staging / Webhook Mode.
        2. Else -> Upload images to CDN -> Create Graph API Media Containers -> Publish.
        """
        logger.info(f"Initiating publication workflow for gadget ASIN {gadget['asin']} ({len(slide_filepaths)} slides)...")

        # Staging / Dry Run Mode Check
        if dry_run or not self.account_id or not self.access_token:
            logger.info("⚡ Executing in STAGING / DRY-RUN mode (No live Meta API publish call executed).")
            return self._execute_staging_publish(slide_filepaths, caption, gadget)

        try:
            return self._execute_graph_api_publish(slide_filepaths, caption, gadget)
        except Exception as e:
            logger.error(f"Meta Graph API publication failed: {e}. Executing fallback staging output.")
            return self._execute_staging_publish(slide_filepaths, caption, gadget)

    def _upload_image_to_cdn(self, filepath: str) -> str:
        """Upload local image file to ImgBB CDN to get public URL required by Meta API."""
        if not self.imgbb_key:
            raise ValueError("IMGBB_API_KEY environment variable is required to host images for Meta API upload.")

        with open(filepath, "rb") as file:
            url = "https://api.imgbb.com/1/upload"
            payload = {"key": self.imgbb_key}
            files = {"image": file}
            resp = requests.post(url, data=payload, files=files, timeout=20)
            if resp.status_code == 200:
                public_url = resp.json()["data"]["url"]
                logger.info(f"Uploaded slide to CDN: {public_url}")
                return public_url
            else:
                raise RuntimeError(f"ImgBB CDN upload failed: {resp.text}")

    def _execute_graph_api_publish(self, slide_filepaths: List[str], caption: str, gadget: Dict[str, Any]) -> Dict[str, Any]:
        """Uploads slides and calls Meta Graph API endpoints (/media & /media_publish)."""
        logger.info("Uploading slide assets to public CDN for Meta Graph API...")
        public_image_urls = [self._upload_image_to_cdn(fp) for fp in slide_filepaths]

        # Step 1: Create individual item containers
        child_container_ids = []
        for idx, img_url in enumerate(public_image_urls):
            url = f"{self.graph_url}/{self.account_id}/media"
            params = {
                "image_url": img_url,
                "is_carousel_item": "true",
                "access_token": self.access_token
            }
            res = requests.post(url, params=params, timeout=15)
            data = res.json()
            if "id" not in data:
                raise RuntimeError(f"Failed creating slide container {idx+1}: {data}")
            container_id = data["id"]
            child_container_ids.append(container_id)
            logger.info(f"Created carousel item container {idx+1}/4: {container_id}")

        # Step 2: Create parent Carousel container
        url = f"{self.graph_url}/{self.account_id}/media"
        params = {
            "media_type": "CAROUSEL",
            "children": ",".join(child_container_ids),
            "caption": caption,
            "access_token": self.access_token
        }
        res = requests.post(url, params=params, timeout=15)
        carousel_data = res.json()
        if "id" not in carousel_data:
            raise RuntimeError(f"Failed creating parent carousel container: {carousel_data}")
        carousel_container_id = carousel_data["id"]
        logger.info(f"Created parent Carousel container: {carousel_container_id}")

        # Wait briefly for Meta server processing
        time.sleep(5)

        # Step 3: Publish container
        pub_url = f"{self.graph_url}/{self.account_id}/media_publish"
        pub_params = {
            "creation_id": carousel_container_id,
            "access_token": self.access_token
        }
        pub_res = requests.post(pub_url, params=pub_params, timeout=20)
        pub_data = pub_res.json()
        if "id" not in pub_data:
            raise RuntimeError(f"Failed publishing carousel container: {pub_data}")

        published_post_id = pub_data["id"]
        logger.info(f"🎉 SUCCESS! Carousel published live on Instagram! Post ID: {published_post_id}")

        return {
            "status": "PUBLISHED_LIVE",
            "post_id": published_post_id,
            "container_id": carousel_container_id,
            "gadget_asin": gadget["asin"]
        }

    def _execute_staging_publish(self, slide_filepaths: List[str], caption: str, gadget: Dict[str, Any]) -> Dict[str, Any]:
        """Save post payload locally and optionally send Webhook notifications."""
        staging_dir = "output_posts"
        os.makedirs(staging_dir, exist_ok=True)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        post_filename = f"post_{gadget['asin']}_{timestamp}.json"
        post_path = os.path.join(staging_dir, post_filename)

        record = {
            "timestamp": timestamp,
            "gadget_asin": gadget["asin"],
            "title": gadget["title"],
            "affiliate_url": gadget["affiliate_url"],
            "caption": caption,
            "slides": slide_filepaths,
            "status": "STAGED_READY_TO_POST"
        }

        with open(post_path, "w", encoding="utf-8") as f:
            json.dump(record, f, indent=2)

        logger.info(f"Saved staged post artifact to '{post_path}'.")

        # Optional Webhook Notifications (Discord / Telegram)
        if self.discord_webhook:
            self._send_discord_notification(gadget, caption, slide_filepaths)

        if self.telegram_token and self.telegram_chat_id:
            self._send_telegram_notification(gadget, caption)

        return {
            "status": "STAGED_SUCCESS",
            "post_artifact": post_path,
            "gadget_asin": gadget["asin"]
        }

    def _send_discord_notification(self, gadget: Dict[str, Any], caption: str, slide_filepaths: List[str]):
        """Send notification to Discord webhook with post copy."""
        try:
            payload = {
                "username": "NextGadget.Lab Bot",
                "avatar_url": "https://m.media-amazon.com/images/I/61k3p+M6Y8L._AC_SL1500_.jpg",
                "embeds": [
                    {
                        "title": f"⚡ NEW INSTAGRAM POST READY: {gadget['title']}",
                        "description": caption[:1900],
                        "color": 61439,  # Cyan
                        "fields": [
                            {"name": "Affiliate Link", "value": gadget["affiliate_url"], "inline": False},
                            {"name": "Slide Count", "value": f"{len(slide_filepaths)} 1080x1350 Carousel Images Generated", "inline": True}
                        ],
                        "footer": {"text": "@nextgadget.lab • Tag: techspecdiges-20"}
                    }
                ]
            }
            requests.post(self.discord_webhook, json=payload, timeout=10)
            logger.info("Sent notification to Discord Webhook.")
        except Exception as e:
            logger.warning(f"Could not send Discord webhook: {e}")

    def _send_telegram_notification(self, gadget: Dict[str, Any], caption: str):
        """Send notification to Telegram Chat."""
        try:
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            text = f"⚡ <b>NEXTGADGET.LAB POST READY</b>\n\n{caption}\n\n<b>Affiliate Link:</b> {gadget['affiliate_url']}"
            payload = {
                "chat_id": self.telegram_chat_id,
                "text": text,
                "parse_mode": "HTML"
            }
            requests.post(url, json=payload, timeout=10)
            logger.info("Sent notification to Telegram Chat.")
        except Exception as e:
            logger.warning(f"Could not send Telegram notification: {e}")
