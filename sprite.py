from pathlib import Path
from PIL import Image


suits = ["hearts", "diamonds", "spades", "clubs"]
values = [
  "2", "3", "4", "5", "6", "7", "8", "9", "10",
  "jack", "queen", "king", "ace"
]

images = [Path(f'./public/game/cards/{val}_of_{suit}.png') for suit in suits for val in values]
print(images)
w, h = (110, 160)
sprite = Image.new('RGBA', (w*14, h*(4+1)))
for i, image in enumerate(images):
    with Image.open(image) as img:
        suit, value = i // 13, i % 13
        sprite.paste(img.resize((w, h)), (value*w, suit*h))
with Image.open('./public/game/cards/back.png') as back:
    sprite.paste(back.resize((w, h)), (0, 4*h))
with Image.open('./public/game/cards/black_joker.png') as black_joker:
    sprite.paste(black_joker.resize((w, h)), (1*w, 4*h))
with Image.open('./public/game/cards/red_joker.png') as red_joker:
    sprite.paste(red_joker.resize((w, h)), (2*w, 4*h))
aces = [Path(f'./public/game/cards/mirror_of_{suit}.png') for suit in suits]
print(aces)
for i, path in enumerate(aces):
    with Image.open(path) as img:
        print(i)
        sprite.paste(img.resize((w, h)), (13*w, i*h))
    

# sprite.show()
sprite.save("public/game/cards.png")
