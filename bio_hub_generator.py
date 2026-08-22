"""
bio_hub_generator.py - Dynamic Dark-Mode Link-In-Bio Website Generator.
Creates a self-updating static hub deployed to GitHub Pages / Cloudflare Pages / Vercel.
Renders high-tech glassmorphism UI displaying product cards with direct affiliate links.
"""

import os
import json
import logging
from typing import List, Dict, Any
from database import GadgetDatabase

logger = logging.getLogger("nextgadget_lab.bio_hub")


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>@nextgadget.lab — Tech Gadget Intelligence & Bio Hub</title>
    <meta name="description" content="Curated high-performance tech gadgets, EDC gear, desk setup upgrades, and smart home hardware reviewed by @nextgadget.lab.">
    
    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
    
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div class="background-grid"></div>
    <div class="radial-glow"></div>

    <main class="container">
        <!-- Header & Profile -->
        <header class="profile-header">
            <div class="avatar-ring">
                <div class="avatar-inner">⚡</div>
            </div>
            <h1 class="brand-title">@nextgadget.lab</h1>
            <p class="brand-subtitle">Curated High-Performance Tech & Desk Setup Benchmarks</p>
            <div class="tag-badge">AFFILIATE TAG ACTIVE: <span class="accent-tag">techspecdiges-20</span></div>
        </header>

        <!-- Stats Bar -->
        <section class="stats-bar">
            <div class="stat-item">
                <span class="stat-value" id="stat-count">0</span>
                <span class="stat-label">Reviewed Gadgets</span>
            </div>
            <div class="stat-divider"></div>
            <div class="stat-item">
                <span class="stat-value">4.6★+</span>
                <span class="stat-label">Min Rating Threshold</span>
            </div>
            <div class="stat-divider"></div>
            <div class="stat-item">
                <span class="stat-value">100%</span>
                <span class="stat-label">Verified Buyers</span>
            </div>
        </section>

        <!-- Search & Filter Controls -->
        <section class="filter-controls">
            <input type="text" id="search-input" placeholder="Search gadgets, specs, or models..." onkeyup="filterGadgets()">
            <div class="category-pills">
                <button class="pill active" onclick="setCategory('all', this)">All Hardware</button>
                <button class="pill" onclick="setCategory('Audio & Desk Setups', this)">Audio & Desk</button>
                <button class="pill" onclick="setCategory('Productivity Hardware', this)">Productivity</button>
                <button class="pill" onclick="setCategory('Smart Home', this)">Smart Home</button>
                <button class="pill" onclick="setCategory('EDC Tech', this)">EDC Tech</button>
            </div>
        </section>

        <!-- Gadgets Grid -->
        <section class="gadget-grid" id="gadget-grid">
            <!-- Rendered dynamically by JS -->
        </section>

        <!-- Footer -->
        <footer class="footer">
            <p>© 2026 @nextgadget.lab • As an Amazon Associate, we earn from qualifying purchases.</p>
        </footer>
    </main>

    <script>
        let allGadgets = __GADGETS_DATA__;

        document.getElementById('stat-count').innerText = allGadgets.length;

        let currentCategory = 'all';

        function renderGrid(items) {
            const grid = document.getElementById('gadget-grid');
            if (items.length === 0) {
                grid.innerHTML = `<div class="empty-state">No matching tech gadgets found.</div>`;
                return;
            }

            grid.innerHTML = items.map(item => `
                <div class="gadget-card" data-category="${item.category}">
                    <div class="card-image-wrapper">
                        <span class="category-badge">${item.category}</span>
                        <img src="${item.image_url || 'https://via.placeholder.com/400x300/14141a/00f0ff?text=NextGadget.Lab'}" alt="${item.title}" loading="lazy">
                        <span class="price-tag">${item.price || '$99.99'}</span>
                    </div>
                    <div class="card-content">
                        <div class="card-rating">
                            <span class="stars">★ ${item.rating}</span>
                            <span class="reviews">(${item.review_count ? item.review_count.toLocaleString() : 250}+ reviews)</span>
                        </div>
                        <h2 class="card-title">${item.title}</h2>
                        
                        <div class="specs-preview">
                            ${Object.entries(item.specs || {}).slice(0, 2).map(([k, v]) => `
                                <div class="spec-chip"><strong>${k}:</strong> ${v}</div>
                            `).join('')}
                        </div>

                        <a href="${item.affiliate_url}" target="_blank" rel="noopener sponsored" class="buy-button">
                            <span>GET ON AMAZON</span>
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="5" y1="12" x2="19" y2="12"></line><polyline points="12 5 19 12 12 19"></polyline></svg>
                        </a>
                    </div>
                </div>
            `).join('');
        }

        function filterGadgets() {
            const query = document.getElementById('search-input').value.toLowerCase();
            const filtered = allGadgets.filter(g => {
                const matchesCat = currentCategory === 'all' || g.category.toLowerCase() === currentCategory.toLowerCase();
                const matchesSearch = g.title.toLowerCase().includes(query) || JSON.stringify(g.specs || {}).toLowerCase().includes(query);
                return matchesCat && matchesSearch;
            });
            renderGrid(filtered);
        }

        function setCategory(cat, el) {
            currentCategory = cat;
            document.querySelectorAll('.pill').forEach(b => b.classList.remove('active'));
            el.classList.add('active');
            filterGadgets();
        }

        // Initial render
        renderGrid(allGadgets);
    </script>
