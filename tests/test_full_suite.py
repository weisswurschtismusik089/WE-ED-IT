#!/usr/bin/env python3
"""
Full Test Suite
Comprehensive testing of all core modules.
"""

import os
import sys
import json
from pathlib import Path
from loguru import logger

from core.audio_analysis import AudioAnalyzer
from core.audio_intelligence import AudioIntelligenceAnalyzer
from core.clip_analyzer import ClipAnalyzer
from db.metadata_db import MetadataDB
from db.clip_vault import ClipVault
from ml.vector_logic import VectorLogicMatcher
from hw.hardware_detection import HardwareDetector, HardwareOptimizer
from utils.logger import setup_logger


def setup_test_environment():
    """
    Setup test environment
    """
    setup_logger("logs/test.log")
    logger.info("=" * 60)
    logger.info("WE.ED.IT - Full Test Suite")
    logger.info("=" * 60)


def test_audio_analysis(audio_path: str) -> bool:
    """
    Test audio analysis module
    
    Args:
        audio_path: Path to test audio file
        
    Returns:
        True if successful
    """
    logger.info("\n[TEST] Audio Analysis Module")
    try:
        analyzer = AudioAnalyzer()
        analysis = analyzer.analyze(audio_path)
        
        logger.success(f"✓ Audio loaded: {analysis.duration:.2f}s @ {analysis.sample_rate}Hz")
        logger.success(f"✓ BPM: {analysis.bpm:.1f}")
        logger.success(f"✓ Beats detected: {len(analysis.beat_times)}")
        logger.success(f"✓ Segments generated: {len(analyzer.get_beat_aligned_segments(analysis.beat_times, analysis.duration))}")
        
        return True
    except Exception as e:
        logger.error(f"✗ Audio analysis failed: {e}")
        return False


