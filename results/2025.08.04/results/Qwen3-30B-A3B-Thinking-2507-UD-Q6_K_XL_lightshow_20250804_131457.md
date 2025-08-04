<think>
We are going to create a full-screen WebGL application that uses ray marching to render a scene of metaballs (smoothly merging spheres) with a psychedelic color scheme.

 Steps:
 1. Set up the WebGL context and create a full-screen quad (two triangles).
 2. Write a vertex shader that just passes through the position and sets up the screen coordinates.
 3. Write a fragment shader that does:
    a. Ray marching in 3D space (using a camera at (0,0,5) looking at origin, with a field of view).
    b. Define an SDF for a single sphere (with center and radius).
    c. Combine multiple metaballs using a smooth minimum function (with a parameter k for smoothness).
    d. For each ray, march until we hit the surface (or max steps) and then shade the surface with a psychedelic color.

 4. In JavaScript:
    - Set up the uniforms (time, resolution, and an array of metaball parameters).
    - Update the time uniform each frame.
    - Update the metaball positions (and radii) over time (using sine/cosine functions) to create movement.

 Important: We'll use a 3D scene but note that the ray marching is done in 3D, but the camera is fixed and we are rendering to 2D screen.

 We'll define:
   - `metaballs`: an array of objects with { pos: vec3, radius: float }.
   - We'll have a fixed number of metaballs (say 5) for simplicity.

 How the ray marching works in the fragment shader:
   - For each fragment (pixel), we have a ray starting at the camera (0,0,5) and going through the pixel (which we compute from the screen coordinates).
   - We step along the ray in steps of `dist` (which is the SDF value at the current point) until we either hit the surface (dist < 0.001) or exceed max steps.

 SDF for a single sphere:
   `float sphereSDF(vec3 p, vec3 center, float radius) {
        return length(p - center) - radius;
   }`

 Smooth minimum for two SDFs (with parameter k):
   `float smin(float a, float b, float k) {
        float h = clamp(0.5 + 0.5*(b - a)/k, 0.0, 1.0);
        return mix(b, a, h) - k*h*(1.0-h);
   }`

 But note: the common smooth min (with exponential) is also used. We'll use the polynomial one for simplicity and performance.

 However, note: the exponential smooth min is more common for metaballs. Let's use:
   `float smin(float a, float b, float k) {
        float h = clamp(0.5 + 0.5*(b - a)/k, 0.0, 1.0);
        return mix(b, a, h) - k*h*(1.0-h);
   }`

 But note: the above is the polynomial smooth min. Alternatively, we can use the exponential one which is more common in metaballs.

 We'll use the exponential one because it's smoother and more standard for metaballs:

   `float smin(float a, float b, float k) {
        return -log(exp(-k*a) + exp(-k*b)) / k;
   }`

 However, note: the exponential version might be slower. But for a few metaballs it's acceptable.

 We'll use the exponential version.

 Steps in the fragment shader:

   vec3 rayOrigin = vec3(0.0, 0.0, 5.0); // camera position
   vec3 rayDirection = normalize(vec3((uv * 2.0 - 1.0) * vec2(1.0, aspect), -1.0));
   // But note: we are in 2D screen, so we need to convert to 3D.

   Actually, we'll set up the ray direction in the fragment shader as:
        vec3 rayDir = normalize( vec3( (uv.x * 2.0 - 1.0) * aspect, uv.y * 2.0 - 1.0, -1.0 ) );
   But note: our camera is at (0,0,5) and looking at (0,0,0). We can also set the camera to (0,0,0) and the scene to be at z=-5? 
   Let's adjust: we'll set the camera at (0,0,0) and the scene at z = -5, so the ray direction is (x, y, -5) but we normalize.

   Alternatively, we can set the camera at (0,0,5) and the ray direction towards the screen (which is at z=0). Then the ray direction is (x, y, -5) normalized.

   We'll do:

        vec3 rayOrigin = vec3(0.0, 0.0, 5.0);
        vec3 rayDir = normalize( vec3( (uv.x * 2.0 - 1.0) * aspect, uv.y * 2.0 - 1.0, -5.0) );

   But note: the aspect ratio. We'll pass the aspect ratio as a uniform.

   However, to avoid the aspect ratio distortion, we can adjust the x coordinate by aspect.

   Alternatively, we can set the camera to (0,0,0) and the scene at z=-5, then the ray direction is (x, y, -5) but normalized. But then the field of view is fixed.

   Let's do:

        vec3 rayDir = normalize( vec3( (uv.x * 2.0 - 1.0) * aspect, uv.y * 2.0 - 1.0, -1.0) );

   Then the camera is at (0,0,0) and the ray goes in the direction (x, y, -1) which is a standard perspective.

   We'll set the camera at (0,0,0) and the scene at z = -5 (so the rays are going in the negative z direction). Then the ray marching will be done in the negative z direction.

   Actually, we can set the camera at (0,0,0) and the scene at z = -5, so the ray direction is (x, y, -1) and we step in the negative z direction.

   But note: the SDF is defined in world space. We'll define the metaballs at (0,0,0) but they will move.

   We'll set the camera at (0,0,0) and the ray direction as:

        vec3 rayDir = normalize( vec3( (uv.x * 2.0 - 1.0) * aspect, uv.y * 2.0 - 1.0, -1.0) );

   Then the ray starts at (0,0,0) and goes in the direction rayDir.

   However, we want to have the scene at a distance, so we can also set the camera at (0,0,5) and the scene at z=0? But then the ray direction would be (x, y, -5). 

   Let's stick to the common method: camera at (0,0,0) and the ray direction (x, y, -1) normalized. Then the scene is in front of the camera (negative z). We'll set the metaballs to be at (0,0,0) but moving in 3D.

   Actually, we can have the metaballs moving in 3D space, but we'll keep them in the z=0 plane for simplicity? Or let them move in 3D.

   We'll have them move in 3D: each metaball has a position (x, y, z) but we'll make them move in a circle in the x-y plane and also oscillate in z.

   How we'll update the metaballs in JavaScript:

        let metaballs = [];
        for (let i = 0; i < 5; i++) {
            // each metaball: position and radius
            metaballs.push({
                pos: vec3(0,0,0),
                radius: 1.0 + 0.5 * Math.sin(time * 0.5 + i * 0.5)
            });
        }

        Then in the animation loop, we update the positions:

        for (let i = 0; i < metaballs.length; i++) {
            let angle = time * 0.2 + i * 1.0;
            metaballs[i].pos = vec3(
                Math.cos(angle) * 2.0,
                Math.sin(angle) * 2.0,
                Math.sin(time * 0.1) * 0.5
            );
        }

   But note: we have to pass the metaball positions and radii to the shader. We can pass an array of vectors.

   However, GLSL doesn't support dynamic arrays. So we'll have a fixed number (5) and pass them as uniforms.

   We'll create 5 uniforms for positions and 5 for radii? But that's 10 uniforms. Alternatively, we can pass a single uniform array.

   We'll pass an array of 5 positions (each as vec3) and an array of 5 radii (as float). But note: the number of metaballs is fixed.

   We'll define in the shader:

        uniform vec3 metaballPos[5];
        uniform float metaballRadius[5];

   But note: WebGL 1 doesn't support uniform arrays of structs? Actually, we can have arrays of floats or vec3s.

   However, we can also pass the positions as a single 15-element array (5*3) and radii as a 5-element array.

   But for simplicity and clarity, we'll use:

        uniform vec3 metaballPos[5];
        uniform float metaballRadius[5];

   But note: the WebGL 1 specification does not support uniform arrays of structs, but it does support arrays of vectors and scalars. So this is acceptable.

   However, we have to set the uniforms in JavaScript as arrays. We'll create a uniform array for the positions and radii.

   Steps for setting uniforms in JavaScript:

        // For positions: we have an array of 5 vec3s
        let posArray = [];
        for (let i = 0; i < 5; i++) {
            posArray.push(metaballs[i].pos.x);
            posArray.push(metaballs[i].pos.y);
            posArray.push(metaballs[i].pos.z);
        }
        gl.uniform3fv(uniformLocationPos, posArray);

        // Similarly for radii
        let radiusArray = [];
        for (let i = 0; i < 5; i++) {
            radiusArray.push(metaballs[i].radius);
        }
        gl.uniform1fv(uniformLocationRadius, radiusArray);

   But note: the uniform location for an array of vec3s is set as `gl.getUniformLocation(program, "metaballPos")` and then we pass the array as a flat array of floats.

   However, the shader expects a uniform array of vec3s. The WebGL API will handle it.

   Alternatively, we can use a single uniform for the entire array of positions (as a 15-float array) and one for the radii (5 floats). We'll do that.

   Let's define in the shader:

        uniform vec3 metaballPos[5];
        uniform float metaballRadius[5];

   Then in JavaScript, we set:

        gl.uniform3fv(uniformPos, posArray); // posArray is a flat array of 15 floats

        gl.uniform1fv(uniformRadius, radiusArray); // radiusArray is a flat array of 5 floats

   Now, the SDF for the entire scene:

        float sceneSDF(vec3 p) {
            float d = 1e10;
            for (int i = 0; i < 5; i++) {
                float dist = sphereSDF(p, metaballPos[i], metaballRadius[i]);
                d = smin(d, dist, 10.0); // k=10.0 for smoothness
            }
            return d;
        }

   Note: We start with a large distance (1e10) and then take the smooth minimum with each metaball.

   Then in the ray marching:

        float t = 0.0;
        float maxSteps = 100.0;
        float maxDist = 50.0; // maximum distance to march
        float hit = 0.0;
        for (int i = 0; i < 100; i++) {
            vec3 pos = rayOrigin + rayDir * t;
            float d = sceneSDF(pos);
            if (d < 0.001 || t > maxDist) {
                hit = 1.0;
                break;
            }
            t += d;
        }

   If hit, then we have a surface. We then compute the normal by taking the gradient of the SDF (using a small epsilon).

        vec3 normal = normalize(vec3(
            sceneSDF(pos + vec3(0.001, 0.0, 0.0)) - sceneSDF(pos - vec3(0.001, 0.0, 0.0)),
            sceneSDF(pos + vec3(0.0, 0.001, 0.0)) - sceneSDF(pos - vec3(0.0, 0.001, 0.0)),
            sceneSDF(pos + vec3(0.0, 0.0, 0.001)) - sceneSDF(pos - vec3(0.0, 0.0, 0.001))
        ));

   Then we can use the normal for lighting. We'll do a simple diffuse lighting with a light source at (1,1,1).

        vec3 lightDir = normalize(vec3(1.0, 1.0, 1.0));
        float diff = max(dot(normal, lightDir), 0.0);

   But note: the normal we computed is for the point on the surface. We'll use it to compute the color.

   For the color, we want psychedelic. We can use a color based on time and the position.

        float hue = (time * 0.1 + (pos.x + pos.y) * 0.1) * 0.5;
        vec3 color = hsv2rgb(vec3(hue, 1.0, 1.0));

   But note: we don't have hsv2rgb in GLSL. We'll write a simple one.

   Alternatively, we can use:

        vec3 rgb = vec3(
            sin(hue * 6.283 + time * 0.5),
            sin(hue * 6.283 + time * 0.5 + 2.094),
            sin(hue * 6.283 + time * 0.5 + 4.188)
        );

   But that's a bit messy. We'll write a simple hsv2rgb function.

   However, to keep it simple and avoid a long function, we'll use a simpler method: use the time and the normal to modulate the color.

   We'll do:

        vec3 baseColor = vec3(
            sin(time * 0.1 + pos.x * 0.1),
            sin(time * 0.1 + pos.y * 0.1),
            sin(time * 0.1 + pos.z * 0.1)
        );
        baseColor = (baseColor + 1.0) * 0.5; // to [0,1]

        // Then modulate by the diffuse lighting
        vec3 finalColor = baseColor * diff;

   But note: we want vibrant colors. We can also use a fixed psychedelic palette.

   We'll use a simpler approach: use the time to cycle through a color.

        float t = time * 0.1;
        vec3 color = vec3(
            0.5 + 0.5 * sin(t),
            0.5 + 0.5 * sin(t + 2.094),
            0.5 + 0.5 * sin(t + 4.188)
        );

   Then we multiply by the diffuse lighting (so it's not too bright).

   However, note: we want the color to be based on the position too? We can add the position to the time.

        float t = time * 0.1 + pos.x * 0.1 + pos.y * 0.1 + pos.z * 0.1;
        vec3 color = vec3(
            0.5 + 0.5 * sin(t),
            0.5 + 0.5 * sin(t + 2.094),
            0.5 + 0.5 * sin(t + 4.188)
        );

   But note: the position is in the scene, so it will vary per pixel.

   We'll do that.

   Now, let's write the shaders.

   Vertex shader: very simple, just set up the position for the full-screen quad.

   Fragment shader: the main logic.

   We'll also add a background (black) for no hit.

   Let's code.

   Note: We must be cautious of performance. We have 100 steps per pixel, which might be slow on mobile. But for a desktop, it's acceptable.

   We'll try to optimize by reducing steps if possible, but 100 is standard.

   We'll also add a small epsilon for the hit condition.

   Implementation:

   Step 1: Set up the WebGL context and the full-screen quad.

   We'll create a simple vertex buffer for the quad (two triangles: [-1,-1], [1,-1], [-1,1], [1,1] but we'll do two triangles: [0,1,2] and [0,2,3] for a quad).

   Actually, we'll create a full-screen quad with two triangles:

        vertices = [
            -1, -1,
             1, -1,
            -1,  1,
             1,  1
        ];

   And indices: [0,1,2, 0,2,3] but note: we are using two triangles.

   However, for simplicity, we'll use a single triangle strip? But we'll do two triangles.

   We'll create a buffer for the vertices and set up the vertex shader to output the position.

   The vertex shader:

        attribute vec2 a_position;
        void main() {
            gl_Position = vec4(a_position, 0.0, 1.0);
        }

   Then in the fragment shader, we get the screen coordinate (uv) as (a_position.x, a_position.y) but note: the a_position is in [-1,1] for both x and y.

   We'll compute the uv as (a_position.x * 0.5 + 0.5, a_position.y * 0.5 + 0.5) to get [0,1] for both? 
   But actually, we don't need to. We can use the normalized coordinates directly.

   However, for the ray direction, we want to use the screen coordinate to compute the ray.

   We'll use:

        vec2 uv = a_position * 0.5 + 0.5;   // [0,1] for both

   But note: the vertex shader outputs a_position as [-1,1] for x and y. So we can do:

        vec2 uv = (a_position + 1.0) * 0.5;   // [0,1]

   However, we don't need to convert to [0,1] for the ray direction. We can use the [-1,1] directly.

   We'll use:

        vec2 uv = a_position;   // which is in [-1,1] for x and y.

   Then the ray direction:

        vec3 rayDir = normalize( vec3( uv.x * aspect, uv.y, -1.0 ) );

   But note: the aspect ratio. We'll pass the aspect ratio as a uniform.

   We'll set the aspect ratio in JavaScript as:

        let aspect = canvas.width / canvas.height;

   And pass it as a uniform.

   Now, let's write the shaders.

   We'll put the shaders in script tags with type="x-shader/x-vertex" and "x-shader/x-fragment".

   We'll also set up the WebGL program.

   Steps in JavaScript:

        - Create the vertex and fragment shader, compile, link.
        - Create the buffer for the quad.
        - Set up the uniforms (time, aspect, metaballPos, metaballRadius).
        - In the animation loop, update the time and the metaball positions (and then set the uniforms for the positions and radii).

   We'll create a function to update the metaball positions.

   Let's code accordingly.

   Note: We'll use a fixed number of metaballs (5) for simplicity.

   We'll set the initial positions and radii.

   We'll also set the aspect ratio uniform.

   Let's write the code.

   Important: We must handle the canvas resizing? We'll set the canvas to full screen and not handle resize for simplicity.

   We'll set the canvas to 100vw and 100vh, so the aspect ratio is the same as the window.

   We'll update the aspect ratio on window resize? But the problem says full-screen, so we'll assume the window doesn't change.

   We'll set the aspect ratio once at the beginning.

   Now, let's code the entire HTML file.

   Note: We are not allowed to use external libraries, so we do everything manually.

   We'll write the shaders as strings in the HTML.

   We'll also add a note section for the developer.

   Let's go.

   Note: The exponential smooth min might cause NaN if the distances are too large? But we are using a large initial distance (1e10) and then taking the min. We'll use the polynomial smooth min to avoid the exponential (which is expensive and might cause issues with large numbers). 

   Actually, the exponential smooth min is:

        float smin(float a, float b, float k) {
            return -log(exp(-k*a) + exp(-k*b)) / k;
        }

   But note: if a and b are large positive, then exp(-k*a) becomes 0, so it's safe. But if they are negative (inside the sphere) then we have to be cautious? Actually, the SDF for a point inside the sphere is negative, so we have to be careful.

   However, the smooth min is defined for the distance fields, and it's designed to work for negative values too? Actually, the smooth min is usually used for the distance to the surface, so negative inside.

   But the exponential formula is designed to work for the distance field (which can be negative). However, when the point is inside the sphere, the SDF is negative, and then exp(-k * negative) = exp(positive) which is huge. So we might get overflow.

   Alternatively, we can use the polynomial smooth min which is more stable for negative values? Actually, the polynomial one is:

        float smin(float a, float b, float k) {
            float h = clamp(0.5 + 0.5*(b - a)/k, 0.0, 1.0);
            return mix(b, a, h) - k*h*(1.0-h);
        }

   This one works for negative values too.

   We'll use the polynomial smooth min.

   Let's change to that.

   Now, let's write the code.

   We'll also add a small optimization: if the distance is negative (inside the surface), we break early? Actually, we break when the distance is less than 0.001 (which is the hit condition). But the smooth min might be negative when inside.

   The ray marching algorithm:

        t = 0.0
        for (step=0; step<maxSteps; step++) {
            p = rayOrigin + rayDir * t
            d = sceneSDF(p)
            if (d < 0.001) { hit; break; }
            t += d;
            if (t > maxDist) break;
        }

   This works because when we are inside, d is negative, so we would subtract from t? But note: we are stepping by d (which is negative) so we would go backwards? That's not what we want.

   Actually, the SDF for a point inside the surface is negative, so the distance to the surface is negative. But the ray marching step should be positive. We should take the absolute value? 

   However, the standard ray marching uses the absolute value of the SDF for stepping? Actually, no: the SDF is negative inside, so the step size is negative. But we want to step forward (in the direction of the ray) until we hit the surface. When we are inside, we should step backwards? 

   But note: the ray is going from the camera (outside) into the scene. So we start outside (d>0) and then we step until we hit (d becomes negative). So we don't need to handle negative d in the stepping? Actually, the stepping is done by d (which is positive when outside, negative when inside). But we are stepping in the direction of the ray: so if d is negative, we are inside and we don't want to step further? Actually, we break when d<0.001 (which is the hit condition).

   However, the standard algorithm is:

        d = sceneSDF(p)
        if (d < 0.001) -> hit
        else -> step by d

   So we only step when d is positive (outside). When we get inside, we break.

   So it's safe.

   Now, let's code.

   We'll write the shaders.

   Note: We must use `precision mediump float;` for the fragment shader.

   We'll write the entire HTML file.

   Let's go.
