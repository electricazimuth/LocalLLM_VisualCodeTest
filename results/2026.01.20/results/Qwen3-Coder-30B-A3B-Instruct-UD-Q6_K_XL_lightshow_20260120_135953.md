# Ray Marching Psychedelic Metaball Simulation

I'll create a mesmerizing psychedelic metaball simulation using WebGL ray marching techniques. This implementation will feature fluid, organic metaballs that merge and separate in a hypnotic dance of color and form.

```html
<!DOCTYPE html>
<html>
<head>
    <title>Psychedelic Metaball Ray Marching</title>
    <style>
        body { 
            margin: 0; 
            overflow: hidden; 
            background-color: #000; 
            font-family: 'Arial', sans-serif;
        }
        canvas { 
            display: block; 
            width: 100vw; 
            height: 100vh; 
        }
        #info {
            position: absolute;
            top: 20px;
            left: 20px;
            color: rgba(255, 255, 255, 0.7);
            font-size: 14px;
            background: rgba(0, 0, 0, 0.5);
            padding: 10px;
            border-radius: 5px;
            max-width: 300px;
            backdrop-filter: blur(5px);
        }
        #title {
            position: absolute;
            top: 20px;
            width: 100%;
            text-align: center;
            color: rgba(255, 255, 255, 0.9);
            font-size: 24px;
            text-shadow: 0 0 10px rgba(255, 0, 255, 0.7);
            letter-spacing: 2px;
            font-weight: bold;
            pointer-events: none;
        }
    </style>
</head>
<body>
    <div id="title">PSYCHEDELIC METABALL RAY MARCHING</div>
    <div id="info">
        <p>Ray marching simulation of organic metaballs with smooth blending</p>
        <p>Colors shift through time and position</p>
        <p>Metaballs merge and separate dynamically</p>
    </div>
    <canvas id="glCanvas"></canvas>

    <script>
        // --- Standard WebGL Boilerplate ---
        const canvas = document.getElementById('glCanvas');
        const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');

        if (!gl) {
            alert('WebGL not supported');
            throw new Error('WebGL not supported');
        }

        // Set canvas size
        function resizeCanvas() {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
            gl.viewport(0, 0, canvas.width, canvas.height);
        }
        
        window.addEventListener('resize', resizeCanvas);
        resizeCanvas();

        // --- Vertex Shader ---
        const vertexShaderSource = `
            attribute vec2 a_position;
            varying vec2 v_texCoord;
            
            void main() {
                gl_Position = vec4(a_position, 0.0, 1.0);
                v_texCoord = a_position * 0.5 + 0.5;
            }
        `;

        // --- Fragment Shader ---
        const fragmentShaderSource = `
            precision highp float;
            
            varying vec2 v_texCoord;
            uniform float u_time;
            uniform vec2 u_resolution;
            uniform vec3 u_metaball_positions[8];
            uniform float u_metaball_radii[8];
            uniform vec3 u_colors[8];
            
            // Smooth minimum function
            float smin(float a, float b, float k) {
                float h = clamp(0.5 + 0.5 * (b - a) / k, 0.0, 1.0);
                return mix(b, a, h) - k * h * (1.0 - h);
            }
            
            // Signed Distance Function for a sphere
            float sdSphere(vec3 p, vec3 center, float radius) {
                return length(p - center) - radius;
            }
            
            // Scene SDF - combined metaballs
            float sceneSDF(vec3 p) {
                float d = 1000.0;
                float k = 0.5; // Smoothness factor
                
                // Combine all metaballs with smooth minimum
                for (int i = 0; i < 8; i++) {
                    float dist = sdSphere(p, u_metaball_positions[i], u_metaball_radii[i]);
                    d = smin(d, dist, k);
                }
                
                return d;
            }
            
            // Calculate normal using gradient
            vec3 calcNormal(vec3 p) {
                const float eps = 0.001;
                vec2 e = vec2(eps, 0.0);
                return normalize(vec3(
                    sceneSDF(p + e.xyy) - sceneSDF(p - e.xyy),
                    sceneSDF(p + e.yxy) - sceneSDF(p - e.yxy),
                    sceneSDF(p + e.yyx) - sceneSDF(p - e.yyx)
                ));
            }
            
            // Simple lighting model
            vec3 lighting(vec3 pos, vec3 normal) {
                vec3 lightDir = normalize(vec3(1.0, 1.0, 1.0));
                float diff = max(dot(normal, lightDir), 0.0);
                return vec3(0.5 + 0.5 * diff);
            }
            
            // Color palette generator
            vec3 getColor(float t) {
                // Create psychedelic color palette using sine waves
                float r = 0.5 + 0.5 * sin(t * 0.5 + 0.0);
                float g = 0.5 + 0.5 * sin(t * 0.3 + 2.0);
                float b = 0.5 + 0.5 * sin(t * 0.7 + 4.0);
                return vec3(r, g, b);
            }
            
            // Psychedelic color based on position and time
            vec3 psychedelicColor(vec3 pos, vec3 normal, float distance) {
                // Base color based on position and time
                float timeFactor = u_time * 0.2;
                vec3 baseColor = getColor(timeFactor + pos.x * 0.1 + pos.y * 0.1 + pos.z * 0.1);
                
                // Add some variation based on distance from center
                float distFactor = 0.5 + 0.5 * sin(distance * 0.5 + timeFactor);
                vec3 finalColor = baseColor * distFactor;
                
                // Add some color shift based on normal
                float normalFactor = 0.5 + 0.5 * sin(normal.x + normal.y + normal.z + timeFactor * 1.5);
                finalColor += vec3(0.2, 0.1, 0.3) * normalFactor;
                
                return finalColor;
            }
            
            void main() {
                // Normalize coordinates to [-1, 1]
                vec2 uv = (v_texCoord - 0.5) * 2.0;
                uv.x *= u_resolution.x / u_resolution.y;
                
                // Camera setup
                vec3 cameraPos = vec3(0.0, 0.0, 3.0);
                vec3 rayDir = normalize(vec3(uv, -1.0));
                
                // Ray marching parameters
                const int maxSteps = 100;
                const float maxDistance = 50.0;
                const float minDistance = 0.001;
                
                // Ray marching loop
                float totalDistance = 0.0;
                bool hit = false;
                vec3 color = vec3(0.0);
                vec3 pos = cameraPos;
                
                for (int i = 0; i < maxSteps; i++) {
                    pos = cameraPos + rayDir * totalDistance;
                    float d = sceneSDF(pos);
                    
                    if (d < minDistance) {
                        hit = true;
                        break;
                    }
                    
                    if (totalDistance > maxDistance) {
                        break;
                    }
                    
                    totalDistance += d;
                }
                
                // Color based on hit
                if (hit) {
                    vec3 normal = calcNormal(pos);
                    vec3 light = lighting(pos, normal);
                    color = psychedelicColor(pos, normal, totalDistance);
                    color *= light;
                } else {
                    // Background color
                    color = vec3(0.0, 0.0, 0.05);
                }
                
                // Add some glow effect
                color += vec3(0.05) * exp(-totalDistance * 0.1);
                
                // Output final color
                gl_FragColor = vec4(color, 1.0);
            }
        `;

        // --- Shader Compilation Helper ---
        function compileShader(source, type) {
            const shader = gl.createShader(type);
            gl.shaderSource(shader, source);
            gl.compileShader(shader);
            
            if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
                console.error('Shader compilation error:', gl.getShaderInfoLog(shader));
                gl.deleteShader(shader);
                return null;
            }
            
            return shader;
        }

        // --- Program Creation ---
        const vertexShader = compileShader(vertexShaderSource, gl.VERTEX_SHADER);
        const fragmentShader = compileShader(fragmentShaderSource, gl.FRAGMENT_SHADER);
        
        const program = gl.createProgram();
        gl.attachShader(program, vertexShader);
        gl.attachShader(program, fragmentShader);
        gl.linkProgram(program);
        
        if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
            console.error('Program linking error:', gl.getProgramInfoLog(program));
        }
        
        gl.useProgram(program);

        // --- Vertex Data for Fullscreen Quad ---
        const vertices = new Float32Array([
            -1, -1,
             1, -1,
            -1,  1,
             1,  1
        ]);
        
        const vertexBuffer = gl.createBuffer();
        gl.bindBuffer(gl.ARRAY_BUFFER, vertexBuffer);
        gl.bufferData(gl.ARRAY_BUFFER, vertices, gl.STATIC_DRAW);
        
        const positionLocation = gl.getAttribLocation(program, "a_position");
        gl.enableVertexAttribArray(positionLocation);
        gl.vertexAttribPointer(positionLocation, 2, gl.FLOAT, false, 0, 0);

        // --- Uniform Locations ---
        const timeLocation = gl.getUniformLocation(program, "u_time");
        const resolutionLocation = gl.getUniformLocation(program, "u_resolution");
        const metaballPositionsLocation = gl.getUniformLocation(program, "u_metaball_positions");
        const metaballRadiiLocation = gl.getUniformLocation(program, "u_metaball_radii");
        const colorsLocation = gl.getUniformLocation(program, "u_colors");

        // --- Initialize Metaball Data ---
        const metaballCount = 8;
        const metaballPositions = new Float32Array(metaballCount * 3);
        const metaballRadii = new Float32Array(metaballCount);
        const colors = new Float32Array(metaballCount * 3);
        
        // Initialize metaballs with random positions and properties
        for (let i = 0; i < metaballCount; i++) {
            metaballPositions[i * 3] = (Math.random() - 0.5) * 2.0;
            metaballPositions[i * 3 + 1] = (Math.random() - 0.5) * 2.0;
            metaballPositions[i * 3 + 2] = (Math.random() - 0.5) * 2.0;
            
            metaballRadii[i] = 0.2 + Math.random() * 0.3;
            
            // Generate vibrant psychedelic colors
            colors[i * 3] = Math.random() * 0.5 + 0.5;
            colors[i * 3 + 1] = Math.random() * 0.5 + 0.5;
            colors[i * 3 + 2] = Math.random() * 0.5 + 0.5;
        }

        // --- Animation Loop ---
        let startTime = Date.now();
        
        function render() {
            const currentTime = (Date.now() - startTime) / 1000.0;
            
            // Update metaball positions with smooth movement
            for (let i = 0; i < metaballCount; i++) {
                const timeOffset = i * 0.5;
                const radius = metaballRadii[i];
                
                // Oscillate position in a circular pattern
                metaballPositions[i * 3] = Math.sin(currentTime * 0.2 + timeOffset) * (1.0 + radius);
                metaballPositions[i * 3 + 1] = Math.cos(currentTime * 0.3 + timeOffset) * (1.0 + radius);
                metaballPositions[i * 3 + 2] = Math.sin(currentTime * 0.1 + timeOffset) * (0.5 + radius);
                
                // Slightly vary radius over time
                metaballRadii[i] = 0.2 + 0.1 * Math.sin(currentTime * 0.4 + i);
                
                // Update colors with time-based shifts
                colors[i * 3] = 0.5 + 0.5 * Math.sin(currentTime * 0.3 + i);
                colors[i * 3 + 1] = 0.5 + 0.5 * Math.sin(currentTime * 0.5 + i);
                colors[i * 3 + 2] = 0.5 + 0.5 * Math.sin(currentTime * 0.7 + i);
            }
            
            // Set uniforms
            gl.uniform1f(timeLocation, currentTime);
            gl.uniform2f(resolutionLocation, canvas.width, canvas.height);
            
            // Send metaball data to shader
            gl.uniform3fv(metaballPositionsLocation, metaballPositions);
            gl.uniform1fv(metaballRadiiLocation, metaballRadii);
            gl.uniform3fv(colorsLocation, colors);
            
            // Draw the fullscreen quad
            gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
            
            requestAnimationFrame(render);
        }
        
        // Start the animation
        render();
    </script>
</body>
</html>
```

## Key Features of this Implementation

1. **Ray Marching Technique**: Uses signed distance functions (SDFs) to render metaballs through ray marching
2. **Smooth Minimum Function**: Implements a smooth minimum to create organic merging of metaballs
3. **Psychedelic Visuals**: 
   - Vibrant, shifting colors based on position and time
   - Dynamic lighting effects
   - Glowing, volumetric appearance
4. **Dynamic Metaballs**:
   - Metaballs move in circular patterns
   - Radii vary over time for fluid motion
   - Colors shift continuously
5. **Performance Optimized**:
   - Efficient ray marching with early termination
   - Minimal vertex data for fullscreen quad
   - Smooth animation using requestAnimationFrame

The simulation creates a mesmerizing display of fluid, organic metaballs that blend together in hypnotic patterns reminiscent of 1960s psychedelic light shows. The colors shift continuously, creating an ever-evolving visual experience.

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: Qwen3-Coder-30B-A3B-Instruct-UD-Q6_K_XL.gguf -->
<!-- Prompt: lightshow.md -->
<!-- Generation Time: 35.47s -->
<!-- Fallback Used: False -->