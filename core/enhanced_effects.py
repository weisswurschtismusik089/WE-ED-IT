#!/usr/bin/env python3
"""
Enhanced Effects & Transitions Module
Professional transitions, visual effects, and creative enhancements.
"""

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
from loguru import logger
import numpy as np
import json
import os


class TransitionType(Enum):
    """Advanced transition types"""
    FADE = "fade"
    CROSSFADE = "crossfade"
    SLIDE_LEFT = "slide_left"
    SLIDE_RIGHT = "slide_right"
    SLIDE_UP = "slide_up"
    SLIDE_DOWN = "slide_down"
    ZOOM_IN = "zoom_in"
    ZOOM_OUT = "zoom_out"
    WIPE = "wipe"
    BLEND = "blend"
    DISSOLVE = "dissolve"
    MOSAIC = "mosaic"
    PIXELATE = "pixelate"
    COLOR_FLASH = "color_flash"
    MOTION_BLUR = "motion_blur"
    CIRCULAR_IRIS = "circular_iris"
    SQUEEZE = "squeeze"
    WOBBLE_SYNC = "wobble_sync"


class BlendMode(Enum):
    """Blend modes for effects"""
    OVERLAY = "overlay"
    SCREEN = "screen"
    MULTIPLY = "multiply"
    LIGHTEN = "lighten"
    DARKEN = "darken"
    ADD = "add"
    SUBTRACT = "subtract"
    XOR = "xor"


@dataclass
class AdvancedTransition:
    """Advanced transition with multiple parameters"""
    type: TransitionType
    duration: float
    intensity: float = 1.0
    easing: str = "ease_in_out"  # linear, ease_in, ease_out, ease_in_out, bounce
    direction: str = "forward"  # forward, backward, bidirectional
    blend_mode: BlendMode = BlendMode.OVERLAY
    color: Optional[Tuple[int, int, int]] = None  # RGB
    audio_responsive: bool = False
    beat_sync: bool = False


@dataclass
class VisualEffect:
    """Visual effect with parameters"""
    name: str
    intensity: float = 1.0
    parameters: Dict[str, float] = None
    enabled: bool = True
    blend_mode: BlendMode = BlendMode.OVERLAY


