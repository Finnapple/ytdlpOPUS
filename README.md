# 🎵 ytdlpOPUS — YouTube Music Downloader

> A lightweight command-line downloader that preserves original **Opus audio quality** from YouTube Music — with clean metadata, no bloat.

---

## ✨ Features

- 🎧 Downloads in **native Opus format** — no re-encoding, no quality loss
- 📀 Supports **tracks, playlists, and albums**
- 🏷️ Clean, accurate **metadata** on every download
- 🖼️ Optional **album art embedding** via `embedder.py`
- 🧹 Built-in **file cleanup** via `delete.py`
- 🐧 Cross-platform — works on **Windows, Linux, and macOS**
- 🔰 Simple terminal interface — no GUI needed

---

## 📋 Requirements

- Python **3.8+** (added to PATH)
- [FFmpeg](https://ffmpeg.org/download.html) installed on your system

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/Finnapple/ytdlpOPUS.git
cd ytdlpOPUS
```

### 2. Run the installer

**Windows:**
```bash
setup.bat
```

**Linux / macOS:**
```bash
chmod +x setup.sh
./setup.sh
```

> The setup script automatically creates a virtual environment and installs all required packages.

### 3. Start downloading

**Windows:**
```bash
ytdlp_opus.bat
```

**Linux / macOS:**
```bash
python ytdlp_opus.py
```

Paste your YouTube Music URL and the downloader handles the rest!

---

## 🖼️ Embedding Album Art

Downloaded Opus files don't include album art by default — keeping them lightweight and clean. To embed artwork after downloading, run:

**Windows:**
```bash
embedder.bat
```

**Or directly:**
```bash
python embedder.py
```

This keeps your library visually consistent in any music player.

---

## 🗑️ Cleaning Up Files

To delete downloaded files or temp data:

**Windows:**
```bash
delete.bat
```

**Or directly:**
```bash
python delete.py
```

---

## 🗂️ Project Structure

```
ytdlpOPUS/
├── ytdlp_opus.py    # Core downloader script
├── ytdlp_opus.bat   # Windows launcher
├── embedder.py      # Album art embedder
├── embedder.bat     # Windows launcher for embedder
├── delete.py        # File cleanup script
├── delete.bat       # Windows launcher for cleanup
├── setup.bat        # Windows installer
└── setup.sh         # Linux/macOS installer
```

---

## ❓ Why Opus?

Opus is the native audio format used by YouTube Music. Downloading in Opus means:

- ✅ **No re-encoding** — the file is saved exactly as streamed
- ✅ **No quality loss** — what you hear on YouTube Music is what you get
- ✅ **Smaller file sizes** compared to equivalent MP3 quality

---

## 🤝 Contributing

Issues and pull requests are welcome!  
Feel free to open an [issue](https://github.com/Finnapple/ytdlpOPUS/issues) if you run into problems or have ideas.

---

## 📄 License

This project is open source. See the repository for details.

---

<p align="center">Made with ❤️ by <a href="https://github.com/Finnapple">Finnapple</a></p>
