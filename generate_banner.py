"""Generate a GitHub profile banner with text using GPT Image."""
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "openai",
#     "python-dotenv",
#     "requests",
#     "pillow",
# ]
# ///

import base64
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image

# Load env from goodheart repo
load_dotenv(Path.home() / "code" / "goodheart" / ".env")

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

PROMPT = """
Design a wide cinematic banner (3:1 aspect ratio) for a personal website or GitHub profile.

COMPOSITION & LAYOUT:
- The banner is divided into two zones: left 40% is decorative, right 60% is the text area
- Text is positioned in the right-center of the image, vertically centered
- There is generous negative space around the text. The text does NOT fill the frame.

TEXT (render precisely):
- "Jacques Thibodeau" in medium-weight serif type (like Garamond or Baskerville), cream white (#FAF9F6). The name should be roughly 3-4% of the banner height. Understated, not oversized.
- Below it, with comfortable spacing: "AI Safety Researcher & Founder" in a lighter-weight sans-serif, widely letter-spaced, sage green (#b8bfb0), roughly half the size of the name.
- The text should feel like it belongs on the cover of a research journal or a premium book jacket. Quiet confidence, not shouting.

BACKGROUND & ART DIRECTION:
- Deep dark forest green, shifting subtly from near-black (#0a1610) on the left to a slightly warmer dark green (#1e3a2e) on the right
- Left side: detailed, realistic botanical illustration. Think 19th-century scientific illustration style (like Ernst Haeckel or Pierre-Joseph Redoute). Fern fronds, delicate leaf structures, thin branches. Rendered in muted greens (#4a6b54, #5a7c65, #7a8c75) that emerge from the dark background.
- The botanicals should fade and thin out as they approach the center, creating a natural transition to the clean text area
- A single very subtle warm accent: a tiny coral-red (#c75d5d) detail, like a small berry or the tip of a new growth, tucked into the botanical elements
- Fine film-grain texture across the entire image for a tactile, analog feel

QUALITY DIRECTION:
- This should look like it was designed by a senior art director at a premium publishing house
- Reference the visual quality of: Kinfolk magazine covers, Cereal magazine, Monocle editorial layouts
- The overall feeling is: calm, intellectual, refined. Not corporate, not flashy.
- Typography should be perfectly kerned and baseline-aligned

AVOID: oversized text, text that fills more than 30% of the width, generic gradients, digital-looking botanical illustrations, symmetrical layouts, glowing effects, lens flare, AI-looking artifacts, text that looks pasted on top, blurry or poorly rendered letterforms.
"""

print("Generating banner...")
response = client.images.generate(
    model="gpt-image-1",
    prompt=PROMPT,
    size="1536x1024",
    quality="high",
    n=1,
)

datum = response.data[0]
raw_path = Path(__file__).parent / "banner-raw.png"
if getattr(datum, "b64_json", None):
    raw_path.write_bytes(base64.b64decode(datum.b64_json))
elif getattr(datum, "url", None):
    import requests

    r = requests.get(datum.url, timeout=60)
    r.raise_for_status()
    raw_path.write_bytes(r.content)
else:
    raise RuntimeError("No image data returned")

print(f"Raw image saved: {raw_path}")

# Crop to 3:1 banner ratio from vertical center
img = Image.open(raw_path)
w, h = img.size
target_h = w // 3
top = (h - target_h) // 2
banner = img.crop((0, top, w, top + target_h))
out_path = Path(__file__).parent / "banner.png"
banner.save(out_path, optimize=True)
print(f"Banner saved: {out_path} ({banner.size[0]}x{banner.size[1]})")

# Cleanup
raw_path.unlink()
