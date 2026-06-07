#!/usr/bin/env python3
"""
Viral Scoring & Analytics
Realistische Viral-Scoring mit konkreten Verbesserungstipps.
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum
from loguru import logger
import json
import os


@dataclass
class ViralMetric:
    """Single viral metric"""
    name: str
    current_value: float
    recommended_value: float
    weight: float
    improvement_tip: str
    potential_gain: str


@dataclass
class ViralAnalysis:
    """Complete viral analysis"""
    viral_score: float  # 0-100
    engagement_potential: float  # 0-1
    retention_potential: float  # 0-1
    shareability_score: float  # 0-1
    metrics: List[ViralMetric] = field(default_factory=list)
    improvements: List[str] = field(default_factory=list)
    top_recommendations: List[str] = field(default_factory=list)


class ViralScoringEngine:
    """Analyzes viral potential and provides optimization tips"""

    def __init__(self):
        """
        Initialize ViralScoringEngine
        """
        self.metric_weights = {
            'face_cuts': 0.20,
            'cut_frequency': 0.15,
            'visual_variety': 0.15,
            'color_grading': 0.10,
            'transitions': 0.10,
            'pacing_energy_match': 0.10,
            'effect_intensity': 0.10,
            'audio_visual_sync': 0.10
        }
        logger.info("ViralScoringEngine initialized")

    def analyze_video_potential(
        self,
        face_cut_count: int,
        face_cut_duration_avg: float,
        cut_frequency: float,
        shot_variety: int,
        transition_smoothness: float,
        effect_intensity: float,
        audio_visual_sync: float,
        bpm: float,
        duration: float
    ) -> ViralAnalysis:
        """
        Analyze viral potential
        
        Args:
            face_cut_count: Number of face close-ups
            face_cut_duration_avg: Average face-cut duration
            cut_frequency: Average cuts per second
            shot_variety: Number of different shots
            transition_smoothness: Transition quality (0-1)
            effect_intensity: Visual effect intensity (0-1)
            audio_visual_sync: Audio-visual sync score (0-1)
            bpm: Beats per minute
            duration: Video duration in seconds
            
        Returns:
            ViralAnalysis object
        """
        logger.info("Analyzing viral potential...")
        
        metrics = []
        scores = {}
        
        # Face cuts metric
        optimal_face_cuts = max(2, min(8, (bpm / 120) * 5))  # Scale with BPM
        face_cuts_score = min(1.0, face_cut_count / optimal_face_cuts)
        scores['face_cuts'] = face_cuts_score
        metrics.append(ViralMetric(
            name="Face Close-Ups",
            current_value=float(face_cut_count),
            recommended_value=optimal_face_cuts,
            weight=self.metric_weights['face_cuts'],
            improvement_tip=f"Add {max(0, int(optimal_face_cuts - face_cut_count))} more face-close-ups during high-energy sections",
            potential_gain="+15%" if face_cut_count < optimal_face_cuts else "+0%"
        ))
        
        # Cut frequency metric
        optimal_cut_freq = 2.0 + (bpm / 120)  # 2-3 cuts per second
        cut_freq_score = min(1.0, cut_frequency / optimal_cut_freq)
        scores['cut_frequency'] = cut_freq_score
        metrics.append(ViralMetric(
            name="Cut Frequency",
            current_value=cut_frequency,
            recommended_value=optimal_cut_freq,
            weight=self.metric_weights['cut_frequency'],
            improvement_tip=f"Increase cutting pace to {optimal_cut_freq:.1f} cuts/second for higher engagement",
            potential_gain="+12%" if cut_frequency < optimal_cut_freq else "+0%"
        ))
        
        # Shot variety
        optimal_shots = max(3, int(duration / 2))  # At least 3 different shots
        shot_variety_score = min(1.0, shot_variety / optimal_shots)
        scores['visual_variety'] = shot_variety_score
        metrics.append(ViralMetric(
            name="Visual Variety",
            current_value=float(shot_variety),
            recommended_value=float(optimal_shots),
            weight=self.metric_weights['visual_variety'],
            improvement_tip=f"Mix {max(0, optimal_shots - shot_variety)} more unique shots for variety",
            potential_gain="+10%" if shot_variety < optimal_shots else "+0%"
        ))
        
        # Color grading
        color_score = 0.7 if effect_intensity > 0.5 else 0.5
        scores['color_grading'] = color_score
        metrics.append(ViralMetric(
            name="Color Grading",
            current_value=effect_intensity,
            recommended_value=0.8,
            weight=self.metric_weights['color_grading'],
            improvement_tip="Apply cinematic color grading for Instagram/TikTok optimization",
            potential_gain="+8%" if effect_intensity < 0.7 else "+0%"
        ))
        
        # Transitions
        transition_score = transition_smoothness
        scores['transitions'] = transition_score
        metrics.append(ViralMetric(
            name="Transition Quality",
            current_value=transition_smoothness,
            recommended_value=1.0,
            weight=self.metric_weights['transitions'],
            improvement_tip="Use beat-sync transitions for professional feel",
            potential_gain="+6%" if transition_smoothness < 0.8 else "+0%"
        ))
        
        # Pacing-energy match
        pacing_score = 0.8 if (bpm / 120) > 0.8 else 0.6  # Fast BPM better for viral
        scores['pacing_energy_match'] = pacing_score
        metrics.append(ViralMetric(
            name="Pacing-Energy Match",
            current_value=bpm,
            recommended_value=120.0,
            weight=self.metric_weights['pacing_energy_match'],
            improvement_tip=f"Faster cuts recommended for BPM-based pacing",
            potential_gain="+7%" if bpm > 100 else "+3%"
        ))
        
        # Effect intensity
        effect_score = effect_intensity
        scores['effect_intensity'] = effect_score
        metrics.append(ViralMetric(
            name="Visual Effects",
            current_value=effect_intensity,
            recommended_value=0.7,
            weight=self.metric_weights['effect_intensity'],
            improvement_tip="Boost bass wobble effects during drops",
            potential_gain="+9%" if effect_intensity < 0.6 else "+0%"
        ))
        
        # Audio-visual sync
        av_sync_score = audio_visual_sync
        scores['audio_visual_sync'] = av_sync_score
        metrics.append(ViralMetric(
            name="Audio-Visual Sync",
            current_value=audio_visual_sync,
            recommended_value=1.0,
            weight=self.metric_weights['audio_visual_sync'],
            improvement_tip="Perfect beat-sync increases retention by 18%",
            potential_gain="+18%" if audio_visual_sync < 0.9 else "+0%"
        ))
        
        # Calculate overall viral score
        viral_score = sum(
            scores[metric] * self.metric_weights[metric]
            for metric in self.metric_weights.keys()
        ) * 100
        
        # Calculate engagement/retention/shareability
        engagement = 0.6 + (cut_freq_score * 0.2) + (face_cuts_score * 0.2)
        retention = 0.5 + (transition_score * 0.3) + (av_sync_score * 0.2)
        shareability = 0.4 + (shot_variety_score * 0.3) + (color_score * 0.3)
        
        # Generate recommendations
        improvements = [m.improvement_tip for m in metrics if float(m.potential_gain.rstrip('%').replace('+', '')) > 5]
        
        # Top 3 recommendations
        ranked_metrics = sorted(metrics, key=lambda m: float(m.potential_gain.rstrip('%').replace('+', '')), reverse=True)
        top_recommendations = [m.improvement_tip for m in ranked_metrics[:3]]
        
        analysis = ViralAnalysis(
            viral_score=min(100, viral_score),
            engagement_potential=min(1.0, engagement),
            retention_potential=min(1.0, retention),
            shareability_score=min(1.0, shareability),
            metrics=metrics,
            improvements=improvements,
            top_recommendations=top_recommendations
        )
        
        logger.success(f"Viral analysis complete: {analysis.viral_score:.1f}/100")
        return analysis

    def export_viral_report(self, analysis: ViralAnalysis, output_path: str) -> None:
        """
        Export viral analysis as JSON report
        
        Args:
            analysis: ViralAnalysis object
            output_path: Output JSON file path
        """
        report = {
            'viral_score': analysis.viral_score,
            'engagement_potential': analysis.engagement_potential,
            'retention_potential': analysis.retention_potential,
            'shareability_score': analysis.shareability_score,
            'metrics': [
                {
                    'name': m.name,
                    'current': m.current_value,
                    'recommended': m.recommended_value,
                    'weight': m.weight,
                    'improvement_tip': m.improvement_tip,
                    'potential_gain': m.potential_gain
                }
                for m in analysis.metrics
            ],
            'recommendations': analysis.top_recommendations,
            'all_improvements': analysis.improvements
        }
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.success(f"Viral report exported to {output_path}")

    def print_viral_report(self, analysis: ViralAnalysis) -> None:
        """
        Print viral analysis report
        
        Args:
            analysis: ViralAnalysis object
        """
        logger.info("\n" + "=" * 70)
        logger.info("VIRAL POTENTIAL ANALYSIS")
        logger.info("=" * 70)
        logger.success(f"Overall Viral Score: {analysis.viral_score:.1f}/100")
        logger.info(f"Engagement Potential: {analysis.engagement_potential:.1%}")
        logger.info(f"Retention Potential: {analysis.retention_potential:.1%}")
        logger.info(f"Shareability Score: {analysis.shareability_score:.1%}")
        
        logger.info("\n" + "-" * 70)
        logger.info("TOP RECOMMENDATIONS:")
        logger.info("-" * 70)
        for i, rec in enumerate(analysis.top_recommendations, 1):
            logger.success(f"{i}. {rec}")
        
        logger.info("\n" + "-" * 70)
        logger.info("DETAILED METRICS:")
        logger.info("-" * 70)
        for metric in analysis.metrics:
            logger.info(f"{metric.name}:")
            logger.info(f"  Current: {metric.current_value:.2f} | Recommended: {metric.recommended_value:.2f}")
            logger.info(f"  Potential Gain: {metric.potential_gain}")
            logger.debug(f"  Tip: {metric.improvement_tip}")
        
        logger.info("\n" + "=" * 70)
