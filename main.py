"""
main.py - Master Pipeline Orchestration Script for @nextgadget.lab.
Integrates Product Selection -> Copy Generation -> Image Composition -> IG Publishing -> Link-in-Bio Site Build.
"""

import os
import sys
import argparse
import logging
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

from database import GadgetDatabase
from amazon_scraper import AmazonIntelligenceEngine
from content_generator import CopywritingSynthesisAgent
from image_composer import SlideComposer
from instagram_publisher import InstagramPublisher
from bio_hub_generator import BioHubGenerator

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("nextgadget_lab.main")


def main():
    parser = argparse.ArgumentParser(description="Autonomous @nextgadget.lab Instagram Affiliate Review Pipeline")
    parser.add_argument("--dry-run", action="store_true", help="Execute pipeline in staging mode without live Instagram publish call")
    parser.add_argument("--asin", type=str, default=None, help="Target specific Amazon ASIN for review")
    parser.add_argument("--category", type=str, default=None, help="Filter selection by category (smart_home, productivity, edc_tech, audio_desk)")
    parser.add_argument("--skip-bio", action="store_true", help="Skip re-building Link-in-Bio static website")
    args = parser.parse_args()

    logger.info("=========================================================")
    logger.info("⚡ INITIATING @NEXTGADGET.LAB AUTOMATED REVIEW PIPELINE ⚡")
    logger.info("=========================================================")

    # 1. Initialize State Store (SQLite DB)
    db = GadgetDatabase("gadgets.db")

    # 2. Product Intelligence & Selection Engine
    engine = AmazonIntelligenceEngine(db=db)
    if args.asin:
        logger.info(f"Targeting specified ASIN: {args.asin}")
        gadget = engine.fetch_gadget_by_asin(args.asin)
        if not gadget:
            logger.error(f"Could not find gadget with ASIN {args.asin}")
            sys.exit(1)
    else:
        gadget = engine.select_next_trending_gadget(category_filter=args.category)

    logger.info(f"Selected Gadget: '{gadget['title']}' (ASIN: {gadget['asin']}, Category: {gadget.get('category')})")
    logger.info(f"Generated Affiliate Link: {gadget['affiliate_url']}")

    # 3. Content Copywriting Synthesis Agent
    copy_agent = CopywritingSynthesisAgent()
    content_payload = copy_agent.generate_content(gadget)
    logger.info("Generated Instagram Copy Payload & Slide Texts.")

    # 4. Visual Asset Generation Pipeline (1080x1350 Carousel Slides)
    composer = SlideComposer(output_dir=os.path.join("output_slides", gadget["asin"]))
    slide_filepaths = composer.compose_carousel(gadget, content_payload["slides_data"])
    logger.info(f"Generated {len(slide_filepaths)} 1080x1350 carousel slides.")

    # 5. Save gadget entry in Database state
    db.save_gadget(gadget)

    # 6. Autonomous Scheduling & Publishing / Staging
    publisher = InstagramPublisher()
    pub_result = publisher.publish_carousel(
        slide_filepaths=slide_filepaths,
        caption=content_payload["caption"],
        gadget=gadget,
        dry_run=args.dry_run
    )

    if pub_result["status"] == "PUBLISHED_LIVE":
        db.mark_gadget_published(gadget["asin"], container_id=pub_result.get("container_id"))
    
    db.record_post(
        asin=gadget["asin"],
        hook=content_payload["hook"],
        caption=content_payload["caption"],
        slides=slide_filepaths,
        status=pub_result["status"]
    )

    # 7. Update Dynamic Link-in-Bio Hub Static Site
    if not args.skip_bio:
        bio_generator = BioHubGenerator(db=db, output_dir="site")
        bio_site_path = bio_generator.build_site()
        logger.info(f"Link-in-Bio Hub Updated: {bio_site_path}")

    logger.info("=========================================================")
    logger.info("🎉 PIPELINE EXECUTION COMPLETED SUCCESSFULLY!")
    logger.info(f"• Target ASIN: {gadget['asin']}")
    logger.info(f"• Affiliate Tag: techspecdiges-20")
    logger.info(f"• Slides Generated: {len(slide_filepaths)} (1080x1350 px)")
    logger.info(f"• Publish Status: {pub_result['status']}")
    logger.info("=========================================================")


if __name__ == "__main__":
    main()
