# Shell Generator

![shell-thumb](https://github.com/user-attachments/assets/7d064310-d5ea-4728-9367-507c03d053b5)

**Author:** The French Monkey (TFMSTYLE)  
**Version:** 1.0.0  

---

## Overview

The Shell Generator procedurally creates natural, spiral shell geometries based on **Raup’s logarithmic shell model**.  
It simulates realistic growth patterns found in mollusk shells using exponential and helical equations that define curvature, aperture shape, and growth rate.  
Includes features for surface ornamentation, aperture twist, and geometric refinement—ideal for modeling marine shells, fossils, or stylized organic forms.

---

## Parameters

### Live Update
When enabled, automatically rebuilds the shell as parameters are modified.  
Useful for interactive modeling and real-time visualization.

---

### Turns
Defines the total number of spiral revolutions generated.  
Higher values create longer, more tightly coiled shells.

---

### Steps per Turn
Controls the resolution of each revolution.  
Increasing this value improves smoothness but also raises polygon count.

---

### Base Radius r₀
Sets the initial radius of the first spiral coil.  
Smaller values produce tighter, more compact shells.

---

### Radial Growth a
Controls the exponential radial expansion per revolution.  
Higher values make the shell widen outward more quickly.

---

### Vertical Rate b
Specifies the vertical (axial) rise per radian of rotation.  
Adjusts how steeply the shell extends along its central axis.

---

### Aperture A (N-axis)
Defines the horizontal radius of the shell’s aperture cross-section along the local **N-axis**.  
Affects overall shell width.

---

### Aperture B (B-axis)
Defines the vertical radius of the aperture cross-section along the **B-axis**.  
Affects the shell’s height at each revolution.

---

### Flare (elongate A)
Scales the aperture’s **A-axis** over successive turns, controlling elongation and opening of the shell mouth.  
Higher values produce wider, flaring shells.

---

### Aperture Twist (°/turn)
Applies a rotational twist to the aperture per revolution.  
Creates spiraling openings or tilted shell mouths.

---

### Aperture Segments
Sets the number of vertices used to define the aperture perimeter.  
Higher values yield smoother cross-sections.

---

### Rib Amplitude
Controls the height of periodic surface ridges (ribs) along the spiral path.  
Used to mimic natural ribbing patterns.

---

### Rib Frequency (per turn)
Specifies how many ribs appear per full revolution.  
Higher values produce more densely packed ridges.

---

### Smooth Shading
Toggles smooth shading for the generated mesh.  
When enabled, produces a polished and continuous surface appearance.

---

## Operators

### Generate Shell
Creates a new shell based on the selected parameters or updates the currently selected one if generated previously.  
Automatically applies smooth shading and a default shell material.

---

### Reset Settings
Restores all parameters to their default values, preserving the current **Live Update** state.  
Useful for starting fresh with new shell variations.

---

## Usage Notes

- Adjust **Turns** and **Radial Growth** to balance shell compactness and openness.  
- Use **Vertical Rate** to create tall or flat spiral shapes.  
- Combine **Flare** and **Aperture Twist** for expressive, organic shell forms.  
- Enable **Ribs** for decorative or naturalistic detailing.  
- **Smooth Shading** enhances realism when rendering.  
- Generated shells are parametric and optimized for further subdivision, texturing, or 3D printing workflows.
