import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import threading
import os
import re
import sys
import hashlib
from pathlib import Path
from collections import deque
import ctypes

# ======================== CONFIG ========================
NOME_PROGRAMA = "YouToMP"
CREATE_NO_WINDOW = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
PASTA_DESTINO = Path.home() / "Downloads" / NOME_PROGRAMA
PASTA_DESTINO.mkdir(parents=True, exist_ok=True)

# guarda o último arquivo convertido (Path) para abrir exatamente onde foi salvo
ULTIMO_ARQUIVO = None

def get_resource_path(filename):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, filename)
    return os.path.join(os.path.abspath("."), filename)

ICONE_ICO_PATH = get_resource_path("yt_mp3_converter_multi_res.ico")

# ======================== CENTRALIZAÇÃO ========================
def centralizar_na_tela_atual(win, largura, altura):
    """Centraliza a janela no monitor atual (onde está o cursor)."""
    win.update_idletasks()
    left, top, right, bottom = 0, 0, win.winfo_screenwidth(), win.winfo_screenheight()

    if os.name == "nt":
        try:
            user32 = ctypes.windll.user32
            MONITOR_DEFAULTTONEAREST = 2

            class POINT(ctypes.Structure):
                _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

            class RECT(ctypes.Structure):
                _fields_ = [("left", ctypes.c_long), ("top", ctypes.c_long),
                            ("right", ctypes.c_long), ("bottom", ctypes.c_long)]

            class MONITORINFO(ctypes.Structure):
                _fields_ = [("cbSize", ctypes.c_ulong),
                            ("rcMonitor", RECT),
                            ("rcWork", RECT),
                            ("dwFlags", ctypes.c_ulong)]

            pt = POINT()
            user32.GetCursorPos(ctypes.byref(pt))
            hmon = user32.MonitorFromPoint(pt, MONITOR_DEFAULTTONEAREST)
            mi = MONITORINFO()
            mi.cbSize = ctypes.sizeof(MONITORINFO)
            user32.GetMonitorInfoW(hmon, ctypes.byref(mi))

            left, top, right, bottom = mi.rcWork.left, mi.rcWork.top, mi.rcWork.right, mi.rcWork.bottom
        except Exception:
            pass

    work_w = right - left
    work_h = bottom - top
    pos_x = left + (work_w - largura) // 2
    pos_y = top + (work_h - altura) // 2
    win.geometry(f"{largura}x{altura}+{pos_x}+{pos_y}")

# ======================== RESOLUÇÃO DE BINÁRIOS ========================
def get_bundled_path(*rel_parts):
    return get_resource_path(os.path.join(*rel_parts))

def which(cmd):
    from shutil import which as _which
    return _which(cmd)

YTDLP_BUNDLED = get_bundled_path("bin", "yt-dlp.exe" if os.name == "nt" else "yt-dlp")
FFMPEG_BUNDLED = get_bundled_path("bin", "ffmpeg.exe" if os.name == "nt" else "ffmpeg")

def resolve_ytdlp():
    if os.path.isfile(YTDLP_BUNDLED):
        return YTDLP_BUNDLED
    y = which("yt-dlp")
    if y:
        return y
    y_local = get_resource_path("yt-dlp.exe")
    if os.path.isfile(y_local):
        return y_local
    return None

def resolve_ffmpeg():
    if os.path.isfile(FFMPEG_BUNDLED):
        return FFMPEG_BUNDLED
    f = which("ffmpeg")
    if f:
        return f
    return None

# ======================== SHA256 DO APP ========================
def compute_self_sha256():
    try:
        alvo = sys.executable if getattr(sys, "frozen", False) else __file__
        h = hashlib.sha256()
        with open(alvo, "rb") as f:
            for bloco in iter(lambda: f.read(1024 * 1024), b""):
                h.update(bloco)
        return h.hexdigest()
    except Exception:
        return "N/A"

APP_SHA256 = compute_self_sha256()

