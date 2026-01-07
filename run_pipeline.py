import os
import subprocess
import re
# We use the older import to avoid the warning
from langchain_community.llms import Ollama

# --- CONFIGURATION ---
FREECAD_PYTHON_PATH = r"C:\Program Files\FreeCAD 1.0\bin\python.exe"
MODEL_NAME = "codellama"

def get_ai_response(user_prompt):
    print(f"🧠 AI is thinking about: '{user_prompt}'...")
    llm = Ollama(model=MODEL_NAME)
    
    # --- UPDATED SYSTEM PROMPT ---
    system_instruction = """
    You are an expert FreeCAD Python scripter.
    Your task is to write a FLAT Python script (NO FUNCTIONS) to create the 3D object described.
    
    CRITICAL RULES:
    1. Start with: import FreeCAD, Part
    2. Create a document: doc = FreeCAD.newDocument("Generated")
    3. Use PARAMETRIC objects ONLY.
       - Correct: obj = doc.addObject("Part::Box", "MyBox")
       - Correct: obj = doc.addObject("Part::Cylinder", "MyCyl")
    4. Set dimensions directly:
       - obj.Length = 100
       - obj.Radius = 10
    5. ALWAYS end with: doc.recompute()
    6. FORBIDDEN: Do NOT write 'def main():', Do NOT use 'return', Do NOT use 'if __name__'.
    7. Just write the raw commands.
    """
    
    full_prompt = f"{system_instruction}\n\nUSER REQUEST: {user_prompt}"
    return llm.invoke(full_prompt)

def clean_code(raw_response):
    # 1. Remove Markdown
    clean = re.sub(r"```python", "", raw_response)
    clean = re.sub(r"```", "", clean)
    
    # 2. THE FIX: Remove 'return' lines and 'def' lines
    lines = clean.split('\n')
    final_lines = []
    for line in lines:
        stripped = line.strip()
        # Skip lines that cause syntax errors
        if stripped.startswith("return "):
            continue
        if stripped.startswith("def "):
            continue
        final_lines.append(line)
        
    return "\n".join(final_lines).strip()

def save_and_run(code):
    script_filename = "temp_generation.py"
    with open(script_filename, "w") as f:
        f.write(code)
        
        # Append the Safe Export Logic
        f.write("\n\n# --- EXPORT LOGIC ---\n")
        f.write("try:\n")
        f.write("    import Part\n")
        f.write("    # Export all objects in the document\n")
        f.write("    objs = App.ActiveDocument.Objects\n")
        f.write("    if len(objs) > 0:\n")
        f.write("        Part.export(objs, 'final_output.step')\n")
        f.write("        print('SUCCESS: Exported to final_output.step')\n")
        f.write("    else:\n")
        f.write("        print('ERROR: Script ran but created no objects.')\n")
        f.write("except Exception as e:\n")
        f.write("    print(f'Export Error: {e}')\n")

    print(f"💾 Code saved to {script_filename}")
    print("🚀 Sending code to FreeCAD...")
    
    # Run FreeCAD
    result = subprocess.run(
        [FREECAD_PYTHON_PATH, script_filename], 
        capture_output=True, 
        text=True
    )
    
    print("\n--- FREECAD OUTPUT ---")
    print(result.stdout)
    if result.stderr:
        print("Errors/Warnings:")
        print(result.stderr)
    print("----------------------")

if __name__ == "__main__":
    while True:
        user_input = input("\nDescribe what you want to build (or 'q' to quit): ")
        if user_input.lower() == 'q':
            break
            
        raw_code = get_ai_response(user_input)
        final_code = clean_code(raw_code)
        save_and_run(final_code)