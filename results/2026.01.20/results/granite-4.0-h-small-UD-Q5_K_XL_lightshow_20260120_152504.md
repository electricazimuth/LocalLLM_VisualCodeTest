Certainly! Below is an example solution that fulfills the requirements. This code includes the WebGL setup, the ray marching algorithm, the SDF scene definition with metaballs, and the animation using JavaScript to update the uniforms. It's a complex topic, so I've broken it down into manageable sections.

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

    <script type="x-shader/x-vertex" id="vertexShader">
        attribute vec3 position;
        varying vec2 vUv;
        void main() {
            vUv = position.xy * 0.5 + 0.5;
            gl_Position = vec4(position, 1.0);
        }
    </script>

    <script type="x-shader/x-fragment" id="fragmentShader">
        precision highp float;
        uniform float uTime;
        uniform vec2 uResolution;
        uniform vec3 metaballPositions[5];
        uniform float metaballRadii[5];
        uniform float metaballColors[5];

        varying vec2 vUv;

        // Smooth minimum function for blending SDFs
        float smin(float a, float b, float k) {
            float h = max(k - abs(a - b), 0.0) / k;
            return min(a, b) - h * h * k * (1.0 / 4.0);
        }

        // Sphere SDF
        float sphereSDF(vec3 p, vec3 c, float r) {
            return length(p - c) - r;
        }

        // Distance estimation function
        float distEstimation(vec3 p) {
            float d = 1e20; // large number for distance
            for (int i = 0; i < 5; i++) {
                // Combine metaball SDFs using smooth minimum
                d = smin(d, sphereSDF(p, metaballPositions[i], metaballRadii[i]), 0.5);
            }
            return d;
        }

        // Ray marching loop
        vec3 rayMarch(vec3 ro, vec3 rd) {
            float t = 0.0;
            float maxT = 100.0;
            float precision = 0.001;
            vec3 hit = vec3(0.0);
            for (int i = 0; i < 100; i++) {
                vec3 p = ro + rd * t;
                float d = distEstimation(p);
                if (d < precision || t > maxT) {
                    hit = p;
                    break;
                }
                t += d;
            }
            return hit;
        }

        // Calculate the normal at a point
        vec3 calcNormal(vec3 p) {
            float d = 0.0005;
            return normalize(vec3(
                distEstimation(p + vec3(d, 0.0, 0.0)) - distEstimation(p - vec3(d, 0.0, 0.0)),
                distEstimation(p + vec3(0.0, d, 0.0)) - distEstimation(p - vec3(0.0, d, 0.0)),
                distEstimation(p + vec3(0.0, 0.0, d)) - distEstimation(p - vec3(0.0, 0.0, d))
            ));
        }

        void main() {
            vec2 uv = vUv * 2.0 - 1.0; // Normalize screen coordinates
            vec3 ro = vec3(0.0, 0.0, 3.0); // Camera position
            vec3 rd = normalize(vec3(uv, -1.0)); // Ray direction

            vec3 hit = rayMarch(ro, rd);
            if (hit != vec3(0.0)) {
                vec3 n = calcNormal(hit); // Surface normal
                vec3 lightDir = normalize(vec3(1.0, 1.0, 1.0)); // Simple light direction
                float diff = max(dot(n, lightDir), 0.0); // Diffuse lighting
                vec3 color = vec3(1.0) * diff; // Base color
                // Vibrant, shifting colors
                color *= vec3(sin(uTime), cos(uTime), sin(uTime + 3.14));
                gl_FragColor = vec4(color, 1.0);
            } else {
                gl_FragColor = vec4(0.0, 0.0, 0.0, 1.0); // Background color
            }
        }
    </script>

    <script>
        const canvas = document.getElementById('glCanvas');
        const gl = canvas.getContext('webgl');

        // Compile shaders
        function compileShader(gl, type, source) {
            const shader = gl.createShader(type);
            gl.shaderSource(shader, source);
            gl.compileShader(shader);
            if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
                console.error('Shader compilation failed: ', gl.getShaderInfoLog(shader));
                gl.deleteShader(shader);
                throw new Error('Shader compilation failed');
            }
            return shader;
        }

        const vertexShaderSource = document.getElementById('vertexShader').text;
        const fragmentShaderSource = document.getElementById('fragmentShader').text;

        const vertexShader = compileShader(gl, gl.VERTEX_SHADER, vertexShaderSource);
        const fragmentShader = compileShader(gl, gl.FRAGMENT_SHADER, fragmentShaderSource);

        // Link shaders into a program
        const shaderProgram = gl.createProgram();
        gl.attachShader(shaderProgram, vertexShader);
        gl.attachShader(shaderProgram, fragmentShader);
        gl.linkProgram(shaderProgram);
        if (!gl.getProgramParameter(shaderProgram, gl.LINK_STATUS)) {
            console.error('Shader linking failed: ', gl.getProgramInfoLog(shaderProgram));
            throw new Error('Shader linking failed');
        }

        // Use the shader program
        gl.useProgram(shaderProgram);

        // Get uniform locations
        const uTime = gl.getUniformLocation(shaderProgram, 'uTime');
        const uResolution = gl.getUniformLocation(shaderProgram, 'uResolution');
        const metaballPositions = gl.getUniformLocation(shaderProgram, 'metaballPositions');
        const metaballRadii = gl.getUniformLocation(shaderProgram, 'metaballRadii');
        const metaballColors = gl.getUniformLocation(shaderProgram, 'metaballColors');

        // Create a full-screen quad
        const positions = new Float32Array([
            -1.0, -1.0,
            1.0, -1.0,
            -1.0, 1.0,
            1.0, 1.0
        ]);
        const positionBuffer = gl.createBuffer();
        gl.bindBuffer(gl.ARRAY_BUFFER, positionBuffer);
        gl.bufferData(gl.ARRAY_BUFFER, positions, gl.STATIC_DRAW);

        const positionAttributeLocation = gl.getAttribLocation(shaderProgram, 'position');
        gl.enableVertexAttribArray(positionAttributeLocation);
        gl.vertexAttribPointer(positionAttributeLocation, 2, gl.FLOAT, false, 0, 0);

        // Initialize metaball parameters
        const metaballs = 5;
        const metaballPositionsArray = new Float32Array(metaballs * 3);
        const metaballRadiiArray = new Float32Array(metaballs);
        const metaballColorsArray = new Float32Array(metaballs * 3);

        for (let i = 0; i < metaballs; i++) {
            metaballPositionsArray[i * 3] = Math.random() * 2.0 - 1.0;
            metaballPositionsArray[i * 3 + 1] = Math.random() * 2.0 - 1.0;
            metaballPositionsArray[i * 3 + 2] = Math.random() * 2.0 - 1.0;
            metaballRadiiArray[i] = Math.random() * 0.1 + 0.05;
            metaballColorsArray[i * 3] = Math.random();
            metaballColorsArray[i * 3 + 1] = Math.random();
            metaballColorsArray[i * 3 + 2] = Math.random();
        }

        // Animation loop
        function animate(time) {
            gl.uniform1f(uTime, time * 0.001);
            gl.uniform2f(uResolution, canvas.width, canvas.height);
            gl.uniform3fv(metaballPositions, metaballPositionsArray);
            gl.uniform1fv(metaballRadii, metaballRadiiArray);
            gl.uniform3fv(metaballColors, metaballColorsArray);

            // Clear the canvas
            gl.clear(gl.COLOR_BUFFER_BIT);

            // Draw the full-screen quad
            gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);

            requestAnimationFrame(animate);
        }

        animate(0);
    </script>
