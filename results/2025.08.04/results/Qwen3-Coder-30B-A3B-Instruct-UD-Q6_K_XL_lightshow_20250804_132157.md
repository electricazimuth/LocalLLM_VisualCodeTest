# Ray Marching Psychedelic Metaball Simulation

I'll create a mesmerizing psychedelic metaball simulation using WebGL ray marching techniques. This implementation will feature fluid, organic metaballs that merge and separate in a hypnotic pattern with vibrant, shifting colors.

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
            z-index: 10;
            background: rgba(0, 0, 0, 0.5);
            padding: 10px;
            border-radius: 5px;
            max-width: 300px;
        }
        #title {
            position: absolute;
            top: 20px;
            width: 100%;
            text-align: center;
            color: rgba(255, 255, 255, 0.9);
            font-size: 24px;
            font-weight: bold;
            text-shadow: 0 0 10px rgba(255, 0, 255, 0.7);
            z-index: 10;
        }
    </style>
</head>
<body>
    <div id="title">PSYCHEDELIC METABALL RAY MARCHING</div>
    <div id="info">Ray marching technique with smooth minimum blending | Dynamic metaballs | Psychedelic color palette</div>
    <canvas id="glCanvas"></canvas>

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
            
            // Smooth minimum function
            float smin(float a, float b, float k) {
                float h = clamp(0.5 + 0.5 * (b - a) / k, 0.0, 1.0);
                return mix(b, a, h) - k * h * (1.0 - h);
            }
            
            // Signed Distance Function for a sphere
            float sdSphere(vec3 p, vec3 center, float radius) {
                return length(p - center) - radius;
            }
            
            // Scene SDF - combines multiple metaballs
            float sceneSDF(vec3 p) {
                float k = 0.2; // Smooth minimum factor
                
                // Create multiple metaballs with dynamic positions
                vec3 c1 = vec3(0.0, 0.0, 0.0) + vec3(sin(u_time * 0.3) * 0.5, cos(u_time * 0.2) * 0.3, sin(u_time * 0.1) * 0.4);
                vec3 c2 = vec3(0.0, 0.0, 0.0) + vec3(cos(u_time * 0.2) * 0.7, sin(u_time * 0.4) * 0.5, cos(u_time * 0.3) * 0.3);
                vec3 c3 = vec3(0.0, 0.0, 0.0) + vec3(sin(u_time * 0.4) * 0.6, cos(u_time * 0.3) * 0.4, sin(u_time * 0.2) * 0.5);
                vec3 c4 = vec3(0.0, 0.0, 0.0) + vec3(cos(u_time * 0.5) * 0.4, sin(u_time * 0.1) * 0.6, cos(u_time * 0.4) * 0.7);
                
                float r1 = 0.3 + sin(u_time * 0.3) * 0.1;
                float r2 = 0.4 + cos(u_time * 0.2) * 0.15;
                float r3 = 0.35 + sin(u_time * 0.4) * 0.1;
                float r4 = 0.45 + cos(u_time * 0.1) * 0.2;
                
                float d1 = sdSphere(p, c1, r1);
                float d2 = sdSphere(p, c2, r2);
                float d3 = sdSphere(p, c3, r3);
                float d4 = sdSphere(p, c4, r4);
                
                // Combine with smooth minimum
                float d = smin(d1, d2, k);
                d = smin(d, d3, k);
                d = smin(d, d4, k);
                
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
            vec3 lighting(vec3 p, vec3 normal) {
                vec3 lightDir = normalize(vec3(0.5, 1.0, 0.7));
                float diff = max(dot(normal, lightDir), 0.0);
                
                // Base color based on position and time
                float colorFactor = sin(p.x * 2.0 + u_time) * 0.5 + 0.5;
                colorFactor += sin(p.y * 3.0 + u_time * 0.7) * 0.5 + 0.5;
                colorFactor += sin(p.z * 4.0 + u_time * 0.5) * 0.5 + 0.5;
                
                // Psychedelic color palette
                vec3 color = vec3(
                    sin(u_time * 0.3 + colorFactor * 3.14) * 0.5 + 0.5,
                    sin(u_time * 0.5 + colorFactor * 3.14) * 0.5 + 0.5,
                    sin(u_time * 0.7 + colorFactor * 3.14) * 0.5 + 0.5
                );
                
                // Apply lighting
                color *= (0.3 + 0.7 * diff);
                
                // Add some glow effect
                float glow = 1.0 - clamp(sceneSDF(p) * 2.0, 0.0, 1.0);
                color += vec3(glow * 0.5);
                
                return color;
            }
            
            void main() {
                // Normalize coordinates
                vec2 uv = (v_texCoord - 0.5) * 2.0;
                uv.x *= u_resolution.x / u_resolution.y;
                
                // Camera setup
                vec3 ro = vec3(0.0, 0.0, 3.0); // Ray origin
                vec3 rd = normalize(vec3(uv, -1.0)); // Ray direction
                
                // Ray marching parameters
                float t = 0.0;
                float maxDist = 100.0;
                float maxSteps = 100.0;
                float totalDist = 0.0;
                
                // Ray marching loop
                for (float i = 0.0; i < maxSteps; i++) {
                    vec3 p = ro + rd * t;
                    float d = sceneSDF(p);
                    totalDist = t;
                    
                    if (d < 0.001) {
                        // Hit surface
                        vec3 normal = calcNormal(p);
                        vec3 color = lighting(p, normal);
                        gl_FragColor = vec4(color, 1.0);
                        return;
                    }
                    
                    if (t > maxDist) {
                        // No hit - background
                        gl_FragColor = vec4(0.0, 0.0, 0.0, 1.0);
                        return;
                    }
                    
                    t += d;
                }
                
                // No hit - background
                gl_FragColor = vec4(0.0, 0.0, 0.0, 1.0);
            }
        `;

        // Compile shader
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

        // Create shader program
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
        
        // Set up vertex data for full-screen quad
        const positionBuffer = gl.createBuffer();
        gl.bindBuffer(gl.ARRAY_BUFFER, positionBuffer);
        const positions = [
            -1, -1,
             1, -1,
            -1,  1,
             1,  1,
        ];
        gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(positions), gl.STATIC_DRAW);
        
        const positionAttributeLocation = gl.getAttribLocation(program, 'a_position');
        gl.enableVertexAttribArray(positionAttributeLocation);
        gl.vertexAttribPointer(positionAttributeLocation, 2, gl.FLOAT, false, 0, 0);
        
        // Get uniform locations
        const timeUniformLocation = gl.getUniformLocation(program, 'u_time');
        const resolutionUniformLocation = gl.getUniformLocation(program, 'u_resolution');
        
        // Set resolution uniform
        gl.uniform2f(resolutionUniformLocation, canvas.width, canvas.height);
        
        // Animation loop
        let startTime = Date.now();
        function render() {
            const currentTime = (Date.now() - startTime) / 1000;
            gl.uniform1f(timeUniformLocation, currentTime);
            
            gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
            
            requestAnimationFrame(render);
        }
        
        render();
    </script>
</body>
</html>
```

## Key Features of this Implementation:

1. **Ray Marching Technique**: Implements a classic ray marching algorithm to render the metaball scene
2. **Smooth Minimum Function**: Uses the `smin` function to create organic, merging metaballs
3. **Dynamic Metaballs**: Multiple metaballs with positions and sizes that change over time
4. **Psychedelic Color Palette**: Vibrant, shifting colors based on position and time
5. **Lighting Model**: Basic lighting with diffuse shading and glow effects
6. **Responsive Design**: Automatically adjusts to window size changes
7. **Performance Optimized**: Efficient ray marching with early termination

The simulation creates a mesmerizing display of fluid, organic metaballs that merge, separate, and flow in a hypnotic pattern reminiscent of 1960s psychedelic light shows. The colors shift dynamically over time, creating a truly immersive visual experience.

The implementation uses only WebGL APIs directly without any external libraries, as requested. The scene is rendered using a full-screen quad with a fragment shader that performs all the ray marching calculations.

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: Qwen3-Coder-30B-A3B-Instruct-UD-Q6_K_XL.gguf -->
<!-- Prompt: lightshow.md -->
<!-- Generation Time: 30.31s -->
<!-- Fallback Used: False -->