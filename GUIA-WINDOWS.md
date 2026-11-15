# Oriden Flow — abrir o CRM no Windows

## 1. Baixe o projeto
No GitHub, entre em **Code > Download ZIP** no repositório
https://github.com/TiktokOriden/Tiktok-Oriden

Extraia o ZIP em uma pasta comum, por exemplo `C:\OridenFlow` (não execute dentro do ZIP).

## 2. Instale
Dê dois cliques em **INSTALAR-WINDOWS.bat**.
O script verifica Python, tenta instalá-lo pelo gerenciador oficial `winget` se necessário, cria o ambiente virtual e instala as dependências do projeto.
Se o Windows pedir autorização para instalar Python, leia e aprove somente se confiar no projeto.

## 3. Abra
Dê dois cliques em **ABRIR-CRM.bat**.
O navegador abrirá em http://127.0.0.1:8000 e o CRM será servido apenas no computador local.
Mantenha a janela do terminal aberta. Para encerrar, use Ctrl+C nela.

## 4. Produza vídeos (opcional)
Para criar vídeos MP4 é necessário instalar o FFmpeg.
Com o terminal aberto:
```powershell
winget install --id Gyan.FFmpeg -e
```
Feche e abra novamente o terminal/CRM para atualizar o PATH.
Para narração local simples, instale eSpeak separadamente e assegure que o comando `espeak` esteja no PATH.

## Observações
- Dados do pipeline ficam no armazenamento local do navegador.
- MP4s e histórico são salvos no computador sob `outputs/` e `data/`.
- Não é um CRM online; não abra a porta 8000 para a internet, pois ainda não há login/autenticação.
- TikTok não está conectado para postagem automática.
- Python 3.12 é recomendado. Outros Pythons compatíveis com requirements podem funcionar.
- Se o instalador não achar Python após o winget, execute-o novamente.
