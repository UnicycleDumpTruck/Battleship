import json
import gtts
import fleet

for i in range(1, fleet.GRID_SIZE + 1):
    gtts.gTTS(str(i)).save(f"audio/{str(i)}.mp3")
    i_char = chr(i + 96)
    gtts.gTTS(i_char).save(f"audio/{i_char}.mp3")

for ship in fleet.ship_sizes.keys():
    gtts.gTTS(ship).save(f"audio/{ship}.mp3")

with open("audio_phrases.json", "r") as phrases_file:
    audio_txt = json.load(phrases_file)
for key, value in audio_txt.items():
    gtts.gTTS(value).save(f"audio/{key}.mp3")

# "Deploy your ships"
for ship in fleet.ship_sizes.keys():
    gtts.gTTS(f"Deploy your {ship}.").save(f"audio/deploy_your_{ship}.mp3")

# You sunk a ...
for ship in fleet.ship_sizes.keys():
    gtts.gTTS(f"You've sunk my {ship}.").save(f"audio/you_sunk_{ship}.mp3")

# Your ... was sunk
for ship in fleet.ship_sizes.keys():
    gtts.gTTS(f"Your {ship} has been sunk.").save(f"audio/your_{ship}_sunk.mp3")
