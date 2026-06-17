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

def get_image_for_entry(filename, context, title_de):
    """Findet passendes Bild basierend auf title_de - MANUELL"""
    
    # MANUELLE ZUORDNUNG - which image for which story (mit Leerzeichen!)
    manual_mapping = {
        # Tag 1: Road/Approach/Night
        "On the Road": "images/day1/going up the way to kakariko.png",
        "Approaching Kakariko": "images/day1/arriving wind throughs cloth wrap away.png",
        "First Night": "images/day1/first_night_sitting_near_the_fire.jpg",
        # Tag 2: Bakery/Morning
        "Awakening": "images/day2/baking at the table.png",
        "Bread & Braids": "images/day2/maron_gives_bread.png",
        "Flour Dust": "images/day2/sifting flour at the counter.png",
        # Tag 3: Windmill
        "Flour Dust v2": "images/day3/in the windmill.png",
        "Bakery Path": "images/day3/perfect scene in the windmill.jpeg",
        "Dough": "images/day3/night moment.png",
        # Tag 4
        "Fourth Morning": "images/day4/at the creek washing.png",
        # Tag 5
        "Bread & Belonging": "images/day5/finding_my_ocarina.jpeg",
        "Laundry": "images/day4/at the creek washing.png",
        # Tag 6
        "Listening": "images/day5/in the mountains with ocarina.jpeg",
        "Ocarina": "images/day5/in the mountains with ocarina.jpeg",
        # Tag 7
        "Teaching Lily": "images/day6/balancing.png",
        "Windmill": "images/day3/perfect scene in the windmill.jpeg",
        "Wisdom": "images/day6/kellerfenster.png",
    }
    
    # Check title_de (the actual title from STORY_DAYS)
    for title_key, img_path in manual_mapping.items():
        if title_key == title_de:
            return img_path
    
    # Fallback
    return "images/day1/going_up_the_way_to_kakariko.png"

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
        image = get_image_for_entry(filename, context, title_de)
        
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