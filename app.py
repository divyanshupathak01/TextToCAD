import streamlit as st
import os
import subprocess
import re
import requests
from streamlit_lottie import st_lottie
# Using the updated import
from langchain_community.llms import Ollama

# --- 1. CONFIGURATION ---
# UPDATE THIS PATH TO MATCH YOUR COMPUTER EXACTLY
FREECAD_PYTHON_PATH = r"C:\Program Files\FreeCAD 1.0\bin\python.exe"

MODEL_NAME = "codellama"
OUTPUT_FILE = "final_output.step"
OUTPUT_STL = "final_output.stl"

# --- 2. PAGE CONFIGURATION ---
st.set_page_config(page_title="Text-to-CAD AI", page_icon="⚙️", layout="wide")

# --- 3. ANIMATION LOADER (Safe Mode) ---
def load_lottieurl(url: str):
    try:
        r = requests.get(url, timeout=3)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

# Load Assets (With Fallbacks)
lottie_ai_brain = load_lottieurl("https://lottie.host/02d153c3-8182-41d9-8805-b9cb4525ebda/uG3xK6Fp48.json")
lottie_success = load_lottieurl("https://lottie.host/6e174415-467a-4043-a60d-77119e530630/8z6W5eA24c.json")
lottie_coding = load_lottieurl("https://lottie.host/933d735f-331d-4876-8806-03f443585806/186k9z1w52.json")

