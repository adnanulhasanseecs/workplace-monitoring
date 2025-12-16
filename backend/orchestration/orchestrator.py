"""
Job orchestrator - coordinates job distribution and GPU allocation.
"""
from typing import Optional, Dict, Any
from datetime import datetime

from orchestration.gpu_manager import GPUManager
from orchestration.job_queue import JobQueue
from observability.logging import get_logger

logger = get_logger(__name__)


class JobOrchestrator:
    """Orchestrates job distribution and resource allocation."""
    
    def __init__(self):
        """Initialize orchestrator."""
        self.gpu_manager = GPUManager()
        self.job_queue = JobQueue()
        self.active_jobs: Dict[str, Dict[str, Any]] = {}
    
    def create_job(
        self,
        camera_id: int,
        source_type: str,  # "stream" or "file"
        source_path: Optional[str] = None,
        job_metadata: Optional[Dict[str, Any]] = None,
        priority: int = 0,
    ) -> str:
        """
        Create and enqueue a processing job.
        
        Args:
            camera_id: Camera ID
            source_type: Type of source ("stream" or "file")
            source_path: Path to source (for file uploads)
            job_metadata: Optional job metadata
            priority: Job priority
            
        Returns:
            Job ID
        """
        job_data = {
            "camera_id": camera_id,
            "source_type": source_type,
            "source_path": source_path,
            "metadata": job_metadata or {},
        }
        
        job_id = self.job_queue.enqueue_job(
            job_type="process_video",
            job_data=job_data,
            priority=priority,
        )
        
        # Track job
        self.active_jobs[job_id] = {
            "job_id": job_id,
            "camera_id": camera_id,
            "status": "pending",
            "created_at": datetime.utcnow(),
        }
        
        logger.info(f"Job created: {job_id}, camera_id={camera_id}, type={source_type}")
        return job_id
    
    def assign_job_to_gpu(self, job_id: str) -> Optional[int]:
        """
        Assign a job to an available GPU.
        
        Args:
            job_id: Job ID
            
        Returns:
            GPU ID or None if no GPU available
        """
        gpu_id = self.gpu_manager.get_available_gpu(min_memory_gb=2.0)
        
        if gpu_id is None:
            logger.warning(f"No available GPU for job {job_id}")
            return None
        
        # Mark GPU as busy
        self.gpu_manager.mark_gpu_busy(gpu_id)
        
        # Update job status
        if job_id in self.active_jobs:
            self.active_jobs[job_id]["gpu_id"] = gpu_id
            self.active_jobs[job_id]["status"] = "assigned"
            self.active_jobs[job_id]["assigned_at"] = datetime.utcnow()
        
        self.job_queue.update_job_status(
            job_id,
            "assigned",
            {"gpu_id": gpu_id},
        )
        
        logger.info(f"Job {job_id} assigned to GPU {gpu_id}")
        return gpu_id
    
    def complete_job(self, job_id: str, result: Optional[Dict[str, Any]] = None):
        """
        Mark job as complete and free GPU.
        
        Args:
            job_id: Job ID
            result: Optional job result data
        """
        if job_id in self.active_jobs:
            job = self.active_jobs[job_id]
            gpu_id = job.get("gpu_id")
            
            if gpu_id is not None:
                self.gpu_manager.mark_gpu_available(gpu_id)
            
            job["status"] = "completed"
            job["completed_at"] = datetime.utcnow()
            if result:
                job["result"] = result
        
        self.job_queue.update_job_status(
            job_id,
            "completed",
            result,
        )
        
        logger.info(f"Job {job_id} completed")
    
    def fail_job(self, job_id: str, error: str):
        """
        Mark job as failed and free GPU.
        
        Args:
            job_id: Job ID
            error: Error message
        """
        if job_id in self.active_jobs:
            job = self.active_jobs[job_id]
            gpu_id = job.get("gpu_id")
            
            if gpu_id is not None:
                self.gpu_manager.mark_gpu_available(gpu_id)
            
            job["status"] = "failed"
            job["error"] = error
            job["failed_at"] = datetime.utcnow()
        
        self.job_queue.update_job_status(
            job_id,
            "failed",
            {"error": error},
        )
        
        logger.error(f"Job {job_id} failed: {error}")
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get job status.
        
        Args:
            job_id: Job ID
            
        Returns:
            Job status dictionary or None if not found
        """
        # Check active jobs first
        if job_id in self.active_jobs:
            return self.active_jobs[job_id].copy()
        
        # Check Redis
        return self.job_queue.get_job_status(job_id)
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """
        Get queue statistics.
        
        Returns:
            Dictionary with queue statistics
        """
        return {
            "queue_length": self.job_queue.get_queue_length(),
            "active_jobs": len(self.active_jobs),
            "gpu_count": len(self.gpu_manager.get_all_gpus()),
            "available_gpus": len([g for g in self.gpu_manager.get_all_gpus() if g["available"]]),
        }

