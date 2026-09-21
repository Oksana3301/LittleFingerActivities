#!/usr/bin/env python3
"""Deterministically author the 20-category workbook expansion.

No dependencies and no writes outside --out. Existing catalogue is never read or
modified. Round 1 is copied to the worksheet root to match the normalized contract.
Run: python generate_expansion.py [--out DIRECTORY]
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from collections import Counter
from itertools import combinations
from pathlib import Path


def T(id, en):
    return {"id": id, "en": en}


# Every asset below is provided by the existing atlases or the three new atlases.
NAMES = {
    "hen": ("Ayam", "Hen"), "duck": ("Bebek", "Duck"),
    "turtle": ("Kura-kura", "Turtle"), "cat": ("Kucing", "Cat"),
    "rabbit": ("Kelinci", "Rabbit"), "goat": ("Kambing", "Goat"),
    "squirrel": ("Tupai", "Squirrel"), "bird": ("Burung", "Bird"),
    "lion": ("Singa", "Lion"), "butterfly": ("Kupu-kupu", "Butterfly"),
    "snail": ("Siput", "Snail"), "ladybug": ("Kepik", "Ladybug"),
    "bee": ("Lebah", "Bee"), "cow": ("Sapi", "Cow"),
    "horse": ("Kuda", "Horse"), "dog": ("Anjing", "Dog"),
    "carrot": ("Wortel", "Carrot"), "cucumber": ("Mentimun", "Cucumber"),
    "tomato": ("Tomat", "Tomato"), "apple": ("Apel", "Apple"),
    "banana": ("Pisang", "Banana"), "leaf": ("Daun", "Leaf"),
    "flower": ("Bunga", "Flower"), "tree": ("Pohon", "Tree"),
    "seed": ("Biji", "Seed"), "sprout": ("Tunas", "Sprout"),
    "sun": ("Matahari", "Sun"), "moon": ("Bulan", "Moon"),
    "cloud": ("Awan", "Cloud"), "raindrop": ("Tetes air", "Water drop"),
    "star": ("Bintang", "Star"), "rocket": ("Roket", "Rocket"),
    "planet": ("Planet", "Planet"), "astronaut": ("Astronaut", "Astronaut"),
    "bicycle": ("Sepeda", "Bicycle"), "umbrella": ("Payung", "Umbrella"),
    "train": ("Kereta", "Train"), "boat": ("Perahu", "Boat"),
    "car": ("Mobil", "Car"), "watering-can": ("Penyiram tanaman", "Watering can"),
    "trowel": ("Sekop kecil", "Trowel"),
    "mercury": ("Merkurius", "Mercury"), "venus": ("Venus", "Venus"),
    "earth": ("Bumi", "Earth"), "mars": ("Mars", "Mars"),
    "jupiter": ("Jupiter", "Jupiter"), "saturn": ("Saturnus", "Saturn"),
    "uranus": ("Uranus", "Uranus"), "neptune": ("Neptunus", "Neptune"),
    "comet": ("Komet", "Comet"), "telescope": ("Teleskop", "Telescope"),
    "satellite": ("Satelit buatan", "Artificial satellite"),
    "microscope": ("Mikroskop", "Microscope"), "magnet": ("Magnet", "Magnet"),
    "ice-cube": ("Es batu", "Ice cube"), "rock": ("Batu", "Rock"),
    "water-glass": ("Air minum", "Drinking water"),
    "mother": ("Ibu", "Mother"), "father": ("Ayah", "Father"),
    "grandmother": ("Nenek", "Grandmother"), "grandfather": ("Kakek", "Grandfather"),
    "older-sibling": ("Kakak", "Older sibling"), "younger-sibling": ("Adik", "Younger sibling"),
    "baby": ("Bayi", "Baby"), "family": ("Keluarga", "Family"),
    "eye": ("Mata", "Eye"), "ear": ("Telinga", "Ear"),
    "nose": ("Hidung", "Nose"), "mouth": ("Mulut", "Mouth"),
    "hand": ("Tangan", "Hand"), "foot": ("Kaki", "Foot"),
    "head": ("Kepala", "Head"), "shoulder": ("Bahu", "Shoulder"),
    "chair": ("Kursi", "Chair"), "table": ("Meja", "Table"),
    "bed": ("Tempat tidur", "Bed"), "lamp": ("Lampu", "Lamp"),
    "clock": ("Jam", "Clock"), "book": ("Buku", "Book"),
    "pencil": ("Pensil", "Pencil"), "bag": ("Tas", "Bag"),
    "scissors": ("Gunting", "Scissors"), "ruler": ("Penggaris", "Ruler"),
    "spoon": ("Sendok", "Spoon"), "plate": ("Piring", "Plate"),
    "cup": ("Cangkir", "Cup"), "toothbrush": ("Sikat gigi", "Toothbrush"),
    "soap": ("Sabun", "Soap"), "towel": ("Handuk", "Towel"),
}
PLANETS = "mercury venus earth mars jupiter saturn uranus neptune".split()
BODY = "eye ear nose mouth hand foot head shoulder".split()
FAMILY = "mother father grandmother grandfather older-sibling younger-sibling baby family".split()
ROOM = "chair table bed lamp clock spoon plate cup".split()
SCHOOL = "book pencil bag scissors ruler chair table clock".split()
LIVING = "cat dog rabbit bird butterfly bee tree sprout cow snail".split()
NONLIVING = "rock ice-cube chair spoon cup pencil lamp car".split()


def pic(asset, id, label=None):
    return {"id": id, "kind": "asset", "asset": asset,
            "label": T(*(label or NAMES[asset])), "showLabel": True}


def glyph(number, id=None):
    return {"id": id or f"n{number}", "kind": "glyph", "symbol": str(number),
            "value": number, "label": T(str(number), str(number))}


def quantity(number, asset, id):
    return {"id": id, "kind": "quantity", "value": number, "groupAsset": asset,
            "label": T("Kelompok gambar", "Picture group"),
            "ariaLabel": T(f"{number} gambar {NAMES[asset][0].lower()}",
                           f"{number} {NAMES[asset][1].lower()} {'picture' if number==1 else 'pictures'}")}


def rotated(items, seed):
    items = copy.deepcopy(items)
    # No global random state or Python-hash dependence.
    if seed % 2:
        items.reverse()
    shift = seed % len(items)
    return items[shift:] + items[:shift]


def pick_pool(pool, exclude, count, seed):
    candidates = [x for x in pool if x not in exclude]
    return rotated(candidates, seed)[:count]


def choose(assets, correct, instruction, seed, labels=None):
    options = [pic(a, f"o{i}", labels[i] if labels else None) for i, a in enumerate(assets)]
    return {"instruction": T(*instruction),
            "options": rotated(options, seed),
            "answer": [f"o{i}" for i in correct],
            "_expected": {"kind": "assets", "assets": [assets[i] for i in correct]}}


def single(target, pool, instruction, seed, count=4):
    return choose([target] + pick_pool(pool, {target}, count - 1, seed), [0], instruction, seed)


def naming(pool, v, r, family=False):
    index = v * 5 + r
    target = pool[index % len(pool)]
    n = 3 if v < 8 else 4 if v < 16 else 5
    if v >= 16:
        second = pool[(index + 1 + (v // 4) % (len(pool)-1)) % len(pool)]
        if second == target:
            second = pool[(index+1) % len(pool)]
        a, b = NAMES[target], NAMES[second]
        instruction = (f"Pilih kartu {a[0]} dan {b[0]}.", f"Choose the {a[1]} and {b[1]} cards.")
        return choose([target, second] + pick_pool(pool, {target, second}, n-2, index),
                      [0,1], instruction, index)
    prompts = [
        (f"Pilih kartu {NAMES[target][0]}.", f"Choose the {NAMES[target][1]} card."),
        (f"Di mana kartu {NAMES[target][0]}?", f"Where is the {NAMES[target][1]} card?"),
        (f"Temukan {NAMES[target][0]} di antara kartu ini.", f"Find {NAMES[target][1]} among these cards."),
    ]
    return single(target, pool, prompts[(v//4) % 3], index, n)


def pairs(pool, v, r, family=False):
    n = 3 if v < 16 else 4
    keys = rotated(pool, v * 3 + r * 5)[:n]
    left = [pic(a, f"l{i}") for i,a in enumerate(keys)]
    right = [pic(a, f"r{i}") for i,a in enumerate(keys)]
    instruction = (("Pasangkan kartu dengan sebutan keluarga yang sama.",
                    "Match cards with the same family term.") if family else
                   ("Pasangkan gambar dan nama yang sama.", "Match the same pictures and names."))
    return {"instruction": T(*instruction), "options": rotated(left, v+r),
            "rightOptions": rotated(right, v*2+r+1), "answer": [],
            "pairs": [{"left": f"l{i}", "right": f"r{i}"} for i in range(n)],
            "_expected": {"kind": "pairs"}}


# Factual clues remain valid independently of stylized illustration color or scale.
PLANET_FACTS = [
    ("earth", "Planet tempat kita tinggal adalah Bumi. Pilih Bumi.", "Earth is our home planet. Choose Earth."),
    ("mars", "Mars dijuluki Planet Merah. Pilih Mars.", "Mars is called the Red Planet. Choose Mars."),
    ("saturn", "Saturnus terkenal dengan cincin lebarnya. Pilih Saturnus.", "Saturn is known for its wide rings. Choose Saturn."),
    ("mercury", "Merkurius paling dekat dengan Matahari. Pilih Merkurius.", "Mercury is the closest planet to the Sun. Choose Mercury."),
    ("jupiter", "Jupiter adalah planet terbesar di tata surya kita. Pilih Jupiter.", "Jupiter is the largest planet in our solar system. Choose Jupiter."),
    ("neptune", "Neptunus adalah planet kedelapan dari Matahari. Pilih Neptunus.", "Neptune is the eighth planet from the Sun. Choose Neptune."),
    ("venus", "Venus adalah planet kedua dari Matahari. Pilih Venus.", "Venus is the second planet from the Sun. Choose Venus."),
    ("uranus", "Uranus adalah planet ketujuh dari Matahari. Pilih Uranus.", "Uranus is the seventh planet from the Sun. Choose Uranus."),
    ("earth", "Planet mana yang menjadi rumah kita?", "Which planet is our home?"),
    ("mars", "Planet mana yang dijuluki Planet Merah?", "Which planet is called the Red Planet?"),
    ("saturn", "Pilih Saturnus, planet yang terkenal dengan cincin lebarnya.", "Choose Saturn, the planet known for its wide rings."),
    ("mercury", "Planet mana yang paling dekat dengan Matahari?", "Which planet is closest to the Sun?"),
    ("jupiter", "Planet mana yang terbesar di tata surya kita?", "Which is the largest planet in our solar system?"),
    ("neptune", "Planet kedelapan dari Matahari bernama apa?", "What is the eighth planet from the Sun called?"),
    ("venus", "Planet kedua dari Matahari bernama apa?", "What is the second planet from the Sun called?"),
    ("uranus", "Planet ketujuh dari Matahari bernama apa?", "What is the seventh planet from the Sun called?"),
    ("earth", "Planet Bumi memiliki daratan dan lautan. Pilih Bumi.", "Earth has land and oceans. Choose Earth."),
    ("mars", "Mars adalah planet keempat dari Matahari. Pilih Mars.", "Mars is the fourth planet from the Sun. Choose Mars."),
    ("saturn", "Saturnus adalah planet keenam dari Matahari. Pilih Saturnus.", "Saturn is the sixth planet from the Sun. Choose Saturn."),
    ("mercury", "Merkurius adalah planet terkecil di tata surya kita. Pilih Merkurius.", "Mercury is the smallest planet in our solar system. Choose Mercury."),
    ("jupiter", "Planet kelima dari Matahari adalah Jupiter. Pilih Jupiter.", "Jupiter is the fifth planet from the Sun. Choose Jupiter."),
    ("neptune", "Dari delapan planet, Neptunus paling jauh dari Matahari. Pilih Neptunus.", "Of the eight planets, Neptune is farthest from the Sun. Choose Neptune."),
    ("earth", "Planet ketiga dari Matahari bernama apa?", "What is the third planet from the Sun called?"),
    ("saturn", "Planet keenam dari Matahari bernama apa?", "What is the sixth planet from the Sun called?"),
]

SENSES = [
    ("eye", "Bagian mana membantu melihat warna bunga?", "Which part helps us see a flower's color?"),
    ("ear", "Bagian mana membantu mendengar kicau burung?", "Which part helps us hear birdsong?"),
    ("nose", "Bagian mana membantu mencium harum bunga?", "Which part helps us smell a flower's scent?"),
    ("mouth", "Lidah ada di dalam mulut. Pilih mulut untuk mengecap rasa.", "The tongue is inside the mouth. Choose the mouth for tasting."),
    ("hand", "Pilih tangan. Kulit tangan dapat merasakan lembutnya handuk.", "Choose the hand. Its skin can feel a soft towel."),
    ("eye", "Bagian mana membantu melihat gambar di buku?", "Which part helps us see a picture in a book?"),
    ("ear", "Bagian mana membantu mendengar bunyi jam?", "Which part helps us hear a clock ticking?"),
    ("nose", "Bagian mana membantu mencium aroma pisang?", "Which part helps us smell a banana?"),
    ("mouth", "Pilih mulut, tempat lidah membantu mengecap rasa apel.", "Choose the mouth, where the tongue helps taste an apple."),
    ("hand", "Pilih tangan. Kulit tangan bisa merasakan permukaan cangkir.", "Choose the hand. Its skin can feel the surface of a cup."),
    ("eye", "Bagian mana membantu melihat awan di langit?", "Which part helps us see clouds in the sky?"),
    ("ear", "Bagian mana membantu mendengar suara teman?", "Which part helps us hear a friend's voice?"),
    ("nose", "Pilih hidung untuk mencium aroma makanan.", "Choose the nose for smelling food."),
    ("mouth", "Di mana lidah yang membantu mengecap rasa makanan?", "Where is the tongue that helps us taste food?"),
    ("hand", "Kulit tangan merasakan halus dan kasar. Pilih tangan.", "The skin on a hand feels smooth and rough. Choose the hand."),
]

CARE = [
    ("soap", "Tangan akan dicuci dengan air. Pilih sabun untuk membantu membersihkannya.", "Hands will be washed with water. Choose soap to help clean them."),
    ("toothbrush", "Pilih alat untuk menyikat gigi dengan bantuan orang dewasa.", "Choose the tool for brushing teeth with an adult's help."),
    ("towel", "Tangan sudah dicuci. Pilih benda untuk mengeringkannya.", "The hands are washed. Choose something to dry them with."),
    ("water-glass", "Nia haus setelah bermain. Pilih air minum.", "Nia is thirsty after playing. Choose drinking water."),
    ("bed", "Bimo mengantuk. Pilih tempat untuk tidur.", "Bimo feels sleepy. Choose a place to sleep."),
    ("soap", "Sebelum makan, kita mencuci tangan dengan air dan apa?", "Before eating, we wash hands with water and what?"),
    ("toothbrush", "Setelah makan malam, Nia menyiapkan alat sikat gigi. Pilih alatnya.", "After dinner, Nia gets ready to brush her teeth. Choose the tool."),
    ("towel", "Selesai mandi, benda apa membantu mengeringkan badan?", "After a bath, what helps dry the body?"),
    ("water-glass", "Bimo ingin minum air. Kartu mana yang ia pilih?", "Bimo wants some water to drink. Which card does he choose?"),
    ("bed", "Sudah waktunya beristirahat sambil berbaring. Pilih tempat tidur.", "It is time to rest lying down. Choose the bed."),
    ("hand", "Sebelum makan, bagian tubuh apa yang kita cuci dengan sabun dan air?", "Before eating, which body part do we wash with soap and water?"),
    ("mouth", "Gigi ada di dalam bagian tubuh mana?", "Inside which body part are the teeth?"),
]

FUNCTIONS = [
    ("chair", "Pilih benda untuk duduk.", "Choose something to sit on."),
    ("table", "Pilih meja, tempat meletakkan buku saat menggambar.", "Choose the table, a place to put a book while drawing."),
    ("bed", "Pilih benda untuk tidur.", "Choose something to sleep in."),
    ("lamp", "Pilih benda untuk menerangi ruangan.", "Choose something that lights a room."),
    ("clock", "Pilih benda untuk melihat waktu.", "Choose something that shows the time."),
    ("book", "Pilih benda untuk membaca cerita.", "Choose something for reading a story."),
    ("pencil", "Pilih benda untuk menggambar di kertas.", "Choose something for drawing on paper."),
    ("bag", "Pilih benda untuk membawa buku ke sekolah.", "Choose something for carrying books to school."),
    ("scissors", "Dengan bantuan orang dewasa, pilih alat untuk menggunting kertas.", "With an adult's help, choose the tool for cutting paper."),
    ("ruler", "Pilih alat untuk mengukur panjang di kertas.", "Choose a tool for measuring length on paper."),
    ("spoon", "Pilih benda untuk menyendok makanan.", "Choose something for scooping food."),
    ("plate", "Pilih piring untuk menaruh makanan.", "Choose the plate for holding food."),
    ("cup", "Pilih cangkir untuk wadah minuman.", "Choose a cup for holding a drink."),
    ("toothbrush", "Pilih alat untuk membersihkan gigi.", "Choose the tool for cleaning teeth."),
    ("soap", "Pilih sabun untuk dipakai bersama air saat mencuci tangan.", "Choose soap to use with water when washing hands."),
    ("towel", "Pilih benda untuk mengeringkan tangan yang basah.", "Choose something for drying wet hands."),
    ("watering-can", "Pilih alat untuk menyiram tanaman.", "Choose the tool for watering a plant."),
    ("umbrella", "Pilih benda yang membantu melindungi dari hujan.", "Choose something that helps keep rain off."),
    ("telescope", "Pilih teleskop untuk mengamati benda langit bersama orang dewasa.", "Choose a telescope for looking at sky objects with an adult."),
    ("microscope", "Pilih mikroskop untuk melihat benda sangat kecil lebih jelas.", "Choose a microscope for seeing very small things more clearly."),
]

# Option captions are actions/utterances, not judgements about a child's character.
KIND = [
    ("book", "Nia ingin meminjam buku. Pilih ucapan untuk meminta izin.", "Nia wants to borrow a book. Choose words for asking permission.",
     ("Boleh aku pinjam bukunya?", "May I borrow the book?"), ("Selamat pagi.", "Good morning."), ("Terima kasih.", "Thank you.")),
    ("pencil", "Bimo mendapat bantuan mencari pensil. Pilih ucapan terima kasih.", "Someone helps Bimo find a pencil. Choose words of thanks.",
     ("Terima kasih sudah membantu.", "Thank you for helping."), ("Boleh aku pinjam?", "May I borrow it?"), ("Sampai jumpa.", "See you later.")),
    ("cup", "Nia tidak sengaja menyenggol cangkir. Pilih ucapan meminta maaf.", "Nia accidentally bumps a cup. Choose words for apologizing.",
     ("Maaf, aku tidak sengaja.", "Sorry, it was an accident."), ("Selamat pagi.", "Good morning."), ("Boleh aku ikut?", "May I join?")),
    ("bag", "Bimo kesulitan membuka tas. Pilih ucapan untuk meminta bantuan.", "Bimo has trouble opening a bag. Choose words for asking for help.",
     ("Tolong bantu buka tasku.", "Please help me open my bag."), ("Sampai jumpa.", "See you later."), ("Terima kasih untuk bukunya.", "Thank you for the book.")),
    ("hand", "Nia ingin ruang untuk bergerak. Pilih ucapan meminta ruang dengan tenang.", "Nia wants room to move. Choose calm words for asking for space.",
     ("Tolong beri aku sedikit ruang.", "Please give me a little space."), ("Selamat pagi.", "Good morning."), ("Terima kasih untuk pensilnya.", "Thank you for the pencil.")),
    ("family", "Bimo bertemu teman di pagi hari. Pilih sapaan pagi.", "Bimo meets a friend in the morning. Choose a morning greeting.",
     ("Selamat pagi!", "Good morning!"), ("Boleh aku pinjam?", "May I borrow it?"), ("Tolong buka tasku.", "Please open my bag.")),
    ("book", "Nia hendak pulang setelah bermain. Pilih ucapan perpisahan.", "Nia is going home after playing. Choose a goodbye.",
     ("Sampai jumpa lagi!", "See you again!"), ("Selamat datang!", "Welcome!"), ("Boleh aku ikut?", "May I join?")),
    ("chair", "Seorang teman datang ke kelompok Bimo. Pilih ucapan menyambut.", "A friend arrives at Bimo's group. Choose welcoming words.",
     ("Selamat datang, ayo duduk di sini.", "Welcome, you can sit here."), ("Sampai jumpa besok.", "See you tomorrow."), ("Tolong bantu buka tas.", "Please help open the bag.")),
    ("pencil", "Nia ingin ikut menggambar. Pilih ucapan untuk meminta ikut.", "Nia wants to join the drawing activity. Choose words for asking to join.",
     ("Boleh aku ikut menggambar?", "May I join in drawing?"), ("Selamat malam.", "Good night."), ("Terima kasih untuk minumnya.", "Thank you for the drink.")),
    ("hand", "Bimo belum ingin berpelukan. Pilih ucapan batas diri yang sopan.", "Bimo does not want a hug right now. Choose polite words for his boundary.",
     ("Aku belum ingin berpelukan, terima kasih.", "I do not want a hug right now, thank you."), ("Tolong pinjamkan pensil.", "Please lend me a pencil."), ("Sampai jumpa.", "See you later.")),
    ("bag", "Nia melihat teman kesulitan membawa tas. Pilih ucapan menawarkan bantuan.", "Nia sees a friend struggling with a bag. Choose words for offering help.",
     ("Mau aku bantu membawa tas?", "Would you like help carrying the bag?"), ("Selamat malam.", "Good night."), ("Boleh aku pinjam buku?", "May I borrow a book?")),
    ("book", "Bimo selesai memakai buku pinjaman. Pilih ucapan saat mengembalikannya.", "Bimo finishes using a borrowed book. Choose words for returning it.",
     ("Ini bukunya, terima kasih.", "Here is the book, thank you."), ("Selamat datang.", "Welcome."), ("Tolong beri aku ruang.", "Please give me some space.")),
]

TURN = [
    ("pencil", "Sekarang giliran Nia memakai pensil. Bimo ingin meminta giliran setelahnya. Pilih ucapannya.", "It is Nia's turn with the pencil. Bimo wants to ask for the next turn. Choose his words.",
     ("Boleh aku pakai setelah kamu?", "May I use it after you?"), ("Selamat pagi.", "Good morning."), ("Terima kasih untuk minumnya.", "Thank you for the drink.")),
    ("book", "Bimo selesai memilih buku. Ia ingin memberi giliran kepada Nia. Pilih ucapannya.", "Bimo has finished choosing a book. He wants to give Nia a turn. Choose his words.",
     ("Sekarang giliranmu memilih.", "Now it is your turn to choose."), ("Aku baru mulai memilih.", "I have just started choosing."), ("Di mana tasku?", "Where is my bag?")),
    ("clock", "Nia menunggu giliran. Ia ingin tahu kapan bisa mulai. Pilih pertanyaannya.", "Nia is waiting for a turn. She wants to know when she can start. Choose her question.",
     ("Kapan giliranku mulai?", "When does my turn start?"), ("Apa warna bukunya?", "What color is the book?"), ("Di mana cangkirnya?", "Where is the cup?")),
    ("family", "Dua teman bingung menentukan urutan. Pilih ucapan untuk meminta bantuan orang dewasa.", "Two friends are unsure about the turn order. Choose words for asking an adult to help.",
     ("Tolong bantu kami menentukan giliran.", "Please help us decide the turn order."), ("Aku suka buku ini.", "I like this book."), ("Selamat malam.", "Good night.")),
    ("book", "Nia menunggu pensil. Ia memilih membaca sambil menunggu. Pilih kartu rencananya.", "Nia is waiting for a pencil. She chooses to read while waiting. Choose her plan.",
     ("Aku membaca buku sambil menunggu.", "I will read a book while I wait."), ("Aku tidur sekarang.", "I will sleep now."), ("Aku menyiram tanaman.", "I will water a plant.")),
    ("pencil", "Bimo masih menggambar. Ia ingin memberi tahu kapan pensil bisa dipinjam. Pilih ucapannya.", "Bimo is still drawing. He wants to say when he can lend the pencil. Choose his words.",
     ("Setelah gambarku selesai, kamu boleh pakai.", "You may use it when I finish my drawing."), ("Selamat datang.", "Welcome."), ("Ini air minummu.", "Here is your drinking water.")),
    ("chair", "Nia mengajak teman bergiliran duduk di kursi cerita. Pilih ajakannya.", "Nia invites a friend to take turns in the story chair. Choose her invitation.",
     ("Ayo bergiliran duduk di kursi cerita.", "Let's take turns in the story chair."), ("Ayo cuci tangan.", "Let's wash our hands."), ("Ayo lihat awan.", "Let's look at clouds.")),
    ("book", "Bimo menunggu. Nia selesai membaca dan ingin memberi buku kepadanya. Pilih ucapannya.", "Bimo is waiting. Nia finishes reading and wants to pass him the book. Choose her words.",
     ("Aku sudah selesai. Ini giliranmu.", "I have finished. It is your turn."), ("Aku baru mulai membaca.", "I have just started reading."), ("Aku ingin minum.", "I would like a drink.")),
    ("hand", "Nia perlu jeda dari permainan. Pilih ucapan untuk meminta jeda.", "Nia needs a break from the game. Choose words for asking for a break.",
     ("Aku ingin istirahat sebentar.", "I would like a short break."), ("Tolong ambilkan buku.", "Please bring the book."), ("Selamat pagi.", "Good morning.")),
    ("clock", "Bimo ingin menyepakati urutan: Nia dulu, lalu Bimo. Pilih ucapannya.", "Bimo wants to agree on the order: Nia first, then Bimo. Choose his words.",
     ("Nia dulu, lalu giliranku.", "Nia first, then my turn."), ("Aku dulu, lalu Nia.", "Me first, then Nia."), ("Kita sedang makan.", "We are eating.")),
    ("pencil", "Giliran Bimo tiba. Ia ingin berterima kasih karena temannya sudah menunggu. Pilih ucapannya.", "Bimo's turn arrives. He wants to thank his friend for waiting. Choose his words.",
     ("Terima kasih sudah menunggu.", "Thank you for waiting."), ("Tolong cuci tangan.", "Please wash your hands."), ("Di mana buku itu?", "Where is that book?")),
    ("family", "Nia belum memahami aturan giliran. Pilih pertanyaan untuk meminta penjelasan.", "Nia does not yet understand the turn rule. Choose a question asking for an explanation.",
     ("Bisa jelaskan urutan gilirannya?", "Can you explain the turn order?"), ("Apa warna pensil ini?", "What color is this pencil?"), ("Boleh minum air?", "May I have water?")),
]


def social(data, v, r):
    item = data[scenario_index(v,r,len(data))]
    asset, id, en, *captions = item
    options = [pic(asset, f"o{i}", caption) for i, caption in enumerate(captions)]
    return {"instruction": T(id, en), "layout": "story-choices",
            "options": rotated(options, v+r), "answer": ["o0"],
            "_expected": {"kind": "caption", "correct": T(*captions[0])}}


PLANTS = [
    ("raindrop", "Tanaman perlu air. Pilih gambar tetes air.", "Plants need water. Choose the water drop.", ["raindrop","chair","spoon","clock"]),
    ("sun", "Tanaman hijau memerlukan cahaya. Pilih Matahari sebagai sumber cahaya.", "Green plants need light. Choose the Sun as a source of light.", ["sun","book","bag","rock"]),
    ("watering-can", "Tanah tanaman ini kering. Pilih alat untuk memberi air secukupnya.", "This plant's soil is dry. Choose a tool for adding a little water.", ["watering-can","pencil","plate","clock"]),
    ("sprout", "Biji dapat tumbuh menjadi tunas. Pilih tunas.", "A seed can grow into a sprout. Choose the sprout.", ["sprout","cup","lamp","spoon"]),
    ("tree", "Pohon adalah tumbuhan hidup. Pilih pohon yang perlu dirawat.", "A tree is a living plant. Choose the tree that needs care.", ["tree","chair","car","cup"]),
    ("raindrop", "Akar tanaman menyerap air. Pilih gambar air.", "Plant roots take in water. Choose the water picture.", ["raindrop","bag","clock","book"]),
    ("sun", "Tanaman ini berada di tempat terlalu gelap. Pilih sumber cahaya alami.", "This plant is in a place that is too dark. Choose a natural light source.", ["sun","spoon","chair","bag"]),
    ("watering-can", "Nia ingin menyiram tanaman bersama orang dewasa. Pilih alatnya.", "Nia wants to water a plant with an adult. Choose the tool.", ["watering-can","pencil","ruler","clock"]),
    ("leaf", "Daun membantu tumbuhan membuat makanan dengan cahaya. Pilih daun.", "Leaves help a plant make food using light. Choose the leaf.", ["leaf","chair","cup","bag"]),
    ("seed", "Bimo akan menanam biji. Pilih biji.", "Bimo is going to plant a seed. Choose the seed.", ["seed","spoon","lamp","clock"]),
    ("flower", "Bunga ini tumbuh pada tanaman. Pilih bunga.", "This flower grows on a plant. Choose the flower.", ["flower","car","cup","ruler"]),
    ("trowel", "Dengan bantuan orang dewasa, pilih sekop kecil untuk memindahkan tanah ke pot.", "With an adult's help, choose the trowel for moving soil into a pot.", ["trowel","pencil","toothbrush","clock"]),
]

WEATHER = [
    ("umbrella", "Hujan turun saat Nia berjalan bersama orang dewasa. Pilih pelindung dari hujan.", "It is raining as Nia walks with an adult. Choose something to keep rain off.", ["umbrella","pencil","spoon","clock"]),
    ("water-glass", "Hari terasa panas dan Bimo haus. Pilih air minum.", "It feels hot and Bimo is thirsty. Choose drinking water.", ["water-glass","book","bag","ruler"]),
    ("cloud", "Langit berawan. Pilih gambar awan.", "The sky is cloudy. Choose the cloud picture.", ["cloud","moon","rock","tree"]),
    ("sun", "Cuaca cerah. Pilih gambar Matahari.", "The weather is sunny. Choose the Sun picture.", ["sun","raindrop","rock","cup"]),
    ("raindrop", "Air hujan jatuh dari awan. Pilih tetes air.", "Rain falls from clouds. Choose the water drop.", ["raindrop","leaf","star","spoon"]),
    ("towel", "Tangan Nia basah terkena hujan. Pilih benda untuk mengeringkannya.", "Rain has made Nia's hands wet. Choose something to dry them with.", ["towel","pencil","clock","plate"]),
    ("umbrella", "Bimo menyiapkan payung sebelum keluar saat hujan. Pilih payung.", "Bimo gets an umbrella before going out in the rain. Choose the umbrella.", ["umbrella","bag","ruler","book"]),
    ("water-glass", "Setelah bermain pada hari hangat, Nia ingin minum. Pilih air minum.", "After playing on a warm day, Nia wants a drink. Choose drinking water.", ["water-glass","lamp","soap","chair"]),
    ("cloud", "Awan menutupi sebagian langit. Kartu mana menunjukkan awan?", "Clouds cover part of the sky. Which card shows a cloud?", ["cloud","star","moon","flower"]),
    ("sun", "Pilih sumber cahaya alami pada siang hari.", "Choose the natural source of light in daytime.", ["sun","lamp","clock","book"]),
    ("raindrop", "Pilih gambar yang mewakili hujan.", "Choose the picture that represents rain.", ["raindrop","star","leaf","moon"]),
    ("towel", "Sepulang dari hujan, Bimo mengeringkan tangan. Pilih handuk.", "After coming in from the rain, Bimo dries his hands. Choose the towel.", ["towel","cup","lamp","pencil"]),
]


def scenario_index(v,r,length):
    # Progress through short stories in different combinations, rather than
    # duplicating the same four-round worksheet with only a new variant number.
    return (v*5+r*(1+2*(v//8))) % length


def fixed_scenario(data, v, r):
    target, id, en, pool = data[scenario_index(v,r,len(data))]
    return single(target, pool, (id,en), v*4+r, 3 if v<8 else 4)


def living_round(v, r):
    i = v*4+r
    living = r%2 == 0
    good, bad = (LIVING, NONLIVING) if living else (NONLIVING,LIVING)
    ncorrect = 1 if v < 8 else 2
    if ncorrect==1:
        targets = [good[(v+r*3)%len(good)]]
    else:
        targets = list(list(combinations(good,2))[(v*3+r*7)%len(list(combinations(good,2)))])
    assets = targets + rotated(bad,i+2)[:3]
    instruction = (("Pilih semua makhluk hidup.", "Choose all the living things.") if living else
                   ("Pilih semua benda tak hidup.", "Choose all the nonliving things."))
    result=choose(assets,list(range(ncorrect)),instruction,i)
    result["_expected"]={"kind":"living", "wantLiving":living}
    return result


def compare_round(v, r, equal=False):
    i=v*4+r
    asset=["apple","pencil","spoon","flower","cup","book"][v%6]
    if equal:
        target=1+(i%5)
        vals=[target]+[n for n in rotated(list(range(1,7)),i) if n!=target][:2]
        instruction=(f"Pilih kelompok dengan {target} gambar, sama banyak dengan contoh.",
                     f"Choose the group with {target} {'picture' if target==1 else 'pictures'}, the same number as the example.")
        result={"instruction":T(*instruction),"reference":quantity(target,asset,"reference")}
        result["_expected"]={"kind":"equal","target":target}
    else:
        vals=list(list(combinations(range(1,7),3))[(v*3+r*7)%20])
        most=r%2==0
        target=max(vals) if most else min(vals)
        instruction=(("Pilih kelompok yang paling banyak.","Choose the group with the most.") if most else
                     ("Pilih kelompok yang paling sedikit.","Choose the group with the fewest."))
        result={"instruction":T(*instruction),"_expected":{"kind":"compare","most":most}}
    options=[quantity(n,asset,f"o{j}") for j,n in enumerate(vals)]
    result.update(options=rotated(options,i),answer=[f"o{vals.index(target)}"])
    return result


def neighbors(v,r):
    start=(v+r)%7
    vals=list(range(start,start+4))
    missing=(v//6+r)%4
    target=vals[missing]
    instruction=("Hitung maju satu-satu. Angka apa yang hilang?", "Count forward by ones. Which number is missing?")
    if missing==0:
        instruction=("Angka apa tepat sebelum angka pertama yang terlihat?", "Which number comes just before the first number shown?")
    elif missing==3:
        instruction=("Angka apa tepat setelah angka terakhir yang terlihat?", "Which number comes just after the last number shown?")
    elif missing in (1,2):
        instruction=("Isi angka di antara dua tetangganya.", "Fill in the number between its two neighbors.")
    options=[glyph(n) for n in rotated(list(range(max(0,target-2),min(10,target+3))),v+r) if n!=target][:3]
    options.append(glyph(target))
    return {"instruction":T(*instruction),"options":rotated(options,v+r),"answer":[f"n{target}"],
            "patternItems":[None if j==missing else glyph(n,f"p{j}") for j,n in enumerate(vals)],
            "_expected":{"kind":"neighbors"}}


def stories(v,r):
    asset=["apple","pencil","spoon","flower","cup","book"][v%6]
    idname,enname=NAMES[asset]
    subtraction=(v//6+r)%2==1
    if subtraction:
        a=2+(v+r)%4
        b=1+(v*2+r)%(a-1)
        result=a-b
        instruction=(f"Ada {a} gambar {idname.lower()}. {b} diambil. Berapa gambar tersisa?",
                     f"Start with {a} {enname.lower()} {'picture' if a==1 else 'pictures'}. Take away {b}. How many remain?")
        op="subtract"
    else:
        a=1+(v+r)%3
        b=1+(v*2+r)%(5-a)
        result=a+b
        instruction=(f"Ada {a} gambar {idname.lower()}. Ditambah {b} lagi. Berapa jumlahnya?",
                     f"Start with {a} {enname.lower()} {'picture' if a==1 else 'pictures'}. Add {b} more. How many altogether?")
        op="add"
    choices=[result]+[n for n in rotated(list(range(0,7)),v+r) if n!=result][:3]
    # Keep the result out of countTarget; the renderer must not display it as a count scene.
    return {"instruction":T(*instruction),"options":rotated([glyph(n) for n in choices],v+r),
            "answer":[f"n{result}"],"operation":op,"operands":[a,b],
            "expression":f"{a} {'−' if subtraction else '+'} {b} = ?",
            "reference":pic(asset,"story-object"),"_expected":{"kind":"story"}}


GENERIC_NOTE=T("Bacakan petunjuk dan nama kartu. Anak boleh menunjuk, menyebut, atau memilih dengan bantuan.",
               "Read the prompt and card names aloud. Children may point, say, or choose with help.")
FAMILY_NOTE=T("Kenali sebutan keluarga. Bacakan label; jangan menebak hubungan dari penampilan. Setiap keluarga berbeda; gunakan sebutan yang nyaman dan lewati yang tidak sesuai.",
              "Explore family terms. Read the labels; do not infer relationships from appearance. Every family is different; use comfortable names and skip any that do not fit.")
SOCIAL_NOTE=T("Bacakan cerita dan semua pilihan. Ini latihan percakapan dengan beberapa contoh ucapan, bukan penilaian perilaku atau kemampuan sosial anak. Anak boleh memilih jeda.",
              "Read the story and every choice. This is conversation practice with example phrases, not an assessment of a child's behavior or social ability. Children may choose a break.")
SPACE_NOTE=T("Gambar planet adalah ilustrasi; ukuran, jarak, dan warna tidak untuk diukur. Bacakan nama dan petunjuk. Matahari adalah bintang, bukan planet.",
             "Planet pictures are illustrations; their sizes, distances, and colors are not for measurement. Read the names and clues. The Sun is a star, not a planet.")
SENSE_NOTE=T("Setiap orang menggunakan indra dengan cara berbeda. Lidah membantu mengecap; kulit di seluruh tubuh merasakan sentuhan. Tangan di sini adalah contoh tempat kulit merasakan sentuhan.",
             "People use their senses in different ways. The tongue helps with taste; skin across the body feels touch. The hand is one example of skin feeling touch.")

CATEGORY_SPECS=[
    ("planet-names","space","identify",3,"earth","Kenali Nama Planet","Planet Names","Kenali delapan nama planet lewat kartu bergambar.","Explore the eight planet names with picture cards."),
    ("planet-facts","space","identify",5,"saturn","Petunjuk Planet","Planet Clues","Dengarkan petunjuk singkat tentang planet.","Listen to short clues about planets."),
    ("space-pairs","space","pair",3,"rocket","Pasangan Antariksa","Space Pairs","Cocokkan gambar dan nama benda antariksa.","Match pictures and names of space objects."),
    ("body-parts","body","identify",2,"hand","Bagian Tubuh","Body Parts","Kenali nama bagian tubuh melalui gambar.","Explore body-part names through pictures."),
    ("five-senses","body","identify",3,"eye","Mengenal Pancaindra","Exploring Five Senses","Hubungkan melihat, mendengar, mencium, mengecap, dan meraba.","Explore seeing, hearing, smelling, tasting, and touch."),
    ("body-care","body","identify",3,"toothbrush","Merawat Tubuh","Caring for Our Bodies","Pilih benda untuk kebersihan, minum, dan istirahat.","Choose things for washing, drinking, and resting."),
    ("family-members","family","identify",2,"family","Sebutan Keluarga","Family Terms","Kenali sebutan keluarga dengan label yang dibacakan.","Explore family terms with labels read aloud."),
    ("family-pairs","family","pair",3,"family","Pasangan Sebutan Keluarga","Family Term Pairs","Pasangkan kartu dengan sebutan keluarga yang sama.","Match cards with the same family term."),
    ("kind-words","social","identify",3,"hand","Kata yang Ramah","Kind Words","Dengarkan cerita dan pilih contoh ucapan yang sesuai.","Listen to a story and choose a fitting phrase."),
    ("taking-turns","social","identify",4,"clock","Cerita Bergiliran","Taking Turns Stories","Jelajahi ucapan untuk meminta, menunggu, dan memberi giliran.","Explore words for asking, waiting, and offering a turn."),
    ("room-objects","everyday","identify",2,"chair","Benda di Rumah","Things at Home","Kenali nama benda yang dapat ditemukan di rumah.","Explore names of things found at home."),
    ("school-objects","everyday","identify",3,"book","Benda untuk Belajar","Things for Learning","Kenali benda yang membantu kegiatan belajar.","Explore things that help us learn."),
    ("object-functions","everyday","identify",3,"pencil","Benda dan Kegunaannya","Objects and Their Uses","Pilih benda yang sesuai dengan kegiatan dalam cerita.","Choose an object for the activity in a short story."),
    ("living-nonliving","science","identify",4,"sprout","Hidup atau Tak Hidup","Living and Nonliving","Kelompokkan makhluk hidup dan benda tak hidup yang jelas.","Sort clear examples of living and nonliving things."),
    ("plant-needs","science","identify",3,"watering-can","Merawat Tanaman","Caring for Plants","Kenali air, cahaya, dan alat untuk merawat tanaman.","Explore water, light, and tools for caring for plants."),
    ("weather-choices","science","identify",3,"umbrella","Cuaca dan Pilihan","Weather and Choices","Kenali cuaca dan benda yang membantu kegiatan sehari-hari.","Explore weather and useful everyday choices."),
    ("math-more-less","numbers","compare",3,"apple","Paling Banyak dan Sedikit","Most and Fewest","Bandingkan tiga kelompok berisi satu sampai enam gambar.","Compare three groups of one to six pictures."),
    ("math-equal","numbers","compare",4,"cup","Sama Banyak","Equal Groups","Cari kelompok yang sama banyak dengan contoh.","Find a group with the same number as the example."),
    ("number-neighbors","numbers","pattern",4,"clock","Tetangga Angka","Number Neighbors","Isi angka sebelum, sesudah, atau di antara angka lain.","Fill in a number before, after, or between other numbers."),
    ("math-stories","numbers","identify",5,"spoon","Cerita Tambah dan Kurang","Addition and Subtraction Stories","Dengarkan cerita tambah dan kurang dengan hasil sampai lima.","Listen to addition and subtraction stories with results up to five."),
]


def round_for(cid,v,r):
    if cid=="planet-names":return naming(PLANETS,v,r)
    if cid=="planet-facts":
        target,id,en=PLANET_FACTS[(v*4+r)%len(PLANET_FACTS)]
        return single(target,PLANETS,(id,en),v*4+r,4)
    if cid=="space-pairs":return pairs(PLANETS+"comet telescope satellite rocket astronaut moon".split(),v,r)
    if cid=="body-parts":return naming(BODY,v,r)
    if cid=="five-senses":
        target,id,en=SENSES[(v*4+r)%len(SENSES)]
        return single(target,BODY,(id,en),v*4+r,4)
    if cid=="body-care":
        target,id,en=CARE[scenario_index(v,r,len(CARE))]
        return single(target,"soap toothbrush towel water-glass bed hand mouth clock pencil".split(),(id,en),v*4+r,4)
    if cid=="family-members":return naming(FAMILY,v,r,True)
    if cid=="family-pairs":return pairs(FAMILY,v,r,True)
    if cid=="kind-words":return social(KIND,v,r)
    if cid=="taking-turns":return social(TURN,v,r)
    if cid=="room-objects":return naming(ROOM,v,r)
    if cid=="school-objects":return naming(SCHOOL,v,r)
    if cid=="object-functions":
        target,id,en=FUNCTIONS[(v*4+r)%len(FUNCTIONS)]
        # Exclude plausible alternate tools from the distractor set for each prompt.
        blockers={"bed":{"chair"},"chair":{"bed","table"},"pencil":{"ruler"},
                  "table":{"bed","chair"},"bag":{"cup"},"plate":{"cup","spoon"},
                  "cup":{"plate","spoon"},"spoon":{"cup","plate","trowel"}}
        pool=[x for x in [a[0] for a in FUNCTIONS] if x not in blockers.get(target,set())]
        return single(target,pool,(id,en),v*4+r,4)
    if cid=="living-nonliving":return living_round(v,r)
    if cid=="plant-needs":return fixed_scenario(PLANTS,v,r)
    if cid=="weather-choices":return fixed_scenario(WEATHER,v,r)
    if cid=="math-more-less":return compare_round(v,r)
    if cid=="math-equal":return compare_round(v,r,True)
    if cid=="number-neighbors":return neighbors(v,r)
    if cid=="math-stories":return stories(v,r)
    raise ValueError(cid)


def notes(group,cid):
    if group=="family":return FAMILY_NOTE
    if group=="social":return SOCIAL_NOTE
    if group=="space":return SPACE_NOTE
    if cid=="five-senses":return SENSE_NOTE
    if cid=="living-nonliving":return T("Pilih contoh yang jelas. Tumbuhan dan hewan hidup; batu, es, dan benda buatan tak hidup. Tidak memakai daun lepas, makanan, atau biji untuk penilaian ini.","Use clear examples. Plants and animals are living; rocks, ice, and manufactured objects are nonliving. Detached leaves, food, and seeds are not used for this sorting task.")
    if cid=="plant-needs":return T("Air dan cahaya hanyalah sebagian kebutuhan tumbuhan. Tumbuhan juga memerlukan udara, unsur hara, dan kondisi yang sesuai. Rawat tanaman bersama orang dewasa.","Water and light are only some plant needs. Plants also need air, nutrients, and suitable conditions. Care for plants with an adult.")
    if group=="numbers":return T("Gunakan benda nyata atau gambar untuk membantu menghitung. Bacakan ceritanya; anak tidak harus membaca sendiri. Waktu pengerjaan tidak dinilai.","Use real objects or pictures to help with counting. Read the story aloud; children do not need to read independently. Working speed is not assessed.")
    return GENERIC_NOTE


def offscreen(group):
    return {
        "space":T("Buka buku planet bersama. Pilih satu nama planet untuk diceritakan kembali.","Look at a planet book together. Choose one planet name to talk about."),
        "body":T("Ceritakan satu cara merawat tubuh yang terasa nyaman. Anak boleh menunjuk gambar atau bercerita.","Talk about one comfortable way to care for the body. Children may point to a picture or tell a story."),
        "family":T("Jika anak ingin, sebutkan orang-orang yang merawatnya dengan panggilan yang biasa dipakai.","If the child wants, name the people who care for them using their familiar names."),
        "social":T("Mainkan cerita dengan boneka. Coba beberapa ucapan atau pilih berhenti sejenak.","Act out the story with toys. Try a few phrases or choose to pause."),
        "everyday":T("Cari satu benda yang aman di sekitar. Ceritakan nama dan kegunaannya bersama.","Find one safe object nearby. Talk about its name and use together."),
        "science":T("Amati halaman atau jendela bersama. Ceritakan satu hal yang kamu lihat.","Look outside together. Talk about one thing you notice."),
        "numbers":T("Gunakan hingga enam benda aman. Susun, hitung, dan ceritakan jumlahnya bersama.","Use up to six safe objects. Arrange them, count, and talk about the amounts together."),
    }[group]


def build():
    categories=[]
    worksheets=[]
    for cid,group,engine,age,asset,ti,te,di,de in CATEGORY_SPECS:
        category={"id":cid,"group":group,"engine":engine,"age":age,"ageRange":[age,6],
                  "asset":asset,"title":T(ti,te),"description":T(di,de),"worksheetCount":24}
        categories.append(category)
        for v in range(24):
            rounds=[round_for(cid,v,r) for r in range(4)]
            worksheet={"id":f"{cid}-{v+1:02d}","category":cid,"engine":engine,
                       "title":T(ti,te),"variant":v+1,"difficulty":1+v//8,
                       "age":age,"ageRange":[age,6],"rounds":rounds,
                       "note":notes(group,cid),"offscreen":offscreen(group)}
            worksheet.update(copy.deepcopy(rounds[0]))
            worksheets.append(worksheet)
    return categories,worksheets


def validate(categories,worksheets):
    errors=[]
    def check(condition,message):
        if not condition:errors.append(message)
    def bilingual(obj,where):
        check(isinstance(obj,dict) and all(isinstance(obj.get(x),str) and obj[x].strip() for x in ("id","en")),f"{where}: missing bilingual text")
    check(len(categories)==20,"Expected exactly 20 categories")
    check(len(worksheets)==480,"Expected exactly 480 worksheets")
    counts=Counter(w["category"] for w in worksheets)
    check(len({w["id"] for w in worksheets})==480,"Duplicate worksheet IDs")
    check(len({c["id"] for c in categories})==20,"Duplicate category IDs")
    checks=0
    for c in categories:
        check(counts[c["id"]]==24,f"{c['id']}: wrong worksheet count")
        check(c["worksheetCount"]==24,f"{c['id']}: wrong displayed count")
        check(2<=c["age"]<=5,f"{c['id']}: invalid minimum age")
        check(c["asset"] in NAMES,f"{c['id']}: unsupported category asset")
        unique_round_sets={json.dumps(w["rounds"],sort_keys=True,ensure_ascii=False) for w in worksheets if w["category"]==c["id"]}
        check(len(unique_round_sets)==24,f"{c['id']}: exact repeated worksheet round set")
        bilingual(c["title"],c["id"]+" title");bilingual(c["description"],c["id"]+" description")
    for w in worksheets:
        check(len(w["rounds"])==4,f"{w['id']}: expected four rounds")
        for k,val in w["rounds"][0].items():check(w[k]==val,f"{w['id']}: top-level {k} does not equal round 1")
        bilingual(w["note"],w["id"]+" note");bilingual(w["offscreen"],w["id"]+" offscreen")
        for ri,r in enumerate(w["rounds"]):
            where=f"{w['id']} round {ri+1}"
            checks+=1
            bilingual(r["instruction"],where)
            options=r["options"];byid={o["id"]:o for o in options}
            check(3<=len(options)<=6,where+": option count out of range")
            check(len(byid)==len(options),where+": duplicate option IDs")
            for o in options+r.get("rightOptions",[])+([r["reference"]] if "reference" in r else [])+[p for p in r.get("patternItems",[]) if p]:
                bilingual(o["label"],where+" label")
                for key in ("asset","groupAsset"):
                    if key in o:check(o[key] in NAMES,where+": unsupported asset "+o[key])
            e=r["_expected"]
            if w["engine"]=="pair":
                right={o["id"]:o for o in r["rightOptions"]}
                check(len(r["pairs"])==len(options)==len(right),where+": incomplete pairs")
                check(len({p["right"] for p in r["pairs"]})==len(right),where+": duplicate right pair")
                for p in r["pairs"]:
                    check(p["left"] in byid and p["right"] in right,where+": pair references missing option")
                    check(byid[p["left"]]["asset"]==right[p["right"]]["asset"],where+": mismatched pair asset")
                    check(byid[p["left"]]["label"]==right[p["right"]]["label"],where+": mismatched pair label")
                continue
            check(len(r["answer"])>0,where+": empty answer")
            check(set(r["answer"])<=set(byid),where+": answer missing from options")
            actual=[byid[a] for a in r["answer"]]
            if e["kind"]=="assets":
                check(Counter(o["asset"] for o in actual)==Counter(e["assets"]),where+": semantic asset answer mismatch")
            elif e["kind"]=="caption":
                check(len(actual)==1 and actual[0]["label"]==e["correct"],where+": wrong dialogue answer")
                check(all(o.get("showLabel") for o in options),where+": dialogue labels hidden")
                check(r.get("layout")=="story-choices",where+": dialogue layout missing")
            elif e["kind"]=="living":
                want=set(LIVING if e["wantLiving"] else NONLIVING)
                expected={o["id"] for o in options if o["asset"] in want}
                check(set(r["answer"])==expected,where+": living classification mismatch")
            elif e["kind"]=="compare":
                val=(max if e["most"] else min)(o["value"] for o in options)
                check({o["id"] for o in options if o["value"]==val}==set(r["answer"]),where+": comparison mismatch")
                check(len(r["answer"])==1,where+": comparison tie")
            elif e["kind"]=="equal":
                val=r["reference"]["value"]
                check({o["id"] for o in options if o["value"]==val}==set(r["answer"]),where+": equality mismatch")
            elif e["kind"]=="neighbors":
                pattern=r["patternItems"]
                missing=[i for i,p in enumerate(pattern) if p is None]
                check(len(missing)==1,where+": gap count wrong")
                m=missing[0]
                expected=pattern[m-1]["value"]+1 if m else pattern[1]["value"]-1
                check(actual[0]["value"]==expected,where+": number-neighbor mismatch")
                rebuilt=[expected if p is None else p["value"] for p in pattern]
                check(all(b-a==1 for a,b in zip(rebuilt,rebuilt[1:])),where+": sequence not consecutive")
            elif e["kind"]=="story":
                a,b=r["operands"]
                expected=a+b if r["operation"]=="add" else a-b
                check(actual[0]["value"]==expected and 0<=expected<=5,where+": arithmetic mismatch")
                check("countTarget" not in r,where+": result exposed as count scene")
            if w["category"].startswith("family-"):
                for o in options:check(o.get("showLabel") and o["label"]==T(*NAMES[o["asset"]]),where+": family role not explicit")
    return {"status":"pass" if not errors else "fail","categories":len(categories),
            "worksheets":len(worksheets),"rounds":checks,"worksheetsPerCategory":dict(counts),
            "errors":errors,"checks":["exact counts and unique stable IDs","bilingual content","3–6 options",
             "supported assets only","round 1 normalization","answer references","pair bijection and exact match",
             "living/nonliving classification","unique numerical comparisons","equal quantities",
             "number sequence gaps","arithmetic results 0–5","explicit social and family labels"]}


def clean(obj):
    if isinstance(obj,dict):return {k:clean(v) for k,v in obj.items() if not k.startswith("_")}
    if isinstance(obj,list):return [clean(v) for v in obj]
    return obj


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out",type=Path,default=Path(__file__).resolve().parent)
    args=parser.parse_args();args.out.mkdir(parents=True,exist_ok=True)
    categories,worksheets=build()
    audit=validate(categories,worksheets)
    if audit["errors"]:
        raise SystemExit(json.dumps(audit,ensure_ascii=False,indent=2))
    outputs={"expansion-categories.json":categories,"expansion-worksheets.json":clean(worksheets),"semantic-audit.json":audit}
    hashes={}
    for name,data in outputs.items():
        payload=json.dumps(data,ensure_ascii=False,separators=(",",":"))+"\n"
        (args.out/name).write_text(payload,encoding="utf-8")
        hashes[name]=hashlib.sha256(payload.encode()).hexdigest()
    manifest={"schema":"normalized Worksheet with root equal to first round", "categoryCount":20,
              "worksheetCount":480,"roundCount":1920,"existingIds":"untouched; this generator writes expansion files only",
              "sourceFacts":[{"title":"NASA: About the Planets","url":"https://science.nasa.gov/solar-system/planets/","supports":"eight planet names, ordinal positions, Mercury nearest/smallest, Jupiter largest, Neptune farthest"},
                             {"title":"NASA: Earth Facts","url":"https://science.nasa.gov/earth/facts/","supports":"home planet, land and oceans"},
                             {"title":"NASA: Mars Facts","url":"https://science.nasa.gov/mars/facts/","supports":"Red Planet nickname"},
                             {"title":"NASA: Saturn Facts","url":"https://science.nasa.gov/saturn/facts/","supports":"prominent ring system"}],
              "illustrations":"not to scale; no answer relies on exact color, distance, or physical planet size", "sha256":hashes}
    (args.out/"expansion-manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({"status":audit["status"],"categories":20,"worksheets":480,"rounds":1920,"errors":len(audit["errors"]),"out":str(args.out)}))


if __name__=="__main__":main()
