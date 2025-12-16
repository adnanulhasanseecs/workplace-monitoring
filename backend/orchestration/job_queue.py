"""
Job queue interface for Redis-based task queue.
"""
import json
import uuid
from typing import Optional, Dict, Any, List
from datetime import datetime

import redis
from app.core.config import settings
from observability.logging import get_logger

logger = get_logger(__name__)


class JobQueue:
    """Redis-based job queue interface."""
    
    def __init__(self):
        """Initialize job queue."""
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB_QUEUE,
            password=settings.REDIS_PASSWORD if settings.REDIS_PASSWORD else None,
            decode_responses=True,
        )
        
        # Test connection
        try:
            self.redis_client.ping()
            logger.info("Job queue connected to Redis")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    def enqueue_job(
        self,
        job_type: str,
        job_data: Dict[str, Any],
        priority: int = 0,
    ) -> str:
        """
        Enqueue a job.
        
        Args:
            job_type: Type of job (e.g., 'process_video', 'process_stream')
            job_data: Job data dictionary
            priority: Job priority (higher = more important)
            
        Returns:
            Job ID
        """
        job_id = str(uuid.uuid4())
        
        job = {
            "id": job_id,
            "type": job_type,
            "data": job_data,
            "priority": priority,
            "status": "pending",
            "created_at": datetime.utcnow().isoformat(),
        }
        
        # Use sorted set for priority queue
        score = priority * 1000000 + int(datetime.utcnow().timestamp() * 1000)
        self.redis_client.zadd("job_queue", {json.dumps(job): score})
        
        logger.info(f"Job enqueued: {job_id}, type={job_type}, priority={priority}")
        return job_id
    
    def dequeue_job(self, timeout: int = 5) -> Optional[Dict[str, Any]]:
        """
        Dequeue a job (blocking).
        
        Args:
            timeout: Blocking timeout in seconds
            
        Returns:
            Job dictionary or None if timeout
        """
        # Get highest priority job
        result = self.redis_client.zrevrange("job_queue", 0, 0, withscores=False)
        
        if not result:
            return None
        
        job_str = result[0]
        job = json.loads(job_str)
        
        # Remove from queue
        self.redis_client.zrem("job_queue", job_str)
        
        logger.info(f"Job dequeued: {job['id']}")
        return job
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get job status.
        
        Args:
            job_id: Job ID
            
        Returns:
            Job status dictionary or None if not found
        """
        status_key = f"job_status:{job_id}"
        status_data = self.redis_client.get(status_key)
        
        if not status_data:
            return None
        
        return json.loads(status_data)
    
    def update_job_status(
        self,
        job_id: str,
        status: str,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Update job status.
        
        Args:
            job_id: Job ID
            status: New status
            metadata: Optional status metadata
        """
        status_data = {
            "job_id": job_id,
            "status": status,
            "updated_at": datetime.utcnow().isoformat(),
        }
        
        if metadata:
            status_data.update(metadata)
        
        status_key = f"job_status:{job_id}"
        self.redis_client.setex(
            status_key,
            86400,  # 24 hour TTL
            json.dumps(status_data),
        )
        
        logger.debug(f"Job status updated: {job_id}, status={status}")
    
    def get_queue_length(self) -> int:
        """
        Get current queue length.
        
        Returns:
            Number of jobs in queue
        """
        return self.redis_client.zcard("job_queue")