# ======================== MSGS ========================
texts = {
    "pt": {
        "paste_url": "Cole a URL do YouTube:",
        "downloading": "Baixando e convertendo...",
        "invalid_url": "URL inválida do YouTube.",
        "success_title": "Sucesso",
        "error_title": "Erro",
        "warn_title": "Aviso",
        "saved_in": "{} salvo em:\n{}",
        "gen_success": "✅ {} gerado com sucesso!",
        "gen_fail": "❌ Erro ao converter para {}.",
        "dl_fail": "Erro ao baixar ou localizar o arquivo.",
        "unexpected": "❌ Erro inesperado.",
        "warn_paste": "Cole uma URL válida.",
        "warn_invalid": "URL inválida do YouTube.",
        "btn_convert_mp3": "Converter para MP3",
        "btn_convert_mp4": "Converter para MP4",
        "btn_open_folder": "Abrir pasta de destino",
        "btn_mp3": "MP3",
        "btn_mp4": "MP4",
        "footer": "por FQ",
        "hash_label": "SHA256",
        "miss_ytdlp": "yt-dlp não encontrado.\nInclua 'yt-dlp(.exe)' em ./bin ou instale no sistema.",
        "miss_ffmpeg": "FFmpeg não encontrado.\nInclua 'ffmpeg(.exe)' em ./bin ou instale no sistema.",
        "open_folder_fail": "Não foi possível abrir a pasta/arquivo:\n{}",
        "log_tail": "\n\nDetalhes (fim do log):\n{}",
    },
    "en": {
        "paste_url": "Paste the YouTube URL:",
        "downloading": "Downloading and converting...",
        "invalid_url": "Invalid YouTube URL.",
        "success_title": "Success",
        "error_title": "Error",
        "warn_title": "Warning",
        "saved_in": "{} saved to:\n{}",
        "gen_success": "✅ {} generated successfully!",
        "gen_fail": "❌ Error converting to {}.",
        "dl_fail": "Error while downloading or locating the file.",
        "unexpected": "❌ Unexpected error.",
        "warn_paste": "Please paste a valid URL.",
        "warn_invalid": "Invalid YouTube URL.",
        "btn_convert_mp3": "Convert to MP3",
        "btn_convert_mp4": "Convert to MP4",
        "btn_open_folder": "Open destination folder",
        "btn_mp3": "MP3",
        "btn_mp4": "MP4",
        "footer": "by FQ",
        "hash_label": "SHA256",
        "miss_ytdlp": "yt-dlp not found.\nBundle 'yt-dlp(.exe)' in ./bin or install it system-wide.",
        "miss_ffmpeg": "FFmpeg not found.\nBundle 'ffmpeg(.exe)' in ./bin or install it system-wide.",
        "open_folder_fail": "Could not open folder/file:\n{}",
        "log_tail": "\n\nDetails (log tail):\n{}",
    },
}
current_lang = "pt"

def t(key: str) -> str:
    return texts[current_lang][key]

# ======================== FUNÇÕES ========================
def abrir_pasta():
    """Abre exatamente a pasta do último arquivo gerado (ou PASTA_DESTINO).
       No Windows, tenta selecionar o arquivo no Explorer."""
    try:
        global ULTIMO_ARQUIVO
        PASTA_DESTINO.mkdir(parents=True, exist_ok=True)

        if ULTIMO_ARQUIVO and Path(ULTIMO_ARQUIVO).exists():
            alvo = Path(ULTIMO_ARQUIVO).resolve()
            if os.name == "nt":
                # explorer /select, "arquivo"
                subprocess.Popen(["explorer.exe", "/select,", str(alvo)], creationflags=CREATE_NO_WINDOW)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", "-R", str(alvo)], creationflags=CREATE_NO_WINDOW)
            else:
                subprocess.Popen(["xdg-open", str(alvo.parent)], creationflags=CREATE_NO_WINDOW)
            return
        else:
            # abre só a pasta padrão
            pasta = str(PASTA_DESTINO.resolve())
            if os.name == "nt":
                try:
                    os.startfile(pasta)
                except Exception:
                    # fallbacks
                    try:
                        ctypes.windll.shell32.ShellExecuteW(None, "open", pasta, None, None, 1)
                    except Exception:
                        subprocess.Popen(["explorer.exe", pasta], creationflags=CREATE_NO_WINDOW)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", pasta], creationflags=CREATE_NO_WINDOW)
            else:
                subprocess.Popen(["xdg-open", pasta], creationflags=CREATE_NO_WINDOW)
    except Exception as e:
        messagebox.showerror(t("error_title"), t("open_folder_fail").format(e))

