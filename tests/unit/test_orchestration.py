"""
Unit tests for orchestration components.
"""
import sys
from pathlib import Path
import pytest
from unittest.mock import Mock, patch, MagicMock

# Add backend to path
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from orchestration.gpu_manager import GPUManager
from orchestration.job_queue import JobQueue
from orchestration.orchestrator import JobOrchestrator


def test_gpu_manager_initialization():
    """Test GPU manager initialization."""
    # Test without pynvml (most common case)
    with patch('orchestration.gpu_manager.PYNVML_AVAILABLE', False):
        manager = GPUManager()
        assert manager is not None
        assert not manager.initialized


def test_gpu_manager_without_nvml():
    """Test GPU manager without pynvml."""
    with patch('orchestration.gpu_manager.PYNVML_AVAILABLE', False):
        manager = GPUManager()
        assert manager is not None
        assert not manager.initialized


@patch('orchestration.job_queue.redis.Redis')
def test_job_queue_enqueue(mock_redis_class):
    """Test job queue enqueue."""
    mock_redis = MagicMock()
    mock_redis_class.return_value = mock_redis
    mock_redis.ping.return_value = True
    mock_redis.zadd.return_value = None
    
    queue = JobQueue()
    job_id = queue.enqueue_job("test_job", {"data": "test"}, priority=1)
    
    assert job_id is not None
    assert len(job_id) > 0
    mock_redis.zadd.assert_called_once()


@patch('orchestration.job_queue.redis.Redis')
def test_job_queue_dequeue(mock_redis_class):
    """Test job queue dequeue."""
    mock_redis = MagicMock()
    mock_redis_class.return_value = mock_redis
    mock_redis.ping.return_value = True
    
    import json
    test_job = {"id": "test_id", "type": "test", "data": {}}
    mock_redis.zrevrange.return_value = [json.dumps(test_job)]
    mock_redis.zrem.return_value = 1
    
    queue = JobQueue()
    job = queue.dequeue_job()
    
    assert job is not None
    assert job["id"] == "test_id"


@patch('orchestration.orchestrator.GPUManager')
@patch('orchestration.orchestrator.JobQueue')
def test_orchestrator_create_job(mock_queue_class, mock_gpu_class):
    """Test orchestrator job creation."""
    mock_queue = MagicMock()
    mock_queue_class.return_value = mock_queue
    mock_queue.enqueue_job.return_value = "test_job_id"
    
    mock_gpu = MagicMock()
    mock_gpu_class.return_value = mock_gpu
    
    orchestrator = JobOrchestrator()
    job_id = orchestrator.create_job(
        camera_id=1,
        source_type="file",
        source_path="/test/path.mp4",
    )
    
    assert job_id == "test_job_id"
    mock_queue.enqueue_job.assert_called_once()


@patch('orchestration.orchestrator.GPUManager')
@patch('orchestration.orchestrator.JobQueue')
def test_orchestrator_assign_job(mock_queue_class, mock_gpu_class):
    """Test orchestrator job assignment."""
    mock_queue = MagicMock()
    mock_queue_class.return_value = mock_queue
    
    mock_gpu = MagicMock()
    mock_gpu.get_available_gpu.return_value = 0
    mock_gpu_class.return_value = mock_gpu
    
    orchestrator = JobOrchestrator()
    orchestrator.active_jobs["test_job"] = {
        "job_id": "test_job",
        "camera_id": 1,
        "status": "pending",
    }
    
    gpu_id = orchestrator.assign_job_to_gpu("test_job")
    
    assert gpu_id == 0
    mock_gpu.mark_gpu_busy.assert_called_once_with(0)

