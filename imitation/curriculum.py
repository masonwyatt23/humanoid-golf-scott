"""
Curriculum stages for humanoid golf training.

Stage 0: Address position stability
Stage 1: Make contact with the ball
Stage 2: Match reference style (PureGolf / Adam Scott)
Stage 3: Optimize ball flight distance and accuracy
"""

from enum import IntEnum


class CurriculumStage(IntEnum):
    ADDRESS = 0
    CONTACT = 1
    STYLE = 2
    BALL_FLIGHT = 3


def get_stage_reward_weights(stage: CurriculumStage) -> dict:
    """Return reward component weights for the current curriculum stage."""
    if stage == CurriculumStage.ADDRESS:
        return {"imitation": 0.5, "contact": 0.0, "ball": 0.0, "stability": 3.0}
    elif stage == CurriculumStage.CONTACT:
        return {"imitation": 1.0, "contact": 5.0, "ball": 0.2, "stability": 1.5}
    elif stage == CurriculumStage.STYLE:
        return {"imitation": 3.0, "contact": 3.0, "ball": 0.5, "stability": 1.0}
    else:  # BALL_FLIGHT
        return {"imitation": 1.5, "contact": 2.0, "ball": 2.0, "stability": 1.0}


def should_advance(stage: CurriculumStage, metrics: dict) -> bool:
    """Simple advancement criteria based on recent performance."""
    if stage == CurriculumStage.ADDRESS:
        return metrics.get("stability_rate", 0) > 0.8
    elif stage == CurriculumStage.CONTACT:
        return metrics.get("contact_rate", 0) > 0.6
    elif stage == CurriculumStage.STYLE:
        return metrics.get("imitation_score", 0) > 0.7
    return False
