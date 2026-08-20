"""
Ablation-study flags. Set via environment variables by ablate.py
so Activity Guide and Scene Description can disable one component at a time.
"""

import os
from dataclasses import dataclass
from typing import Optional


ENV_KEYS = {
    "no_active_guidance": "AIRIS_NO_ACTIVE_GUIDANCE",
    "no_hand_tracking": "AIRIS_NO_HAND_TRACKING",
    "no_depth_heuristic": "AIRIS_NO_DEPTH_HEURISTIC",
    "no_blip": "AIRIS_NO_BLIP",
    "no_llm": "AIRIS_NO_LLM",
}

CONDITIONS = {
    "no_active_guidance": {
        "flag": "--noActiveGuidance",
        "service": "activity_guide_service",
        "title": "No Active Guidance / No directional loop",
        "disables": "Closed-loop left/right/up/down/forward instructions",
        "keeps": "YOLO detection, MediaPipe, depth heuristic, object-location announcement",
        "mode": "Activity Guide",
    },
    "no_hand_tracking": {
        "flag": "--noHandTracking",
        "service": "activity_guide_service",
        "title": "No Hand Tracking / MediaPipe off",
        "disables": "MediaPipe hand landmarks and hand-to-object vectors",
        "keeps": "YOLO detection, object-vs-frame-center directions, depth heuristic",
        "mode": "Activity Guide",
    },
    "no_depth_heuristic": {
        "flag": "--noDepthHeuristic",
        "service": "activity_guide_service",
        "title": "No depth heuristic / Area ratio forward/backoff",
        "disables": "Bounding-box area-ratio depth (forward / back) and depth-gated contact",
        "keeps": "YOLO detection, MediaPipe, 2D left/right/up/down guidance",
        "mode": "Activity Guide",
    },
    "no_blip": {
        "flag": "--noBLIP",
        "service": "scene_description_service",
        "title": "No BLIP / Captioning off",
        "disables": "BLIP image captioning (no per-frame descriptions)",
        "keeps": "Recording loop, LLM unused because there are no captions",
        "mode": "Scene Description",
    },
    "no_llm": {
        "flag": "--noLLM",
        "service": "scene_description_service",
        "title": "No LLM / Groq/GPT-OSS off",
        "disables": "Groq GPT-OSS summarization and LLM risk scoring",
        "keeps": "BLIP captions, keyword risk assessment, heuristic fall detection",
        "mode": "Scene Description",
    },
}


def _flag_on(env_name: str) -> bool:
    return os.environ.get(env_name, "").strip().lower() in ("1", "true", "yes", "on")


@dataclass
class AblationFlags:
    no_active_guidance: bool = False
    no_hand_tracking: bool = False
    no_depth_heuristic: bool = False
    no_blip: bool = False
    no_llm: bool = False

    def active_keys(self) -> list:
        keys = []
        for key in CONDITIONS:
            if getattr(self, key):
                keys.append(key)
        return keys

    def any_active(self) -> bool:
        return bool(self.active_keys())

    def describe(self) -> str:
        keys = self.active_keys()
        if not keys:
            return "baseline (all components on)"
        return "; ".join(CONDITIONS[k]["title"] for k in keys)


def get_ablation_flags() -> AblationFlags:
    return AblationFlags(
        no_active_guidance=_flag_on(ENV_KEYS["no_active_guidance"]),
        no_hand_tracking=_flag_on(ENV_KEYS["no_hand_tracking"]),
        no_depth_heuristic=_flag_on(ENV_KEYS["no_depth_heuristic"]),
        no_blip=_flag_on(ENV_KEYS["no_blip"]),
        no_llm=_flag_on(ENV_KEYS["no_llm"]),
    )


def apply_condition(condition_key: Optional[str]) -> None:
    """Set env vars for one ablation condition (or clear them for baseline)."""
    for env_name in ENV_KEYS.values():
        os.environ.pop(env_name, None)
    if condition_key and condition_key in ENV_KEYS:
        os.environ[ENV_KEYS[condition_key]] = "1"
