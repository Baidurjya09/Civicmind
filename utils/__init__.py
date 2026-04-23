"""CivicMind Utils Package"""

import json
from pathlib import Path
from typing import List, Dict, Any


class EpisodeTracker:
    """Track episode metrics"""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.episodes = []
    
    def log_episode(self, episode_data: Dict[str, Any]):
        """Log one episode"""
        self.episodes.append(episode_data)
    
    def save(self, filename: str = "episodes.jsonl"):
        """Save all episodes"""
        path = self.log_dir / filename
        with open(path, "w") as f:
            for ep in self.episodes:
                f.write(json.dumps(ep) + "\n")
        return str(path)


class TrainingLogger:
    """Log training metrics"""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.metrics = []
    
    def log(self, step: int, metrics: Dict[str, float]):
        """Log metrics for one step"""
        self.metrics.append({"step": step, **metrics})
    
    def save(self, filename: str = "training.jsonl"):
        """Save metrics"""
        path = self.log_dir / filename
        with open(path, "w") as f:
            for m in self.metrics:
                f.write(json.dumps(m) + "\n")
        return str(path)
