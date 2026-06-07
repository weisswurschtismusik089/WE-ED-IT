# WE.ED.IT - AI Art Director & Intelligent Beat-Sync Video Editor

> "Musik dirigiert. KI schneidet. Du kreierst."

WE.ED.IT ist der erste intelligente KI-Regisseur für Musikvideos. Die Song ist der Director. Die Clips sind die Darsteller. Die KI ist der Cutter mit jahrelanger Musikvideo-Erfahrung.

## 🎬 Kernphilosophie

**Die Song gibt den Takt vor – die Clips tanzen danach.**

- 🎵 **Musikverständnis auf Profi-Niveau**: Vollständige MP3-Tag-, Lyric-, Struktur- & Semantik-Analyse
- 🎬 **Smarter Clip-Pool**: Automatisches Einlesen mit Symlink-Unterstützung, keine Dateien werden bewegt
- 🧠 **Tiefe KI-Visuelle Analyse**: Shot Composition, Kamerabewegung, Lighting, Emotion, Dynamik
- 🎯 **Vector Logic**: Gender Vectors, bidirektionale "Hast du? - Brauchst du?"-Matching
- ⚡ **Professionelle Schnittmuster**: Automatische Beat-, Breath- & Drop-Schnitte
- 📊 **Realistisches Viral Scoring**: Mit konkreten Verbesserungstipps
- 🖥️ **Hardware-Optimiert**: Voll lokal, GPU-Support, auch ältere Hardware

## 🎯 Features

### 1. Audio-Intelligence
- ✅ MP3-Tag Extraction (Artist, Genre, BPM, Lyrics, Custom Tags)
- ✅ Song-Struktur Analyse (Verse, Chorus, Bridge, Drop, Breakdown)
- ✅ Semantische Emotion-Erkennung (Energy, Mood, Intensity Curves)
- ✅ Beat, Breath & Drop Detection
- ✅ Dynamic Timeline mit intelligenten Schnittmarkern

### 2. Video Vault (Clip-Pool)
- ✅ Rekursives Einlesen mit Symlink-Support
- ✅ Keine Quelldateien werden verändert
- ✅ Interne JSON/Node-basierte Database
- ✅ NFO-Datei-Extraktion (Metadaten, Subtitle-Info)
- ✅ Auto-Tagging basierend auf Dateiname & Inhaltsanalyse

### 3. KI-Visuelle Analyse
- ✅ Shot Composition (Wide, Medium, Close-up, ECU)
- ✅ Camera Movement (Static, Pan, Tilt, Zoom, Tracking)
- ✅ Lighting Analysis (Key Light, Fill, Backlighting, Gels)
- ✅ Emotion & Dynamik Detection
- ✅ Export als JSON/CSV

### 4. Creative Vector Logic
- ✅ Gender Vector (z.B. weibliche Rapperinnen bei weiblichem Rap)
- ✅ Style Vector (Genre-Matching, Visual Style Alignment)
- ✅ Energy Vector (Intensity Matching zwischen Song & Clips)
- ✅ Story Vector (Narrative Flow & Visual Continuity)
- ✅ Bidirektionales Matching: "Hast du? – Brauchst du?"

### 5. Professional Director's Cutter
- ✅ Automatische Beat-Sync Schnitte
- ✅ Intelligent Transition Effects
- ✅ Dynamic Pacing & Rhythm-Based Cuts
- ✅ Face-Cut Optimization für Viral-Potential

### 6. Viral Scoring & Analytics
- ✅ Realistisches Viral Scoring (0-100)
- ✅ Konkrete Verbesserungstipps
  - "Mehr Face-Cuts im Drop +15% Viral-Potential"
  - "Schnellere Schnitte in Verse +8% Engagement"
  - "Bessere Farb-Balance +12% Watchtime"

### 7. Hardware & Performance
- ✅ Hardware-Detection (CPU, GPU, RAM)
- ✅ Automatische Optimierung für schwache Hardware
- ✅ GPU-Support (CUDA, OpenCL, Metal)
- ✅ Speichereffiziente Processing

## 📁 Projektstruktur

