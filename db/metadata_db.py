#!/usr/bin/env python3
"""
Metadata Database
JSON-based internal database for storing song and clip metadata.
"""

import json
import os
from typing import Dict, List, Optional, Any
from pathlib import Path
from loguru import logger
from datetime import datetime


class MetadataDB:
    """JSON-based metadata database"""

    def __init__(self, db_dir: str = "db_data"):
        """
        Initialize MetadataDB
        
        Args:
            db_dir: Database directory
        """
        self.db_dir = db_dir
        self.songs_db_path = os.path.join(db_dir, "songs.json")
        self.clips_db_path = os.path.join(db_dir, "clips.json")
        self.analysis_db_path = os.path.join(db_dir, "analysis.json")
        self.vectors_db_path = os.path.join(db_dir, "vectors.json")
        
        os.makedirs(db_dir, exist_ok=True)
        self._initialize_dbs()
        logger.info(f"MetadataDB initialized at {db_dir}")

    def _initialize_dbs(self) -> None:
        """
        Initialize database files if they don't exist
        """
        for db_path in [self.songs_db_path, self.clips_db_path, self.analysis_db_path, self.vectors_db_path]:
            if not os.path.exists(db_path):
                with open(db_path, 'w') as f:
                    json.dump({}, f)

    def add_song(self, audio_path: str, metadata: Dict[str, Any]) -> None:
        """
        Add song to database
        
        Args:
            audio_path: Path to audio file
            metadata: Song metadata dictionary
        """
        songs = self._load_db(self.songs_db_path)
        songs[audio_path] = {
            **metadata,
            'added_at': datetime.now().isoformat()
        }
        self._save_db(self.songs_db_path, songs)
        logger.debug(f"Song added: {audio_path}")

    def get_song(self, audio_path: str) -> Optional[Dict[str, Any]]:
        """
        Get song metadata
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Song metadata or None
        """
        songs = self._load_db(self.songs_db_path)
        return songs.get(audio_path)

    def add_clip(self, clip_path: str, metadata: Dict[str, Any]) -> None:
        """
        Add clip to database
        
        Args:
            clip_path: Path to video file
            metadata: Clip metadata dictionary
        """
        clips = self._load_db(self.clips_db_path)
        clips[clip_path] = {
            **metadata,
            'added_at': datetime.now().isoformat()
        }
        self._save_db(self.clips_db_path, clips)
        logger.debug(f"Clip added: {clip_path}")

    def get_clip(self, clip_path: str) -> Optional[Dict[str, Any]]:
        """
        Get clip metadata
        
        Args:
            clip_path: Path to video file
            
        Returns:
            Clip metadata or None
        """
        clips = self._load_db(self.clips_db_path)
        return clips.get(clip_path)

    def get_all_clips(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all clips from database
        
        Returns:
            Dictionary of all clips
        """
        return self._load_db(self.clips_db_path)

    def add_analysis(self, item_path: str, analysis_type: str, analysis_data: Dict[str, Any]) -> None:
        """
        Store analysis results
        
        Args:
            item_path: Path to analyzed item (song or clip)
            analysis_type: Type of analysis (audio_intelligence, clip_analysis)
            analysis_data: Analysis results
        """
        analysis = self._load_db(self.analysis_db_path)
        if item_path not in analysis:
            analysis[item_path] = {}
        
        analysis[item_path][analysis_type] = {
            **analysis_data,
            'analyzed_at': datetime.now().isoformat()
        }
        self._save_db(self.analysis_db_path, analysis)
        logger.debug(f"Analysis stored: {item_path} ({analysis_type})")

    def get_analysis(self, item_path: str, analysis_type: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get analysis results
        
        Args:
            item_path: Path to analyzed item
            analysis_type: Specific analysis type or None for all
            
        Returns:
            Analysis results or None
        """
        analysis = self._load_db(self.analysis_db_path)
        if item_path not in analysis:
            return None
        
        if analysis_type:
            return analysis[item_path].get(analysis_type)
        return analysis[item_path]

    def add_vector(self, item_path: str, vector_type: str, vector_data: List[float]) -> None:
        """
        Store vector embeddings
        
        Args:
            item_path: Path to item
            vector_type: Type of vector (audio_embedding, visual_embedding, etc.)
            vector_data: Vector data
        """
        vectors = self._load_db(self.vectors_db_path)
        if item_path not in vectors:
            vectors[item_path] = {}
        
        vectors[item_path][vector_type] = {
            'data': vector_data,
            'stored_at': datetime.now().isoformat()
        }
        self._save_db(self.vectors_db_path, vectors)
        logger.debug(f"Vector stored: {item_path} ({vector_type})")

    def get_vector(self, item_path: str, vector_type: str) -> Optional[List[float]]:
        """
        Get vector embeddings
        
        Args:
            item_path: Path to item
            vector_type: Type of vector
            
        Returns:
            Vector data or None
        """
        vectors = self._load_db(self.vectors_db_path)
        if item_path in vectors and vector_type in vectors[item_path]:
            return vectors[item_path][vector_type]['data']
        return None

    def _load_db(self, db_path: str) -> Dict[str, Any]:
        """
        Load database from file
        
        Args:
            db_path: Path to database file
            
        Returns:
            Database dictionary
        """
        try:
            with open(db_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading database {db_path}: {e}")
            return {}

    def _save_db(self, db_path: str, data: Dict[str, Any]) -> None:
        """
        Save database to file
        
        Args:
            db_path: Path to database file
            data: Database dictionary
        """
        try:
            with open(db_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving database {db_path}: {e}")

    def export_metadata_json(self, output_path: str, include_analysis: bool = True) -> None:
        """
        Export complete metadata as JSON
        
        Args:
            output_path: Output JSON file path
            include_analysis: Include analysis data
        """
        export_data = {
            'songs': self._load_db(self.songs_db_path),
            'clips': self._load_db(self.clips_db_path),
        }
        
        if include_analysis:
            export_data['analysis'] = self._load_db(self.analysis_db_path)
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        logger.success(f"Metadata exported to {output_path}")

    def export_metadata_csv(self, output_path: str, item_type: str = 'clips') -> None:
        """
        Export metadata as CSV
        
        Args:
            output_path: Output CSV file path
            item_type: 'songs' or 'clips'
        """
        import csv
        
        if item_type == 'songs':
            data = self._load_db(self.songs_db_path)
        else:
            data = self._load_db(self.clips_db_path)
        
        if not data:
            logger.warning(f"No {item_type} data to export")
            return
        
        # Get all unique keys
        all_keys = set()
        for item in data.values():
            all_keys.update(item.keys())
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['path'] + sorted(list(all_keys)))
            writer.writeheader()
            for path, metadata in data.items():
                writer.writerow({'path': path, **metadata})
        
        logger.success(f"Metadata exported to CSV: {output_path}")
