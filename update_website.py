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

# STORY ORDER (die echten Tage aus Obsidian)
STORY_DAYS = [
    ("2026_06_11_Morning_kakariko_On_the_Road_Through_Lost_Woods.md", "Tag 1", "On the Road", "lost woods"),
    ("2026_06_11_Noon_kakariko_Approaching_Kakariko.md", "Tag 1", "Approaching Kakariko", "kakariko approach"),
    ("2026_06_11_Evening_kakariko_First_Night_in_Kakariko.md", "Tag 1", "First Night", "first night"),
    ("2026_06_12_Morning_kakariko_Awakening_in_Kakariko.md", "Tag 2", "Awakening", "morning"),
    ("2026_06_12_Noon_kakariko_Bread,_Braids,_and_a_Name.md", "Tag 2", "Bread & Braids", "bakery"),
    ("2026_06_12_Evening_kakariko_First_Night_in_Kakariko.md", "Tag 2", "First Night v2", "evening"),
    ("2026_06_13_Morning_kakariko_Flour_Dust_and_Gratitude.md", "Tag 3", "Flour Dust", "bakery"),
    ("2026_06_13_Noon_kakariko_The_Bakery_and_the_Windmill_Path.md", "Tag 3", "Bakery Path", "windmill"),
    ("2026_06_13_Evening_kakariko_Dough_and_Determination.md", "Tag 3", "Dough", "evening"),
    ("2026_06_14_Morning_kakariko_Fourth_Morning.md", "Tag 4", "Fourth Morning", "morning"),
    ("2026_06_15_Morning_kakariko_Fifth_Morning_—_Bread_and_Belonging.md", "Tag 5", "Bread & Belonging", "morning"),
    ("2026_06_15_LateMorning_kakariko_Laundry_at_the_Creek.md", "Tag 5", "Laundry", "creek"),
    ("2026_06_16_Morning_kakariko_Sixth_Morning_—_The_Gift_of_Listening.md", "Tag 6", "Listening", "morning"),
    ("2026_06_16_Afternoon_kakariko_Ocarina_in_the_Mountains.md", "Tag 6", "Ocarina", "mountains"),
    ("2026_06_17_Morning_kakariko_Teaching_Lily_to_Listen.md", "Tag 7", "Teaching Lily", "morning"),
    ("2026_06_17_Noon_kakariko_The_Windmill's_Second_Lesson.md", "Tag 7", "Windmill", "noon"),
    ("2026_06_17_Evening_kakariko_The_Wisdom_Grows.md", "Tag 7", "Wisdom", "evening"),
]

def get_image_for_day(day_num):
    """Findet passendes Bild zum Tag"""
    day_folder = IMAGES_DIR / f"day{day_num}"
    if not day_folder.exists():
        day_folder = IMAGES_DIR / "misc"
    
    images = list(day_folder.glob("*.*"))
    if images:
        # Nimm das erste Bild das nicht test/crop drin hat
        for img in images:
            if "test" not in img.name.lower() and "crop" not in img.name.lower():
                return f"images/{day_folder.name}/{img.name}"
        return f"images/{day_folder.name}/{images[0].name}"
    return None

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
        image = get_image_for_day(day_num)
        
        entry = {
            "day": day,
            "day_num": day_num,
            "title_de": title_de,
            "title_en": title_de,  # TODO: echte Übersetzung
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