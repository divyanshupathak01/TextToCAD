import FreeCAD, Part

doc = FreeCAD.newDocument("Generated")
obj = doc.addObject("Part::Cylinder", "MyCylinder")
obj.Radius = 20
obj.Height = 100
doc.recompute()

# --- EXPORT LOGIC ---
try:
    import Part
    # Export all objects in the document
    objs = App.ActiveDocument.Objects
    if len(objs) > 0:
        Part.export(objs, 'final_output.step')
        print('SUCCESS: Exported to final_output.step')
    else:
        print('ERROR: Script ran but created no objects.')
except Exception as e:
    print(f'Export Error: {e}')
