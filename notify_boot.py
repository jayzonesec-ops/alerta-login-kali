#!/usr/bin/env python3
# /opt/soc/soc-notify-boot.py
import subprocess
import requests
import os
import time
import sys

sys.path.insert(0, "/opt/soc")
from soc_helpers import (
    TOKEN_TELEGRAM, CHAT_ID_TELEGRAM,
    enviar_lista_bloqueados
)

def enviar_alerta_simples(titulo, mensagem):
    url = f"https://api.telegram.org/bot{TOKEN_TELEGRAM}/sendMessage"
    payload = {
        "chat_id": CHAT_ID_TELEGRAM,
        "text": f"{titulo}\n\n{mensagem}",
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"[-] Erro: {e}")

def enviar_foto_telegram(legenda):
    caminho = "/tmp/intruso.jpg"
    try:
        subprocess.run(
            ["fswebcam", "-r", "640x480", "--jpeg", "85",
             "--skip", "2", "--quiet", caminho],
            check=True, timeout=15
        )
        if os.path.exists(caminho):
            url = f"https://api.telegram.org/bot{TOKEN_TELEGRAM}/sendPhoto"
            with open(caminho, "rb") as f:
                requests.post(
                    url,
                    data={"chat_id": CHAT_ID_TELEGRAM,
                          "caption": f"📸 **Verificação Física**\n\n{legenda}",
                          "parse_mode": "Markdown"},
                    files={"photo": f},
                    timeout=30
                )
            os.remove(caminho)
    except Exception as e:
        print(f"[-] Webcam: {e}")

if __name__ == "__main__":
    enviar_alerta_simples(
        "🚀 **SOC: Sistema Inicializado**",
        "O HIDS/SOAR tático acabou de subir."
    )
    enviar_foto_telegram("Dispositivo Kali Linux ligado/reiniciado.")
    time.sleep(2)  # pequena pausa para a foto chegar antes
    enviar_lista_bloqueados("🔐 **IPs Bloqueados no SSH (estado atual)**")