def _parse_final_path_from_stdout(line: str, modo_audio: bool):
    """Extrai o caminho final a partir do stdout do yt-dlp."""
    if modo_audio:
        m = re.search(r"\[ExtractAudio\]\s+Destination:\s+(.+?\.mp3)$", line, re.IGNORECASE)
        if m:
            return m.group(1).strip('"')
    else:
        m = re.search(r'\[Merger\]\s+Merging formats into\s+"(.+?\.mp4)"', line, re.IGNORECASE)
        if m:
            return m.group(1)
    m = re.search(r"\[download\]\s+Destination:\s+(.+)", line, re.IGNORECASE)
    if m:
        return m.group(1).strip('"')
    return None

def _newest_by_ext(ext: str):
    arquivos = list(PASTA_DESTINO.glob(f"*.{ext}"))
    if not arquivos:
        return None
    arquivos.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    return arquivos[0]

def _yt_dlp_update(ytdlp_path: str):
    """Tenta auto-atualizar yt-dlp (-U). Ignora erros."""
    try:
        subprocess.run([ytdlp_path, "-U"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                       text=True, creationflags=CREATE_NO_WINDOW, timeout=25)
    except Exception:
        pass

def _run_ytdlp(comando_base, url, modo_audio):
    """Gera progresso e, ao final, (rc, final_path, tail)."""
    tail = deque(maxlen=40)
    final_path = None

    processo = subprocess.Popen(
        comando_base + [url],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        creationflags=CREATE_NO_WINDOW
    )

    for linha in processo.stdout:
        linha = linha.rstrip()
        tail.append(linha)

        mprog = re.search(r"\[download\]\s+(\d{1,3}(?:\.\d+)?)%", linha)
        if mprog:
            progresso = float(mprog.group(1))
            yield ("progress", int(progresso))

        found = _parse_final_path_from_stdout(linha, modo_audio)
        if found:
            final_path = found

    processo.wait()

    final_path_resolved = None
    if final_path:
        p = Path(final_path)
        final_path_resolved = p if p.is_absolute() else (PASTA_DESTINO / p.name)

    yield ("done", (processo.returncode, final_path_resolved, "\n".join(tail)))

def baixar(url, status_label, progress_bar, progress_label, modo_audio):
    try:
        global ULTIMO_ARQUIVO
        status_label.config(text=t("downloading"))
        progress_bar["value"] = 0
        progress_label.config(text="0%")

        clean_url = url.strip()

        ext = "mp3" if modo_audio else "mp4"
        output_template = str(PASTA_DESTINO / "%(title)s.%(ext)s")

        ytdlp_path = resolve_ytdlp()
        ffmpeg_exec = resolve_ffmpeg()

        if not ytdlp_path:
            messagebox.showerror(t("error_title"), t("miss_ytdlp"))
            status_label.config(text=t("unexpected"))
            return
        if not ffmpeg_exec:
            messagebox.showerror(t("error_title"), t("miss_ffmpeg"))
            status_label.config(text=t("unexpected"))
            return

        _yt_dlp_update(ytdlp_path)

        ffmpeg_loc = os.path.dirname(ffmpeg_exec) if os.name != "nt" else ffmpeg_exec
        base_cmd = [
            ytdlp_path, "--newline", "--no-playlist",
            "--ffmpeg-location", ffmpeg_loc,
            "-o", output_template
        ]
        if modo_audio:
            base_cmd += ["-x", "--audio-format", "mp3", "--audio-quality", "0", "--no-keep-video"]
        else:
            base_cmd += ["-f", "bestvideo*+bestaudio/best", "--merge-output-format", "mp4"]

        rc = None
        final_path = None
        tail = ""
        for kind, payload in _run_ytdlp(base_cmd, clean_url, modo_audio):
            if kind == "progress":
                progress_bar["value"] = payload
                progress_label.config(text=f"{payload}%")
                progress_bar.update_idletasks()
                progress_label.update_idletasks()
            else:
                rc, final_path, tail = payload

        saber_signals = ("SABER", "nsig extraction failed", "Only images are available", "images only")
        needs_retry = (rc != 0) or (("Requested format is not available" in tail) or any(s in tail for s in saber_signals))

        if needs_retry:
            base_cmd_android = base_cmd + ["--extractor-args", "youtube:player_client=android"]
            if not modo_audio:
                base_cmd_android = [arg for arg in base_cmd_android if arg != "--merge-output-format" and arg != "mp4"]
                base_cmd_android += ["-f", "bv*+ba/best"]

            for kind, payload in _run_ytdlp(base_cmd_android, clean_url, modo_audio):
                if kind == "progress":
                    progress_bar["value"] = payload
                    progress_label.config(text=f"{payload}%")
                    progress_bar.update_idletasks()
                    progress_label.update_idletasks()
                else:
                    rc, final_path, tail = payload

        if (not final_path) or (not final_path.exists()):
            nf = _newest_by_ext(ext)
            if nf:
                final_path = nf

        if rc == 0 and final_path and final_path.exists():
            ULTIMO_ARQUIVO = final_path  # <- salva para o botão abrir exatamente aqui
            progress_bar["value"] = 100
            progress_label.config(text="100%")
            status_label.config(text=t("gen_success").format(ext.upper()))
            messagebox.showinfo(t("success_title"), t("saved_in").format(ext.upper(), final_path))
        else:
            status_label.config(text=t("gen_fail").format(ext.upper()))
            messagebox.showerror(t("error_title"), t("dl_fail") + t("log_tail").format(tail))

    except Exception as e:
        status_label.config(text=t("unexpected"))
        messagebox.showerror(t("error_title"), str(e))

def iniciar_thread(url_entry, status_label, progress_bar, progress_label, modo_audio):
    url = url_entry.get().strip()
    if not url:
        messagebox.showwarning(t("warn_title"), t("warn_paste"))
        return
    threading.Thread(
        target=baixar,
        args=(url, status_label, progress_bar, progress_label, modo_audio),
        daemon=True
    ).start()

# ======================== INTERFACE ========================
janela = tk.Tk()
janela.title(NOME_PROGRAMA)
janela.resizable(False, False)

largura, altura = 480, 410
centralizar_na_tela_atual(janela, largura, altura)

try:
    janela.iconbitmap(ICONE_ICO_PATH)
except Exception as e:
    print("Erro ao aplicar ícone .ico:", e)

# Barra superior (idiomas)
topbar = tk.Frame(janela)
topbar.pack(anchor="nw", padx=8, pady=6)

# Flags
FLAGS_DIR = get_resource_path("Flags")
BR_FLAG_PATH = os.path.join(FLAGS_DIR, "br.png")
US_FLAG_PATH = os.path.join(FLAGS_DIR, "us.png")
br_img = us_img = None
try:
    if os.path.exists(BR_FLAG_PATH) and os.path.exists(US_FLAG_PATH):
        br_img = tk.PhotoImage(file=BR_FLAG_PATH).subsample(3, 3)
        us_img = tk.PhotoImage(file=US_FLAG_PATH).subsample(3, 3)
except Exception:
    br_img = us_img = None

# Container
container = tk.Frame(janela)
container.pack(pady=10)

label_url = tk.Label(container, text=t("paste_url"))
label_url.pack(pady=10)

url_entry = tk.Entry(container, width=50)
url_entry.pack()

status_label = tk.Label(container, text="")
status_label.pack(pady=10)

progress_bar = ttk.Progressbar(container, length=320, mode='determinate')
progress_bar.pack(pady=5)

progress_label = tk.Label(container, text="0%")
progress_label.pack(pady=0)

botao_converter = tk.Button(container, text=t("btn_convert_mp3"))
botao_converter.pack(pady=5)

frame_botoes_modo = tk.Frame(container)
frame_botoes_modo.pack(pady=5)

modo_audio = True

def definir_modo_audio(valor):
    global modo_audio
    modo_audio = valor
    if modo_audio:
        botao_mp3.config(relief="sunken")
        botao_mp4.config(relief="raised")
        botao_converter.config(text=t("btn_convert_mp3"))
    else:
        botao_mp3.config(relief="raised")
        botao_mp4.config(relief="sunken")
        botao_converter.config(text=t("btn_convert_mp4"))
    botao_converter.config(
        command=lambda: iniciar_thread(url_entry, status_label, progress_bar, progress_label, modo_audio)
    )

botao_mp3 = tk.Button(frame_botoes_modo, text=t("btn_mp3"), width=10, command=lambda: definir_modo_audio(True))
botao_mp4 = tk.Button(frame_botoes_modo, text=t("btn_mp4"), width=10, command=lambda: definir_modo_audio(False))
botao_mp3.pack(side="left", padx=5)
botao_mp4.pack(side="left", padx=5)

definir_modo_audio(True)

btn_open = tk.Button(container, text=t("btn_open_folder"), command=abrir_pasta)
btn_open.pack(pady=5)

# Rodapé
footer_dev_label = tk.Label(janela, text="", anchor="e")
footer_dev_label.pack(side="bottom", anchor="se", padx=10, pady=(0, 0))

footer_hash_label = tk.Label(janela, text="", anchor="e", font=("Consolas", 8))
footer_hash_label.pack(side="bottom", anchor="se", padx=10, pady=(0, 6))

def set_language(lang: str):
    global current_lang
    current_lang = lang
    label_url.config(text=t("paste_url"))
    btn_open.config(text=t("btn_open_folder"))
    botao_mp3.config(text=t("btn_mp3"))
    botao_mp4.config(text=t("btn_mp4"))
    botao_converter.config(text=t("btn_convert_mp3") if modo_audio else t("btn_convert_mp4"))
    footer_dev_label.config(text=t("footer"))
    footer_hash_label.config(text=f"{t('hash_label')}: {APP_SHA256}")
    if current_lang == "pt":
        if br_img and us_img:
            btn_br_img.config(relief="sunken")
            btn_us_img.config(relief="raised")
        else:
            btn_br.config(relief="sunken")
            btn_us.config(relief="raised")
    else:
        if br_img and us_img:
            btn_br_img.config(relief="raised")
            btn_us_img.config(relief="sunken")
        else:
            btn_br.config(relief="raised")
            btn_us.config(relief="sunken")

btn_br_img = btn_us_img = None
if br_img and us_img:
    btn_br_img = tk.Button(topbar, image=br_img, command=lambda: set_language("pt"))
    btn_us_img = tk.Button(topbar, image=us_img, command=lambda: set_language("en"))
    btn_br_img.image = br_img
    btn_us_img.image = us_img
    btn_br_img.grid(row=0, column=0, padx=(0, 6))
    btn_us_img.grid(row=0, column=1)
else:
    btn_br = tk.Button(topbar, text="🇧🇷", width=3, font=("Arial", 14, "bold"), command=lambda: set_language("pt"))
    btn_us = tk.Button(topbar, text="🇺🇸", width=3, font=("Arial", 14, "bold"), command=lambda: set_language("en"))
    btn_br.grid(row=0, column=0, padx=(0, 6))
    btn_us.grid(row=0, column=1)

set_language("pt")

try:
    if btn_br_img and btn_us_img:
        btn_br_img.config(relief="sunken")
        btn_us_img.config(relief="raised")
except Exception:
    pass

janela.mainloop()
