# src/model/chroma_model.py
# Slightly refactored version of your analyze_image function for reuse.
# Exposes analyze_image(image_path) -> dict result.

import torch
from transformers import AutoImageProcessor, AutoModelForSemanticSegmentation
from PIL import Image
import numpy as np
from sklearn.cluster import KMeans
import math

_processor = None
_model = None


def _ensure_model_loaded():
    global _processor, _model
    if _processor is None or _model is None:
        # you can change the HF model name if needed
        _processor = AutoImageProcessor.from_pretrained("jonathandinu/face-parsing")
        _model = AutoModelForSemanticSegmentation.from_pretrained(
            "jonathandinu/face-parsing"
        )
    return _processor, _model


def rgb2lab(rgb):
    rgb = np.array(rgb) / 255.0
    mask = rgb > 0.04045
    rgb[mask] = ((rgb[mask] + 0.055) / 1.055) ** 2.4
    rgb[~mask] /= 12.92
    rgb *= 100

    X = rgb[0] * 0.4124 + rgb[1] * 0.3576 + rgb[2] * 0.1805
    Y = rgb[0] * 0.2126 + rgb[1] * 0.7152 + rgb[2] * 0.0722
    Z = rgb[0] * 0.0193 + rgb[1] * 0.1192 + rgb[2] * 0.9505

    X /= 95.047
    Y /= 100.0
    Z /= 108.883

    def f(t):
        return t ** (1 / 3) if t > 0.008856 else (7.787 * t) + (16 / 116)

    X, Y, Z = f(X), f(Y), f(Z)

    L = (116 * Y) - 16
    a = 500 * (X - Y)
    b = 200 * (Y - Z)
    return np.array([L, a, b])


def ciede2000(lab1, lab2):
    L1, a1, b1 = lab1
    L2, a2, b2 = lab2

    C1 = math.sqrt(a1**2 + b1**2)
    C2 = math.sqrt(a2**2 + b2**2)
    C_bar = (C1 + C2) / 2
    G = 0.5 * (1 - math.sqrt(C_bar**7 / (C_bar**7 + 25**7)))

    a1p = a1 * (1 + G)
    a2p = a2 * (1 + G)
    C1p = math.sqrt(a1p**2 + b1**2)
    C2p = math.sqrt(a2p**2 + b2**2)

    h1p = math.degrees(math.atan2(b1, a1p)) % 360
    h2p = math.degrees(math.atan2(b2, a2p)) % 360

    delta_Lp = L2 - L1
    delta_Cp = C2p - C1p
    dhp = h2p - h1p
    if abs(dhp) > 180:
        dhp -= 360 if dhp > 0 else -360
    delta_Hp = 2 * math.sqrt(C1p * C2p) * math.sin(math.radians(dhp / 2))

    L_bar = (L1 + L2) / 2
    C_bar_p = (C1p + C2p) / 2
    if abs(h1p - h2p) > 180:
        h_bar_p = (h1p + h2p + 360) / 2
    else:
        h_bar_p = (h1p + h2p) / 2

    T = (
        1
        - 0.17 * math.cos(math.radians(h_bar_p - 30))
        + 0.24 * math.cos(math.radians(2 * h_bar_p))
        + 0.32 * math.cos(math.radians(3 * h_bar_p + 6))
        - 0.20 * math.cos(math.radians(4 * h_bar_p - 63))
    )

    SL = 1 + (0.015 * ((L_bar - 50) ** 2)) / math.sqrt(20 + ((L_bar - 50) ** 2))
    SC = 1 + 0.045 * C_bar_p
    SH = 1 + 0.015 * C_bar_p * T

    delta_theta = 30 * math.exp(-(((h_bar_p - 275) / 25) ** 2))
    RC = 2 * math.sqrt((C_bar_p**7) / (C_bar_p**7 + 25**7))
    RT = -math.sin(math.radians(2 * delta_theta)) * RC

    delta_E = math.sqrt(
        (delta_Lp / SL) ** 2
        + (delta_Cp / SC) ** 2
        + (delta_Hp / SH) ** 2
        + RT * (delta_Cp / SC) * (delta_Hp / SH)
    )
    return delta_E


def find_closest_color(lab_color, color_dict):
    min_dist = float("inf")
    closest_name = None
    for name, ref_lab in color_dict.items():
        dist = ciede2000(lab_color, ref_lab)
        if dist < min_dist:
            min_dist = dist
            closest_name = name
    return closest_name


def extract_region_lab(region_mask, image_np, k=2):
    region_pixels = image_np[region_mask]
    if len(region_pixels) == 0:
        return np.array([0, 0, 0])
    region_pixels_lab = np.array([rgb2lab(pixel) for pixel in region_pixels])
    kmeans = KMeans(n_clusters=k, n_init=10, random_state=42)
    kmeans.fit(region_pixels_lab)
    unique, counts = np.unique(kmeans.labels_, return_counts=True)
    dominant_idx = unique[np.argmax(counts)]
    return kmeans.cluster_centers_[dominant_idx]


