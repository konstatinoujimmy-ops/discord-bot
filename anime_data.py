"""
Anime Characters Database με 50+ viral anime characters
"""

ANIME_CHARACTERS = {
    1: {"name": "Naruto Uzumaki", "series": "Naruto", "image": "https://via.placeholder.com/200?text=Naruto"},
    2: {"name": "Sasuke Uchiha", "series": "Naruto", "image": "https://via.placeholder.com/200?text=Sasuke"},
    3: {"name": "Luffy", "series": "One Piece", "image": "https://via.placeholder.com/200?text=Luffy"},
    4: {"name": "Goku", "series": "Dragon Ball", "image": "https://via.placeholder.com/200?text=Goku"},
    5: {"name": "Ichigo Kurosaki", "series": "Bleach", "image": "https://via.placeholder.com/200?text=Ichigo"},
    6: {"name": "Eren Yeager", "series": "Attack on Titan", "image": "https://via.placeholder.com/200?text=Eren"},
    7: {"name": "Levi Ackerman", "series": "Attack on Titan", "image": "https://via.placeholder.com/200?text=Levi"},
    8: {"name": "Tanjiro Kamado", "series": "Demon Slayer", "image": "https://via.placeholder.com/200?text=Tanjiro"},
    9: {"name": "Nezuko Kamado", "series": "Demon Slayer", "image": "https://via.placeholder.com/200?text=Nezuko"},
    10: {"name": "Deku", "series": "My Hero Academia", "image": "https://via.placeholder.com/200?text=Deku"},
    11: {"name": "Bakugo", "series": "My Hero Academia", "image": "https://via.placeholder.com/200?text=Bakugo"},
    12: {"name": "Todoroki", "series": "My Hero Academia", "image": "https://via.placeholder.com/200?text=Todoroki"},
    13: {"name": "All Might", "series": "My Hero Academia", "image": "https://via.placeholder.com/200?text=AllMight"},
    14: {"name": "Colossal Titan", "series": "Attack on Titan", "image": "https://via.placeholder.com/200?text=Colossal"},
    15: {"name": "Rem", "series": "Re:Zero", "image": "https://via.placeholder.com/200?text=Rem"},
    16: {"name": "Emilia", "series": "Re:Zero", "image": "https://via.placeholder.com/200?text=Emilia"},
    17: {"name": "Sukuna", "series": "Jujutsu Kaisen", "image": "https://via.placeholder.com/200?text=Sukuna"},
    18: {"name": "Yuji Itadori", "series": "Jujutsu Kaisen", "image": "https://via.placeholder.com/200?text=Yuji"},
    19: {"name": "Gojo Satoru", "series": "Jujutsu Kaisen", "image": "https://via.placeholder.com/200?text=Gojo"},
    20: {"name": "Mikasa Ackerman", "series": "Attack on Titan", "image": "https://via.placeholder.com/200?text=Mikasa"},
    21: {"name": "Hange Zoe", "series": "Attack on Titan", "image": "https://via.placeholder.com/200?text=Hange"},
    22: {"name": "Zero Two", "series": "Darling in the FranXX", "image": "https://via.placeholder.com/200?text=ZeroTwo"},
    23: {"name": "Jotaro Kujo", "series": "JoJo's Bizarre Adventure", "image": "https://via.placeholder.com/200?text=Jotaro"},
    24: {"name": "DIO Brando", "series": "JoJo's Bizarre Adventure", "image": "https://via.placeholder.com/200?text=DIO"},
    25: {"name": "Giorno Giovanna", "series": "JoJo's Bizarre Adventure", "image": "https://via.placeholder.com/200?text=Giorno"},
    26: {"name": "Vegeta", "series": "Dragon Ball", "image": "https://via.placeholder.com/200?text=Vegeta"},
    27: {"name": "Frieza", "series": "Dragon Ball", "image": "https://via.placeholder.com/200?text=Frieza"},
    28: {"name": "Cell", "series": "Dragon Ball", "image": "https://via.placeholder.com/200?text=Cell"},
    29: {"name": "Majin Buu", "series": "Dragon Ball", "image": "https://via.placeholder.com/200?text=MajinBuu"},
    30: {"name": "Android 17", "series": "Dragon Ball", "image": "https://via.placeholder.com/200?text=Android17"},
    31: {"name": "Android 18", "series": "Dragon Ball", "image": "https://via.placeholder.com/200?text=Android18"},
    32: {"name": "Piccolo", "series": "Dragon Ball", "image": "https://via.placeholder.com/200?text=Piccolo"},
    33: {"name": "Krillin", "series": "Dragon Ball", "image": "https://via.placeholder.com/200?text=Krillin"},
    34: {"name": "Master Roshi", "series": "Dragon Ball", "image": "https://via.placeholder.com/200?text=Roshi"},
    35: {"name": "Yamcha", "series": "Dragon Ball", "image": "https://via.placeholder.com/200?text=Yamcha"},
    36: {"name": "Light Yagami", "series": "Death Note", "image": "https://via.placeholder.com/200?text=Light"},
    37: {"name": "L Lawliet", "series": "Death Note", "image": "https://via.placeholder.com/200?text=L"},
    38: {"name": "Ryuk", "series": "Death Note", "image": "https://via.placeholder.com/200?text=Ryuk"},
    39: {"name": "Misa Amane", "series": "Death Note", "image": "https://via.placeholder.com/200?text=Misa"},
    40: {"name": "Roronoa Zoro", "series": "One Piece", "image": "https://via.placeholder.com/200?text=Zoro"},
    41: {"name": "Nami", "series": "One Piece", "image": "https://via.placeholder.com/200?text=Nami"},
    42: {"name": "Usopp", "series": "One Piece", "image": "https://via.placeholder.com/200?text=Usopp"},
    43: {"name": "Sanji", "series": "One Piece", "image": "https://via.placeholder.com/200?text=Sanji"},
    44: {"name": "Tony Tony Chopper", "series": "One Piece", "image": "https://via.placeholder.com/200?text=Chopper"},
    45: {"name": "Nico Robin", "series": "One Piece", "image": "https://via.placeholder.com/200?text=Robin"},
    46: {"name": "Franky", "series": "One Piece", "image": "https://via.placeholder.com/200?text=Franky"},
    47: {"name": "Brook", "series": "One Piece", "image": "https://via.placeholder.com/200?text=Brook"},
    48: {"name": "Jinbe", "series": "One Piece", "image": "https://via.placeholder.com/200?text=Jinbe"},
    49: {"name": "Acnologia", "series": "Fairy Tail", "image": "https://via.placeholder.com/200?text=Acnologia"},
    50: {"name": "Natsu Dragneel", "series": "Fairy Tail", "image": "https://via.placeholder.com/200?text=Natsu"},
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
