To create a visually stunning, continuously evolving simulation of merging metaballs using WebGL and ray marching, follow these steps:

1. **WebGL Setup**

First, set up a basic WebGL context and create a full-screen canvas. Then, compile and link the vertex and fragment shaders. Initialize necessary uniforms to pass data from JavaScript to the shaders, such as time, screen resolution, and metaball parameters.

```html
<script>
  // --- Standard WebGL Boilerplate ---
  const canvas = document.getElementById('glCanvas');
  const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');

  if (!gl) {
    alert('WebGL not supported');
    throw new Error('WebGL not supported');
  }

  // Vertex shader
  const vertexShaderSource = `
    attribute vec2 a_position;
    varying vec2 v_texCoord;
    void main() {
      gl_Position = vec4(a_position, 0.0, 1.0);
      v_texCoord = a_position * 0.5 + 0.5;
    }
  `;

  // Fragment shader
  const fragmentShaderSource = `
    precision mediump float;
    uniform mat4 u_matrix;
    uniform float u_time;
    uniform vec2 u_resolution;

    // Metaball parameters will be added here...

    // SDF and ray marching implementation will go here...

    void main() {
      // Shading and coloring will go here...
    }
  `;

  // Compile and link shaders...
</script>
```

2. **Ray Marching Implementation**

In the fragment shader, implement the core ray marching loop that iteratively steps a ray forward based on the distance estimated by the scene's SDF. Stop marching when the ray gets very close to a surface or exceeds a maximum distance/step count.

```html
<script>
  // Fragment shader
  const fragmentShaderSource = `
    precision mediump float;
    uniform mat4 u_matrix;
    uniform float u_time;
    uniform vec2 u_resolution;

    // Metaball parameters will be added here...

    float sphereSDF(vec3 p, float r) {
      return length(p) - r;
    }

    float metaballSDF(vec3 p) {
      float smin = smin(sphereSDF(p - v1, r1), sphereSDF(p - v2, r2), k);
      return smin;
    }

    void main() {
      vec2 uv = (gl_FragCoord.xy / u_resolution.xy);
      vec3 ro = vec3(0.0, 0.0, -5.0);
      vec3 rd = normalize(vec3(uv, 1.0));

      float t = 0.0;
      for (float d = 0.0; d < 50.0; d += 0.1) {
        vec3 pos = ro + t * rd;
        float dist = metaballSDF(pos);
        if (dist < 0.001) break;
        t += dist;
      }

      // Shading and coloring will go here...
    }
  `;
</script>
```

3. **SDF Scene Definition**

Define a Signed Distance Function (SDF) for a single sphere and represent multiple metaballs using this sphere SDF. Implement a smooth minimum function to combine the SDFs of individual metaballs, creating the characteristic organic merging effect.

```html
<script>
  // Fragment shader
  const fragmentShaderSource = `
    precision mediump float;
    uniform mat4 u_matrix;
    uniform float u_time;
    uniform vec2 u_resolution;

    // Metaball parameters
    uniform vec3 u_v1;
    uniform vec3 u_v2;
    uniform float u_r1;
    uniform float u_r2;
    uniform float u_k;

    float sphereSDF(vec3 p, float r) {
      return length(p) - r;
    }

    float smin(float a, float b, float k) {
      return -log(exp(-k * a) + exp(-k * b)) / k;
    }

    float metaballSDF(vec3 p) {
      return smin(sphereSDF(p - u_v1, u_r1), sphereSDF(p - u_v2, u_r2), u_k);
    }

    void main() {
      vec2 uv = (gl_FragCoord.xy / u_resolution.xy);
      vec3 ro = vec3(0.0, 0.0, -5.0);
      vec3 rd = normalize(vec3(uv, 1.0));

      float t = 0.0;
      for (float d = 0.0; d < 50.0; d += 0.1) {
        vec3 pos = ro + t * rd;
        float dist = metaballSDF(pos);
        if (dist < 0.001) break;
        t += dist;
      }

      // Shading and coloring will go here...
    }
  `;
</script>
```

4. **Shading and Coloring**

Determine the final pixel color based on the ray marching result. If a hit occurred, calculate the surface normal and implement basic lighting or assign color based on the closest metaball, distance traveled, or position. Use vibrant, shifting colors drawn from a psychedelic palette.

```html
<script>
  // Fragment shader
  const fragmentShaderSource = `
    precision mediump float;
    uniform mat4 u_matrix;
    uniform float u_time;
    uniform vec2 u_resolution;

    // Metaball parameters
    uniform vec3 u_v1;
    uniform vec3 u_v2;
    uniform float u_r1;
    uniform float u_r2;
    uniform float u_k;

    float sphereSDF(vec3 p, float r) {
      return length(p) - r;
    }

    float smin(float a, float b, float k) {
      return -log(exp(-k * a) + exp(-k * b)) / k;
    }

    float metaballSDF(vec3 p) {
      return smin(sphereSDF(p - u_v1, u_r1), sphereSDF(p - u_v2, u_r2), u_k);
    }

    void main() {
      vec2 uv = (gl_FragCoord.xy / u_resolution.xy);
      vec3 ro = vec3(0.0, 0.0, -5.0);
      vec3 rd = normalize(vec3(uv, 1.0));

      float t = 0.0;
      for (float d = 0.0; d < 50.0; d += 0.1) {
        vec3 pos = ro + t * rd;
        float dist = metaballSDF(pos);
        if (dist < 0.001) break;
        t += dist;
      }

      vec3 color = vec3(0.0);
      if (t < 50.0) {
        vec3 pos = ro + t * rd;
        vec3 normal = normalize(dFdx(pos) * rd.x + dFdy(pos) * rd.y);
        float lighting = max(dot(normal, vec3(0.0, 0.0, 1.0)), 0.0);
        color = mix(vec3(1.0, 0.0, 0.0), vec3(0.0, 0.0, 1.0), lighting);
      }

      gl_FragColor = vec4(color, 1.0);
    }
  `;
</script>
```

5. **Animation and Dynamics**

Use `requestAnimationFrame` in JavaScript to create the main loop and update uniforms each frame, especially the `time` uniform. Use the `time` uniform to dynamically change the positions, sizes, or colors of the metaballs over time, creating the swirling, evolving effect.

```html
<script>
  // Main loop
  function tick() {
    // Update uniforms...
    // gl.uniform1f(u_time, u_time + 0.01);

    // Render...
    gl.drawElements(gl.TRIANGLES, 6, gl.UNSIGNED_SHORT, 0);

    requestAnimationFrame(tick);
  }

  tick();
</script>
```

6. **Generative & Autonomous**

The simulation should run continuously and generate evolving patterns without user interaction after initialization.

By following these steps, you will create a visually stunning, continuously evolving simulation of merging metaballs using WebGL and ray marching, reminiscent of 1960s psychedelic light shows.

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: Mistral-Nemo-Instruct-2407-Q4_K_L.gguf -->
<!-- Prompt: lightshow.md -->
<!-- Generation Time: 24.63s -->
<!-- Fallback Used: False -->