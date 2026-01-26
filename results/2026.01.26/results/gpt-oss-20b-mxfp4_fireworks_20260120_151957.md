```html
<!DOCTYPE html>
<html>
<head>
    <title>Fireworks Simulation</title>
    <style>
        body { margin: 0; overflow: hidden; background-color: #111; } /* Dark background suggested */
        canvas { border: 1px solid #444; background-color: #000; display: block; margin: 20px auto; } /* Dark canvas bg */
    </style>
</head>
<body>
    <canvas id="gameCanvas" width="512" height="512"></canvas>
    <script>
        /* ------------------------------------------------------------------
           Fireworks Simulation – Core
           ------------------------------------------------------------------ */
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const W = canvas.width;
        const H = canvas.height;

        // Gravity (pixels per second²)
        const GRAVITY = 200;

        // All active particles (rockets + explosion fragments)
        const particles = [];

        /* ------------------------------------------------------------------
           Utility
           ------------------------------------------------------------------ */
        function randomRange(min, max) {
            return Math.random() * (max - min) + min;
        }

        /* ------------------------------------------------------------------
           Rocket – the launching projectile
           ------------------------------------------------------------------ */
        class Rocket {
            constructor() {
                // Start near the bottom‑center of the canvas
                this.x = W / 2 + randomRange(-30, 30);
                this.y = H;
                // Slight horizontal jitter, strong upward velocity
                this.vx = randomRange(-30, 30);
                this.vy = randomRange(-350, -300);
                // Random bright hue
                this.color = `hsl(${Math.floor(randomRange(0, 360))},100%,70%)`;
                this.radius = 3;
                this.age = 0;                     // seconds since launch
                this.fuse = randomRange(1, 2);    // explode after 1–2 s
                this.type = 'rocket';
            }

            update(dt) {
                this.age += dt;
                this.vy += GRAVITY * dt;          // gravity pulls it down
                this.x += this.vx * dt;
                this.y += this.vy * dt;

                // If it somehow falls below the bottom, kill it
                if (this.y > H + 100) return false;
                // Still alive until fuse time expires
                return this.age < this.fuse;
            }

            draw(ctx) {
                ctx.fillStyle = this.color;
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
                ctx.fill();
            }
        }

        /* ------------------------------------------------------------------
           ExplosionParticle – the sparks that fall after an explosion
           ------------------------------------------------------------------ */
        class ExplosionParticle {
            constructor(x, y, baseColor) {
                const angle = randomRange(0, Math.PI * 2);
                const speed = randomRange(50, 200);
                this.vx = Math.cos(angle) * speed;
                this.vy = Math.sin(angle) * speed;

                this.x = x;
                this.y = y;
                this.color = baseColor;
                this.radius = randomRange(2, 4);
                this.life = randomRange(1, 3);   // seconds
                this.alpha = 1;
                this.type = 'explosion';
            }

            update(dt) {
                this.life -= dt;
                if (this.life <= 0) return false;

                this.vy += GRAVITY * dt;
                this.x += this.vx * dt;
                this.y += this.vy * dt;
                this.alpha = Math.max(0, this.life / 3);   // fade out
                return true;
            }

            draw(ctx) {
                ctx.globalAlpha = this.alpha;
                ctx.fillStyle = this.color;
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
                ctx.fill();
                ctx.globalAlpha = 1;
            }
        }

        /* ------------------------------------------------------------------
           Launching & Explosion logic
           ------------------------------------------------------------------ */
        function launchRocket() {
            particles.push(new Rocket());
        }

        function explode(rocket) {
            const count = Math.floor(randomRange(30, 80));
            for (let i = 0; i < count; i++) {
                particles.push(new ExplosionParticle(rocket.x, rocket.y, rocket.color));
            }
        }

        /* ------------------------------------------------------------------
           Game Loop
           ------------------------------------------------------------------ */
        let lastTimestamp = 0;
        let nextLaunchTime = 0;     // ms

        function gameLoop(timestamp) {
            if (!lastTimestamp) lastTimestamp = timestamp;
            const dt = (timestamp - lastTimestamp) / 1000;   // seconds
            lastTimestamp = timestamp;

            // Autonomous launch
            if (timestamp >= nextLaunchTime) {
                launchRocket();
                nextLaunchTime = timestamp + randomRange(500, 2000); // 0.5–2 s
            }

            // Update particles
            for (let i = particles.length - 1; i >= 0; i--) {
                const p = particles[i];
                if (p.type === 'rocket') {
                    const alive = p.update(dt);
                    if (!alive) {
                        explode(p);
                        particles.splice(i, 1);   // remove rocket
                    }
                } else if (p.type === 'explosion') {
                    const alive = p.update(dt);
                    if (!alive) particles.splice(i, 1);
                }
            }

            // Draw
            ctx.fillStyle = '#000';
            ctx.fillRect(0, 0, W, H);

            for (const p of particles) {
                p.draw(ctx);
            }

            requestAnimationFrame(gameLoop);
        }

        // Start the simulation
        nextLaunchTime = performance.now() + randomRange(0, 1000);
        requestAnimationFrame(gameLoop);

    </script>
    <section id="notes">
        <h3>Implementation notes</h3>
        <ul>
            <li>All active particles are stored in a single <code>particles</code> array – rockets and explosion fragments share the same container.</li>
            <li>Rockets are launched automatically from the bottom‑center at random intervals (0.5–2 s).</li>
            <li>Each rocket has a random fuse time (1–2 s). When the fuse expires, the rocket explodes and is removed from the array.</li>
            <li>Explosion particles are created with random velocities radiating from the explosion point. They are affected by gravity, have a limited lifespan, and fade out as they die.</li>
            <li>The main loop uses <code>requestAnimationFrame</code> and calculates <code>delta time</code> so the simulation runs at the same speed regardless of frame rate.</li>
            <li>Dead particles are removed from the array by iterating backwards and splicing, which keeps the array compact and efficient.</li>
            <li>Drawing is split into two phases: a dark background is cleared first, then each particle is drawn with its own color and transparency.</li>
            <li>All code is plain JavaScript and the Canvas API – no external libraries or physics engines are required.</li>
        </ul>
    </section>
</body>
</html>
```

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: gpt-oss-20b-mxfp4.gguf -->
<!-- Prompt: fireworks.md -->
<!-- Generation Time: 23.22s -->
<!-- Fallback Used: False -->