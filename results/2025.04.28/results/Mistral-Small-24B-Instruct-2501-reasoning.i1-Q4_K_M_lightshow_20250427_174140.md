<think>
Okay, so I need to create this psychedelic metaball simulation using WebGL and ray marching. Let me start breaking down the problem.

First, I know that WebGL requires a vertex and fragment shader. The vertex shader will handle passing positions to the fragment shader, and the fragment shader will do the heavy lifting with ray marching. Since we're going for a full-screen effect, the vertex shader can just pass through the screen coordinates.

The main challenge is the fragment shader. Ray marching involves casting a ray from the camera into the scene and stepping through it until we hit a surface or give up. The Signed Distance Function (SDF) defines the distance from any point to the surface, so we can use that to determine when we've hit something.

For the metaballs, each is a sphere in the SDF. To get the smooth merging, we need to combine multiple sphere SDFs using a smooth minimum (smin). The smin function will blend the distances from multiple spheres, creating the organic, merging look.

Let me recall the formula for a sphere SDF: distance = length(pos - center) - radius. For multiple spheres, we take the smin of each sphere's distance. The smin function is important here; a common choice is using the exponential form with a k parameter controlling the smoothness.

Once we have the combined SDF, the ray marching loop can step through the scene. At each step, we compute the distance to the surface, move the ray forward by that distance, and repeat until we either hit the surface (distance is below a threshold) or exceed the maximum steps.

For coloring, we can use the normal at the hit point, calculated via the gradient of the SDF. Then apply some basic lighting, but since it's psychedelic, maybe use more vibrant colors, possibly shifting over time. Alternatively, color based on the position or some noise function.

Now, the dynamics. Using the time uniform, we can animate the positions, radii, or colors of the metaballs. Maybe using sine waves or noise functions to create movement. For example, metaballs could oscillate or drift through space, changing size and color over time.

Let me start writing the shaders. The vertex shader is straightforward.

Vertex Shader (vertex.shader.glsl):
```glsl
precision mediump float;

void main() {
    gl_Position = vec4(0.5, 0.5, 1.0, 1.0);  // Full screen quad
}
```

Wait, no. Actually, to cover the entire screen, we need to use a quad that maps from -1 to 1 in both x and y. The vertex positions would be (-1, -1), (1, -1), (-1, 1), (1, 1), forming two triangles. But in a vertex shader, each vertex is assigned coordinates. Let's correct that.

Vertex Shader:
```glsl
attribute vec2 aPosition;
varying vec2 vUv;

void main() {
    vUv = aPosition;
    gl_Position = vec4(aPosition, 0.0, 1.0);
}
```

Wait, but in a full-screen quad, the positions are typically (-1, -1), (1, -1), (-1, 1), (1, 1). So the vertex shader would pass through the coordinates as texture coordinates (vUv). Then in the fragment shader, we can use vUv as the screen space coordinates. However, for ray marching, we need to map these 2D screen coordinates to a 3D ray direction.

Assuming a simple perspective camera, the ray direction can be computed from the screen coordinates. Let's set up the fragment shader.

