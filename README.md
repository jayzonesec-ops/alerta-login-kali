# 🛡️ Alerta Login Kali

> Script em Python que monitora eventos de segurança do sistema e envia alertas em tempo real para o **Telegram** — com **foto do operador local** capturada pela webcam. Detecta inicialização do sistema, login local (sucesso e falha) e desligamento/reboot, inclusive via interface gráfica.

![Versão](https://img.shields.io/badge/versão-1.0-blue?style=for-the-badge)
![Plataforma](https://img.shields.io/badge/plataforma-Linux-333?style=for-the-badge&logo=linux&logoColor=white)
![Python](https://img.shields.io/badge/python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Telegram](https://img.shields.io/badge/telegram-bot-26A5E4?style=for-the-badge&logo=telegram&logoColor=white)
![Systemd](https://img.shields.io/badge/systemd-journal-000?style=for-the-badge&logo=systemd&logoColor=white)
![Licença](https://img.shields.io/badge/licença-MIT-green?style=for-the-badge)

---

> [!NOTE]
> O **Alerta Login Kali** é um HIDS/SOAR tático minimalista: ele lê o `journalctl` em tempo real e, sempre que detecta um evento relevante (boot, login local, falha de autenticação, shutdown/reboot), envia uma mensagem no Telegram. Nos eventos críticos, **tira uma foto pela webcam** para identificar quem estava na frente da máquina.
>
> O script é iniciado automaticamente no boot via `cron @reboot`, mas também pode ser executado manualmente para testes.

---

## 📋 Índice

- [Sobre o Projeto](#-sobre-o-projeto)
- [Funcionalidades](#-funcionalidades)
- [Eventos Monitorados](#-eventos-monitorados)
- [Tecnologias Utilizadas](#-tecnologias-utilizadas)
- [Pré-requisitos](#-pré-requisitos)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Configuração e Execução](#️-configuração-e-execução)
- [Configurando o Bot do Telegram](#-configurando-o-bot-do-telegram)
- [Agendando no Cron](#-agendando-no-cron)
- [Uso](#-uso)
- [Personalização](#-personalização)
- [Limitações Conhecidas](#️-limitações-conhecidas)
- [Solução de Problemas](#-solução-de-problemas)
- [Licença](#-licença)
- [Autor](#-autor)

---

## 🔍 Sobre o Projeto

O **Alerta Login Kali** é um monitor de segurança passivo que roda em segundo plano e notifica o administrador via Telegram sobre eventos sensíveis do sistema operacional. Ele foi criado para monitorar máquinas expostas fisicamente (laboratório, escritório, home office) e responder à pergunta: **"quem ligou, tentou logar ou desligou essa máquina?"**

O script:

- ✅ Envia alerta + **foto** quando o sistema é **inicializado**
- ✅ Envia alerta + **foto** quando alguém faz **login local com sucesso**
- ✅ Envia alerta + **foto** quando alguém **falha no login local** (com cooldown de 60s)
- ✅ Envia alerta quando o sistema é **desligado ou reiniciado** (incluindo via interface gráfica)
- ✅ Ignora ruído: não alerta sobre SSH, `sudo`, USB, rede, bluetooth ou microSD
- ✅ Roda automaticamente no boot via `cron @reboot`

---

## ✨ Funcionalidades

- ✅ **Captura de foto** na inicialização do sistema
- ✅ **Captura de foto** em login local bem-sucedido
- ✅ **Captura de foto** em falha de autenticação local (com cooldown)
- ✅ **Detecção de reboot/shutdown** via `systemd-shutdown`, `systemd-logind` e `gnome-session`
- ✅ **Alerta em tempo real** no Telegram via Bot API
- ✅ **Parser de logs** do `journalctl -f` em tempo real
- ✅ **Cooldown configurável** entre fotos de falha (`COOLDOWN_FOTO_FALHA`)
- ✅ **Redirecionamento de log** para arquivo local (útil para depuração)
- ✅ **Autostart** via `cron @reboot` (sem necessidade de root)

---

## 📡 Eventos Monitorados

| Evento | Fonte no `journalctl` | Alerta | Foto |
|--------|----------------------|--------|------|
| Inicialização do sistema | execução do script no `@reboot` | ✅ | ✅ |
| Login local com sucesso | `pam_unix`, `gdm-password`, `lightdm` | ✅ | ✅ |
| Falha de login local | `pam_unix`, `gdm-password`, `lightdm` | ✅ | ✅ (cooldown 60s) |
| Reboot | `systemd-shutdown`, `systemd-logind`, `gnome-session` | ✅ | ❌ |
| Shutdown | `systemd-shutdown`, `systemd-logind`, `gnome-session` | ✅ | ❌ |

> [!TIP]
> Eventos como **SSH**, **sudo**, **USB**, **rede**, **bluetooth** e **microSD** foram **intencionalmente removidos** para reduzir ruído. Se quiser reativar algum, basta adicionar o filtro no loop `for` dentro de `monitorar_journalctl()`.

---

## 🛠 Tecnologias Utilizadas

| Tecnologia | Função |
|------------|--------|
| **Python 3** | Linguagem do script |
| **systemd/journalctl** | Leitura de logs do sistema em tempo real |
| **Telegram Bot API** | Envio de mensagens e fotos |
| **fswebcam** | Captura de imagem pela webcam |
| **requests** | Requisições HTTP para o Telegram |
| **cron** | Agendamento no boot (`@reboot`) |

---

## 📦 Pré-requisitos

- **Sistema operacional:** Linux com systemd (testado em **Kali Linux**)
- **Python:** 3.x
- **Webcam:** conectada e acessível (ex: `/dev/video0`)
- **Bot do Telegram:** token e chat ID válidos
- **Usuário no grupo `systemd-journal`** (para ler logs de login)

### Instalação das dependências

```bash
sudo apt update
sudo apt install -y python3 python3-pip fswebcam
pip3 install requests
```

### Permissão para ler os logs do systemd

```bash
sudo usermod -aG systemd-journal $USER
```

> [!IMPORTANT]
> Após adicionar o usuário ao grupo `systemd-journal`, faça **logout e login** (ou reinicie) para o grupo ter efeito. Sem isso, o script só verá os próprios logs e **não detectará logins de outros usuários**.

---

## 📁 Estrutura do Projeto

```text
Gerenciadores/Alerta_Login_Kali/
├── Alerta_Login.py        # Script principal
├── Alerta_Login.log       # Log gerado em runtime (não versionar)
└── README.md              # Este arquivo
```

> [!NOTE]
> Recomendo adicionar `Alerta_Login.log` e `__pycache__/` ao `.gitignore` para não versionar logs e cache.

---

## ⚙️ Configuração e Execução

### 1️⃣ Clonar o repositório

```bash
git clone https://github.com/jayzonesec-ops/Alerta_Login_Kali.git
cd Alerta_Login_Kali
```

O projeto será criado na pasta `Alerta_Login_Kali/`, dentro do diretório onde o comando foi executado. Por padrão, isso cai em:

```text
/home/<seu_usuario>/Alerta_Login_Kali/
```

> [!IMPORTANT]
> Todos os exemplos abaixo usam `/home/usuario/Alerta_Login_Kali/`. **Troque `usuario` pelo seu nome de usuário real.** Para descobrir, rode `echo $HOME`.

### 2️⃣ Editar as credenciais do Telegram

Abra o script e edite as duas primeiras linhas de configuração:

```python
TOKEN_TELEGRAM = "SEU_TOKEN_AQUI"
CHAT_ID_TELEGRAM = "SEU_CHAT_ID_AQUI"
```

Veja a seção [Configurando o Bot do Telegram](#-configurando-o-bot-do-telegram) para saber como obter esses valores.

### 3️⃣ Testar manualmente

```bash
cd ~/Alerta_Login_Kali
python3 Alerta_Login.py
```

Se estiver tudo certo, você deve receber no Telegram:

- Mensagem de "SOC: Sistema Inicializado"
- Foto do operador local

Para encerrar o teste, use `Ctrl+C`.

---

## 🤖 Configurando o Bot do Telegram

1. No Telegram, fale com o **@BotFather** e crie um bot com `/newbot`.
2. Copie o **token** gerado (formato `123456789:ABCdef...`).
3. Fale com o **@userinfobot** para descobrir seu **chat ID**.
4. Envie uma mensagem qualquer para o seu bot (senão ele não consegue te responder).
5. Cole os valores no topo do `Alerta_Login.py`.

---

## ⏰ Agendando no Cron

### Jeito certo: crontab do **seu usuário** (sem sudo)

```bash
crontab -e
```

Na primeira vez, o sistema pergunta qual editor usar (nano, vim, etc.). Escolha o de sua preferência.

Adicione a linha abaixo **no final do arquivo**:

```cron
@reboot sleep 10 && /usr/bin/python3 /home/usuario/Alerta_Login_Kali/Alerta_Login.py > /home/usuario/Alerta_Login_Kali/Alerta_Login.log 2>&1
```

### O que cada parte faz

| Parte | Significado |
|-------|-------------|
| `@reboot` | Executa **uma vez**, toda vez que o sistema iniciar |
| `sleep 10` | Espera **10 segundos** antes de rodar (dá tempo do systemd/journalctl subirem) |
| `/usr/bin/python3` | Caminho absoluto do interpretador Python (cron não usa `$PATH` do shell) |
| `/home/usuario/.../Alerta_Login.py` | Caminho absoluto do script |
| `>` | Redireciona a **saída padrão** para o log |
| `/home/usuario/.../Alerta_Login.log` | Arquivo onde ficam os logs do script |
| `2>&1` | Redireciona também os **erros** para o mesmo log |

### Por que **não** usar `sudo crontab -e`

- O script **não precisa de root** — ele só lê logs e acessa a webcam.
- Rodar como root faria a webcam e o `/tmp/intruso.jpg` ficarem com dono `root`, o que pode causar conflito.
- O `journalctl` já foi liberado pro seu usuário via grupo `systemd-journal`.
- Segurança: menos privilégio = menos risco.

> [!TIP]
> Para conferir se o cron agendou corretamente, rode `crontab -l`. Para ver se o cron executou, use `grep CRON /var/log/syslog`.

---

## 📡 Uso

Após o boot, o script roda em segundo plano e envia notificações no Telegram conforme os eventos acontecem.

### Exemplos de mensagens enviadas

```text
🚀 SOC: Sistema Inicializado
O monitor de segurança subiu junto com o sistema.

📸 Verificação Física de Inicialização
Dispositivo ligado/reiniciado com sucesso.
```

```text
🔓 ALERTA: Login efetuado na Máquina
Sessão local aberta com sucesso.
👤 Usuário: jaison
```

```text
🚨 ALERTA: Falha de Autenticação Local
Tentativa incorreta de login local:
`pam_unix(gdm-password:auth): authentication failure; ...`
```

```text
⚠️ AVISO: Sistema sendo Encerrado/Rebootado
`systemd-logind: Powering off...`
```

---

## 🔧 Personalização

No topo do script, você pode ajustar:

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `TOKEN_TELEGRAM` | Token do bot | (obrigatório) |
| `CHAT_ID_TELEGRAM` | ID do chat que recebe alertas | (obrigatório) |
| `COOLDOWN_FOTO_FALHA` | Segundos entre fotos em falha de login | `60` |

> [!TIP]
> Se quiser **remover a foto no login bem-sucedido**, basta apagar a chamada `enviar_foto_telegram(...)` dentro do bloco "Sucesso no login local".

---

## ⚠️ Limitações Conhecidas

- **Webcam é obrigatória** — se não houver webcam conectada, o alerta de texto ainda é enviado, mas a foto falha silenciosamente (log registra o erro).
- **`fswebcam` pode conflitar** com outros programas que usam a webcam (Zoom, OBS, etc.). Se estiver em uso, a captura falha.
- **Login gráfico (GDM/LightDM)**: a detecção via `pam_unix`/`gdm-password`/`lightdm` pode variar conforme a versão da distro. Teste antes de confiar.
- **Desligamento via interface gráfica**: detectado via `systemd-logind` e `gnome-session`. Se usar outro ambiente (KDE, XFCE), pode não capturar — ajuste o filtro no script.
- **Foto no `/tmp`**: o arquivo `intruso.jpg` é apagado após o envio, mas se o script for interrompido no meio, pode sobrar no `/tmp`.

---

## 🛠️ Solução de Problemas

### Não recebo nada no Telegram

1. Confirme que o token e o chat ID estão corretos.
2. Envie uma mensagem para o bot **antes** de testar (senão ele não pode te responder).
3. Rode o script manualmente e veja se aparece erro no terminal.

### A foto não é enviada

1. Confirme que a webcam existe: `ls /dev/video*`
2. Teste o `fswebcam` isoladamente:
   ```bash
   fswebcam -r 640x480 /tmp/teste.jpg
   ```
3. Veja o log: `tail -f ~/Alerta_Login_Kali/Alerta_Login.log`

### O cron não executa no `@reboot`

1. Confirme que o serviço está ativo: `systemctl status cron`
2. Veja se o cron registrou a execução: `grep CRON /var/log/syslog`
3. Aumente o `sleep` (ex: `sleep 20`) — em máquinas lentas, 10s pode não bastar.

### `journalctl` retorna "permissão negada"

- Confirme que você está no grupo: `groups | grep systemd-journal`
- Se não estiver: `sudo usermod -aG systemd-journal $USER` e faça logout/login.

---

## 📄 Licença

Este projeto está sob a licença **MIT**. Consulte o arquivo `LICENSE` para mais detalhes.

---

## 👨‍💻 Autor

**JayZoneSec**

- 🐙 GitHub: [@jayzonesec-ops](https://github.com/jayzonesec-ops)
- 📦 Projeto: [Alerta Login Kali](https://github.com/jayzonesec-ops/alerta-login-kali)

💻 Built by [JayZoneSec](https://github.com/jayzonesec-ops) — Ethical Hacking & Tools 🔐
