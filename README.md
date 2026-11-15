# Oriden Flow — MVP

Plataforma local para os canais Fato Pop (@faatopop5) e Motivação (@enzo.valenti05).

## Executar
1. Instale Python 3.10+ e FFmpeg (no PATH).
2. Execute `pip install -r requirements.txt`.
3. Execute `uvicorn main:app --host 127.0.0.1 --port 8000`.
4. Abra http://127.0.0.1:8000.

Opcional: instale eSpeak para narração local em português.

## Funcionalidades
- Roteiros com cenas editáveis para dois canais.
- Renderização local de vídeo vertical MP4 720x1280 com FFmpeg.
- Narração básica opcional com eSpeak e histórico SQLite.
- Download do vídeo pronto.

## Limitações
Não publica no TikTok, não cria vídeos cinematográficos com IA, não utiliza APIs externas e não tem autenticação. Não exponha o servidor à internet. Revise o conteúdo antes de publicar.
