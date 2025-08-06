```html
<!DOCTYPE html>
<html>
<head>
    <title>Vehicle Collision Simulation</title>
    <style>
        body { margin: 0; overflow: hidden; background-color: #333; }
        canvas { display: block; margin: 20px auto; border: 1px solid #666; background-color: #000; }
    </style>
</head>
<body>
    <canvas id="simulationCanvas" width="512" height="512"></canvas>

    <script>
        /* -------------------------------------------------------------
           Vehicle Collision & Restart Simulation
           ------------------------------------------------------------- */

        // ----- Configuration ------------------------------------------------
        const CANVAS_WIDTH  = 512;
        const CANVAS_HEIGHT = 512;
        const NUM_VEHICLES  = 7;          // 5‑10 vehicles
        const VEHICLE_MIN_RADIUS = 15;
        const VEHICLE_MAX_RADIUS = 25;
        const VEHICLE_MIN_SPEED = 30;     // px/s
        const VEHICLE_MAX_SPEED = 80;
        const EXPLOSION_PARTICLES = 25;
        const PARTICLE_MIN_SPEED = 50;
        const PARTICLE_MAX_SPEED = 150;
        const PARTICLE_LIFESPAN = 1.0;    // seconds
        const RESTART_DELAY = 1.5;        // seconds after explosion

        // ----- Canvas & Context ------------------------------------------
        const canvas = document.getElementById('simulationCanvas');
        const ctx = canvas.getContext('2d');

        // ----- State Variables --------------------------------------------
        let simulationState = 'RUNNING';   // 'RUNNING', 'EXPLODING', 'RESTARTING'
        let vehicles = [];
        let explosionParticles = [];
        let boomTimer = 0;                // time since explosion started
        let restartTimer = 0;             // countdown to restart

        // ----- Utility Functions ------------------------------------------
        function randomRange(min, max) {
            return Math.random() * (max - min) + min;
        }

        function randomColor() {
            const hue = Math.floor(Math.random() * 360);
            return `hsl(${hue}, 70%, 60%)`;
        }

        // ----- Vehicle Class ---------------------------------------------
        class Vehicle {
            constructor() {
                this.radius = randomRange(VEHICLE_MIN_RADIUS, VEHICLE_MAX_RADIUS);
                this.x = randomRange(this.radius, CANVAS_WIDTH - this.radius);
                this.y = randomRange(this.radius, CANVAS_HEIGHT - this.radius);
                const angle = randomRange(0, Math.PI * 2);
                const speed = randomRange(VEHICLE_MIN_SPEED, VEHICLE_MAX_SPEED);
                this.vx = Math.cos(angle) * speed;
                this.vy = Math.sin(angle) * speed;
                this.color = randomColor();
            }

            update(dt) {
                this.x += this.vx * dt;
                this.y += this.vy * dt;

                // Wrap around
                if (this.x < -this.radius) this.x = CANVAS_WIDTH + this.radius;
                if (this.x > CANVAS_WIDTH + this.radius) this.x = -this.radius;
                if (this.y < -this.radius) this.y = CANVAS_HEIGHT + this.radius;
                if (this.y > CANVAS_HEIGHT + this.radius) this.y = -this.radius;
            }

            draw(ctx) {
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
                ctx.fillStyle = this.color;
                ctx.fill();
            }
        }

        // ----- Explosion Particle Class ----------------------------------
        class ExplosionParticle {
            constructor(x, y) {
                this.x = x;
                this.y = y;
                const angle = randomRange(0, Math.PI * 2);
                const speed = randomRange(PARTICLE_MIN_SPEED, PARTICLE_MAX_SPEED);
                this.vx = Math.cos(angle) * speed;
                this.vy = Math.sin(angle) * speed;
                this.lifespan = PARTICLE_LIFESPAN;
                this.size = randomRange(2, 5);
                this.color = `hsl(${Math.floor(Math.random() * 360)}, 80%, 50%)`;
                this.alpha = 1.0;
            }

            update(dt) {
                this.x += this.vx * dt;
                this.y += this.vy * dt;
                this.lifespan -= dt;
                this.alpha = Math.max(this.lifespan / PARTICLE_LIFESPAN, 0);
            }

            draw(ctx) {
                ctx.globalAlpha = this.alpha;
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                ctx.fillStyle = this.color;
                ctx.fill();
                ctx.globalAlpha = 1.0;
            }
        }

        // ----- Initialization --------------------------------------------
        function initVehicles() {
            vehicles = [];
            for (let i = 0; i < NUM_VEHICLES; i++) {
                vehicles.push(new Vehicle());
            }
        }

        function initExplosion(x, y) {
            explosionParticles = [];
            for (let i = 0; i < EXPLOSION_PARTICLES; i++) {
                explosionParticles.push(new ExplosionParticle(x, y));
            }
            boomTimer = 0;
        }

        // ----- Collision Detection ---------------------------------------
        function checkCollisions() {
            for (let i = 0; i < vehicles.length; i++) {
                for (let j = i + 1; j < vehicles.length; j++) {
                    const v1 = vehicles[i];
                    const v2 = vehicles[j];
                    const dx = v1.x - v2.x;
                    const dy = v1.y - v2.y;
                    const dist = Math.hypot(dx, dy);
                    if (dist < v1.radius + v2.radius) {
                        // Collision detected
                        const collisionX = (v1.x + v2.x) / 2;
                        const collisionY = (v1.y + v2.y) / 2;
                        simulationState = 'EXPLODING';
                        initExplosion(collisionX, collisionY);
                        // Remove the colliding vehicles
                        vehicles.splice(j, 1);
                        vehicles.splice(i, 1);
                        return; // Only handle one collision per frame
                    }
                }
            }
        }

        // ----- Animation Loop --------------------------------------------
        let lastTimestamp = null;
        function animate(timestamp) {
            if (!lastTimestamp) lastTimestamp = timestamp;
            const delta = (timestamp - lastTimestamp) / 1000; // seconds
            lastTimestamp = timestamp;

            // Update & Draw based on state
            if (simulationState === 'RUNNING') {
                vehicles.forEach(v => v.update(delta));
                checkCollisions();
            } else if (simulationState === 'EXPLODING') {
                boomTimer += delta;
                explosionParticles.forEach(p => p.update(delta));
                // Remove dead particles
                explosionParticles = explosionParticles.filter(p => p.lifespan > 0);
                if (explosionParticles.length === 0) {
                    simulationState = 'RESTARTING';
                    restartTimer = RESTART_DELAY;
                }
            } else if (simulationState === 'RESTARTING') {
                restartTimer -= delta;
                if (restartTimer <= 0) {
                    initVehicles();
                    simulationState = 'RUNNING';
                }
            }

            // Render
            ctx.clearRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);

            if (simulationState === 'RUNNING') {
                vehicles.forEach(v => v.draw(ctx));
            } else if (simulationState === 'EXPLODING') {
                explosionParticles.forEach(p => p.draw(ctx));
                // Draw expanding "BOOM" text
                if (boomTimer < 0.5) { // show for 0.5s
                    const scale = 1 + boomTimer * 8; // quick expansion
                    ctx.font = `${30 * scale}px Arial`;
                    ctx.fillStyle = `rgba(255, 255, 0, ${1 - boomTimer * 2})`;
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    // Position at center of canvas for simplicity
                    ctx.fillText('BOOM', CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2);
                }
            } else if (simulationState === 'RESTARTING') {
                // Optional: show a subtle "Restarting..." message
                ctx.font = '20px Arial';
                ctx.fillStyle = '#fff';
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillText('Restarting...', CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2);
            }

            requestAnimationFrame(animate);
        }

        // ----- Start ------------------------------------------------------
        initVehicles();
        requestAnimationFrame(animate);
    </script>

    <!-- Optional section for notes -->
    <!--
    <section id="notes">
        <h2>Implementation Notes</h2>
        <ul>
            <li>Vehicles are represented as circles for simple collision detection.</li>
            <li>Collision detection uses a pairwise distance check, breaking after the first collision to trigger an explosion.</li>
            <li>Explosion particles are short‑lived and fade out by reducing their alpha over time.</li>
            <li>State machine controls the flow: RUNNING → EXPLODING → RESTARTING → RUNNING.</li>
            <li>Delta time ensures consistent movement across different frame rates.</li>
        </ul>
    </section>
    -->
</body>
</html>
```

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: DeepSeek-R1-Distill-Qwen-32B-Q4_K_M.gguf -->
<!-- Prompt: vehicles.md -->
<!-- Generation Time: 20.60s -->
<!-- Fallback Used: False -->