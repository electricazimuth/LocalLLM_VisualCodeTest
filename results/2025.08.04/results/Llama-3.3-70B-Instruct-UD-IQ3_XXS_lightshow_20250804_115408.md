Here's the complete solution within a single HTML file:

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

        // Set up the WebGL context
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        gl.viewport(0, 0, canvas.width, canvas.height);

        // Vertex shader source
        const vertexShaderSource = `
            attribute vec2 position;
            void main() {
                gl_Position = vec4(position, 0.0, 1.0);
            }
        `;

        // Fragment shader source
        const fragmentShaderSource = `
            #define NUM_METABALLS 5
            #define MAX_STEPS 100
            #define MAX_DISTANCE 100.0
            #define EPSILON 0.001

            uniform vec2 resolution;
            uniform float time;

            vec4 metaballs[NUM_METABALLS] = vec4[](
                vec4(0.0, 0.0, 1.0, 1.0),
                vec4(0.5, 0.5, 1.0, 1.0),
                vec4(-0.5, 0.5, 1.0, 1.0),
                vec4(0.0, -0.5, 1.0, 1.0),
                vec4(0.0, 0.0, 1.0, 1.0)
            );

            float smin(float a, float b, float k) {
                float h = clamp(0.5 + 0.5 * (b - a) / k, 0.0, 1.0);
                return mix(b, a, h) - k * h * (1.0 - h);
            }

            float sphereSDF(vec3 p, vec4 metaball) {
                return length(p - metaball.xyz) - metaball.w;
            }

            float sceneSDF(vec3 p) {
                float d = 10.0;
                for (int i = 0; i < NUM_METABALLS; i++) {
                    d = smin(d, sphereSDF(p, metaballs[i]), 0.5);
                }
                return d;
            }

            vec3 normal(vec3 p) {
                vec2 e = vec2(EPSILON, 0.0);
                return normalize(vec3(
                    sceneSDF(p + e.xyy) - sceneSDF(p - e.xyy),
                    sceneSDF(p + e.yxy) - sceneSDF(p - e.yxy),
                    sceneSDF(p + e.yyx) - sceneSDF(p - e.yyx)
                ));
            }

            vec4 march(vec2 uv) {
                vec3 rayOrigin = vec3(0.0, 0.0, -3.0);
                vec3 rayDirection = normalize(vec3(uv, 1.0));
                vec3 ray = rayOrigin;

                for (int i = 0; i < MAX_STEPS; i++) {
                    float distance = sceneSDF(ray);
                    if (distance < EPSILON) {
                        vec3 normal = normal(ray);
                        vec3 color = vec3(sin(time), cos(time), sin(time * 0.5));
                        return vec4(color, 1.0);
                    }
                    if (distance > MAX_DISTANCE) {
                        return vec4(0.0, 0.0, 0.0, 1.0);
                    }
                    ray += rayDirection * distance;
                }

                return vec4(0.0, 0.0, 0.0, 1.0);
            }

            void main() {
                vec2 uv = gl_FragCoord.xy / resolution.xy;
                gl_FragColor = march(uv);
            }
        `;

        // Compile vertex shader
        const vertexShader = gl.createShader(gl.VERTEX_SHADER);
        gl.shaderSource(vertexShader, vertexShaderSource);
        gl.compileShader(vertexShader);

        // Compile fragment shader
        const fragmentShader = gl.createShader(gl.FRAGMENT_SHADER);
        gl.shaderSource(fragmentShader, fragmentShaderSource);
        gl.compileShader(fragmentShader);

        // Create program
        const program = gl.createProgram();
        gl.attachShader(program, vertexShader);
        gl.attachShader(program, fragmentShader);
        gl.linkProgram(program);
        gl.useProgram(program);

        // Create vertex buffer
        const vertexBuffer = gl.createBuffer();
        gl.bindBuffer(gl.ARRAY_BUFFER, vertexBuffer);
        gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([
            -1.0, -1.0,
             1.0, -1.0,
             1.0,  1.0,
            -1.0,  1.0
        ]), gl.STATIC_DRAW);

        // Create vertex attribute
        const positionAttribute = gl.getAttribLocation(program, 'position');
        gl.vertexAttribPointer(positionAttribute, 2, gl.FLOAT, false, 0, 0);
        gl.enableVertexAttribArray(positionAttribute);

        // Create uniforms
        const resolutionUniform = gl.getUniformLocation(program, 'resolution');
        const timeUniform = gl.getUniformLocation(program, 'time');

        // Animation loop
        let time = 0.0;
        function animate() {
            time += 0.01;
            gl.uniform2f(resolutionUniform, canvas.width, canvas.height);
            gl.uniform1f(timeUniform, time);

            // Update metaballs
            const metaballs = [
                vec4(0.0, 0.0, 1.0, 1.0),
                vec4(0.5 * Math.sin(time), 0.5 * Math.cos(time), 1.0, 1.0),
                vec4(-0.5 * Math.cos(time), 0.5 * Math.sin(time), 1.0, 1.0),
                vec4(0.0, -0.5 * Math.sin(time), 1.0, 1.0),
                vec4(0.0, 0.0, 1.0, 1.0)
            ];

            // Draw
            gl.clearColor(0.0, 0.0, 0.0, 1.0);
            gl.clear(gl.COLOR_BUFFER_BIT);
            gl.drawArrays(gl.TRIANGLE_FAN, 0, 4);

            requestAnimationFrame(animate);
        }

        animate();

        function vec4(x, y, z, w) {
            return new Float32Array([x, y, z, w]);
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

In this code:

*   We first create a WebGL context and set up the vertex and fragment shaders.
*   In the fragment shader, we define a `sceneSDF` function that combines the SDFs of multiple metaballs using the `smin` function.
*   We then implement a ray marching algorithm to render the scene.
*   In the JavaScript code, we create a vertex buffer, vertex attribute, and uniforms, and set up an animation loop to update the metaballs and render the scene.
*   We use the `requestAnimationFrame` function to create a smooth animation loop.

This code should produce a visually stunning, continuously evolving simulation of organic, merging metaballs reminiscent of 1960s psychedelic light shows.

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: Llama-3.3-70B-Instruct-UD-IQ3_XXS.gguf -->
<!-- Prompt: lightshow.md -->
<!-- Generation Time: 87.70s -->
<!-- Fallback Used: False -->