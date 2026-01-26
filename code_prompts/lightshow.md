You are an expert javascript and WebGL shader programmer with a strong understanding of 3D graphics techniques and creative coding.

# Ray Marching Psychedelic Metaball Simulation

**Goal:**
Create a visually stunning, continuously evolving simulation reminiscent of 1960s psychedelic light shows using HTML WebGL and advanced shader techniques. The core visual element will be organic, merging "metaballs" rendered using ray marching against Signed Distance Functions (SDFs).

**Task:**
Develop a full-screen WebGL application where the fragment shader implements a ray marching algorithm to render a scene composed of multiple, smoothly merging metaballs. These metaballs should move, potentially change size or color, and blend together to create fluid, volumetric, psychedelic patterns.

**Requirements:**
1.  **WebGL Setup:**
    *   Initialize a WebGL context (`webgl` or `webgl2`) on a full-screen canvas.
    *   Compile and link a basic vertex shader (primarily for passing coordinates/setting up the full-screen quad) and a complex fragment shader (where the main logic resides).
    *   Set up necessary uniforms to pass data from JavaScript to the shaders (e.g., time, screen resolution, metaball parameters).
    *   Render a simple quad (two triangles) covering the entire canvas so the fragment shader executes for every pixel.
2.  **Ray Marching Implementation (Fragment Shader):**
    *   For each pixel (fragment), cast a ray from a camera position into the 3D scene.
    *   Implement the core ray marching loop: iteratively step the ray forward based on the distance estimated by the scene's SDF.
    *   Stop marching when the ray gets very close to a surface (a "hit") or exceeds a maximum distance/step count.
3.  **SDF Scene Definition (Fragment Shader):**
    *   Define a Signed Distance Function (SDF) for a single sphere. This function takes a 3D point and returns the shortest distance to the sphere's surface (negative if inside).
    *   Represent multiple metaballs using this sphere SDF. Their positions (and potentially radii) will be controlled, likely via uniforms updated from JavaScript.
    *   Implement a **smooth minimum** function (e.g., `smin(a, b, k) = -log(exp(-k*a) + exp(-k*b))/k` or polynomial smooth min) to combine the SDFs of individual metaballs. This is crucial for achieving the characteristic organic merging effect. The combined result represents the SDF for the entire metaball structure.
    *   Use this combined SDF within the ray marching loop to determine the distance to the nearest surface at each step.
4.  **Shading and Coloring (Fragment Shader):**
    *   Determine the final pixel color based on the ray marching result.
    *   If a hit occurred:
        *   Calculate the surface normal (often by sampling the SDF gradient near the hit point).
        *   Implement basic lighting (e.g., using the normal and a light direction) or simply assign color based on which metaball was closest, distance traveled, or position.
        *   Use vibrant, shifting colors drawn from a psychedelic palette (e.g., using time, position, or noise functions to modulate HSL/RGB values).
    *   If no hit occurred (ray reached max distance), output a background color (likely black or very dark).
5.  **Animation and Dynamics (JavaScript & Uniforms):**
    *   Use `requestAnimationFrame` in JavaScript for the main loop.
    *   Update uniforms each frame, especially a `time` uniform.
    *   Use the `time` uniform (and potentially noise functions or trigonometric functions in JS or the shader) to dynamically change the positions, sizes, or even colors of the metaballs over time, creating the swirling, evolving effect.
6.  **Generative & Autonomous:** The simulation should run continuously and generate evolving patterns without user interaction after initialization.

**Visual Goal:**
A full-screen, fluid, 3D-like visualization of glowing, volumetric blobs that smoothly merge and separate. Colors should be vibrant and potentially shift dynamically. The overall effect should be hypnotic, organic, and capture the essence of psychedelic visuals through modern rendering techniques.

**Functional Requirements:**
*   Must use WebGL and implement ray marching in the fragment shader.
*   Must use Signed Distance Functions (SDFs) to define the scene geometry.
*   Must use a smooth minimum function to blend multiple metaball SDFs.
*   Metaballs must appear to move and evolve over time, driven by JS updating shader uniforms.
*   Animation must be smooth (correct delta time concept applied via the `time` uniform).
*   The simulation must run autonomously.

**Desirable Features:**
*   Implement more sophisticated lighting models in the shader (e.g., ambient occlusion approximation, reflections).
*   Use noise functions (like simplex or Perlin noise, potentially implemented within the shader) to add texture to the metaballs or drive more complex movement patterns.
*   Experiment with `globalCompositeOperation` or shader-based blending for post-processing effects if layering multiple passes (though core effect should be raymarched).
*   Allow the number of metaballs or their properties (like the 'k' factor in `smin`) to change over time.
*   Optimize shader performance.

# Deliverable
The simulation must run directly in a modern web browser supporting WebGL. Provide the complete solution within a single HTML file, including JavaScript for WebGL setup/uniform updates and the GLSL code for the vertex and fragment shaders (e.g., within `<script>` tags with types like `x-shader/x-vertex`). No external graphics libraries (like Three.js or Babylon.js) are allowed – direct WebGL API usage only. You may add notes about your implementation approach within HTML comments or a dedicated `<section id="notes">`. 

Remember this should be a visual simulation reminiscent of 1960s psychedelic light shows (think liquid light projections, early Pink Floyd visuals), make it super groovy dude!

```html
<!DOCTYPE html>
<html>
<head>
    <title>Ray Marching Metaballs</title>
    <style>
        body { margin: 0; overflow: hidden; background-color: #000; }
        canvas { display: block; width: 100vw; height: 100vh; }
    </style>
</head>
<body>
    <canvas id="glCanvas"></canvas>

    <script>
        // --- Standard WebGL Boilerplate ---
        const canvas = document.getElementById('glCanvas');
        const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');

        if (!gl) {
            alert('WebGL not supported');
            throw new Error('WebGL not supported');
        }

    </script>

    <!-- Optional section for notes -->
    <!--
    <section id="notes">
        Developer notes regarding SDF combination, ray marching optimizations, lighting/coloring choices, etc.
    </section>
    -->
</body>
</html>
```