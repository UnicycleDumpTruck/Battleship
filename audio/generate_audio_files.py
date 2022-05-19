import json
import gtts
import fleet

for i in range(1, fleet.GRID_SIZE + 1):
    gtts.gTTS(i).save(f"audio/{str(i)}.mp3")
    i_char = chr(i + 97)
    gtts.gTTS(i_char).save(f"audio/{i_char}.mp3")

for ship in fleet.ship_sizes.keys():
    gtts.gTTS(ship).save(f"audio/{ship}.mp3")

with open("audio_phrases.json", "r") as phrases_file:
    audio_txt = json.load(phrases_file)

for key, value in audio_txt.items():
    gtts.gTTS(value).save(f"{key}.mp3")
