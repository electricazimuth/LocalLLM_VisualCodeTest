<|channel|>analysis<|message|>We need to provide final answer: a single HTML file with script. We need to create fireworks simulation following requirements.

We need to implement:

- Particle management: single array for all particles.
- Autonomous launching: periodic launching at random intervals between 0.5-2 sec.
- Rocket: has position, velocity, gravity, fuse/time or altitude threshold. On explosion, create explosion particles.
- Explosion particles: random velocities, gravity, lifespan, color, size, fade.

- Use requestAnimationFrame loop with delta time.

- Remove particles when done.

- Use efficient array removal: filter or loop from end.

- Use object/class structure: maybe classes Rocket, ExplosionParticle, or Particle with type property.

- Use randomization, color.

- Use canvas width/height.

- Optimize: keep array size manageable.

- Provide final code inside script tags.

We also need to add notes in section#notes.

Let's design.

Plan:

- Have a global array "particles".

- Each particle has properties:

    - type: 'rocket' or 'spark'.

    - x, y, vx, vy.

    - life: for spark: remaining life.

    - size: for spark: radius.

    - color: for spark: maybe string or rgba.

    - alpha: for spark: fade.

- For rocket: we can store fuseTime or targetHeight: maybe fuseTime: random between 1-2 sec. Or we can use targetHeight: random between 0.3-0.6 H.

- When rocket reaches y <= targetHeight or time since launch >= fuseTime, triggers explosion.

- Each rocket has property "createdAt" timestamp.

- For explosion, we create 30-80 sparks with random velocities: magnitude maybe 0-200 px/s.

- Each spark has lifespan: 1-3 sec.

- Each spark color: random or derived from rocket color.

- In update loop:

    - compute dt = (timestamp - lastTimestamp)/1000 (seconds).

    - For each particle:

        - Update position: x += vx * dt; y += vy * dt.

        - Update vy: vy += GRAVITY * dt.

        - For rocket: check explosion condition: if y <= targetHeight or age >= fuseTime: explode.

            - Remove rocket: maybe mark for removal.

            - Add explosion particles.

        - For spark: age += dt; if age >= life: remove.

- For removal: iterate from end to start and splice.

- For drawing:

    - Clear canvas: maybe use clearRect.

    - For each particle:

        - if rocket: draw small rectangle or line: maybe use ctx.fillStyle = "#FFF" or color.

        - if spark: set ctx.globalAlpha = 1 - age / life; set fillStyle = color; draw circle.

- We'll also add some trailing effect: maybe fade background? But not required.

- We'll also implement random launching: maintain variable nextLaunchTime; when timestamp >= nextLaunchTime, launch a rocket: create rocket object with initial position: random x near center: maybe within width/5? Actually bottom center area: x between W/2 - 30 to W/2 + 30. y = H.

- Launch interval: random between 0.5-2 sec.

- For rocket's initial velocity: vy negative: random between -200 to -300 px/s. vx: random -30 to 30.

- For rocket's fuseTime: random 1-2 sec or targetHeight: random 0.3*H to 0.6*H.

- For rocket's color: maybe random color; explosion color same.

- Use global constants: gravity = 200 px/s^2.

- Use time in seconds.

- Provide code inside script.

- Provide notes: maybe include explanation.

Let's craft code.

Edge Cases:

- deltaTime may be large on first frame: we can set lastTimestamp = timestamp initially.

- Provide random function: random(min, max) returns float.

- For color: we can use HSL: random hue 0-360, saturation 70-100, lightness 50-70.

- For spark color: same hue as rocket but maybe random brightness.

- For rocket color: maybe bright white or random color.

- For spark color: maybe color = `hsl(hue, 100%, 50%)`.

- For rocket: maybe use same color as spark.

- For spark size: random 2-4 px.

- For explosion particles: number: random 30-80.

- For spark velocities: speed random 0-400 px/s; direction random 0-360.

- For rocket's initial velocity: vy random -250 to -400 px/s; vx random -50 to 50.

- For rocket's fuse: maybe random 1-2 sec.

- For rocket's targetHeight: random 0.3-0.6 H; choose whichever earlier? We can use both: if time > fuseTime OR y <= targetHeight: explode.

- For rocket's age: track.

- Use "age" for rocket as well.

- For each particle, we can store "age" property for rockets as well.

Simplify: Use class Particle with subclass Rocket and Spark? Could just use simple object.

We need to maintain array "particles".

Implementation Steps:

- Create function random(min, max) returns value.

- Create function launchRocket(currentTime):

    - x = random(W/2 - 30, W/2 + 30)

    - y = H

    - vx = random(-50, 50)

    - vy = random(-400, -250)

    - hue = random(0, 360)

    - color = `hsl(${hue}, 100%, 50%)`

    - fuseTime = random(1, 2)  // seconds

    - targetHeight = random(0.3 * H, 0.6 * H)

    - rocket = { type: 'rocket', x, y, vx, vy, hue, color, fuseTime, targetHeight, age: 0 }

    - particles.push(rocket)