</body>
</html>
```

### Explanation:

1. **WebGL Setup:**
    - The full-screen canvas is initialized.
    - Shaders are compiled and linked into a WebGL program.
    - A full-screen quad is created and drawn.

2. **Ray Marching Implementation:**
    - The fragment shader implements the ray marching loop, iteratively stepping a ray from the camera into the scene.
    - The loop stops when a hit is detected or the maximum distance is reached.

3. **SDF Scene Definition:**
    - The `sphereSDF` function defines a single sphere.
    - The `distEstimation` function combines the SDFs of multiple metaballs using a smooth minimum function (`smin`).

4. **Shading and Coloring:**
    - The surface normal is calculated at the hit point.
    - Basic lighting is implemented using the surface normal and a simple light direction.
    - Vibrant, shifting colors are applied using trigonometric functions based on time.

5. **Animation and Dynamics:**
    - The `requestAnimationFrame` function is used to update the `uTime` uniform and animate the metaballs.
    - Metaball positions, radii, and colors are initialized randomly and can be further modified for more complex animations.

6. **Optimization and Desirable Features:**
    - Further optimization can be achieved by reducing the number of iterations in the ray marching loop or using more efficient SDF blending techniques.
    - Desirable features such as more sophisticated lighting models, noise functions, and additional post-processing effects can be added to enhance the visual quality.

This code provides a basic framework for creating a psychedelic metaball simulation using WebGL and ray marching. You can further customize and expand it to achieve the desired visual effects.

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: granite-4.0-h-small-UD-Q5_K_XL.gguf -->
<!-- Prompt: lightshow.md -->
<!-- Generation Time: 42.02s -->
<!-- Fallback Used: False -->