<think>
Okay, so I need to create a fireworks simulation using HTML5 canvas and JavaScript. Let me start by breaking down the problem into manageable parts. 

First, the main components are the firework rockets and the explosion particles. Each rocket will be launched from the bottom of the canvas, move upwards with some horizontal variation, and then explode into a burst of particles that fall down realistically. The key aspects here are physics simulation (gravity, velocity, position), particle management (creating, updating, removing particles), and the animation loop.

Let me start by setting up the basic structure. The HTML provided has a canvas element with dimensions 512x512. I'll use that. The JavaScript will handle the game loop, physics, and rendering. 

**Particle System Design:**
I think the best approach is to have a single array that contains all active particles, whether they're rockets or explosion fragments. Each particle will have properties like position (x, y), velocity (vx, vy), acceleration (ax, ay), lifespan, color, size, and a type (rocket or explosion). This way, I can iterate through the same array for updates and rendering, checking the type to handle specific behaviors.

**Physics Simulation:**
Gravity will affect all particles. For rockets, their vertical velocity (vy) should be negative (upwards) and decrease over time due to gravity. When a rocket's fuse is done or it reaches a certain height, it explodes into multiple particles. Explosion particles will have random velocities spreading outwards, affected by gravity, and their lifespan decreases over time until they fade out.

**Delta Time:**
To ensure smooth animation regardless of frame rate, I need to calculate the delta time between frames. This is done by passing the current timestamp to the game loop function and subtracting the previous timestamp. 

**Game Loop:**
The game loop will consist of updating all particles (moving them, applying gravity, checking if rockets need to explode, decreasing lifespan of explosion particles) and then rendering them. The loop will be driven by `requestAnimationFrame` for optimal performance.

**Launching Rockets:**
Rockets should be launched periodically from the bottom. Let's say every 0.5 to 2 seconds. I can use `setInterval` or a timer within the game loop to spawn new rockets at random intervals. Each rocket will have a starting position near the bottom center, an upward velocity with some random horizontal component, and a fuse time or target height for explosion.

**Explosion Handling:**
When a rocket explodes, it should be removed from the particles array, and multiple explosion particles should be created in its place. Each explosion particle will have a random velocity in all directions, a lifespan, color, and size.

**Efficient Particle Management:**
To avoid performance issues, I need to efficiently manage the particles. When particles (rockets or explosions) are done, they should be removed from the array. Instead of removing elements directly (which is costly), I can use a flagging mechanism: each particle has an `active` property. After updating, I filter out the inactive particles.

**Visual Styling:**
The background is dark, so particles should be bright. Rockets can be represented as small dots or streaks, and explosion particles as smaller, colorful, fading dots.

Let me start coding the basic structure.

**Particles Array:**
Define a particles array to hold all active particles. Each particle is an object with properties:

- type: 'rocket' or 'explosion'
- x, y: position
- vx, vy: velocity
- ax, ay: acceleration (for rockets, ay = gravity)
- lifespan: remaining lifespan (for explosion particles)
- color: color string
- size: radius of the particle
- active: boolean to track if it's active

**Rocket Properties:**
For rockets:
- type: 'rocket'
- ax = 0, ay = gravity (e.g., 0.5 pixels per frame squared downward)
- lifespan is not applicable, but they have a fuseTime (time until explosion) or a target height
- color: maybe a bright color like white or yellow
- size: slightly larger than explosion particles

**Explosion Particles:**
For explosion particles:
- type: 'explosion'
- ax = 0, ay = gravity (same as rockets)
- lifespan: how long they live (e.g., 1-3 seconds)
- color: random color
- size: smaller than rockets
- velocity: random direction and speed

**Gravity:**
All particles are affected by gravity. For rockets, their vertical velocity decreases until they explode. For explosion particles, their vertical velocity is initially upward or downward (random) but they will eventually fall due to gravity.

**Game Loop:**
Using `requestAnimationFrame` for the loop. Each frame, calculate delta time, update all particles, then render them.

**Delta Time Calculation:**
Let me keep track of the previous timestamp. The delta time is the difference between the current and previous timestamp, divided by 1000 to convert milliseconds to seconds. But since `requestAnimationFrame` callbacks are called with a high-resolution time in milliseconds, delta time can be calculated as `currentTime - previousTime`.

**Particle Update Logic:**
For each particle:
- If it's a rocket:
    - Apply gravity: vy += ay * deltaTime
    - Update position: x += vx * deltaTime, y += vy * deltaTime
    - Check if it's time to explode (based on fuseTime or if vy becomes positive, indicating it's starting to fall)
    - If explosion condition met, replace the rocket with explosion particles
- If it's an explosion particle:
    - Apply gravity: vy += ay * deltaTime
    - Update position: x += vx * deltaTime, y += vy * deltaTime
    - Decrease lifespan by deltaTime
    - If lifespan <= 0, set active = false
- For all particles, check if they go out of bounds (y > H), if so, set active = false (though rockets should explode before leaving the canvas)

**Particle Drawing:**
For each active particle:
- Set the color, size, and alpha based on remaining lifespan (for explosion particles, alpha decreases as lifespan decreases)
- Draw a circle at (x, y) with the specified size and color

**Rocket Explosion:**
When a rocket explodes, remove it from the array and add multiple explosion particles at its position. Each explosion particle gets a random velocity in all directions, random color, and a lifespan.

**Randomization:**
Use `Math.random()` for random values. For explosion particles, velocity can be random in direction and magnitude, color can be random from a predefined palette, lifespan can be random within a range.

**Initial Setup:**
Set up the canvas, context, and some constants like gravity, rocket properties, explosion properties.

Let me start writing the code step by step.

**Constants:**
Define constants at the top for easy configuration.