Fragment Shader (fragment.shader.glsl):
```glsl
precision mediump float;

uniform vec2 uResolution;
uniform float uTime;
varying vec2 vUv;

const int MAX_STEPS = 100;
const float SURFACE_DISTANCE = 0.001;
const float MAX_DISTANCE = 100.0;
const float K = 5.0;  // Smooth min parameter

struct Sphere {
    vec3 center;
    float radius;
    vec3 color;
};

Sphere spheres[5];  // Let's say up to 5 spheres for example

vec3 getSphereSDF(vec3 pos, Sphere sphere) {
    return length(pos - sphere.center) - sphere.radius;
}

vec3 smin(vec3 a, vec3 b) {
    return -log(exp(-K * a) + exp(-K * b)) / K;
}

vec3 combineSDFs(vec3 pos) {
    vec3 total = getSphereSDFs(pos, spheres[0]);
    for (int i = 1; i < 5; i++) {
        total = smin(total, getSphereSDFs(pos, spheres[i]));
    }
    return total;
}

vec3 computeRayDirection(vec2 uv) {
    vec2 normalizedUV = (uv - 0.5) * 2.0;
    return vec3(normalizedUV, 1.0);  // Assume a simple perspective with z=1
}

vec3 rayMarch(vec3 ro, vec3 rd) {
    vec3 p = ro;
    for (int i = 0; i < MAX_STEPS; i++) {
        vec3 dist = combineSDFs(p);
        if (dist.z < SURFACE_DISTANCE) {  // Assuming the combined SDF returns the distance in z component? Wait, no, need to clarify.

Wait, maybe each sphere's SDF is a distance, and the combined SDF is the smooth minimum of all distances. So, the combined SDF gives the distance to the closest surface.

But in the combineSDFs function, we need to return the smooth minimum of all sphere distances.

Wait, perhaps each getSphereSDF returns a vec3 where x, y, z are distances for each sphere? No, that's overcomplicating. Let's think again.

Each sphere contributes a distance value. The smin function combines two distances into a smooth minimum. So, if we have multiple spheres, we iteratively apply smin to combine all distances.

But how is the smin defined? Let's recall the formula.

smin(a, b, k) = - (ln(exp(-k a) + exp(-k b)) ) / k

This is the smooth minimum of a and b with strength k. So, for combining multiple distances, we can iteratively apply smin.

But in GLSL, we can't have a loop over arbitrary elements, but since we know the number of spheres (let's say 5), we can apply smin sequentially.

But wait, the problem is that smin takes two distances at a time. So, to combine five spheres, we'd do smin(smin(smin(smin(d1, d2), d3), d4), d5).

But in the code above, we have:

vec3 combineSDFs(vec3 pos) {
    vec3 total = getSphereSDF(pos, spheres[0]);
    for (int i = 1; i < 5; i++) {
        total = smin(total, getSphereSDF(pos, spheres[i]));
    }
    return total;
}

But this assumes that smin is defined for vec3. Wait, no, the SDF for each sphere is a scalar distance. So perhaps total should be a scalar, not vec3. Wait, confusion here.

Hold on. Let's correct this. Each sphere's SDF is a scalar distance. The smooth minimum combines these scalar distances into a single scalar distance. Then, during ray marching, we step based on this scalar distance.

But in the code above, the combineSDFs function is supposed to return a vec3. That seems incorrect. Let me fix this.

Let me redefine combineSDFs to return a scalar distance.

First, let's correct the sphere structure. Each sphere has a center, radius, and maybe color.

Then, the SDF for a single sphere is length(pos - center) - radius.

The smooth minimum combines all the scalar distances. So, combineSDFs should return a scalar.

Therefore, the smin function is a scalar function.

But in the initial code, the smin was defined as returning a vec3. That's incorrect. Let me correct that.

First, define the smin function properly:

scalar smin(scalar a, scalar b, scalar k) {
    return - (ln(exp(-k a) + exp(-k b)) ) / k;
}

Then, the combineSDFs function would be:

scalar combineSDFs(vec3 pos) {
    scalar total = getSphereSDF(pos, spheres[0]);
    for (int i = 1; i < 5; i++) {
        total = smin(total, getSphereSDF(pos, spheres[i]), K);
    }
    return total;
}

But in GLSL, we can't have a loop with a variable number of iterations, but since we know the number of spheres (let's say 5), it's okay.

Wait, but in GLSL, for loops with constant bounds are allowed. So, we can loop from 1 to 5.

Therefore, the combineSDFs function becomes:

scalar combineSDFs(vec3 pos) {
    scalar total = getSphereSDF(pos, spheres[0]);
    for (int i = 1; i < 5; i++) {
        total = smin(total, getSphereSDF(pos, spheres[i]), K);
    }
    return total;
}

Okay, now the combineSDFs returns a scalar distance.

Then, in the rayMarch function, we can use this scalar distance to step through the scene.

So, the rayMarch function would be:

scalar rayMarch(vec3 ro, vec3 rd, out vec3 hitColor) {
    vec3 p = ro;
    for (int i = 0; i < MAX_STEPS; i++) {
        scalar d = combineSDFs(p);
        if (d < SURFACE_DISTANCE) {
            // Hit surface
            hitColor = computeColor(p, rd);  // Compute color based on position, normal, etc.
            return 1.0;  // Indicate hit
        }
        if (d > MAX_DISTANCE) {
            break;
        }
        p += rd * d;  // Step forward by distance d
    }
    return 0.0;  // No hit
}

Then, in the fragment shader's main function:

void main() {
    vec2 uv = vUv;
    vec3 ro = vec3(0, 0, 1);  // Camera position at (0,0,1)
    vec3 rd = computeRayDirection(uv);  // Compute ray direction from UV
    vec3 hitColor = vec3(0.0);
    scalar hit = rayMarch(ro, rd, hitColor);
    if (hit == 1.0) {
        gl_FragColor = vec4(hitColor, 1.0);
    } else {
        gl_FragColor = vec4(0.0, 0.0, 0.0, 1.0);  // Background color
    }
}

Now, the computeColor function needs to determine the color at the hit point. To get the normal, we can perturb the position slightly in each axis and compute the gradient.

Alternatively, since the SDF's gradient is the normal. The gradient of the SDF at point p is the unit normal vector.

Therefore, computeNormal(vec3 p) {
    vec3 epsilon = vec3(0.001, 0.001, 0.001);
    return normalize(vec3(
        combineSDFs(p + epsilon.xyz) - combineSDFs(p - epsilon.xyz),
        combineSDFs(p + epsilon.yxz) - combineSDFs(p - epsilon.yxz),
        combineSDFs(p + epsilon.zyx) - combineSDFs(p - epsilon.zyx)
    ));
}

But this computation would be noisy and expensive. Alternatively, since the SDF is composed of multiple spheres, the normal can be computed as the sum of the gradients of each sphere's SDF, weighted by their contribution.

Wait, but since we have a smooth minimum of the SDFs, the gradient of the combined SDF is not straightforward. The smooth minimum's gradient would be a combination of the gradients of the individual SDFs, but the exact formula depends on the derivative of the smin function.

This might get complicated. Alternatively, since the smooth minimum approximates the minimum of the SDFs, the gradient would be the gradient of the closest sphere, but weighted by the smoothness.

Alternatively, maybe we can approximate the normal by using the gradient of the combined SDF. Let's try the central difference approach for the normal.

But in the fragment shader, doing this would require 6 additional SDF calls (for each axis perturbation), which is expensive. However, since we are already doing a lot of computations, maybe it's feasible.

Alternatively, we can use the fact that the normal is the gradient of the SDF, so:

normal = gradient(SDF(p)) = (d/SDF/dx, d/SDF/dy, d/SDF/dz)

But computing these partial derivatives in GLSL would require finite differences as above.

Let me define the computeNormal function:

vec3 computeNormal(vec3 p) {
    const float h = 0.001;
    vec3 n = vec3(0.0);
    n.x = combineSDFs(p + vec3(h, 0, 0)) - combineSDFs(p - vec3(h, 0, 0));
    n.y = combineSDFs(p + vec3(0, h, 0)) - combineSDFs(p - vec3(0, h, 0));
    n.z = combineSDFs(p + vec3(0, 0, h)) - combineSDFs(p - vec3(0, 0, h));
    return normalize(n);
}

But this adds 6 SDF calls per normal computation, which might be too much. Alternatively, we can use the fact that the SDF is a sum of spheres, and compute the gradient as the sum of the gradients of each sphere. But with the smooth minimum, this isn't straightforward. However, maybe the gradient of the smooth minimum is the weighted sum of the gradients of the individual SDFs, weighted by the contribution of each sphere.

But this requires more advanced calculus. Let me recall that the gradient of the smooth minimum would be:

If F = smin(f1, f2, k), then gradient F = (exp(-k f1) / (exp(-k f1) + exp(-k f2))) * gradient f1 + (exp(-k f2) / (exp(-k f1) + exp(-k f2))) * gradient f2

But for multiple terms, this extends similarly. So, in general, the gradient would be a weighted sum of the gradients of each individual SDF, with weights depending on their distance.

This would be computationally intensive, but perhaps manageable.

Alternatively, maybe we can approximate the normal by looking at the closest sphere. If the combined SDF is dominated by one sphere near the hit point, then the normal would be approximately the normal of that sphere.

But given the smooth minimum, the transition between spheres is smooth, so the normal would be a combination. However, calculating this exactly would be complex.

Given the complexity, maybe it's better to precompute the normal as part of the ray marching loop, using the finite difference method. Even though it's 6 SDF calls, it might be necessary for the visual effect. However, this would significantly slow down the shader.

Alternatively, since the problem asks for a psychedelic effect, maybe we can forgo accurate normals and instead use a simple color based on the position or time.

For example, color the metaballs based on their position or a function of time, creating a shifting color effect. This might be simpler and still achieve the desired visual.

Let me try this approach. Suppose each metaball has a color that changes over time. The color could be a function of the metaball's position or a global time variable. For example, using a hue that shifts based on the z-coordinate or time.

Alternatively, use a color gradient based on the distance from the camera or the height (y-coordinate). For a more dynamic look, incorporate the time uniform into the color calculation.

Let me define the computeColor function as follows:

vec3 computeColor(vec3 p, vec3 normal) {
    // Example: color based on y-coordinate and time
    float y = (p.y + 1.0) / 2.0;  // Map y from [-1,1] to [0,1]
    float t = (uTime + p.z) / 10.0;  // Mix time and z-coordinate
    vec3 color = vec3(y + sin(t), y + cos(t), y + sin(t + 1.0));
    return color;
}

Alternatively, since we have the normal, we can use basic Lambertian shading with a changing light direction over time.

vec3 computeColor(vec3 p, vec3 normal) {
    vec3 lightDir = vec3(sin(uTime), cos(uTime), 0.5);  // Rotating light
    lightDir = normalize(lightDir);
    float diff = max(dot(normal, lightDir), 0.0);
    vec3 color = vec3(diff, diff, diff) + vec3(0.1, 0.0, 0.1);  // Basic color with a magenta tint
    return color;
}

This would give a simple shading where the color varies based on the angle of the rotating light.

Alternatively, to achieve more vibrant, shifting colors, we can use the time and position to generate a color via a function like hsv2rgb with hue derived from time or position.

For example:

vec3 computeColor(vec3 p) {
    float h = (p.x + uTime) / 10.0;  // Hue based on x-coordinate and time
    float s = 1.0;  // Full saturation
    float v = 1.0;  // Full value
    vec3 color = hsv2rgb(h, s, v);
    return color;
}

This would create a color that shifts over time and varies with the x-coordinate, leading to a rainbow-like effect.

The hsv2rgb function can be defined in GLSL as follows:

vec3 hsv2rgb(vec3 c) {
    vec4 K = vec4(1.0, 2.0/3.0, 1.0/3.0, 3.0);
    vec3 p = abs(fract(c.x * K.x + K.w * (c.y * K.x + c.z * K.y)) * K.z - K.w) - K.x;
    return c.z * mix(K.x + p.x, K.x + p.y, step(p.x, p.y)) + c.y * mix(K.x + p.z, K.x + p.w, step(p.z, p.w)) + c.x * mix(K.x + p.x + p.z, K.x + p.x + p.w, step(p.z, p.w));
}

But this might be overcomplicating. Alternatively, use a simpler hsv2rgb conversion:

vec3 hsv2rgb(float h, float s, float v) {
    h = h - floor(h);
    if (h < 1/3.0) {
        return vec3(3h, 1 - h, 1 - h) * v * (1 - s) + vec3(1, 1, 1) * v * s;
    } else if (h < 2/3.0) {
        h = h - 1/3.0;
        return vec3(1 - h, 3h, 1 - h) * v * (1 - s) + vec3(1, 1, 1) * v * s;
    } else {
        h = h - 2/3.0;
        return vec3(1 - h, 1 - h, 3h) * v * (1 - s) + vec3(1, 1, 1) * v * s;
    }
}

This function converts HSB (HSV) to RGB. Using this, we can create a color that shifts based on the time and position.

Now, putting it all together, the fragment shader would look like:

Fragment Shader (fragment.shader.glsl):
```glsl
precision mediump float;

