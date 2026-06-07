#!/usr/bin/env python3
"""
Audio Intelligence Layer
Extensive MP3 analysis: tags, structure, semantics, lyrics, emotion detection.
"""

import json
import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from loguru import logger

import librosa
import numpy as np
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3

from core.audio_analysis import AudioAnalyzer, AudioAnalysis


class SongSection(Enum):
    """Song structure sections"""
    INTRO = "intro"
    VERSE = "verse"
    PRE_CHORUS = "pre_chorus"
    CHORUS = "chorus"
    BRIDGE = "bridge"
    OUTRO = "outro"
    BREAKDOWN = "breakdown"
    BUILD_UP = "build_up"
    DROP = "drop"


class Mood(Enum):
    """Emotional mood classification"""
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    CALM = "calm"
    ENERGETIC = "energetic"
    MELANCHOLIC = "melancholic"
    PLAYFUL = "playful"
    INTENSE = "intense"


@dataclass
class SongStructure:
    """Detected song structure"""
    sections: List[Tuple[float, float, SongSection]] = field(default_factory=list)
    verse_times: List[Tuple[float, float]] = field(default_factory=list)
    chorus_times: List[Tuple[float, float]] = field(default_factory=list)
    bridge_times: List[Tuple[float, float]] = field(default_factory=list)
    drop_times: List[Tuple[float, float]] = field(default_factory=list)
    breath_times: List[float] = field(default_factory=list)


@dataclass
class AudioTags:
    """MP3 ID3 Tags"""
    artist: Optional[str] = None
    title: Optional[str] = None
    album: Optional[str] = None
    genre: Optional[str] = None
    year: Optional[str] = None
    bpm: Optional[int] = None
    key: Optional[str] = None
    custom_tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class EmotionProfile:
    """Emotion and mood analysis"""
    primary_mood: Mood
    mood_confidence: float
    energy_curve: np.ndarray
    intensity_curve: np.ndarray
    valence: float  # Positivity -1 to 1
    arousal: float  # Calmness -1 to 1
    tension_curve: np.ndarray


@dataclass
class SongIntelligence:
    """Complete song analysis"""
    audio_path: str
    tags: AudioTags
    audio_analysis: AudioAnalysis
    structure: SongStructure
    emotion: EmotionProfile
    lyrics: Optional[str] = None
    lyric_themes: List[str] = field(default_factory=list)


