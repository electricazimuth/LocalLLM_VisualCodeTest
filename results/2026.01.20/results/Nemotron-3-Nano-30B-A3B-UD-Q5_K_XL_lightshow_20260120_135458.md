Below is a **single‑file** WebGL demo that satisfies every requirement in the brief.  
Save the whole snippet as `index.html` and open it in any modern browser (Chrome, Edge, Firefox, Safari). No external libraries are used – only the WebGL 1 API.

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Ray‑Marched Metaballs – Psychedelic 60s Light Show</title>
    <style>
        body { margin:0; overflow:hidden; background:#000; }
        canvas { display:block; width:100vw; height:100vh; }
    </style>
</head>
<body>
    <canvas id="glCanvas"></canvas>

    <!-- --------------------------------------------------------------
         1️⃣  WebGL Boilerplate + Shader Sources
         -------------------------------------------------------------- -->
    <script>
        // ----- Grab canvas & initialise WebGL --------------------------------
        const canvas = document.getElementById('glCanvas');
        const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
        if (!gl) throw new Error('WebGL not supported');

        // Resize canvas to match the actual window size
        function resize() {
            canvas.width  = window.innerWidth;
            canvas.height = window.innerHeight;
            gl.viewport(0,0,canvas.width,canvas.height);
        }
        window.addEventListener('resize', resize);
        resize();

        // ----- Vertex shader – passes a full‑screen quad ----------------------
        const vsSource = `
            attribute vec2 a_position;
            void main() {
                // a_position runs from -1..1 in both axes → covers NDC
                gl_Position = vec4(a_position, 0.0, 1.0);
            }
        `;

        // ----- Fragment shader – ray marching + SDF + psychedelic colour ---
        const fsSource = `
            precision highp float;

            // ---------- Uniforms ------------------------------------------------
            uniform vec2 u_resolution;   // canvas size
            uniform float u_time;        // elapsed seconds
            uniform float u_k;           // smooth‑min factor (used for blending)

            // ---------- Helper functions ----------------------------------------
            // Signed distance to a sphere of radius r centred at 'c'
            float sdSphere(vec3 p, vec3 c, float r) {
                return length(p - c) - r;
            }

            // Smooth minimum of two floats (k controls sharpness)
            float smin(float a, float b, float k) {
                vec2 h = vec2(a,b);
                return -log(exp(-k*h.x) + exp(-k*h.y)) / k;
            }

            // Convert HSV (h in [0,1]) to RGB – simple approximation
            vec3 hsv2rgb(float h) {
                float r = mod(h + 0.0/3.0, 1.0);
                float g = mod(h + 2.0/3.0, 1.0);
                float b = mod(h + 4.0/3.0, 1.0);
                return vec3(r,g,b);
            }

            // ---------- Scene SDF – many metaballs -----------------------------
            // Number of metaballs (hard‑coded for simplicity)
            const int N = 5;

            // Returns the distance to the whole metaball structure
            float sceneSDF(vec3 p) {
                float d = 1e30;                 // start with “infinity”
                for (int i=0; i<N; i++) {
                    // ---- animate each ball -------------------------------------------------
                    float a   = u_time + float(i) * 0.3;               // phase
                    vec2  off = vec2(cos(a + float(i)*0.8), sin(a + float(i)*0.8)) * 0.2;
                    float r   = 0.1 + 0.04 * sin(u_time*0.5 + float(i)); // pulsating radius

                    vec3  centre = vec3(off.x, off.y, 0.0);
                    float dist   = sdSphere(p, centre, r);
                    // ---- blend with smooth‑min -------------------------------------------
                    d = smin(d, dist, u_k);
                }
                return d;
            }

            // ---------- Ray marching ------------------------------------------------
            const int   MAX_STEPS = 128;
            const float MAX_DIST  = 20.0;
            const float EPS       = 0.001;

            void main() {
                // ---- Normalised pixel coordinates (0‑1) ---------------------------------
                vec2 uv = gl_FragCoord.xy / u_resolution.xy;
                // map to [-1,1] and add a little perspective feel
                vec2 ndc = uv * 2.0 - 1.0;
                float aspect = u_resolution.x / u_resolution.y;
                vec3  ro = vec3(0.0, 0.0, 0.0);                     // ray origin (camera)
                vec3  rd = normalize(vec3(ndc.x * aspect, ndc.y, -1.0)); // look down -Z

                // ---- Ray marching -------------------------------------------------------
                float t = 0.0;
                bool  hit = false;
                vec3  hitPos = vec3(0);
                for (int i=0; i<MAX_STEPS; i++) {
                    if (t > MAX_DIST) break;
                    vec3 p = ro + rd * t;
                    float d = sceneSDF(p);
                    if (d < EPS) {               // we are (almost) inside the surface
                        hit = true;
                        hitPos = p;
                        break;
                    }
                    t += d;                       // step by the distance field
                }

                // ---- Background ---------------------------------------------------------
                vec3 col = vec3(0.0);             // black if we missed everything

                // ---- Shading when we hit ------------------------------------------------
                if (hit) {
                    // Approximate normal by central differences
                    vec3 normal = vec3(
                        sceneSDF(hitPos + vec3(EPS,0,0)) - sceneSDF(hitPos - vec3(EPS,0,0)),
                        sceneSDF(hitPos + vec3(0,EPS,0)) - sceneSDF(hitPos - vec3(0,EPS,0)),
                        sceneSDF(hitPos + vec3(0,0,EPS)) - sceneSDF(hitPos - vec3(0,0,EPS))
                    );
                    normal = normalize(normal);

                    // Psychedelic colour – hue drifts with time and position
                    float hue = mod(u_time*0.1 + normal.x*2.0 + normal.y*3.0, 1.0);
                    col = hsv2rgb(hue);          // vivid, constantly shifting palette

                    // Simple rim‑light effect for extra glow
                    float rim = 1.0 - dot(normal, vec3(0,0,1));
                    col = mix(col, col*2.0, pow(rim, 3.0));
                }

                // ---- Output -------------------------------------------------------------
                gl_FragColor = vec4(col, 1.0);
            }
        `;

        // ----- Compile shaders ----------------------------------------------------
        function compileShader(src, type) {
            const sh = gl.createShader(type);
            gl.shaderSource(sh, src);
            gl.compileShader(sh);
            if (!gl.getShaderParameter(sh, gl.COMPILE_STATUS)) {
                console.error('Shader compile error:', gl.getShaderInfoLog(sh));
                gl.deleteShader(sh);
                return null;
            }
            return sh;
        }

        const vertShader = compileShader(vsSource, gl.VERTEX_SHADER);
        const fragShader = compileShader(fsSource, gl.FRAGMENT_SHADER);

        // ----- Link program -------------------------------------------------------
        const program = gl.createProgram();
        gl.attachShader(program, vertShader);
        gl.attachShader(program, fragShader);
        gl.linkProgram(program);
        if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
            console.error('Program link error:', gl.getProgramInfoLog(program));
        }
        gl.useProgram(program);

        // ----- Set up full‑screen quad -------------------------------------------
        // 4 vertices: (-1,-1), (1,-1), (-1,1), (1,1)
        const quad = new Float32Array([
            -1,-1,
             1,-1,
            -1, 1,
             1, 1
        ]);
        const posBuf = gl.createBuffer();
        gl.bindBuffer(gl.ARRAY_BUFFER, posBuf);
        gl.bufferData(gl.ARRAY_BUFFER, quad, gl.STATIC_DRAW);

        const aPos = gl.getAttribLocation(program, 'a_position');
        gl.enableVertexAttribArray(aPos);
        gl.vertexAttribPointer(aPos, 2, gl.FLOAT, false, 0, 0);

        // ----- Uniform locations ---------------------------------------------------
        const uniResolution = gl.getUniformLocation(program, 'u_resolution');
        const uniTime       = gl.getUniformLocation(program, 'u_time');
        const uniK          = gl.getUniformLocation(program, 'u_k');

        // ----- Animation loop ------------------------------------------------------
        let start = performance.now();
        function render(now) {
            now *= 0.001;                     // convert to seconds
            const elapsed = now - start;

            // Update uniforms
            gl.uniform2f(uniResolution, canvas.width, canvas.height);
            gl.uniform1f(uniTime, elapsed);
            gl.uniform1f(uniK, 32.0);         // smooth‑min sharpness (feel free to animate)

            // Clear to black
            gl.clearColor(0.0, 0.0, 0.0, 1.0);
            gl.clear(gl.COLOR_BUFFER_BIT);

            // Draw the quad (2 triangles)
            gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);

            requestAnimationFrame(render);
        }
        requestAnimationFrame(render);
    </script>
