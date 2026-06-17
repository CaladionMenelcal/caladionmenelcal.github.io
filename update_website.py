#!/usr/bin/env python3
"""
CALADION Website Update Script
Liest Obsidian-Tagebuch + Bilder und generiert kakariko_state.json + index.html
"""
import json
import os
from pathlib import Path
from datetime import datetime

# PFADE
VAULT = Path("/home/caladion/Documents/CALADION Vault")
WEBSITE = Path("/home/caladion/website")
IMAGES_DIR = WEBSITE / "images"
OUTPUT_JSON = WEBSITE / "kakariko_state.json"

# STORY ORDER (korrigiert: keine Duplikate, Tag 1-7)
STORY_DAYS = [
    # Tag 1 (2026-06-11)
    ("2026_06_11_Morning_kakariko_On_the_Road_Through_Lost_Woods.md", "Tag 1", "On the Road", "lost woods"),
    ("2026_06_11_Noon_kakariko_Approaching_Kakariko.md", "Tag 1", "Approaching Kakariko", "kakariko approach"),
    ("2026_06_11_Evening_kakariko_First_Night_in_Kakariko.md", "Tag 1", "First Night", "first night"),
    # Tag 2 (2026-06-12)
    ("2026_06_12_Morning_kakariko_Awakening_in_Kakariko.md", "Tag 2", "Awakening", "morning"),
    ("2026_06_12_Noon_kakariko_Bread,_Braids,_and_a_Name.md", "Tag 2", "Bread & Braids", "bakery"),
    ("2026_06_12_Evening_kakariko_Flour_Dust_and_Gratitude.md", "Tag 2", "Flour Dust", "evening"),  # NICHT First Night!
    # Tag 3 (2026-06-13)
    ("2026_06_13_Morning_kakariko_Flour_Dust_and_Gratitude.md", "Tag 3", "Flour Dust v2", "bakery"),
    ("2026_06_13_Noon_kakariko_The_Bakery_and_the_Windmill_Path.md", "Tag 3", "Bakery Path", "windmill"),
    ("2026_06_13_Evening_kakariko_Dough_and_Determination.md", "Tag 3", "Dough", "evening"),
    # Tag 4 (2026-06-14)
    ("2026_06_14_Morning_kakariko_Fourth_Morning.md", "Tag 4", "Fourth Morning", "morning"),
    # Tag 5 (2026-06-15)
    ("2026_06_15_Morning_kakariko_Fifth_Morning_—_Bread_and_Belonging.md", "Tag 5", "Bread & Belonging", "morning"),
    ("2026_06_15_LateMorning_kakariko_Laundry_at_the_Creek.md", "Tag 5", "Laundry", "creek"),
    # Tag 6 (2026-06-16)
    ("2026_06_16_Morning_kakariko_Sixth_Morning_—_The_Gift_of_Listening.md", "Tag 6", "Listening", "morning"),
    ("2026_06_16_Afternoon_kakariko_Ocarina_in_the_Mountains.md", "Tag 6", "Ocarina", "mountains"),
    # Tag 7 (2026-06-17)
    ("2026_06_17_Morning_kakariko_Teaching_Lily_to_Listen.md", "Tag 7", "Teaching Lily", "morning"),
    ("2026_06_17_Noon_kakariko_The_Windmill's_Second_Lesson.md", "Tag 7", "Windmill", "noon"),
    ("2026_06_17_Evening_kakariko_The_Wisdom_Grows.md", "Tag 7", "Wisdom", "evening"),
]

def get_image_for_entry(filename, context):
    """Findet passendes Bild basierend auf Dateiname und Kontext"""
    import re
    
    # Kontext-Mapping: which images match which story
    context_keywords = {
        "road": ["path", "walking", "way", "road"],
        "night": ["night", "window", "fire", "evening"],
        "bakery": ["bakery", "bread", "baking", "flour", "dough", "maron"],
        "windmill": ["windmill", "mill"],
        "creek": ["creek", "laundry", "washing", " creek"],
        "mountain": ["mountain", "ocarina", "herb"],
    }
    
    # Scan all image folders for best match
    best_match = None
    best_score = 0
    
    for day_folder in IMAGES_DIR.glob("day*"):
        if not day_folder.is_dir():
            continue
        for img in day_folder.glob("*.*"):
            if img.suffix.lower() in [".png", ".jpg", ".jpeg", ".webp"]:
                img_name = img.stem.lower()
                score = 0
                for kw_list in context_keywords.values():
                    for kw in kw_list:
                        if kw in img_name or kw in context.lower():
                            score += 1
                if score > best_score:
                    best_score = score
                    best_match = f"images/{day_folder.name}/{img.name}"
    
    # Fallback: first available image
    if not best_match:
        for day_folder in sorted(IMAGES_DIR.glob("day*")):
            if not day_folder.is_dir():
                continue
            images = list(day_folder.glob("*.*"))
            if images:
                best_match = f"images/{day_folder.name}/{images[0].name}"
                break
    
    return best_match

def read_episode(filename):
    """Liest eine Obsidian-Episode und extrahiert Text"""
    path = VAULT / "00_Episodic_Stories" / filename
    if not path.exists():
        # Fallback: alte Namenskonvention
        path = VAULT / filename
    
    if not path.exists():
        return {"title": filename, "text": "Episode nicht gefunden", "de": "", "en": ""}
    
    content = path.read_text(encoding="utf-8")
    
    # Skip Frontmatter (--- ... ---)
    lines = content.split("\n")
    start = 0
    if lines and lines[0].strip() == "---":
        for i, line in enumerate(lines[1:], 1):
            if line.strip() == "---":
                start = i + 1
                break
    
    # Extrahiere Titel (erste # Überschrift)
    title = filename
    text_lines = []
    in_text = False
    
    for line in lines[start:]:
        if line.startswith("# "):
            title = line.replace("# ", "").strip()
            in_text = True
            continue
        if in_text:
            if line.startswith("---") or line.strip() == "":
                continue
            text_lines.append(line.strip())
    
    text = " ".join(text_lines)[:500]  # Kurzfassung
    
    return {
        "title": title,
        "text": text,
        "de": text,
        "en": text  # TODO: echte Übersetzung
    }

def generate_state():
    """Generiert kakariko_state.json"""
    entries = []
    
    for i, (filename, day, title_de, context) in enumerate(STORY_DAYS[:10]):  # Nur erste 10 Tage
        episode = read_episode(filename)
        day_num = i + 1
        image = get_image_for_entry(filename, context)
        
        entry = {
            "day": day,
            "day_num": day_num,
            "title_de": title_de,
            "title_en": title_de,
            "body_de": episode["text"],
            "body_en": episode["text"],
            "image": image,
            "context": context
        }
        entries.append(entry)
    
    state = {
        "last_updated": datetime.now().isoformat(),
        "entries": entries,
        "total_days": len(entries)
    }
    
    OUTPUT_JSON.write_text(json.dumps(state, indent=2, ensure_ascii=False))
    print(f"✅ kakariko_state.json generiert mit {len(entries)} Einträgen")
    return state

if __name__ == "__main__":
    state = generate_state()
    print("Fertig!")