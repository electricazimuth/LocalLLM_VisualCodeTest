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
    /* -------------  GLOBAL VARIABLES ------------- */
    const canvas = document.getElementById('simulationCanvas');
    const ctx = canvas.getContext('2d');
    const WIDTH = canvas.width, HEIGHT = canvas.height;

    const NUM_VEHICLES = 8;                 // Number of vehicles to spawn
    const VEHICLE_RADIUS = 20;              // Radius used for collision & wrapping
    const EXPLOSION_PARTICLES = 25;         // Particles per explosion
    const EXPLOSION_MIN_LIFE = 0.5;         // Seconds
    const EXPLOSION_MAX_LIFE = 1.5;         // Seconds
    const RESTART_DELAY = 1500;             // Milliseconds before new run

    let simulationState = 'RUNNING';        // 'RUNNING', 'EXPLODING', 'RESTARTING'
    let vehicles = [];
    let explosionParticles = [];
    let lastTimestamp = performance.now();
    let restartTimer = null;

    /* -------------  CLASSES ------------- */
    class Vehicle {
        constructor() {
            this.radius = VEHICLE_RADIUS;
            this.x = Math.random() * WIDTH;
            this.y = Math.random() * HEIGHT;
            // Random speed between 30-80 pixels per second
            const speed = 30 + Math.random() * 50;
            const angle = Math.random() * Math.PI * 2;
            this.vx = Math.cos(angle) * speed;
            this.vy = Math.sin(angle) * speed;
            this.color = this.randomColor();
            this.isActive = true;
        }

        randomColor() {
            const r = Math.floor(128 + Math.random() * 127);
            const g = Math.floor(128 + Math.random() * 127);
            const b = Math.floor(128 + Math.random() * 127);
            return `rgb(${r},${g},${b})`;
        }

        update(dt) {
            if (!this.isActive) return;
            this.x += this.vx * dt;
            this.y += this.vy * dt;
            this.wrap();
        }

        wrap() {
            if (this.x < -this.radius) this.x = WIDTH + this.radius;
            if (this.x > WIDTH + this.radius) this.x = -this.radius;
            if (this.y < -this.radius) this.y = HEIGHT + this.radius;
            if (this.y > HEIGHT + this.radius) this.y = -this.radius;
        }

        draw(ctx) {
            if (!this.isActive) return;
            // Draw body
            ctx.save();
            ctx.translate(this.x, this.y);
            ctx.rotate(Math.atan2(this.vy, this.vx));
            ctx.fillStyle = this.color;
            ctx.fillRect(-this.radius, -this.radius/2, this.radius*2, this.radius);
            // Draw wheels
            ctx.fillStyle = '#444';
            ctx.beginPath();
            ctx.arc(-this.radius/2, this.radius/2, this.radius/4, 0, Math.PI*2);
            ctx.fill();
            ctx.beginPath();
            ctx.arc(this.radius/2, this.radius/2, this.radius/4, 0, Math.PI*2);
            ctx.fill();
            ctx.restore();
        }
    }

    class ExplosionParticle {
        constructor(x, y) {
            this.x = x;
            this.y = y;
            this.radius = 3 + Math.random() * 3;
            // Random outward speed
            const speed = 50 + Math.random() * 100;
            const angle = Math.random() * Math.PI * 2;
            this.vx = Math.cos(angle) * speed;
            this.vy = Math.sin(angle) * speed;
            this.life = EXPLOSION_MIN_LIFE + Math.random() * (EXPLOSION_MAX_LIFE - EXPLOSION_MIN_LIFE);
            this.remaining = this.life;
            this.color = this.randomColor();
            this.alpha = 1;
        }

        randomColor() {
            const r = 200 + Math.floor(Math.random() * 55);
            const g = 100 + Math.floor(Math.random() * 155);
            const b = 0;
            return `rgb(${r},${g},${b})`;
        }

        update(dt) {
            this.x += this.vx * dt;
            this.y += this.vy * dt;
            this.remaining -= dt;
            this.alpha = Math.max(0, this.remaining / this.life);
        }

        isAlive() {
            return this.remaining > 0;
        }

        draw(ctx) {
            if (!this.isAlive()) return;
            ctx.save();
            ctx.globalAlpha = this.alpha;
            ctx.fillStyle = this.color;
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
            ctx.fill();
            ctx.restore();
        }
    }

    /* -------------  INITIALISATION ------------- */
    function initVehicles() {
        vehicles = [];
        for (let i = 0; i < NUM_VEHICLES; i++) {
            vehicles.push(new Vehicle());
        }
    }

    initVehicles(); // Start first run

    /* -------------  COLLISION DETECTION ------------- */
    function checkCollisions() {
        for (let i = 0; i < vehicles.length; i++) {
            const a = vehicles[i];
            if (!a.isActive) continue;
            for (let j = i + 1; j < vehicles.length; j++) {
                const b = vehicles[j];
                if (!b.isActive) continue;
                const dx = a.x - b.x;
                const dy = a.y - b.y;
                const distSq = dx * dx + dy * dy;
                const radiusSum = a.radius + b.radius;
                if (distSq <= radiusSum * radiusSum) {
                    // Collision!
                    a.isActive = false;
                    b.isActive = false;
                    triggerExplosion((a.x + b.x) / 2, (a.y + b.y) / 2);
                    return; // Only one collision per frame needed
                }
            }
        }
    }

    /* -------------  EXPLOSION ------------- */
    function triggerExplosion(x, y) {
        simulationState = 'EXPLODING';
        explosionParticles = [];
        for (let i = 0; i < EXPLOSION_PARTICLES; i++) {
            explosionParticles.push(new ExplosionParticle(x, y));
        }
        // Optional: add a "BOOM" text effect
        boomText = {
            x: x,
            y: y,
            alpha: 1,
            scale: 1
        };
    }

    /* -------------  UPDATE LOOP ------------- */
    function update(dt) {
        switch (simulationState) {
            case 'RUNNING':
                vehicles.forEach(v => v.update(dt));
                checkCollisions();
                break;
            case 'EXPLODING':
                explosionParticles.forEach(p => p.update(dt));
                // Remove dead particles
                explosionParticles = explosionParticles.filter(p => p.isAlive());
                if (explosionParticles.length === 0) {
                    simulationState = 'RESTARTING';
                    restartTimer = setTimeout(() => {
                        simulationState = 'RUNNING';
                        initVehicles();
                    }, RESTART_DELAY);
                }
                break;
            case 'RESTARTING':
                // Nothing to update; waiting for timeout
                break;
        }
    }

    /* -------------  DRAW LOOP ------------- */
    function draw() {
        ctx.clearRect(0, 0, WIDTH, HEIGHT);
        switch (simulationState) {
            case 'RUNNING':
                vehicles.forEach(v => v.draw(ctx));
                break;
            case 'EXPLODING':
                explosionParticles.forEach(p => p.draw(ctx));
                // Draw BOOM text
                if (boomText) {
                    ctx.save();
                    ctx.globalAlpha = boomText.alpha;
                    ctx.fillStyle = 'white';
                    ctx.font = `${30 * boomText.scale}px Arial`;
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    ctx.fillText('BOOM', boomText.x, boomText.y);
                    ctx.restore();
                    // Animate boom text
                    boomText.alpha -= 0.02;
                    boomText.scale += 0.01;
                }
                break;
            case 'RESTARTING':
                // Could show a fading message or nothing
                break;
        }
    }

    /* -------------  MAIN LOOP ------------- */
    function mainLoop(timestamp) {
        const dt = (timestamp - lastTimestamp) / 1000; // Convert ms to seconds
        lastTimestamp = timestamp;

        update(dt);
        draw();

        requestAnimationFrame(mainLoop);
    }

    requestAnimationFrame(mainLoop);
    </script>

    <!-- Optional section for notes -->
    <section id="notes">
        <h2>Developer Notes</h2>
        <ul>
            <li>Vehicles are represented as simple rectangles with two wheels for visual variety.</li>
            <li>Collision detection uses a circle‑based distance check for simplicity and performance.</li>
            <li>When a collision occurs, the two involved vehicles are marked inactive and an explosion burst is created.</li>
            <li>Explosion particles fade out based on a lifespan counter; once all have expired, the simulation restarts after a short delay.</li>
            <li>The simulation uses <code>requestAnimationFrame</code> and delta time to keep movement frame‑rate independent.</li>
            <li>All logic is contained in a single file for easy deployment; no external libraries are required.</li>
        </ul>
    </section>
</body>
</html>
```

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: gpt-oss-20b-mxfp4.gguf -->
<!-- Prompt: vehicles.md -->
<!-- Generation Time: 17.67s -->
<!-- Fallback Used: False -->