class AudioIntelligenceAnalyzer:
    """Comprehensive audio intelligence system"""

    def __init__(self):
        """
        Initialize Audio Intelligence Analyzer
        """
        self.audio_analyzer = AudioAnalyzer()
        logger.info("AudioIntelligenceAnalyzer initialized")

    def analyze_complete(self, audio_path: str) -> SongIntelligence:
        """
        Perform complete song analysis
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            SongIntelligence object
        """
        logger.info(f"Starting complete song analysis: {audio_path}")
        
        try:
            # Extract tags
            tags = self._extract_tags(audio_path)
            
            # Audio analysis
            audio_analysis = self.audio_analyzer.analyze(audio_path)
            
            # Detect song structure
            structure = self._detect_structure(audio_analysis)
            
            # Emotion profiling
            emotion = self._analyze_emotion(audio_analysis)
            
            # Extract lyrics (if available)
            lyrics = self._extract_lyrics(audio_path, tags)
            lyric_themes = self._analyze_lyric_themes(lyrics) if lyrics else []
            
            song_intelligence = SongIntelligence(
                audio_path=audio_path,
                tags=tags,
                audio_analysis=audio_analysis,
                structure=structure,
                emotion=emotion,
                lyrics=lyrics,
                lyric_themes=lyric_themes
            )
            
            logger.success(f"Song analysis complete: {tags.title} by {tags.artist}")
            return song_intelligence
            
        except Exception as e:
            logger.error(f"Error analyzing song: {e}")
            raise

    def _extract_tags(self, audio_path: str) -> AudioTags:
        """
        Extract ID3 tags from MP3
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            AudioTags object
        """
        logger.debug(f"Extracting tags from {audio_path}")
        
        try:
            audio = EasyID3(audio_path)
            tags = AudioTags(
                artist=audio.get('artist', [None])[0],
                title=audio.get('title', [None])[0],
                album=audio.get('album', [None])[0],
                genre=audio.get('genre', [None])[0],
                year=audio.get('date', [None])[0],
                bpm=int(audio.get('bpm', ['0'])[0]) if audio.get('bpm') else None,
                key=audio.get('initialkey', [None])[0],
            )
            
            # Extract custom tags
            custom_tags = {k: v[0] for k, v in audio.items() 
                          if k not in ['artist', 'title', 'album', 'genre', 'date', 'bpm', 'initialkey']}
            tags.custom_tags = custom_tags
            
            logger.debug(f"Tags extracted: {tags.title} by {tags.artist}")
            return tags
            
        except Exception as e:
            logger.warning(f"Error extracting tags: {e}")
            return AudioTags()

    def _detect_structure(self, audio_analysis: AudioAnalysis) -> SongStructure:
        """
        Detect song structure (verses, choruses, drops, etc.)
        
        Args:
            audio_analysis: AudioAnalysis object
            
        Returns:
            SongStructure object
        """
        logger.debug("Detecting song structure...")
        
        structure = SongStructure()
        
        # Detect drops (sudden energy increase)
        drops = self._detect_drops(audio_analysis.energy)
        structure.drop_times = drops
        
        # Detect breaks (silence/low energy)
        breaks = self._detect_breaks(audio_analysis.energy)
        structure.breath_times = [b for b, _ in breaks]
        
        logger.debug(f"Detected {len(drops)} drops and {len(breaks)} breaks")
        return structure

    def _detect_drops(self, energy: np.ndarray, threshold: float = 0.3) -> List[Tuple[float, float]]:
        """
        Detect energy drops (sudden increases)
        
        Args:
            energy: Energy array from audio analysis
            threshold: Drop threshold
            
        Returns:
            List of (time, energy_increase) tuples
        """
        drops = []
        hop_length = 512
        sr = 22050
        
        for i in range(1, len(energy) - 1):
            prev_energy = np.mean(energy[max(0, i-10):i])
            curr_energy = energy[i]
            next_energy = np.mean(energy[i:min(len(energy), i+10)])
            
            if curr_energy - prev_energy > threshold and curr_energy > next_energy * 0.8:
                time = librosa.frames_to_time(i, sr=sr, hop_length=hop_length)
                drops.append((time, curr_energy - prev_energy))
        
        return drops

    def _detect_breaks(self, energy: np.ndarray, threshold: float = 0.2) -> List[Tuple[float, float]]:
        """
        Detect breaks/breath points (low energy)
        
        Args:
            energy: Energy array
            threshold: Break threshold
            
        Returns:
            List of (time, duration) tuples
        """
        breaks = []
        hop_length = 512
        sr = 22050
        
        in_break = False
        break_start = 0
        
        for i in range(len(energy)):
            if energy[i] < threshold and not in_break:
                in_break = True
                break_start = i
            elif energy[i] >= threshold and in_break:
                in_break = False
                break_end = i
                start_time = librosa.frames_to_time(break_start, sr=sr, hop_length=hop_length)
                end_time = librosa.frames_to_time(break_end, sr=sr, hop_length=hop_length)
                breaks.append((start_time, end_time - start_time))
        
        return breaks

    def _analyze_emotion(self, audio_analysis: AudioAnalysis) -> EmotionProfile:
        """
        Analyze emotional content
        
        Args:
            audio_analysis: AudioAnalysis object
            
        Returns:
            EmotionProfile object
        """
        logger.debug("Analyzing emotion...")
        
        # Energy-based mood
        mean_energy = np.mean(audio_analysis.energy)
        std_energy = np.std(audio_analysis.energy)
        
        # Spectral features
        mean_centroid = np.mean(audio_analysis.spectral_centroid)
        
        # Determine primary mood
        if mean_energy > 0.7:
            primary_mood = Mood.ENERGETIC if std_energy > 0.2 else Mood.HAPPY
        elif mean_energy < 0.3:
            primary_mood = Mood.CALM if mean_centroid < 4000 else Mood.MELANCHOLIC
        else:
            primary_mood = Mood.PLAYFUL
        
        # Create energy curve
        energy_curve = audio_analysis.energy
        
        # Create intensity curve
        intensity_curve = (energy_curve - np.min(energy_curve)) / (np.max(energy_curve) - np.min(energy_curve) + 1e-8)
        
        # Valence (positivity)
        valence = 1.0 if mean_centroid > 5000 else -0.5 if mean_centroid < 2000 else 0.0
        
        # Arousal (calmness)
        arousal = -1.0 if std_energy < 0.1 else 0.5 if std_energy < 0.3 else 1.0
        
        # Tension curve
        tension_curve = np.abs(np.diff(energy_curve, prepend=energy_curve[0]))
        
        emotion = EmotionProfile(
            primary_mood=primary_mood,
            mood_confidence=0.7 + (std_energy / 10),
            energy_curve=energy_curve,
            intensity_curve=intensity_curve,
            valence=valence,
            arousal=arousal,
            tension_curve=tension_curve
        )
        
        logger.debug(f"Emotion detected: {primary_mood.value}")
        return emotion

    def _extract_lyrics(self, audio_path: str, tags: AudioTags) -> Optional[str]:
        """
        Extract lyrics from ID3 tags or file
        
        Args:
            audio_path: Path to audio file
            tags: AudioTags object
            
        Returns:
            Lyrics text or None
        """
        try:
            # Try ID3 USLT frame
            audio = ID3(audio_path)
            for frame in audio.values():
                if frame.FrameID == 'USLT':
                    return frame.text[0] if frame.text else None
        except Exception as e:
            logger.debug(f"Could not extract lyrics from ID3: {e}")
        
        return None

    def _analyze_lyric_themes(self, lyrics: str) -> List[str]:
        """
        Analyze lyric themes/topics
        
        Args:
            lyrics: Lyrics text
            
        Returns:
            List of detected themes
        """
        themes = []
        
        # Simple keyword-based theme detection
        theme_keywords = {
            'love': ['love', 'heart', 'kiss', 'baby', 'lover'],
            'party': ['party', 'dance', 'club', 'weekend', 'fun'],
            'sadness': ['cry', 'sad', 'down', 'alone', 'pain'],
            'strength': ['strong', 'fight', 'power', 'warrior', 'conquer'],
            'success': ['win', 'success', 'goal', 'achieve', 'climb']
        }
        
        lyrics_lower = lyrics.lower()
        for theme, keywords in theme_keywords.items():
            if any(kw in lyrics_lower for kw in keywords):
                themes.append(theme)
        
        return themes

    def export_intelligence_json(self, intelligence: SongIntelligence, output_path: str) -> None:
        """
        Export song intelligence as JSON
        
        Args:
            intelligence: SongIntelligence object
            output_path: Output JSON file path
        """
        export_data = {
            'tags': asdict(intelligence.tags),
            'audio_analysis': {
                'bpm': float(intelligence.audio_analysis.bpm),
                'duration': float(intelligence.audio_analysis.duration),
                'sample_rate': intelligence.audio_analysis.sample_rate,
            },
            'structure': {
                'drops': [(float(t), float(e)) for t, e in intelligence.structure.drop_times],
                'breaths': [float(t) for t in intelligence.structure.breath_times]
            },
            'emotion': {
                'mood': intelligence.emotion.primary_mood.value,
                'mood_confidence': float(intelligence.emotion.mood_confidence),
                'valence': float(intelligence.emotion.valence),
                'arousal': float(intelligence.emotion.arousal)
            },
            'lyric_themes': intelligence.lyric_themes
        }
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        logger.success(f"Song intelligence exported to {output_path}")
