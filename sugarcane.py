import torch
import torchvision.transforms as transforms
from torchvision.models import resnet50
from torchvision.models import ResNet50_Weights
from PIL import Image
import torch.nn.functional as F

# -------- Device --------
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# -------- Load Model --------
model = resnet50(weights=None)
model.fc = torch.nn.Linear(model.fc.in_features, 5)
model.load_state_dict(torch.load("sugarcane_resnet50.pth", map_location=device))
model.to(device)
model.eval()

# -------- Class Names (IMPORTANT: same order as training) --------
class_names = ['Healthy', 'Mosaic', 'RedRot', 'Rust', 'Yellow']
# -------- Image Transform --------
transform = transforms.Compose([
    transforms.Resize((224,224)),
    transforms.ToTensor(),
])

# -------- Load Image --------
image_path ="pd.jpg"   # Put your test image here
image = Image.open(image_path).convert("RGB")
image = transform(image).unsqueeze(0).to(device)

# -------- Prediction --------
with torch.no_grad():
    outputs = model(image)
    probs = F.softmax(outputs, dim=1)
    confidence, predicted = torch.max(probs, 1)

confidence = confidence.item()
predicted_class = class_names[predicted.item()]

if confidence < 0.55:
    print("Prediction: Unknown / Not Sugarcane")
    print("Confidence:", confidence)
else:
    print("Prediction:", predicted_class)
    print("Confidence:", round(confidence * 100, 2), "%")