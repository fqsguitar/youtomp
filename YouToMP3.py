import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import threading
import os
import re
import sys
import hashlib
from pathlib import Path

# ======================== CONFIG ========================
NOME_PROGRAMA = "YouToMP"
CREATE_NO_WINDOW = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
PASTA_DESTINO = Path.home() / "Downloads" / NOME_PROGRAMA
PASTA_DESTINO.mkdir(parents=True, exist_ok=True)
FFMPEG_PATH = "C:/ProgramData/chocolatey/lib/ffmpeg/tools/ffmpeg/bin"

def get_resource_path(filename):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, filename)
    return os.path.join(os.path.abspath("."), filename)

ICONE_ICO_PATH = get_resource_path("yt_mp3_converter_multi_res.ico")

# ======================== SHA256 DO APP ========================
def compute_self_sha256():
    """
    Calcula o SHA-256 do próprio app:
    - Se empacotado (--onefile), aponta para o executável (sys.executable)
    - Caso contrário, aponta para este arquivo .py
    """
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
    },
}
current_lang = "pt"

def t(key: str) -> str:
    return texts[current_lang][key]

# ======================== FUNÇÕES ========================
def abrir_pasta():
    os.startfile(PASTA_DESTINO)

def baixar(url, status_label, progress_bar, progress_label, modo_audio):
    try:
        status_label.config(text=t("downloading"))
        progress_bar["value"] = 0
        progress_label.config(text="0%")

        match = re.search(r"(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})", url)
        if not match:
            raise Exception(t("invalid_url"))
        video_id = match.group(1)
        clean_url = f"https://www.youtube.com/watch?v={video_id}"

        ext = "mp3" if modo_audio else "mp4"
        output_template = str(PASTA_DESTINO / "%(title)s.%(ext)s")
        arquivos_antes = set(PASTA_DESTINO.glob(f"*.{ext}"))

        comando = ["yt-dlp", "--ffmpeg-location", FFMPEG_PATH, "-o", output_template]

        if modo_audio:
            comando += ["-x", "--audio-format", "mp3", "--audio-quality", "0", "--no-keep-video"]
        else:
            comando += ["-f", "bestvideo+bestaudio", "--merge-output-format", "mp4"]

        comando.append(clean_url)

        processo = subprocess.Popen(
            comando,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            creationflags=CREATE_NO_WINDOW
        )

        for linha in processo.stdout:
            linha = linha.strip()
            match = re.search(r"\[download\]\s+(\d{1,3}(?:\.\d+)?)%", linha)
            if match:
                progresso = float(match.group(1))
                progress_bar["value"] = progresso
                progress_label.config(text=f"{int(progresso)}%")
                progress_bar.update_idletasks()
                progress_label.update_idletasks()

        processo.wait()
        arquivos_depois = set(PASTA_DESTINO.glob(f"*.{ext}"))
        novos = list(arquivos_depois - arquivos_antes)

        if processo.returncode == 0 and novos:
            caminho_final = novos[0]
            progress_bar["value"] = 100
            progress_label.config(text="100%")
            status_label.config(text=t("gen_success").format(ext.upper()))
            messagebox.showinfo(t("success_title"), t("saved_in").format(ext.upper(), caminho_final))
        else:
            status_label.config(text=t("gen_fail").format(ext.upper()))
            messagebox.showerror(t("error_title"), t("dl_fail"))
    except Exception as e:
        status_label.config(text=t("unexpected"))
        messagebox.showerror(t("error_title"), str(e))