- Create function createExplosion(rocket, currentTime):

    - number = randomInt(30, 80)

    - For i in 0..number-1:

        - angle = random(0, 2π)

        - speed = random(50, 300) // px/s

        - vx = Math.cos(angle) * speed

        - vy = Math.sin(angle) * speed

        - life = random(1, 3)

        - size = random(2, 4)

        - color = `hsl(${rocket.hue}, 100%, ${random(50, 70)}%)` or maybe use same hue.

        - spark = { type: 'spark', x: rocket.x, y: rocket.y, vx, vy, life, age: 0, size, color }

        - particles.push(spark)

- In gameLoop:

    - dt = (timestamp - lastTimestamp)/1000

    - lastTimestamp = timestamp

    - // Launch new rocket if time >= nextLaunchTime

    - if timestamp >= nextLaunchTime: launchRocket(timestamp); nextLaunchTime = timestamp + random(0.5, 2)

    - // Update particles

    - for (let i = particles.length - 1; i >= 0; i--) { let p = particles[i]; if (p.type === 'rocket') { p.age += dt; p.vy += GRAVITY * dt; p.x += p.vx * dt; p.y += p.vy * dt; if (p.age >= p.fuseTime || p.y <= p.targetHeight) { createExplosion(p, timestamp); particles.splice(i, 1); } } else if (p.type === 'spark') { p.age += dt; p.vy += GRAVITY * dt; p.x += p.vx * dt; p.y += p.vy * dt; if (p.age >= p.life) { particles.splice(i, 1); } } }

    - // Draw

    - ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H);

    - for each particle: if rocket: ctx.fillStyle = p.color; ctx.fillRect(p.x, p.y, 2, 2); if spark: ctx.globalAlpha = 1 - p.age / p.life; ctx.fillStyle = p.color; ctx.beginPath(); ctx.arc(p.x, p.y, p.size, 0, Math.PI*2); ctx.fill(); ctx.globalAlpha = 1; // reset.

- Start loop: requestAnimationFrame(gameLoop).

- Add notes: maybe mention explanation.

- Ensure using requestAnimationFrame properly.

- Use performance: ensure not using heavy operations each frame. But fine.

- Provide final code inside script tags.

Let's craft final HTML file.

But the user said: "A single HTML file with the code added, use the following boilerplate html." So we must insert code into the script tag.

Also we need to add notes in section#notes.

Let's produce final answer: the entire HTML code.

Let's craft final output: Provide the entire HTML file with script inserted.

Also we might add some comments.