# MST reference data (unchanged)
monk_lab = {
    1: np.array([94.2884, 1.8519, 5.5425]),
    2: np.array([92.251, 1.9045, 7.7661]),
    3: np.array([93.0112, -0.1348, 14.0799]),
    4: np.array([87.342, 1.1245, 16.8999]),
    5: np.array([77.9011, 3.4755, 23.1345]),
    6: np.array([54.7394, 7.7105, 27.3153]),
    7: np.array([42.6321, 11.4027, 20.1281]),
    8: np.array([30.952, 11.0444, 13.7036]),
    9: np.array([21.0691, 2.6924, 5.9636]),
    10: np.array([14.7252, 1.9748, 3.7045]),
}

mst_details = {
    1: {"group": "Light", "descriptor": "Porcelain / Very Light"},
    2: {"group": "Light", "descriptor": "Ivory / Fair"},
    3: {"group": "Light", "descriptor": "Beige / Light"},
    4: {"group": "Medium", "descriptor": "Sand / Light Medium"},
    5: {"group": "Medium", "descriptor": "Honey / Medium"},
    6: {"group": "Medium", "descriptor": "Caramel / Medium Tan"},
    7: {"group": "Dark", "descriptor": "Chestnut / Tan"},
    8: {"group": "Dark", "descriptor": "Mocha / Deep"},
    9: {"group": "Dark", "descriptor": "Espresso / Dark"},
    10: {"group": "Dark", "descriptor": "Ebony / Very Dark"},
}

iris_colors_rgb = {
    "Dark Blue": (97, 143, 159),
    "Light Blue": (126, 173, 186),
    "Dark Green": (91, 113, 82),
    "Light Green": (141, 140, 106),
    "Dark Hazel": (90, 60, 40),
    "Light Brown (Hazel)": (175, 134, 107),
    "Black": (30, 30, 30),
    "Brown": (70, 40, 20),
    "Gray": (150, 150, 150),
}
iris_lab = {name: rgb2lab(rgb) for name, rgb in iris_colors_rgb.items()}

hair_colors_rgb = {
    "Black": (20, 20, 20),
    "Dark Brown": (60, 40, 30),
    "Brown": (150, 110, 80),
    "Dark Blonde": (178, 128, 65),
    "Blonde": (220, 200, 140),
    "Red": (150, 60, 40),
    "Gray": (160, 160, 160),
}
hair_lab = {name: rgb2lab(rgb) for name, rgb in hair_colors_rgb.items()}


def analyze_image(image_path: str):
    """
    Analyze an image to detect:
    - Closest Monk Skin Tone (MST)
    - Tone group and descriptor
    - Skin undertone (cool, warm, neutral)
    - Eye and hair color
    """
    processor, model = _ensure_model_loaded()

    image = Image.open(image_path).convert("RGB")
    inputs = processor(images=image, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs)

    logits = outputs.logits
    upsampled_logits = torch.nn.functional.interpolate(
        logits, size=image.size[::-1], mode="bilinear", align_corners=False
    )
    pred_seg = upsampled_logits.argmax(dim=1)[0].numpy()
    img_np = np.array(image)

    # Masks
    skin_mask = pred_seg == 1
    left_eye_mask = pred_seg == 4
    right_eye_mask = pred_seg == 5
    hair_mask = pred_seg == 13

    # Extract dominant LAB
    skin_lab = extract_region_lab(skin_mask, img_np)
    left_eye_lab = extract_region_lab(left_eye_mask, img_np)
    right_eye_lab = extract_region_lab(right_eye_mask, img_np)
    hair_lab_val = extract_region_lab(hair_mask, img_np)

    # Closest matches
    skin_level = find_closest_color(skin_lab, monk_lab)
    left_eye_color = find_closest_color(left_eye_lab, iris_lab)
    right_eye_color = find_closest_color(right_eye_lab, iris_lab)
    hair_color = find_closest_color(hair_lab_val, hair_lab)

    # Undertone detection
    L, a, b = skin_lab
    if a > b + 2:
        undertone = "Cool"
    elif b > a + 2:
        undertone = "Warm"
    else:
        undertone = "Neutral"

    tone_info = mst_details.get(skin_level, {})
    return {
        "skin_tone": f"MST {skin_level}",
        "tone_group": tone_info.get("group"),
        "descriptor": tone_info.get("descriptor"),
        "undertone": undertone,
        "eye_color": (
            left_eye_color
            if left_eye_color == right_eye_color
            else (left_eye_color, right_eye_color)
        ),
        "hair_color": hair_color,
    }
