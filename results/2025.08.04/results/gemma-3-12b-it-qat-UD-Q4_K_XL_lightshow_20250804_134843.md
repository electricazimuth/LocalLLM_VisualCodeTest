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

        const vs = `
            attribute vec2 position;
            varying vec2 uv;

            void main() {
                gl_Position = vec4(position, 1.0);
                uv = position * 0.5 + 0.5;
            }
        `;

        const fs = `
            precision mediump float;
            uniform float time;
            uniform vec2 resolution;
            uniform vec3 lightDir;

            // Sphere SDF
            float sphereSDF(vec3 p, float radius) {
                return length(p) - radius;
            }

            // Smooth Minimum
            float smin(float a, float b, float k) {
                return -log(exp(-k*a) + exp(-k*b))/k;
            }

            // Metaball SDF
            float metaballSDF(vec3 p) {
                float totalDist = 0.0;
                float k = 0.1;
                vec3 metaballPositions = vec3(0.5, 0.5, 0.5);
                float metaballRadii = 0.2;
                int numMetaballs = 3;

                for (int i = 0; i < numMetaballs; ++i) {
                    vec3 pos = metaballPositions + vec3(sin(time * (i + 1)), cos(time * (i + 2)), sin(time * (i + 3))) * 0.2;
                    totalDist = smin(totalDist, sphereSDF(p - pos, metaballRadii), k);
                }
                return totalDist;
            }

            // Ray Marching
            vec3 rayDirection(vec2 uv) {
                return normalize(vec3(uv - 0.5, 1.0));
            }

            vec3 rayOrigin() {
                return vec3(0.0, 0.0, 1.0);
            }

            vec3 getNormal(vec3 p) {
                float eps = 0.001;
                vec3 tangent = vec3(eps, 0.0, 0.0) + p;
                vec3 normal = normalize(vec3(
                    metaballSDF(tangent + vec3(0.0, eps, 0.0)) - metaballSDF(tangent - vec3(0.0, eps, 0.0)),
                    metaballSDF(tangent + vec3(eps, 0.0, 0.0)) - metaballSDF(tangent - vec3(eps, 0.0, 0.0)),
                    metaballSDF(tangent + vec3(0.0, 0.0, eps)) - metaballSDF(tangent - vec3(0.0, 0.0, eps))
                ));
                return normal;
            }


            void main() {
                vec2 uv = gl_FragCoord.xy / resolution;
                vec3 rayDir = rayDirection(uv);
                vec3 rayOrigin = rayOrigin();

                float t = 0.0;
                float maxDist = 1.0;
                float maxSteps = 64;

                vec3 currentPos = rayOrigin;
                for (int i = 0; i < maxSteps; ++i) {
                    float dist = metaballSDF(currentPos + rayDir * t);
                    if (dist < 0.001) {
                        vec3 normal = getNormal(currentPos + rayDir * t);
                        vec3 lightVector = normalize(lightDir);
                        float diffuse = max(0.0, dot(normal, lightVector));
                        vec3 color = vec3(0.2, 0.4, 0.6) * diffuse;

                        gl_FragColor = vec4(color, 1.0);
                        return;
                    }
                    t += dist;
                    currentPos += rayDir * t;

                    if (t > maxDist) {
                        gl_FragColor = vec4(0.0, 0.0, 0.0, 1.0);
                        return;
                    }
                }

                gl_FragColor = vec4(0.0, 0.0, 0.0, 1.0);
            }
        `;

        const vertexShader = vs;
        const fragmentShader = fs;

        const shaderProgram = gl.createProgram();
        gl.attachShader(shaderProgram, gl.createShader(gl.VERTEX_SHADER));
        gl.shaderSource(shaderProgram, [vertexShader]);
        gl.compileShader(shaderProgram);
        gl.attachShader(shaderProgram, gl.createShader(gl.FRAGMENT_SHADER));
        gl.shaderSource(shaderProgram, [fragmentShader]);
        gl.compileShader(shaderProgram);
        gl.linkProgram(shaderProgram);

        gl.useProgram(shaderProgram);

        const positionAttribute = gl.getAttribLocation(shaderProgram, 'position');
        gl.enableVertexAttribArray(positionAttribute);

        const vertices = [
            -1, -1,
            1, -1,
            1, 1,
            -1, 1
        ];
        const vertexBuffer = gl.createBuffer();
        gl.bindBuffer(gl.ARRAY_BUFFER, vertexBuffer);
        gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(vertices), gl.STATIC_DRAW);
        gl.vertexAttribPointer(positionAttribute, 2, gl.FLOAT, false, 0, 0);


        gl.uniform1f(gl.getUniformLocation(shaderProgram, 'time'), 0.0);
        gl.uniform2f(gl.getUniformLocation(shaderProgram, 'resolution'), canvas.width, canvas.height);
        gl.uniform3f(gl.getUniformLocation(shaderProgram, 'lightDir'), 0.5, 0.5, 0.5);

        gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);

        function render() {
            gl.useProgram(shaderProgram);
            gl.uniform1f(gl.getUniformLocation(shaderProgram, 'time'), Date.now() / 1000.0);
            gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
            requestAnimationFrame(render);
        }

        render();
    </script>

    <!-- Optional section for notes -->
    <!--
    <section id="notes">
        This implementation uses a basic ray marching algorithm to render metaballs.
        The SDF for a sphere is defined, and a smooth minimum function is used to
        combine the SDFs of multiple metaballs.  The ray direction and origin are
        calculated based on the fragment's UV coordinates.  The ray is marched
        until a hit is detected or a maximum distance is reached.
        Surface normals are approximated using central differences.
        Dynamic behavior is driven by updating the 'time' uniform each frame.
        The positions of metaballs are altered based on the time uniform.
        The lighting is simple diffuse shading based on a fixed light direction.
        Optimization considerations: SDF evaluation is the bottleneck.  Pre-computed
        tables or more efficient SDF approximations could improve performance.
    </section>
    -->
</body>
</html>
```

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: gemma-3-12b-it-qat-UD-Q4_K_XL.gguf -->
<!-- Prompt: lightshow.md -->
<!-- Generation Time: 28.64s -->
<!-- Fallback Used: False -->