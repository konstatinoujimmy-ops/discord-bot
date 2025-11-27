"""
Anime Characters Database με 50+ viral anime characters
"""

ANIME_CHARACTERS = {
    1: {"name": "Naruto Uzumaki", "series": "Naruto", "image": "https://images.wikia.nocookie.net/naruto/images/d/d6/Naruto_Part_III.png"},
    2: {"name": "Sasuke Uchiha", "series": "Naruto", "image": "https://images.wikia.nocookie.net/naruto/images/0/0e/Sasuke_Shippuden.png"},
    3: {"name": "Luffy", "series": "One Piece", "image": "https://images.wikia.nocookie.net/onepiece/images/1/1f/Luffy_Wano.png"},
    4: {"name": "Goku", "series": "Dragon Ball", "image": "https://images.wikia.nocookie.net/dragonball/images/7/7e/Goku_UI.png"},
    5: {"name": "Ichigo Kurosaki", "series": "Bleach", "image": "https://images.wikia.nocookie.net/bleach/images/8/82/Ichigo_Bankai.png"},
    6: {"name": "Eren Yeager", "series": "Attack on Titan", "image": "https://images.wikia.nocookie.net/shingekinokyojin/images/2/2d/Eren_Colossal.png"},
    7: {"name": "Levi Ackerman", "series": "Attack on Titan", "image": "https://images.wikia.nocookie.net/shingekinokyojin/images/3/36/Levi_Profile.png"},
    8: {"name": "Tanjiro Kamado", "series": "Demon Slayer", "image": "https://images.wikia.nocookie.net/kimetsu-no-yaiba/images/9/92/Tanjiro_Demon.png"},
    9: {"name": "Nezuko Kamado", "series": "Demon Slayer", "image": "https://images.wikia.nocookie.net/kimetsu-no-yaiba/images/4/48/Nezuko_Form.png"},
    10: {"name": "Deku", "series": "My Hero Academia", "image": "https://images.wikia.nocookie.net/bokunoheroacademia/images/5/51/Deku_Final.png"},
    11: {"name": "Bakugo", "series": "My Hero Academia", "image": "https://images.wikia.nocookie.net/bokunoheroacademia/images/7/71/Bakugo_Hero.png"},
    12: {"name": "Todoroki", "series": "My Hero Academia", "image": "https://images.wikia.nocookie.net/bokunoheroacademia/images/e/ea/Todoroki_Quirk.png"},
    13: {"name": "All Might", "series": "My Hero Academia", "image": "https://images.wikia.nocookie.net/bokunoheroacademia/images/8/80/All_Might.png"},
    14: {"name": "Colossal Titan", "series": "Attack on Titan", "image": "https://images.wikia.nocookie.net/shingekinokyojin/images/b/bf/Colossal_Titan.png"},
    15: {"name": "Rem", "series": "Re:Zero", "image": "https://images.wikia.nocookie.net/rezero/images/8/8f/Rem_Character.png"},
    16: {"name": "Emilia", "series": "Re:Zero", "image": "https://images.wikia.nocookie.net/rezero/images/c/ca/Emilia_Character.png"},
    17: {"name": "Sukuna", "series": "Jujutsu Kaisen", "image": "https://images.wikia.nocookie.net/jujutsu-kaisen/images/9/96/Sukuna_Form.png"},
    18: {"name": "Yuji Itadori", "series": "Jujutsu Kaisen", "image": "https://images.wikia.nocookie.net/jujutsu-kaisen/images/a/a7/Yuji_Character.png"},
    19: {"name": "Gojo Satoru", "series": "Jujutsu Kaisen", "image": "https://images.wikia.nocookie.net/jujutsu-kaisen/images/3/39/Gojo_Profile.png"},
    20: {"name": "Mikasa Ackerman", "series": "Attack on Titan", "image": "https://images.wikia.nocookie.net/shingekinokyojin/images/d/d8/Mikasa_Profile.png"},
    21: {"name": "Hange Zoe", "series": "Attack on Titan", "image": "https://images.wikia.nocookie.net/shingekinokyojin/images/a/a9/Hange_Profile.png"},
    22: {"name": "Zero Two", "series": "Darling in the FranXX", "image": "https://images.wikia.nocookie.net/darling-in-the-franxx/images/4/4f/Zero_Two.png"},
    23: {"name": "Jotaro Kujo", "series": "JoJo's Bizarre Adventure", "image": "https://images.wikia.nocookie.net/jojosbizarreadventure/images/5/5f/Jotaro_Profile.png"},
    24: {"name": "DIO Brando", "series": "JoJo's Bizarre Adventure", "image": "https://images.wikia.nocookie.net/jojosbizarreadventure/images/a/a5/DIO_Character.png"},
    25: {"name": "Giorno Giovanna", "series": "JoJo's Bizarre Adventure", "image": "https://images.wikia.nocookie.net/jojosbizarreadventure/images/9/9a/Giorno_Profile.png"},
    26: {"name": "Vegeta", "series": "Dragon Ball", "image": "https://images.wikia.nocookie.net/dragonball/images/f/f0/Vegeta_UI.png"},
    27: {"name": "Frieza", "series": "Dragon Ball", "image": "https://images.wikia.nocookie.net/dragonball/images/3/3c/Frieza_Final.png"},
    28: {"name": "Cell", "series": "Dragon Ball", "image": "https://images.wikia.nocookie.net/dragonball/images/e/e9/Cell_Perfect.png"},
    29: {"name": "Majin Buu", "series": "Dragon Ball", "image": "https://images.wikia.nocookie.net/dragonball/images/8/87/Majin_Buu.png"},
    30: {"name": "Android 17", "series": "Dragon Ball", "image": "https://images.wikia.nocookie.net/dragonball/images/5/5e/Android_17.png"},
    31: {"name": "Android 18", "series": "Dragon Ball", "image": "https://images.wikia.nocookie.net/dragonball/images/6/6c/Android_18.png"},
    32: {"name": "Piccolo", "series": "Dragon Ball", "image": "https://images.wikia.nocookie.net/dragonball/images/4/43/Piccolo_Final.png"},
    33: {"name": "Krillin", "series": "Dragon Ball", "image": "https://images.wikia.nocookie.net/dragonball/images/1/10/Krillin_Profile.png"},
    34: {"name": "Master Roshi", "series": "Dragon Ball", "image": "https://images.wikia.nocookie.net/dragonball/images/c/cb/Master_Roshi.png"},
    35: {"name": "Yamcha", "series": "Dragon Ball", "image": "https://images.wikia.nocookie.net/dragonball/images/7/78/Yamcha_Profile.png"},
    36: {"name": "Light Yagami", "series": "Death Note", "image": "https://images.wikia.nocookie.net/deathnote/images/2/2e/Light_Yagami.png"},
    37: {"name": "L Lawliet", "series": "Death Note", "image": "https://images.wikia.nocookie.net/deathnote/images/5/5a/L_Character.png"},
    38: {"name": "Ryuk", "series": "Death Note", "image": "https://images.wikia.nocookie.net/deathnote/images/9/91/Ryuk_Profile.png"},
    39: {"name": "Misa Amane", "series": "Death Note", "image": "https://images.wikia.nocookie.net/deathnote/images/2/25/Misa_Amane.png"},
    40: {"name": "Roronoa Zoro", "series": "One Piece", "image": "https://images.wikia.nocookie.net/onepiece/images/9/9c/Zoro_Wano.png"},
    41: {"name": "Nami", "series": "One Piece", "image": "https://images.wikia.nocookie.net/onepiece/images/2/20/Nami_Profile.png"},
    42: {"name": "Usopp", "series": "One Piece", "image": "https://images.wikia.nocookie.net/onepiece/images/7/7e/Usopp_Profile.png"},
    43: {"name": "Sanji", "series": "One Piece", "image": "https://images.wikia.nocookie.net/onepiece/images/e/e8/Sanji_Profile.png"},
    44: {"name": "Tony Tony Chopper", "series": "One Piece", "image": "https://images.wikia.nocookie.net/onepiece/images/f/f3/Chopper_Profile.png"},
    45: {"name": "Nico Robin", "series": "One Piece", "image": "https://images.wikia.nocookie.net/onepiece/images/c/c8/Robin_Profile.png"},
    46: {"name": "Franky", "series": "One Piece", "image": "https://images.wikia.nocookie.net/onepiece/images/a/a7/Franky_Profile.png"},
    47: {"name": "Brook", "series": "One Piece", "image": "https://images.wikia.nocookie.net/onepiece/images/f/f7/Brook_Profile.png"},
    48: {"name": "Jinbe", "series": "One Piece", "image": "https://images.wikia.nocookie.net/onepiece/images/e/ea/Jinbe_Profile.png"},
    49: {"name": "Acnologia", "series": "Fairy Tail", "image": "https://images.wikia.nocookie.net/fairytail/images/5/54/Acnologia_Dragon.png"},
    50: {"name": "Natsu Dragneel", "series": "Fairy Tail", "image": "https://images.wikia.nocookie.net/fairytail/images/8/86/Natsu_Profile.png"},
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
