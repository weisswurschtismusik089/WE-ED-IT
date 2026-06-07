#!/usr/bin/env python3
"""
Vector Logic System
Gender, Style, Energy, Story vectors for intelligent clip-song matching.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
from loguru import logger
from sklearn.preprocessing import normalize
from sklearn.metrics.pairwise import cosine_similarity


class GenderVector(Enum):
    """Gender classification for artist/content"""
    MALE = np.array([1.0, 0.0, 0.0])
    FEMALE = np.array([0.0, 1.0, 0.0])
    NEUTRAL = np.array([0.0, 0.0, 1.0])
    MIXED = np.array([0.5, 0.5, 0.0])


class StyleVector(Enum):
    """Visual/Audio style classification"""
    HIP_HOP = "hip_hop"
    POP = "pop"
    ROCK = "rock"
    ELECTRONIC = "electronic"
    R_AND_B = "r_and_b"
    INDIE = "indie"
    METAL = "metal"
    JAZZ = "jazz"
    CLASSICAL = "classical"
    EXPERIMENTAL = "experimental"


@dataclass
class VectorProfile:
    """Complete vector profile for matching"""
    gender: np.ndarray
    style: np.ndarray
    energy: np.ndarray
    emotion: np.ndarray
    narrative: np.ndarray
    visual_intensity: np.ndarray


class VectorLogicMatcher:
    """Performs intelligent matching using vector logic"""

    def __init__(self):
        """
        Initialize VectorLogicMatcher
        """
        self.gender_vectors = {
            'male': np.array([1.0, 0.0, 0.0]),
            'female': np.array([0.0, 1.0, 0.0]),
            'neutral': np.array([0.0, 0.0, 1.0]),
            'mixed': np.array([0.5, 0.5, 0.0])
        }
        
        self.style_vectors = self._create_style_vectors()
        logger.info("VectorLogicMatcher initialized")

    def _create_style_vectors(self) -> Dict[str, np.ndarray]:
        """
        Create semantic vectors for styles
        
        Returns:
            Dictionary of style vectors
        """
        return {
            'hip_hop': np.array([1.0, 0.0, 0.8, 0.9, 0.7]),  # aggressive, rhythmic, energetic, dynamic
            'pop': np.array([0.6, 0.8, 0.7, 0.8, 0.6]),
            'rock': np.array([0.9, 0.2, 0.9, 0.8, 0.8]),
            'electronic': np.array([0.3, 1.0, 0.7, 0.6, 0.8]),
            'r_and_b': np.array([0.4, 0.9, 0.5, 0.7, 0.5]),
            'indie': np.array([0.7, 0.6, 0.6, 0.7, 0.7]),
            'metal': np.array([1.0, 0.1, 1.0, 0.9, 0.9]),
            'jazz': np.array([0.5, 0.7, 0.6, 0.8, 0.4]),
            'classical': np.array([0.3, 0.9, 0.3, 0.6, 0.2]),
            'experimental': np.array([0.8, 0.8, 0.7, 0.7, 0.9])
        }

    def create_song_vector(
        self,
        gender: str,
        genre: str,
        bpm: float,
        energy: float,
        mood: str,
        narrative: Optional[str] = None
    ) -> VectorProfile:
        """
        Create vector profile for a song
        
        Args:
            gender: 'male', 'female', 'neutral', 'mixed'
            genre: Musical genre
            bpm: Beats per minute
            energy: Energy level (0-1)
            mood: Emotional mood
            narrative: Story/narrative type
            
        Returns:
            VectorProfile object
        """
        # Gender vector
        gender_vec = self.gender_vectors.get(gender.lower(), self.gender_vectors['neutral'])
        
        # Style vector
        style_vec = self.style_vectors.get(genre.lower(), np.ones(5) * 0.5)
        
        # Energy vector (BPM-based and direct energy)
        bpm_normalized = min(bpm / 200, 1.0)  # Normalize BPM
        energy_vec = np.array([bpm_normalized, energy, energy, bpm_normalized, energy])
        
        # Emotion vector based on mood
        emotion_vec = self._create_emotion_vector(mood)
        
        # Narrative vector
        narrative_vec = self._create_narrative_vector(narrative or "generic")
        
        # Visual intensity (based on energy and BPM)
        visual_vec = np.array([energy, bpm_normalized, energy]) * 0.8
        
        return VectorProfile(
            gender=normalize(gender_vec.reshape(1, -1))[0],
            style=normalize(style_vec.reshape(1, -1))[0],
            energy=normalize(energy_vec.reshape(1, -1))[0],
            emotion=normalize(emotion_vec.reshape(1, -1))[0],
            narrative=normalize(narrative_vec.reshape(1, -1))[0],
            visual_intensity=visual_vec
        )

    def create_clip_vector(
        self,
        gender: str,
        shot_scale: str,
        camera_movement: str,
        lighting: str,
        emotional_intensity: float,
        dynamic_score: float
    ) -> VectorProfile:
        """
        Create vector profile for a clip
        
        Args:
            gender: Gender in clip
            shot_scale: 'wide', 'medium', 'close_up', 'extreme_close_up'
            camera_movement: 'static', 'pan', 'tracking', 'handheld'
            lighting: Color grading
            emotional_intensity: Emotion intensity (0-1)
            dynamic_score: Movement/dynamic score (0-1)
            
        Returns:
            VectorProfile object
        """
        # Gender vector
        gender_vec = self.gender_vectors.get(gender.lower(), self.gender_vectors['neutral'])
        
        # Visual style vector (based on technical aspects)
        shot_intensity = self._shot_scale_to_intensity(shot_scale)
        movement_intensity = self._camera_movement_to_intensity(camera_movement)
        style_vec = np.array([shot_intensity, movement_intensity, dynamic_score, emotional_intensity, dynamic_score])
        
        # Energy vector (from dynamic score)
        energy_vec = np.array([dynamic_score] * 5)
        
        # Emotion vector
        emotion_vec = np.array([emotional_intensity, emotional_intensity, emotional_intensity, 
                               dynamic_score, emotional_intensity])
        
        # Narrative vector (visual storytelling)
        narrative_vec = np.array([shot_intensity, emotional_intensity, movement_intensity, 
                                dynamic_score, shot_intensity])
        
        # Visual intensity
        visual_vec = np.array([emotional_intensity, dynamic_score, shot_intensity])
        
        return VectorProfile(
            gender=normalize(gender_vec.reshape(1, -1))[0],
            style=normalize(style_vec.reshape(1, -1))[0],
            energy=normalize(energy_vec.reshape(1, -1))[0],
            emotion=normalize(emotion_vec.reshape(1, -1))[0],
            narrative=normalize(narrative_vec.reshape(1, -1))[0],
            visual_intensity=visual_vec
        )

    def match_song_to_clips(
        self,
        song_vector: VectorProfile,
        clip_vectors: List[Tuple[str, VectorProfile]],
        weights: Optional[Dict[str, float]] = None
    ) -> List[Tuple[str, float]]:
        """
        Match song vector to clip vectors and rank clips
        
        Args:
            song_vector: Song VectorProfile
            clip_vectors: List of (clip_id, VectorProfile) tuples
            weights: Vector component weights
            
        Returns:
            List of (clip_id, similarity_score) tuples sorted by score
        """
        if weights is None:
            weights = {
                'gender': 0.2,
                'style': 0.2,
                'energy': 0.2,
                'emotion': 0.2,
                'narrative': 0.1,
                'visual': 0.1
            }
        
        scores = []
        for clip_id, clip_vector in clip_vectors:
            score = self._calculate_match_score(song_vector, clip_vector, weights)
            scores.append((clip_id, score))
        
        # Sort by score (descending)
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores

    def _calculate_match_score(
        self,
        song_vec: VectorProfile,
        clip_vec: VectorProfile,
        weights: Dict[str, float]
    ) -> float:
        """
        Calculate similarity score between song and clip
        
        Args:
            song_vec: Song vector
            clip_vec: Clip vector
            weights: Component weights
            
        Returns:
            Similarity score (0-1)
        """
        # Calculate cosine similarities
        gender_sim = cosine_similarity(
            song_vec.gender.reshape(1, -1),
            clip_vec.gender.reshape(1, -1)
        )[0, 0]
        
        style_sim = cosine_similarity(
            song_vec.style.reshape(1, -1),
            clip_vec.style.reshape(1, -1)
        )[0, 0]
        
        energy_sim = cosine_similarity(
            song_vec.energy.reshape(1, -1),
            clip_vec.energy.reshape(1, -1)
        )[0, 0]
        
        emotion_sim = cosine_similarity(
            song_vec.emotion.reshape(1, -1),
            clip_vec.emotion.reshape(1, -1)
        )[0, 0]
        
        narrative_sim = cosine_similarity(
            song_vec.narrative.reshape(1, -1),
            clip_vec.narrative.reshape(1, -1)
        )[0, 0]
        
        visual_sim = np.dot(
            song_vec.visual_intensity / np.linalg.norm(song_vec.visual_intensity),
            clip_vec.visual_intensity / np.linalg.norm(clip_vec.visual_intensity)
        )
        
        # Weighted combination
        total_score = (
            gender_sim * weights['gender'] +
            style_sim * weights['style'] +
            energy_sim * weights['energy'] +
            emotion_sim * weights['emotion'] +
            narrative_sim * weights['narrative'] +
            visual_sim * weights['visual']
        )
        
        return total_score

    def _create_emotion_vector(self, mood: str) -> np.ndarray:
        """
        Create emotion vector from mood
        
        Args:
            mood: Emotional mood
            
        Returns:
            Emotion vector
        """
        mood_vectors = {
            'happy': np.array([1.0, 0.8, 0.7, 0.9, 0.6]),
            'sad': np.array([0.2, 0.3, 0.1, 0.4, 0.2]),
            'angry': np.array([0.9, 0.2, 0.9, 0.8, 0.9]),
            'calm': np.array([0.3, 0.8, 0.2, 0.2, 0.3]),
            'energetic': np.array([0.9, 0.9, 0.8, 0.9, 0.9]),
            'melancholic': np.array([0.4, 0.5, 0.3, 0.5, 0.4]),
            'playful': np.array([0.8, 0.9, 0.7, 0.8, 0.7]),
            'intense': np.array([0.9, 0.7, 0.9, 0.9, 0.8])
        }
        return mood_vectors.get(mood.lower(), np.ones(5) * 0.5)

    def _create_narrative_vector(self, narrative: str) -> np.ndarray:
        """
        Create narrative vector from story type
        
        Args:
            narrative: Narrative type
            
        Returns:
            Narrative vector
        """
        narrative_vectors = {
            'love': np.array([0.8, 0.7, 0.3, 0.7, 0.8]),
            'party': np.array([0.9, 0.9, 0.9, 0.8, 0.9]),
            'action': np.array([0.9, 0.8, 0.9, 0.8, 0.9]),
            'drama': np.array([0.6, 0.7, 0.4, 0.8, 0.6]),
            'comedy': np.array([0.7, 0.8, 0.6, 0.7, 0.7]),
            'introspective': np.array([0.4, 0.5, 0.2, 0.6, 0.4]),
            'inspirational': np.array([0.8, 0.8, 0.7, 0.9, 0.8]),
            'generic': np.array([0.5, 0.5, 0.5, 0.5, 0.5])
        }
        return narrative_vectors.get(narrative.lower(), np.ones(5) * 0.5)

    def _shot_scale_to_intensity(self, shot_scale: str) -> float:
        """
        Convert shot scale to intensity value
        
        Args:
            shot_scale: Shot scale type
            
        Returns:
            Intensity (0-1)
        """
        scale_intensity = {
            'wide': 0.3,
            'medium': 0.5,
            'close_up': 0.8,
            'extreme_close_up': 1.0,
            'two_shot': 0.6,
            'group_shot': 0.4
        }
        return scale_intensity.get(shot_scale.lower(), 0.5)

    def _camera_movement_to_intensity(self, movement: str) -> float:
        """
        Convert camera movement to intensity value
        
        Args:
            movement: Camera movement type
            
        Returns:
            Intensity (0-1)
        """
        movement_intensity = {
            'static': 0.0,
            'pan': 0.3,
            'tilt': 0.3,
            'zoom': 0.6,
            'tracking': 0.7,
            'dolly': 0.8,
            'handheld': 0.9
        }
        return movement_intensity.get(movement.lower(), 0.5)
