import subprocess
import requests
import re
import time
import threading
import os
import sys

# Adiciona o diretório do script ao PATH para importar o soc_helpers
sys.path.insert(0, "/opt/soc")
from soc_helpers import (
    TOKEN_TELEGRAM,
    CHAT_ID_TELEGRAM,
    desbloquear_ip,
    enviar_lista_bloqueados
)

# --- CONFIGURAÇÕES ---
NOME_SCRIPT = os.path.basename(__file__)
COOLDOWN_ALERTA_IP = 60
_ultimo_alerta_ip = {}
foto_tirada = False

# Caminho absoluto do iptables (evita falha de PATH no systemd)
IPTABLES = "/usr/sbin/iptables"

# ---------------------------------------------------------------------------
# UTILITÁRIOS
# ---------------------------------------------------------------------------

def extrair_ip(texto_log):
    padrao_ip = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
    resultado = re.search(padrao_ip, texto_log)
    return resultado.group(0) if resultado else None

def pode_alertar_ip(ip):
    """Retorna True se o IP ainda não foi alertado nos últimos N segundos."""
    agora = time.time()
    ultimo = _ultimo_alerta_ip.get(ip, 0)
    if agora - ultimo < COOLDOWN_ALERTA_IP:
        return False
    _ultimo_alerta_ip[ip] = agora
    return True

# ---------------------------------------------------------------------------
# TELEGRAM - ENVIO
# ---------------------------------------------------------------------------

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
        print(f"[-] Erro ao enviar alerta simples: {e}")

def enviar_alerta_com_botao(titulo, mensagem, ip_alvo):
    url = f"https://api.telegram.org/bot{TOKEN_TELEGRAM}/sendMessage"
    botoes = {
        "inline_keyboard": [[
            {"text": f"❌ Bloquear IP {ip_alvo}", "callback_data": f"bloquear_{ip_alvo}"}
        ]]
    }
    payload = {
        "chat_id": CHAT_ID_TELEGRAM,
        "text": f"{titulo}\n\n{mensagem}\n\n**Deseja banir o IP {ip_alvo} do sistema?**",
        "parse_mode": "Markdown",
        "reply_markup": botoes
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"[-] Erro ao enviar mensagem interativa: {e}")

def enviar_foto_telegram(legenda):
    """Captura uma foto usando a webcam local (usado apenas sob demanda)."""
    global foto_tirada
    if foto_tirada:
        return

    caminho_foto = "/tmp/intruso.jpg"
    print("[*] 📸 Capturando imagem do operador local...")

    comando_camera = [
        "fswebcam", "-r", "640x480", "--jpeg", "85",
        "--skip", "2", "--quiet", caminho_foto
    ]

    try:
        subprocess.run(comando_camera, check=True, timeout=15)
        if os.path.exists(caminho_foto):
            url = f"https://api.telegram.org/bot{TOKEN_TELEGRAM}/sendPhoto"
            with open(caminho_foto, "rb") as foto:
                files = {"photo": foto}
                data = {
                    "chat_id": CHAT_ID_TELEGRAM,
                    "caption": f"📸 **Verificação Física**\n\n{legenda}",
                    "parse_mode": "Markdown"
                }
                requests.post(url, data=data, files=files, timeout=30)
            os.remove(caminho_foto)
            foto_tirada = True
            print("[+] Foto enviada com sucesso!")
    except Exception as e:
        print(f"[-] Falha ao usar a webcam: {e}")

# ---------------------------------------------------------------------------
# IPTABLES - BLOQUEIO
# ---------------------------------------------------------------------------

def executar_bloqueio_iptables(ip):
    if not re.fullmatch(r'(?:\d{1,3}\.){3}\d{1,3}', ip or ''):
        print(f"[-] IP inválido recusado: {ip}")
        return False

    # Verifica se a regra já existe
    try:
        check = subprocess.run(
            [IPTABLES, "-C", "INPUT", "-s", ip, "-j", "DROP"],
            capture_output=True, text=True, timeout=5
        )
        if check.returncode == 0:
            print(f"[*] IP {ip} já está bloqueado. Nada a fazer.")
            return True
    except Exception:
        pass

    # TROCADO: -A para -I INPUT 1 (Insere no topo da lista)
    comandos = [
        [IPTABLES, "-I", "INPUT", "1", "-s", ip, "-j", "DROP"],
        ["sudo", "-n", IPTABLES, "-I", "INPUT", "1", "-s", ip, "-j", "DROP"],
    ]
    
    sucesso = False
    for cmd in comandos:
        try:
            subprocess.run(cmd, check=True, timeout=10)
            print(f"[+] IP {ip} bloqueado via: {' '.join(cmd)}")
            sucesso = True
            break
        except Exception as e:
            print(f"[-] Falha com {' '.join(cmd)}: {e}")
            
    if sucesso:
        # Limpa a conexão atual do invasor para derrubar a sessão ativa
        try:
            subprocess.run(["conntrack", "-D", "--src", ip], timeout=5)
        except Exception:
            pass

        # Persiste a regra
        try:
            subprocess.run(["netfilter-persistent", "save"], timeout=15)
        except Exception as e:
            print(f"[-] Falha ao persistir regra: {e}")
            
    return sucesso