</body>
</html>
```

### How It Works (quick walk‑through)

| Step | What the code does |
|------|--------------------|
| **1️⃣ Boilerplate** | Creates a full‑screen canvas, grabs a WebGL context, and resizes it to the window size. |
| **2️⃣ Shaders** | *Vertex* just emits four vertices that form a quad covering `[-1,1]²` in NDC. *Fragment* contains the whole psychedelic pipeline. |
| **3️⃣ SDF & Metaballs** | `sceneSDF()` builds a distance field for **5** spheres whose positions, radii and phases are animated with `u_time`. The `smin` function smoothly blends them, giving the characteristic “merging” look. |
| **4️⃣ Ray Marching** | For each pixel we cast a ray (`ro` + `t·rd`) and march forward, stepping by the distance returned from `sceneSDF`. When the distance drops below a tiny epsilon we consider it a hit. |
| **5️⃣ Normal & Colour** | The surface normal is approximated by central differences. Colour is derived from a hue that depends on time and the normal, converted to RGB via a tiny HSV→RGB helper (`hsv2rgb`). A rim‑light term adds extra glow. |
| **6️⃣ Animation** | `requestAnimationFrame` drives the loop; the elapsed time uniform is updated each frame, causing the metaballs to pulsate, orbit and continuously reshape. |
| **7️⃣ No external libs** | Everything is pure WebGL 1 + GLSL, packaged in a single HTML file. |

Feel free to tweak parameters (`u_k`, number of metaballs, colour formulas, etc.) to explore different psychedelic patterns. Enjoy the trippy, ever‑evolving light‑show!

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: Nemotron-3-Nano-30B-A3B-UD-Q5_K_XL.gguf -->
<!-- Prompt: lightshow.md -->
<!-- Generation Time: 40.41s -->
<!-- Fallback Used: False -->