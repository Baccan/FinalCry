# kill pid process from C:\Program Files (x86)\Spectre\FinalCry\pid.txt

import os
import signal
import sys
import win32api

from winotify import Notification, audio

pid = open(r'C:\Program Files (x86)\Spectre\FinalCry\pid.txt', 'r')
pid = pid.read()
pid = int(pid)
os.kill(pid, signal.SIGTERM)

toast = Notification(app_id="Final Cry",
                     title="Encerrando a aplicação",
                     msg="O Final Cry foi encerrado com sucesso...",
                     duration='long',
                     icon=r"C:\Program Files (x86)\Spectre\Spectre.ico")

toast.set_audio(audio.Mail, loop=False)
toast.show()

win32api.MessageBox(0, 'A aplicação foi finalizada com sucesso...', 'Final Cry', 0x00001000)

sys.exit()