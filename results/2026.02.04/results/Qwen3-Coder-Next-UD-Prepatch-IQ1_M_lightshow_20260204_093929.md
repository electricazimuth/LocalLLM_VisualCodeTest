Here is a complete, self-contained solution. It sets up a full-screen WebGL context, compiles custom shaders, and implements a ray marched metaball engine with organic, psychedelic movement patterns driven by time and smooth minimum functions.

```html
<!DOCTYPE html>
<html>
<head>
    <title>Psychedelic Ray Marching Metaballs</title>
    <style>
        body { 
            margin: 0; 
            overflow: hidden; 
            background-color: #000; 
            color: #eee;
            font-family: monospace;
        }
        canvas { 
            display: block; 
            width: 100vw; 
            height: 100vh; 
        }
        #ui {
            position: absolute;
            top: 10px;
            left: 10px;
            z-index: 10;
            pointer-events: none;
            color: rgba(255,255,255,0.7);
            background: rgba(0,0,0,0.5);
            padding: 10px;
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <div id="ui">
        <h1>Metaball Fluid Dynamics</h1>
        <p>WebGL Ray Marching Simulation</p>
        <p>Rendered using Signed Distance Functions (SDFs)</p>
    </div>
    <canvas id="glCanvas"></canvas>

    <!-- Vertex Shader: Simple Pass-Through -->
    <script id="vertexShader" type="x-shader/x-vertex">
        attribute vec2 position;
        void main() {
            gl_Position = vec4(position, 0.0, 1.0);
        }
    </script>

    <!-- Fragment Shader: The Psychedelic Engine -->
    <script id="fragmentShader" type="x-shader/x-fragment">
        precision highp float;

        uniform vec2 iResolution;
        uniform float iTime;
        uniform float iGlobalTime;

        // ----------------------------------------------------------
        // CONFIGURATION
        // ----------------------------------------------------------
        #define MAX_DIST 100.0
        #define MAX_STEPS 100
        #define FOV 60.0
        #define BOUNDS 4.0

        // ----------------------------------------------------------
        // HASHING / NOISE FUNCTIONS (Purely procedural, no textures)
        // ----------------------------------------------------------
        vec3 hash3(vec3 p) {
            p = fract(p * 0.1031);
            p += dot(p, p.xz + 31.33);
            return fract(p.xzy * (p.x + p.y));
        }

        float noise(vec3 p) {
            vec3 pi = floor(p);
            vec3 pf = fract(p);
            pf = pf * pf * (3.0 - 2.0 * pf);
            
            vec3 w = pf;
            vec3 a = hash3(pi + vec3(0.0,0.0,0.0));
            vec3 b = hash3(pi + vec3(1.0,0.0,0.0));
            vec3 c = hash3(pi + vec3(0.0,1.0,0.0));
            vec3 d = hash3(pi + vec3(1.0,1.0,0.0));
            
            vec3 u = w.xzy * a + (w.xzy * (1.0 - a));
            vec3 v = w.xzy * c + (w.xzy * (1.0 - c));
            vec3 x = w.y * u + (w.y * (1.0 - u));
            vec3 y = w.y * v + (w.y * (1.0 - y));
            
            return fract(dot(x, vec3(1.0)));
        }

        // Smooth Minimum Function
        // Used to blend metaballs smoothly
        float smin(float a, float b, float k) {
            float h = clamp(0.5 + 0.5 * (b - a) / k, 0.0, 1.0);
            return mix(b, a, h) - k * h * (1.0 - h);
        }

        // ----------------------------------------------------------
        // SCENE SDF DEFINITIONS
        // ----------------------------------------------------------
        
        // Sphere SDF
        float sdSphere(vec3 p, vec3 center, float radius) {
            float dist = length(p - center) - radius;
            return dist;
        }

        // Main Scene Function
        float MapScene(vec3 p) {
            // Animation parameters
            float t = iGlobalTime;
            
            // Define Metaballs dynamically based on time
            // Format: [center.x, center.y, center.z, radius, color_r, color_g, color_b]
            
            // Dynamic Metaball 1: Rotating Sphere
            vec3 pos1 = vec3(
                sin(t * 0.8) * 2.5, 
                cos(t * 0.6) * 2.0, 
                sin(t * 0.5) * 2.0
            );
            float rad1 = 1.5 + 0.5 * sin(t * 0.3);
            
            // Dynamic Metaball 2: Rotating on Y axis
            vec3 pos2 = vec3(
                cos(t * 0.5) * 2.0, 
                sin(t * 0.4) * 2.5, 
                cos(t * 0.3) * 2.0
            );
            float rad2 = 1.2 + 0.3 * sin(t * 0.7);

            // Dynamic Metaball 3: Pulsing
            vec3 pos3 = vec3(
                sin(t * 0.3) * 3.0, 
                -2.0 + sin(t * 0.9) * 2.0, 
                -0.5
            );
            float rad3 = 1.8 + 0.5 * cos(t * 0.4);

            // Define Colors (Psychedelic Palette)
            vec3 col1 = vec3(1.0, 0.2, 0.5); // Hot Pink
            vec3 col2 = vec3(0.1, 0.6, 1.0); // Electric Blue
            vec3 col3 = vec3(0.5, 1.0, 0.3); // Lime Green

            // Blend using Smooth Minimum
            // We blend the distance fields of all three balls
            float d1 = sdSphere(p, pos1, rad1);
            float d2 = sdSphere(p, pos2, rad2);
            float d3 = sdSphere(p, pos3, rad3);

            // First blend: d1 and d2
            float d_xy = smin(d1, d2, 0.5);
            
            // Final blend: result and d3
            float d_scene = smin(d_xy, d3, 0.5);

            return d_scene;
        }

        // ----------------------------------------------------------
        // RAYMARCHING CORE
        // ----------------------------------------------------------
        float RayMarch(vec3 from, vec3 dir) {
            float d = 0.0; // Distance traveled
            float delta = 0.01; // Step size for adaptive stepping
            
            // March forward
            for (int i = 0; i < MAX_STEPS; i++) {
                vec3 pos = from + dir * d; // Current position
                float dist = MapScene(pos); // Get distance to nearest surface
                
                // If we hit inside a ball (distance < 0), we might have hit the surface
        // Actually, in raymarching, we march until dist is very small
        // Adaptive step sizing
        float stepSize = max(delta, dist * 0.5); 
        d += stepSize;
        
        // Check for hit or max distance
        if (dist < 0.01 || d > MAX_DIST) {
            break;
        }
            }
            return d;
        }

        // ----------------------------------------------------------
        // LIGHTING & SHADES
        // ----------------------------------------------------------
        vec3 GetLighting(vec3 pos, vec3 normal, vec3 lightDir) {
            vec3 ambient = vec3(0.1);
            float diffuse = max(dot(normal, lightDir), 0.0);
            float spec = pow(max(dot(normal, reflect(-lightDir, normal)), 0.0), 32.0);
            
            vec3 color = vec3(1.0);
            
            // Apply psychedelic color modulation based on position and time
            float r = sin(pos.x * 2.0 + iGlobalTime);
            float g = sin(pos.y * 2.0 + iGlobalTime);
            float b = sin(pos.z * 2.0 + iGlobalTime);
            
            vec3 psychedelicColor = 0.5 + 0.5 * vec3(r, g, b);
            
            vec3 finalColor = ambient + diffuse * psychedelicColor + spec * vec3(1.0);
            return finalColor;
        }

        // ----------------------------------------------------------
        // MAIN RENDER LOOP
        // ----------------------------------------------------------
        void main() {
            // Normalize fragment coordinates (-1.0 to 1.0)
            vec2 uv = (2.0 * gl_FragCoord.xy - iResolution.xy) / iResolution.xy;
            
            // Camera Setup
            vec3 cameraPos = vec3(0.0, 0.0, 3.0); // Move camera slightly back
            vec3 lookDir = normalize(vec3(uv, 1.0));
            
            // Ray March
            float dist = RayMarch(cameraPos, lookDir);
            
            vec3 finalColor = vec3(0.0); // Default background (black)
            
            if (dist < MAX_DIST) {
                // Calculate surface point
                vec3 point = cameraPos + lookDir * dist;
                
                // Calculate Normal using finite differences (gradient of SDF)
                vec3 epsilon = vec3(0.01, 0.0, 0.0);
                vec3 normal = normalize(vec3(
                    MapScene(point + epsilon.xyy) - MapScene(point - epsilon.xyy),
                    MapScene(point + epsilon.yxy) - MapScene(point - epsilon.yxy),
                    MapScene(point + epsilon.yyx) - MapScene(point - epsilon.yyx)
                ));
                
                // Lighting
                vec3 lightDir = normalize(vec3(1.0, 1.0, 0.0));
                vec3 color = GetLighting(point, normal, lightDir);
                
                // Add some "glow" based on distance traveled (fog-like effect)
                float fog = 1.0 - clamp(dist / MAX_DIST, 0.0, 1.0);
                vec3 fogColor = vec3(0.05, 0.02, 0.1); // Deep dark background
                
                // Combine color and fog
                finalColor = mix(fogColor, color, fog);
                
                // Add noise texture to surface for extra groovy texture
                float noiseVal = noise(point * 2.0);
                finalColor += vec3(noiseVal * 0.2);
            }
            
            // Gamma correction
            finalColor = pow(finalColor, vec3(0.45));
            
            gl_FragColor = vec4(finalColor, 1.0);
        }
    </script>

    <script>
        // --- JavaScript WebGL Controller ---
        const canvas = document.getElementById('glCanvas');
        const gl = canvas.getContext('webgl');

        // Resize canvas to fit window
        function resize() {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
            // Trigger a redraw
            if(shaderProgram) render();
        }
        window.addEventListener('resize', resize);

        // --- Shader Compilation Helpers ---
        function createShader(type, source) {
            const shader = gl.createShader(type);
            gl.shaderSource(shader, source);
            gl.compileShader(shader);
            if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
                console.error(gl.getShaderInfoLog(shader));
                gl.deleteShader(shader);
                return null;
            }
            return shader;
        }

        // Get shader source from DOM
        const vsSource = document.getElementById('vertexShader').text;
        const fsSource = document.getElementById('fragmentShader').text;

        const vertexShader = createShader(gl.VERTEX_SHADER, vsSource);
        const fragmentShader = createShader(gl.FRAGMENT_SHADER, fsSource);

        const shaderProgram = gl.createProgram();
        gl.attachShader(shaderProgram, vertexShader);
        gl.attachShader(shaderProgram, fragmentShader);
        gl.linkProgram(shaderProgram);

        if (!gl.getProgramParameter(shaderProgram, gl.LINK_STATUS)) {
            console.error("Shader Link Error:", gl.getProgramInfoLog(shaderProgram));
        }

        // --- Rendering Setup ---
        const positionLocation = gl.getAttribLocation(shaderProgram, "position");
        
        // Full screen quad vertices
        const vertices = new Float32Array([
            -1, -1, // Bottom Left
            1, -1,  // Bottom Right
            -1, 1,   // Top Left
            1, 1,    // Top Right
            -1, 1,   // Top Left (Triangle 2)
            1, -1    // Bottom Right (Triangle 2)
        ]);

        const buffer = gl.createBuffer();
        gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
        gl.bufferData(gl.ARRAY_BUFFER, vertices, gl.STATIC_DRAW);

        // Uniform locations
        const resLoc = gl.getUniformLocation(shaderProgram, "iResolution");
        const timeLoc = gl.getUniformLocation(shaderProgram, "iTime");
        const globalTimeLoc = gl.getUniformLocation(shaderProgram, "iGlobalTime");

        // Animation Loop
        let lastTime = 0;

        function render(timestamp) {
            if (!timestamp) timestamp = 0;
            
            // Calculate time delta for smooth animation
            const deltaTime = timestamp - lastTime;
            lastTime = timestamp;
            
            // Accumulate time for shader
            const time = timestamp / 1000; // Convert to seconds
            
            gl.clearColor(0.0, 0.0, 0.0, 1.0);
            gl.clear(gl.COLOR_BUFFER_BIT);
            
            gl.useProgram(shaderProgram);
            
            // Enable vertex attribute
            gl.enableVertexAttribArray(positionLocation);
            gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
            gl.vertexAttribPointer(positionLocation, 2, gl.FLOAT, false, 0, 0);

            // Set Uniforms
            gl.uniform2f(resLoc, canvas.width, canvas.height);
            gl.uniform1f(timeLoc, time); // Pass 'time' as 'iTime'
            gl.uniform1f(globalTimeLoc, time); // Pass 'time' as 'iGlobalTime'

            // Draw the quad
            gl.drawArrays(gl.TRIANGLES, 0, 6);
            
            requestAnimationFrame(render);
        }

        // Initialize
        resize();
        requestAnimationFrame(render);

        // Expose resize to global scope for clean startup
        window.render = render;

    </script>
</body>
</html>
```

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: Qwen3-Coder-Next-UD-IQ1_M.gguf -->
<!-- Prompt: lightshow.md -->
<!-- Time: 48.21s -->
<!-- Fallback: False -->