<think>
Okay, I need to create a WebGL ray marching simulation of psychedelic metaballs. Let's start by understanding the requirements. The core is ray marching with SDFs and smooth merging using smin. The metaballs should move and change over time, creating a fluid, organic effect.

First, the WebGL setup. I'll need to create a full-screen canvas, initialize the WebGL context, and set up a vertex shader that just passes through coordinates. The fragment shader will handle all the ray marching logic.

For the vertex shader, it's straightforward. I'll take in a position attribute, pass through the UV coordinates (which are the pixel coordinates), and set gl_Position to the transformed position. Since it's a full-screen quad, the positions can be from -1 to 1 in both x and y.

Now the fragment shader. The main steps here are:

1. **Camera Setup**: Define a camera position, direction, and possibly a look-at vector. For simplicity, maybe the camera is fixed, looking at the origin, and the metaballs move around.

2. **Ray Marching Loop**: For each fragment (pixel), cast a ray. The ray starts at the camera position and direction. Then, step along the ray, checking the SDF at each point. The step size can be based on the distance returned by the SDF. The loop continues until we hit a surface (distance is below a threshold) or we exceed the max steps.

3. **SDF for Metaballs**: Each metaball is a sphere. The SDF for a sphere at position p with radius r is length(p - center) - r. But since the metaballs move, their positions and radii will be uniforms or vary over time.

4. **Combining SDFs with Smooth Minimum**: Use the smin function to blend the SDFs of all metaballs. The smin function allows for smooth transitions between the spheres. The formula for smin is something like -log(exp(-k*a) + exp(-k*b)) / k, where k controls the smoothness.

5. **Shading**: Once a hit is detected, calculate the normal by sampling the SDF in the vicinity (like (sdf(p + epsilon) - sdf(p - epsilon)) for each axis). Then apply some basic lighting, like a directional light, or use color based on the position, time, or other factors. For psychedelic effect, colors should be vibrant and change over time, maybe using HSL with varying hue.

6. **Animation in JavaScript**: Update uniforms each frame, like time, and possibly the positions of the metaballs. Use requestAnimationFrame for the loop. The positions can be animated using sine waves, noise, or other functions to create movement.

Let's outline the steps in code:

In JavaScript:

- Set up the canvas and WebGL context.
- Create a vertex buffer for the quad.
- Compile vertex and fragment shaders.
- Set up uniforms: time, resolution, camera parameters, metaball parameters (positions, radii, colors, etc.).
- Animation loop: update time, update metaball positions, set uniforms, render.

In the fragment shader:

- Define the SDF for a sphere.
- Combine all metaballs' SDFs using smin.
- Ray march loop.
- Calculate color based on hit or miss.

Potential challenges:

- Performance: Ray marching can be computationally heavy, especially with many metaballs. Need to optimize the SDF calculations and possibly reduce the number of steps or use early exits.
- Smooth transitions: The smin function's k parameter affects how smooth the merge is. Finding a good balance.
- Color transitions: To get the psychedelic effect, colors should blend and shift. Using time to modulate hue in the HSL space could work.

Let's start coding.

First, the vertex shader. It's simple:

attribute vec2 position;
varying vec2 vUV;

void main() {
    gl_Position = vec4(position, 0.0, 1.0);
    vUV = position * 0.5 + 0.5; // Convert from [-1,1] to [0,1]
}

Wait, but in WebGL, the vertex position can be from -1 to 1, so the UV can be calculated as (position + 1.0)/2.0.

Then, in the fragment shader:

precision highp float;
uniform float time;
uniform vec2 resolution;

varying vec2 vUV;

// Camera setup
vec3 cameraPosition = vec3(0.0, 0.0, 3.0);
vec3 lookAt = vec3(0.0, 0.0, 0.0);
vec3 cameraDirection = normalize(lookAt - cameraPosition);
vec3 cameraRight = normalize(cross(cameraDirection, vec3(0.0, 1.0, 0.0)));
vec3 cameraUp = cross(cameraDirection, cameraRight);

// Ray direction for current fragment
vec3 getRayDirection(vec2 uv) {
    vec3 rayDir = cameraRight * uv.x + cameraUp * uv.y + cameraDirection;
    return normalize(rayDir);
}

Then, the SDF for a sphere:

float sphereSDF(vec3 p, vec3 center, float radius) {
    return length(p - center) - radius;
}

Now, combining multiple metaballs. Let's say we have a fixed number of metaballs, maybe 5. Their positions can be controlled via uniforms. For simplicity, in the shader, we can have arrays of centers and radii. However, in GLSL, the size of arrays must be known at compile time. So perhaps define a constant number, like 5 metaballs.

But how to pass their positions from JavaScript? Maybe using uniform arrays. For example:

uniform vec3 metaballCenters[5];
uniform float metaballRadii[5];

But in WebGL, the maximum size of uniform arrays can vary, but 5 is manageable.

Alternatively, encode the positions in a texture or use other methods, but for simplicity, let's stick with uniform arrays.

Then, the scene SDF is the smooth min of all individual sphere SDFs.

float sceneSDF(vec3 p) {
    float res = 1000.0; // initial large value
    float k = 2.0; // smoothness factor
    for (int i = 0; i < NUM_METABALLS; i++) {
        float d = sphereSDF(p, metaballCenters[i], metaballRadii[i]);
        res = smin(res, d, k);
    }
    return res;
}

The smin function:

