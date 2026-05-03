<<<<<<< HEAD
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
# TRANSFORM
# -----------------------------
transform = transforms.Compose([
    transforms.Resize((224,224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                        std=[0.229, 0.224, 0.225])
])

# -----------------------------
# TEMPORAL SMOOTHING BUFFER
# -----------------------------
buffer = []
BUFFER_SIZE = 10   # increase for more stability

# -----------------------------
# VIDEO CAPTURE
# -----------------------------
cap = cv2.VideoCapture(0)

frame_count = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_count += 1

    # -------- Frame Skipping (improves FPS) --------
    if frame_count % 2 != 0:
        continue

    # -----------------------------
    # IMAGE PREPROCESSING
    # -----------------------------

    # Convert to RGB
    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img_pil = transforms.ToPILImage()(img_rgb)
    img_tensor = transform(img_pil).unsqueeze(0).to(device)

    # -----------------------------
    # MODEL INFERENCE
    # -----------------------------
    with torch.no_grad():
        outputs = model(img_tensor)
        probs = F.softmax(outputs, dim=1)

    buffer.append(probs.cpu().numpy())

    if len(buffer) > 10:
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
    # DISPLAY RESULT
    # -----------------------------
    cv2.putText(frame,
                f"{label} ({confidence*100:.1f}%)",
                (20,40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0,255,0),
                2)

    cv2.imshow("Sugarcane Disease Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
=======
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
# TRANSFORM
# -----------------------------
transform = transforms.Compose([
    transforms.Resize((224,224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                        std=[0.229, 0.224, 0.225])
])

# -----------------------------
# TEMPORAL SMOOTHING BUFFER
# -----------------------------
buffer = []
BUFFER_SIZE = 10   # increase for more stability

# -----------------------------
# VIDEO CAPTURE
# -----------------------------
cap = cv2.VideoCapture(0)

frame_count = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_count += 1

    # -------- Frame Skipping (improves FPS) --------
    if frame_count % 2 != 0:
        continue

    # -----------------------------
    # IMAGE PREPROCESSING
    # -----------------------------

    # Convert to RGB
    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img_pil = transforms.ToPILImage()(img_rgb)
    img_tensor = transform(img_pil).unsqueeze(0).to(device)

    # -----------------------------
    # MODEL INFERENCE
    # -----------------------------
    with torch.no_grad():
        outputs = model(img_tensor)
        probs = F.softmax(outputs, dim=1)

    buffer.append(probs.cpu().numpy())

    if len(buffer) > 10:
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
    # DISPLAY RESULT
    # -----------------------------
    cv2.putText(frame,
                f"{label} ({confidence*100:.1f}%)",
                (20,40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0,255,0),
                2)

    cv2.imshow("Sugarcane Disease Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
>>>>>>> 02bf4c63654402b04d168b6fc7afd8d4908f6094
cv2.destroyAllWindows()