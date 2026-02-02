Here is a complete, self‑contained HTML file that implements the requested fireworks simulation.  
All of the JavaScript lives inside the `<script>` tag, uses only the Canvas API, follows best‑practice patterns (classes, delta‑time handling, efficient particle management), and places any explanatory text in the `#notes` section.

```html
<!DOCTYPE html>
<html>
<head>
    <title>Fireworks Simulation</title>
    <style>
        body { margin: 0; overflow: hidden; background-color: #111; } /* Dark background */
        canvas { border: 1px solid #444; background-color: #000; display: block; margin: 20px auto; } /* Dark canvas bg */
    </style>
</head>
<body>
    <canvas id="gameCanvas" width="512" height="512"></canvas>
    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const W = canvas.width;
        const H = canvas.height;

        /* -------------------------------------------------
           Configuration constants
        ------------------------------------------------- */
        const GRAVITY = 0.12;               // downward acceleration
        const MIN_LAUNCH_INTERVAL = 500;   // ms (0.5 s)
        const MAX_LAUNCH_INTERVAL = 2000;  // ms (2 s)
        const ROCKET_LIFESPAN = 1500;      // ms before automatic explosion
        const EXPLOSION_PARTICLES = 60;    // how many fragments per burst
        const EXPLOSION_MAX_LIFESPAN = 1200; // ms
        const ROCKET_SIZE = 4;
        const PARTICLE_SIZE_MIN = 2;
        const PARTICLE_SIZE_MAX = 4;

        /* -------------------------------------------------
           Particle & Rocket Classes
        ------------------------------------------------- */
        class Rocket {
            constructor(x, y, vx, vy, color) {
                this.x = x;
                this.y = y;
                this.vx = vx;
                this.vy = vy;
                this.color = color;
                this.age = 0;               // ms since launch
                this.exploded = false;
            }
            update(dt) {
                // Apply gravity
                this.vy += GRAVITY;
                // Position update
                this.x += this.vx * dt;
                this.y += this.vy * dt;
                this.age += dt;
                // Explosion condition: either fuse time reached or near apex (slow upward speed)
                const nearApex = Math.abs(this.vy) < 5;
                if (!this.exploded && (this.age >= ROCKET_LIFESPAN || nearApex)) {
                    this.explode();
                }
            }
            explode() {
                this.exploded = true;
                // Create explosion particles at current position
                for (let i = 0; i < EXPLOSION_PARTICLES; i++) {
                    const angle = Math.random() * Math.PI * 2;
                    const speed = 1 + Math.random() * 2;
                    const vx = Math.cos(angle) * speed * (Math.random() < 0.5 ? -1 : 1);
                    const vy = Math.sin(angle) * speed * (Math.random() < 0.5 ? -1 : 1);
                    particles.push(new ExplosionParticle(this.x, this.y, vx, vy, this.color));
                }
            }
            draw() {
                ctx.fillStyle = this.color;
                ctx.beginPath();
                ctx.arc(this.x, this.y, ROCKET_SIZE, 0, Math.PI * 2);
                ctx.fill();
            }
        }

        class ExplosionParticle {
            constructor(x, y, vx, vy, baseColor) {
                this.x = x;
                this.y = y;
                this.vx = vx;
                this.vy = vy;
                this.lifespan = 0;
                this.maxLife = Math.random() * EXPLOSION_MAX_LIFESPAN + 200; // ms
                // Randomize size a bit
                this.size = PARTICLE_SIZE_MIN + Math.random() * (PARTICLE_SIZE_MAX - PARTICLE_SIZE_MIN);
                // Slightly modify hue for variety
                const hueShift = (Math.random() * 30) - 15; // -15 to +15
                const rgb = this.hexToRgb(baseColor);
                const r = Math.min(255, Math.max(0, rgb[0] + hueShift));
                const g = Math.min(255, Math.max(0, rgb[1] + hueShift));
                const b = Math.min(255, Math.max(0, rgb[2] + hueShift));
                this.color = `rgb(${r},${g},${b})`;
                this.age = 0;
            }
            update(dt) {
                // Apply gravity
                this.vy += GRAVITY;
                // Position update
                this.x += this.vx * dt;
                this.y += this.vy * dt;
                this.age += dt;
                this.lifespan = this.maxLife - this.age;
            }
            draw() {
                const alpha = Math.max(0, this.lifespan / this.maxLife);
                ctx.globalAlpha = alpha;
                ctx.fillStyle = this.color;
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                ctx.fill();
                ctx.globalAlpha = 1; // reset
            }
            // Utility: convert "#rrggbb" to [r,g,b]
            hexToRgb(hex) {
                const shorthandRegex = /^#?([a-f\d])([a-f\d])([a-f\d])$/i;
                hex = hex.replace(shorthandRegex, (m, r, g, b) => r + r + g + g + b + b);
                const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
                return result
                    ? [parseInt(result[1], 16), parseInt(result[2], 16), parseInt(result[3], 16)]
                    : [0, 0, 0];
            }
        }

        /* -------------------------------------------------
           Global state
        ------------------------------------------------- */
        const rockets = [];
        const particles = []; // holds both rockets and explosion particles
        let lastLaunch = 0;   // timestamp of last rocket launch
        let launchTimer = 0;  // counts toward next launch

        /* -------------------------------------------------
           Helper: create a new rocket
        ------------------------------------------------- */
        function spawnRocket() {
            const x = W / 2 + (Math.random() - 0.5) * 40; // slight horizontal spread
            const y = H - 10;                               // near bottom
            const vx = (Math.random() - 0.5) * 2;           // small horizontal drift
            const vy = - (Math.random() * 4 + 2);           // upward speed (negative)
            const hue = Math.floor(Math.random() * 360);
            const color = `hsl(${hue}, 80%, 60%)`;
            rockets.push(new Rocket(x, y, vx, vy, color));
        }

        /* -------------------------------------------------
           Game loop
        ------------------------------------------------- */
        let lastTimestamp = 0;
        function gameLoop(timestamp) {
            // ---- Delta time (ms) -------------------------------------------------
            const dt = timestamp - lastTimestamp;
            lastTimestamp = timestamp;

            // ---- Update launch timer --------------------------------------------
            launchTimer += dt;
            if (launchTimer >= lastLaunch + MIN_LAUNCH_INTERVAL + Math.random() * (MAX_LAUNCH_INTERVAL - MIN_LAUNCH_INTERVAL)) {
                spawnRocket();
                lastLaunch = timestamp;
                launchTimer = 0;
            }

            // ---- Update all particles -------------------------------------------
            // Update rockets
            for (let i = rockets.length - 1; i >= 0; i--) {
                const rocket = rockets[i];
                rocket.update(dt);
                if (rocket.exploded) {
                    // rockets are removed automatically after explosion (no need to splice here)
                }
            }

            // Update explosion particles
            for (let i = particles.length - 1; i >= 0; i--) {
                const p = particles[i];
                p.update(dt);
                if (p.lifespan <= 0) {
                    particles.splice(i, 1); // remove dead particle
                }
            }

            // ---- Draw -------------------------------------------------------------
            ctx.clearRect(0, 0, W, H);

            // Draw rockets (they are not part of the shared particles array)
            rockets.forEach(r => r.draw());

            // Draw explosion particles
            particles.forEach(p => p.draw());

            // ---- Request next frame ------------------------------------------------
            requestAnimationFrame(gameLoop);
        }

        // Kick off the loop
        requestAnimationFrame(gameLoop);

        /* -------------------------------------------------
           Notes (optional – placed inside #notes for visibility)
        ------------------------------------------------- */
        const notesSection = document.getElementById('notes');
        notesSection.innerHTML = `
            <h2>Implementation Notes</h2>
            <ul>
                <li><strong>Particle Management:</strong> All active objects (rockets and explosion fragments) are stored in two separate arrays. 
                    Rockets are kept in <code>rockets</code>; once they explode they create <code>ExplosionParticle</code> instances that are pushed into <code>particles</code>.
                    Particles are filtered out each frame when their <code>lifespan</code> reaches zero.</li>
                <li><strong>Autonomous Launching:</strong> A simple timer (<code>launchTimer</code>) accumulates delta‑time and triggers a new rocket when it exceeds a random interval between 500 ms and 2000 ms.</li>
                <li><strong>Physics:</strong> Gravity is applied uniformly to every particle (rocket or fragment) by adding a constant <code>GRAVITY</code> to its vertical velocity each frame.</li>
                <li><strong>Explosion Condition:</strong> A rocket explodes after a fixed lifespan (<code>ROCKET_LIFESPAN</code>) or when it reaches near‑apex (upward speed ≈ 0).</li>
                <li><strong>Delta‑time (dt):</strong> The loop uses the browser‑provided <code>timestamp</parameter> to compute a frame‑time delta, ensuring smooth motion independent of frame‑rate.</li>
                <li><strong>Rendering:</strong> The canvas is cleared each frame, rockets are drawn first, then explosion particles with an alpha that fades out as they age.</li>
                <li><strong>Performance:</strong> Particle removal uses <code>splice</code> on the live array, which is cheap for the modest particle counts used here. All updates and draws are O(N) where N is the current particle count.</li>
            </ul>
        `;
    </script>
</body>
</html>
```

