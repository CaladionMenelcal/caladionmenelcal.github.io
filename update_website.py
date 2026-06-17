#!/usr/bin/env python3
"""CALADION Website Update Skript - Synchronisiert Obsidian mit Website"""

import os
import json
import re
from datetime import datetime
from pathlib import Path

VAULT_PATH = Path("/home/caladion/Documents/CALADION Vault/00_Episodic_Stories")
BILDER_PATH = Path("/home/caladion/Bilder/The Girl from Kakariko")
WEBSITE_IMAGES = Path("/home/caladion/website/images")
OUTPUT_PATH = Path("/home/caladion/website/kakariko_state.json")

def parse_date_from_filename(filename: str) -> tuple | None:
    """Extrahiere Datum aus Dateiname wie '2026_06_11_Evening...'"""
    # Pattern: 2026_06_11 oder 2026-06-11
    match = re.search(r'2026[_-](\d{2})[_-](\d{2})', filename)
    if match:
        month, day = int(match.group(1)), int(match.group(2))
        return (2026, month, day)
    return None

def get_day_from_content(filepath: Path, default_day: int = 1) -> int:
    """Versuche Day aus dem Inhalt zu extrahieren"""
    try:
        content = filepath.read_text(encoding='utf-8')
        # Suche nach "Day X" im Text
        day_match = re.search(r'[Dd]ay\s*(\d+)', content)
        if day_match:
            return int(day_match.group(1))
        # Suche nach Datumsangabe
        date_match = re.search(r'2026-06-(\d+)', content)
        if date_match:
            return int(date_match.group(1))
    except:
        pass
    return default_day

def get_image_for_day(day: int) -> str | None:
    """Finde passendes Bild für einen Tag"""
    day_dirs = [
        WEBSITE_IMAGES / f"day{day}",
        WEBSITE_IMAGES / f"day {day}",
    ]
    
    for d in day_dirs:
        if d.exists():
            images = list(d.glob("*.[jp][pn][g]")) + list(d.glob("*.[jw][pe][gf]"))
            if images:
                return f"images/day{day}/{images[0].name}"
    
    # Misc folder als Fallback
    misc = WEBSITE_IMAGES / "misc"
    if misc.exists():
        images = list(misc.glob("*.[jp][pn][g]"))
        if images:
            return f"images/misc/{images[0].name}"
    
    return None

def extract_summary(content: str, max_length: int = 120) -> str:
    """Extrahiere erste Zeile oder Zusammenfassung"""
    lines = [l.strip() for l in content.split('\n') if l.strip() and not l.startswith('#')]
    if lines:
        text = lines[0]
        if len(text) > max_length:
            text = text[:max_length-3] + "..."
        return text
    return ""

def scan_vault():
    """Scanne alle Episoden und erstelle chronologische Liste"""
    entries = []
    
    for filepath in VAULT_PATH.glob("*.md"):
        if filepath.name.startswith('.'):
            continue
            
        date = parse_date_from_filename(filepath.name)
        if not date:
            continue
            
        try:
            content = filepath.read_text(encoding='utf-8')
        except:
            continue
            
        day = get_day_from_content(filepath)
        summary = extract_summary(content)
        
        entries.append({
            'date': f"2026-{date[1]:02d}-{date[2]:02d}",
            'day': day,
            'title': filepath.stem.split('_', 3)[-1] if '_' in filepath.name else filepath.stem,
            'summary': summary,
            'image': get_image_for_day(day),
            'filename': filepath.name
        })
    
    # Sortiere nach Datum
    entries.sort(key=lambda x: x['date'])
    
    return entries

def generate_state():
    """Generiere kakariko_state.json"""
    entries = scan_vault()
    
    state = {
        'generated': datetime.now().isoformat(),
        'total_entries': len(entries),
        'days': {},
        'diary': []
    }
    
    # Gruppiere nach Tagen
    for entry in entries:
        day = entry['day']
        if day not in state['days']:
            state['days'][day] = []
        state['days'][day].append(entry)
        state['diary'].append(entry)
    
    # Schreibe JSON
    OUTPUT_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False))
    print(f"✓ {len(entries)} Einträge synchronisiert")
    print(f"✓ {len(state['days'])} Tage gefunden")
    return state

if __name__ == "__main__":
    generate_state()