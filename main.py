import json, sqlite3, shutil, subprocess, uuid
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
DATA, OUT = ROOT / "data", ROOT / "outputs"
DATA.mkdir(exist_ok=True)
OUT.mkdir(exist_ok=True)
DB = DATA / "oriden.sqlite3"
app = FastAPI(title="Oriden Flow")
app.mount("/outputs", StaticFiles(directory=OUT), name="outputs")

def connect():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c

with connect() as db:
    db.execute("CREATE TABLE IF NOT EXISTS channels (id INTEGER PRIMARY KEY, name TEXT, handle TEXT UNIQUE, niche TEXT)")
    db.execute("CREATE TABLE IF NOT EXISTS videos (id TEXT PRIMARY KEY, channel_id INTEGER, title TEXT, status TEXT, url TEXT, error TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP)")
    for name, handle, niche in [("Fato Pop", "@faatopop5", "Curiosidades"), ("Motivação", "@enzo.valenti05", "Motivação")]:
        db.execute("INSERT OR IGNORE INTO channels(name,handle,niche) VALUES (?,?,?)", (name, handle, niche))

class Job(BaseModel):
    channel_id: int
    title: str = Field(min_length=2, max_length=120)
    scenes: list[str] = Field(min_length=2, max_length=8)
    voice: bool = False

def font(size):
    paths = ["C:/Windows/Fonts/arialbd.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf"]
    for path in paths:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()

def render_slide(text, label, idx, total, dest):
    img = Image.new("RGB", (720, 1280), (14, 23, 43))
    draw = ImageDraw.Draw(img)
    accent = (30, 220, 194) if label == "FATO POP" else (255, 174, 79)
    draw.rounded_rectangle((40, 55, 680, 145), radius=18, fill=(29, 43, 65))
    draw.text((72, 82), label, font=font(38), fill=accent)
    words, lines, line = text.split(), [], ""
    big = font(54)
    for word in words:
        candidate = (line + " " + word).strip()
        if draw.textbbox((0, 0), candidate, font=big)[2] > 610 and line:
            lines.append(line)
            line = word
        else:
            line = candidate
    if line:
        lines.append(line)
    if len(lines) > 10:
        raise ValueError("Cena muito longa para renderização legível")
    start_y = max(300, 625 - len(lines) * 37)
    for n, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=big)
        draw.text(((720 - bbox[2]) / 2, start_y + n * 84), line, font=big, fill="white")
    draw.rectangle((45, 1165, 45 + int(630 * (idx + 1) / total), 1175), fill=accent)
    draw.text((48, 1200), f"{idx+1} / {total}", font=font(28), fill=(205, 210, 220))
    img.save(dest)

def run(cmd, timeout=180):
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
    if proc.returncode:
        raise RuntimeError(proc.stderr.decode(errors="replace")[-600:])

@app.get("/")
def home():
    return FileResponse(ROOT / "static" / "index.html")

@app.get("/api/health")
def health():
    return {"ok": True, "ffmpeg": bool(shutil.which("ffmpeg")), "espeak": bool(shutil.which("espeak"))}

@app.get("/api/channels")
def channels():
    with connect() as db:
        return [dict(r) for r in db.execute("SELECT * FROM channels ORDER BY id")]

@app.get("/api/videos")
def videos():
    with connect() as db:
        return [dict(r) for r in db.execute("SELECT v.*,c.name AS channel FROM videos v JOIN channels c ON c.id=v.channel_id ORDER BY v.created_at DESC LIMIT 100")]

@app.post("/api/render")
def render(job: Job):
    if not shutil.which("ffmpeg"):
        raise HTTPException(503, "FFmpeg não instalado no PATH")
    with connect() as db:
        channel = db.execute("SELECT * FROM channels WHERE id=?", (job.channel_id,)).fetchone()
    if not channel:
        raise HTTPException(404, "Canal não encontrado")
    scenes = [s.strip()[:450] for s in job.scenes if s.strip()]
    if len(scenes) < 2:
        raise HTTPException(400, "Informe no mínimo duas cenas")
    vid = uuid.uuid4().hex[:12]
    folder = OUT / vid
    folder.mkdir()
    with connect() as db:
        db.execute("INSERT INTO videos(id,channel_id,title,status) VALUES (?,?,?,?)", (vid,job.channel_id,job.title,"processando"))
    try:
        label = "FATO POP" if channel["niche"] == "Curiosidades" else "MOTIVAÇÃO"
        for idx, scene in enumerate(scenes):
            render_slide(scene,label,idx,len(scenes),folder / f"slide_{idx:02}.png")
        listing = folder / "frames.txt"
        with listing.open("w", encoding="utf-8") as f:
            for idx in range(len(scenes)):
                f.write(f"file 'slide_{idx:02}.png'\nduration 4.5\n")
            f.write(f"file 'slide_{len(scenes)-1:02}.png'\n")
        audio = folder / "voice.wav"
        voice_ready = False
        if job.voice and shutil.which("espeak"):
            run(["espeak","-v","pt-br","-s","145","-w",str(audio),". ".join(scenes)],50)
            voice_ready = audio.exists() and audio.stat().st_size > 1000
        output = folder / "video.mp4"
        cmd = ["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",str(listing)]
        if voice_ready:
            cmd += ["-i",str(audio)]
        cmd += ["-vf","fps=24,format=yuv420p","-c:v","libx264","-preset","ultrafast","-crf","26"]
        cmd += ["-c:a","aac","-af","apad","-shortest"] if voice_ready else ["-an"]
        cmd += ["-movflags","+faststart",str(output)]
        run(cmd)
        url = f"/outputs/{vid}/video.mp4"
        with connect() as db:
            db.execute("UPDATE videos SET status='pronto',url=? WHERE id=?", (url,vid))
        return {"id":vid,"status":"pronto","url":url,"voice_generated":voice_ready}
    except Exception as exc:
        with connect() as db:
            db.execute("UPDATE videos SET status='erro', error=? WHERE id=?", (str(exc)[:400],vid))
        raise HTTPException(500,f"Erro de renderização: {str(exc)[:220]}")
