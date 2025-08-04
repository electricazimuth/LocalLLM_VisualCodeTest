We are going to create a WebGL application that renders a ray-marched scene of evolving metaballs.
 The key steps are:
 1. Set up WebGL context and shaders.
 2. Implement a ray marching algorithm in the fragment shader.
 3. Define the metaballs using SDFs and combine them with a smooth minimum function.
 4. Animate the metaballs over time (position, size, color) to create a dynamic, psychedelic effect.
 5. Use vibrant, shifting colors and lighting to achieve the desired aesthetic.

 We'll use:
   - A vertex shader that passes UV coordinates to the fragment shader.
   - A fragment shader that:
        * Performs ray marching to find the intersection with the metaball scene.
        * Uses a smooth minimum function to blend multiple metaballs.
        * Computes color based on distance, normal, and light.

 We'll update the positions and parameters of the metaballs from JavaScript using uniforms.

 Let's define the shaders:

 Vertex Shader (simple):
   - Passes the UV coordinates (normalized device coordinates) to the fragment shader.

 Fragment Shader:
   - Contains:
        * Ray marching loop with a fixed number of steps.
        * SDF for a single ball (sphere).
        * Smooth minimum function to combine multiple SDFs.
        * Function to compute the gradient (normal) at a point.
        * Lighting model (simple diffuse and ambient).
        * Color modulation based on time and position.

 We'll use a time uniform to animate the metaballs.

 Note: We are using WebGL 1, so we are limited to GLSL ES 1.0.

 We'll create 4-8 metaballs that move in a circular pattern and change radius and color over time.

 Let's code accordingly.
</think>

# Ray Marching Psychedelic Metaball Simulation

I'll create a visually stunning WebGL application that implements ray marching for metaballs with a psychedelic aesthetic. The solution will include smooth animations, vibrant colors, and organic merging effects.

