import sys
sys.path.append('/workspaces/InteractionFreePy/InteractionFreePy')

from interactionfreepy import IFWorker, IFLoop

worker = IFWorker('interactionfree.cn:1061')
print(worker.protocol())

class DragonCipher:
  def encrypt_to_dragon_speech(self, text: str) -> str:
    result = []
    for char in text:
      lower_char = char.lower()
      if lower_char in {'a', 'e', 'i', 'o', 'u'}:
        new_char = '*'
      elif char.isalpha():
        new_char = f"{char}-ar" if char.isupper() else f"{char}-ar"
      else:
        new_char = char
      result.append(new_char)
    return ''.join(result)
  
dragon_cipher = DragonCipher()
worker.bindService('DragonCipher_Alice', dragon_cipher)

import time
time.sleep(5)

from interactionfreepy import IFWorker

worker = IFWorker('tcp://interactionfree.cn:1061')
print(worker.listServiceNames())
humam_speech = 'To be or not to be'
dragon_speech = worker.DragonCipher_Alice.encrypt_to_dragon_speech(humam_speech)
print(f'{humam_speech} -> {dragon_speech}')