# --- 4. CUSTOM CSS STYLING ---
st.markdown("""
<style>
    @keyframes pulse {
        0% { color: #ffffff; }
        50% { color: #00e5ff; }
        100% { color: #ffffff; }
    }
    .main-title {
        font-size: 3em;
        font-weight: bold;
        animation: pulse 3s infinite;
        text-align: center;
        margin-bottom: 20px;
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background-color: #ff4b4b;
        color: white;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# --- 5. CORE FUNCTIONS ---

def get_ai_code(prompt):
    """
    Sends the user prompt to Ollama with strict engineering rules.
    """
    llm = Ollama(model=MODEL_NAME)
    
    system_instruction = """
    You are an expert FreeCAD Python scripter.
    Your task is to write a FLAT Python script (NO FUNCTIONS) to create the 3D object described.
    
    CRITICAL SYNTAX RULES:
    1. import FreeCAD, Part, Mesh
    2. doc = FreeCAD.newDocument("Generated")
    3. Use PARAMETRIC objects ONLY.
       - Correct: obj = doc.addObject("Part::Box", "MyBox")
       - Correct: obj = doc.addObject("Part::Cylinder", "MyCyl")
       
    4. USE CORRECT ATTRIBUTES (DO NOT GUESS):
       - For Box: obj.Length, obj.Width, obj.Height
       - For Cylinder: obj.Radius, obj.Height (NOT Length!)
       - For Sphere: obj.Radius
       - For Cone: obj.Radius1, obj.Radius2, obj.Height
       
    5. PLACEMENT logic:
       - To move up: obj.Placement.Base = FreeCAD.Vector(0,0,100)
       
    6. End with: doc.recompute()
    7. OUTPUT FORMAT: Write ONLY valid Python code. No English explanations.
    """
    
    full_prompt = f"{system_instruction}\n\nUSER REQUEST: {prompt}"
    return llm.invoke(full_prompt)
def clean_code(raw_response):
    """
    Cleans up the AI response to ensure only executable Python remains.
    Removes Markdown, English explanations, and dangerous keywords.
    """
    # 1. Extract code blocks if they exist (```python ... ```)
    if "```python" in raw_response:
        parts = raw_response.split("```python")
        if len(parts) > 1:
            raw_response = parts[1].split("```")[0]
    elif "```" in raw_response:
        parts = raw_response.split("```")
        if len(parts) > 1:
            raw_response = parts[1]

    # 2. Filter line by line
    lines = raw_response.split('\n')
    final_lines = []
    
    for line in lines:
        stripped = line.strip()
        
        # Skip empty lines
        if not stripped:
            continue
            
        # Skip conversational lines (The "Chatter" filter)
        # If a line starts with a word like "Here", "This", "The", it's likely English, not Code.
        # But we must preserve code lines like 'import', 'doc', 'obj'
        if not stripped.startswith(("#", "import", "from", "doc", "obj", "Part", "App", "FreeCAD", "Gui", "Mesh")):
            # If it doesn't contain an equals sign or parenthesis, it's probably text
            if "=" not in stripped and "(" not in stripped:
                continue

        # Skip dangerous keywords
        if stripped.startswith(("return ", "def ", "class ", "if __name__")):
            continue
            
        final_lines.append(line)
        
    return "\n".join(final_lines).strip()

def run_freecad(code):
    """
    Saves the code to a file and executes it using the FreeCAD Python Engine.
    """
    script_filename = "temp_web_gen.py"
    
    # We manually force the imports at the top to prevent NameErrors
    with open(script_filename, "w") as f:
        # --- FORCE IMPORTS ---
        f.write("import FreeCAD, Part, Mesh\n")
        f.write("import FreeCAD as App\n\n")
        
        # Write the AI's code (skipping its own import lines to avoid duplicates)
        for line in code.split('\n'):
            if "import FreeCAD" not in line:
                f.write(line + "\n")

        # --- APPEND EXPORT LOGIC ---
        f.write("\n\n# --- EXPORT LOGIC ---\n")
        f.write("try:\n")
        f.write("    objs = App.ActiveDocument.Objects\n")
        f.write("    if len(objs) > 0:\n")
        # Use absolute paths for safety
        f.write(f"        Part.export(objs, r'{os.path.join(os.getcwd(), OUTPUT_FILE)}')\n")
        f.write(f"        Mesh.export(objs, r'{os.path.join(os.getcwd(), OUTPUT_STL)}')\n")
        f.write("        print('SUCCESS')\n")
        f.write("    else:\n")
        f.write("        print('ERROR: No objects created')\n")
        f.write("except Exception as e:\n")
        f.write("    print(f'Export Error: {e}')\n")

    # Execute the script headless
    result = subprocess.run(
        [FREECAD_PYTHON_PATH, script_filename], 
        capture_output=True, text=True
    )
    return result.stdout, result.stderr

# --- 6. UI LAYOUT ---

st.markdown('<p class="main-title">⚙️ Generative AI CAD Engine</p>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("System Status")
    
    if lottie_coding:
        st_lottie(lottie_coding, height=150, key="sidebar_anim")
    else:
        st.info("🤖 System Active")
    
    if os.path.exists(FREECAD_PYTHON_PATH):
        st.success("✅ FreeCAD Engine Ready")
    else:
        st.error("❌ FreeCAD Not Found")
    
    try:
        # Quick check if Ollama is responsive
        llm = Ollama(model=MODEL_NAME)
        st.success(f"✅ Model: {MODEL_NAME}")
    except:
        st.warning("⚠️ AI Offline (Check Ollama)")

# Main Columns
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. Describe Object")
    prompt = st.text_area("Enter prompt:", "Create a hammer. It should have a wooden handle that is a cylinder with radius 10 and length 200. It should have a steel head that is a box with length 80, width 40, and height 40, placed at the top of the handle.", height=150)
    generate_btn = st.button("🚀 Generate 3D Model")

with col2:
    st.subheader("2. Visual Output")
    result_container = st.empty()

# --- 7. MAIN EXECUTION LOOP ---
if generate_btn:
    with col2:
        # Show Loading Animation
        with st.spinner("🧠 AI is engineering the geometry..."):
            if lottie_ai_brain:
                st_lottie(lottie_ai_brain, height=200, key="loading_anim")
            
            # 1. Generate
            raw_code = get_ai_code(prompt)
            
            # 2. Clean
            final_code = clean_code(raw_code)
            
            # 3. Execute
            out, err = run_freecad(final_code)
            
            # Clear animation
            result_container.empty()

    # Display Results
    if "SUCCESS" in out:
        with col2:
            if lottie_success:
                st_lottie(lottie_success, height=150, key="success_anim")
            else:
                st.success("✅ Done!")
            
            st.success("Generation Complete!")
            
            # Download Button
            if os.path.exists(OUTPUT_FILE):
                with open(OUTPUT_FILE, "rb") as file:
                    st.download_button(
                        label="📥 Download STEP File (Professional)",
                        data=file,
                        file_name="ai_model.step",
                        mime="application/octet-stream"
                    )
            else:
                st.error("File creation failed.")
        
        # Show Debug Code
        with st.expander("View Python Script"):
            st.code(final_code, language='python')
            
    else:
        st.error("⚠️ Generation Failed")
        st.text("FreeCAD Error Log:")
        st.code(err)