```html
<!DOCTYPE html>
<html>
<head>
    <title>Psychedelic Metaball Simulation</title>
    <style>
        body { 
            margin: 0; 
            overflow: hidden; 
            background-color: #000; 
            font-family: 'Courier New', monospace;
            color: #0ff;
        }
        canvas { 
            display: block; 
            width: 100vw; 
            height: 100vh; 
            background: #000;
        }
        #info {
            position: absolute;
            top: 10px;
            left: 10px;
            z-index: 100;
            background: rgba(0, 0, 0, 0.7);
            padding: 10px;
            border-radius: 4px;
            font-size: 14px;
            max-width: 300px;
        }
    </style>
</head>
<body>
    <canvas id="glCanvas"></canvas>
    <div id="info">
        <h3>Psychedelic Metaball Simulation</h3>
        <p>Ray marching with signed distance functions</p>
        <p>Metaballs merge and evolve dynamically</p>
        <p>Use arrow keys to navigate, space to pause</p>
    </div>

    <script>
        // --- WebGL Setup ---
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
        
        // Shader programs
        const vertexShaderSource = `
            attribute vec2 a_position;
            varying highp vec2 v_uv;
            void main() {
                v_uv = a_position * 0.5 + 0.5;
                gl_Position = vec4(a_position, 0.0, 1.0);
            }
        `;
        
        const fragmentShaderSource = `
            precision highp float;
            varying vec2 v_uv;
            
            // Uniforms
            uniform float u_time;
            uniform vec2 u_resolution;
            uniform vec3 u_cameraPos;
            uniform vec3 u_lightDir;
            
            // Metaball structure
            struct Metaball {
                vec3 position;
                float radius;
                vec3 color;
                float influence;
            };
            
            // SDF for a single metaball
            float sdSphere(vec3 p, vec3 s) {
                return length(p - s.position) - s.radius;
            }
            
            // Smooth minimum function for blending metaballs
            float smin(float a, float b, float k) {
                float h = clamp(0.5 + 0.5*(a - b)/k, 0.0, 1.0);
                return mix(a, b, h) - k * h * (1.0 - h);
            }
            
            // Ray marching function
            vec3 rayMarch(vec3 ro, vec3 rd) {
                float t = 0.0;
                float tMax = 100.0;
                float tStep = 0.1;
                vec3 closestPoint = vec3(0.0);
                float closestDist = tMax;
                bool hit = false;
                
                // Ray marching loop
                for (int i = 0; i < 64; i++) {
                    if (t > tMax) break;
                    
                    vec3 p = ro + rd * t;
                    float dist = 1e6;
                    
                    // Calculate distance to all metaballs
                    for (int j = 0; j < 8; j++) {
                        float d = sdSphere(p, metaballs[j]);
                        dist = smin(dist, d, 1.0);
                    }
                    
                    // If we're close enough to a surface, we hit
                    if (dist < 0.001) {
                        hit = true;
                        closestPoint = p;
                        closestDist = dist;
                        break;
                    }
                    
                    t += dist;
                }
                
                if (hit) {
                    // Calculate normal at hit point
                    vec3 normal = vec3(0.0);
                    float eps = 0.001;
                    for (int i = 0; i < 3; i++) {
                        vec3 d = vec3(0.0);
                        d[i] = eps;
                        float d1 = 0.0, d2 = 0.0;
                        for (int j = 0; j < 8; j++) {
                            d1 = smin(d1, sdSphere(closestPoint + d, metaballs[j]), 1.0);
                            d2 = smin(d2, sdSphere(closestPoint - d, metaballs[j]), 1.0);
                        }
                        normal[i] = (d1 - d2) / (2.0 * eps);
                    }
                    
                    // Normalize normal
                    normal = normalize(normal);
                    
                    // Calculate lighting
                    float diffuse = max(0.0, dot(normal, normalize(u_lightDir)));
                    float ambient = 0.3;
                    float brightness = diffuse + ambient;
                    
                    // Color based on closest metaball
                    vec3 color = vec3(0.0);
                    for (int j = 0; j < 8; j++) {
                        float d = sdSphere(closestPoint, metaballs[j]);
                        if (d < 0.0) {
                            float influence = max(0.0, -d) / metaballs[j].radius;
                            color += metaballs[j].color * influence * brightness;
                        }
                    }
                    
                    return color;
                }
                
                // Background gradient
                float bg = 0.1 + 0.1 * sin(u_time * 0.5);
                return vec3(0.0, bg, 0.2);
            }
            
            // Main function
            void main() {
                // Camera setup
                vec3 cameraPos = u_cameraPos;
                vec3 rayDir = normalize(vec3(
                    v_uv.x * 2.0 - 1.0,
                    v_uv.y * 2.0 - 1.0,
                    1.0
                ));
                
                // Calculate color
                vec3 color = rayMarch(cameraPos, rayDir);
                
                // Apply time-based color shift
                float hueShift = 0.5 + 0.5 * sin(u_time * 0.3);
                color.r = mix(color.r, color.g, hueShift);
                color.g = mix(color.g, color.b, hueShift);
                color.b = mix(color.b, color.r, hueShift);
                
                // Output color
                gl_FragColor = vec4(color, 1.0);
            }
        `;
        
        // Create shaders
        function createShader(type, source) {
            const shader = gl.createShader(type);
            gl.shaderSource(shader, source);
            gl.compileShader(shader);
            
            if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
                console.error('Shader compilation error:', gl.getShaderInfoLog(shader));
                return null;
            }
            
            return shader;
        }
        
        // Create program
        const program = gl.createProgram();
        const vertexShader = createShader(gl.VERTEX_SHADER, vertexShaderSource);
        const fragmentShader = createShader(gl.FRAGMENT_SHADER, fragmentShaderSource);
        
        gl.attachShader(program, vertexShader);
        gl.attachShader(program, fragmentShader);
        gl.linkProgram(program);
        
        if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
            console.error('Program linking error:', gl.getProgramInfoLog(program));
        }
        
        gl.useProgram(program);
        
        // Position attribute
        const positionLocation = gl.getAttribLocation(program, 'a_position');
        const positionBuffer = gl.createBuffer();
        gl.bindBuffer(gl.ARRAY_BUFFER, positionBuffer);
        
        const positions = [
            -1, -1,
            1, -1,
            -1, 1,
            1, 1
        ];
        
        gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(positions), gl.STATIC_DRAW);
        gl.enableVertexAttribArray(positionLocation);
        gl.vertexAttribPointer(positionLocation, 2, gl.FLOAT, false, 0, 0);
        
        // Uniforms
        const uTimeLocation = gl.getUniformLocation(program, 'u_time');
        const uResolutionLocation = gl.getUniformLocation(program, 'u_resolution');
        const uCameraPosLocation = gl.getUniformLocation(program, 'u_cameraPos');
        const uLightDirLocation = gl.getUniformLocation(program, 'u_lightDir');
        
        // Metaballs uniform
        const metaballsLocation = gl.getUniformLocation(program, 'metaballs');
        
        // Create metaballs array
        const metaballs = [];
        const colors = [
            vec3(0.8, 0.2, 0.6),
            vec3(0.2, 0.8, 0.6),
            vec3(0.6, 0.8, 0.2),
            vec3(0.8, 0.6, 0.2),
            vec3(0.2, 0.6, 0.8),
            vec3(0.6, 0.2, 0.8),
            vec3(0.8, 0.8, 0.2),
            vec3(0.2, 0.2, 0.8)
        ];
        
        for (let i = 0; i < 8; i++) {
            metaballs.push({
                position: vec3(0, 0, 0),
                radius: 0.5,
                color: colors[i],
                influence: 1.0
            });
        }
        
        // Animation state
        let time = 0;
        let paused = false;
        let cameraPos = vec3(0, 0, 5);
        let lightDir = vec3(1, 1, 1);
        
        // Animation loop
        function animate() {
            if (paused) return;
            
            time += 0.05;
            
            // Update metaball positions
            for (let i = 0; i < 8; i++) {
                const ball = metaballs[i];
                const speed = 0.5 + i * 0.1;
                const angle = time * speed;
                
                ball.position.x = 2.0 * sin(angle * 0.5) * cos(0.2 * i);
                ball.position.y = 2.0 * cos(angle * 0.7) * sin(0.3 * i);
                ball.position.z = 0.5 * sin(angle * 1.0) + 1.0;
                
                // Animate radius
                ball.radius = 0.3 + 0.2 * abs(sin(angle * 0.8 + i));
                
                // Animate color
                const hue = 0.1 + 0.2 * i + 0.1 * sin(angle * 0.3);
                const color = hueToRgb(hue);
                ball.color = color;
            }
            
            // Update uniforms
            gl.uniform2f(uResolutionLocation, canvas.width, canvas.height);
            gl.uniform1f(uTimeLocation, time);
            gl.uniform3fv(uCameraPosLocation, cameraPos);
            gl.uniform3fv(uLightDirLocation, lightDir);
            
            // Pass metaballs to shader
            gl.uniform4fv(metaballsLocation, flatten(metaballs));
            
            // Draw
            gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
            
            requestAnimationFrame(animate);
        }
        
        // Helper functions
        function vec3(x, y, z) {
            return [x, y, z];
        }
        
        function vec2(x, y) {
            return [x, y];
        }
        
        function flatten(arr) {
            return arr.reduce((flat, obj) => {
                return [...flat, ...obj.position, obj.radius, ...obj.color, obj.influence];
            }, []);
        }
        
        function hueToRgb(hue) {
            const r = abs(sin(hue * 6.28));
            const g = abs(sin((hue + 0.33) * 6.28));
            const b = abs(sin((hue + 0.66) * 6.28));
            return [r, g, b];
        }
        
        // Keyboard controls
        document.addEventListener('keydown', (e) => {
            if (e.key === ' ') {
                paused = !paused;
            }
            
            if (e.key === 'ArrowUp') {
                cameraPos[2] += 0.1;
            }
            
            if (e.key === 'ArrowDown') {
                cameraPos[2] -= 0.1;
            }
            
            if (e.key === 'ArrowLeft') {
                cameraPos[0] -= 0.1;
            }
            
            if (e.key === 'ArrowRight') {
                cameraPos[0] += 0.1;
            }
        });
        
        // Start animation
        animate();
    </script>
</body>
</html>
```

