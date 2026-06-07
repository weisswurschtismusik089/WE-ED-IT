#!/usr/bin/env python3
"""
Clip Analyzer
KI-based visual analysis of video clips: shot composition, camera movement, lighting, emotion.
"""

import cv2
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum
from loguru import logger
import json
import os


class ShotScale(Enum):
    """Shot scale classification"""
    WIDE = "wide"
    MEDIUM = "medium"
    CLOSE_UP = "close_up"
    EXTREME_CLOSE_UP = "extreme_close_up"
    TWO_SHOT = "two_shot"
    GROUP_SHOT = "group_shot"


class CameraMovement(Enum):
    """Camera movement type"""
    STATIC = "static"
    PAN = "pan"
    TILT = "tilt"
    ZOOM = "zoom"
    TRACKING = "tracking"
    DOLLY = "dolly"
    HANDHELD = "handheld"


class LightingType(Enum):
    """Lighting classification"""
    KEY_LIGHT = "key_light"
    FILL_LIGHT = "fill_light"
    BACK_LIGHT = "back_light"
    GEL_LIGHT = "gel_light"
    NATURAL = "natural"
    ARTIFICIAL = "artificial"
    DARK = "dark"


@dataclass
class ShotComposition:
    """Shot composition analysis"""
    scale: ShotScale
    aspect_ratio: float
    rule_of_thirds: bool
    center_focus: bool
    face_detection: bool
    face_count: int
    dominant_colors: List[Tuple[int, int, int]] = field(default_factory=list)


@dataclass
class CameraAnalysis:
    """Camera movement analysis"""
    movement_type: CameraMovement
    movement_intensity: float  # 0-1
    optical_flow: Optional[np.ndarray] = None
    dominant_direction: str = "static"  # left, right, up, down, zoom_in, zoom_out


@dataclass
class LightingAnalysis:
    """Lighting analysis"""
    primary_type: LightingType
    brightness: float  # 0-1
    contrast: float  # 0-1
    color_temperature: float  # 3000K-6500K
    color_grading: str  # cool, warm, neutral, cinematic, vintage
    dominant_hue: float  # 0-360


@dataclass
class ClipVisualAnalysis:
    """Complete visual analysis of a clip"""
    clip_path: str
    duration: float
    frame_count: int
    fps: float
    composition: ShotComposition
    camera: CameraAnalysis
    lighting: LightingAnalysis
    emotional_intensity: float  # 0-1
    dynamic_score: float  # 0-1 (How dynamic/movement-heavy)
    overall_quality: float  # 0-1
    tags: List[str] = field(default_factory=list)


