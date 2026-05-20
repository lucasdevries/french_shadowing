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
BLUE   = "\033[34m"
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


def group_by_lesson(all_pairs):
    lessons = {}
    for fr, nl, source in all_pairs:
        lessons.setdefault(source, []).append((fr, nl, source))
    return [(source, lessons[source]) for source in sorted(lessons)]


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
    print(f"  {BOLD}{BLUE}Frans:{RESET}")
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


def draw_menu(total_new, total_seen, total_lessons):
    clear()
    print()
    print(f"  {BOLD}{CYAN}{'SHADOWING OEFENING':^{WIDTH}}{RESET}")
    print(f"  {DIM}{'─' * WIDTH}{RESET}")
    print()
    print(f"  Wat wil je oefenen?")
    print()
    print(f"  {BOLD}[1]{RESET}  {GREEN}Nieuwe zinnen{RESET}          {GRAY}({total_new} beschikbaar){RESET}")
    print(f"  {BOLD}[2]{RESET}  {MAGENTA}Al geziene zinnen{RESET}      {GRAY}({total_seen} beschikbaar){RESET}")
    print(f"  {BOLD}[3]{RESET}  {BLUE}Volledige les{RESET}          {GRAY}({total_lessons} lessen){RESET}")
    print()
    print(f"  {DIM}{'─' * WIDTH}{RESET}")
    print()
    print(f"  {GRAY}{BOLD}[q]{RESET}{GRAY} afsluiten{RESET}")
    print()


def draw_lesson_picker(lessons, seen):
    clear()
    print()
    print(f"  {BOLD}{BLUE}{'KIES EEN LES':^{WIDTH}}{RESET}")
    print(f"  {DIM}{'─' * WIDTH}{RESET}")
    print()
    for idx, (source, items) in enumerate(lessons, 1):
        done = sum(1 for fr, _, _ in items if sentence_id(fr) in seen)
        total = len(items)
        mark = f"{GREEN}✓{RESET}" if done == total else f"{GRAY}·{RESET}"
        title = source[:WIDTH - 14]
        print(f"  {BOLD}[{idx:>2}]{RESET} {mark}  {title} {GRAY}({done}/{total}){RESET}")
    print()
    print(f"  {DIM}{'─' * WIDTH}{RESET}")
    print()
    print(f"  {GRAY}Typ een nummer + {BOLD}[Enter]{RESET}{GRAY}   {BOLD}[q]{RESET}{GRAY} terug{RESET}")
    print()


def read_number(max_value):
    buf = ""
    while True:
        ch = getch()
        if ch in ("q", "Q", "\x03"):
            return None
        if ch in ("\r", "\n"):
            if buf and 1 <= int(buf) <= max_value:
                return int(buf)
            buf = ""
            sys.stdout.write("\r\033[K  > ")
            sys.stdout.flush()
            continue
        if ch == "\x7f":
            buf = buf[:-1]
        elif ch.isdigit():
            buf += ch
        sys.stdout.write(f"\r\033[K  > {buf}")
        sys.stdout.flush()


def main():
    all_pairs = load_pairs()
    if not all_pairs:
        print("Geen zinnen gevonden. Controleer de mappen.")
        sys.exit(1)

    seen = load_db()
    lessons = group_by_lesson(all_pairs)

    new_pairs  = [(fr, nl, s) for fr, nl, s in all_pairs if sentence_id(fr) not in seen]
    seen_pairs = [(fr, nl, s) for fr, nl, s in all_pairs if sentence_id(fr) in seen]

    draw_menu(len(new_pairs), len(seen_pairs), len(lessons))

    full_lesson = False
    while True:
        ch = getch()
        if ch == "1":
            if not new_pairs:
                clear()
                print(f"\n  {BLUE}Geen nieuwe zinnen meer! Probeer modus 2.{RESET}\n")
                sys.exit(0)
            pairs = list(new_pairs)
            random.shuffle(pairs)
            pairs = pairs[:SESSION]
            mode_label = "Nieuwe zinnen"
            mode_color = GREEN
            break
        elif ch == "2":
            if not seen_pairs:
                clear()
                print(f"\n  {BLUE}Nog geen zinnen gezien. Start met modus 1.{RESET}\n")
                sys.exit(0)
            pairs = list(seen_pairs)
            random.shuffle(pairs)
            pairs = pairs[:SESSION]
            mode_label = "Herhaling"
            mode_color = MAGENTA
            break
        elif ch == "3":
            draw_lesson_picker(lessons, seen)
            choice = read_number(len(lessons))
            if choice is None:
                draw_menu(len(new_pairs), len(seen_pairs), len(lessons))
                continue
            source, pairs = lessons[choice - 1]
            pairs = list(pairs)
            mode_label = f"Les: {source[:WIDTH - 12]}"
            mode_color = BLUE
            full_lesson = True
            break
        elif ch in ("q", "Q", "\x03"):
            clear()
            sys.exit(0)

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
    if full_lesson:
        print(f"  {CYAN}Je hebt de hele les ({total} zinnen) afgerond.{RESET}")
    else:
        print(f"  {CYAN}Je hebt de {total} zinnen van vandaag afgerond.{RESET}")
        print(f"  {GRAY}Kom morgen terug voor de volgende sessie.{RESET}")
    print()


if __name__ == "__main__":
    main()
