import re
from itertools import permutations

# Flag offuscata
flag = "l_4nb_3cnnbcg3r3slm4Id__gb4u_ct0mr3sds"

# Sostituzione leetspeak
leet_dict = {
    "4": "A", "3": "E", "0": "O", "1": "I"
}

def deobfuscate(text):
    for key, value in leet_dict.items():
        text = text.replace(key, value)
    return text

# Proviamo a sostituire i caratteri
decoded_flag = deobfuscate(flag)

# Proviamo a separare le parole
words = decoded_flag.split("_")

print("Possibile flag deoffuscata:")
print(" ".join(words))
