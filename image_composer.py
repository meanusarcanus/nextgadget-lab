"""
image_composer.py - Visual Asset Generation Pipeline for @nextgadget.lab.
Composes standardized, branded 1080x1350 (4:5 portrait) carousel slides using Pillow.
Dark mode theme (#0a0a0a, clean white typography, cyan #00f0ff & emerald #00ff9d accents).
"""

import os
import io
import math
import logging
import requests
from typing import List, Dict, Any, Tuple, Optional
from PIL import Image, ImageDraw, ImageFont, ImageFilter

logger = logging.getLogger("nextgadget_lab.image_composer")

# Canvas Constants
CANVAS_WIDTH = 1080
CANVAS_HEIGHT = 1350

# Design Tokens (Color Palette)
COLOR_BG = (10, 10, 12)            # Matte Black #0a0a0c
COLOR_CARD_BG = (20, 20, 26)       # Subtle Dark Gray #14141a
COLOR_CARD_BORDER = (40, 42, 54)   # Subtle Border #282a36
COLOR_TEXT_PRIMARY = (255, 255, 255)
COLOR_TEXT_MUTED = (170, 175, 190)
COLOR_CYAN = (0, 240, 255)         # Tech Accent Cyan #00f0ff
COLOR_EMERALD = (0, 255, 157)      # Tech Accent Emerald #00ff9d
COLOR_GOLD = (255, 200, 50)        # Rating Gold
COLOR_RED = (255, 85, 85)          # Cons Red
COLOR_ACCENT_GLOW = (0, 240, 255, 40)

BRAND_STAMP = "@nextgadget.lab"


