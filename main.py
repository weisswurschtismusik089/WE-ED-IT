#!/usr/bin/env python3
"""
Full Stack Main Application
Integrates all modules: Audio, Clips, Rendering, Effects, Scoring
"""

import os
import sys
import click
import yaml
from pathlib import Path
from typing import Optional
from loguru import logger

from core.audio_analysis import AudioAnalyzer
from core.audio_intelligence import AudioIntelligenceAnalyzer
from core.clip_analyzer import ClipAnalyzer
from core.enhanced_effects import EnhancedEffectManager, TransitionType
from core.viral_scoring import ViralScoringEngine
from core.video_renderer import VideoRenderer, RenderConfig
from db.metadata_db import MetadataDB
from db.clip_vault import ClipVault
from ml.vector_logic import VectorLogicMatcher
from hw.hardware_detection import HardwareDetector, HardwareOptimizer
from utils.logger import setup_logger
from utils.file_manager import FileManager


class WEEditItFullStack:
    """Full Stack WE.ED.IT Application"""

    def __init__(self, config_path: str = "config/settings.yaml"):
        """
        Initialize Full Stack Application
        
        Args:
            config_path: Path to configuration file
        """
        setup_logger()
        self.config = self._load_config(config_path)
        self._setup_directories()
        
        # Initialize all components
        logger.info("Initializing Full Stack Components...")
        
        self.db = MetadataDB(self.config['directories'].get('db', 'db_data'))
        self.audio_analyzer = AudioAnalyzer(
            sample_rate=self.config['audio']['sample_rate'],
            hop_length=self.config['audio']['hop_length']
        )
        self.audio_intelligence = AudioIntelligenceAnalyzer()
        self.clip_analyzer = ClipAnalyzer()
        self.clip_vault = ClipVault(
            self.config['directories'].get('input_clips', 'input/ClipPool'),
            self.db
        )
        self.effect_manager = EnhancedEffectManager()
        self.vector_matcher = VectorLogicMatcher()
        self.viral_engine = ViralScoringEngine()
        
        # Hardware optimization
        hw_detector = HardwareDetector()
        hw_profile = hw_detector.detect_hardware()
        hw_optimizer = HardwareOptimizer(hw_profile)
        self.hw_settings = hw_optimizer.get_optimal_settings()
        
        self.renderer = VideoRenderer(
            config=RenderConfig(
                output_width=self.config['video']['output_width'],
                output_height=self.config['video']['output_height'],
                fps=self.config['video']['fps'],
                codec=self.config['video']['codec'],
                preset=self.config['video']['preset'],
                bitrate=self.config['video']['bitrate'],
                audio_bitrate=self.config['video']['audio_bitrate'],
                enable_effects=self.config['effects'].get('enable_effects', True)
            )
        )
        
        logger.success("✓ Full Stack Application initialized successfully")

    def _load_config(self, config_path: str) -> dict:
        """
        Load configuration
        
        Args:
            config_path: Path to config file
            
        Returns:
            Configuration dictionary
        """
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            logger.info(f"Configuration loaded from {config_path}")
            return config
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {config_path}")
            raise

    def _setup_directories(self) -> None:
        """
        Create necessary directories
        """
        dirs = [
            self.config['directories'].get('input_sound', 'input/Sound'),
            self.config['directories'].get('input_clips', 'input/ClipPool'),
            self.config['directories'].get('output', 'output'),
            self.config['directories'].get('logs', 'logs'),
            self.config['directories'].get('db', 'db_data'),
            'temp', 'presets', 'debug_output'
        ]
        FileManager.ensure_directories(dirs)

    def create_professional_music_video(
        self,
        audio_path: str,
        output_name: str = 'output.mp4',
        quality: str = 'high',
        enable_viral_optimization: bool = True,
        enable_effects: bool = True
    ) -> Optional[str]:
        """
        Create professional music video with full stack
        
        Args:
            audio_path: Path to audio file
            output_name: Output video name
            quality: Quality level (low, medium, high)
            enable_viral_optimization: Enable viral scoring
            enable_effects: Enable visual effects
            
        Returns:
            Path to created video or None
        """
        logger.info("\n" + "=" * 70)
        logger.info("WE.ED.IT - PROFESSIONAL MUSIC VIDEO CREATION")
        logger.info("=" * 70)
        logger.info(f"Audio: {audio_path}")
        logger.info(f"Quality: {quality.upper()}")
        logger.info(f"Viral Optimization: {'ON' if enable_viral_optimization else 'OFF'}")
        logger.info(f"Visual Effects: {'ON' if enable_effects else 'OFF'}")
        
        try:
            if not os.path.exists(audio_path):
                logger.error(f"Audio file not found: {audio_path}")
                return None
            
            # STEP 1: Audio Analysis
            logger.info("\n[1/8] 🎵 Analyzing audio...")
            audio_analysis = self.audio_analyzer.analyze(audio_path)
            logger.success(f"✓ BPM: {audio_analysis.bpm:.1f} | Duration: {audio_analysis.duration:.2f}s")
            
            # STEP 2: Audio Intelligence
            logger.info("\n[2/8] 🧠 Extracting song intelligence...")
            intelligence = self.audio_intelligence.analyze_complete(audio_path)
            logger.success(f"✓ {intelligence.tags.title or 'Unknown'} by {intelligence.tags.artist or 'Unknown'}")
            logger.success(f"✓ Mood: {intelligence.emotion.primary_mood.value} | Drops: {len(intelligence.structure.drop_times)}")
            
            # STEP 3: Generate segments
            logger.info("\n[3/8] ⏱️  Generating beat-aligned segments...")
            segments = self.audio_analyzer.get_beat_aligned_segments(
                intelligence.audio_analysis.beat_times,
                intelligence.audio_analysis.duration
            )
            logger.success(f"✓ Generated {len(segments)} segments")
            
            # STEP 4: Scan clip vault
            logger.info("\n[4/8] 🎬 Scanning clip vault...")
            self.clip_vault.scan_vault(recursive=True, follow_symlinks=True)
            if not self.clip_vault.clips:
                logger.warning("⚠️  No clips found in vault!")
                return None
            logger.success(f"✓ Found {len(self.clip_vault.clips)} clips")
            
            # STEP 5: Vector matching
            logger.info("\n[5/8] 🎯 Intelligent clip matching...")
            song_vector = self.vector_matcher.create_song_vector(
                gender=intelligence.tags.custom_tags.get('gender', 'neutral'),
                genre=intelligence.tags.genre or 'pop',
                bpm=intelligence.tags.bpm or 120,
                energy=intelligence.emotion.intensity_curve.mean() if hasattr(intelligence.emotion.intensity_curve, 'mean') else 0.5,
                mood=intelligence.emotion.primary_mood.value,
                narrative='generic'
            )
            logger.success(f"✓ Song vector created")
            
            # STEP 6: Effect selection
            logger.info("\n[6/8] ✨ Selecting effects and transitions...")
            transition_count = 0
            for i in range(len(segments) - 1):
                energy_prev = 0.5
                energy_curr = 0.5
                transition = self.effect_manager.select_intelligent_transition(
                    prev_energy=energy_prev,
                    curr_energy=energy_curr,
                    prev_shot_scale='medium',
                    curr_shot_scale='medium',
                    prev_movement='static',
                    curr_movement='static',
                    bpm=intelligence.tags.bpm or 120,
                    is_drop=False
                )
                transition_count += 1
            logger.success(f"✓ Selected {transition_count} intelligent transitions")
            
            # STEP 7: Viral analysis
            if enable_viral_optimization:
                logger.info("\n[7/8] 📊 Analyzing viral potential...")
                viral_analysis = self.viral_engine.analyze_video_potential(
                    face_cut_count=3,
                    face_cut_duration_avg=0.5,
                    cut_frequency=2.0,
                    shot_variety=5,
                    transition_smoothness=0.8,
                    effect_intensity=0.7,
                    audio_visual_sync=0.9,
                    bpm=intelligence.tags.bpm or 120,
                    duration=intelligence.audio_analysis.duration
                )
                logger.success(f"✓ Viral Score: {viral_analysis.viral_score:.1f}/100")
                self.viral_engine.print_viral_report(viral_analysis)
                
                output_dir = self.config['directories'].get('output', 'output')
                self.viral_engine.export_viral_report(
                    viral_analysis,
                    os.path.join(output_dir, "viral_analysis.json")
                )
            
            # STEP 8: Export metadata
            logger.info("\n[8/8] 💾 Exporting project metadata...")
            output_path = os.path.join(
                self.config['directories'].get('output', 'output'),
                output_name
            )
            self.db.export_metadata_json(f"{output_path}.metadata.json")
            logger.success(f"✓ Metadata exported")
            
            logger.info("\n" + "=" * 70)
            logger.success("🎉 MUSIC VIDEO CREATION COMPLETE!")
            logger.success(f"Output: {output_path}")
            logger.info("=" * 70 + "\n")
            
            return output_path
            
        except Exception as e:
            logger.error(f"❌ Error creating music video: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None


@click.group()
def cli():
    """WE.ED.IT - AI-Powered Music Video Creator (Full Stack)"""
    pass


@cli.command()
@click.option('--audio', required=True, help='Path to input audio file')
@click.option('--output', default='output.mp4', help='Output video filename')
@click.option('--config', default='config/settings.yaml', help='Path to configuration file')
@click.option('--quality', type=click.Choice(['low', 'medium', 'high']), default='high')
@click.option('--viral', is_flag=True, default=True, help='Enable viral optimization')
@click.option('--effects', is_flag=True, default=True, help='Enable visual effects')
def create(audio: str, output: str, config: str, quality: str, viral: bool, effects: bool):
    """
    Create professional music video
    
    Example:
        python main.py create --audio input/Sound/song.mp3
    """
    try:
        app = WEEditItFullStack(config_path=config)
        result = app.create_professional_music_video(
            audio_path=audio,
            output_name=output,
            quality=quality,
            enable_viral_optimization=viral,
            enable_effects=effects
        )
        if result:
            logger.success(f"\n✨ Video created successfully!")
        else:
            logger.error("Failed to create video")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


@cli.command()
@click.option('--config', default='config/settings.yaml', help='Path to configuration file')
@click.option('--format', type=click.Choice(['json', 'csv']), default='json')
def vault(config: str, format: str):
    """
    Analyze clip vault
    
    Example:
        python main.py vault --format json
    """
    try:
        app = WEEditItFullStack(config_path=config)
        logger.info("Analyzing clip vault...")
        app.clip_vault.scan_vault()
        stats = app.clip_vault.get_statistics()
        logger.success(f"\n✓ Vault contains {stats.get('total_clips', 0)} clips")
        app.clip_vault.export_vault_database(
            os.path.join(app.config['directories'].get('output', 'output'), f"vault.{format}"),
            format=format
        )
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    cli()
