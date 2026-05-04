"""Checkpoint management for transcription state."""

import json
import hashlib
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class CheckpointManager:
    """Manage JSON checkpoint files for transcription state."""

    def __init__(self, checkpoint_path: Path):
        """Initialize checkpoint manager."""
        self.checkpoint_path = checkpoint_path
        self.checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
        self.state: Dict[str, Any] = {}

    def load(self) -> Dict[str, Any]:
        """Load checkpoint state from JSON file."""
        if not self.checkpoint_path.exists():
            logger.info(f"Checkpoint not found: {self.checkpoint_path}")
            return {}

        try:
            with open(self.checkpoint_path, 'r', encoding='utf-8') as f:
                self.state = json.load(f)
            logger.info(f"Loaded checkpoint: {self.checkpoint_path}")
            return self.state
        except (json.JSONDecodeError, Exception) as e:
            logger.error(f"Failed to load checkpoint: {e}")
            return {}

    def save(self) -> bool:
        """Save checkpoint state atomically."""
        try:
            self.state['last_updated'] = datetime.utcnow().isoformat() + 'Z'
            temp_path = self.checkpoint_path.with_suffix('.tmp')

            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, indent=2, ensure_ascii=False)

            temp_path.replace(self.checkpoint_path)
            return True
        except Exception as e:
            logger.error(f"Failed to save checkpoint: {e}")
            return False

    def initialize(self, book_name: str, total_images: int, yaml_version: str, yaml_hash: str):
        """Initialize checkpoint state for a new book."""
        if not self.state:
            self.state = {
                'book_name': book_name,
                'yaml_version': yaml_version,
                'yaml_hash': yaml_hash,
                'last_updated': datetime.utcnow().isoformat() + 'Z',
                'total_images': total_images,
                'processed_images': 0,
                'total_cost_usd': 0.0,
                'images': {}
            }

    def update_image_status(
        self,
        image_name: str,
        status: str,
        cost_usd: float = 0.0,
        verses: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None
    ):
        """Update status for specific image."""
        if 'images' not in self.state:
            self.state['images'] = {}

        image_data = {
            'status': status,
            'processed_at': datetime.utcnow().isoformat() + 'Z',
            'cost_usd': cost_usd
        }

        if verses:
            image_data['verses'] = verses
        if error:
            image_data['error'] = error

        self.state['images'][image_name] = image_data

        self.state['processed_images'] = sum(
            1 for img in self.state['images'].values()
            if img.get('status') == 'completed'
        )
        self.state['total_cost_usd'] = sum(
            img.get('cost_usd', 0.0) for img in self.state['images'].values()
        )

    def is_image_processed(self, image_name: str) -> bool:
        """Check if image already processed."""
        if 'images' not in self.state:
            return False
        image_data = self.state['images'].get(image_name)
        return image_data.get('status') == 'completed' if image_data else False

    def get_processed_verses(self) -> List[Dict[str, Any]]:
        """Get all completed verses from checkpoint."""
        verses = []
        if 'images' not in self.state:
            return verses

        for image_name, image_data in self.state['images'].items():
            if image_data.get('status') == 'completed' and 'verses' in image_data:
                for verse_key, verse_data in image_data['verses'].items():
                    if verse_data.get('status') == 'completed':
                        verses.append({
                            'chapter': verse_data.get('chapter'),
                            'verse': verse_data.get('verse'),
                            'text_nikud': verse_data.get('text_nikud'),
                            'source_files': verse_data.get('source_files', [image_name]),
                            'visual_uncertainty': verse_data.get('visual_uncertainty', [])
                        })
        return verses

    def get_failed_images(self) -> List[str]:
        """Get list of failed image names."""
        if 'images' not in self.state:
            return []
        return [
            name for name, data in self.state['images'].items()
            if data.get('status') == 'failed'
        ]

    @staticmethod
    def calculate_yaml_hash(yaml_content: str) -> str:
        """Calculate SHA256 hash of YAML content."""
        return hashlib.sha256(yaml_content.encode('utf-8')).hexdigest()

