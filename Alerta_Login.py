import subprocess
import requests
import re
import time
import threading
import os

# --- CONFIGURAÇÕES ---
TOKEN_TELEGRAM = "6835420667:AAG49VWwrf0J1H4K_ejG50ivBsApzh-S8Po"
CHAT_ID_TELEGRAM = "7239458170"

# Controles de estado
foto_inicial_enviada = False
ultima_foto_falha = 0
COOLDOWN_FOTO_FALHA = 60  # segundos entre fotos de falha de login


def enviar_alerta_simples(titulo, mensagem):
    url = f"https://api.telegram.org/bot{TOKEN_TELEGRAM}/sendMessage"
    payload = {
        "chat_id": CHAT_ID_TELEGRAM,
        "text": f"{titulo}\n\n{mensagem}",
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"[-] Erro ao enviar alerta simples: {e}")


def enviar_foto_telegram(legenda):
    """Captura uma foto usando a webcam local e envia pelo Telegram."""
    caminho_foto = "/tmp/intruso.jpg"
    print("[*] 📸 Capturando imagem do operador local...")

    comando_camera = ["fswebcam", "-r", "640x480", "--jpeg", "85",
                      "--skip", "2", "--quiet", caminho_foto]

    try:
        subprocess.run(comando_camera, check=True)
        if os.path.exists(caminho_foto):
            url = f"https://api.telegram.org/bot{TOKEN_TELEGRAM}/sendPhoto"
            with open(caminho_foto, "rb") as foto:
                files = {"photo": foto}
                data = {
                    "chat_id": CHAT_ID_TELEGRAM,
                    "caption": legenda,
                    "parse_mode": "Markdown"
                }
                requests.post(url, data=data, files=files)
            os.remove(caminho_foto)
            print("[+] Foto enviada com sucesso!")
    except Exception as e:
        print(f"[-] Falha ao usar a webcam: {e}")


def foto_de_falha(linha_log):
    """Tira foto em falha de login, respeitando cooldown para não spammar."""
    global ultima_foto_falha
    agora = time.time()
    if agora - ultima_foto_falha < COOLDOWN_FOTO_FALHA:
        return
    ultima_foto_falha = agora
    enviar_foto_telegram(
        f"🚨 **Falha de Login Detectada!**\n\n`{linha_log}`"
    )


def monitorar_journalctl():
    global foto_inicial_enviada
    print("[*] CENTRAL SOC ATIVADA...")

    enviar_alerta_simples(
        "🚀 **SOC: Sistema Inicializado**",
        "O monitor de segurança subiu junto com o sistema."
    )
    enviar_foto_telegram(
        "📸 **Verificação Física de Inicialização**\n\n"
        "Dispositivo ligado/reiniciado com sucesso."
    )
    foto_inicial_enviada = True

    comando = ["journalctl", "-f", "-n", "0"]
    processo = subprocess.Popen(
        comando, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )

    for _, linha in enumerate(processo.stdout):
        linha = linha.strip()
        linha_min = linha.lower()

        # --- REBOOT / SHUTDOWN / DESLIGAMENTO GRÁFICO ---
        if (
            "systemd-shutdown" in linha_min
            or "reboot:" in linha_min
            or "systemd-logind" in linha_min and "power" in linha_min
            or "systemd-logind" in linha_min and "reboot" in linha_min
            or "gnome-session" in linha_min and "shutdown" in linha_min
            or "gnome-session" in linha_min and "reboot" in linha_min
        ):
            enviar_alerta_simples(
                "⚠️ **AVISO: Sistema sendo Encerrado/Rebootado**",
                f"`{linha}`"
            )
            continue

        # --- AUTENTICAÇÃO LOCAL (PAM / GDM / LIGHTDM) ---
        if (
            "pam_unix" in linha_min
            or "gdm-password" in linha_min
            or "lightdm" in linha_min
        ):
            # Sucesso no login local
            if "session opened" in linha_min and "root" not in linha_min:
                usuario = re.search(r'user\s+([a-zA-Z0-9_-]+)', linha)
                user_str = usuario.group(1) if usuario else "Usuário Local"
                enviar_alerta_simples(
                    "🔓 **ALERTA: Login efetuado na Máquina**",
                    f"Sessão local aberta com sucesso.\n👤 **Usuário:** `{user_str}`"
                )
                enviar_foto_telegram(
                    f"📸 **Login Local Bem-sucedido**\n\n"
                    f"👤 **Usuário:** `{user_str}`"
                )

            # Falha de autenticação local
            elif (
                "authentication failure" in linha_min
                or "check pass; user unknown" in linha_min
            ):
                if "sshd" in linha_min:
                    continue
                enviar_alerta_simples(
                    "🚨 **ALERTA: Falha de Autenticação Local**",
                    f"Tentativa incorreta de login local:\n`{linha}`"
                )
                foto_de_falha(linha)


if __name__ == "__main__":
    monitorar_journalctl()
