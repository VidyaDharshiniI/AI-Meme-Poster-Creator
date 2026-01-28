import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import os, time

st.set_page_config(page_title="MemeCraft Studio", layout="wide")


TEMPLATE_FOLDER = "templates_img"
FONT_FOLDER = "fonts"
OUTPUT_FOLDER = "output"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ---------------- FONTS ----------------
fonts = {
    "Poppins Regular": "Poppins-Regular.ttf",
    "Poppins Bold": "Poppins-Bold.ttf",
    "Poppins Italic": "Poppins-Italic.ttf",

    "Montserrat Regular": "Montserrat-Regular.ttf",
    "Montserrat Bold": "Montserrat-Bold.ttf",
    "Montserrat Italic": "Montserrat-Italic.ttf",

    "Comic Neue Regular": "ComicNeue-Regular.ttf",
    "Comic Neue Bold": "ComicNeue-Bold.ttf",
    "Comic Neue Italic": "ComicNeue-Italic.ttf",

    "Oswald Regular": "Oswald-Regular.ttf",
    "Oswald Bold": "Oswald-Bold.ttf",

    "Playfair Regular": "PlayfairDisplay-Regular.ttf",
    "Playfair Bold": "PlayfairDisplay-Bold.ttf",

    "Lobster": "Lobster-Regular.ttf",
    "Impact": "IMPACTED.ttf"
}

# ---------------- LOAD TEMPLATES ----------------
all_imgs = os.listdir(TEMPLATE_FOLDER)
meme_imgs = [f for f in all_imgs if f.lower().startswith("meme")]
poster_imgs = [f for f in all_imgs if f.lower().startswith("poster")]

# ---------------- SESSION STATE ----------------
if "selected_template" not in st.session_state:
    st.session_state.selected_template = None

if "show_all_memes" not in st.session_state:
    st.session_state.show_all_memes = False

if "show_all_posters" not in st.session_state:
    st.session_state.show_all_posters = False

if "text_layers" not in st.session_state:
    st.session_state.text_layers = []

# ---------------- SIDEBAR ----------------
st.sidebar.title("🛠 Editor Panel")

if st.sidebar.button("➕ Add New Text"):
    st.session_state.text_layers.append({
        "text": "",
        "x": 0,
        "y": 0,
        "size": 40,
        "color": "#ffffff",
        "font": list(fonts.keys())[0],
        "h_align": "Center",
        "v_align": "Center"
    })

st.sidebar.markdown("---")
st.sidebar.subheader("📝 Text Layers")

for i, layer in enumerate(st.session_state.text_layers):
    with st.sidebar.expander(f"Text Layer {i+1}", expanded=True):
        layer["text"] = st.text_input("Text", layer["text"], key=f"text_{i}")

        layer["h_align"] = st.selectbox(
            "Horizontal Align",
            ["Left", "Center", "Right"],
            index=["Left", "Center", "Right"].index(layer["h_align"]),
            key=f"h_align_{i}"
        )

        layer["v_align"] = st.selectbox(
            "Vertical Align",
            ["Top", "Center", "Bottom"],
            index=["Top", "Center", "Bottom"].index(layer["v_align"]),
            key=f"v_align_{i}"
        )

        layer["x"] = st.slider("X Fine Adjustment", -500, 500, layer["x"], key=f"x_{i}")
        layer["y"] = st.slider("Y Fine Adjustment", -500, 500, layer["y"], key=f"y_{i}")

        layer["size"] = st.slider("Font Size", 10, 150, layer["size"], key=f"size_{i}")
        layer["color"] = st.color_picker("Color", layer["color"], key=f"color_{i}")

        layer["font"] = st.selectbox(
            "Font Style",
            list(fonts.keys()),
            index=list(fonts.keys()).index(layer["font"]),
            key=f"font_{i}"
        )

        if st.button("❌ Remove This Text", key=f"remove_{i}"):
            st.session_state.text_layers.pop(i)
            st.experimental_rerun()

# ---------------- UI ----------------
st.title("🎨 MemeCraft Studio")
st.subheader("A Smart Meme & Poster Designing Application")

st.markdown("Select template → Add text → Align → Adjust → Preview → Download")

def show_section(images, title, show_key):
    st.subheader(title)

    display_imgs = images if st.session_state[show_key] else images[:7]
    cols = st.columns(7)

    for i, img_name in enumerate(display_imgs):
        img = Image.open(os.path.join(TEMPLATE_FOLDER, img_name))
        with cols[i % 7]:
            st.image(img, width=120)
            if st.button("Select", key=f"{title}_{img_name}"):
                st.session_state.selected_template = img_name

    if not st.session_state[show_key] and len(images) > 7:
        if st.button("View More", key=f"viewmore_{title}"):
            st.session_state[show_key] = True

# Meme Section
show_section(meme_imgs, "😂 Meme Templates", "show_all_memes")
st.markdown("---")
# Poster Section
show_section(poster_imgs, "📄 Poster Backgrounds", "show_all_posters")
st.markdown("---")

# ---------------- LIVE PREVIEW ----------------
st.header("🖼 Live Preview")

if st.session_state.selected_template:
    base_img = Image.open(
        os.path.join(TEMPLATE_FOLDER, st.session_state.selected_template)
    ).convert("RGB")

    preview = base_img.copy()
    draw = ImageDraw.Draw(preview)

    for layer in st.session_state.text_layers:
        try:
            font_path = os.path.join(FONT_FOLDER, fonts[layer["font"]])
            font = ImageFont.truetype(font_path, layer["size"])
        except:
            font = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), layer["text"], font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]

        # Horizontal alignment
        if layer["h_align"] == "Left":
            x = 20
        elif layer["h_align"] == "Center":
            x = (base_img.width - w) // 2
        else:
            x = base_img.width - w - 20

        # Vertical alignment
        if layer["v_align"] == "Top":
            y = 20
        elif layer["v_align"] == "Center":
            y = (base_img.height - h) // 2
        else:
            y = base_img.height - h - 20

        # Fine adjustment
        x += layer["x"]
        y += layer["y"]

        draw.text((x, y), layer["text"], fill=layer["color"], font=font)

    st.image(preview, width=500)

else:
    st.info("Select a template to start editing.")

# ---------------- EXPORT ----------------
if st.button("🚀 Generate & Download"):
    if not st.session_state.selected_template:
        st.error("Select a template first.")
    else:
        filename = f"output_{int(time.time())}.png"
        path = os.path.join(OUTPUT_FOLDER, filename)
        preview.save(path)

        with open(path, "rb") as f:
            st.download_button(
                "📥 Download Final Image",
                f,
                file_name=filename,
                mime="image/png"
            )
