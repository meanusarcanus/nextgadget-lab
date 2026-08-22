"""
content_generator.py - Copywriting Synthesis Agent for @nextgadget.lab.
Generates structured Instagram copy & carousel slide payloads with technical precision.
"""

import os
import json
import logging
import requests
from typing import Dict, Any, List

logger = logging.getLogger("nextgadget_lab.content")


class CopywritingSynthesisAgent:
    def __init__(self, gemini_api_key: str = None, openai_api_key: str = None):
        self.gemini_api_key = gemini_api_key or os.getenv("GEMINI_API_KEY")
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")

    def generate_content(self, gadget: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point: Synthesizes full Instagram post payload & carousel slide contents.
        Uses LLM API if key is present, otherwise executes built-in high-tech copy synthesis engine.
        """
        if self.gemini_api_key:
            try:
                logger.info("Generating copy using Gemini API...")
                return self._generate_with_gemini(gadget)
            except Exception as e:
                logger.warning(f"Gemini API generation failed ({e}). Falling back to template synthesis engine.")

        return self._generate_structured_technical_copy(gadget)

    def _generate_structured_technical_copy(self, gadget: Dict[str, Any]) -> Dict[str, Any]:
        """Built-in high-precision technical copy generator tailored for @nextgadget.lab aesthetic."""
        title = gadget["title"]
        category = gadget.get("category", "Tech Gadget")
        rating = gadget.get("rating", 4.6)
        review_count = gadget.get("review_count", 500)
        price = gadget.get("price", "$99.99")
        specs = gadget.get("specs", {})
        pros = gadget.get("pros", [])
        cons = gadget.get("cons", "Slight learning curve for full feature customization.")
        scorecard = gadget.get("scorecard", {"Design": 9.5, "Build/Battery": 9.2, "Value": 9.0})
        affiliate_tag = os.getenv("AMAZON_AFFILIATE_TAG", "techspecdiges-20")

        # 1. Hook
        hook = f"⚡ TECH SPEC DIGEST: {title.upper()} — IS IT WORTH THE HYPER-DESK UPGRADE?"

        # 2. Specs formatting
        spec_bullets = []
        for k, v in specs.items():
            spec_bullets.append(f"• {k}: {v}")
        specs_str = "\n".join(spec_bullets)

        # 3. Pros / Cons formatting
        pros_str = "\n".join([f"✅ {p}" for p in pros])
        cons_str = f"⚠️ {cons}"

        # 4. Verdict
        verdict = f"VERDICT: Rated {rating}★ across {review_count:,}+ verified customer logs. A precision engineering choice for power users seeking high efficiency and clean desktop aesthetic."

        # 5. Call To Action (CTA)
        cta = f"🔗 DIRECT LINK & SPECS: Tap the link in our bio (@nextgadget.lab) or swipe to Story for instant access. (Tag: {affiliate_tag})"

        # 6. Hashtags
        hashtags = (
            "#NextGadgetLab #TechGadgets #DeskSetup #SmartHome #EDCTech "
            "#AmazonFinds #TechReview #MinimalistTech #FutureTech #TechSpec"
        )

        # Complete Instagram Caption
        caption = (
            f"{hook}\n\n"
            f"─── ENGINEERING HIGHLIGHTS ───\n"
            f"{specs_str}\n\n"
            f"─── REAL-WORLD PERFORMANCE ───\n"
            f"{pros_str}\n"
            f"{cons_str}\n\n"
            f"─── THE VERDICT ───\n"
            f"{verdict}\n\n"
            f"{cta}\n\n"
            f"{hashtags}"
        )

        # Structured Slide Contents for Image Composer (1080x1350)
        slides_data = {
            "slide_1": {
                "badge": f"FEATURED {category.upper()}",
                "title": title,
                "subtitle": f"Rating: {rating} ★ | {review_count:,}+ Reviews | {price}",
                "tagline": "SYSTEM ARCHITECTURE & IN-DEPTH REVIEW"
            },
            "slide_2": {
                "header": "ENGINEERING SPECS",
                "specs": specs
            },
            "slide_3": {
                "header": "PERFORMANCE SCORECARD",
                "scorecard": scorecard,
                "pros": pros[:2],
                "con": cons
            },
            "slide_4": {
                "header": "FINAL VERDICT",
                "verdict": verdict,
                "price": price,
                "cta_title": "LINK IN BIO",
                "cta_subtitle": "Tap @nextgadget.lab bio for direct affiliate discount"
            }
        }

        return {
            "hook": hook,
            "caption": caption,
            "slides_data": slides_data,
            "hashtags": hashtags
        }

    def _generate_with_gemini(self, gadget: Dict[str, Any]) -> Dict[str, Any]:
        """Calls Gemini API for dynamic high-tech copy synthesis."""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_api_key}"
        prompt = f"""
        Act as the head editor for @nextgadget.lab (a high-tech, minimalist Instagram gadget review account).
        Generate an engaging, precision technical review caption and carousel slide data for this gadget:
        {json.dumps(gadget, indent=2)}

        Response format MUST be valid JSON with keys: 'hook', 'caption', 'slides_data'.
        Return strictly raw JSON.
        """
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        res = requests.post(url, json=payload, timeout=15)
        if res.status_code == 200:
            text = res.json()["candidates"][0]["content"]["parts"][0]["text"]
            # Clean json fences if present
            cleaned = text.replace("```json", "").replace("```", "").strip()
            return json.loads(cleaned)
        else:
            raise RuntimeError(f"Gemini API returned status {res.status_code}")