class ClipAnalyzer:
    """Analyzes video clips with AI-powered visual analysis"""

    def __init__(self, sample_frames: int = 10):
        """
        Initialize ClipAnalyzer
        
        Args:
            sample_frames: Number of frames to sample for analysis
        """
        self.sample_frames = sample_frames
        logger.info(f"ClipAnalyzer initialized (sample_frames={sample_frames})")

    def analyze_clip(self, clip_path: str) -> ClipVisualAnalysis:
        """
        Perform complete visual analysis of a clip
        
        Args:
            clip_path: Path to video file
            
        Returns:
            ClipVisualAnalysis object
        """
        logger.info(f"Analyzing clip: {clip_path}")
        
        try:
            # Open video
            cap = cv2.VideoCapture(clip_path)
            if not cap.isOpened():
                raise ValueError(f"Cannot open video: {clip_path}")
            
            # Get metadata
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = frame_count / fps if fps > 0 else 0
            
            # Sample frames
            frame_indices = np.linspace(0, frame_count - 1, self.sample_frames, dtype=int)
            frames = self._load_frames(cap, frame_indices)
            
            # Analyze composition
            composition = self._analyze_composition(frames)
            
            # Analyze camera movement
            camera = self._analyze_camera_movement(frames)
            
            # Analyze lighting
            lighting = self._analyze_lighting(frames)
            
            # Calculate overall metrics
            emotional_intensity = self._calculate_emotional_intensity(frames)
            dynamic_score = self._calculate_dynamic_score(frames, camera)
            overall_quality = self._calculate_quality(frames, composition, lighting)
            
            # Generate tags
            tags = self._generate_tags(composition, camera, lighting)
            
            analysis = ClipVisualAnalysis(
                clip_path=clip_path,
                duration=duration,
                frame_count=frame_count,
                fps=fps,
                composition=composition,
                camera=camera,
                lighting=lighting,
                emotional_intensity=emotional_intensity,
                dynamic_score=dynamic_score,
                overall_quality=overall_quality,
                tags=tags
            )
            
            logger.success(f"Clip analysis complete: {os.path.basename(clip_path)}")
            cap.release()
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing clip: {e}")
            raise

    def _load_frames(self, cap: cv2.VideoCapture, frame_indices: List[int]) -> List[np.ndarray]:
        """
        Load specific frames from video
        
        Args:
            cap: OpenCV VideoCapture object
            frame_indices: Indices of frames to load
            
        Returns:
            List of frames
        """
        frames = []
        for idx in frame_indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ret, frame = cap.read()
            if ret:
                frames.append(frame)
        return frames

    def _analyze_composition(self, frames: List[np.ndarray]) -> ShotComposition:
        """
        Analyze shot composition
        
        Args:
            frames: List of video frames
            
        Returns:
            ShotComposition object
        """
        if not frames:
            return ShotComposition(
                scale=ShotScale.MEDIUM,
                aspect_ratio=16/9,
                rule_of_thirds=False,
                center_focus=True,
                face_detection=False,
                face_count=0
            )
        
        # Analyze frame dimensions
        h, w = frames[0].shape[:2]
        aspect_ratio = w / h
        
        # Detect faces
        face_detector = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        total_faces = 0
        for frame in frames:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_detector.detectMultiScale(gray, 1.3, 5)
            total_faces += len(faces)
        
        avg_faces = total_faces / len(frames) if frames else 0
        
        # Determine shot scale
        if avg_faces > 2:
            shot_scale = ShotScale.GROUP_SHOT
        elif avg_faces > 1:
            shot_scale = ShotScale.TWO_SHOT
        elif avg_faces > 0.5:
            shot_scale = ShotScale.CLOSE_UP
        else:
            shot_scale = ShotScale.WIDE
        
        # Dominant colors
        dominant_colors = self._extract_dominant_colors(frames[len(frames)//2])
        
        return ShotComposition(
            scale=shot_scale,
            aspect_ratio=aspect_ratio,
            rule_of_thirds=True,  # Assume generally composed
            center_focus=avg_faces > 0,
            face_detection=avg_faces > 0,
            face_count=int(avg_faces),
            dominant_colors=dominant_colors
        )

    def _analyze_camera_movement(self, frames: List[np.ndarray]) -> CameraAnalysis:
        """
        Analyze camera movement
        
        Args:
            frames: List of video frames
            
        Returns:
            CameraAnalysis object
        """
        if len(frames) < 2:
            return CameraAnalysis(
                movement_type=CameraMovement.STATIC,
                movement_intensity=0.0
            )
        
        # Calculate optical flow
        gray1 = cv2.cvtColor(frames[0], cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(frames[-1], cv2.COLOR_BGR2GRAY)
        
        flow = cv2.calcOpticalFlowFarneback(gray1, gray2, None, 0.5, 3, 15, 3, 5, 1.2, 0)
        
        # Calculate movement magnitude
        mag, ang = cv2.cartToPolar(flow[..., 0], flow[..., 1])
        movement_intensity = np.mean(mag) / 255.0  # Normalize
        
        # Determine movement type
        if movement_intensity < 0.05:
            movement_type = CameraMovement.STATIC
        elif movement_intensity < 0.15:
            movement_type = CameraMovement.PAN
        elif movement_intensity < 0.3:
            movement_type = CameraMovement.TRACKING
        else:
            movement_type = CameraMovement.HANDHELD
        
        return CameraAnalysis(
            movement_type=movement_type,
            movement_intensity=min(movement_intensity, 1.0),
            optical_flow=flow,
            dominant_direction="mixed"
        )

    def _analyze_lighting(self, frames: List[np.ndarray]) -> LightingAnalysis:
        """
        Analyze lighting conditions
        
        Args:
            frames: List of video frames
            
        Returns:
            LightingAnalysis object
        """
        if not frames:
            return LightingAnalysis(
                primary_type=LightingType.NATURAL,
                brightness=0.5,
                contrast=0.5,
                color_temperature=5500,
                color_grading="neutral",
                dominant_hue=0
            )
        
        # Analyze middle frame
        frame = frames[len(frames)//2]
        
        # Convert to LAB and HSV
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Calculate brightness and contrast
        brightness = np.mean(lab[:, :, 0]) / 255.0
        contrast = np.std(lab[:, :, 0]) / 127.0
        
        # Dominant hue
        hue_hist = cv2.calcHist([hsv], [0], None, [180], [0, 180])
        dominant_hue = np.argmax(hue_hist) * 2
        
        # Color temperature (estimate from color channels)
        b, g, r = cv2.split(frame)
        color_temp = 3000 + (np.mean(r) - np.mean(b)) * 10
        color_temp = np.clip(color_temp, 3000, 6500)
        
        # Determine color grading
        if color_temp < 4000:
            color_grading = "warm"
        elif color_temp > 6000:
            color_grading = "cool"
        else:
            color_grading = "neutral"
        
        return LightingAnalysis(
            primary_type=LightingType.NATURAL if brightness > 0.3 else LightingType.DARK,
            brightness=brightness,
            contrast=min(contrast, 1.0),
            color_temperature=color_temp,
            color_grading=color_grading,
            dominant_hue=dominant_hue
        )

    def _extract_dominant_colors(self, frame: np.ndarray, k: int = 3) -> List[Tuple[int, int, int]]:
        """
        Extract dominant colors from frame
        
        Args:
            frame: Video frame
            k: Number of colors to extract
            
        Returns:
            List of RGB tuples
        """
        # Reshape frame
        data = frame.reshape((-1, 3))
        data = np.float32(data)
        
        # K-means clustering
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        _, _, centers = cv2.kmeans(data, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        
        # Convert to RGB
        colors = [(int(c[2]), int(c[1]), int(c[0])) for c in centers]
        return colors

    def _calculate_emotional_intensity(self, frames: List[np.ndarray]) -> float:
        """
        Calculate emotional intensity based on visual characteristics
        
        Args:
            frames: List of video frames
            
        Returns:
            Emotional intensity (0-1)
        """
        if not frames:
            return 0.5
        
        # Use color saturation as proxy for emotion
        total_saturation = 0
        for frame in frames:
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            saturation = np.mean(hsv[:, :, 1]) / 255.0
            total_saturation += saturation
        
        return total_saturation / len(frames) if frames else 0.5

    def _calculate_dynamic_score(self, frames: List[np.ndarray], camera: CameraAnalysis) -> float:
        """
        Calculate how dynamic/movement-heavy the clip is
        
        Args:
            frames: List of video frames
            camera: CameraAnalysis object
            
        Returns:
            Dynamic score (0-1)
        """
        return camera.movement_intensity

    def _calculate_quality(self, frames: List[np.ndarray], composition: ShotComposition, lighting: LightingAnalysis) -> float:
        """
        Calculate overall clip quality
        
        Args:
            frames: List of video frames
            composition: ShotComposition object
            lighting: LightingAnalysis object
            
        Returns:
            Quality score (0-1)
        """
        # Combine various factors
        lighting_quality = min(lighting.contrast, 1.0) * 0.3
        composition_quality = (0.5 if composition.rule_of_thirds else 0.3) * 0.4
        brightness_quality = (1.0 if 0.3 < lighting.brightness < 0.9 else 0.5) * 0.3
        
        return lighting_quality + composition_quality + brightness_quality

    def _generate_tags(self, composition: ShotComposition, camera: CameraAnalysis, lighting: LightingAnalysis) -> List[str]:
        """
        Generate descriptive tags
        
        Args:
            composition: ShotComposition object
            camera: CameraAnalysis object
            lighting: LightingAnalysis object
            
        Returns:
            List of tags
        """
        tags = []
        
        # Composition tags
        tags.append(composition.scale.value)
        if composition.face_detection:
            tags.append(f"{composition.face_count}_faces")
        
        # Camera tags
        tags.append(camera.movement_type.value)
        
        # Lighting tags
        tags.append(lighting.color_grading)
        tags.append(f"brightness_{int(lighting.brightness * 100)}")
        
        return tags

    def export_analysis_json(self, analysis: ClipVisualAnalysis, output_path: str) -> None:
        """
        Export clip analysis as JSON
        
        Args:
            analysis: ClipVisualAnalysis object
            output_path: Output JSON file path
        """
        export_data = {
            'clip_path': analysis.clip_path,
            'duration': float(analysis.duration),
            'fps': float(analysis.fps),
            'composition': {
                'scale': analysis.composition.scale.value,
                'face_count': analysis.composition.face_count,
                'dominant_colors': analysis.composition.dominant_colors
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
            'tags': analysis.tags
        }
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        logger.success(f"Clip analysis exported to {output_path}")