</body>
</html>
"""

CSS_CONTENT = """/* Modern Glassmorphism & High-Tech Design System */
:root {
    --bg-color: #0a0a0d;
    --card-bg: rgba(20, 20, 26, 0.7);
    --card-border: rgba(42, 45, 60, 0.6);
    --text-primary: #ffffff;
    --text-muted: #a0a5b5;
    --cyan: #00f0ff;
    --emerald: #00ff9d;
    --gold: #ffc832;
    --font-main: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    --font-mono: 'JetBrains Mono', monospace;
}

* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

body {
    background-color: var(--bg-color);
    color: var(--text-primary);
    font-family: var(--font-main);
    min-height: 100vh;
    padding: 24px 16px;
    position: relative;
    overflow-x: hidden;
}

.background-grid {
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background-image: 
        linear-gradient(to right, rgba(255, 255, 255, 0.03) 1px, transparent 1px),
        linear-gradient(to bottom, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
    background-size: 40px 40px;
    z-index: -2;
}

.radial-glow {
    position: fixed;
    top: -100px;
    left: 50%;
    transform: translateX(-50%);
    width: 600px;
    height: 400px;
    background: radial-gradient(circle, rgba(0, 240, 255, 0.12) 0%, rgba(0,0,0,0) 70%);
    z-index: -1;
    pointer-events: none;
}

.container {
    max-width: 1000px;
    margin: 0 auto;
}

.profile-header {
    text-align: center;
    margin-bottom: 32px;
}

.avatar-ring {
    width: 80px;
    height: 80px;
    margin: 0 auto 16px;
    border-radius: 50%;
    padding: 3px;
    background: linear-gradient(135deg, var(--cyan), var(--emerald));
    box-shadow: 0 0 20px rgba(0, 240, 255, 0.4);
}

.avatar-inner {
    width: 100%;
    height: 100%;
    background: #0a0a0d;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 36px;
}

.brand-title {
    font-size: 28px;
    font-weight: 800;
    letter-spacing: -0.5px;
    background: linear-gradient(to right, #ffffff, var(--cyan));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 6px;
}

.brand-subtitle {
    color: var(--text-muted);
    font-size: 14px;
    margin-bottom: 12px;
}

.tag-badge {
    display: inline-block;
    background: rgba(0, 240, 255, 0.1);
    border: 1px solid var(--cyan);
    color: var(--text-muted);
    font-size: 11px;
    font-family: var(--font-mono);
    padding: 4px 12px;
    border-radius: 20px;
}

.accent-tag {
    color: var(--emerald);
    font-weight: 700;
}

.stats-bar {
    display: flex;
    align-items: center;
    justify-content: space-around;
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    backdrop-filter: blur(12px);
    border-radius: 16px;
    padding: 16px;
    margin-bottom: 32px;
}

.stat-item {
    text-align: center;
}

.stat-value {
    display: block;
    font-size: 20px;
    font-weight: 800;
    color: var(--cyan);
    font-family: var(--font-mono);
}

.stat-label {
    font-size: 11px;
    color: var(--text-muted);
    text-transform: uppercase;
}

.stat-divider {
    width: 1px;
    height: 28px;
    background: var(--card-border);
}

.filter-controls {
    margin-bottom: 32px;
}

#search-input {
    width: 100%;
    padding: 14px 18px;
    background: rgba(20, 20, 26, 0.9);
    border: 1px solid var(--card-border);
    border-radius: 12px;
    color: #fff;
    font-size: 15px;
    margin-bottom: 16px;
    outline: none;
    transition: all 0.2s ease;
}

#search-input:focus {
    border-color: var(--cyan);
    box-shadow: 0 0 12px rgba(0, 240, 255, 0.3);
}