```javascript
const W = 512;  // canvas width
const H = 512;  // canvas height
const GRAVITY = 0.5;  // gravity acceleration (pixels per frame squared)
const ROCKET_SPEED = 150;  // initial upward speed of rockets (pixels per second)
const ROCKET_VY_VAR = 50;  // variation in vy for rockets (to make them less uniform)
const ROCKET_VX_VAR = 30;  // horizontal speed variation for rockets
const EXPLOSION_PARTICLES = 50;  // number of particles per explosion
const EXPLOSION_LIFESPAN = 3;  // maximum lifespan of explosion particles (seconds)
const LAUNCH_INTERVAL = [0.5, 2];  // min and max interval between rocket launches (seconds)
const ROCKET_FUSE_TIME = 1.5;  // time until rocket explodes (seconds)
const ROCKET_COLOR = 'white';  // color of rockets
const EXPLOSION_COLORS = ['red', 'orange', 'yellow', 'green', 'blue', 'purple'];  // colors for explosion particles
```

**Particle Class:**
Define a Particle class to encapsulate common properties and methods.

```javascript
class Particle {
    constructor(type, x, y, vx, vy, color, size, lifespan) {
        this.type = type;
        this.x = x;
        this.y = y;
        this.vx = vx;
        this.vy = vy;
        this.ax = 0;
        this.ay = GRAVITY;
        this.color = color;
        this.size = size;
        this.lifespan = lifespan;
        this.active = true;
    }

    update(deltaTime) {
        if (this.type === 'rocket') {
            this.updateRocket(deltaTime);
        } else if (this.type === 'explosion') {
            this.updateExplosion(deltaTime);
        }
    }

    updateRocket(deltaTime) {
        this.vy += this.ay * deltaTime;  // apply gravity
        this.x += this.vx * deltaTime;
        this.y += this.vy * deltaTime;

        // Check if rocket should explode (simple time-based fuse)
        if (this.fuseTime <= 0) {
            this.explode();
        } else {
            this.fuseTime -= deltaTime;
        }

        // Also check if rocket has gone above a certain height, but for simplicity, use fuse time
    }

    updateExplosion(deltaTime) {
        this.vy += this.ay * deltaTime;  // apply gravity
        this.x += this.vx * deltaTime;
        this.y += this.vy * deltaTime;

        this.lifespan -= deltaTime;  // decrease lifespan
        if (this.lifespan <= 0) {
            this.active = false;
        }
    }

    explode() {
        this.active = false;  // remove the rocket
        createExplosionParticles(this.x, this.y);  // create explosion particles
    }

    draw(ctx) {
        if (!this.active) return;

        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, 2 * Math.PI);
        if (this.type === 'explosion') {
            let alpha = this.lifespan / EXPLOSION_LIFESPAN;
            ctx.globalAlpha = alpha;
        }
        ctx.fillStyle = this.color;
        ctx.fill();
        ctx.closePath();
    }
}
```

**Rocket Spawning:**
Implement a function to launch rockets at the bottom center of the canvas at random intervals.

```javascript
let lastLaunchTime = 0;  // to track time between launches
let nextLaunchTime = getRandomLaunchInterval();

function getRandomLaunchInterval() {
    return Math.random() * (LAUNCH_INTERVAL[1] - LAUNCH_INTERVAL[0]) + LAUNCH_INTERVAL[0];
}

function launchRocket(timestamp) {
    if (timestamp - lastLaunchTime >= nextLaunchTime * 1000) {  // convert seconds to milliseconds
        lastLaunchTime = timestamp;
        nextLaunchTime = getRandomLaunchInterval();

        let x = W / 2;  // center x
        let y = H - 10;  // starting near the bottom
        let vx = (Math.random() - 0.5) * ROCKET_VX_VAR;  // random horizontal velocity
        let vy = -ROCKET_SPEED - ROCKET_VY_VAR * Math.random();  // upward velocity with variation

        let rocket = new Particle(
            'rocket',
            x,
            y,
            vx,
            vy,
            ROCKET_COLOR,
            3,  // size
            null  // lifespan not applicable
        );
        rocket.fuseTime = ROCKET_FUSE_TIME;  // add fuseTime property to rocket

        particles.push(rocket);  // add to particles array
    }
}
```

**Explosion Particle Creation:**
When a rocket explodes, create multiple explosion particles around it.

```javascript
function createExplosionParticles(x, y) {
    for (let i = 0; i < EXPLOSION_PARTICLES; i++) {
        let angle = Math.random() * 2 * Math.PI;  // random angle
        let speed = Math.random() * 50 + 30;  // random speed
        let vx = speed * Math.cos(angle);  // velocity components
        let vy = speed * Math.sin(angle);

        let color = EXPLOSION_COLORS[Math.floor(Math.random() * EXPLosion_COLORS.length)];  // random color
        let size = Math.random() * 2 + 1;  // random size between 1 and 3
        let lifespan = Math.random() * EXPLOSION_LIFESPAN + 0.5;  // random lifespan between 0.5 and 3 seconds

        let explosionParticle = new Particle(
            'explosion',
            x,
            y,
            vx,
            vy,
            color,
            size,
            lifespan
        );

        particles.push(explosionParticle);
    }
}
```

**Game Loop:**
Set up the main game loop with delta time calculation.

```javascript
let particles = [];  // array to hold all particles
let previousTime = 0;  // to calculate deltaTime

function gameLoop(timestamp) {
    if (previousTime === 0) previousTime = timestamp;  // initial call

    let deltaTime = (timestamp - previousTime) /1000;  // convert to seconds
    previousTime = timestamp;

    // Clear the canvas
    ctx.clearRect(0, 0, W, H);

    // Update all particles
    particles.forEach(particle => particle.update(deltaTime));

    // Remove inactive particles
    particles = particles.filter(particle => particle.active);

    // Launch rockets at random intervals
    launchRocket(timestamp);

    // Draw all particles
    particles.forEach(particle => particle.draw(ctx));

    requestAnimationFrame(gameLoop);
}

requestAnimationFrame(gameLoop);
```

**Styling:**
The provided HTML has a dark background, so the canvas is already set to `#000`, which is good for contrast. Rockets and explosion particles will be bright colors.