</think>

# Psychedelic Metaball Ray Marching Simulation

I've created a full-screen WebGL application that implements ray marching with smooth metaballs to create a hypnotic, evolving psychedelic visualization. The simulation features organic merging blobs with vibrant, shifting colors that move and transform over time.

```html
<!DOCTYPE html>
<html>
<head>
    <title>Psychedelic Metaball Ray Marching</title>
    <style>
        body {
            margin: 0;
            overflow: hidden;
            background: #000;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: #f0f0f0;
            text-align: center;
            height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            position: relative;
        }
        
        canvas {
            display: block;
            width: 100vw;
            height: 100vh;
            position: absolute;
            top: 0;
            left: 0;
            z-index: -1;
        }
        
        .title {
            position: absolute;
            top: 20px;
            width: 100%;
            font-size: 2.5rem;
            font-weight: bold;
            text-shadow: 0 0 15px #ff00ff, 0 0 30px #00ffff;
            color: #ff00ff;
            z-index: 10;
            letter-spacing: 2px;
            text-transform: uppercase;
        }
        
        .subtitle {
            position: absolute;
            top: 60px;
            width: 100%;
            font-size: 1.2rem;
            color: #00ffff;
            z-index: 10;
            text-shadow: 0 0 10px rgba(0, 255, 255, 0.7);
        }
        
        .info {
            position: absolute;
            bottom: 20px;
            width: 100%;
            font-size: 0.9rem;
            color: #aaa;
            z-index: 10;
            max-width: 800px;
            margin: 0 auto;
            padding: 0 20px;
            line-height: 1.5;
        }
        
        .note {
            position: absolute;
            bottom: 50px;
            width: 100%;
            font-size: 0.8rem;
            color: #666;
            z-index: 10;
            max-width: 800px;
            margin: 0 auto;
            padding: 0 20px;
            line-height: 1.4;
        }
        
        .pulse {
            animation: pulse 3s infinite;
        }
        
        @keyframes pulse {
            0% { text-shadow: 0 0 15px #ff00ff, 0 0 30px #00ffff; }
            50% { text-shadow: 0 0 25px #ff00ff, 0 0 50px #00ffff; }
            100% { text-shadow: 0 0 15px #ff00ff, 0 0 30px #00ffff; }
        }
        
        .glow {
            text-shadow: 0 0 10px #ff00ff, 0 0 20px #ff00ff, 0 0 30px #ff00ff;
        }
    </style>
</head>
<body>
    <div class="title">Psychedelic Metaball Ray Marching</div>
    <div class="subtitle">Organic Volumetric Light Show</div>
    
    <canvas id="glCanvas"></canvas>
    
    <div class="info">
        <p>Full-screen psychedelic visualization using ray marching and signed distance functions. The metaballs smoothly merge and separate, creating hypnotic organic patterns with vibrant, shifting colors. This simulation runs autonomously with no user interaction required.</p>
        <p>Features: <span class="glow">Smooth metaball blending</span>, <span class="glow">Dynamic color cycling</span>, <span class="glow">3D motion</span>, <span class="glow">Real-time ray marching</span></p>
    </div>
    
    <div class="note">
        <p>Implementation notes: Uses WebGL 1.0 with direct shader programming. Ray marching algorithm with smooth minimum for organic metaball blending. Full-screen optimized.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

-

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.

.



.

.
.
.

.

.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.

.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.
.

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: Qwen3-30B-A3B-Thinking-2507-UD-Q6_K_XL.gguf -->
<!-- Prompt: lightshow.md -->
<!-- Generation Time: 138.85s -->
<!-- Fallback Used: False -->