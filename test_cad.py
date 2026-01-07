import sys
import os

# --- 1. CONFIGURATION (FIXED) ---
# We use r"..." so Python ignores the backslashes.
FREECADPATH = r"C:\Program Files\FreeCAD 1.0\bin"

print(f"Checking path: {FREECADPATH}")

# Verify the folder actually exists
if not os.path.exists(FREECADPATH):
    print("CRITICAL ERROR: The path does not exist on your computer.")
    sys.exit(1)

# --- 2. SETUP PATHS ---
sys.path.append(FREECADPATH)

# --- 3. WINDOWS PERMISSION FIX (CRUCIAL FOR PYTHON 3.10+) ---
# This line allows Python to load the FreeCAD .dll files
if sys.platform == "win32":
    try:
        os.add_dll_directory(FREECADPATH)
    except AttributeError:
        pass # Older python versions don't need this

# --- 4. IMPORT FREECAD ---
try:
    import FreeCAD
    import Part
    print("\n---------------------------------------------------")
    print("SUCCESS! FreeCAD is successfully connected to Python.")
    print("---------------------------------------------------\n")
except ImportError as e:
    print("\n---------------------------------------------------")
    print("IMPORT FAILED.")
    print(f"Error Message: {e}")
    print("---------------------------------------------------")
    print("Tip: If the error says 'DLL load failed', it usually means")
    print("FreeCAD's 'bin' folder is missing some .dll files or")
    print("your Python version is incompatible.")
    sys.exit(1)

# --- 5. CREATE A TEST FILE ---
def create_test_part():
    print("Creating a test cube...")
    doc = FreeCAD.newDocument("TestDoc")
    box = doc.addObject("Part::Box", "TestBox")
    box.Length = 50
    box.Width = 50
    box.Height = 50
    doc.recompute()
    
    # Save directly to your project folder
    output_path = os.path.join(os.getcwd(), "test_cube.step")
    Part.export([box], output_path)
    print(f"File saved at: {output_path}")

if __name__ == "__main__":
    create_test_part()