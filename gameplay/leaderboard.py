import json
import os
import datetime
import logging
from dataclasses import dataclass
from typing import List
from security.encryption import encrypt_data, decrypt_data
from core.paths import project_root  # optional


@dataclass
class ScoreEntry:
    name: str
    score: int
    level: int
    difficulty: str
    date: str = ""

    def to_dict(self):
        return self.__dict__

    @staticmethod
    def from_dict(data: dict):
        return ScoreEntry(
            name=data.get("name", "Unknown"),
            score=data.get("score", 0),
            level=data.get("level", 1),
            difficulty=data.get("difficulty", "NORMAL"),
            date=data.get("date", "")
        )


class Leaderboard:
    MAX_ENTRIES = 10
    FILENAME = os.path.join(project_root(), "data", "leaderboard.json")

    @staticmethod
    def load() -> List[ScoreEntry]:
        if not os.path.exists(Leaderboard.FILENAME):
            return []
        try:
            with open(Leaderboard.FILENAME, "rb") as f:
                encrypted_data = f.read()
            decrypted_json = decrypt_data(encrypted_data)
            data = json.loads(decrypted_json)
            return [ScoreEntry.from_dict(entry) for entry in data]
        except Exception as e:
            logging.warning(f"Failed to load leaderboard: {e}")
            return []

    @staticmethod
    def save(scores: List[ScoreEntry]):
        os.makedirs(os.path.dirname(Leaderboard.FILENAME), exist_ok=True)
        try:
            scores_json = json.dumps([s.to_dict() for s in scores], indent=2)
            encrypted_scores = encrypt_data(scores_json)
            with open(Leaderboard.FILENAME, "wb") as f:
                f.write(encrypted_scores)
        except Exception as e:
            logging.warning(f"Failed to save leaderboard: {e}")

    @staticmethod
    def add_score(name: str, score: int, level: int, difficulty: str) -> bool:
        scores = Leaderboard.load()
        entry = ScoreEntry(
            name=name,
            score=score,
            level=level,
            difficulty=difficulty,
            date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        )
        scores.append(entry)
        scores.sort(key=lambda x: x.score, reverse=True)
        scores = scores[:Leaderboard.MAX_ENTRIES]
        Leaderboard.save(scores)
        return entry in scores

    @staticmethod
    def get_top_scores() -> List[ScoreEntry]:
        scores = Leaderboard.load()
        return sorted(scores, key=lambda x: x.score, reverse=True)