float smin(float a, float b, float k) {
    float h = clamp(0.5 + 0.5*(a-b)/k, 0.0, 1.0);
    return mix(a, b, h) - k*h*(1.0-h);
}

Wait, there are different versions of smin. The polynomial one is often used for performance. The formula I remember is:

float smin(float a, float b, float k) {
    float h = clamp(0.5 + 0.5 * (a - b) / k, 0.0, 1.0);
    return mix(a, b, h) - k * h * (1.0 - h);
}

But some sources use the log-exp version. However, the polynomial version is cheaper computationally.

Once the scene SDF is defined, the ray marching loop:

vec3 raymarch(vec3 origin, vec3 dir) {
    float t = 0.0; // distance along the ray
    for (int i = 0; i < MAX_STEPS; i++) {
        vec3 p = origin + dir * t;
        float d = sceneSDF(p);
        if (d < 0.001) { // hit
            return vec4(p, 1.0); // return position and a flag
        }
        t += d;
        if (t > MAX_DIST) break;
    }
    return vec4(0.0, 0.0, 0.0, 0.0); // miss
}

Wait, but in the loop, we step t by d each time. However, sometimes people use a small minimum step to avoid getting stuck. Also, MAX_STEPS and MAX_DIST are parameters to be defined.

Once the hit is found, we need to calculate the normal. The normal can be approximated by:

vec3 getNormal(vec3 p) {
    float eps = 0.001;
    return normalize(vec3(
        sceneSDF(p + vec3(eps, 0, 0)) - sceneSDF(p - vec3(eps, 0, 0)),
        sceneSDF(p + vec3(0, eps, 0)) - sceneSDF(p - vec3(0, eps, 0)),
        sceneSDF(p + vec3(0, 0, eps)) - sceneSDF(p - vec3(0, 0, eps))
    ));
}

But actually, since sceneSDF returns the distance, the central difference would be (sceneSDF(p + eps) - sceneSDF(p - eps)) / (2*eps), but for the normal, we can just take the gradient.

Alternatively:

vec3 getNormal(vec3 p) {
    vec2 eps = vec2(0.001, 0.0);
    return normalize(vec3(
        sceneSDF(p + eps.xyy) - sceneSDF(p - eps.xyy),
        sceneSDF(p + eps.yxy) - sceneSDF(p - eps.yxy),
        sceneSDF(p + eps.yyx) - sceneSDF(p - eps.yyx)
    ));
}

But perhaps for performance, use a smaller epsilon.

Once the normal is calculated, apply some lighting. For simplicity, maybe use a single light direction and calculate diffuse and ambient lighting.

But for the psychedelic effect, maybe the color is based on the position, time, or other factors. For example, using the normal's components to index into a color palette, or using the distance traveled (t) to modulate color.

Alternatively, use a HSL to RGB conversion where the hue changes with time.

Now, in the fragment shader's main function:

void main() {
    vec2 uv = vUV * 2.0 - 1.0; // convert back to [-1,1] if needed
    vec3 rayDir = getRayDirection(uv);
    vec4 hit = raymarch(cameraPosition, rayDir);
    if (hit.w == 1.0) {
        vec3 p = hit.xyz;
        vec3 normal = getNormal(p);
        // calculate color based on normal, time, etc.
        // example: use normal to create a color
        float h = (normal.x + 1.0) * 0.5; // map from -1 to 1 to 0 to 1
        // but for psychedelic, maybe use time to shift hue
        // or use a function that varies with time
        vec3 color = vec3(h, 0.7, 0.5); // arbitrary base color
        // apply some lighting
        vec3 lightPos = vec3(5.0, 5.0, 5.0);
        vec3 lightDir = normalize(lightPos - p);
        float diff = max(0.0, dot(normal, lightDir));
        color *= diff;
        // add ambient
        color += 0.2;
        // modulate with time for shifting effect
        float timeFactor = sin(time * 0.5);
        color *= 1.0 + 0.5 * timeFactor;
        gl_FragColor = vec4(color, 1.0);
    } else {
        gl_FragColor = vec4(0.0, 0.0, 0.0, 1.0); // background
    }
}

But this is a basic approach. For more psychedelic colors, perhaps use a noise function or a palette that cycles over time.

Now, the JavaScript part. Need to set up the uniforms for metaball positions and radii. Let's say we have 5 metaballs. Their positions can be animated using sine functions with different frequencies and phases.

In JavaScript:

let metaballCount = 5;
let metaballCenters = new Float32Array(3 * metaballCount);
let metaballRadii = new Float32Array(metaballCount);

// Initialize them, maybe randomly or in some pattern

function updateMetaballs(time) {
    for (let i = 0; i < metaballCount; i++) {
        // Example: position in x and z, y fixed
        let angle = time + i;
        let x = Math.sin(angle) * 2.0;
        let z = Math.cos(angle * 0.7) * 2.0;
        metaballCenters[i*3] = x;
        metaballCenters[i*3 + 1] = 0.0; // y position
        metaballCenters[i*3 + 2] = z;
        metaballRadii[i] = 0.8 + 0.2 * Math.sin(time * 0.3 + i);
    }
}

Then, in the animation loop:

