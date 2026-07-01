#!/usr/bin/env python3
"""Печатает список имён JPG для коллеги (public/cards/)."""

from app.domain.tarot_deck_seed import TAROT_CARDS_RIDER_WAITE

if __name__ == "__main__":
    for card in TAROT_CARDS_RIDER_WAITE:
        print(f"{card['code']}.jpg")