# ---------------------------------------------------------------------------
# THREAD - ESCUTA CALLBACKS DO TELEGRAM
# ---------------------------------------------------------------------------

def escutar_respostas_telegram():
    offset = 0
    print("[*] Thread de escuta do Telegram iniciada.")
    while True:
        url = (f"https://api.telegram.org/bot{TOKEN_TELEGRAM}"
               f"/getUpdates?offset={offset}&timeout=10")
        try:
            response = requests.get(url, timeout=15).json()
            if "result" in response:
                for update in response["result"]:
                    offset = update["update_id"] + 1

                    if "callback_query" not in update:
                        continue

                    callback = update["callback_query"]
                    dados_comando = callback.get("data", "")
                    callback_id = callback["id"]

                    # -------- BLOQUEAR IP --------
                    if dados_comando.startswith("bloquear_"):
                        ip_para_bloquear = dados_comando.replace("bloquear_", "")

                        try:
                            requests.post(
                                f"https://api.telegram.org/bot{TOKEN_TELEGRAM}/answerCallbackQuery",
                                json={
                                    "callback_query_id": callback_id,
                                    "text": f"Processando bloqueio de {ip_para_bloquear}..."
                                },
                                timeout=10
                            )
                        except Exception: pass

                        sucesso = executar_bloqueio_iptables(ip_para_bloquear)

                        msg = f"✅ IP `{ip_para_bloquear}` bloqueado via iptables." if sucesso else f"❌ Falha ao bloquear `{ip_para_bloquear}`."
                        
                        try:
                            requests.post(
                                f"https://api.telegram.org/bot{TOKEN_TELEGRAM}/sendMessage",
                                json={"chat_id": CHAT_ID_TELEGRAM, "text": msg, "parse_mode": "Markdown"},
                                timeout=10
                            )
                        except Exception: pass

                    # -------- DESBLOQUEAR IP --------
                    elif dados_comando.startswith("desbloquear_"):
                        ip_para_desbloquear = dados_comando.replace("desbloquear_", "")

                        try:
                            requests.post(
                                f"https://api.telegram.org/bot{TOKEN_TELEGRAM}/answerCallbackQuery",
                                json={
                                    "callback_query_id": callback_id,
                                    "text": f"Desbloqueando {ip_para_desbloquear}..."
                                },
                                timeout=10
                            )
                        except Exception: pass

                        sucesso = desbloquear_ip(ip_para_desbloquear)

                        msg = f"✅ IP `{ip_para_desbloquear}` desbloqueado com sucesso." if sucesso else f"❌ Falha ao desbloquear `{ip_para_desbloquear}`.\nVerifique permissões e se a regra existia."
                        
                        try:
                            requests.post(
                                f"https://api.telegram.org/bot{TOKEN_TELEGRAM}/sendMessage",
                                json={"chat_id": CHAT_ID_TELEGRAM, "text": msg, "parse_mode": "Markdown"},
                                timeout=10
                            )
                        except Exception: pass

                        # Reenvia a lista atualizada de IPs bloqueados
                        enviar_lista_bloqueados("🔐 **Lista Atualizada de IPs Bloqueados**")

        except requests.exceptions.RequestException as e:
            print(f"[-] Erro de rede no polling do Telegram: {e}")
        except Exception as e:
            print(f"[-] Erro inesperado na thread Telegram: {e}")

        time.sleep(1)

# ---------------------------------------------------------------------------
# MONITOR PRINCIPAL - journalctl -f
# ---------------------------------------------------------------------------

