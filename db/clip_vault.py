#!/usr/bin/env python3
"""
Clip Vault
Intelligent clip pool management with recursive loading, symlink support, and NFO parsing.
"""

import os
import json
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from loguru import logger

from core.clip_analyzer import ClipAnalyzer, ClipVisualAnalysis
from db.metadata_db import MetadataDB
from utils.nfo_parser import NFOParser


class ClipVault:
    """Manages video clip pool with intelligence"""

    def __init__(self, vault_dir: str, db: MetadataDB):
        """
        Initialize ClipVault
        
        Args:
            vault_dir: Root directory of clip pool
            db: MetadataDB instance
        """
        self.vault_dir = vault_dir
        self.db = db
        self.analyzer = ClipAnalyzer()
        self.nfo_parser = NFOParser()
        self.clips: Dict[str, Dict] = {}
        logger.info(f"ClipVault initialized at {vault_dir}")

    def scan_vault(self, recursive: bool = True, follow_symlinks: bool = True) -> Dict[str, Dict]:
        """
        Scan vault for video clips and metadata
        
        Args:
            recursive: Scan subdirectories
            follow_symlinks: Follow symbolic links
            
        Returns:
            Dictionary of discovered clips
        """
        logger.info(f"Scanning vault: {self.vault_dir}")
        
        video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.flv', '.webm', '.m4v'}
        self.clips = {}
        
        for root, dirs, files in os.walk(self.vault_dir, followlinks=follow_symlinks):
            for filename in files:
                _, ext = os.path.splitext(filename)
                
                if ext.lower() not in video_extensions:
                    continue
                
                filepath = os.path.join(root, filename)
                
                try:
                    clip_data = self._load_clip(filepath)
                    self.clips[filepath] = clip_data
                    logger.debug(f"Loaded clip: {filename}")
                except Exception as e:
                    logger.warning(f"Error loading clip {filename}: {e}")
            
            # Don't recurse if not requested
            if not recursive:
                break
        
        logger.success(f"Vault scan complete: {len(self.clips)} clips found")
        self.db.export_metadata_json("db_data/vault_snapshot.json")
        return self.clips

    def _load_clip(self, clip_path: str) -> Dict:
        """
        Load clip with metadata and analysis
        
        Args:
            clip_path: Path to video file
            
        Returns:
            Clip data dictionary
        """
        # Check if already analyzed
        cached = self.db.get_clip(clip_path)
        if cached:
            return cached
        
        # Analyze clip
        analysis = self.analyzer.analyze_clip(clip_path)
        
        # Load associated NFO files
        nfo_data = self._load_nfo_files(clip_path)
        
        # Create clip data
        clip_data = {
            'path': clip_path,
            'filename': os.path.basename(clip_path),
            'duration': analysis.duration,
            'fps': analysis.fps,
            'composition': {
                'scale': analysis.composition.scale.value,
                'face_count': analysis.composition.face_count,
                'colors': analysis.composition.dominant_colors
            },
            'camera': {
                'movement_type': analysis.camera.movement_type.value,
                'movement_intensity': float(analysis.camera.movement_intensity)
            },
            'lighting': {
                'brightness': float(analysis.lighting.brightness),
                'contrast': float(analysis.lighting.contrast),
                'color_temperature': float(analysis.lighting.color_temperature),
                'color_grading': analysis.lighting.color_grading
            },
            'emotional_intensity': float(analysis.emotional_intensity),
            'dynamic_score': float(analysis.dynamic_score),
            'overall_quality': float(analysis.overall_quality),
            'tags': analysis.tags,
            'nfo_data': nfo_data
        }
        
        # Store in database
        self.db.add_clip(clip_path, clip_data)
        logger.debug(f"Cached clip: {clip_path}")
        
        return clip_data

    def _load_nfo_files(self, clip_path: str) -> Dict:
        """
        Load associated NFO metadata files
        
        Args:
            clip_path: Path to video file
            
        Returns:
            NFO data dictionary
        """
        base_path = os.path.splitext(clip_path)[0]
        nfo_paths = [f"{base_path}.nfo", f"{base_path}.info"]
        
        for nfo_path in nfo_paths:
            if os.path.exists(nfo_path):
                try:
                    return self.nfo_parser.parse(nfo_path)
                except Exception as e:
                    logger.debug(f"Error parsing NFO {nfo_path}: {e}")
        
        return {}

    def get_clip(self, clip_path: str) -> Optional[Dict]:
        """
        Get clip data
        
        Args:
            clip_path: Path to clip
            
        Returns:
            Clip data or None
        """
        return self.clips.get(clip_path)

    def filter_by_criteria(
        self,
        min_duration: Optional[float] = None,
        max_duration: Optional[float] = None,
        min_quality: Optional[float] = None,
        tags: Optional[List[str]] = None,
        composition: Optional[str] = None
    ) -> List[Tuple[str, Dict]]:
        """
        Filter clips by criteria
        
        Args:
            min_duration: Minimum duration in seconds
            max_duration: Maximum duration in seconds
            min_quality: Minimum quality score (0-1)
            tags: Clips must have all these tags
            composition: Shot composition type
            
        Returns:
            List of (clip_path, clip_data) tuples
        """
        results = []
        
        for clip_path, clip_data in self.clips.items():
            # Duration filter
            if min_duration and clip_data['duration'] < min_duration:
                continue
            if max_duration and clip_data['duration'] > max_duration:
                continue
            
            # Quality filter
            if min_quality and clip_data['overall_quality'] < min_quality:
                continue
            
            # Tags filter
            if tags:
                if not all(tag in clip_data['tags'] for tag in tags):
                    continue
            
            # Composition filter
            if composition:
                if clip_data['composition']['scale'] != composition:
                    continue
            
            results.append((clip_path, clip_data))
        
        return results

    def get_statistics(self) -> Dict:
        """
        Get vault statistics
        
        Returns:
            Statistics dictionary
        """
        if not self.clips:
            return {}
        
        durations = [c['duration'] for c in self.clips.values()]
        qualities = [c['overall_quality'] for c in self.clips.values()]
        dynamics = [c['dynamic_score'] for c in self.clips.values()]
        
        return {
            'total_clips': len(self.clips),
            'total_duration': sum(durations),
            'avg_duration': sum(durations) / len(durations),
            'avg_quality': sum(qualities) / len(qualities),
            'avg_dynamic_score': sum(dynamics) / len(dynamics),
            'unique_tags': set(tag for c in self.clips.values() for tag in c['tags']),
            'composition_distribution': self._get_composition_distribution()
        }

    def _get_composition_distribution(self) -> Dict[str, int]:
        """
        Get distribution of shot compositions
        
        Returns:
            Dictionary with counts
        """
        distribution = {}
        for clip_data in self.clips.values():
            scale = clip_data['composition']['scale']
            distribution[scale] = distribution.get(scale, 0) + 1
        return distribution

    def export_vault_database(self, output_path: str, format: str = 'json') -> None:
        """
        Export vault database
        
        Args:
            output_path: Output file path
            format: 'json' or 'csv'
        """
        if format == 'json':
            self.db.export_metadata_json(output_path, include_analysis=True)
        elif format == 'csv':
            self.db.export_metadata_csv(output_path, item_type='clips')
        else:
            logger.error(f"Unknown format: {format}")
