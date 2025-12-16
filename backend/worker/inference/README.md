# YOLO11 Inference Engine

This module provides the YOLO11 inference engine for object detection in video streams.

## Usage

```python
from worker.inference.yolo_engine import YOLO11Engine
import cv2

# Initialize engine
engine = YOLO11Engine()

# Load model (downloads automatically if not present)
engine.load_model()

# Process a frame
frame = cv2.imread("image.jpg")
detections = engine.detect(frame)

# Process detections
for detection in detections:
    print(f"Found {detection['class_name']} with confidence {detection['confidence']:.2f}")
    print(f"Bounding box: {detection['bbox']}")
```

## Model Options

YOLO11 supports multiple model sizes:
- `yolo11n.pt` - Nano (fastest, least accurate)
- `yolo11s.pt` - Small
- `yolo11m.pt` - Medium
- `yolo11l.pt` - Large
- `yolo11x.pt` - XLarge (slowest, most accurate)

Set `YOLO_MODEL_PATH` in your `.env` file to use a different model.

## Configuration

Configure via environment variables:
- `YOLO_MODEL_PATH`: Path to model file (default: `./models/yolo11n.pt`)
- `YOLO_CONFIDENCE_THRESHOLD`: Confidence threshold (default: 0.25)
- `YOLO_IOU_THRESHOLD`: IoU threshold for NMS (default: 0.45)
- `CUDA_VISIBLE_DEVICES`: GPU device IDs (default: "0")
- `GPU_MEMORY_FRACTION`: GPU memory fraction (default: 0.8)
- `BATCH_SIZE`: Batch size for inference (default: 16)

