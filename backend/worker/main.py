"""
Worker entry point for GPU-accelerated video processing.
"""
import sys
import signal
from pathlib import Path
from typing import Optional

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from observability.logging import setup_logging, get_logger
from worker.inference.yolo_engine import YOLO11Engine
from app.core.config import settings

# Initialize logging
setup_logging()
logger = get_logger(__name__)


class Worker:
    """GPU worker for video processing."""
    
    def __init__(self, worker_id: Optional[str] = None):
        """
        Initialize worker.
        
        Args:
            worker_id: Unique worker identifier
        """
        self.worker_id = worker_id or f"worker_{Path(__file__).parent.name}"
        self.yolo_engine: Optional[YOLO11Engine] = None
        self.running = False
        
        logger.info(f"Initializing worker: {self.worker_id}")
    
    def initialize(self):
        """Initialize worker components."""
        try:
            # Initialize YOLO11 engine
            self.yolo_engine = YOLO11Engine()
            self.yolo_engine.load_model()
            logger.info(f"Worker {self.worker_id} initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize worker: {e}")
            raise
    
    def start(self):
        """Start worker processing loop."""
        if self.running:
            logger.warning("Worker is already running")
            return
        
        if not self.yolo_engine:
            self.initialize()
        
        self.running = True
        logger.info(f"Worker {self.worker_id} started")
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        try:
            # Main processing loop (will be implemented with queue)
            self._process_loop()
        except KeyboardInterrupt:
            logger.info("Worker interrupted by user")
        finally:
            self.stop()
    
    def stop(self):
        """Stop worker."""
        if not self.running:
            return
        
        self.running = False
        logger.info(f"Worker {self.worker_id} stopping...")
        
        # Cleanup
        if self.yolo_engine:
            # Model cleanup if needed
            pass
        
        logger.info(f"Worker {self.worker_id} stopped")
    
    def _process_loop(self):
        """Main processing loop (placeholder for queue integration)."""
        logger.info("Processing loop started (queue integration pending)")
        # TODO: Implement queue polling and job processing
        while self.running:
            # Placeholder - will poll Redis queue for jobs
            import time
            time.sleep(1)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger.info(f"Received signal {signum}, shutting down...")
        self.stop()
        sys.exit(0)


def main():
    """Main entry point for worker."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Video Processing Worker")
    parser.add_argument("--worker-id", type=str, help="Worker identifier")
    args = parser.parse_args()
    
    worker = Worker(worker_id=args.worker_id)
    
    try:
        worker.start()
    except Exception as e:
        logger.error(f"Worker failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

