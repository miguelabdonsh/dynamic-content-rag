"""
Auto-Ingestion System - File watcher for automatic processing
"""

from pathlib import Path
from typing import Set
from threading import Thread, Event
from backend.services.ingestor import ContentIngestor
from backend.config.settings import settings

class AutoIngest:
    """Automatic file watcher and processor"""
    
    def __init__(self):
        self.ingestor = ContentIngestor()
        self.processed_files: Set[str] = set()
        self.stop_event = Event()
        self.running = False
        self._load_processed_files()
    
    def _load_processed_files(self) -> None:
        """Load list of already processed files"""
        json_files = settings.CRAWLED_DIR.glob("*.json")
        self.processed_files = {f.name for f in json_files}
    
    def _detect_new_files(self) -> list[Path]:
        """Detect new JSON files"""
        current_files = set(f.name for f in settings.CRAWLED_DIR.glob("*.json"))
        new_files = current_files - self.processed_files
        
        if new_files:
            new_paths = [settings.CRAWLED_DIR / fname for fname in new_files]
            self.processed_files.update(new_files)
            return new_paths
        return []
    
    def _process_new_files(self, new_files: list[Path]) -> None:
        """Process specific new files only"""
        if not new_files:
            return
        
        try:
            # Process ONLY the specific new files
            self.ingestor.process_specific_files(new_files)
        except Exception:
            pass
    
    def start_watching(self, interval: int = 300) -> None:
        """Start file watching (5 minutes default)"""
        if self.running:
            return
        
        self.running = True
        self.stop_event.clear()
        
        def watch_loop():
            while not self.stop_event.wait(interval):
                new_files = self._detect_new_files()
                if new_files:
                    self._process_new_files(new_files)
        
        self.watch_thread = Thread(target=watch_loop, daemon=True)
        self.watch_thread.start()
    
    def stop_watching(self) -> None:
        """Stop file watching"""
        if self.running:
            self.stop_event.set()
            self.running = False
    
    def is_running(self) -> bool:
        """Check if watcher is running"""
        return self.running

# Global auto-ingest instance
auto_ingest = AutoIngest() 