.category-pills {
    display: flex;
    gap: 8px;
    overflow-x: auto;
    padding-bottom: 8px;
}

.pill {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid var(--card-border);
    color: var(--text-muted);
    padding: 8px 16px;
    border-radius: 20px;
    font-size: 13px;
    cursor: pointer;
    white-space: nowrap;
    transition: all 0.2s ease;
}

.pill.active, .pill:hover {
    background: var(--cyan);
    color: #000;
    border-color: var(--cyan);
    font-weight: 600;
}

.gadget-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 24px;
    margin-bottom: 48px;
}

.gadget-card {
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: 16px;
    overflow: hidden;
    backdrop-filter: blur(10px);
    transition: transform 0.25s ease, box-shadow 0.25s ease;
    display: flex;
    flex-direction: column;
}

.gadget-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 24px rgba(0, 240, 255, 0.15);
    border-color: var(--cyan);
}

.card-image-wrapper {
    position: relative;
    width: 100%;
    height: 220px;
    background: #14141a;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
}

.card-image-wrapper img {
    max-width: 85%;
    max-height: 85%;
    object-fit: contain;
    transition: transform 0.3s ease;
}

.gadget-card:hover .card-image-wrapper img {
    transform: scale(1.05);
}

.category-badge {
    position: absolute;
    top: 12px; left: 12px;
    background: rgba(0, 0, 0, 0.75);
    border: 1px solid var(--cyan);
    color: var(--cyan);
    font-size: 10px;
    font-weight: 700;
    padding: 3px 8px;
    border-radius: 6px;
    text-transform: uppercase;
}

.price-tag {
    position: absolute;
    bottom: 12px; right: 12px;
    background: var(--emerald);
    color: #000;
    font-weight: 800;
    font-size: 13px;
    padding: 4px 10px;
    border-radius: 8px;
    font-family: var(--font-mono);
}

.card-content {
    padding: 18px;
    display: flex;
    flex-direction: column;
    flex-grow: 1;
}

.card-rating {
    display: flex;
    align-items: center;
    gap: 6px;
    margin-bottom: 8px;
}

.stars {
    color: var(--gold);
    font-weight: 700;
    font-size: 14px;
}

.reviews {
    color: var(--text-muted);
    font-size: 12px;
}

.card-title {
    font-size: 16px;
    font-weight: 700;
    line-height: 1.3;
    margin-bottom: 12px;
    color: #fff;
}

.specs-preview {
    margin-bottom: 18px;
    flex-grow: 1;
}

.spec-chip {
    font-size: 12px;
    color: var(--text-muted);
    background: rgba(255, 255, 255, 0.03);
    padding: 4px 8px;
    border-radius: 6px;
    margin-bottom: 4px;
    border-left: 2px solid var(--cyan);
}

.buy-button {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    background: linear-gradient(135deg, var(--cyan), #00b8ff);
    color: #000;
    font-weight: 800;
    font-size: 14px;
    padding: 12px;
    border-radius: 10px;
    text-decoration: none;
    transition: all 0.2s ease;
}

.buy-button:hover {
    background: linear-gradient(135deg, var(--emerald), var(--cyan));
    box-shadow: 0 0 16px rgba(0, 255, 157, 0.4);
}

.footer {
    text-align: center;
    color: var(--text-muted);
    font-size: 12px;
    padding: 24px 0;
    border-top: 1px solid var(--card-border);
}
"""


class BioHubGenerator:
    def __init__(self, db: GadgetDatabase, output_dir: str = "site"):
        self.db = db
        self.output_dir = output_dir

    def build_site(self) -> str:
        """Fetch all processed gadgets from database and generate site assets."""
        os.makedirs(self.output_dir, exist_ok=True)
        
        gadgets = self.db.get_published_gadgets(limit=100)
        logger.info(f"Generating Link-in-Bio Hub for {len(gadgets)} reviewed gadgets...")

        # Write data.json
        data_path = os.path.join(self.output_dir, "data.json")
        with open(data_path, "w", encoding="utf-8") as f:
            json.dump(gadgets, f, indent=2)

        # Write styles.css
        css_path = os.path.join(self.output_dir, "styles.css")
        with open(css_path, "w", encoding="utf-8") as f:
            f.write(CSS_CONTENT)

        # Write index.html with embedded gadgets json
        html_path = os.path.join(self.output_dir, "index.html")
        html_rendered = HTML_TEMPLATE.replace("__GADGETS_DATA__", json.dumps(gadgets))
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_rendered)

        logger.info(f"🎉 Dynamic Bio Hub site built successfully in '{self.output_dir}/index.html'")
        return html_path