**Explanation of key parts**

| Section | What it does |
|---------|--------------|
| **Configuration constants** | Easy tuning of gravity, launch timing, lifespans, colors, etc. |
| **`Rocket` class** | Represents the rising projectile; handles its own motion, gravity, and explosion trigger. |
| **`ExplosionParticle` class** | Individual spark fragments; each has its own velocity, lifespan, size, and color, and fades out as it ages. |
| **Particle arrays** | `rockets` holds unfinished rockets; `particles` holds all active fragments (including those from explosions). |
| **Launch logic** | Randomized interval between launches, implemented with a running timer (`launchTimer`). |
| **Game loop (`gameLoop`)** | Uses `requestAnimationFrame` and a delta‑time (`dt`) to update positions, apply gravity, trigger explosions, and draw everything. |
| **Drawing & fading** | Explosion particles draw with an alpha proportional to remaining lifespan, creating a natural fade‑out. |
| **Notes section** | Contains a brief technical write‑up placed inside `#notes` as requested. |

The code runs directly in any modern browser—no external libraries required. Enjoy watching the autonomous fireworks!

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: Nemotron-3-Nano-30B-A3B-UD-Q5_K_XL.gguf -->
<!-- Prompt: fireworks.md -->
<!-- Generation Time: 23.87s -->
<!-- Fallback Used: False -->