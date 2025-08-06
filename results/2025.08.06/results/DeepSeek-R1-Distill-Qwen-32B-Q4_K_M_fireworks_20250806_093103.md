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
        const W = canvas.width;
        const H = canvas.height;
        const GRAVITY = 200; // pixels per second²

        /* ---------- Utility functions ---------- */
        const rand = (min, max) => Math.random() * (max - min) + min;
        const randInt = (min, max) => Math.floor(rand(min, max + 1));

        /* ---------- Particle base class (optional) ---------- */
        class Particle {
            constructor(x, y, vx, vy, color, size, life) {
                this.x = x;
                this.y = y;
                this.vx = vx;
                this.vy = vy;
                this.color = color;
                this.size = size;
                this.life = life; // seconds
                this.age = 0;
            }
            update(dt) {
                this.vy += GRAVITY * dt;
                this.x += this.vx * dt;
                this.y += this.vy * dt;
                this.age += dt;
            }
            isDead() {
                return this.age >= this.life;
            }
            draw(ctx) {
                const alpha = Math.max(0, 1 - this.age / this.life);
                ctx.globalAlpha = alpha;
                ctx.fillStyle = this.color;
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                ctx.fill();
                ctx.globalAlpha = 1;
            }
        }

        /* ---------- Rocket class ---------- */
        class Rocket extends Particle {
            constructor() {
                const x = W / 2 + rand(-30, 30);
                const y = H - 10;
                const vx = rand(-20, 20);
                const vy = rand(-400, -300); // upward
                const color = `hsl(${randInt(0, 360)}, 100%, 70%)`;
                const size = 3;
                const life = 5; // never really used
                super(x, y, vx, vy, color, size, life);
                this.fuse = rand(1.0, 2.0); // seconds before explosion
                this.exploded = false;
            }
            update(dt) {
                super.update(dt);
                if (!this.exploded && (this.age >= this.fuse || this.vy > 0)) {
                    this.explode();
                }
            }
            explode() {
                this.exploded = true;
                const count = randInt(30, 80);
                for (let i = 0; i < count; i++) {
                    const angle = rand(0, Math.PI * 2);
                    const speed = rand(50, 200);
                    const vx = Math.cos(angle) * speed;
                    const vy = Math.sin(angle) * speed;
                    const life = rand(1.0, 3.0);
                    const size = rand(2, 4);
                    const color = this.color; // same hue as rocket
                    particles.push(new ExplosionParticle(
                        this.x, this.y, vx, vy, color, size, life
                    ));
                }
            }
            draw(ctx) {
                // Rockets are drawn as bright streaks
                ctx.globalAlpha = 1;
                ctx.fillStyle = this.color;
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                ctx.fill();
            }
        }

        /* ---------- Explosion particle class ---------- */
        class ExplosionParticle extends Particle {
            constructor(x, y, vx, vy, color, size, life) {
                super(x, y, vx, vy, color, size, life);
            }
        }

        /* ---------- Main simulation state ---------- */
        const particles = []; // holds both rockets and explosion fragments
        let lastTimestamp = 0;
        let nextLaunch = 0; // timestamp of next rocket launch

        /* ---------- Launch a new rocket ---------- */
        function launchRocket() {
            particles.push(new Rocket());
            // schedule next launch
            nextLaunch = performance.now() + rand(500, 2000);
        }

        /* ---------- Game loop ---------- */
        function gameLoop(timestamp) {
            if (!lastTimestamp) lastTimestamp = timestamp;
            const dt = (timestamp - lastTimestamp) / 1000; // seconds
            lastTimestamp = timestamp;

            // Autonomous launching
            if (timestamp >= nextLaunch) launchRocket();

            // Update particles
            for (let i = particles.length - 1; i >= 0; i--) {
                const p = particles[i];
                p.update(dt);
                if (p.isDead() || (p instanceof Rocket && p.exploded)) {
                    particles.splice(i, 1); // remove dead or exploded rocket
                }
            }

            // Render
            ctx.clearRect(0, 0, W, H);
            for (const p of particles) {
                p.draw(ctx);
            }

            requestAnimationFrame(gameLoop);
        }

        // Start the simulation
        requestAnimationFrame(gameLoop);
    </script>
    <section id="notes">
        <h2>Notes &amp; How It Works</h2>
        <ul>
            <li>All particles (rockets and sparks) are stored in a single array for simplicity.</li>
            <li>Delta‑time (dt) is calculated each frame to keep motion frame‑rate independent.</li>
            <li>Rockets have a random fuse time; when the fuse expires or the rocket starts falling, it explodes.</li>
            <li>Explosion particles inherit the rocket’s hue but have random velocities and lifespans.</li>
            <li>Particles are removed from the array when they exceed their lifespan or rockets explode.</li>
            <li>Gravity is applied uniformly to all particles.</li>
            <li>Canvas is cleared each frame; rockets are drawn as bright circles, sparks fade out.</li>
            <li>The simulation automatically launches new rockets at random intervals (0.5–2 s).</li>
        </ul>
    </section>
</body>
</html>
```

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: DeepSeek-R1-Distill-Qwen-32B-Q4_K_M.gguf -->
<!-- Prompt: fireworks.md -->
<!-- Generation Time: 16.78s -->
<!-- Fallback Used: False -->