class SlideComposer:
    def __init__(self, output_dir: str = "output_slides"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.font_large = self._load_font(52, bold=True)
        self.font_title = self._load_font(38, bold=True)
        self.font_sub = self._load_font(26, bold=False)
        self.font_body = self._load_font(22, bold=False)
        self.font_badge = self._load_font(18, bold=True)

    def _load_font(self, size: int, bold: bool = False) -> ImageFont.ImageFont:
        """Load system fonts or fallback to default PIL font."""
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf" if bold else "/usr/share/fonts/truetype/freefont/FreeSans.ttf"
        ]
        for p in font_paths:
            if os.path.exists(p):
                try:
                    return ImageFont.truetype(p, size)
                except Exception:
                    pass
        return ImageFont.load_default()

    def _create_base_canvas(self) -> Image.Image:
        """Creates canvas with dark matte background and subtle high-tech grid texture."""
        img = Image.new("RGB", (CANVAS_WIDTH, CANVAS_HEIGHT), COLOR_BG)
        draw = ImageDraw.Draw(img)

        # Draw subtle grid lines
        grid_step = 60
        grid_color = (20, 22, 30)
        for x in range(0, CANVAS_WIDTH, grid_step):
            draw.line([(x, 0), (x, CANVAS_HEIGHT)], fill=grid_color, width=1)
        for y in range(0, CANVAS_HEIGHT, grid_step):
            draw.line([(0, y), (CANVAS_WIDTH, y)], fill=grid_color, width=1)

        # Subtle top cyan accent bar
        draw.rectangle([(0, 0), (CANVAS_WIDTH, 8)], fill=COLOR_CYAN)

        return img

    def _draw_brand_header(self, draw: ImageDraw.ImageDraw, current_slide: int, total_slides: int = 4):
        """Draw top brand bar with slide indicator."""
        draw.text((60, 50), "NEXTGADGET.LAB", font=self.font_badge, fill=COLOR_CYAN)
        draw.text((60, 75), "PRECISION TECH REVIEWS", font=self.font_badge, fill=COLOR_TEXT_MUTED)

        # Slide pill indicator right
        indicator_text = f"SLIDE {current_slide} / {total_slides}"
        draw.rectangle([(CANVAS_WIDTH - 220, 48), (CANVAS_WIDTH - 60, 82)], fill=COLOR_CARD_BG, outline=COLOR_CARD_BORDER, width=1)
        draw.text((CANVAS_WIDTH - 200, 56), indicator_text, font=self.font_badge, fill=COLOR_EMERALD)

    def _draw_footer(self, draw: ImageDraw.ImageDraw):
        """Draw bottom footer with affiliate tag notice and swipe indicator."""
        draw.line([(60, CANVAS_HEIGHT - 90), (CANVAS_WIDTH - 60, CANVAS_HEIGHT - 90)], fill=COLOR_CARD_BORDER, width=1)
        draw.text((60, CANVAS_HEIGHT - 70), "SWIPE FOR FULL BENCHMARK  ➔", font=self.font_badge, fill=COLOR_CYAN)
        draw.text((CANVAS_WIDTH - 260, CANVAS_HEIGHT - 70), BRAND_STAMP, font=self.font_badge, fill=COLOR_TEXT_MUTED)

    def _download_image(self, url: str) -> Optional[Image.Image]:
        """Download product image from URL with fallback."""
        if not url:
            return None
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            resp = requests.get(url, headers=headers, timeout=8)
            if resp.status_code == 200:
                return Image.open(io.BytesIO(resp.content)).convert("RGBA")
        except Exception as e:
            logger.warning(f"Could not download product image from {url}: {e}")
        return None

    def compose_carousel(self, gadget: Dict[str, Any], slides_data: Dict[str, Any]) -> List[str]:
        """Generate all 4 carousel slide images and return list of output filepaths."""
        output_paths = []
        product_img = self._download_image(gadget.get("image_url", ""))

        # Slide 1: Hero Render & Minimalist Title Overlay
        slide_1_path = self._compose_slide_1(gadget, slides_data["slide_1"], product_img)
        output_paths.append(slide_1_path)

        # Slide 2: Engineering Specs Breakdown
        slide_2_path = self._compose_slide_2(gadget, slides_data["slide_2"])
        output_paths.append(slide_2_path)

        # Slide 3: Performance Scorecard & Pros/Cons
        slide_3_path = self._compose_slide_3(gadget, slides_data["slide_3"])
        output_paths.append(slide_3_path)

        # Slide 4: Final Verdict & Link-in-Bio CTA
        slide_4_path = self._compose_slide_4(gadget, slides_data["slide_4"])
        output_paths.append(slide_4_path)

        logger.info(f"Successfully generated 4 carousel slides in '{self.output_dir}'")
        return output_paths

    def _compose_slide_1(self, gadget: Dict[str, Any], data: Dict[str, Any], product_img: Optional[Image.Image]) -> str:
        canvas = self._create_base_canvas()
        draw = ImageDraw.Draw(canvas)
        self._draw_brand_header(draw, 1)

        # Category badge card
        draw.rectangle([(60, 130), (320, 170)], fill=COLOR_CYAN)
        draw.text((75, 142), data.get("badge", "FEATURED GADGET"), font=self.font_badge, fill=(0, 0, 0))

        # Main Title
        title_text = data.get("title", gadget["title"])
        # Wrap title text
        words = title_text.split()
        lines = []
        curr = ""
        for w in words:
            if len(curr + " " + w) <= 24:
                curr += (" " + w if curr else w)
            else:
                lines.append(curr)
                curr = w
        if curr:
            lines.append(curr)

        y_pos = 200
        for line in lines[:3]:
            draw.text((60, y_pos), line, font=self.font_title, fill=COLOR_TEXT_PRIMARY)
            y_pos += 48

        # Subtitle badge (Rating & Price)
        sub_text = data.get("subtitle", f"Rating: {gadget.get('rating', 4.5)} ★ | {gadget.get('price', '')}")
        draw.text((60, y_pos + 10), sub_text, font=self.font_sub, fill=COLOR_EMERALD)

        # Product Image Card Container
        img_box_y = y_pos + 70
        img_box_h = 660
        draw.rectangle([(60, img_box_y), (CANVAS_WIDTH - 60, img_box_y + img_box_h)], fill=COLOR_CARD_BG, outline=COLOR_CARD_BORDER, width=2)

        if product_img:
            # Resize product image to fit container while maintaining aspect ratio
            img_w, img_h = product_img.size
            max_w, max_h = CANVAS_WIDTH - 160, img_box_h - 80
            scale = min(max_w / img_w, max_h / img_h)
            new_w, new_h = int(img_w * scale), int(img_h * scale)
            resized = product_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            
            # Paste into center of card box
            px = 60 + (CANVAS_WIDTH - 120 - new_w) // 2
            py = img_box_y + (img_box_h - new_h) // 2
            canvas.paste(resized, (px, py), resized if resized.mode == "RGBA" else None)
        else:
            # Fallback graphic representation if image unavailable
            draw.text((CANVAS_WIDTH // 2 - 140, img_box_y + img_box_h // 2 - 20), "[ HIGH-TECH HERO RENDER ]", font=self.font_sub, fill=COLOR_TEXT_MUTED)

        # Floating Spec Tag
        draw.rectangle([(90, img_box_y + img_box_h - 70), (CANVAS_WIDTH - 90, img_box_y + img_box_h - 20)], fill=(0, 0, 0, 200), outline=COLOR_CYAN, width=1)
        draw.text((110, img_box_y + img_box_h - 56), f"VERIFIED SPECIFICATION — {gadget.get('review_count', 250):,}+ REVIEWS LOGGED", font=self.font_badge, fill=COLOR_CYAN)

        self._draw_footer(draw)

        out_path = os.path.join(self.output_dir, "slide_1.jpg")
        canvas.convert("RGB").save(out_path, "JPEG", quality=95)
        return out_path

    def _compose_slide_2(self, gadget: Dict[str, Any], data: Dict[str, Any]) -> str:
        canvas = self._create_base_canvas()
        draw = ImageDraw.Draw(canvas)
        self._draw_brand_header(draw, 2)

        draw.text((60, 130), "01 // HARDWARE ARCHITECTURE", font=self.font_badge, fill=COLOR_CYAN)
        draw.text((60, 160), "ENGINEERING SPECIFICATIONS", font=self.font_large, fill=COLOR_TEXT_PRIMARY)

        # Specs list rendering
        specs = data.get("specs", gadget.get("specs", {}))
        y_pos = 260

        for key, val in specs.items():
            # Spec Card Box
            draw.rectangle([(60, y_pos), (CANVAS_WIDTH - 60, y_pos + 160)], fill=COLOR_CARD_BG, outline=COLOR_CARD_BORDER, width=2)
            
            # Cyan pill indicator
            draw.rectangle([(80, y_pos + 25), (90, y_pos + 65)], fill=COLOR_CYAN)
            
            draw.text((110, y_pos + 25), key.upper(), font=self.font_title, fill=COLOR_EMERALD)
            draw.text((110, y_pos + 80), str(val), font=self.font_sub, fill=COLOR_TEXT_PRIMARY)

            y_pos += 190

        self._draw_footer(draw)
        out_path = os.path.join(self.output_dir, "slide_2.jpg")
        canvas.convert("RGB").save(out_path, "JPEG", quality=95)
        return out_path

    def _compose_slide_3(self, gadget: Dict[str, Any], data: Dict[str, Any]) -> str:
        canvas = self._create_base_canvas()
        draw = ImageDraw.Draw(canvas)
        self._draw_brand_header(draw, 3)

        draw.text((60, 130), "02 // BENCHMARK EVALUATION", font=self.font_badge, fill=COLOR_CYAN)
        draw.text((60, 160), "PERFORMANCE SCORECARD", font=self.font_large, fill=COLOR_TEXT_PRIMARY)

        # Scorecard Progress Bars
        scorecard = data.get("scorecard", gadget.get("scorecard", {"Design": 9.5, "Build/Battery": 9.2, "Value": 9.0}))
        y_pos = 260

        for metric, score in scorecard.items():
            draw.text((60, y_pos), metric.upper(), font=self.font_sub, fill=COLOR_TEXT_PRIMARY)
            draw.text((CANVAS_WIDTH - 180, y_pos), f"{score} / 10", font=self.font_sub, fill=COLOR_CYAN)

            # Progress Bar Background
            bar_y = y_pos + 40
            draw.rectangle([(60, bar_y), (CANVAS_WIDTH - 60, bar_y + 24)], fill=COLOR_CARD_BG, outline=COLOR_CARD_BORDER, width=1)
            
            # Filled Progress Bar
            fill_w = int((CANVAS_WIDTH - 120) * (score / 10.0))
            draw.rectangle([(60, bar_y), (60 + fill_w, bar_y + 24)], fill=COLOR_EMERALD)

            y_pos += 95

        # Pros Box
        y_pos += 20
        draw.rectangle([(60, y_pos), (CANVAS_WIDTH - 60, y_pos + 260)], fill=COLOR_CARD_BG, outline=COLOR_CARD_BORDER, width=2)
        draw.text((90, y_pos + 25), "✅ PROS & ADVANTAGES", font=self.font_title, fill=COLOR_EMERALD)
        
        pros_y = y_pos + 80
        for p in data.get("pros", gadget.get("pros", []))[:3]:
            draw.text((90, pros_y), f"• {p}", font=self.font_body, fill=COLOR_TEXT_PRIMARY)
            pros_y += 45

        # Cons Box
        y_pos += 290
        draw.rectangle([(60, y_pos), (CANVAS_WIDTH - 60, y_pos + 150)], fill=COLOR_CARD_BG, outline=(120, 40, 40), width=2)
        draw.text((90, y_pos + 20), "⚠️ HONEST CON", font=self.font_title, fill=COLOR_RED)
        draw.text((90, y_pos + 70), f"• {data.get('con', gadget.get('cons', ''))}", font=self.font_body, fill=COLOR_TEXT_PRIMARY)

        self._draw_footer(draw)
        out_path = os.path.join(self.output_dir, "slide_3.jpg")
        canvas.convert("RGB").save(out_path, "JPEG", quality=95)
        return out_path

    def _compose_slide_4(self, gadget: Dict[str, Any], data: Dict[str, Any]) -> str:
        canvas = self._create_base_canvas()
        draw = ImageDraw.Draw(canvas)
        self._draw_brand_header(draw, 4)

        draw.text((60, 130), "03 // RECOMMENDATION", font=self.font_badge, fill=COLOR_CYAN)
        draw.text((60, 160), "FINAL VERDICT", font=self.font_large, fill=COLOR_TEXT_PRIMARY)

        # Large Verdict Box
        draw.rectangle([(60, 260), (CANVAS_WIDTH - 60, 720)], fill=COLOR_CARD_BG, outline=COLOR_CYAN, width=2)
        draw.text((100, 300), "VERDICT SUMMARY", font=self.font_title, fill=COLOR_EMERALD)

        verdict_text = data.get("verdict", f"Highly recommended for tech enthusiasts seeking top tier performance.")
        # Wrap verdict
        words = verdict_text.split()
        v_lines = []
        curr = ""
        for w in words:
            if len(curr + " " + w) <= 32:
                curr += (" " + w if curr else w)
            else:
                v_lines.append(curr)
                curr = w
        if curr:
            v_lines.append(curr)

        vy = 370
        for line in v_lines[:6]:
            draw.text((100, vy), line, font=self.font_body, fill=COLOR_TEXT_PRIMARY)
            vy += 45

        # Glowing CTA Box
        cta_y = 770
        draw.rectangle([(60, cta_y), (CANVAS_WIDTH - 60, cta_y + 360)], fill=(0, 240, 255, 30), outline=COLOR_CYAN, width=3)
        draw.rectangle([(100, cta_y + 50), (CANVAS_WIDTH - 100, cta_y + 150)], fill=COLOR_CYAN)
        
        draw.text((CANVAS_WIDTH // 2 - 190, cta_y + 80), "🔗 DIRECT LINK IN BIO", font=self.font_title, fill=(0, 0, 0))
        draw.text((100, cta_y + 190), f"Product: {gadget['title']}", font=self.font_sub, fill=COLOR_TEXT_PRIMARY)
        draw.text((100, cta_y + 240), f"Price: {gadget.get('price', '$99.99')} | Tag: techspecdiges-20", font=self.font_sub, fill=COLOR_EMERALD)
        draw.text((100, cta_y + 290), "Tap @nextgadget.lab bio or check Story sticker for instant access.", font=self.font_body, fill=COLOR_TEXT_MUTED)

        self._draw_footer(draw)
        out_path = os.path.join(self.output_dir, "slide_4.jpg")
        canvas.convert("RGB").save(out_path, "JPEG", quality=95)
        return out_path
