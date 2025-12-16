"""
Video ingestion API endpoints.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from pathlib import Path

from app.core.database import get_db
from gateway.middleware.auth import get_current_user
from gateway.middleware.rbac import require_role
from models.db.user import User
from models.enums import UserRole
from domain.cameras.service import CameraService
from ingestion.service import IngestionService
from ingestion.validator import VideoValidator
from observability.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/ingestion", tags=["ingestion"])


@router.post("/upload")
async def upload_video(
    file: UploadFile = File(...),
    camera_id: int = Form(...),
    job_id: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Upload video file for processing.
    Requires: Supervisor or Admin role.
    """
    require_role(current_user, [UserRole.SUPERVISOR, UserRole.ADMIN])
    
    # Verify camera exists
    camera_service = CameraService(db)
    camera = camera_service.get_camera(camera_id)
    if not camera:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Camera not found")
    
    # Initialize ingestion service
    ingestion_service = IngestionService(db)
    
    try:
        # Handle file upload and create chunks
        file_path, chunks = await ingestion_service.handle_file_upload(
            file=file,
            camera_id=camera_id,
            job_id=job_id,
        )
        
        # Create processing job for each chunk
        from orchestration.orchestrator import JobOrchestrator
        orchestrator = JobOrchestrator()
        
        job_ids = []
        for chunk_path, chunk_metadata in chunks:
            job_id = orchestrator.create_job(
                camera_id=camera_id,
                source_type="file",
                source_path=str(chunk_path),
                job_metadata={
                    "chunk_index": chunk_metadata["chunk_index"],
                    "original_file": file_path.name,
                    **chunk_metadata,
                },
            )
            job_ids.append(job_id)
        
        logger.info(
            f"Video uploaded: {file_path.name}, camera_id={camera_id}, "
            f"chunks={len(chunks)}, jobs={len(job_ids)}"
        )
        
        return {
            "message": "Video uploaded and processing jobs created",
            "file_path": str(file_path),
            "chunks": len(chunks),
            "job_ids": job_ids,
        }
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error uploading video: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload video",
        )


@router.post("/cameras/{camera_id}/test-stream")
def test_stream_connection(
    camera_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Test connection to camera stream.
    Requires: Supervisor or Admin role.
    """
    require_role(current_user, [UserRole.SUPERVISOR, UserRole.ADMIN])
    
    # Get camera
    camera_service = CameraService(db)
    camera = camera_service.get_camera(camera_id)
    if not camera:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Camera not found")
    
    # Test stream connection
    ingestion_service = IngestionService(db)
    is_connected, error_msg, stream_info = ingestion_service.test_stream_connection(camera)
    
    if not is_connected:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg or "Failed to connect to stream",
        )
    
    return {
        "connected": True,
        "stream_info": stream_info,
    }


@router.post("/cameras/{camera_id}/start-stream")
def start_stream_processing(
    camera_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Start processing stream from camera.
    Requires: Supervisor or Admin role.
    """
    require_role(current_user, [UserRole.SUPERVISOR, UserRole.ADMIN])
    
    # Get camera
    camera_service = CameraService(db)
    camera = camera_service.get_camera(camera_id)
    if not camera:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Camera not found")
    
    # Validate stream
    ingestion_service = IngestionService(db)
    is_valid, error_msg = ingestion_service.validate_camera_stream(camera)
    if not is_valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_msg)
    
    # Create processing job
    from orchestration.orchestrator import JobOrchestrator
    orchestrator = JobOrchestrator()
    
    job_id = orchestrator.create_job(
        camera_id=camera_id,
        source_type="stream",
        source_path=camera.stream_url,
        job_metadata={
            "stream_type": camera.stream_type,
        },
        priority=1,  # Streams have higher priority
    )
    
    logger.info(f"Stream processing job created: job_id={job_id}, camera_id={camera_id}")
    
    return {
        "message": "Stream processing job created",
        "job_id": job_id,
        "camera_id": camera_id,
    }

