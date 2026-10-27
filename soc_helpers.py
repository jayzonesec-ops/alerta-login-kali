# /opt/soc/soc_helpers.py
import subprocess
import re
import requests
import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega o .env da mesma pasta onde este arquivo está (/opt/soc/.env)
caminho_env = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=caminho_env)

TOKEN_TELEGRAM = os.getenv("TOKEN_TELEGRAM")
CHAT_ID_TELEGRAM = os.getenv("CHAT_ID_TELEGRAM")

if not TOKEN_TELEGRAM or not CHAT_ID_TELEGRAM:
    raise RuntimeError(
        "Credenciais do Telegram não configuradas. "
        "Certifique-se de que /opt/soc/.env contém TOKEN_TELEGRAM e CHAT_ID_TELEGRAM."
    )

IPTABLES = "/usr/sbin/iptables"

def listar_ips_bloqueados():
    """
    Retorna lista de IPs com regra DROP no INPUT.
    Usa iptables -S INPUT e filtra.
    """
    try:
        r = subprocess.run(
            [IPTABLES, "-S", "INPUT"],
            capture_output=True, text=True, timeout=10
        )
        if r.returncode != 0:
            print(f"[-] iptables -S falhou: {r.stderr}")
            return []
    except Exception as e:
        print(f"[-] Erro ao executar iptables: {e}")
        return []

    ips = []
    padrao = re.compile(r'-A INPUT -s (\d{1,3}(?:\.\d{1,3}){3})(?:/\d+)? -j DROP')
    for linha in r.stdout.splitlines():
        m = padrao.search(linha)
        if m:
            ips.append(m.group(1))
    return sorted(set(ips))

def montar_teclado_desbloqueio(ips):
    """
    Monta teclado inline com botões verdes de desbloqueio, um por IP.
    Se lista vazia, retorna None.
    """
    if not ips:
        return None
    botoes = []
    for ip in ips:
        botoes.append([{
            "text": f"✅ Desbloquear {ip}",
            "callback_data": f"desbloquear_{ip}"
        }])
    return {"inline_keyboard": botoes}

def enviar_lista_bloqueados(cabecalho="🔐 **IPs Bloqueados no SSH**"):
    """
    Envia mensagem com a lista atual de IPs bloqueados e botões de desbloqueio.
    Se não houver nenhum, envia mensagem informando lista vazia (sem botões).
    """
    ips = listar_ips_bloqueados()
    teclado = montar_teclado_desbloqueio(ips)

    if not ips:
        texto = f"{cabecalho}\n\n_Nenhum IP bloqueado no momento._"
    else:
        linhas = "\n".join([f"• `{ip}`" for ip in ips])
        texto = f"{cabecalho}\n\n{linhas}\n\nClique em ✅ para desbloquear."

    payload = {
        "chat_id": CHAT_ID_TELEGRAM,
        "text": texto,
        "parse_mode": "Markdown"
    }
    if teclado:
        payload["reply_markup"] = teclado

    try:
        requests.post(
            f"https://api.telegram.org/bot{TOKEN_TELEGRAM}/sendMessage",
            json=payload, timeout=10
        )
    except Exception as e:
        print(f"[-] Erro ao enviar lista: {e}")

def desbloquear_ip(ip):
    """Remove a regra DROP do INPUT. Retorna True se removeu."""
    if not re.fullmatch(r'(?:\d{1,3}\.){3}\d{1,3}', ip or ''):
        return False
    try:
        r = subprocess.run(
            [IPTABLES, "-D", "INPUT", "-s", ip, "-j", "DROP"],
            capture_output=True, text=True, timeout=10
        )
        if r.returncode == 0:
            # Persiste a mudança
            try:
                subprocess.run(["netfilter-persistent", "save"], timeout=15)
            except Exception:
                pass
            return True
        print(f"[-] iptables -D falhou: {r.stderr}")
        return False
    except Exception as e:
        print(f"[-] Erro ao desbloquear: {e}")
        return False
