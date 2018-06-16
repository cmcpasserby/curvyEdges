curvyEdges
==========

curvyEdges is a script for creating nurbs or bezier curves from edge selections, than using the curves to edit underlying geometry. This script allows for very fast changes of geometry while maintaining smooth curves. The script features a simple UI for creating the curves, and controls for adjusting the falloff distance, scale, and envelope. Multiple curves can be worked on at once since the process is non-destructive up to the point where history gets deleted on the mesh.

![curvyEdges](https://rsggassets.nyc3.digitaloceanspaces.com/assets/images/curvyEdges01.jpg)

Installation
------------
Clone or extract `curvyEdges.py` to your Maya scripts folder and restart maya. 
Once this is done simply open a python console and run these commands.
```
import curvyEdges
curvyEdges.UI()
```
Optionally you could create a shelf button containing the same python code as above.