uniform vec2 uResolution;
uniform float uTime;
uniform K;  // Smooth min parameter
uniform spheres[5];  // Spheres array

varying vec2 vUv;

const int MAX_STEPS = 100;
const float SURFACE_DISTANCE = 0.001;
const float MAX_DISTANCE = 100.0;

vec3 getSphereSDF(vec3 pos, Sphere sphere) {
    return length(pos - sphere.center) - sphere.radius;
}

float smin(float a, float b, float k) {
    return -log(exp(-k * a) + exp(-k * b)) / k;
}

float combineSDFs(vec3 pos) {
    float total = getSphereSDF(pos, spheres[0]);
    for (int i = 1; i < 5; i++) {
        total = smin(total, getSphereSDF(pos, spheres[i]), K);
    }
    return total;
}

vec3 computeRayDirection(vec2 uv) {
    vec2 normalizedUV = (uv - 0.5) * 2.0;
    return vec3(normalizedUV, 1.0);  // Perspective projection
}

vec3 computeColor(vec3 p) {
    float h = (p.x + uTime) / 10.0;
    vec3 color = hsv2rgb(h, 1.0, 1.0);
    return color;
}

vec3 hsv2rgb(float h, float s, float v) {
    h = h - floor(h);
    if (h < 1/3.0) {
        return vec3(3h, 1 - h, 1 - h) * v * (1 - s) + vec3(1, 1, 1) * v * s;
    } else if (h < 2/3.0) {
        h = h - 1/3.0;
        return vec3(1 - h, 3h, 1 - h) * v * (1 - s) + vec3(1, 1, 1) * v * s;
    } else {
        h = h - 2/3.0;
        return vec3(1 - h, 1 - h, 3h) * v * (1 - s) + vec3(1, 1, 1) * v * s;
    }
}