Let's produce final answer.<|start|>assistant<|channel|>final<|message|>```html
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
        const W = canvas.width;
        const H = canvas.height;

        /* ---------- Config & Helpers ---------- */
        const GRAVITY = 200;               // px/s²
        const LAUNCH_INTERVAL_MIN = 0.5;   // seconds
        const LAUNCH_INTERVAL_MAX = 2.0;   // seconds
        const ROCKET_SPEED_Y_MIN = -400;   // px/s
        const ROCKET_SPEED_Y_MAX = -250;   // px/s
        const ROCKET_SPEED_X_MIN = -50;    // px/s
        const ROCKET_SPEED_X_MAX = 50;     // px/s
        const ROCKET_FUSE_MIN = 1.0;       // seconds
        const ROCKET_FUSE_MAX = 2.0;       // seconds
        const ROCKET_TARGET_MIN = 0.3;     // fraction of height
        const ROCKET_TARGET_MAX = 0.6;     // fraction of height
        const EXPLOSION_PARTICLES_MIN = 30;
        const EXPLOSION_PARTICLES_MAX = 80;
        const EXPLOSION_SPEED_MIN = 50;    // px/s
        const EXPLOSION_SPEED_MAX = 300;   // px/s
        const EXPLOSION_LIFE_MIN = 1.0;    // seconds
        const EXPLOSION_LIFE_MAX = 3.0;    // seconds
        const EXPLOSION_SIZE_MIN = 2;      // px
        const EXPLOSION_SIZE_MAX = 4;      // px

        function rand(min, max) { return Math.random() * (max - min) + min; }
        function randInt(min, max) { return Math.floor(rand(min, max)); }

        /* ---------- Particle Array ---------- */
        const particles = [];   // holds both rockets and sparks

        /* ---------- Launch Timing ---------- */
        let nextLaunch = performance.now() + rand(LAUNCH_INTERVAL_MIN, LAUNCH_INTERVAL_MAX) * 1000;

        /* ---------- Rocket Launch ---------- */
        function launchRocket(now) {
            const x = rand(W / 2 - 30, W / 2 + 30);
            const y = H;
            const vx = rand(ROCKET_SPEED_X_MIN, ROCKET_SPEED_X_MAX);
            const vy = rand(ROCKET_SPEED_Y_MIN, ROCKET_SPEED_Y_MAX);
            const hue = randInt(0, 360);
            const color = `hsl(${hue}, 100%, 50%)`;
            const fuseTime = rand(ROCKET_FUSE_MIN, ROCKET_FUSE_MAX);
            const targetHeight = rand(ROCKET_TARGET_MIN, ROCKET_TARGET_MAX) * H;

            particles.push({
                type: 'rocket',
                x,
                y,
                vx,
                vy,
                hue,
                color,
                fuseTime,
                targetHeight,
                age: 0
            });
        }

        /* ---------- Explosion Creation ---------- */
        function createExplosion(rocket, now) {
            const num = randInt(EXPLOSION_PARTICLES_MIN, EXPLOSION_PARTICLES_MAX);
            for (let i = 0; i < num; i++) {
                const angle = rand(0, Math.PI * 2);
                const speed = rand(EXPLOSION_SPEED_MIN, EXPLOSION_SPEED_MAX);
                const vx = Math.cos(angle) * speed;
                const vy = Math.sin(angle) * speed;
                const life = rand(EXPLOSION_LIFE_MIN, EXPLOSION_LIFE_MAX);
                const size = rand(EXPLOSION_SIZE_MIN, EXPLOSION_SIZE_MAX);
                const light = rand(50, 70);
                const color = `hsl(${rocket.hue}, 100%, ${light}%)`;

                particles.push({
                    type: 'spark',
                    x: rocket.x,
                    y: rocket.y,
                    vx,
                    vy,
                    life,
                    age: 0,
                    size,
                    color
                });
            }
        }

        /* ---------- Game Loop ---------- */
        let lastTimestamp = performance.now();

        function gameLoop(timestamp) {
            const dt = (timestamp - lastTimestamp) / 1000; // seconds
            lastTimestamp = timestamp;

            /* ---- Launch new rockets ---- */
            if (timestamp >= nextLaunch) {
                launchRocket(timestamp);
                nextLaunch = timestamp + rand(LAUNCH_INTERVAL_MIN, LAUNCH_INTERVAL_MAX) * 1000;
            }

            /* ---- Update particles ---- */
            for (let i = particles.length - 1; i >= 0; i--) {
                const p = particles[i];

                // Apply physics
                p.vy += GRAVITY * dt;
                p.x += p.vx * dt;
                p.y += p.vy * dt;
                p.age += dt;

                if (p.type === 'rocket') {
                    // Check for explosion
                    if (p.age >= p.fuseTime || p.y <= p.targetHeight) {
                        createExplosion(p, timestamp);
                        particles.splice(i, 1); // remove rocket
                    }
                } else if (p.type === 'spark') {
                    // Remove expired sparks
                    if (p.age >= p.life) {
                        particles.splice(i, 1);
                    }
                }
            }

            /* ---- Render ---- */
            ctx.fillStyle = '#000';
            ctx.fillRect(0, 0, W, H);

            for (const p of particles) {
                if (p.type === 'rocket') {
                    ctx.fillStyle = p.color;
                    ctx.fillRect(p.x, p.y, 2, 2);
                } else if (p.type === 'spark') {
                    const alpha = 1 - p.age / p.life;
                    ctx.globalAlpha = alpha;
                    ctx.fillStyle = p.color;
                    ctx.beginPath();
                    ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.globalAlpha = 1; // reset
                }
            }

            requestAnimationFrame(gameLoop);
        }

        requestAnimationFrame(gameLoop);
    </script>
    <section id="notes">
        <h2>How It Works</h2>
        <p>
            The simulation keeps a single array <code>particles</code> containing both
            launching rockets and explosion fragments (sparks). Each frame we:
        </p>
        <ul>
            <li>Calculate the delta‑time for frame‑rate independence.</li>
            <li>Launch new rockets at random intervals.</li>
            <li>Update every particle’s position, velocity (gravity), and age.</li>
            <li>Detect when a rocket should explode and replace it with a burst of sparks.</li>
            <li>Remove particles that have exceeded their lifespan.</li>
            <li>Render all remaining particles with simple shapes and fading.</li>
        </ul>
        <p>
            The use of <code>requestAnimationFrame</code> ensures smooth animations,
            and iterating from the end of the array when removing items keeps the
            performance high even with hundreds of particles.
        </p>
    </section>
</body>
</html>
```

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: gpt-oss-20b-mxfp4.gguf -->
<!-- Prompt: fireworks.md -->
<!-- Generation Time: 23.91s -->
<!-- Fallback Used: False -->