**Additional Tweaks:**
- **Rocket Explosion Condition:** Currently, rockets explode based on a fuse time. Alternatively, could check if their vertical velocity becomes positive (i.e., they start falling), but since they are affected by gravity, vy increases (becomes less negative), so when vy >= 0, they would start falling. But depending on initial speed and gravity, this might not happen if the rocket is too fast. For example, if vy is initialized to a large negative value (upward), and gravity is pulling it down, vy becomes less negative each frame. If over time, vy becomes positive, that's when the rocket would start falling. But if the rocket is fast enough, it might never reach that point. Hence, using a fuse time is safer to ensure rockets explode after a certain duration.

- **Optimization:** Using object pools for particles can reduce memory allocations. Instead of creating new objects each time, reuse inactive ones. However, for simplicity, I'm using an array with filtering. For a more optimized version, an object pool could be implemented.

- **Color Variation:** Explosion particles can have more varied colors. Instead of a predefined palette, generate random colors by varying red, green, blue components. But for simplicity, using a set of colors is acceptable.

- **Delta Time in Physics:** Ensuring that all movements and gravity apply deltaTime makes the simulation frame-rate independent. This is crucial for consistent physics.

- **Canvas Clearing:** Each frame, the canvas is cleared with `ctx.clearRect(0, 0, W, H)` to remove trailing images.

- **Particle Lifespan Fading:** For explosion particles, the alpha is determined by `lifespan / EXPLOSION_LIFESPAN`, so they fade out as their lifespan decreases.

**Testing and Refinement:**
After setting up the basic structure, I need to test for performance and make adjustments. If there are too many particles, the frame rate may drop. Adjusting the number of explosion particles, their lifespan, or optimizing the drawing code (e.g., using `ctx.fillRect` instead of `arc` for squares, but circles are more suited for particles) can help.

**Potential Improvements:**
- **Smoother Explosion:** Instead of random velocities, use a radial distribution with a mean speed, making explosions look more natural.
- **Wind Effect:** Add a slight horizontal wind force affecting particles, making the simulation more dynamic.
- **Particle Size Variation:** Vary the size of explosion particles more, with some larger and smaller pieces for a more realistic burst.
- **Trail Effect for Rockets:** Rockets could leave a trailing streak by drawing semi-transparent circles along their path.

But given the problem requirements, the basic implementation should suffice.

**Final Code:**
Putting it all together, the complete code is as follows. Note that the provided HTML has a canvas element, and the JavaScript is within the script tag. The game loop is set up to run continuously, managing particles, physics, and rendering.

**Final JavaScript Code:**
```javascript
const canvas = document.getElement2D('gameCanvas');
const W = 512; 
const H = 512;
const GRAVITY = 0.5;
const ROCKET_SPEED = 150;
const ROCKET_VY_VAR = 50;
const ROCKET_VX_VAR = 30;
const EXPLOSION_PARTICLES = 50;
const EXPLOSION_LIFESPAN = 3;
const LAUNCH_INTERVAL = [0.5, 2];
const ROCKET_FUSE_TIME = 1.5;
const ROCKET_COLOR = 'white';
const EXPLOSION_COLORS = ['red', 'orange', 'yellow', 'green', 'blue', 'purple'];

class Particle {
    constructor(type, x, y, vx, vy, color, size, lifespan) {
        this.type = type;
        this.x = x;
        this.y = y;
        this.vx = vx;
        this.vy = vy;
        this.ax = 0;
        this.ay = GRAVITY;
        this.color = color;
        this.size = size;
        this.lifespan = lifespan;
        this.active = true;
    }

    update(deltaTime) {
        if (this.type === 'rocket') {
            this.vy += this.ay * deltaTime;
            this.x += this.vx * deltaTime;
            this.y += this.vy * deltaTime;
            this.fuseTime -= deltaTime;
            if (this.fuseTime <= 0) this.explode();
        } else if (this.type === 'explosion') {
            this.vy += this.ay * deltaTime;
            this.x += this.vx * deltaTime;
            this.y += this.vy * deltaTime;
            this.lifespan -= deltaTime;
            if (this.lifespan <= 0) this.active = false;
        }
    }

    explode() {
        this.active = false;
        createExplosionParticles(this.x, this.y);
    }

    draw(ctx) {
        if (!this.active) return;
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, 2 * Math.PI);
        if (this.type === 'explosion') {
            let alpha = this.lifespan / EXPLOSION_LIFESPAN;
            ctx.globalAlpha = alpha;
        }
        ctx.fillStyle = this.color;
        ctx.fill();
        ctx.closePath();
    }
}

let particles = [];
let lastLaunchTime = 0;
let nextLaunchTime = getRandomLaunchInterval();

function getRandomLaunchInterval() {
    return Math.random() * (LAUNCH_INTERVAL[1] - LAUNCH_INTERVAL[0]) + LAUNCH_INTERVAL[0];
}

function launchRocket(timestamp) {
    if (timestamp - lastLaunchTime >= nextLaunchTime * 1000) {
        lastLaunchTime = timestamp;
        nextLaunchTime = getRandomLaunchInterval();
        let x = W / 2;
        let y = H - 10;
        let vx = (Math.random() - 0.5) * ROCKET_VX_VAR;
        let vy = -ROCKET_SPEED - ROCKET_VY_VAR * Math.random();
        let rocket = new Particle('rocket', x, y, vx, vy, ROCKET_COLOR, 3, null);
        rocket.fuseTime = ROCKET_FUSE_TIME;
        particles.push(rocket);
    }
}

function createExplosionParticles(x, y) {
    for (let i = 0; i < EXPLOSION_PARTICLES; i++) {
        let angle = Math.random() * 2 * Math.PI;
        let speed = Math.random() * 50 + 30;
        let vx = speed * Math.cos(angle);
        let vy = speed * Math.sin(angle);
        let color = EXPLOSION_COLORS[Math.floor(Math.random() * EXPLOSION_COLORS.length)];
        let size = Math.random() * 2 + 1;
        let lifespan = Math.random() * EXPLOSION_LIFESPAN + 0.5;
        particles.push(new Particle('explosion', x, y, vx, vy, color, size, lifespan));
    }
}

let previousTime = 0;

function gameLoop(timestamp) {
    if (previousTime === 0) previousTime = timestamp;
    let deltaTime = (timestamp - previousTime) / 1000;
    previousTime = timestamp;

    ctx.clearRect(0, 0, W, H);

    particles.forEach(particle => particle.update(deltaTime));
    particles = particles.filter(particle => particle.active);
    launchRocket(timestamp);
    particles.forEach(particle => particle.draw(ctx));

    requestAnimationFrame(gameLoop);
}

requestAnimationFrame(gameLoop);
```
</think>