def iniciar_thread(url_entry, status_label, progress_bar, progress_label, modo_audio):
    url = url_entry.get().strip()
    if not url:
        messagebox.showwarning(t("warn_title"), t("warn_paste"))
        return

    match = re.search(r"(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})", url)
    if not match:
        messagebox.showwarning(t("warn_title"), t("warn_invalid"))
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
janela.update_idletasks()
pos_x = (janela.winfo_screenwidth() // 2) - (largura // 2)
pos_y = (janela.winfo_screenheight() // 2) - (altura // 2)
janela.geometry(f"{largura}x{altura}+{pos_x}+{pos_y}")

try:
    janela.iconbitmap(ICONE_ICO_PATH)
except Exception as e:
    print("Erro ao aplicar ícone .ico:", e)

# Barra superior (idiomas) no canto superior esquerdo
topbar = tk.Frame(janela)
topbar.pack(anchor="nw", padx=8, pady=6)

# ===== Carrega bandeiras PNG (Flags\br.png e Flags\us.png), com fallback p/ emoji =====
FLAGS_DIR = get_resource_path("Flags")
BR_FLAG_PATH = os.path.join(FLAGS_DIR, "br.png")
US_FLAG_PATH = os.path.join(FLAGS_DIR, "us.png")
br_img = us_img = None
try:
    if os.path.exists(BR_FLAG_PATH) and os.path.exists(US_FLAG_PATH):
        # Reduz 72x72 -> ~24x24 (ajusta se quiser menor/maior: .subsample(4,4) = ~18x18)
        br_img = tk.PhotoImage(file=BR_FLAG_PATH).subsample(3, 3)
        us_img = tk.PhotoImage(file=US_FLAG_PATH).subsample(3, 3)
except Exception:
    br_img = us_img = None

# Container do conteúdo
container = tk.Frame(janela)
container.pack(pady=10)

# Widgets (criados já com texto de PT como default)
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

modo_audio = True  # Começa em MP3

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

# Botão abrir pasta
btn_open = tk.Button(container, text=t("btn_open_folder"), command=abrir_pasta)
btn_open.pack(pady=5)

# ======================== Rodapé (duas linhas) ========================
# Linha 1: "por FQ" / "by FQ"
footer_dev_label = tk.Label(janela, text="", anchor="e")
footer_dev_label.pack(side="bottom", anchor="se", padx=10, pady=(0, 0))

# Linha 2: "SHA256: <hash>" (monoespaçado, menor)
footer_hash_label = tk.Label(janela, text="", anchor="e", font=("Consolas", 8))
footer_hash_label.pack(side="bottom", anchor="se", padx=10, pady=(0, 6))

# ======================== Idiomas ========================
def set_language(lang: str):
    global current_lang
    current_lang = lang

    # Atualiza textos dos widgets
    label_url.config(text=t("paste_url"))
    btn_open.config(text=t("btn_open_folder"))
    botao_mp3.config(text=t("btn_mp3"))
    botao_mp4.config(text=t("btn_mp4"))
    botao_converter.config(text=t("btn_convert_mp3") if modo_audio else t("btn_convert_mp4"))

    # Rodapé (duas linhas)
    footer_dev_label.config(text=t("footer"))
    footer_hash_label.config(text=f"{t('hash_label')}: {APP_SHA256}")

    # Ajusta visual dos botões de bandeira
    if current_lang == "pt":
        if btn_br_img:
            btn_br_img.config(relief="sunken")
            btn_us_img.config(relief="raised")
        else:
            btn_br.config(relief="sunken")
            btn_us.config(relief="raised")
    else:
        if btn_br_img:
            btn_br_img.config(relief="raised")
            btn_us_img.config(relief="sunken")
        else:
            btn_br.config(relief="raised")
            btn_us.config(relief="sunken")

# Botões de idioma
btn_br_img = btn_us_img = None
if br_img and us_img:
    btn_br_img = tk.Button(topbar, image=br_img, command=lambda: set_language("pt"))
    btn_us_img = tk.Button(topbar, image=us_img, command=lambda: set_language("en"))
    # evita coleta de lixo
    btn_br_img.image = br_img
    btn_us_img.image = us_img
    btn_br_img.grid(row=0, column=0, padx=(0, 6))
    btn_us_img.grid(row=0, column=1)
else:
    # fallback: emojis
    btn_br = tk.Button(topbar, text="🇧🇷", width=3, font=("Arial", 14, "bold"), command=lambda: set_language("pt"))
    btn_us = tk.Button(topbar, text="🇺🇸", width=3, font=("Arial", 14, "bold"), command=lambda: set_language("en"))
    btn_br.grid(row=0, column=0, padx=(0, 6))
    btn_us.grid(row=0, column=1)

# Inicializa estados padrão
definir_modo_audio(True)   # deixa MP3 "afundado"
set_language("pt")         # inicia em PT-BR e “afunda” 🇧🇷

# Ajuste visual inicial dos botões de bandeira (quando usa PNG)
try:
    if btn_br_img and btn_us_img:
        btn_br_img.config(relief="sunken")
        btn_us_img.config(relief="raised")
except Exception:
    pass

janela.mainloop()