```
WE-ED-IT/
├── core/
│   ├── audio_analysis.py          # MP3-Tags, Struktur, Semantik
│   ├── audio_intelligence.py      # Song Intelligence Layer
│   ├── clip_analyzer.py           # KI-Visuelle Analyse
│   ├── clip_matcher.py            # Vector-based Matching
│   ├── video_renderer.py          # FFmpeg Rendering
│   ├── effects.py                 # Creative Effects
│   └── viral_scoring.py           # Viral Analytics
├── db/
│   ├── clip_vault.py              # Video Vault Management
│   ├── metadata_db.py             # JSON-basierte Metadaten-DB
│   ├── vector_store.py            # Vector Embeddings Storage
│   └── migrations/
├── ml/
│   ├── visual_analyzer.py         # Shot Composition, Camera, Lighting
│   ├── emotion_detector.py        # Emotion & Dynamik Recognition
│   ├── vector_logic.py            # Gender, Style, Energy Vectors
│   └── models/                    # Pre-trained Models
├── hw/
│   ├── hardware_detection.py      # GPU, CPU Detection
│   ├── optimization.py            # Hardware-specific Optimizations
│   └── gpu_support.py             # CUDA, OpenCL, Metal
├── utils/
│   ├── mp3_metadata.py
│   ├── file_manager.py
│   ├── logger.py
│   ├── nfo_parser.py              # NFO-Datei Parser
│   └── export.py                  # JSON/CSV Export
├── config/
│   ├── settings.yaml
│   ├── effects_config.json
│   └── vector_config.json
├── input/
│   ├── Sound/
│   └── ClipPool/
├── output/
├── db_data/                       # Interne Datenbank
├── main.py
├── requirements.txt
└── README.md
```

## 🚀 Installation

```bash
# Clone Repository
git clone https://github.com/weisswurschtismusik089/WE-ED-IT.git
cd WE-ED-IT

# Virtual Environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Dependencies
pip install -r requirements.txt

# FFmpeg (Required)
# macOS: brew install ffmpeg
# Linux: sudo apt-get install ffmpeg
# Windows: choco install ffmpeg
```

## 💻 Schnellstart

```bash
# Basis-Beispiel
python main.py --audio input/Sound/song.mp3 --output output/video.mp4

# Mit Custom Settings
python main.py \
  --audio input/Sound/song.mp3 \
  --output output/video.mp4 \
  --config config/settings.yaml \
  --quality high \
  --viral-mode

# Clip-Pool Analyse
python main.py --analyze-vault

# Export Metadata
python main.py --export-metadata output/metadata.json --format json
python main.py --export-metadata output/metadata.csv --format csv
```

## 🎯 Typischer Workflow

1. **MP3-Datei hochladen** → Audio Intelligence extrahiert Tags, Struktur, Lyrics
2. **Clip-Pool scannen** → Video Vault lädt alle Clips mit visueller Analyse
3. **Vector Matching** → Song & Clips werden semantisch gematcht
4. **Auto-Schnittmuster** → KI erzeugt professionelle Schnitte
5. **Viral Optimization** → Tipps zur Verbesserung
6. **Render & Export** → Finale Video mit allen Optimierungen

## 🧠 Vector Logic Beispiele

### Gender Vector
```python
# Song: Weibliche Rapperein → Zeige nur weibliche Rapper-Clips
if song.gender == "female" and song.genre == "rap":
    clips = clip_vault.filter(gender="female", vibe="rap")
```

### Energy Vector
```python
# Song-Energy: 0.8 (High) → Zeige dynamische, schnelle Clips
energy_vector = song.analyze_energy()  # [0-1]
clips = clip_vault.match_by_energy(energy_vector, tolerance=0.2)
```

### Story Vector
```python
# Song erzählt "Love Story" → Zeige emotionale, intime Clips
story_type = song.extract_narrative()
clips = clip_vault.match_by_narrative(story_type)
```

## 📊 Viral Scoring

```json
{
  "viral_score": 73,
  "improvements": [
    {
      "category": "Cuts in Drop",
      "current": 3,
      "recommended": 5,
      "potential_gain": "+15%"
    },
    {
      "category": "Face-Close-Ups",
      "current": 12,
      "recommended": 18,
      "potential_gain": "+12%"
    }
  ]
}
```

## 🔧 Hardware-Optimierung

WE.ED.IT detektiert automatisch die Hardware und optimiert:

- **GPU Support**: NVIDIA CUDA, AMD OpenCL, Apple Metal
- **CPU Fallback**: Effiziente CPU-basierte Processing
- **RAM-Optimierung**: Streaming statt vollständiges Laden
- **Old Hardware Mode**: Reduzierte Auflösung, schnellere Rendering

```bash
# Force CPU-only mode
python main.py --audio song.mp3 --device cpu

# GPU-accelerated
python main.py --audio song.mp3 --device gpu
```

## 📝 Lizenz

MIT License

## 🤝 Beitragen

Issues, Feature Requests und Pull Requests sind willkommen!

---

**WE.ED.IT** - Der erste echte KI Art Director für Musikvideos.