void main() {
    vec2 uv = vUv;
    vec3 ro = vec3(0, 0, 1);  // Camera at (0,0,1)
    vec3 rd = computeRayDirection(uv); 
    vec3 p = ro;
    vec3 hitColor = vec3(0.0);
    for (int i = 0; i < MAX_STEPS; i++) {
        float d = combineSDFs(p);
        if (d < SURFACE_DISTANCE) {
            hitColor = computeColor(p);
            break;
        }
        if (d > MAX_DISTANCE) break;
        p += rd * d;
    }

    gl_FragColor = vec4(hitColor, 1.0);
}
```

Now, the vertex shader passes the UV coordinates to the fragment shader. The fragment shader computes the ray direction, casts the ray, and computes the color if a surface is hit. The color is determined by the position and time, creating a shifting hue effect.

Next, we need to set up the JavaScript to initialize the shaders, uniforms, and animation.

JavaScript (included in the HTML):
```html
    <script>
        const vertexShaderSource = `
            precision mediump float;
            attribute vec2 aPosition;
            varying vec2 vUv;
            void main() {
                vUv = aPosition;
                gl_Position = vec4(aPosition, 0.0, 1.0);
            }
        `;

        const fragmentShaderSource = `
            precision mediump float;
            uniform vec2 uResolution;
            uniform float uTime;
            uniform float K;
            uniform spheres[5]; 
            varying vec2 vUv;

            struct Sphere { vec3 center; float radius; vec3 color; };

            vec3 getSphereSDF(vec3 pos, Sphere sphere) { return length(pos - sphere.center) - sphere.radius; }
            float smin(float a, float b, float k) { return -log(exp(-k * a) + exp(-k * b)) / k; }
            float combineSDFs(vec3 pos) { float total = getSphereSDF(pos, spheres[0]); for (int i=1; i<5; i++) total = smin(total, getSphereSDF(pos, spheres[i]), K); return total; }

            vec3 computeRayDirection(vec2 uv) { vec2 normalizedUV = (uv - 0.5) * 2.0; return vec3(normalizedUV, 1.0); }
            vec3 computeColor(vec3 p) { float h = (p.x + uTime)/10.0; vec3 color = hsv2rgb(h, 1.0, 1.0); return color; }

            vec3 hsv2rgb(float h, float s, float v) { ... }  // As defined earlier

            void main() { ... }  // As defined earlier
        `;

        let gl, program, spheresUniform, timeUniform, kUniform, resolutionUniform;

        function createSphere(center, radius, color) {
            return { center, radius, color };
        }

        function initSpheres() {
            const spheres = [];
            for (let i = 0; i < 5; i++) {
                spheres[i] = createSphere(
                    vec3((Math.random() - 0.5) * 2, (Math.random() - 0.5) * 2, (Math.random() - 0.5) * 2), 
                    Math.random() * 0.5 + 0.5, 
                    vec3(Math.random(), Math.random(), Math.random())
                );
            }
            return spheres;
        }

        function createShaders() {
            const vertexShader = gl.createShader(gl.VERTEX_SHADER);
            gl.shaderSource(vertexShader, vertexShaderSource);
            gl.compileShader(vertexShader);
            if (!gl.getShaderParameter(vertexShader, gl.COMPILE_STATUS)) {
                console.error(gl.getShaderInfoLog(vertexShader));
                return null;
            }

            const fragmentShader = gl.createShader(gl.FRAGMENT_SHADER);
            gl.shaderSource(fragmentShader, fragmentShaderSource);
            gl.compileShader(fragmentShader);
            if (!gl.getShaderParameter(fragmentShader, gl.COMPILE_STATUS)) {
                console.error(gl.getShaderInfoLog(fragmentShader));
                return null;
            }

            program = gl.createProgram();
            gl.attachShader(program, vertexShader);
            gl.attachShader(program, fragmentShader);
            gl.linkProgram(program);
            if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
                console.error(gl.getProgramInfoLog(program));
                return null;
            }

            gl.useProgram(program);

            program.aPosition = gl.getAttribLocation(program, 'aPosition');
            gl.enableVertexAttribArray(program.aPosition);

            const positionBuffer = gl.createBuffer();
            gl.bindBuffer(gl.ARRAY_BUFFER, positionBuffer);
            gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 1, -1, -1, 1, 1, 1]), gl.STATIC_DRAW);
            gl.vertexAttribPointer(program.aPosition, 2, gl.FLOAT, false, 0, 0);

            spheresUniform = gl.getUniformLocation(program, 'spheres');
            timeUniform = gl.getUniformLocation(program, 'uTime');
            kUniform = gl.getUniformLocation(program, 'K');
            resolutionUniform = gl.getUniformLocation(program, 'uResolution');
        }

        function setUniforms() {
            gl.uniform2f(resolutionUniform, gl.canvas.width, gl.canvas.height);
            gl.uniform1f(kUniform, 5.0);  // K value for smooth minimum
            const time = performance.now() / 1000;
            gl.uniform1f(timeUniform, time);

            const spheres = initSpheres();
            gl.uniform3fv(spheresUniform, spheres.flatMap(s => [s.center.x, s.center.y, s.center.z, s.radius, s.color.x, s.color.y, s.color.z]));
        }

        function render() {
            gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);
            setUniforms();
            gl.drawArrays(gl.TRIANGLES, 0, 6);
            requestAnimationFrame(render);
        }

        function main() {
            gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
            if (!gl) {
                alert('WebGL not supported');
                return;
            }

            createShaders();
            setUniforms();
            render();
        }

        window.onload = main;
    </script>
```

This JavaScript sets up the WebGL context, compiles the shaders, and initializes the uniforms. The spheres are randomly generated with centers in the range [-1, 1]^3, radii between 0.5 and 1.0, and colors as random RGB values. The uniforms are updated each frame with the current time and other parameters. The `render` function is called recursively via `requestAnimationFrame` to create the animation.

This setup should create a dynamic, ever-changing simulation of merging metaballs with shifting colors, achieving the desired psychedelic effect. The key components are the smooth minimum for blending the spheres, the ray marching loop for rendering the volumes, and the time-based animation for dynamics.

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: Mistral-Small-24B-Instruct-2501-reasoning.i1-Q4_K_M.gguf -->
<!-- Prompt: lightshow.md -->
<!-- Generation Time: 524.86s -->
<!-- Fallback Used: False -->