def test_audio_intelligence(audio_path: str) -> bool:
    """
    Test audio intelligence analyzer
    
    Args:
        audio_path: Path to test audio file
        
    Returns:
        True if successful
    """
    logger.info("\n[TEST] Audio Intelligence Module")
    try:
        analyzer = AudioIntelligenceAnalyzer()
        intelligence = analyzer.analyze_complete(audio_path)
        
        logger.success(f"✓ Song: {intelligence.tags.title} by {intelligence.tags.artist}")
        logger.success(f"✓ Genre: {intelligence.tags.genre}")
        logger.success(f"✓ BPM: {intelligence.tags.bpm}")
        logger.success(f"✓ Primary mood: {intelligence.emotion.primary_mood.value}")
        logger.success(f"✓ Detected {len(intelligence.structure.drop_times)} drops")
        logger.success(f"✓ Detected {len(intelligence.structure.breath_times)} breath points")
        logger.success(f"✓ Lyric themes: {intelligence.lyric_themes}")
        
        # Export
        os.makedirs("test_output", exist_ok=True)
        analyzer.export_intelligence_json(intelligence, "test_output/song_intelligence.json")
        logger.success(f"✓ Exported to test_output/song_intelligence.json")
        
        return True
    except Exception as e:
        logger.error(f"✗ Audio intelligence failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def test_hardware_detection() -> bool:
    """
    Test hardware detection
    
    Returns:
        True if successful
    """
    logger.info("\n[TEST] Hardware Detection")
    try:
        detector = HardwareDetector()
        profile = detector.detect_hardware()
        
        logger.success(f"✓ Device: {profile.device.value}")
        logger.success(f"✓ CPU Cores: {profile.cpu_cores}")
        logger.success(f"✓ RAM: {profile.ram_gb:.2f}GB")
        if profile.gpu_name:
            logger.success(f"✓ GPU: {profile.gpu_name} ({profile.vram_gb:.2f}GB)")
        
        optimizer = HardwareOptimizer(profile)
        settings = optimizer.get_optimal_settings()
        logger.success(f"✓ Optimal settings: {json.dumps(settings, indent=2)}")
        
        return True
    except Exception as e:
        logger.error(f"✗ Hardware detection failed: {e}")
        return False


def test_metadata_db() -> bool:
    """
    Test metadata database
    
    Returns:
        True if successful
    """
    logger.info("\n[TEST] Metadata Database")
    try:
        db = MetadataDB("test_output/db")
        
        # Add test data
        test_song = {
            'title': 'Test Song',
            'artist': 'Test Artist',
            'genre': 'hip_hop',
            'bpm': 120
        }
        db.add_song("test.mp3", test_song)
        logger.success(f"✓ Song added to database")
        
        # Retrieve
        retrieved = db.get_song("test.mp3")
        logger.success(f"✓ Song retrieved: {retrieved['title']}")
        
        # Export
        db.export_metadata_json("test_output/database_export.json")
        logger.success(f"✓ Database exported")
        
        return True
    except Exception as e:
        logger.error(f"✗ Metadata database failed: {e}")
        return False


def test_vector_logic() -> bool:
    """
    Test vector logic system
    
    Returns:
        True if successful
    """
    logger.info("\n[TEST] Vector Logic System")
    try:
        matcher = VectorLogicMatcher()
        
        # Create song vector
        song_vector = matcher.create_song_vector(
            gender="female",
            genre="hip_hop",
            bpm=120,
            energy=0.8,
            mood="energetic",
            narrative="party"
        )
        logger.success(f"✓ Song vector created")
        
        # Create clip vectors
        clip_vector1 = matcher.create_clip_vector(
            gender="female",
            shot_scale="close_up",
            camera_movement="tracking",
            lighting="cool",
            emotional_intensity=0.8,
            dynamic_score=0.7
        )
        logger.success(f"✓ Clip vector 1 created")
        
        clip_vector2 = matcher.create_clip_vector(
            gender="male",
            shot_scale="wide",
            camera_movement="static",
            lighting="warm",
            emotional_intensity=0.5,
            dynamic_score=0.3
        )
        logger.success(f"✓ Clip vector 2 created")
        
        # Match
        matches = matcher.match_song_to_clips(
            song_vector,
            [("clip1.mp4", clip_vector1), ("clip2.mp4", clip_vector2)]
        )
        logger.success(f"✓ Matching complete:")
        for clip_id, score in matches:
            logger.success(f"  - {clip_id}: {score:.3f}")
        
        return True
    except Exception as e:
        logger.error(f"✗ Vector logic failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def run_all_tests(audio_path: str, video_dir: Optional[str] = None) -> None:
    """
    Run all tests
    
    Args:
        audio_path: Path to test audio file
        video_dir: Path to test video directory
    """
    setup_test_environment()
    
    results = {}
    
    # Check prerequisites
    if not os.path.exists(audio_path):
        logger.error(f"Audio file not found: {audio_path}")
        return
    
    logger.info(f"Test audio: {audio_path}")
    if video_dir:
        logger.info(f"Test video directory: {video_dir}")
    
    # Run tests
    results['audio_analysis'] = test_audio_analysis(audio_path)
    results['audio_intelligence'] = test_audio_intelligence(audio_path)
    results['hardware_detection'] = test_hardware_detection()
    results['metadata_db'] = test_metadata_db()
    results['vector_logic'] = test_vector_logic()
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"{status}: {test_name}")
    
    logger.info(f"\nTotal: {passed}/{total} tests passed")
    logger.info("=" * 60)
    
    if passed == total:
        logger.success("\n🎉 All tests passed!")
    else:
        logger.warning(f"\n⚠️  {total - passed} test(s) failed")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="WE.ED.IT Test Suite")
    parser.add_argument('--audio', required=True, help='Path to test audio file')
    parser.add_argument('--videos', help='Path to test video directory')
    
    args = parser.parse_args()
    
    run_all_tests(args.audio, args.videos)