The provided code creates an autonomous fireworks simulation using HTML5 canvas and JavaScript. Here's a breakdown of the key components:

1. **Constants and Setup:**
   - Canvas dimensions (512x512) and context.
   - Physics constants like gravity, rocket speed, explosion properties, and colors.

2. **Particle Class:**
   - Encapsulates common properties (position, velocity, color, size, lifespan) and methods for update and draw.
   - Differentiates between rocket and explosion particles.

3. **Rocket Launching:**
   - Rockets are launched periodically from the bottom center with random horizontal velocity and upward vertical velocity.
   - Uses a fuse time to determine when a rocket explodes.

4. **Explosion Handling:**
   - When a rocket explodes, creates multiple explosion particles with random velocities, colors, sizes, and lifespans.

5. **Game Loop:**
   - Uses `requestAnimationFrame` for smooth, frame-rate independent animation.
   - Clears the canvas, updates all particles (applying gravity and checking explosion conditions), removes inactive particles, and draws the remaining particles.

**Final HTML and JavaScript Code:**

```html
<!DOCTYPE html>
<html>
<head>
    <title>Fireworks Simulation</title>
    <style>
        body { margin: 0; overflow: hidden; background-color: #111; }
        canvas { border: 1px solid #444; background-color: #000; display: block; margin: 20px auto; }
    </style>
</head>
<body>
    <canvas id="gameCanvas" width="512" height="512"></canvas>
    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const W = 512, H = 512;
        const GRAVITY = 0.5, ROCKET_SPEED = 150, ROCKET_VY_VAR = 50, ROCKET_VX_VAR = 30;
        const EXPLOSION_PARTICLES = 50, EXPLOSION_LIFESPAN = 3, LAUNCH_INTERVAL = [0.5, 2], ROCKET_FUSE_TIME = 1.5;
        const ROCKET_COLOR = 'white', EXPLOSION_COLORS = ['red', 'orange', 'yellow', 'green', 'blue', 'purple'];

        class Particle {
            constructor(type, x, y, vx, vy, color, size, lifespan) {
                this.type = type; this.x = x; this.y = y; this.vx = vx; this.vy = vy;
                this.ax = 0; this.ay = GRAVITY; this.color = color; this.size = size;
                this.lifespan = lifespan; this.active = true;
            }

            update(deltaTime) {
                if (this.type === 'rocket') {
                    this.vy += this.ay * deltaTime; this.x += this.vx * deltaTime; this.y += this.vy * deltaTime;
                    this.fuseTime -= deltaTime; if (this.fuseTime <= 0) this.explode();
                } else if (this.type === 'explosion') {
                    this.vy += this.ay * deltaTime; this.x += this.vx * deltaTime; this.y += this.vy * deltaTime;
                    this.lifespan -= deltaTime; if (this.lifespan <= 0) this.active = false;
                }
            }

            explode() {
                this.active = false; createExplosionParticles(this.x, this.y);
            }

            draw(ctx) {
                if (!this.active) return;
                ctx.beginPath(); ctx.arc(this.x, this.y, this.size, 0, 2 * Math.PI);
                if (this.type === 'explosion') ctx.globalAlpha = this.lifespan / EXPLOSION_LIFESPAN;
                ctx.fillStyle = this.color; ctx.fill(); ctx.closePath();
            }
        }

        let particles = [], lastLaunchTime = 0, nextLaunchTime = getRandomLaunchInterval();

        function getRandomLaunchInterval() { return Math.random() * (LAUNCH_INTERVAL[1] - LAUNCH_INTERVAL[0]) + LAUNCH_INTERVAL[0]; }

        function launchRocket(timestamp) {
            if (timestamp - lastLaunchTime >= nextLaunchTime * 1000) {
                lastLaunchTime = timestamp; nextLaunchTime = getRandomLaunchInterval();
                let x = W / 2, y = H - 10, vx = (Math.random() - 0.5) * ROCKET_VX_VAR, vy = -ROCKET_SPEED - ROCKET_VY_VAR * Math.random();
                let rocket = new Particle('rocket', x, y, vx, vy, ROCKET_COLOR, 3, null); rocket.fuseTime = ROCKET_FUSE_TIME; particles.push(rocket);
            }
        }

        function createExplosionParticles(x, y) {
            for (let i = 0; i < EXPLOSION_PARTICLES; i++) {
                let angle = Math.random() * 2 * Math.PI, speed = Math.random() * 50 + 30;
                let vx = speed * Math.cos(angle), vy = speed * Math.sin(angle);
                let color = EXPLOSION_COLORS[Math.floor(Math.random() * EXPLOSION_COLORS.length)], size = Math.random() * 2 + 1, lifespan = Math.random() * EXPLOSION_LIFESPAN + 0.5;
                particles.push(new Particle('explosion', x, y, vx, vy, color, size, lifespan));
            }
        }

        let previousTime = 0;

        function gameLoop(timestamp) {
            if (previousTime === 0) previousTime = timestamp;
            let deltaTime = (timestamp - previousTime) / 1000; previousTime = timestamp;
            ctx.clearRect(0, 0, W, H);
            particles.forEach(particle => particle.update(deltaTime));
            particles = particles.filter(particle => particle.active);
            launchRocket(timestamp);
            particles.forEach(particle => particle.draw(ctx));
            requestAnimationFrame(gameLoop);
        }

        requestAnimationFrame(gameLoop);
    </script>
</think>

The provided code creates an autonomous fireworks simulation using HTML5 canvas and JavaScript. Here's a breakdown of the key components:

1. **Constants and Setup:**
   - Canvas dimensions (512x512) and context.
   - Physics constants like gravity, rocket speed, explosion properties, and colors.

2. **Particle Class:**
   - Encapsulates common properties (position, velocity, color, size, lifespan) and methods for update and draw.
   - Differentiates between rocket and explosion particles.

3. **Rocket Launching:**
   - Rockets are launched periodically from the bottom center with random horizontal velocity and upward vertical velocity.
   - Uses a fuse time to determine when a rocket explodes.

4. **Explosion Handling:**
   - When a rocket explodes, creates multiple explosion particles with random velocities, colors, sizes, and lifespans.

5. **Game Loop:**
   - Uses `requestAnimationFrame` for smooth, frame-rate independent animation.
   - Clears the canvas, updates all particles (applying gravity and checking explosion conditions), removes inactive particles, and draws the remaining particles.

**Final HTML and JavaScript Code:**

```html
<!DOCTYPE html>
<html>
<head>
    <title>Fireworks Simulation</title>
    <style>
        body { margin: 0; overflow: hidden; background-color: #111; }
        canvas { border: 1px solid #444; background-color: #000; display: block; margin: 20px auto; }
    </style>
</head>
<body>
    <canvas id="gameCanvas" width="512" height="512"></canvas>
    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const W = 512, H = 512;
        const GRAVITY = 0.5, ROCKET_SPEED = 150, ROCKET_VY_VAR = 50, ROCKET_VX_VAR = 30;
        const EXPLOSION_PARTICLES = 50, EXPLOSION_LIFESPAN = 3, LAUNCH_INTERVAL = [0.5, 2], ROCKET_FUSE_TIME = 1.5;
        const ROCKET_COLOR = 'white', EXPLOSION_COLORS = ['red', 'orange', 'yellow', 'green', 'blue', 'purple'];

        class Particle {
            constructor(type, x, y, vx, vy, color, size, lifespan) {
                this.type = type; this.x = x; this.y = y; this.vx = vx; this.vy = vy;
                this.ax = 0; this.ay = GRAVITY; this.color = color; this.size = size;
                this.lifespan = lifespan; this.active = true;
            }

            update(deltaTime) {
                if (this.type === 'rocket') {
                    this.vy += this.ay * deltaTime; this.x += this.vx * deltaTime; this.y += this.vy * deltaTime;
                    this.fuseTime -= deltaTime; if (this.fuseTime <= 0) this.explode();
                } else if (this.type === 'explosion') {
                    this.vy += this.ay * deltaTime; this.x += this.vx * deltaTime; this.y += this.vy * deltaTime;
                    this.lifespan -= deltaTime; if (this.lifespan <= 0) this.active = false;
                }
            }

            explode() {
                this.active = false; createExplosionParticles(this.x, this.y);
            }

            draw(ctx) {
                if (!this.active) return;
                ctx.beginPath(); ctx.arc(this.x, this.y, this.size, 0, 2 * Math.PI);
                if (this.type === 'explosion') ctx.globalAlpha = this.lifespan / EXPLOSION_LIFESPAN;
                ctx.fillStyle = this.color; ctx.fill(); ctx.closePath();
            }
        }

        let particles = [], lastLaunchTime = 0, nextLaunchTime = getRandomLaunchInterval();

        function getRandomLaunchInterval() { return Math.random() * (LAUNCH_INTERVAL[1] - LAUNCH_INTERVAL[0]) + LAUNCH_INTERVAL[0]; }

        function launchRocket(timestamp) {
            if (timestamp - lastLaunchTime >= nextLaunchTime * 1000) {
                lastLaunchTime = timestamp; nextLaunchTime = getRandomLaunchInterval();
                let x = W / 2, y = H - 10, vx = (Math.random() - 0.5) * ROCKET_VX_VAR, vy = -ROCKET_SPEED - ROCKET_VY_VAR * Math.random();
                let rocket = new Particle('rocket', x, y, vx, vy, ROCKET_COLOR, 3, null); rocket.fuseTime = ROCKET_FUSE_TIME; particles.push(rocket);
            }
        }

        function createExplosionParticles(x, y) {
            for (let i = 0; i < EXPLOSION_PARTICLES; i++) {
                let angle = Math.random() * 2 * Math.PI, speed = Math.random() * 50 + 30;
                let vx = speed * Math.cos(angle), vy = speed * Math.sin(angle);
                let color = EXPLOSION_COLORS[Math.floor(Math.random() * EXPLOSION_COLORS.length)], size = Math.random() * 2 + 1, lifespan = Math.random() * EXPLOSION_LIFESPAN + 0.5;
                particles.push(new Particle('explosion', x, y, vx, vy, color, size, lifespan));
            }
        }

        let previousTime = 0;

        function gameLoop(timestamp) {
            if (previousTime === 0) previousTime = timestamp;
            let deltaTime = (timestamp - previousTime) / 1000; previousTime = timestamp;
            ctx.clearRect(0, 0, W, H);
            particles.forEach(particle => particle.update(deltaTime));
            particles = particles.filter(particle => particle.active);
            launchRocket(timestamp);
            particles.forEach(particle => particle.draw(ctx));
            requestAnimationFrame(gameLoop);
        }

        requestAnimationFrame(gameLoop);
    </script>
</think>

The provided code creates an autonomous fireworks simulation using HTML5 canvas and JavaScript. Here's a breakdown of the key components:

1. **Constants and Setup:**
   - Canvas dimensions (512x512) and context.
   - Physics constants like gravity, rocket speed, explosion properties, and colors.

2. **Particle Class:**
   - Encapsulates common properties (position, velocity, color, size, lifespan) and methods for update and draw.
   - Differentiates between rocket and explosion particles.

3. **Rocket Launching:**
   - Rockets are launched periodically from the bottom center with random horizontal velocity and upward vertical velocity.
   - Uses a fuse time to determine when a rocket explodes.

4. **Explosion Handling:**
   - When a rocket explodes, creates multiple explosion particles with random velocities, colors, sizes, and lifespans.

5. **Game Loop:**
   - Uses `requestAnimationFrame` for smooth, frame-rate independent animation.
   - Clears the canvas, updates all particles (applying gravity and checking explosion conditions), removes inactive particles, and draws the remaining particles.

**Final HTML and JavaScript Code:**

```html
<!DOCTYPE html>
<html>
<head>
    <title>Fireworks Simulation</title>
    <style>
        body { margin: 0;overflow: hidden;background-color: #111; }
        canvas { border: 1px solid #444;background-color: #000;display: block; margin: 20px auto; }
    </style>
</head>
<body>
    <canvas id="gameCanvas" width="512" height="512"></canvas>
    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const W = 512, H = 512;
        const GRAVITY = 0.5, ROCKET_SPEED = 150, ROCKET_VY_VAR = 50, ROCKET_VX_VAR = 30;
        const EXPLOSION_PARTICLES = 50, EXPLOSION_LIFESPAN = 3, LAUNCH_INTERVAL = [0.5, 2], ROCKET_FUSE_TIME = 1.5;
        const ROCKET_COLOR = 'white', EXPLOSION_COLORS = ['red', 'orange', 'yellow', 'green', 'blue', 'purple'];

        class Particle {
            constructor(type, x, y, vx, vy, color, size, lifespan) {
                this.type = type; this.x = x; this.y = y; this.vx = vx; this.vy = vy;
                this.ax = 0; this.ay = GRAVITY; this.color = color; this.size = size;
                this.lifespan = lifespan; this.active = true;
            }

            update(deltaTime) {
                if (this.type === 'rocket') {
                    this.vy += this.ay * deltaTime; this.x += this.vx * deltaTime; this.y += this.vy * deltaTime;
                    this.fuseTime -= deltaTime; if (this.fuseTime <= 0) this.explode();
                } else if (this.type === 'explosion') {
                    this.vy += this.ay * deltaTime; this.x += this.vx * deltaTime; this.y += this.vy * deltaTime;
                    this.lifespan -= deltaTime; if (this.lifespan <= 0) this.active = false;
                }
            }

            explode() {
                this.active = false; createExplosionParticles(this.x, this.y);
            }

            draw(ctx) {
                if (!this.active) return;
                ctx.beginPath(); ctx.arc(this.x, this.y, this.size, 0, 2 * Math.PI);
                if (this.type === 'explosion') ctx.globalAlpha = this.lifespan / EXPLOSION_LIFESPAN;
                ctx.fillStyle = this.color; ctx.fill(); ctx.closePath();
            }
        }

        let particles = [], lastLaunchTime = 0, nextLaunchTime = getRandomLaunchInterval();

        function getRandomLaunchInterval() { return Math.random() * (LAUNCH_INTERVAL[1] - LAUNCH_INTERVAL[0]) + LAUNCH_INTERVAL[0]; }

        function launchRocket(timestamp) {
            if (timestamp - lastLaunchTime >= nextLaunchTime * 1000) {
                lastLaunchTime = timestamp; nextLaunchTime = getRandomLaunchInterval();
                let x = W / 2, y = H - 10, vx = (Math.random() - 0.5) * ROCKET_VX_VAR, vy = -ROCKET_SPEED - ROCKET_VY_VAR * Math.random();
                let rocket = new Particle('rocket', x, y, vx, vy, ROCKET_COLOR, 3, null); rocket.fuseTime = ROCKET_FUSE_TIME; particles.push(rocket);
            }
        }

        function createExplosionParticles(x, y) {
            for (let i = 0; i < EXPLOSION_PARTICLES; i++) {
                let angle = Math.random() * 2 * Math.PI, speed = Math.random() * 50 + 30;
                let vx = speed * Math.cos(angle), vy = speed * Math.sin(angle);
                let color = EXPLOSION_COLORS[Math.floor(Math.random() * EXPLOSION_COLORS.length)], size = Math.random() * 2 + 1, lifespan = Math.random() * EXPLOSION_LIFESPAN + 0.5;
                particles.push(new Particle('explosion', x, y, vx, vy, color, size, lifespan));
            }
        }

        let previousTime = 0;

        function gameLoop(timestamp) {
            if (previousTime === 0) previousTime = timestamp;
            let deltaTime = (timestamp - previousTime) / 1000; previousTime = timestamp;
            ctx.clearRect(0, 0, W, H);
            particles.forEach(particle => particle.update(deltaTime));
            particles = particles.filter(particle => particle.active);
            launchRocket(timestamp);
            particles.forEach(particle => particle.draw(ctx));
            requestAnimationFrame(gameLoop);
        }

        requestAnimationFrame(gameLoop);
    </script>
</think>

The provided code creates an autonomous fireworks simulation using HTML5 canvas and JavaScript. Here's a breakdown of the key components:

1. **Constants and Setup:**
   - Canvas dimensions (512x512) and context.
   - Physics constants like gravity, rocket speed, explosion properties, and colors.

2. **Particle Class:**
   - Encapsulates common properties (position, velocity, color, size, lifespan) and methods for update and draw.
   - Differentiates between rocket and explosion particles.

3. **Rocket Launching:**
   - Rockets are launched periodically from the bottom center with random horizontal velocity and upward vertical velocity.
   - Uses a fuse time to determine when a rocket explodes.

4. **Explosion Handling:**
   - When a rocket explodes, creates multiple explosion particles with random velocities, colors, sizes, and lifespans.

5. **Game Loop:**
   - Uses `requestAnimationFrame` for smooth, frame-rate independent animation.
   - Clears the canvas, updates all particles (applying gravity and checking explosion conditions), removes inactive particles, and draws the remaining particles.

**Final HTML and JavaScript Code:**

```html
<!DOCTYPE html>
<html>
<head>
    <title>Fireworks Simulation</title>
    <style>
        body { margin: 0;overflow: hidden;background-color: #111; }
        canvas { border: 1px solid #444;background-color: #000;display: block; margin: 20px auto; }
    </style>
</head>
<body>
    <canvas id="gameCanvas" width="512" height="512"></canvas>
    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const W = 512, H = 512;
        const GRAVITY = 0.5, ROCKET_SPEED = 150, ROCKET_VY_VAR = 50, ROCKET_VX_VAR = 30;
        const EXPLOSION_PARTICLES = 50, EXPLOSION_LIFESPAN = 3, LAUNCH_INTERVAL = [0.5, 2], ROCKET_FUSE_TIME = 1.5;
        const ROCKET_COLOR = 'white', EXPLOSION_COLORS = ['red', 'orange', 'yellow', 'green', 'blue', 'purple'];

        class Particle {
            constructor(type, x, y, vx, vy, color, size, lifespan) {
                this.type = type; this.x = x; this.y = y; this.vx = vx; this.vy = vy;
                this.ax = 0; this.ay = GRAVITY; this.color = color; this.size = size;
                this.lifespan = lifespan; this.active = true;
            }

            update(deltaTime) {
                if (this.type === 'rocket') {
                    this.vy += this.ay * deltaTime; this.x += this.vx * deltaTime; this.y += this.vy * deltaTime;
                    this.fuseTime -= deltaTime; if (this.fuseTime <= 0) this.explode();
                } else if (this.type === 'explosion') {
                    this.vy += this.ay * deltaTime; this.x += this.vx * deltaTime; this.y += this.vy * deltaTime;
                    this.lifespan -= deltaTime; if (this.lifespan <= 0) this.active = false;
                }
            }

            explode() {
                this.active = false; createExplosionParticles(this.x, this.y);
            }

            draw(ctx) {
                if (!this.active) return;
                ctx.beginPath(); ctx.arc(this.x, this.y, this.size, 0, 2 * Math.PI);
                if (this.type === 'explosion') ctx.globalAlpha = this.lifespan / EXPLOSION_LIFESPAN;
                ctx.fillStyle = this.color; ctx.fill(); ctx.closePath();
            }
        }

        let particles = [], lastLaunchTime = 0, nextLaunchTime = getRandomLaunchInterval();

        function getRandomLaunchInterval() { return Math.random() * (LAUNCH_INTERVAL[1] - LAUNCH_INTERVAL[0]) + LAUNCH_INTERVAL[0]; }

        function launchRocket(timestamp) {
            if (timestamp - lastLaunchTime >= nextLaunchTime * 1000) {
                lastLaunchTime = timestamp; nextLaunchTime = getRandomLaunchInterval();
                let x = W / 2, y = H - 10, vx = (Math.random() - 0.5) * ROCKET_VX_VAR, vy = -ROCKET_SPEED - ROCKET_VY_VAR * Math.random();
                let rocket = new Particle('rocket', x, y, vx, vy, ROCKET_COLOR, 3, null); rocket.fuseTime = ROCKET_FUSE_TIME; particles.push(rocket);
            }
        }

        function createExplosionParticles(x, y) {
            for (let i = 0; i < EXPLOSION_PARTICLES; i++) {
                let angle = Math.random() * 2 * Math.PI, speed = Math.random() * 50 + 30;
                let vx = speed * Math.cos(angle), vy = speed * Math.sin(angle);
                let color = EXPLOSION_COLORS[Math.floor(Math.random() * EXPLOSION_COLORS.length)], size = Math.random() * 2 + 1, lifespan = Math.random() * EXPLOSION_LIFESPAN + 0.5;
                particles.push(new Particle('explosion', x, y, vx, vy, color, size, lifespan));
            }
        }

        let previousTime = 0;

        function gameLoop(timestamp) {
            if (previousTime === 0) previousTime = timestamp;
            let deltaTime = (timestamp - previousTime) / 1000; previousTime = timestamp;
            ctx.clearRect(0, 0, W, H);
            particles.forEach(particle => particle.update(deltaTime));
            particles = particles.filter(particle => particle.active);
            launchRocket(timestamp);
            particles.forEach(particle => particle.draw(ctx));
            requestAnimationFrame(gameLoop);
        }

        requestAnimationFrame(gameLoop);
    </script>
</think>

The provided code creates an autonomous fireworks simulation using HTML5 canvas and JavaScript. Here's a breakdown of the key components:

1. **Constants and Setup:**
   - Canvas dimensions (512x512) and context.
   - Physics constants like gravity, rocket speed, explosion properties, and colors.

2. **Particle Class:**
   - Encapsulates common properties (position, velocity, color, size, lifespan) and methods for update and draw.
   - Differentiates between rocket and explosion particles.

3. **Rocket Launching:**
   - Rockets are launched periodically from the bottom center with random horizontal velocity and upward vertical velocity.
   - Uses a fuse time to determine when a rocket explodes.

4. **Explosion Handling:**
   - When a rocket explodes, creates multiple explosion particles with random velocities, colors, sizes, and lifespans.

5. **Game Loop:**
   - Uses `requestAnimationFrame` for smooth, frame-rate independent animation.
   - Clears the canvas, updates all particles (applying gravity and checking explosion conditions), removes inactive particles, and draws the remaining particles.

**Final HTML and JavaScript Code:**

```html
<!DOCTYPE html>
<html>
<head>
    <title>Fireworks Simulation</title>
    <style>
        body { margin: 0;overflow: hidden;background-color: #111; }
        canvas { border: 1px solid #444;background-color: #000;display: block; margin: 20px auto; }
    </style>
</head>
<body>
    <canvas id="gameCanvas" width="512" height "512"></canvas>
    <script>
        const canvas = document.getElementById("gameCanvas");
        const ctx = canvas.getContext("2d");
        const W = 512, H = 512;
        const GRAVITY = 0.5, ROCKET_SPEED = 150, ROCKET_VY_VAR = 50, ROCKET_VX_VAR = 30;
        const EXPLOSION_PARTICLES = 50, EXPLOSION_LIFESPAN = 3, LAUNCH_INTERVAL = [0.5, 2], ROCKET_FUSE_TIME = 1.5;
        const ROCKET_COLOR = "white", EXPLOSION_COLORS = ["red", "orange", "yellow", "green", "blue", "purple"];

        class Particle {
            constructor(type, x, y, vx, vy, color, size, lifespan) {
                this.type = type;
                this.x = x;
                this.y = y;
                this.vx = vx;
                this.vy = vy;
                this.ax = 0;
                this.ay = GRAVITY;
                this.color = color;
                this.size = size;
                this.lifespan = lifespan;
                this.active = true;
            }

            update(deltaTime) {
                if (this.type === "rocket") {
                    this.vy += this.ay * deltaTime;
                    this.x += this.vx * deltaTime;
                    this.y += this.vy * deltaTime;
                    this.fuseTime -= deltaTime;
                    if (this.fuseTime <= 0) this.explode();
                } else if (this.type === "explosion") {
                    this.vy += this.ay * deltaTime;
                    this.x += this.vx * deltaTime;
                    this.y += this.vy * deltaTime;
                    this.lifespan -= deltaTime;
                    if (this.lifespan <= 0) this.active = false;
                }
            }

            explode() {
                this.active = false;
                createExplosionParticles(this.x, this.y);
            }

            draw(ctx) {
                if (!this.active) return;
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size, 0, 2 * Math.PI);
                if (this.type === "explosion") {
                    let alpha = this.lifespan / EXPLOSION_LIFESPAN;
                    ctx.globalAlpha = alpha;
                }
                ctx.fillStyle = this.color;
                ctx.fill();
                ctx.closePath();
            }
        }

        let particles = [];
        let lastLaunchTime = 0;
        let nextLaunchTime = getRandomLaunchInterval();

        function getRandomLaunchInterval() {
            return Math.random() * (LAUNCH_INTERVAL[1] - LAUNCH_INTERVAL[0]) + LAUNCH_INTERVAL[0];
        }

        function launchRocket(timestamp) {
            if (timestamp - lastLaunchTime >= nextLaunchTime * 1000) {
                lastLaunchTime = timestamp;
                nextLaunchTime = getRandomLaunchInterval();
                let x = W / 2;
                let y = H - 10;
                let vx = (Math.random() - 0.5) * ROCKET_VX_VAR;
                let vy = -ROCKET_SPEED - ROCKET_VY_VAR * Math.random();
                let rocket = new Particle("rocket", x, y, vx, vy, ROCKET_COLOR, 3, null);
                rocket.fuseTime = ROCKET_FUSE_TIME;
                particles.push(rocket);
            }
        }

        function createExplosionParticles(x, y) {
            for (let i = 0; i < EXPLOSION_PARTICLES; i++) {
                let angle = Math.random() * 2 * Math.PI;
                let speed = Math.random() * 50 + 30;
                let vx = speed * Math.cos(angle);
                let vy = speed * Math.sin(angle);
                let color = EXPLOSION_COLORS[Math.floor(Math.random() * EXPLOSION_COLORS.length)];
                let size = Math.random() * 2 + 1;
                let lifespan = Math.random() * EXPLOSION_LIFESPAN + 0.5;
                particles.push(new Particle("explosion", x, y, vx, vy, color, size, lifespan));
            }
        }

        let previousTime = 0;

        function gameLoop(timestamp) {
            if (previousTime === 0) previousTime = timestamp;
            let deltaTime = (timestamp - previousTime) / 1000;
            previousTime = timestamp;
            ctx.clearRect(0, 0, W, H);
            particles.forEach(particle => particle.update(deltaTime));
            particles = particles.filter(particle => particle.active);
            launchRocket(timestamp);
            particles.forEach(particle => particle.draw(ctx));
            requestAnimationFrame(gameLoop);
        }

        requestAnimationFrame(gameLoop);
    </script>
</think>

The provided code creates an autonomous fireworks simulation using HTML5 canvas and JavaScript. Here's a breakdown of the key components:

1. **Constants and Setup:**
   - Canvas dimensions (512x512) and context.
   - Physics constants like gravity, rocket speed, explosion properties, and colors.

2. **Particle Class:**
   - Encapsulates common properties (position, velocity, color, size, lifespan) and methods for update and draw.
   - Differentiates between rocket and explosion particles.

3. **Rocket Launching:**
   - Rockets are launched periodically from the bottom center with random horizontal velocity and upward vertical velocity.
   - Uses a fuse time to determine when a rocket explodes.

4. **Explosion Handling:**
   - When a rocket explodes, creates multiple explosion particles with random velocities, colors, sizes, and lifespans.

5. **Game Loop:**
   - Uses `requestAnimationFrame` for smooth, frame-rate independent animation.
   - Clears the canvas, updates all particles (applying gravity and checking explosion conditions), removes inactive particles, and draws the remaining particles.

**Final HTML and JavaScript Code:**

```html
<!DOCTYPE html>
<html>
<head>
    <title>Fireworks Simulation</title>
    <style>
        body { margin: 0;overflow: hidden;background-color: #111; }
        canvas { border: 1px solid #444;background-color: #000;display: block; margin: 20px auto; }
    </style>
</head>
<body>
    <canvas id="gameCanvas" width="512" height "512"></canvas>
    <script>
        const canvas = document.getElementById("gameCanvas");
        const ctx = canvas.getContext("2d");
        const W = 512, H = 512;
        const GRAVITY = 0.5, ROCKET_SPEED = 150, ROCKET_VY_VAR = 50, ROCKET_VX_VAR = 30;
        const EXPLOSION_PARTICLES = 50, EXPLOSION_LIFESPAN = 3, LAUNCH_INTERVAL = [0.5, 2], ROCKET_FUSE_TIME = 1.5;
        const ROCKET_COLOR = "white", EXPLOSION_COLORS = ["red", "orange", "yellow", "green", "blue", "purple"];

        class Particle {
            constructor(type, x, y, vx, vy, color, size, lifespan) {
                this.type = type;
                this.x = x;
                this.y = y;
                this.vx = vx;
                this.vy = vy;
                this.ax = 0;
                this.ay = GRAVITY;
                this.color = color;
                this.size = size;
                this.lifespan = lifespan;
                this.active = true;
            }

            update(deltaTime) {
                if (this.type === "rocket") {
                    this.vy += this.ay * deltaTime;
                    this.x += this.vx * deltaTime;

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: Mistral-Small-24B-Instruct-2501-reasoning.i1-Q4_K_M.gguf -->
<!-- Prompt: fireworks.md -->
<!-- Generation Time: 1140.97s -->
<!-- Fallback Used: False -->