function animate(time) {
    time = time / 1000.0; // convert to seconds
    // Update metaball positions
    updateMetaballs(time);
    // Set uniforms
    gl.uniform1f(u_time, time);
    gl.uniform3v(u_metaballCenters[0], ...); // but need to handle array uniforms
    // Wait, how to set uniform arrays?
    // For each metaball, set a uniform for center and radius.

Wait, in WebGL, uniform arrays are handled by specifying the index. For example, if we have a uniform vec3 metaballCenters[5], then in JavaScript, we can set each element with:

for (let i = 0; i < metaballCount; i++) {
    gl.uniform3fv(gl.getUniformLocation(program, `metaballCenters[${i}]`), metaballCenters.slice(i*3, i*3+3));
    gl.uniform1f(gl.getUniformLocation(program, `metaballRadii[${i}]`), metaballRadii[i]);
}

But this can be slow if done every frame. Alternatively, pack all centers into a single uniform array. However, in WebGL 1 (which is common), the support for array uniforms might be limited. Since the user specified WebGL or WebGL2, perhaps using WebGL2.

Alternatively, use a single uniform for all centers and radii. For example, have a uniform vec3 metaballCenters[5], and a uniform float metaballRadii[5]. Then in the shader, loop through them.

But in JavaScript, setting each element of the array can be done by looping through each index.

But for 5 metaballs, it's manageable.

Alternatively, use a single uniform variable that is a flat array. For example, a uniform vec3 metaballCenters[5], which in JavaScript can be set by passing a Float32Array of 15 elements (3 per metaball).

But in WebGL, when you have a uniform array, you can set the entire array at once if the shader expects it. For example:

In the shader:

uniform vec3 metaballCenters[5];
uniform float metaballRadii[5];

In JavaScript:

gl.uniform3fv( [location of metaballCenters], metaballCentersArray );
gl.uniform1fv( [location of metaballRadii], radiiArray );

But how to get the location for the entire array? Because in WebGL, each element of the array is a separate uniform location. So for metaballCenters[0], metaballCenters[1], etc.

This can be tedious. Alternatively, use a different approach, like encoding all positions into a texture, but that's more complex.

Alternatively, since the number is small (5), loop through each index and set them individually.

In code:

const NUM_METABALLS = 5;

// In the shader setup, after creating the program:
const uMetaballCenters = [];
const uMetaballRadii = [];
for (let i = 0; i < NUM_METABALLS; i++) {
    uMetaballCenters.push(gl.getUniformLocation(program, `metaballCenters[${i}]`));
    uMetaballRadii.push(gl.getUniformLocation(program, `metaballRadii[${i}]`));
}

Then, in the animation loop:

for (let i = 0; i < NUM_METABALLS; i++) {
    gl.uniform3fv(uMetaballCenters[i], metaballCenters.slice(i*3, i*3+3));
    gl.uniform1f(uMetaballRadii[i], metaballRadii[i]);
}

But slicing the array each time may not be efficient, but for 5 elements, it's acceptable.

Another approach is to have a single uniform for all centers and radii. For example, a uniform vec3 metaballCenters[5], which in JavaScript can be set by passing a Float32Array of 15 elements (since each vec3 is 3 floats). Similarly for radii.

In the shader:

uniform vec3 metaballCenters[5];
uniform float metaballRadii[5];

In JavaScript:

gl.uniform3fv(gl.getUniformLocation(program, "metaballCenters"), metaballCentersArray);
gl.uniform1fv(gl.getUniformLocation(program, "metaballRadii"), radiiArray);

But in WebGL, when you have a uniform array, the location is for the entire array. However, the way to set them depends on the GL context. For example, in WebGL 1, you can't set the entire array at once, but in WebGL2 you can. So perhaps better to loop through each element.

Alternatively, use a single uniform for all centers and radii. But for simplicity, let's proceed with looping.

Now, the animation loop in JavaScript:

let lastTime = 0;

function animate(timestamp) {
    requestAnimationFrame(animate);
    const deltaTime = timestamp - lastTime;
    lastTime = timestamp;

    const time = timestamp / 1000.0;

    // Update metaball positions and radii based on time
    updateMetaballs(time);

    // Set uniforms
    gl.uniform1f(u_time, time);
    // Update metaball uniforms
    for (let i = 0; i < NUM_METABALLS; i++) {
        gl.uniform3fv(uMetaballCenters[i], metaballCenters.slice(i*3, i*3+3));
        gl.uniform1f(uMetaballRadii[i], metaballRadii[i]);
    }

    // Clear the canvas
    gl.clear(gl.COLOR_BUFFER_BIT);

    // Draw the quad
    gl.drawArrays(gl.TRIANGLES, 0, 4); // assuming 4 vertices for two triangles

    // Or, if using a vertex buffer with two triangles (6 vertices)
}

Wait, the vertex buffer setup: need to create a buffer with the quad's vertices. For example, two triangles covering the entire screen.

The vertices can be:

const vertices = new Float32Array([
    -1, -1, 0.0,
     1, -1, 0.0,
    -1,  1, 0.0,

     1, -1, 0.0,
     1,  1, 0.0,
    -1,  1, 0.0
]);

Then, create a vertex buffer, bind it, and set the attribute pointer.

In JavaScript:

const vertexBuffer = gl.createBuffer();
gl.bindBuffer(gl.ARRAY_BUFFER, vertexBuffer);
gl.bufferData(gl.ARRAY_BUFFER, vertices, gl.STATIC_DRAW);

const vertexPosition = gl.getAttribLocation(program, 'position');
gl.enableVertexAttribArray(vertexPosition);
gl.vertexAttribPointer(vertexPosition, 3, gl.FLOAT, false, 0, 0);

Now, putting all together.

Potential issues:

- The camera setup: The initial camera direction and lookAt may need adjustment. For example, the camera is at (0,0,3), looking at (0,0,0). The ray direction calculation uses the UV coordinates to create a view frustum.

But in the getRayDirection function, the UV is from the vertex shader's vUV, which is in [0,1] (since in the vertex shader, vUV = (position + 1.0)/2.0). Wait, original position is from -1 to 1, so adding 1 gives 0 to 2, divided by 2 gives 0 to 1. So in the fragment shader, vUV is in [0,1]. Then, to convert to [-1,1], we do (vUV * 2.0 - 1.0). So in the getRayDirection function, uv.x and uv.y are in [-1,1], which can be used to create the ray direction.

But the camera setup may need to be adjusted for proper perspective.

Another thing: the ray marching loop. The step size is based on the distance returned by the SDF. However, sometimes it's better to use a small minimum step to avoid getting stuck, especially when the distance is very small.

In the raymarch function:

float t = 0.0;
for (int i = 0; i < MAX_STEPS; i++) {
    vec3 p = origin + dir * t;
    float d = sceneSDF(p);
    if (d < 0.001) {
        // hit
        return vec4(p, 1.0);
    }
    t += d;
    if (t > MAX_DIST) break;
}

But sometimes, when the distance is very small, adding it could overshoot. So some implementations use a small minimum step, like t += max(d, 0.01).

Now, the SDF combination. For each metaball, compute the sphere SDF and apply smin.

But in the sceneSDF function, need to loop through all metaballs and apply smin.

Now, the smooth min function. Let's implement the polynomial version.

float smin(float a, float b, float k) {
    float h = clamp(0.5 + 0.5*(a - b)/k, 0.0, 1.0);
    return mix(a, b, h) - k * h * (1.0 - h);
}

But in the loop, for each metaball, we compare the current res with the new sphere's SDF.

In the sceneSDF:

float sceneSDF(vec3 p) {
    float res = 1000.0; // initial large value
    float k = 2.0; // smoothness factor
    for (int i = 0; i < NUM_METABALLS; i++) {
        float d = sphereSDF(p, metaballCenters[i], metaballRadii[i]);
        res = smin(res, d, k);
    }
    return res;
}

But in GLSL, loops with dynamic indices can be tricky. However, since NUM_METABALLS is a constant (like 5), it's okay.

Now, the color calculation. For psychedelic effect, perhaps use a color based on the normal and time. For example, using the normal's components to generate a color, and modulating with time.

Alternatively, use a function that maps the hit point's position or normal to a color palette that shifts over time.

Another idea: use a hash function or noise in the shader to generate color variations. But for simplicity, let's start with a basic approach.

For example:

vec3 getColor(vec3 normal, float time) {
    // Use normal to create a base color
    float h = (normal.x + 1.0) * 0.5; // map from -1 to 1 to 0 to 1
    // Use time to shift hue
    h += sin(time) * 0.1;
    h = fract(h); // wrap around
    // Convert HSL to RGB
    float s = 0.8;
    float l = 0.5;
    return hslToRgb(h, s, l);
}

But need a hslToRgb function. Alternatively, use a palette based on the normal's components.

Alternatively, use a simple sine wave modulation:

vec3 color = vec3(
    sin(time + normal.x * 5.0),
    sin(time + normal.y * 5.0),
    sin(time + normal.z * 5.0)
) * 0.5 + 0.5;

But this could create a trippy effect.

Another approach is to use the distance traveled (t) to modulate color.

But perhaps the simplest is to use the normal's components to create a color, and then modulate with time.

Now, putting all together.

Potential performance optimizations:

- Limit the number of steps in ray marching. Maybe 100 steps.
- Use a smaller step when close to the surface.
- Optimize the SDF calculations by using local variables and minimizing computations.

Now, testing. But since I can't test here, need to make sure the code is correct.

Another thing: the camera's position and direction. Maybe the initial setup has the camera looking at the origin, but the metaballs are moving around, so they should come into view.

Now, the JavaScript code for metaball movement. For example, each metaball's position can be animated with sine waves with different frequencies and phases.

In the updateMetaballs function:

function updateMetaballs(time) {
    for (let i = 0; i < NUM_METABALLS; i++) {
        // Example: x and z positions oscillate
        let angle = time * 0.5 + i;
        let x = Math.sin(angle) * 1.5;
        let z = Math.cos(angle * 0.7 + i) * 1.5;
        metaballCenters[i*3] = x;
        metaballCenters[i*3 + 1] = 0.0; // y position
        metaballCenters[i*3 + 2] = z;
        // Radii can also change
        metaballRadii[i] = 0.8 + 0.2 * Math.sin(time * 0.3 + i);
    }
}

This should create moving and breathing metaballs.

Now, the vertex shader code:

attribute vec2 position;
varying vec2 vUV;

void main() {
    gl_Position = vec4(position, 0.0, 1.0);
    vUV = (position + 1.0) * 0.5; // from [-1,1] to [0,1]
}

But the position attribute is a vec2, but in the vertex data, we have x, y, z (but z is 0.0). Wait, the vertices are defined as 3D points, but in the vertex shader, the attribute is a vec2. That's a problem. Because the vertices have x, y, z (with z=0), but the attribute is declared as vec2, which will read only x and y, leaving z as 0. But in the vertex shader, the position is passed as vec4(position, 0.0, 1.0), which is correct.

Wait, the vertex data has three components, but the attribute is declared as vec2. That will cause an error. Because the vertex attribute is set up with size=3, but the shader expects size=2. So that's a mistake.

Ah, right! The vertex data has 3 components (x, y, z), but the vertex shader's 'position' attribute is a vec2. So that's incorrect. Need to fix that.

The vertices are:

const vertices = new Float32Array([
    -1, -1, 0.0,
     1, -1, 0.0,
    -1,  1, 0.0,

     1, -1, 0.0,
     1,  1, 0.0,
    -1,  1, 0.0
]);

Each vertex has x, y, z. So the 'position' attribute should be a vec3. But in the vertex shader, since z is always 0, we can ignore it. But the code must read it correctly.

So in the vertex shader:

attribute vec3 position;
varying vec2 vUV;

void main() {
    gl_Position = vec4(position, 1.0);
    vUV = (position.xy + 1.0) * 0.5; // since position.x and y are from -1 to 1
}

Then, in JavaScript, when setting up the attribute:

const vertexPosition = gl.getAttribLocation(program, 'position');
gl.enableVertexAttribArray(vertexPosition);
gl.vertexAttribPointer(vertexPosition, 3, gl.FLOAT, false, 0, 0);

This way, each vertex is read as a vec3, and the z component is ignored in the vUV calculation.

That's better.

Now, the fragment shader code.

Putting all the shader code together:

Fragment shader:

precision highp float;

uniform float time;
uniform vec2 resolution;

varying vec2 vUV;

#define NUM_METABALLS 5
#define MAX_STEPS 100
#define MAX_DIST 10.0
#define SURFACE_DIST 0.001

uniform vec3 metaballCenters[NUM_METABALLS];
uniform float metaballRadii[NUM_METABALLS];

float smin(float a, float b, float k) {
    float h = clamp(0.5 + 0.5*(a - b)/k, 0.0, 1.0);
    return mix(a, b, h) - k * h * (1.0 - h);
}

float sphereSDF(vec3 p, vec3 center, float radius) {
    return length(p - center) - radius;
}

float sceneSDF(vec3 p) {
    float res = 1000.0;
    float k = 2.0;
    for (int i = 0; i < NUM_METABALLS; i++) {
        float d = sphereSDF(p, metaballCenters[i], metaballRadii[i]);
        res = smin(res, d, k);
    }
    return res;
}

vec3 getNormal(vec3 p) {
    vec2 eps = vec2(0.001, 0.0);
    return normalize(vec3(
        sceneSDF(p + eps.xyy) - sceneSDF(p - eps.xyy),
        sceneSDF(p + eps.yxy) - sceneSDF(p - eps.yxy),
        sceneSDF(p + eps.yyx) - sceneSDF(p - eps.yyx)
    ));
}

vec4 raymarch(vec3 origin, vec3 dir) {
    float t = 0.0;
    for (int i = 0; i < MAX_STEPS; i++) {
        vec3 p = origin + dir * t;
        float d = sceneSDF(p);
        if (d < SURFACE_DIST) {
            return vec4(p, 1.0);
        }
        t += d;
        if (t > MAX_DIST) break;
    }
    return vec4(0.0, 0.0, 0.0, 0.0);
}

vec3 hslToRgb(float h, float s, float l) {
    vec4 k = vec4(1.0 < 0.5, 1.0, 1.0, 0.6);
    vec3 p = mix(k.xzz, k.zxx, h);
    vec3 d = p - l;
    return mix(l, 1.0, s) * (abs(d) < 1.0 ? 6.0 - 2.0 * abs(d) : 2.0);
}

void main() {
    vec2 uv = vUV;
    vec3 cameraPos = vec3(0.0, 0.0, 3.0);
    vec3 rayDir = normalize(vec3(uv * 2.0 - 1.0, -1.0)); // Adjust for perspective

    vec4 hit = raymarch(cameraPos, rayDir);
    vec3 color = vec3(0.0);
    if (hit.w > 0.0) {
        vec3 p = hit.xyz;
        vec3 normal = getNormal(p);
        // Use normal and time to generate color
        float h = (normal.x + 1.0) * 0.5;
        h += sin(time) * 0.1;
        h = fract(h);
        float s = 0.8;
        float l = 0.5;
        color = hslToRgb(h, s, l);
    } else {
        // Background color
        color = vec3(0.0);
    }

    gl_FragColor = vec4(color, 1.0);
}

Wait, the rayDir calculation. In the original code, the camera is at (0,0,3), looking towards (0,0,0). The ray direction should be calculated based on the view frustum.

In the main function:

vec3 rayDir = normalize(vec3(uv * 2.0 - 1.0, -1.0));

But this creates a ray that goes from the camera (at z=3) towards the negative z direction. However, the camera's position is at (0,0,3), and the ray direction is (uv.x, uv.y, -1), which is towards the origin.

But to create a perspective projection, the ray direction should be calculated based on the camera's position and the view matrix. However, for simplicity, this approach can work.

Another way: the camera is at (0,0,3), looking at (0,0,0), with up vector (0,1,0). The view frustum can be represented by rays from the camera through each pixel.

The direction can be calculated as:

vec3 rayDir = normalize(vec3(uv, -1.0));

But uv is in [-1,1], so this creates a frustum that covers the entire scene.

Alternatively, use a perspective matrix, but that's more complex.

Now, the hslToRgb function. The code above may have errors. A correct implementation:

vec3 hslToRgb(float h, float s, float l) {
    vec3 rgb = clamp(3.0 * vec3(h, h, h) - vec3(1.0, 2.0, 0.0), 0.0, 1.0);
    rgb = mix(vec3(l), clamp(3.0 * rgb - 2.0 * rgb * rgb, 0.0, 1.0), s);
    return rgb;
}

But I'm not sure. Alternatively, use a simpler approach for color.

Alternatively, use the normal's components directly:

color = normal * 0.5 + 0.5;

Then modulate with time:

color += sin(time + normal.x * 10.0) * 0.1;

But this can create a dynamic effect.

Putting all together, the final code should be:

HTML:

<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Metaballs</title>
    <style>
        body { margin: 0; overflow: hidden; }
        canvas { display: block; }
    </style>
</head>
<body>
    <canvas id="canvas"></canvas>
    <script src="script.js"></script>
</body>
</html>

JavaScript (script.js):

const NUM_METABALLS = 5;

const vs = `
attribute vec3 position;
varying vec2 vUV;

void main() {
    gl_Position = vec4(position, 1.0);
    vUV = (position.xy + 1.0) * 0.5;
}
`;

const fs = `
precision highp float;

uniform float time;
uniform vec2 resolution;

varying vec2 vUV;

#define NUM_METABALLS ${NUM_METABALLS}
#define MAX_STEPS 100
#define MAX_DIST 10.0
#define SURFACE_DIST 0.001

uniform vec3 metaballCenters[NUM_METABALLS];
uniform float metaballRadii[NUM_METABALLS];

float smin(float a, float b, float k) {
    float h = clamp(0.5 + 0.5*(a - b)/k, 0.0, 1.0);
    return mix(a, b, h) - k * h * (1.0 - h);
}

float sphereSDF(vec3 p, vec3 center, float radius) {
    return length(p - center) - radius;
}

float sceneSDF(vec3 p) {
    float res = 1000.0;
    float k = 2.0;
    for (int i = 0; i < NUM_METABALLS; i++) {
        float d = sphereSDF(p, metaballCenters[i], metaballRadii[i]);
        res = smin(res, d, k);
    }
    return res;
}

vec3 getNormal(vec3 p) {
    vec2 eps = vec2(0.001, 0.0);
    return normalize(vec3(
        sceneSDF(p + eps.xyy) - sceneSDF(p - eps.xyy),
        sceneSDF(p + eps.yxy) - sceneSDF(p - eps.yxy),
        sceneSDF(p + eps.yyx) - sceneSDF(p - eps.yyx)
    ));
}

vec4 raymarch(vec3 origin, vec3 dir) {
    float t = 0.0;
    for (int i = 0; i < MAX_STEPS; i++) {
        vec3 p = origin + dir * t;
        float d = sceneSDF(p);
        if (d < SURFACE_DIST) {
            return vec4(p, 1.0);
        }
        t += d;
        if (t > MAX_DIST) break;
    }
    return vec4(0.0, 0.0, 0.0, 0.0);
}

void main() {
    vec2 uv = vUV;
    vec3 cameraPos = vec3(0.0, 0.0, 3.0);
    vec3 rayDir = normalize(vec3(uv * 2.0 - 1.0, -1.0));

    vec4 hit = raymarch(cameraPos, rayDir);
    vec3 color = vec3(0.0);
    if (hit.w > 0.0) {
        vec3 p = hit.xyz;
        vec3 normal = getNormal(p);
        // Use normal to generate color
        color = normal * 0.5 + 0.5;
        // Modulate with time for psychedelic effect
        color += sin(time + normal.x * 10.0) * 0.1;
        color += sin(time + normal.y * 10.0) * 0.1;
        color += sin(time + normal.z * 10.0) * 0.1;
        color = clamp(color, 0.0, 1.0);
    }

    gl_FragColor = vec4(color, 1.0);
}
`;

let canvas, gl, program, uMetaballCenters, uMetaballRadii, uTime;

function init() {
    canvas = document.getElementById('canvas');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    gl = canvas.getContext('webgl2');
    if (!gl) {
        alert('WebGL 2 not supported');
        return;
    }

    // Compile shaders
    const vertexShader = gl.createShader(gl.VERTEX_SHADER);
    gl.shaderSource(vertexShader, vs);
    gl.compileShader(vertexShader);
    if (!gl.getShaderParameter(vertexShader, gl.COMPILE_STATUS)) {
        console.log('Vertex shader compile error:', gl.getShaderInfoLog(vertexShader));
    }

    const fragmentShader = gl.createShader(gl.FRAGMENT_SHADER);
    gl.shaderSource(fragmentShader, fs);
    gl.compileShader(fragmentShader);
    if (!gl.getShaderParameter(fragmentShader, gl.COMPILE_STATUS)) {
        console.log('Fragment shader compile error:', gl.getShaderInfoLog(fragmentShader));
    }

    program = gl.createProgram();
    gl.attachShader(program, vertexShader);
    gl.attachShader(program, fragmentShader);
    gl.linkProgram(program);
    if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
        console.log('Program link error:', gl.getProgramInfoLog(program));
    }

    // Get uniform locations
    uTime = gl.getUniformLocation(program, 'time');
    uMetaballCenters = [];
    uMetaballRadii = [];
    for (let i = 0; i < NUM_METABALLS; i++) {
        uMetaballCenters.push(gl.getUniformLocation(program, `metaballCenters[${i}]`));
        uMetaballRadii.push(gl.getUniformLocation(program, `metaballRadii[${i}]`));
    }

    // Create vertex buffer
    const vertices = new Float32Array([
        -1, -1, 0.0,
         1, -1, 0.0,
        -1,  1, 0.0,

         1, -1, 0.0,
         1,  1, 0.0,
        -1,  1, 0.0
    ]);

    const vertexBuffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, vertexBuffer);
    gl.bufferData(gl.ARRAY_BUFFER, vertices, gl.STATIC_DRAW);

    const vertexPosition = gl.getAttribLocation(program, 'position');
    gl.enableVertexAttribArray(vertexPosition);
    gl.vertexAttribPointer(vertexPosition, 3, gl.FLOAT, false, 0, 0);

    // Initialize metaball data
    const metaballCenters = new Float32Array(NUM_METABALLS * 3);
    const metaballRadii = new Float32Array(NUM_METABALLS);

    function updateMetaballs(time) {
        for (let i = 0; i < NUM_METABALLS; i++) {
            let angle = time * 0.5 + i;
            let x = Math.sin(angle) * 1.5;
            let z = Math.cos(angle * 0.7 + i) * 1.5;
            metaballCenters[i*3] = x;
            metaballCenters[i*3 + 1] = 0.0;
            metaballCenters[i*3 + 2] = z;
            metaballRadii[i] = 0.8 + 0.2 * Math.sin(time * 0.3 + i);
        }
    }

    // Animation loop
    let lastTime = 0;
    function animate(timestamp) {
        requestAnimationFrame(animate);
        const time = timestamp / 1000.0;

        // Update metaballs
        updateMetaballs(time);

        // Set uniforms
        gl.uniform1f(uTime, time);
        for (let i = 0; i < NUM_METABALLS; i++) {
            gl.uniform3fv(uMetaballCenters[i], [metaballCenters[i*3], metaballCenters[i*3+1], metaballCenters[i*3+2]]);
            gl.uniform1f(uMetaballRadii[i], metaballRadii[i]);
        }

        // Clear
        gl.clearColor(0.0, 0.0, 0.0, 1.0);
        gl.clear(gl.COLOR_BUFFER_BIT);

        // Draw
        gl.useProgram(program);
        gl.drawArrays(gl.TRIANGLES, 0, 6); // 6 vertices for two triangles
    }

    animate();
}

