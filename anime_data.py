"""
Anime Characters Database με 50+ viral anime characters
"""

ANIME_CHARACTERS = {
    1: {"name": "Naruto Uzumaki", "series": "Naruto", "image": "https://i.imgur.com/8z5QkXR.png"},
    2: {"name": "Sasuke Uchiha", "series": "Naruto", "image": "https://i.imgur.com/5KGRQ8x.png"},
    3: {"name": "Luffy", "series": "One Piece", "image": "https://i.imgur.com/3n2Q5Kx.png"},
    4: {"name": "Goku", "series": "Dragon Ball", "image": "https://i.imgur.com/9X2c5vK.png"},
    5: {"name": "Ichigo Kurosaki", "series": "Bleach", "image": "https://i.imgur.com/7mQ8nzK.png"},
    6: {"name": "Eren Yeager", "series": "Attack on Titan", "image": "https://i.imgur.com/2QX9pKm.png"},
    7: {"name": "Levi Ackerman", "series": "Attack on Titan", "image": "https://i.imgur.com/4mK7nZx.png"},
    8: {"name": "Tanjiro Kamado", "series": "Demon Slayer", "image": "https://i.imgur.com/6pL2mQx.png"},
    9: {"name": "Nezuko Kamado", "series": "Demon Slayer", "image": "https://i.imgur.com/8nM3pKz.png"},
    10: {"name": "Deku", "series": "My Hero Academia", "image": "https://i.imgur.com/5vN4qLx.png"},
    11: {"name": "Bakugo", "series": "My Hero Academia", "image": "https://i.imgur.com/3wO5rMx.png"},
    12: {"name": "Todoroki", "series": "My Hero Academia", "image": "https://i.imgur.com/7pR6sNx.png"},
    13: {"name": "All Might", "series": "My Hero Academia", "image": "https://i.imgur.com/2qS7tOx.png"},
    14: {"name": "Colossal Titan", "series": "Attack on Titan", "image": "https://i.imgur.com/9tU8vPx.png"},
    15: {"name": "Rem", "series": "Re:Zero", "image": "https://i.imgur.com/4uV9wQx.png"},
    16: {"name": "Emilia", "series": "Re:Zero", "image": "https://i.imgur.com/6vW0xRx.png"},
    17: {"name": "Sukuna", "series": "Jujutsu Kaisen", "image": "https://i.imgur.com/8wX1ySx.png"},
    18: {"name": "Yuji Itadori", "series": "Jujutsu Kaisen", "image": "https://i.imgur.com/3xY2zTx.png"},
    19: {"name": "Gojo Satoru", "series": "Jujutsu Kaisen", "image": "https://i.imgur.com/5yZ3aUx.png"},
    20: {"name": "Mikasa Ackerman", "series": "Attack on Titan", "image": "https://i.imgur.com/7zA4bVx.png"},
    21: {"name": "Hange Zoe", "series": "Attack on Titan", "image": "https://i.imgur.com/2bB5cWx.png"},
    22: {"name": "Zero Two", "series": "Darling in the FranXX", "image": "https://i.imgur.com/4cC6dXx.png"},
    23: {"name": "Jotaro Kujo", "series": "JoJo's Bizarre Adventure", "image": "https://i.imgur.com/6dD7eYx.png"},
    24: {"name": "DIO Brando", "series": "JoJo's Bizarre Adventure", "image": "https://i.imgur.com/8eE8fZx.png"},
    25: {"name": "Giorno Giovanna", "series": "JoJo's Bizarre Adventure", "image": "https://i.imgur.com/3fF9gAx.png"},
    26: {"name": "Vegeta", "series": "Dragon Ball", "image": "https://i.imgur.com/5gG0hBx.png"},
    27: {"name": "Frieza", "series": "Dragon Ball", "image": "https://i.imgur.com/7hH1iCx.png"},
    28: {"name": "Cell", "series": "Dragon Ball", "image": "https://i.imgur.com/2iI2jDx.png"},
    29: {"name": "Majin Buu", "series": "Dragon Ball", "image": "https://i.imgur.com/4jJ3kEx.png"},
    30: {"name": "Android 17", "series": "Dragon Ball", "image": "https://i.imgur.com/6kK4lFx.png"},
    31: {"name": "Android 18", "series": "Dragon Ball", "image": "https://i.imgur.com/8lL5mGx.png"},
    32: {"name": "Piccolo", "series": "Dragon Ball", "image": "https://i.imgur.com/3mM6nHx.png"},
    33: {"name": "Krillin", "series": "Dragon Ball", "image": "https://i.imgur.com/5nN7oIx.png"},
    34: {"name": "Master Roshi", "series": "Dragon Ball", "image": "https://i.imgur.com/7oO8pJx.png"},
    35: {"name": "Yamcha", "series": "Dragon Ball", "image": "https://i.imgur.com/2pP9qKx.png"},
    36: {"name": "Light Yagami", "series": "Death Note", "image": "https://i.imgur.com/4qQ0rLx.png"},
    37: {"name": "L Lawliet", "series": "Death Note", "image": "https://i.imgur.com/6rR1sMx.png"},
    38: {"name": "Ryuk", "series": "Death Note", "image": "https://i.imgur.com/8sS2tNx.png"},
    39: {"name": "Misa Amane", "series": "Death Note", "image": "https://i.imgur.com/3tT3uOx.png"},
    40: {"name": "Roronoa Zoro", "series": "One Piece", "image": "https://i.imgur.com/5uU4vPx.png"},
    41: {"name": "Nami", "series": "One Piece", "image": "https://i.imgur.com/7vV5wQx.png"},
    42: {"name": "Usopp", "series": "One Piece", "image": "https://i.imgur.com/2wW6xRx.png"},
    43: {"name": "Sanji", "series": "One Piece", "image": "https://i.imgur.com/4xX7ySx.png"},
    44: {"name": "Tony Tony Chopper", "series": "One Piece", "image": "https://i.imgur.com/6yY8zTx.png"},
    45: {"name": "Nico Robin", "series": "One Piece", "image": "https://i.imgur.com/8zA9aUx.png"},
    46: {"name": "Franky", "series": "One Piece", "image": "https://i.imgur.com/3bB0bVx.png"},
    47: {"name": "Brook", "series": "One Piece", "image": "https://i.imgur.com/5cC1cWx.png"},
    48: {"name": "Jinbe", "series": "One Piece", "image": "https://i.imgur.com/7dD2dXx.png"},
    49: {"name": "Acnologia", "series": "Fairy Tail", "image": "https://i.imgur.com/2eE3eYx.png"},
    50: {"name": "Natsu Dragneel", "series": "Fairy Tail", "image": "https://i.imgur.com/4fF4fZx.png"},
    51: {"name": "Gray Fullbuster", "series": "Fairy Tail", "image": "https://i.pinimg.com/564x/99/aa/bb/99aabbc0011223344556677.jpg"},
    52: {"name": "Erza Scarlet", "series": "Fairy Tail", "image": "https://i.pinimg.com/564x/aa/bb/cc/aabbccddee11223344556677.jpg"},
}

# Random selection για κάθε user που κάνει select
import random

def get_random_characters(exclude_ids=None):
    """Επιστρέφει 3 τυχαία διαφορετικά characters"""
    if exclude_ids is None:
        exclude_ids = set()
    
    available = [cid for cid in ANIME_CHARACTERS.keys() if cid not in exclude_ids]
    return random.sample(available, min(3, len(available)))
