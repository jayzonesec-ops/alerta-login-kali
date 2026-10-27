# 🛡️ Alerta Login Kali

> HIDS/SOAR tático em Python que monitora eventos de segurança do sistema e envia alertas em tempo real para o Telegram, com captura de foto pela webcam e controle remoto de firewall via botões interativos.

![Versão](https://img.shields.io/badge/versão-2.0-blue?style=for-the-badge)
![Plataforma](https://img.shields.io/badge/plataforma-Linux-333?style=for-the-badge&logo=linux&logoColor=white)
![Python](https://img.shields.io/badge/python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Telegram](https://img.shields.io/badge/telegram-bot-26A5E4?style=for-the-badge&logo=telegram&logoColor=white)
![Systemd](https://img.shields.io/badge/systemd-journal-000?style=for-the-badge&logo=systemd&logoColor=white)
![Licença](https://img.shields.io/badge/licença-MIT-green?style=for-the-badge)

---

> [!NOTE]
> O **Alerta Login Kali** lê o `journalctl` em tempo real e notifica o administrador sobre eventos sensíveis:
>
> - Inicialização do sistema
> - Tentativas de acesso SSH
> - Comandos `sudo`
> - Login local
> - Desligamento e reinicialização
>
> **Novidade na v2.0:** o bot permite bloquear e desbloquear IPs diretamente pelo Telegram com botões interativos. As regras de firewall são persistentes e sobrevivem a reinicializações.
                                                   
---
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           ré-Requisitos]#-pré-requisitos
## 📋 Índice

- [Sobre o Projeto](#-sobre-o-projeto)
- [Funcionalidades](#-funcionalidades)
- [Eventos Monitorados](#-eventos-monitorados)
- [Tecnologias Utilizadas](#-tecnologias-utilizadas)
- [Pré-requisitos](#-pré-requisitos)
- [Instalação](#️-instalação-passo-a-passo)
- [Configuração do Firewall](#-configuração-do-firewall-base)
- [Configuração do Telegram](#-configurando-o-bot-do-telegram)
- [Ativação dos Serviços](#-ativando-os-serviços)
- [Como Usar](#-como-usar-o-bot)
- [Limitações Conhecidas](#️-limitações-conhecidas)
- [Solução de Problemas](#️-solução-de-problemas)
- [Licença](#-licença)
- [Autor](#-autor)

---

# 🔍 Sobre o Projeto

O **Alerta Login Kali** é um monitor de segurança executado em segundo plano que ajuda a responder à pergunta:

**Quem iniciou sessão, tentou acessar ou desligou esta máquina?**

Na versão 2.0, o projeto oferece recursos de **SOAR (Security Orchestration, Automation and Response)**.

Quando uma tentativa de autenticação SSH falha, o bot pode enviar um alerta contendo um botão para bloqueio imediato do IP.

Durante a inicialização, o sistema também pode enviar automaticamente a lista de IPs bloqueados, juntamente com botões para desbloqueio.

## Mudança importante na v2.0

O projeto deixou de utilizar `cron`.

Toda a execução agora é controlada pelo **systemd**, que oferece:

- Reinicialização automática do serviço em caso de falha
- Inicialização no boot
- Melhor gerenciamento dos processos
- Redução de notificações duplicadas

---

# ✨ Funcionalidades

- ✅ Alerta de inicialização com captura de foto pela webcam
- ✅ Alerta de login local bem-sucedido com foto
- ✅ Alerta de falha de login local com foto
- ✅ Alerta de comandos executados via `sudo`
- ✅ Alerta de tentativas de autenticação SSH malsucedidas
- ✅ Bloqueio de IPs diretamente pelo Telegram
- ✅ Desbloqueio de IPs diretamente pelo Telegram
- ✅ Persistência das regras de firewall com `iptables-persistent`
- ✅ Envio automático da lista de IPs bloqueados na inicialização
- ✅ Cooldown para reduzir alertas repetidos do mesmo IP

---

# 📡 Eventos Monitorados

| Evento | Alerta | Botão de Ação | Foto |
|----------|---------|---------|---------|
| Inicialização do sistema | ✅ | — | ✅ |
| Login local com sucesso | ✅ | — | ✅ |
| Falha de login local | ✅ | — | ✅ |
| Falha de autenticação SSH | ✅ | ❌ Bloquear IP | ❌ |
| Comando executado via sudo | ✅ | — | ❌ |
| Lista de IPs bloqueados na inicialização | ✅ | ✅ Desbloquear IP | ❌ |
| Reinicialização ou desligamento | ✅ | — | ❌ |

---

# 🛠 Tecnologias Utilizadas

| Tecnologia | Função |
|------------|---------|
| Python 3 | Linguagem dos scripts |
| systemd / journalctl | Leitura de logs e gerenciamento dos serviços |
| iptables-persistent | Persistência do firewall |
| Telegram Bot API | Interface de alertas e controle |
| fswebcam | Captura de imagens |
| requests | Comunicação HTTP |
| python-dotenv | Leitura das variáveis do arquivo `.env` |

---

# 📦 Pré-requisitos

- Linux com `systemd` (testado em Kali Linux)
- Python 3.x
- Webcam acessível em `/dev/video0` (ou equivalente)
- Bot Telegram configurado
- Permissões administrativas (root)

## Instalação das dependências

```bash
sudo apt update

sudo apt install -y \
python3 \
python3-requests \
python3-dotenv \
fswebcam \
iptables-persistent
```

> [!WARNING]
> A instalação de `iptables-persistent` pode remover o `ufw` para evitar conflitos. Verifique atentamente as mensagens exibidas pelo instalador.

---

# ⚙️ Instalação Passo a Passo

## 1. Clonar o repositório

```bash
git clone https://github.com/jayzonesec-ops/alerta-login-kali.git

cd alerta-login-kali
```

## 2. Criar o diretório do SOC

```bash
sudo mkdir -p /opt/soc
```

## 3. Copiar os arquivos Python

```bash
sudo cp soc_helpers.py /opt/soc/
sudo cp soc-notify-boot.py /opt/soc/
sudo cp Alerta_Login_Kali.py /opt/soc/

sudo chmod +x /opt/soc/*.py
```

## 4. Copiar os serviços do systemd

```bash
sudo cp soc-monitor.service /etc/systemd/system/
sudo cp soc-notify-boot.service /etc/systemd/system/
```

## 5. Criar o arquivo `.env`

```bash
sudo nano /opt/soc/.env
```

Conteúdo:

```env
TOKEN_TELEGRAM=seu_token_aqui
CHAT_ID_TELEGRAM=seu_chat_id_aqui
```

Defina permissões restritas:

```bash
sudo chmod 600 /opt/soc/.env
```

## 6. Remover a cópia clonada (opcional)

Execute apenas após confirmar que todos os arquivos foram copiados corretamente.

```bash
cd ~

rm -rf alerta-login-kali/
```

---

# 🔥 Configuração do Firewall Base

> [!WARNING]
> As regras abaixo alteram o firewall da máquina. Execute-as preferencialmente pelo console local para evitar perda de acesso remoto.

```bash
# Permite tráfego de saída
sudo iptables -A OUTPUT -j ACCEPT

# Permite conexões estabelecidas
sudo iptables -A INPUT \
-m conntrack \
--ctstate ESTABLISHED,RELATED \
-j ACCEPT

# Permite localhost
sudo iptables -A INPUT -i lo -j ACCEPT

# Permite SSH
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT

# Bloqueio padrão
sudo iptables -P INPUT DROP

# Salva as regras
sudo netfilter-persistent save
```

Para verificar:

```bash
sudo iptables -S

sudo iptables -L -n -v
```

---

# 🤖 Configurando o Bot do Telegram

1. Abra o Telegram.
2. Converse com o **@BotFather**.
3. Crie um novo bot usando:

```text
/newbot
```

4. Copie o token gerado.
5. Obtenha seu Chat ID usando o **@userinfobot**.
6. Envie uma mensagem para seu bot.
7. Configure os dados no arquivo:

```text
/opt/soc/.env
```

> [!WARNING]
> Nunca publique o token do bot no GitHub. O arquivo `.env` deve permanecer protegido pelas permissões `600`.

---

# 🚀 Ativando os Serviços

Recarregue o systemd:

```bash
sudo systemctl daemon-reload
```

Habilite os serviços:

```bash
sudo systemctl enable soc-notify-boot.service

sudo systemctl enable soc-monitor.service
```

Inicie os serviços:

```bash
sudo systemctl start soc-notify-boot.service

sudo systemctl start soc-monitor.service
```

Verifique o status:

```bash
sudo systemctl status soc-notify-boot.service

sudo systemctl status soc-monitor.service
```

Se tudo estiver correto, você receberá no Telegram:

- Alerta de inicialização
- Foto da webcam
- Lista de IPs bloqueados (quando houver)

---

# 📡 Como Usar o Bot

## Durante a execução

Ao detectar uma falha de autenticação SSH, o sistema pode enviar:

```text
❌ Bloquear IP
```

Ao pressionar o botão, uma regra de firewall será criada.

## Após reinicialização

O sistema pode enviar a lista de IPs atualmente bloqueados.

Cada IP terá o botão:

```text
✅ Desbloquear
```

Utilize essas funções apenas em sistemas e redes que você administra ou possui autorização para proteger.

---

# ⚠️ Limitações Conhecidas

- A captura da webcam pode falhar se o dispositivo estiver sendo utilizado por outro programa.
- A detecção de login gráfico pode variar entre GDM, LightDM e SDDM.
- O projeto não foi projetado para milhares de regras simultâneas no `iptables`.
- Os eventos dependem da disponibilidade dos logs no sistema.

---

# 🛠️ Solução de Problemas

## Não recebo mensagens no Telegram

Verifique:

- Se o arquivo `/opt/soc/.env` existe
- Se o token está correto
- Se o Chat ID está correto
- Se você enviou uma mensagem para o bot

Verifique o status:

```bash
sudo systemctl status soc-monitor.service
```

Logs em tempo real:

```bash
sudo journalctl -u soc-monitor.service -f
```

---

## O botão de desbloquear não funciona

Confira os logs:

```bash
sudo journalctl -u soc-monitor.service -f
```

Confirme também:

- Se o `iptables-persistent` está instalado
- Se o serviço possui permissões suficientes

---

## Erro: Credenciais do Telegram não configuradas

O arquivo `.env` não foi encontrado ou está vazio.

Verifique:

```text
/opt/soc/.env
```

---

## Erro: can't open file

Normalmente indica caminho incorreto no serviço systemd.

Verifique:

```bash
sudo systemctl cat soc-monitor.service
```

Editar:

```bash
sudo systemctl edit --full soc-monitor.service
```

Após alterações:

```bash
sudo systemctl daemon-reload

sudo systemctl restart soc-monitor.service
```

---

# 📄 Licença

Este projeto está licenciado sob a licença MIT.

Consulte o arquivo:

```text
LICENSE
```

para os termos completos.

---

# 👨‍💻 Autor

**JayZoneSec**

- **GitHub:** [@jayzonesec-ops](https://github.com/jayzonesec-ops)
- **Projeto:** [Alerta Login Kali](https://github.com/jayzonesec-ops/alerta-login-kali)

---

*Built by JayZoneSec — Ethical Hacking & Tools 🔐*
