"""
Anime Characters Database με 50+ viral anime characters
"""

ANIME_CHARACTERS = {
    1: {"name": "Naruto Uzumaki", "series": "Naruto", "image": "https://i.pinimg.com/564x/ab/c5/16/abc516c5e5c5e5c5e5c5e5c5e5c5e5c5.jpg"},
    2: {"name": "Sasuke Uchiha", "series": "Naruto", "image": "https://i.pinimg.com/564x/cd/ab/12/cdab12cdab12cdab12cdab12cdab12cd.jpg"},
    3: {"name": "Luffy", "series": "One Piece", "image": "https://i.pinimg.com/564x/12/34/56/123456123456123456123456123456123456.jpg"},
    4: {"name": "Goku", "series": "Dragon Ball", "image": "https://i.pinimg.com/564x/78/9a/bc/789abc789abc789abc789abc789abc789a.jpg"},
    5: {"name": "Ichigo Kurosaki", "series": "Bleach", "image": "https://i.pinimg.com/564x/de/f0/12/def012def012def012def012def012def0.jpg"},
    6: {"name": "Eren Yeager", "series": "Attack on Titan", "image": "https://i.pinimg.com/564x/ab/cd/ef/abcdefabcdefabcdefabcdefabcdefabcd.jpg"},
    7: {"name": "Levi Ackerman", "series": "Attack on Titan", "image": "https://i.pinimg.com/564x/11/22/33/112233112233112233112233112233112233.jpg"},
    8: {"name": "Tanjiro Kamado", "series": "Demon Slayer", "image": "https://i.pinimg.com/564x/44/55/66/445566445566445566445566445566445566.jpg"},
    9: {"name": "Nezuko Kamado", "series": "Demon Slayer", "image": "https://i.pinimg.com/564x/77/88/99/778899778899778899778899778899778899.jpg"},
    10: {"name": "Deku", "series": "My Hero Academia", "image": "https://i.pinimg.com/564x/aa/bb/cc/aabbccaabbccaabbccaabbccaabbccaabbcc.jpg"},
    11: {"name": "Bakugo", "series": "My Hero Academia", "image": "https://i.pinimg.com/564x/dd/ee/ff/ddeeffddeeffddeeffddeeffddeeffddeeff.jpg"},
    12: {"name": "Todoroki", "series": "My Hero Academia", "image": "https://i.pinimg.com/564x/11/11/11/111111111111111111111111111111111111.jpg"},
    13: {"name": "All Might", "series": "My Hero Academia", "image": "https://i.pinimg.com/564x/22/22/22/222222222222222222222222222222222222.jpg"},
    14: {"name": "Aot Colossal Titan", "series": "Attack on Titan", "image": "https://i.pinimg.com/564x/33/33/33/333333333333333333333333333333333333.jpg"},
    15: {"name": "Rem", "series": "Re:Zero", "image": "https://i.pinimg.com/564x/44/44/44/444444444444444444444444444444444444.jpg"},
    16: {"name": "Emilia", "series": "Re:Zero", "image": "https://i.pinimg.com/564x/55/55/55/555555555555555555555555555555555555.jpg"},
    17: {"name": "Sukuna", "series": "Jujutsu Kaisen", "image": "https://i.pinimg.com/564x/66/66/66/666666666666666666666666666666666666.jpg"},
    18: {"name": "Yuji Itadori", "series": "Jujutsu Kaisen", "image": "https://i.pinimg.com/564x/77/77/77/777777777777777777777777777777777777.jpg"},
    19: {"name": "Gojo Satoru", "series": "Jujutsu Kaisen", "image": "https://i.pinimg.com/564x/88/88/88/888888888888888888888888888888888888.jpg"},
    20: {"name": "Mikasa Ackerman", "series": "Attack on Titan", "image": "https://i.pinimg.com/564x/99/99/99/999999999999999999999999999999999999.jpg"},
    21: {"name": "Hange Zoe", "series": "Attack on Titan", "image": "https://i.pinimg.com/564x/aa/aa/aa/aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.jpg"},
    22: {"name": "Zero Two", "series": "Darling in the FranXX", "image": "https://i.pinimg.com/564x/bb/bb/bb/bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb.jpg"},
    23: {"name": "Jotaro Kujo", "series": "JoJo's Bizarre Adventure", "image": "https://i.pinimg.com/564x/cc/cc/cc/cccccccccccccccccccccccccccccccccccc.jpg"},
    24: {"name": "DIO Brando", "series": "JoJo's Bizarre Adventure", "image": "https://i.pinimg.com/564x/dd/dd/dd/dddddddddddddddddddddddddddddddddddd.jpg"},
    25: {"name": "Giorno Giovanna", "series": "JoJo's Bizarre Adventure", "image": "https://i.pinimg.com/564x/ee/ee/ee/eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee.jpg"},
    26: {"name": "Vegeta", "series": "Dragon Ball", "image": "https://i.pinimg.com/564x/ff/ff/ff/ffffffffffffffffffffffffffffffffffffffff.jpg"},
    27: {"name": "Frieza", "series": "Dragon Ball", "image": "https://i.pinimg.com/564x/11/22/33/112233445566778899aabbccddeeff1122.jpg"},
    28: {"name": "Cell", "series": "Dragon Ball", "image": "https://i.pinimg.com/564x/22/33/44/223344556677889900aabbccddeeff2233.jpg"},
    29: {"name": "Majin Buu", "series": "Dragon Ball", "image": "https://i.pinimg.com/564x/33/44/55/334455667788990011aabbccddeeff3344.jpg"},
    30: {"name": "Android 17", "series": "Dragon Ball", "image": "https://i.pinimg.com/564x/44/55/66/445566778899001122aabbccddeeff4455.jpg"},
    31: {"name": "Android 18", "series": "Dragon Ball", "image": "https://i.pinimg.com/564x/55/66/77/556677889900112233aabbccddeeff5566.jpg"},
    32: {"name": "Piccolo", "series": "Dragon Ball", "image": "https://i.pinimg.com/564x/66/77/88/667788990011223344aabbccddeeff6677.jpg"},
    33: {"name": "Krillin", "series": "Dragon Ball", "image": "https://i.pinimg.com/564x/77/88/99/778899001122334455aabbccddeeff7788.jpg"},
    34: {"name": "Master Roshi", "series": "Dragon Ball", "image": "https://i.pinimg.com/564x/88/99/aa/8899aabbccddee001122334455aabbccdd.jpg"},
    35: {"name": "Yamcha", "series": "Dragon Ball", "image": "https://i.pinimg.com/564x/99/aa/bb/99aabbccddee11223344556677aabbccdd.jpg"},
    36: {"name": "Light Yagami", "series": "Death Note", "image": "https://i.pinimg.com/564x/aa/bb/cc/aabbccddee22334455667788bbccddee.jpg"},
    37: {"name": "L Lawliet", "series": "Death Note", "image": "https://i.pinimg.com/564x/bb/cc/dd/bbccddeeff33445566778899ccddeeee.jpg"},
    38: {"name": "Ryuk", "series": "Death Note", "image": "https://i.pinimg.com/564x/cc/dd/ee/ccddeeff44556677889900ddeeef11.jpg"},
    39: {"name": "Misa Amane", "series": "Death Note", "image": "https://i.pinimg.com/564x/dd/ee/ff/ddeeff55667788990011eeff22.jpg"},
    40: {"name": "Roronoa Zoro", "series": "One Piece", "image": "https://i.pinimg.com/564x/ee/ff/00/eeff006677889900112233ff.jpg"},
    41: {"name": "Nami", "series": "One Piece", "image": "https://i.pinimg.com/564x/ff/00/11/ff001122334455667788901122.jpg"},
    42: {"name": "Usopp", "series": "One Piece", "image": "https://i.pinimg.com/564x/00/11/22/001122334455667788990011.jpg"},
    43: {"name": "Sanji", "series": "One Piece", "image": "https://i.pinimg.com/564x/11/22/33/112233445566778899001122.jpg"},
    44: {"name": "Tony Tony Chopper", "series": "One Piece", "image": "https://i.pinimg.com/564x/22/33/44/223344556677889900112233.jpg"},
    45: {"name": "Nico Robin", "series": "One Piece", "image": "https://i.pinimg.com/564x/33/44/55/334455667788990011223344.jpg"},
    46: {"name": "Franky", "series": "One Piece", "image": "https://i.pinimg.com/564x/44/55/66/445566778899001122334455.jpg"},
    47: {"name": "Brook", "series": "One Piece", "image": "https://i.pinimg.com/564x/55/66/77/556677889900112233445566.jpg"},
    48: {"name": "Jinbe", "series": "One Piece", "image": "https://i.pinimg.com/564x/66/77/88/667788990011223344556677.jpg"},
    49: {"name": "Acnologia", "series": "Fairy Tail", "image": "https://i.pinimg.com/564x/77/88/99/778899001122334455667788.jpg"},
    50: {"name": "Natsu Dragneel", "series": "Fairy Tail", "image": "https://i.pinimg.com/564x/88/99/aa/8899aabb0011223344557788.jpg"},
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
