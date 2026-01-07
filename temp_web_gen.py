import FreeCAD, Part, Mesh
import FreeCAD as App

doc = FreeCAD.newDocument("Generated")
# Create the wooden handle as a cylinder
handle = doc.addObject("Part::Cylinder", "Handle")
handle.Radius = 10
handle.Height = 200
# Move the handle up by 100mm
handle.Placement.Base = FreeCAD.Vector(0, 0, 100)
# Create the steel head as a box
head = doc.addObject("Part::Box", "Head")
head.Length = 80
head.Width = 40
head.Height = 40
# Place the head on top of the handle
head.Placement.Base = FreeCAD.Vector(0, 0, 200)
doc.recompute()


# --- EXPORT LOGIC ---
try:
    objs = App.ActiveDocument.Objects
    if len(objs) > 0:
        Part.export(objs, r'C:\Users\divya\OneDrive\Desktop\TextToCAD\final_output.step')
        Mesh.export(objs, r'C:\Users\divya\OneDrive\Desktop\TextToCAD\final_output.stl')
        print('SUCCESS')
    else:
        print('ERROR: No objects created')
except Exception as e:
    print(f'Export Error: {e}')