class EnhancedEffectManager:
    """Advanced effects and transitions management"""

    def __init__(self):
        """
        Initialize EnhancedEffectManager
        """
        self.transitions: List[AdvancedTransition] = []
        self.effects: List[VisualEffect] = []
        self.config = self._load_effect_config()
        logger.info("EnhancedEffectManager initialized")

    def _load_effect_config(self) -> Dict:
        """
        Load effect configuration
        
        Returns:
            Effect configuration dictionary
        """
        try:
            with open('config/effects_config.json', 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load effects config: {e}")
            return {}

    def create_transition(
        self,
        transition_type: TransitionType,
        duration: float,
        intensity: float = 1.0,
        easing: str = "ease_in_out",
        audio_responsive: bool = False,
        beat_sync: bool = False
    ) -> AdvancedTransition:
        """
        Create advanced transition
        
        Args:
            transition_type: Type of transition
            duration: Duration in seconds
            intensity: Effect intensity (0-1)
            easing: Easing function
            audio_responsive: Respond to audio energy
            beat_sync: Sync to music beats
            
        Returns:
            AdvancedTransition object
        """
        return AdvancedTransition(
            type=transition_type,
            duration=duration,
            intensity=min(intensity, 1.0),
            easing=easing,
            audio_responsive=audio_responsive,
            beat_sync=beat_sync
        )

    def generate_ffmpeg_transition_filter(self, transition: AdvancedTransition) -> str:
        """
        Generate FFmpeg filter for transition
        
        Args:
            transition: AdvancedTransition object
            
        Returns:
            FFmpeg filter string
        """
        duration = transition.duration
        intensity = int(transition.intensity * 100)
        
        filters = {
            TransitionType.FADE: f"fade=t=in:st=0:d={duration},fade=t=out:st={max(0.1, duration-0.5)}:d={min(0.5, duration)}",
            TransitionType.CROSSFADE: f"xfade=transition=fade:duration={duration}",
            TransitionType.SLIDE_LEFT: f"xfade=transition=slideleft:duration={duration}",
            TransitionType.SLIDE_RIGHT: f"xfade=transition=slideright:duration={duration}",
            TransitionType.SLIDE_UP: f"xfade=transition=slideup:duration={duration}",
            TransitionType.SLIDE_DOWN: f"xfade=transition=slidedown:duration={duration}",
            TransitionType.ZOOM_IN: f"scale=w=iw*{1+intensity/100}:h=ih*{1+intensity/100},pad=w=iw:h=ih:(iw-w)/2:(ih-h)/2",
            TransitionType.ZOOM_OUT: f"scale=w=iw*{max(0.5, 1-intensity/100)}:h=ih*{max(0.5, 1-intensity/100)},pad=w=iw:h=ih:(iw-w)/2:(ih-h)/2",
            TransitionType.WIPE: f"xfade=transition=wipeleft:duration={duration}",
            TransitionType.BLEND: f"overlay=x=0:y=0:alpha={intensity/100}",
            TransitionType.DISSOLVE: f"xfade=transition=smoothleft:duration={duration}",
            TransitionType.MOSAIC: f"boxblur=luma_radius={int(5*intensity/100)}:luma_power=1",
            TransitionType.PIXELATE: f"pixelate=block_size={max(1, int(10*intensity/100))}",
            TransitionType.COLOR_FLASH: f"format=yuv420p,colorlevels=r_in=0:g_in=0:b_in=0",
            TransitionType.MOTION_BLUR: f"split[a][b];[a]trim=duration={duration/2}[a];[b]trim=start={duration/2},motion=200:200[b];[a][b]concat",
            TransitionType.CIRCULAR_IRIS: f"xfade=transition=circlecrop:duration={duration}",
            TransitionType.SQUEEZE: f"scale=w=iw*{1-intensity/200}:h=ih:force_original_aspect_ratio=decrease,pad=w=iw:h=ih:(iw-w)/2:(ih-h)/2",
            TransitionType.WOBBLE_SYNC: self._create_wobble_filter(duration, intensity)
        }
        
        return filters.get(transition.type, "fade=t=in:st=0:d=0.5")

    def _create_wobble_filter(self, duration: float, intensity: int) -> str:
        """
        Create wobble/sync filter for beat-matched effects
        
        Args:
            duration: Duration in seconds
            intensity: Intensity percentage
            
        Returns:
            FFmpeg filter string
        """
        freq = 1 + (intensity / 100) * 4  # 1-5 Hz
        return f"""split[a][b];
                [a]scale=w='if(eq(n,0),iw,iw+(20*sin(t*{freq}*pi)*{intensity/100}))':
                h='if(eq(n,0),ih,ih+(20*sin(t*{freq}*pi)*{intensity/100}))'[a];
                [a][b]overlay=x='(W-w)/2+(10*sin(t*{freq}*pi))':y='(H-h)/2+(10*cos(t*{freq}*pi))'[out]
        """

    def select_intelligent_transition(
        self,
        prev_energy: float,
        curr_energy: float,
        prev_shot_scale: str,
        curr_shot_scale: str,
        prev_movement: str,
        curr_movement: str,
        bpm: float,
        is_drop: bool = False,
        is_breath: bool = False
    ) -> AdvancedTransition:
        """
        Intelligently select transition based on context
        
        Args:
            prev_energy: Previous segment energy
            curr_energy: Current segment energy
            prev_shot_scale: Previous shot scale
            curr_shot_scale: Current shot scale
            prev_movement: Previous camera movement
            curr_movement: Current camera movement
            bpm: Beats per minute
            is_drop: Is this a drop point?
            is_breath: Is this a breath/silence?
            
        Returns:
            Selected AdvancedTransition
        """
        energy_diff = abs(curr_energy - prev_energy)
        shot_change = prev_shot_scale != curr_shot_scale
        movement_change = prev_movement != curr_movement
        
        # High energy drop -> dramatic transition
        if is_drop and energy_diff > 0.6:
            return self.create_transition(
                TransitionType.COLOR_FLASH,
                duration=0.2,
                intensity=1.0,
                easing="ease_out",
                beat_sync=True
            )
        
        # Silence/breath -> smooth, slow transition
        if is_breath:
            return self.create_transition(
                TransitionType.DISSOLVE,
                duration=1.0,
                intensity=0.7,
                easing="ease_in_out"
            )
        
        # Large shot scale change -> dynamic transition
        if shot_change:
            shot_intensity = self._calculate_shot_change_intensity(
                prev_shot_scale, curr_shot_scale
            )
            if shot_intensity > 0.7:
                return self.create_transition(
                    TransitionType.ZOOM_IN,
                    duration=0.4,
                    intensity=0.8,
                    beat_sync=True
                )
        
        # High energy change -> energetic transition
        if energy_diff > 0.5:
            return self.create_transition(
                TransitionType.BLEND,
                duration=0.3,
                intensity=0.9,
                easing="ease_out",
                beat_sync=True
            )
        
        # Medium energy change -> standard transitions
        if energy_diff > 0.2:
            if movement_change:
                return self.create_transition(
                    TransitionType.SLIDE_LEFT,
                    duration=0.5,
                    intensity=0.6
                )
            else:
                return self.create_transition(
                    TransitionType.CROSSFADE,
                    duration=0.5,
                    intensity=0.7
                )
        
        # Low energy change -> subtle transition
        return self.create_transition(
            TransitionType.FADE,
            duration=0.8,
            intensity=0.5,
            easing="ease_in_out"
        )

    def _calculate_shot_change_intensity(self, shot1: str, shot2: str) -> float:
        """
        Calculate intensity of shot change
        
        Args:
            shot1: First shot scale
            shot2: Second shot scale
            
        Returns:
            Change intensity (0-1)
        """
        scale_order = {
            'wide': 0,
            'medium': 1,
            'close_up': 2,
            'extreme_close_up': 3
        }
        scale1 = scale_order.get(shot1, 1)
        scale2 = scale_order.get(shot2, 1)
        return abs(scale2 - scale1) / 3.0

    def create_bass_wobble_effect(
        self,
        intensity: float = 0.8,
        frequency: float = 4.0,
        decay: float = 0.7
    ) -> VisualEffect:
        """
        Create bass-intensity wobble zoom effect
        
        Args:
            intensity: Effect intensity (0-1)
            frequency: Wobble frequency (Hz)
            decay: Decay from center (0-1)
            
        Returns:
            VisualEffect object
        """
        return VisualEffect(
            name="bass_wobble_zoom",
            intensity=intensity,
            parameters={
                'frequency': frequency,
                'decay': decay,
                'zoom_min': 1.0,
                'zoom_max': 1.0 + intensity * 0.3,
                'center_x': 0.5,
                'center_y': 0.5
            }
        )

    def create_color_grading_effect(
        self,
        color_temp: str = "cool",
        saturation: float = 1.0,
        contrast: float = 1.0,
        vibrance: float = 0.0
    ) -> VisualEffect:
        """
        Create color grading effect
        
        Args:
            color_temp: Color temperature (cool, warm, neutral)
            saturation: Saturation level (0-2)
            contrast: Contrast level (0-2)
            vibrance: Vibrance level (-1 to 1)
            
        Returns:
            VisualEffect object
        """
        color_lut = {
            'cool': {'r': 0.9, 'g': 0.95, 'b': 1.1},
            'warm': {'r': 1.1, 'g': 1.0, 'b': 0.85},
            'neutral': {'r': 1.0, 'g': 1.0, 'b': 1.0},
            'cinematic': {'r': 1.05, 'g': 0.98, 'b': 0.92},
            'vintage': {'r': 1.1, 'g': 0.95, 'b': 0.85}
        }
        
        return VisualEffect(
            name="color_grading",
            intensity=1.0,
            parameters={
                'color_temp': color_lut.get(color_temp, color_lut['neutral']),
                'saturation': saturation,
                'contrast': contrast,
                'vibrance': vibrance
            }
        )

    def create_face_cut_optimizer() -> Dict:
        """
        Get recommendations for face-cut optimization
        Based on viral marketing best practices
        
        Returns:
            Optimization dictionary
        """
        return {
            'optimal_face_cut_duration': 0.5,  # 500ms
            'min_face_cuts_per_minute': 2,
            'max_face_cuts_per_minute': 8,
            'drop_section_face_cuts': '+40%',
            'chorus_face_cut_frequency': 'high',
            'viral_recommendation': 'Increase face close-ups during high-energy sections by 15-20%'
        }

    def create_dynamic_pacing_effect(
        self,
        bpm: float,
        energy: float
    ) -> Dict:
        """
        Create dynamic pacing based on music
        
        Args:
            bpm: Beats per minute
            energy: Energy level (0-1)
            
        Returns:
            Pacing dictionary
        """
        if bpm > 140:  # Fast
            cut_frequency = "every 0.3-0.5s"
            effect_intensity = 0.9
        elif bpm > 100:  # Medium-fast
            cut_frequency = "every 0.5-0.8s"
            effect_intensity = 0.7
        elif bpm > 70:  # Medium
            cut_frequency = "every 0.8-1.2s"
            effect_intensity = 0.5
        else:  # Slow
            cut_frequency = "every 1.2-2.0s"
            effect_intensity = 0.3
        
        return {
            'bpm': bpm,
            'energy': energy,
            'cut_frequency': cut_frequency,
            'effect_intensity': effect_intensity,
            'transition_duration': max(0.2, 1.0 / (bpm / 60)) / 2
        }

    def export_transition_preset(self, preset_name: str, transition: AdvancedTransition) -> None:
        """
        Export transition as preset
        
        Args:
            preset_name: Name of preset
            transition: AdvancedTransition object
        """
        os.makedirs("presets", exist_ok=True)
        preset_data = {
            'name': preset_name,
            'type': transition.type.value,
            'duration': transition.duration,
            'intensity': transition.intensity,
            'easing': transition.easing,
            'audio_responsive': transition.audio_responsive,
            'beat_sync': transition.beat_sync
        }
        
        with open(f"presets/{preset_name}.json", 'w') as f:
            json.dump(preset_data, f, indent=2)
        
        logger.success(f"Transition preset exported: {preset_name}")
