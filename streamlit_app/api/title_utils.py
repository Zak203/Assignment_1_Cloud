"""
Utilitaires pour la normalisation des titres de films.
Les titres dans la base de données ont les articles en suffixe :
  "Matrix, The"       -> "The Matrix"
  "Animatrix, The"    -> "The Animatrix"
  "400 Coups, Les"    -> "Les 400 Coups"

La fonction normalize_title convertit ce format en titre naturel.
La fonction db_title convertit l'inverse (titre naturel -> format base de données).
"""

import re

# Articles reconnus en fin de titre (EN, FR, ES, etc.)
_TRAILING_ARTICLES = [
    "The", "A", "An",           # Anglais
    "Le", "La", "Les", "L",     # Français
    "El", "Los", "Las", "Un",   # Espagnol
    "Die", "Das", "Der", "Ein", # Allemand
]

# Pattern : "Titre, Article (..."  ou  "Titre, Article"
_PATTERN = re.compile(
    r"^(.+?),\s+(" + "|".join(_TRAILING_ARTICLES) + r")(\s+\(.+\))?$"
)


def normalize_title(db_title: str) -> str:
    """
    Convertit un titre de la base de données en titre lisible.
    "Matrix, The (1999)"  ->  "The Matrix (1999)"
    "Matrix, The"         ->  "The Matrix"
    """
    m = _PATTERN.match(db_title)
    if m:
        main, article, suffix = m.group(1), m.group(2), m.group(3) or ""
        return f"{article} {main}{suffix}"
    return db_title


def db_title(display_title: str) -> str:
    """
    Convertit un titre lisible en format base de données.
    "The Matrix (1999)"  ->  "Matrix, The (1999)"
    "The Matrix"         ->  "Matrix, The"
    Utilisé pour retrouver la clé dans movies_dict après normalisation.
    """
    for article in _TRAILING_ARTICLES:
        prefix = article + " "
        if display_title.startswith(prefix):
            rest = display_title[len(prefix):]
            # Sépare le titre et l'année éventuelle entre parenthèses
            year_match = re.search(r"(\s+\(\d{4}\))$", rest)
            if year_match:
                core = rest[:year_match.start()]
                year = year_match.group(1)
                return f"{core}, {article}{year}"
            return f"{rest}, {article}"
    return display_title