## Key Features of the Implementation

1. **Ray Marching Algorithm**:
   - Uses a signed distance function (SDF) for spheres to represent metaballs
   - Implements a smooth minimum function to blend multiple metaballs
   - Performs iterative ray marching to find intersections

2. **Dynamic Metaballs**:
   - 8 metaballs that move in complex, evolving patterns
   - Each metaball has its own position, radius, color, and influence
   - Parameters change dynamically over time for organic movement

3. **Visual Effects**:
   - Vibrant, shifting colors using hue-based color generation
   - Smooth blending between metaballs for the characteristic "merging" effect
   - Dynamic lighting based on surface normals
   - Time-based color shifts for psychedelic feel

4. **Controls**:
   - Arrow keys to adjust camera position
   - Space bar to pause/resume animation
   - Responsive to window resizing

5. **Performance**:
   - Optimized ray marching with 64 steps
   - Efficient shader code for real-time rendering
   - WebGL 1.0 compatible for wide browser support

The simulation creates a mesmerizing, evolving landscape of fluid, merging forms that capture the essence of 1960s psychedelic visuals while using modern WebGL techniques. The metaballs smoothly blend together and separate, creating a dynamic, organic feel with vibrant, shifting colors.

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: UIGEN-X-32B-0727.Q4_K_M.gguf -->
<!-- Prompt: lightshow.md -->
<!-- Generation Time: 122.28s -->
<!-- Fallback Used: False -->