#!/usr/bin/env python3
import os
import random
import sys
import tty
import termios
import json
import hashlib

BASE    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FR_DIR  = os.path.join(BASE, "transcripts_cleaned")
NL_DIR  = os.path.join(BASE, "transcripts_vertalingen")
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "seen.json")

RESET  = "\033[0m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
CYAN   = "\033[96m"
YELLOW = "\033[93m"
GREEN  = "\033[92m"
GRAY   = "\033[90m"
MAGENTA = "\033[95m"
WIDTH   = 64
SESSION = 35


def sentence_id(fr):
    return hashlib.md5(fr.encode()).hexdigest()


def load_db():
    if os.path.exists(DB_PATH):
        with open(DB_PATH, encoding="utf-8") as f:
            return set(json.load(f))
    return set()


def save_db(seen):
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(list(seen), f)


def load_pairs():
    pairs = []
    for filename in sorted(os.listdir(FR_DIR)):
        if not filename.endswith(".txt"):
            continue
        fr_path = os.path.join(FR_DIR, filename)
        nl_path = os.path.join(NL_DIR, filename)
        if not os.path.exists(nl_path):
            continue
        with open(fr_path, encoding="utf-8") as f:
            fr_lines = [s.strip() for s in f.read().split("\n\n") if s.strip()]
        with open(nl_path, encoding="utf-8") as f:
            nl_lines = [s.strip() for s in f.read().split("\n\n") if s.strip()]
        for fr, nl in zip(fr_lines, nl_lines):
            pairs.append((fr, nl, filename.replace(".txt", "")))
    return pairs


def getch():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
    return ch


def clear():
    print("\033[H\033[2J", end="")


def wrap_text(text, indent="  ", width=WIDTH):
    words = text.split()
    lines = []
    line = indent
    for word in words:
        if len(line) + len(word) + 1 > width + len(indent):
            lines.append(line.rstrip())
            line = indent + word + " "
        else:
            line += word + " "
    if line.strip():
        lines.append(line.rstrip())
    return lines


def draw(fr, nl, source, index, total, mode_label, mode_color):
    clear()
    print()
    print(f"  {BOLD}{CYAN}{'SHADOWING OEFENING':^{WIDTH}}{RESET}")
    print(f"  {DIM}{'─' * WIDTH}{RESET}")
    print()
    print(f"  {GRAY}Modus: {mode_color}{BOLD}{mode_label}{RESET}   {GRAY}│  Bron: {source[:WIDTH - 22]}{RESET}")
    print()
    print(f"  {BOLD}{YELLOW}Frans:{RESET}")
    print()
    for line in wrap_text(fr):
        print(f"  {BOLD}{line}{RESET}")
    print()
    print(f"  {DIM}{'─' * WIDTH}{RESET}")
    print()
    print(f"  {GREEN}Nederlands:{RESET}")
    print()
    for line in wrap_text(nl):
        print(f"  {line}")
    print()
    print(f"  {DIM}{'─' * WIDTH}{RESET}")
    print()
    print(f"  {GRAY}Zin {index}/{total}   •   {BOLD}[Enter]{RESET}{GRAY} volgende   {BOLD}[q]{RESET}{GRAY} stoppen{RESET}")
    print()


def draw_menu(total_new, total_seen):
    clear()
    print()
    print(f"  {BOLD}{CYAN}{'SHADOWING OEFENING':^{WIDTH}}{RESET}")
    print(f"  {DIM}{'─' * WIDTH}{RESET}")
    print()
    print(f"  Wat wil je oefenen?")
    print()
    print(f"  {BOLD}[1]{RESET}  {GREEN}Nieuwe zinnen{RESET}          {GRAY}({total_new} beschikbaar){RESET}")
    print(f"  {BOLD}[2]{RESET}  {MAGENTA}Al geziene zinnen{RESET}      {GRAY}({total_seen} beschikbaar){RESET}")
    print()
    print(f"  {DIM}{'─' * WIDTH}{RESET}")
    print()
    print(f"  {GRAY}{BOLD}[q]{RESET}{GRAY} afsluiten{RESET}")
    print()


def main():
    all_pairs = load_pairs()
    if not all_pairs:
        print("Geen zinnen gevonden. Controleer de mappen.")
        sys.exit(1)

    seen = load_db()

    new_pairs  = [(fr, nl, s) for fr, nl, s in all_pairs if sentence_id(fr) not in seen]
    seen_pairs = [(fr, nl, s) for fr, nl, s in all_pairs if sentence_id(fr) in seen]

    draw_menu(len(new_pairs), len(seen_pairs))

    while True:
        ch = getch()
        if ch == "1":
            if not new_pairs:
                clear()
                print(f"\n  {YELLOW}Geen nieuwe zinnen meer! Probeer modus 2.{RESET}\n")
                sys.exit(0)
            pairs = new_pairs
            mode_label = "Nieuwe zinnen"
            mode_color = GREEN
            break
        elif ch == "2":
            if not seen_pairs:
                clear()
                print(f"\n  {YELLOW}Nog geen zinnen gezien. Start met modus 1.{RESET}\n")
                sys.exit(0)
            pairs = seen_pairs
            mode_label = "Herhaling"
            mode_color = MAGENTA
            break
        elif ch in ("q", "Q", "\x03"):
            clear()
            sys.exit(0)

    random.shuffle(pairs)
    pairs = pairs[:SESSION]
    total = len(pairs)

    for i, (fr, nl, source) in enumerate(pairs, 1):
        draw(fr, nl, source, i, total, mode_label, mode_color)
        sid = sentence_id(fr)
        seen.add(sid)
        save_db(seen)

        while True:
            ch = getch()
            if ch in ("\r", "\n", " "):
                break
            if ch in ("q", "Q", "\x03"):
                clear()
                print(f"\n  {CYAN}Tot ziens! Je hebt {i} van de {total} zinnen geoefend.{RESET}\n")
                sys.exit(0)

    clear()
    print()
    print(f"  {BOLD}{GREEN}{'Goed gedaan!':^{WIDTH}}{RESET}")
    print()
    print(f"  {CYAN}Je hebt de {total} zinnen van vandaag afgerond.{RESET}")
    print(f"  {GRAY}Kom morgen terug voor de volgende sessie.{RESET}")
    print()


if __name__ == "__main__":
    main()
