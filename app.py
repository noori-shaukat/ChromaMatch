import streamlit as st
import requests
from PIL import Image
import io
import base64

st.set_page_config(
    page_title="ChromaMatch",
    page_icon="🎨",
    layout="centered"
)

# ---------------- BACKGROUND IMAGE FUNCTION ----------------
def add_bg(image_path):
    with open(image_path, "rb") as file:
        encoded = base64.b64encode(file.read()).decode()
    st.markdown(
        f"""
        <style>
        body {{
            background-image: url("data:image/jpg;base64,{encoded}");
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
            font-family: 'Poppins', sans-serif;
        }}
        .stApp {{
            background: transparent;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

add_bg("bg6.jpg")

# ---------------- GLOBAL CSS ---------------- #
st.markdown("""
<style>

/* REMOVE STREAMLIT TOP HEADER */
header {display: none !important;}
.stAppHeader {display: none !important;}
[data-testid="stHeader"] {display: none !important;}

/* Default page text black */
body, div, p, span, h1, h2, h3, h4, h5, h6, label {
    font-size: 20px !important;
    color: #000 !important;
}
/* Exclude Streamlit tooltips so they stay readable */
.stTooltip, .stTooltip * {
    color: #000 !important;
}

/* File uploader text white */
.stFileUploader label,
.stFileUploader div,
.stFileUploader span {
    color: white !important;
}

/* Main container and cards */
.main-container {
    width: 100%;
    max-width: 620px;
    margin: auto;
    text-align: center;
    padding-top: 80px;
}
.card {
    background: #ffffffdd;
    padding: 35px;
    border-radius: 25px;
    box-shadow: 0 20px 45px rgba(0,0,0,0.12);
    margin-bottom: 35px;
}
.title {
    font-size: 38px;
    font-weight: 800;
}
.subtitle {
    font-size: 18px;
    margin-bottom: 28px;
}
.option-btn {
    background: #f7f7f7;
    padding: 12px 25px;
    border-radius: 12px;
    border: 2px solid #ddd;
    font-size: 20px;
    cursor: pointer;
    margin: 8px;
}
.option-btn:hover {
    border-color: #ff5fa4;
}
.upload-box {
    border: 3px dashed #bbb;
    padding: 35px;
    border-radius: 20px;
    background: #fafafaee;
    margin-top: 15px;
    transition: 0.25s;
}
.upload-box:hover {
    border-color: #ff66b3;
}

/* Style Streamlit buttons */
.stButton button {
    background: linear-gradient(135deg, #ff66b3, #ff3e84);
    color: white !important;
    padding: 14px 28px;
    border-radius: 30px;
    border: none;
    font-size: 18px;
    cursor: pointer;
}
.stButton button:hover {
    opacity: 0.92;
    transform: translateY(-2px);
}

.color-box {
    width: 60px;
    height: 60px;
    border-radius: 14px;
    box-shadow: 0 5px 14px rgba(0,0,0,0.22);
    margin: auto;
    display: flex;
    align-items: center;
    justify-content: center;
}
.color-box p {
    color: white !important;
    margin: 0;
    font-size: 20px;
}
.reco-box {
    padding: 12px;
    background: #ff3e84;
    border-radius: 14px;
    margin-bottom: 10px;
    box-shadow: 0 5px 12px rgba(0,0,0,0.1);
    color: white !important;
}
.reco-box * {
    color: white !important;
}

</style>
""", unsafe_allow_html=True)

# ---------------- MAIN UI ----------------
st.markdown("<div class='main-container'>", unsafe_allow_html=True)
st.markdown('<div style="height:240px;"></div>', unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Upload/Take a selfie to analyze your undertone and find your perfect color palette!</div>", unsafe_allow_html=True)

# ---------------- PHOTO INPUT OPTIONS ----------------
choice = st.radio(
    "Choose:",
    ["Upload a Photo", "Take a Photo"],
    horizontal=True
)

photo = None

if choice == "Upload a Photo":
    st.markdown("<div class='upload-box'>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader(" ", type=["jpg","jpeg","png"])
    st.markdown("</div>", unsafe_allow_html=True)
    if uploaded_file:
        photo = Image.open(uploaded_file)
        st.image(photo, width=280)

elif choice == "Take a Photo":
    st.markdown("<div class='upload-box'>", unsafe_allow_html=True)
    camera_file = st.camera_input("Take a picture")
    st.markdown("</div>", unsafe_allow_html=True)
    if camera_file:
        photo = Image.open(camera_file)
        st.image(photo, width=280)

# ---------------- ANALYZE BUTTON ----------------
clicked = st.button(
    "Analyze My Colors",
    key="analyze_btn",
    help="Click to analyze skin tone and get recommendations"
)

# ---------------- OUTPUT ----------------
if clicked and photo:
    img_bytes = io.BytesIO()
    photo.save(img_bytes, format="JPEG")
    img_bytes = img_bytes.getvalue()

    with st.spinner("Analyzing..."):
        try:
            EC2_IP = "http://13.60.180.47:8000"
            analyze_url = f"{EC2_IP}/analyze"
            reco_url = f"{EC2_IP}/recommend"
            ml_response = requests.post(
                analyze_url,
                files={"file": ("image.jpg", img_bytes, "image/jpeg")}
            )

            if ml_response.status_code != 200:
                st.error("Error from /analyze endpoint.")
                st.write(ml_response.text)
            else:
                ml_result = ml_response.json()

                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.markdown("<h2 style='color:#ff3e84;'>Your Skin Analysis</h2>", unsafe_allow_html=True)
                st.json(ml_result)

                reco_payload = {
                    "skin_tone": ml_result.get("skin_tone"),
                    "tone_group": ml_result.get("tone_group"),
                    "descriptor": ml_result.get("descriptor"),
                    "undertone": ml_result.get("undertone"),
                    "eye_color": ml_result.get("eye_color_left", []),
                    "hair_color": ml_result.get("hair_color", "Unknown"),
                }

                reco_response = requests.post(reco_url, json=reco_payload)

                if reco_response.status_code != 200:
                    st.error("Error from /recommend endpoint.")
                    st.write(reco_response.text)
                else:
                    recommendations = reco_response.json()
                    st.markdown("<h2 style='color:#ff3e84;'>✨ Personalized Style Guide</h2>", unsafe_allow_html=True)

                    if "fashion" in recommendations:
                        st.subheader("Fashion Advice")
                        for item in recommendations["fashion"]:
                            st.markdown(f'<div class="reco-box">{item}</div>', unsafe_allow_html=True)

                    if "colors" in recommendations:
                        st.subheader("🎨 Best Colors for You")
                        cols = st.columns(5)
                        for idx, color in enumerate(recommendations["colors"]):
                            with cols[idx % 5]:
                                st.markdown(
                                    f"""
                                    <div class="color-box" style='background:{color}'></div>
                                    <p style='text-align:center;font-size:12px'>{color}</p>
                                    """,
                                    unsafe_allow_html=True
                                )

                    if "makeup" in recommendations:
                        st.subheader("Makeup Recommendations")
                        for item in recommendations["makeup"]:
                            st.markdown(f'<div class="reco-box">{item}</div>', unsafe_allow_html=True)

                    if "hair" in recommendations:
                        st.subheader("Hair Suggestions")
                        for item in recommendations["hair"]:
                            st.markdown(f'<div class="reco-box">{item}</div>', unsafe_allow_html=True)

                st.markdown("</div>", unsafe_allow_html=True)

        except Exception as e:
            st.error("Something went wrong.")
            st.exception(e)

st.markdown("</div>", unsafe_allow_html=True)