def monitorar_journalctl():
    print("[*] CENTRAL SOC AVANÇADA ATIVADA...")

    comando = ["journalctl", "-f", "-n", "0"]
    processo = subprocess.Popen(
        comando,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )

    try:
        for linha in processo.stdout:
            linha = linha.strip()
            if not linha:
                continue
            linha_min = linha.lower()

            # -------- PARSER DE AUDITORIA SUDO --------
            if "sudo[" in linha_min and "command=" in linha_min:
                if NOME_SCRIPT in linha or "python" in linha_min:
                    continue

                usuario = re.search(r'sudo\[\d+\]:\s+([a-zA-Z0-9_-]+)', linha)
                pwd = re.search(r'PWD=([^;\s]+)', linha)
                comando_executado = re.search(r'COMMAND=(.+)$', linha)
                pid = re.search(r'sudo\[(\d+)\]', linha)

                user_str = usuario.group(1) if usuario else "Desconhecido"
                pwd_str = pwd.group(1) if pwd else "Desconhecido"
                cmd_str = comando_executado.group(1) if comando_executado else "Desconhecido"
                pid_str = pid.group(1) if pid else "0"

                msg_formatada = (
                    f"👤 **Usuário:** `{user_str}` (PID: `{pid_str}`)\n"
                    f"📂 **Diretório:** `{pwd_str}`\n"
                    f"⚙️ **Comando:** `{cmd_str}`"
                )
                enviar_alerta_simples("👑 **INFO: Comando Executado via SUDO**", msg_formatada)

            # -------- AUDITORIA SSH --------
            elif "sshd" in linha_min:
                if "accepted password" in linha_min or "accepted publickey" in linha_min:
                    ip = extrair_ip(linha)
                    usuario = re.search(r'for\s+([a-zA-Z0-9_-]+)\s+from', linha)
                    user_str = usuario.group(1) if usuario else "Desconhecido"
                    msg = (
                        f"🟢 **Acesso Autorizado via SSH**\n\n"
                        f"👤 **Usuário:** `{user_str}`\n"
                        f"🌐 **IP de Origem:** `{ip}`"
                    )
                    enviar_alerta_simples("🔑 **SSH: Sessão Iniciada**", msg)

                elif "disconnected from user" in linha_min:
                    ip = extrair_ip(linha)
                    usuario = re.search(r'disconnected from user\s+([a-zA-Z0-9_-]+)', linha)
                    user_str = usuario.group(1) if usuario else "Desconhecido"
                    msg = (
                        f"⚪ **Sessão Finalizada**\n\n"
                        f"👤 **Usuário:** `{user_str}`\n"
                        f"🌐 **IP:** `{ip}`"
                    )
                    enviar_alerta_simples("🚪 **SSH: Conexão Encerrada**", msg)

                elif "failed password" in linha_min or "invalid user" in linha_min:
                    ip = extrair_ip(linha)
                    if ip and pode_alertar_ip(ip):
                        msg = f"⚠️ **Tentativa de Invasão Detectada!**\n\n`{linha}`"
                        enviar_alerta_com_botao("🔒 **SSH: Bloqueio Disponível**", msg, ip)

            # -------- AUTENTICAÇÃO LOCAL (PAM / GDM / LIGHTDM) --------
            elif ("pam_unix" in linha_min or "gdm-password" in linha_min or "lightdm" in linha_min):
                if "session opened" in linha_min and "root" not in linha_min:
                    usuario = re.search(r'user\s+([a-zA-Z0-9_-]+)', linha)
                    user_str = usuario.group(1) if usuario else "Usuário Local"
                    enviar_alerta_simples(
                        "🔓 **ALERTA: Login efetuado na Máquina**",
                        f"Sessão local aberta com sucesso.\n👤 **Usuário:** `{user_str}`"
                    )
                elif "authentication failure" in linha_min or "check pass; user unknown" in linha_min:
                    if "sshd" in linha_min:
                        continue
                    enviar_alerta_simples(
                        "🚨 **ALERTA: Falha de Autenticação Local**",
                        f"Tentativa incorreta de login local:\n`{linha}`"
                    )

            # -------- DESLIGAMENTO / REBOOT --------
            elif "systemd-shutdown" in linha_min or "reboot:" in linha_min:
                enviar_alerta_simples(
                    "⚠️ **AVISO: O Sistema está sendo Encerrado/Rebootado**",
                    linha
                )

    except KeyboardInterrupt:
        print("[*] Interrompido pelo usuário.")
    finally:
        processo.terminate()
        try:
            processo.wait(timeout=5)
        except subprocess.TimeoutExpired:
            processo.kill()

# ---------------------------------------------------------------------------
# ENTRYPOINT
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    threading.Thread(target=escutar_respostas_telegram, daemon=True).start()
    monitorar_journalctl()