window.onload = init;

This should work. However, there might be issues with the ray direction calculation, leading to metaballs not being visible. For example, if the camera is at (0,0,3) and the metaballs are centered around (0,0,0), but the ray direction is towards negative z, then the metaballs should be visible.

Another thing: the initial camera position and ray direction. The rayDir is calculated as normalize(vec3(uv * 2.0 - 1.0, -1.0)). This means that for a pixel in the center (uv = (0.5, 0.5)), the ray direction is (0,0,-1), which is straight down the z-axis, towards the origin. The camera is at (0,0,3), so the ray starts at (0,0,3) and goes towards (0,0,0), which is correct.

The metaballs are moving around (0,0,0), so they should be visible.

Potential issues:

- The metaballs are too small or not moving into the view.
- The SDF calculation has errors.
- The ray marching parameters are not set correctly.

But given the complexity, this should be a good starting point.

Finally, the answer should provide the complete code as described.
</think>
Here's a complete implementation of a psychedelic metaball animation using WebGL and ray marching:

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Psychedelic Metaballs</title>
    <style>
        body { margin: 0; overflow: hidden; }
        canvas { display: block; }
    </style>
</head>
<body>
    <canvas id="canvas"></canvas>
    <script>
        // WebGL 2 context setup
        const canvas = document.getElementById('canvas');
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        const gl = canvas.getContext('webgl2');
        if (!gl) {
            alert('WebGL 2 not supported');
        }

        // Shader sources
        const vs = `
            attribute vec3 position;
            varying vec2 vUV;
            
            void main() {
                gl_Position = vec4(position, 1.0);
                vUV = (position.xy + 1.0) * 0.5;
            }
        `;

        const fs = `
            precision highp float;
            
            uniform float time;
            uniform vec2 resolution;
            
            varying vec2 vUV;
            
            #define NUM_METABALLS 5
            #define MAX_STEPS 100
            #define MAX_DIST 10.0
            #define SURFACE_DIST 0.001
            
            uniform vec3 metaballCenters[NUM_METABALLS];
            uniform float metaballRadii[NUM_METABALLS];
            
            float smin(float a, float b, float k) {
                float h = clamp(0.5 + 0.5*(a - b)/k, 0.0, 1.0);
                return mix(a, b, h) - k * h * (1.0 - h);
            }
            
            float sphereSDF(vec3 p, vec3 center, float radius) {
                return length(p - center) - radius;
            }
            
            float sceneSDF(vec3 p) {
                float res = 1000.0;
                float k = 2.0;
                for (int i = 0; i < NUM_METABALLS; i++) {
                    float d = sphereSDF(p, metaballCenters[i], metaballRadii[i]);
                    res = smin(res, d, k);
                }
                return res;
            }
            
            vec3 getNormal(vec3 p) {
                vec2 eps = vec2(0.001, 0.0);
                return normalize(vec3(
                    sceneSDF(p + eps.xyy) - sceneSDF(p - eps.xyy),
                    sceneSDF(p + eps.yxy) - sceneSDF(p - eps.yxy),
                    sceneSDF(p + eps.yyx) - sceneSDF(p - eps.yyx)
                ));
            }
            
            vec4 raymarch(vec3 origin, vec3 dir) {
                float t = 0.0;
                for (int i = 0; i < MAX_STEPS; i++) {
                    vec3 p = origin + dir * t;
                    float d = sceneSDF(p);
                    if (d < SURFACE_DIST) {
                        return vec4(p, 1.0);
                    }
                    t += d;
                    if (t > MAX_DIST) break;
                }
                return vec4(0.0, 0.0, 0.0, 0.0);
            }
            
            void main() {
                vec2 uv = vUV;
                vec3 cameraPos = vec3(0.0, 0.0, 3.0);
                vec3 rayDir = normalize(vec3(uv * 2.0 - 1.0, -1.0));
                
                vec4 hit = raymarch(cameraPos, rayDir);
                vec3 color = vec3(0.0);
                if (hit.w > 0.0) {
                    vec3 p = hit.xyz;
                    vec3 normal = getNormal(p);
                    color = normal * 0.5 + 0.5;
                    
                    // Psychedelic color modulation
                    color += sin(time + normal.x * 10.0) * 0.1;
                    color += sin(time + normal.y * 10.0) * 0.1;
                    color += sin(time + normal.z * 10.0) * 0.1;
                    color = clamp(color, 0.0, 1.0);
                }
                
                gl_FragColor = vec4(color, 1.0);
            }
        `;

        // Compile shaders and create program
        function compileShader(type, source) {
            const shader = gl.createShader(type);
            gl.shaderSource(shader, source);
            gl.compileShader(shader);
            if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
                console.error('Shader compile error:', gl.getShaderInfoLog(shader));
            }
            return shader;
        }

        const vertexShader = compileShader(gl.VERTEX_SHADER, vs);
        const fragmentShader = compileShader(gl.FRAGMENT_SHADER, fs);
        
        const program = gl.createProgram();
        gl.attachShader(program, vertexShader);
        gl.attachShader(program, fragmentShader);
        gl.linkProgram(program);
        if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
            console.error('Program link error:', gl.getProgramInfoLog(program));
        }

        // Vertex buffer setup
        const vertices = new Float32Array([
            -1, -1, 0.0,
             1, -1, 0.0,
            -1,  1, 0.0,
             1, -1, 0.0,
             1,  1, 0.0,
            -1,  1, 0.0
        ]);

        const vertexBuffer = gl.createBuffer();
        gl.bindBuffer(gl.ARRAY_BUFFER, vertexBuffer);
        gl.bufferData(gl.ARRAY_BUFFER, vertices, gl.STATIC_DRAW);

        const vertexPosition = gl.getAttribLocation(program, 'position');
        gl.enableVertexAttribArray(vertexPosition);
        gl.vertexAttribPointer(vertexPosition, 3, gl.FLOAT, false, 0, 0);

        // Uniform locations
        const uTime = gl.getUniformLocation(program, 'time');
        const uMetaballCenters = [];
        const uMetaballRadii = [];
        for (let i = 0; i < 5; i++) {
            uMetaballCenters.push(gl.getUniformLocation(program, `metaballCenters[${i}]`));
            uMetaballRadii.push(gl.getUniformLocation(program, `metaballRadii[${i}]`));
        }

        // Metaball data
        const metaballCenters = new Float32Array(15);
        const metaballRadii = new Float32Array(5);

        // Animation loop
        let lastTime = 0;
        function animate(timestamp) {
            requestAnimationFrame(animate);
            const time = timestamp / 1000.0;

            // Update metaballs
            for (let i = 0; i < 5; i++) {
                const angle = time * 0.5 + i;
                metaballCenters[i*3] = Math.sin(angle) * 1.5;
                metaballCenters[i*3+1] = 0.0;
                metaballCenters[i*3+2] = Math.cos(angle * 0.7 + i) * 1.5;
                metaballRadii[i] = 0.8 + 0.2 * Math.sin(time * 0.3 + i);
            }

            // Set uniforms
            gl.uniform1f(uTime, time);
            for (let i = 0; i < 5; i++) {
                gl.uniform3fv(uMetaballCenters[i], metaballCenters.subarray(i*3, i*3+3));
                gl.uniform1f(uMetaballRadii[i], metaballRadii[i]);
            }

            // Clear
            gl.clearColor(0.0, 0.0, 0.0, 1.0);
            gl.clear(gl.COLOR_BUFFER_BIT);

            // Draw
            gl.useProgram(program);
            gl.drawArrays(gl.TRIANGLES, 0, 6);
        }

        animate();
    </script>
</body>
</html>
```

### How it Works:
1. **Shader Setup**: The vertex shader handles basic vertex positioning, while the fragment shader implements ray marching through a scene defined by metaballs.
2. **Metaball Animation**: The JavaScript code updates the positions and radii of five metaballs in a circular pattern using sine and cosine functions.
3. **Psychedelic Effects**: The fragment shader modulates the surface colors using sine functions based on normal vectors and time, creating dynamic, trippy patterns.
4. **Ray Marching**: The scene is rendered using ray marching, which allows for complex, organic shapes and smooth surfaces without needing traditional 3D models.

This implementation creates a mesmerizing, ever-changing psychedelic animation that showcases the power of real-time ray marching and WebGL.

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: Nemotron-Super-49B-v1_5-IQ4_XS.gguf -->
<!-- Prompt: lightshow.md -->
<!-- Generation Time: 520.41s -->
<!-- Fallback Used: False -->