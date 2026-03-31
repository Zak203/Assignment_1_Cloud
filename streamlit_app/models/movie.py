from dataclasses import dataclass, field
from typing import Optional
import re

LANGUAGE_MAP = {
    "en": "Anglais",
    "fr": "Français",
    "es": "Espagnol",
    "ja": "Japonais",
    "ko": "Coréen",
    "de": "Allemand",
    "it": "Italien",
    "pt": "Portugais",
    "zh": "Chinois",
    "ru": "Russe",
    "hi": "Hindi",
    "ar": "Arabe",
    "sv": "Suédois",
    "da": "Danois",
    "no": "Norvégien",
    "fi": "Finnois",
    "nl": "Néerlandais",
    "pl": "Polonais",
    "tr": "Turc",
    "th": "Thaï",
    "cs": "Tchèque",
    "hu": "Hongrois",
    "ro": "Roumain",
    "el": "Grec",
    "he": "Hébreu",
    "id": "Indonésien",
    "ms": "Malais",
    "vi": "Vietnamien",
    "uk": "Ukrainien",
    "fa": "Persan",
    "bn": "Bengali",
    "ta": "Tamoul",
    "te": "Télougou",
    "cn": "Cantonais",
    "la": "Latin",
    "xx": "Sans dialogues",
}


@dataclass
class Movie:
    title: str = "Sans titre"
    release_year: Optional[int] = None
    avg_rating: float = 0.0
    genres: str = ""
    language: str = "N/A"
    tmdb_id: Optional[int] = None

    @property
    def display_language(self) -> str:
        return LANGUAGE_MAP.get(self.language.lower(), self.language.upper())

    @property
    def genres_list(self) -> list:
        return [g.strip() for g in self.genres.split('|')] if self.genres else []

    @staticmethod
    def normalize_title(title: str) -> str:
        """Corrige les titres avec article rejeté à la fin: 'Animatrix, The (2003)' -> 'The Animatrix (2003)'"""
        match = re.match(
            r'^(.+),\s*(The|A|An|Le|La|Les|L\'|Un|Une|Des|Der|Die|Das|El|Los|Las)\b((?:\s*\([^)]*\))*)$',
            title, re.IGNORECASE
        )
        if match:
            base = match.group(1).strip()
            article = match.group(2)
            suffix = match.group(3)  # ex: " (2003)" ou " (Cma) (1980)"
            return f"{article} {base}{suffix}"
        return title

    @staticmethod
    def from_dict(data: dict) -> 'Movie':
        raw_title = data.get('title', 'Sans titre')
        return Movie(
            title=Movie.normalize_title(raw_title),
            release_year=data.get('release_year'),
            avg_rating=data.get('avg_rating', 0.0),
            genres=data.get('genres', ''),
            language=str(data.get('original_language') or data.get('language') or 'N/A'),
            tmdb_id=data.get('tmdbId'),
        )


@dataclass
class MovieDetail:
    title: str = "Titre inconnu"
    tagline: str = ""
    overview: str = "Aucune description disponible."
    poster_path: Optional[str] = None
    vote_average: float = 0.0
    vote_count: int = 0
    release_date: str = "N/A"
    runtime: Optional[int] = None
    budget: int = 0
    revenue: int = 0
    original_language: str = "N/A"
    genres: list = field(default_factory=list)

    @property
    def poster_url(self) -> Optional[str]:
        return f"https://image.tmdb.org/t/p/w500{self.poster_path}" if self.poster_path else None

    @property
    def genres_names(self) -> list:
        return [g['name'] for g in self.genres]

    @property
    def display_language(self) -> str:
        return LANGUAGE_MAP.get(self.original_language.lower(), self.original_language.upper())

    @staticmethod
    def from_dict(data: dict) -> 'MovieDetail':
        return MovieDetail(
            title=data.get('title', 'Titre inconnu'),
            tagline=data.get('tagline', ''),
            overview=data.get('overview', 'Aucune description disponible.'),
            poster_path=data.get('poster_path'),
            vote_average=data.get('vote_average', 0.0),
            vote_count=data.get('vote_count', 0),
            release_date=data.get('release_date', 'N/A'),
            runtime=data.get('runtime'),
            budget=data.get('budget', 0),
            revenue=data.get('revenue', 0),
            original_language=data.get('original_language', 'N/A'),
            genres=data.get('genres', []),
        )
