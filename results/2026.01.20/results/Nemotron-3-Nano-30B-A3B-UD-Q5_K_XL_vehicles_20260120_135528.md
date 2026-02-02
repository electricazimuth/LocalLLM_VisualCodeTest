```html
<!DOCTYPE html>
<html>
<head>
    <title>Vehicle Collision Simulation</title>
    <style>
        body { margin:0; overflow:hidden; background:#111; }
        canvas { display:block; margin:20px auto; background:#000; border:1px solid #555; }
    </style>
</head>
<body>
    <canvas id="simulationCanvas" width="512" height="512"></canvas>

    <script>
        /*=====================================================================
        Vehicle Collision & Restart Simulation
        --------------------------------------------------------------------
        • Vehicles move with random velocity and wrap around the canvas edges.
        • Collision detection (circle based) removes the colliding vehicles.
        • An explosion of particles is emitted at the collision point.
        • After the explosion finishes, the simulation restarts with fresh
          vehicles after a short delay.
        • All logic uses plain JavaScript + Canvas API, driven by
          requestAnimationFrame with proper delta‑time handling.
        =====================================================================*/

        /*------------------------------- CONFIG -------------------------------*/
        const NUM_VEHICLES   = 6;          // how many vehicles start each round
        const PARTICLES_MAX  = 25;         // max particles per explosion
        const EXPLOSION_TIME = 1500;       // ms to wait before restarting
        const VEHICLE_SIZE   = 30;         // width/height of vehicle body
        const WHEEL_RADIUS   = 6;          // wheel radius for drawing
        const VEHICLE_SPEED  = 120;        // max initial speed (px/s)
        const CANVAS_W       = 512;
        const CANVAS_H       = 512;

        /*------------------------------- STATE ---------------------------------*/
        const canvas = document.getElementById('simulationCanvas');
        const ctx    = canvas.getContext('2d');

        let vehicles          = [];   // active Vehicle instances
        let particles         = [];   // currently active explosion particles
        let state             = 'RUNNING'; // 'RUNNING' | 'EXPLODING' | 'RESTARTING'
        let lastTimestamp     = 0;    // for delta‑time calculation
        let lastCollisionPos  = {x:0, y:0}; // cached collision point (optional)

        /*------------------------------- HELPERS ---------------------------------*/
        const rand = (min, max) => Math.random() * (max - min) + min;
        const randInt = (max) => Math.floor(Math.random() * max);
        const randColor = () => `hsl(${rand(0,360)},70%,${rand(40,70)}%)`;

        /*------------------------------- CLASSES --------------------------------*/
        class Vehicle {
            constructor() {
                // random start position inside canvas (allow slight offset)
                this.x = rand(0, CANVAS_W);
                this.y = rand(0, CANVAS_H);
                // random velocity, magnitude limited to VEHICLE_SPEED
                const speed = rand(20, VEHICLE_SPEED);
                const angle = rand(0, Math.PI * 2);
                this.vx = Math.cos(angle) * speed;
                this.vy = Math.sin(angle) * speed;
                // size / collision radius
                this.width  = VEHICLE_SIZE;
                this.height = VEHICLE_SIZE;
                this.radius = VEHICLE_SIZE / 2;
                // visual style
                this.color  = randColor();
                this.active = true; // removed when collided
            }

            update(dt) {
                if (!this.active) return;
                this.x += this.vx * dt;
                this.y += this.vy * dt;
                this._wrap();
            }

            _wrap() {
                if (this.x < 0)      this.x = CANVAS_W;
                if (this.x > CANVAS_W) this.x = 0;
                if (this.y < 0)      this.y = CANVAS_H;
                if (this.y > CANVAS_H) this.y = 0;
            }

            draw() {
                if (!this.active) return;
                const w = this.width, h = this.height;
                const r = WHEEL_RADIUS;
                const cx = this.x, cy = this.y;

                // body – simple rounded rectangle
                ctx.save();
                ctx.fillStyle = this.color;
                ctx.strokeStyle = '#555';
                ctx.lineWidth = 1;
                ctx.beginPath();
                ctx.moveTo(cx - w/2, cy - h/2);
                ctx.lineTo(cx + w/2, cy - h/2);
                ctx.lineTo(cx + w/2, cy + h/2);
                ctx.lineTo(cx - w/2, cy + h/2);
                ctx.closePath();
                ctx.fill();
                ctx.stroke();

                // wheels
                ctx.beginPath();
                ctx.arc(cx - w/3, cy + h/3, r, 0, Math.PI*2);
                ctx.arc(cx + w/3, cy + h/3, r, 0, Math.PI*2);
                ctx.fillStyle = '#222';
                ctx.fill();
                ctx.restore();
            }
        }

        class ExplosionParticle {
            constructor(x, y) {
                this.x = x;
                this.y = y;
                // outward random velocity
                const speed = rand(100, 200);
                const angle = rand(0, Math.PI*2);
                this.vx = Math.cos(angle) * speed;
                this.vy = Math.sin(angle) * speed;
                // visual
                this.size   = rand(2, 5);
                this.life   = 1;            // normalized 0‑1
                this.maxLife = 1;
                this.color  = `hsl(${rand(0,360)},80%,${rand(70,90)}%)`;
            }

            update(dt) {
                this.life -= dt / this.maxLife; // lifespan in seconds
                if (this.life < 0) this.life = 0;
                this.x += this.vx * dt;
                this.y += this.vy * dt;
            }

            draw() {
                const alpha = this.life; // 0‑1
                if (alpha <= 0) return;
                ctx.save();
                ctx.globalAlpha = alpha;
                ctx.fillStyle = this.color;
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size, 0, Math.PI*2);
                ctx.fill();
                ctx.restore();
            }

            isDead() {
                return this.life <= 0;
            }
        }

        /*------------------------------- INITIALISATION --------------------------*/
        function initVehicles() {
            vehicles = [];
            for (let i = 0; i < NUM_VEHICLES; i++) {
                vehicles.push(new Vehicle());
            }
        }

        function initParticles(x, y) {
            particles = [];
            const count = randInt(PARTICLES_MAX) + 5;
            for (let i = 0; i < count; i++) {
                particles.push(new ExplosionParticle(x, y));
            }
        }

        function createExplosion(x, y) {
            // store point for drawing “BOOM” later if desired
            lastCollisionPos = {x, y};
            initParticles(x, y);
            state = 'EXPLODING';
        }

        function restartSimulation() {
            initVehicles();
            particles = [];
            state = 'RUNNING';
        }

        /*------------------------------- COLLISION ---------------------------------*/
        function checkCollision() {
            const active = vehicles.filter(v => v.active);
            for (let i = 0; i < active.length; i++) {
                for (let j = i + 1; j < active.length; j++) {
                    const a = active[i], b = active[j];
                    const dx = a.x - b.x;
                    const dy = a.y - b.y;
                    const distSq = dx*dx + dy*dy;
                    const radiiSum = a.radius + b.radius;
                    if (distSq < radiiSum * radiiSum) {
                        return {i, j, x: (a.x + b.x) / 2, y: (a.y + b.y) / 2};
                    }
                }
            }
            return null;
        }

        /*------------------------------- MAIN LOOP --------------------------------*/
        function loop(timestamp) {
            if (!lastTimestamp) lastTimestamp = timestamp;
            const dt = (timestamp - lastTimestamp) / 1000; // seconds
            lastTimestamp = timestamp;

            ctx.clearRect(0, 0, CANVAS_W, CANVAS_H);

            switch (state) {
                case 'RUNNING':
                    // update all vehicles
                    vehicles.forEach(v => v.update(dt));

                    // collision detection
                    const coll = checkCollision();
                    if (coll) {
                        // deactivate the two vehicles that hit each other
                        vehicles[coll.i].active = false;
                        vehicles[coll.j].active = false;
                        // spawn explosion at cached collision point
                        createExplosion(coll.x, coll.y);
                    }
                    break;

                case 'EXPLODING':
                    // update particles
                    particles.forEach(p => p.update(dt));
                    // draw particles
                    particles.forEach(p => p.draw());

                    // when all particles are dead, start countdown to restart
                    if (particles.every(p => p.isDead())) {
                        // wait a short moment before restarting
                        if (!window.__restartTimer) window.__restartTimer = timestamp;
                        if (timestamp - window.__restartTimer > EXPLOSION_TIME) {
                            restartSimulation();
                            window.__restartTimer = null;
                        }
                    }
                    break;

                case 'RESTARTING':
                    // nothing special – state already switched back to RUNNING
                    break;
            }

            // draw active vehicles
            vehicles.forEach(v => v.draw());

            requestAnimationFrame(loop);
        }

        /*------------------------------- STARTUP ---------------------------------*/
        initVehicles();               // first round of vehicles
        requestAnimationFrame(loop);  // kick off animation
    </script>

    <!--
    Developer notes:
    • Vehicles are represented as simple rounded rectangles with two wheels.
    • Collision detection uses circle‑based overlap (radius = half vehicle size).
    • When a collision occurs both vehicles are marked inactive and an
      explosion of `ExplosionParticle` objects is emitted at the midpoint.
    • The simulation state machine cleanly separates RUNNING, EXPLODING,
      and RESTARTING phases, ensuring no vehicle or particle is updated
      outside its intended phase.
    • Delta‑time (`dt`) is calculated from `requestAnimationFrame` timestamps
      and used for frame‑rate independent movement and particle fading.
    • After the explosion finishes, a short delay (`EXPLOSION_TIME`) passes
      before the next round of vehicles is spawned, giving a clear visual
      pause before the restart.
    • All code lives in a single HTML file and uses only the Canvas API.
    -->
</body>
</html>
```

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: Nemotron-3-Nano-30B-A3B-UD-Q5_K_XL.gguf -->
<!-- Prompt: vehicles.md -->
<!-- Generation Time: 30.43s -->
<!-- Fallback Used: False -->