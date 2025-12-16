"""
YOLO11 inference engine for object detection.
"""
from pathlib import Path
from typing import List, Dict, Any, Optional
import torch
import numpy as np
from ultralytics import YOLO

from app.core.config import settings
from observability.logging import get_logger

logger = get_logger(__name__)


class YOLO11Engine:
    """
    YOLO11 inference engine wrapper.
    
    Handles model loading, inference, and result processing.
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize YOLO11 engine.
        
        Args:
            model_path: Path to YOLO11 model file. If None, uses settings.YOLO_MODEL_PATH
        """
        self.model_path = model_path or settings.YOLO_MODEL_PATH
        self.model: Optional[YOLO] = None
        self.device = self._get_device()
        self.confidence_threshold = settings.YOLO_CONFIDENCE_THRESHOLD
        self.iou_threshold = settings.YOLO_IOU_THRESHOLD
        
        logger.info(
            "initializing_yolo11_engine",
            model_path=self.model_path,
            device=self.device,
            confidence_threshold=self.confidence_threshold,
        )
    
    def _get_device(self) -> str:
        """
        Get the best available device (CUDA GPU or CPU).
        
        Returns:
            Device string ('cuda' or 'cpu')
        """
        if torch.cuda.is_available():
            device_id = settings.CUDA_VISIBLE_DEVICES.split(",")[0] if settings.CUDA_VISIBLE_DEVICES else "0"
            return f"cuda:{device_id}"
        return "cpu"
    
    def load_model(self) -> None:
        """
        Load YOLO11 model.
        
        Raises:
            FileNotFoundError: If model file doesn't exist
            RuntimeError: If model loading fails
        """
        model_file = Path(self.model_path)
        
        if not model_file.exists():
            # Try to download if it's a standard YOLO11 model name
            if self.model_path.startswith("yolo11"):
                logger.info("downloading_yolo11_model", model=self.model_path)
                self.model = YOLO(self.model_path)
            else:
                raise FileNotFoundError(f"Model file not found: {self.model_path}")
        else:
            logger.info("loading_yolo11_model", path=str(model_file))
            self.model = YOLO(str(model_file))
        
        # Move model to device
        if self.device.startswith("cuda"):
            logger.info("using_gpu", device=self.device)
        else:
            logger.warning("using_cpu", note="GPU not available, using CPU (slower)")
    
    def detect(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """
        Perform object detection on a single frame.
        
        Args:
            frame: Input frame as numpy array (BGR format from OpenCV)
            
        Returns:
            List of detection dictionaries with keys:
            - class_id: Class ID
            - class_name: Class name
            - confidence: Confidence score
            - bbox: Bounding box [x1, y1, x2, y2]
            - center: Center point [x, y]
        """
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        # Run inference
        results = self.model.predict(
            frame,
            conf=self.confidence_threshold,
            iou=self.iou_threshold,
            device=self.device,
            verbose=False,
        )
        
        detections = []
        
        if results and len(results) > 0:
            result = results[0]
            
            # Extract detections
            if result.boxes is not None:
                boxes = result.boxes
                
                for i in range(len(boxes)):
                    # Get box coordinates
                    box = boxes.xyxy[i].cpu().numpy()
                    x1, y1, x2, y2 = box
                    
                    # Get class and confidence
                    cls_id = int(boxes.cls[i].cpu().numpy())
                    conf = float(boxes.conf[i].cpu().numpy())
                    cls_name = result.names[cls_id]
                    
                    # Calculate center
                    center_x = (x1 + x2) / 2
                    center_y = (y1 + y2) / 2
                    
                    detection = {
                        "class_id": cls_id,
                        "class_name": cls_name,
                        "confidence": conf,
                        "bbox": [float(x1), float(y1), float(x2), float(y2)],
                        "center": [float(center_x), float(center_y)],
                    }
                    
                    detections.append(detection)
        
        return detections
    
    def detect_batch(self, frames: List[np.ndarray]) -> List[List[Dict[str, Any]]]:
        """
        Perform batch object detection on multiple frames.
        
        Args:
            frames: List of input frames as numpy arrays
            
        Returns:
            List of detection lists (one per frame)
        """
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        all_detections = []
        
        for frame in frames:
            detections = self.detect(frame)
            all_detections.append(detections)
        
        return all_detections
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the loaded model.
        
        Returns:
            Dictionary with model information
        """
        if self.model is None:
            return {"loaded": False}
        
        return {
            "loaded": True,
            "model_path": self.model_path,
            "device": self.device,
            "confidence_threshold": self.confidence_threshold,
            "iou_threshold": self.iou_threshold,
            "num_classes": len(self.model.names) if hasattr(self.model, "names") else 0,
        }

