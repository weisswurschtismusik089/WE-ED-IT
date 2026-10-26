#!/usr/bin/env python3
"""
Debug Helper
Quick debugging and file inspection.
"""

import os
import sys
from pathlib import Path
from loguru import logger

from utils.logger import setup_logger
from utils.file_manager import FileManager
from core.audio_analysis import AudioAnalyzer
from core.audio_intelligence import AudioIntelligenceAnalyzer


def debug_audio_file(audio_path: str):
    """
    Debug audio file
    
    Args:
        audio_path: Path to audio file
    """
    setup_logger("logs/debug.log")
    
    logger.info("=" * 70)
    logger.info("WE.ED.IT Debug Assistant")
    logger.info("=" * 70)
    
    if not os.path.exists(audio_path):
        logger.error(f"File not found: {audio_path}")
        return
    
    logger.info(f"\nAudio File: {audio_path}")
    logger.info(f"File size: {os.path.getsize(audio_path) / (1024*1024):.2f} MB")
    
    try:
        # Audio Analysis
        logger.info("\n[1] Basic Audio Analysis...")
        analyzer = AudioAnalyzer()
        analysis = analyzer.analyze(audio_path)
        
        logger.success(f"✓ Duration: {analysis.duration:.2f}s")
        logger.success(f"✓ Sample rate: {analysis.sample_rate} Hz")
        logger.success(f"✓ BPM: {analysis.bpm:.1f}")
        logger.success(f"✓ Beats: {len(analysis.beat_times)}")
        logger.success(f"✓ Onsets: {len(analysis.onset_times)}")
        
        # Audio Intelligence
        logger.info("\n[2] Audio Intelligence Analysis...")
        intelligence_analyzer = AudioIntelligenceAnalyzer()
        intelligence = intelligence_analyzer.analyze_complete(audio_path)
        
        logger.success(f"✓ Title: {intelligence.tags.title or 'Unknown'}")
        logger.success(f"✓ Artist: {intelligence.tags.artist or 'Unknown'}")
        logger.success(f"✓ Genre: {intelligence.tags.genre or 'Unknown'}")
        logger.success(f"✓ BPM: {intelligence.tags.bpm}")
        logger.success(f"✓ Primary mood: {intelligence.emotion.primary_mood.value}")
        logger.success(f"✓ Drops detected: {len(intelligence.structure.drop_times)}")
        logger.success(f"✓ Breath points: {len(intelligence.structure.breath_times)}")
        logger.success(f"✓ Lyric themes: {intelligence.lyric_themes}")
        
        # Export
        logger.info("\n[3] Exporting analysis...")
        os.makedirs("debug_output", exist_ok=True)
        intelligence_analyzer.export_intelligence_json(
            intelligence,
            "debug_output/song_analysis.json"
        )
        logger.success(f"✓ Analysis exported to debug_output/song_analysis.json")
        
        logger.info("\n" + "=" * 70)
        logger.success("\n✨ Debug analysis complete!\n")
        
    except Exception as e:
        logger.error(f"Error during analysis: {e}")
        import traceback
        logger.error(traceback.format_exc())


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="WE.ED.IT Debug Helper")
    parser.add_argument('--audio', required=True, help='Path to audio file')
    
    args = parser.parse_args()
    
    debug_audio_file(args.audio)
