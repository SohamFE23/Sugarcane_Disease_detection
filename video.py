import cv2
import torch
import torch.nn.functional as F
import torchvision.transforms as transforms
from torchvision.models import resnet50
import numpy as np

# -----------------------------
# DEVICE
# -----------------------------
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Using device:", device)

# -----------------------------
# LOAD MODEL
# -----------------------------
model = resnet50(weights=None)
model.fc = torch.nn.Linear(model.fc.in_features, 5)
model.load_state_dict(torch.load("sugarcane_resnet50.pth", map_location=device))
model.to(device)
model.eval()

class_names = ['Healthy', 'Mosaic', 'RedRot', 'Rust', 'Yellow']

# -----------------------------
# TRANSFORM (MATCH TRAINING)
# -----------------------------
transform = transforms.Compose([
    transforms.Resize((224,224)),
    transforms.ToTensor(),
])

# -----------------------------
# TEMPORAL SMOOTHING
# -----------------------------
buffer = []
BUFFER_SIZE = 8

# -----------------------------
# VIDEO SOURCE
# -----------------------------
# For webcam use 0
# For video file use: "video.mp4"
video_source = "vi.mp4"
cap = cv2.VideoCapture(video_source)

frame_count = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_count += 1

    # Optional: process every 2nd frame (improves speed)
    if frame_count % 2 != 0:
        continue

    # Convert BGR → RGB
    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Convert to PIL and tensor
    img_pil = transforms.ToPILImage()(img_rgb)
    img_tensor = transform(img_pil).unsqueeze(0).to(device)

    # -----------------------------
    # MODEL INFERENCE
    # -----------------------------
    with torch.no_grad():
        outputs = model(img_tensor)
        probs = F.softmax(outputs, dim=1)

    # -----------------------------
    # TEMPORAL SMOOTHING
    # -----------------------------
    buffer.append(probs.cpu().numpy())

    if len(buffer) > BUFFER_SIZE:
        buffer.pop(0)

    avg_probs = np.mean(buffer, axis=0)

    confidence = np.max(avg_probs)
    predicted = np.argmax(avg_probs)

    # -----------------------------
    # CONFIDENCE THRESHOLD
    # -----------------------------
    if confidence < 0.55:
        label = "Unknown"
    else:
        label = class_names[predicted]

    # -----------------------------
    # DISPLAY
    # -----------------------------
    cv2.putText(frame,
                f"{label} ({confidence*100:.1f}%)",
                (20,40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0,255,0),
                2)

    cv2.imshow("Sugarcane Disease Detection - Video", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()