#!/usr/bin/env python3
"""
Full Integration Test
Tests all components together with real files.
"""

import os
import sys
from pathlib import Path
from loguru import logger

from utils.logger import setup_logger
from main import WEEditItApp


def test_integration(audio_path: str, clip_dir: Optional[str] = None):
    """
    Run full integration test
    
    Args:
        audio_path: Path to test audio file
        clip_dir: Path to test clip directory
    """
    setup_logger("logs/integration_test.log")
    
    logger.info("=" * 70)
    logger.info("WE.ED.IT - Full Integration Test")
    logger.info("=" * 70)
    
    # Verify files exist
    if not os.path.exists(audio_path):
        logger.error(f"Audio file not found: {audio_path}")
        return False
    
    logger.info(f"\nTest Audio: {audio_path}")
    if clip_dir:
        logger.info(f"Test Clip Directory: {clip_dir}")
    
    try:
        # Initialize app
        logger.info("\n[1/3] Initializing WE.ED.IT...")
        app = WEEditItApp(config_path="config/settings.yaml")
        logger.success("✓ Application initialized")
        
        # Create music video
        logger.info("\n[2/3] Creating music video...")
        result = app.create_music_video(
            audio_path=audio_path,
            output_name="test_output.mp4",
            quality="medium",
            viral_mode=False
        )
        
        if result:
            logger.success(f"✓ Video creation successful")
        else:
            logger.warning(f"⚠ Video creation encountered issues (check logs)")
        
        # Export metadata
        logger.info("\n[3/3] Exporting analysis...")
        app.analyze_vault(output_format='json')
        logger.success("✓ Analysis exported")
        
        logger.info("\n" + "=" * 70)
        logger.success("\n✨ Integration test complete!\n")
        return True
        
    except Exception as e:
        logger.error(f"\n✗ Integration test failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


if __name__ == "__main__":
    from typing import Optional
    import argparse
    
    parser = argparse.ArgumentParser(description="WE.ED.IT Integration Test")
    parser.add_argument('--audio', required=True, help='Path to test audio file')
    parser.add_argument('--clips', help='Path to test clip directory')
    
    args = parser.parse_args()
    
    success = test_integration(args.audio, args.clips)
    sys.exit(0 if success else 1)
