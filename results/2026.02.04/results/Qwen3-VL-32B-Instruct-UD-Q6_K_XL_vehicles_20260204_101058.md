```html
<!DOCTYPE html>
<html>
<head>
    <title>Vehicle Collision Simulation</title>
    <style>
        body { margin: 0; overflow: hidden; background-color: #333; }
        canvas { display: block; margin: 20px auto; border: 1px solid #666; background-color: #000; }
        #notes {
            position: absolute;
            bottom: 10px;
            left: 10px;
            color: #aaa;
            font-family: monospace;
            font-size: 12px;
            background-color: rgba(0,0,0,0.7);
            padding: 10px;
            border-radius: 5px;
            width: 300px;
            z-index: 10;
        }
    </style>
</head>
<body>
    <canvas id="simulationCanvas" width="512" height="512"></canvas>

    <script>
        // --- YOUR JAVASCRIPT CODE GOES HERE ---

        // Constants
        const CANVAS_WIDTH = 512;
        const CANVAS_HEIGHT = 512;
        const VEHICLE_COUNT = 8;
        const EXPLOSION_PARTICLE_COUNT = 25;
        const EXPLOSION_DURATION = 3000; // 3 seconds
        const VEHICLE_SIZE = 30;
        const VEHICLE_SPEED_RANGE = 2; // pixels per frame (max)

        // Simulation state
        let simulationState = 'RUNNING';
        let lastTime = 0;
        let vehicles = [];
        let explosionParticles = [];
        let explosionStartTime = 0;
        let explosionCenter = { x: 0, y: 0 };

        // Canvas setup
        const canvas = document.getElementById('simulationCanvas');
        const ctx = canvas.getContext('2d');

        // Vehicle class
        class Vehicle {
            constructor(x, y, vx, vy, color) {
                this.x = x;
                this.y = y;
                this.vx = vx;
                this.vy = vy;
                this.color = color || this.getRandomColor();
                this.width = VEHICLE_SIZE;
                this.height = VEHICLE_SIZE;
                this.isActive = true;
            }

            getRandomColor() {
                const colors = ['#FF5733', '#33FF57', '#3357FF', '#FF33F5', '#F5FF33', '#33FFF5'];
                return colors[Math.floor(Math.random() * colors.length)];
            }

            update(dt) {
                this.x += this.vx * dt;
                this.y += this.vy * dt;
                this.wrap();
            }

            wrap() {
                // Wrap around edges
                if (this.x < 0) this.x = CANVAS_WIDTH;
                if (this.x > CANVAS_WIDTH) this.x = 0;
                if (this.y < 0) this.y = CANVAS_HEIGHT;
                if (this.y > CANVAS_HEIGHT) this.y = 0;
            }

            draw() {
                // Draw body (rectangle)
                ctx.fillStyle = this.color;
                ctx.fillRect(this.x - this.width / 2, this.y - this.height / 2, this.width, this.height);

                // Draw wheels (circles)
                ctx.fillStyle = '#000000';
                ctx.beginPath();
                ctx.arc(this.x - this.width / 4, this.y + this.height / 4, 5, 0, Math.PI * 2);
                ctx.arc(this.x + this.width / 4, this.y + this.height / 4, 5, 0, Math.PI * 2);
                ctx.fill();

                // Draw front light (circle)
                ctx.fillStyle = '#FFD700';
                ctx.beginPath();
                ctx.arc(this.x + this.width / 2 - 5, this.y - this.height / 4, 4, 0, Math.PI * 2);
                ctx.fill();
            }

            // Check collision with another vehicle
            collidesWith(other) {
                if (!this.isActive || !other.isActive) return false;
                const dx = this.x - other.x;
                const dy = this.y - other.y;
                const distance = Math.sqrt(dx * dx + dy * dy);
                return distance < (this.width + other.width) / 2;
            }

            // Get bounding box for collision detection
            getBoundingBox() {
                return {
                    x: this.x - this.width / 2,
                    y: this.y - this.height / 2,
                    width: this.width,
                    height: this.height
                };
            }
        }

        // Explosion Particle class
        class ExplosionParticle {
            constructor(x, y, vx, vy, color, lifespan) {
                this.x = x;
                this.y = y;
                this.vx = vx;
                this.vy = vy;
                this.color = color;
                this.lifespan = lifespan;
                this.maxLifespan = lifespan;
                this.size = 5 + Math.random() * 10;
            }

            update(dt) {
                this.x += this.vx * dt;
                this.y += this.vy * dt;
                this.lifespan -= dt;
                if (this.lifespan <= 0) {
                    this.isActive = false;
                }
            }

            draw() {
                // Fade out over time
                const alpha = this.lifespan / this.maxLifespan;
                ctx.fillStyle = `rgba(${this.color.r}, ${this.color.g}, ${this.color.b}, ${alpha})`;
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                ctx.fill();
            }

            isExpired() {
                return this.lifespan <= 0;
            }
        }

        // Helper function to generate random color
        function getRandomColor() {
            const r = Math.floor(Math.random() * 255);
            const g = Math.floor(Math.random() * 255);
            const b = Math.floor(Math.random() * 255);
            return { r, g, b };
        }

        // Initialize simulation
        function initSimulation() {
            // Clear existing vehicles
            vehicles = [];

            // Create new vehicles
            for (let i = 0; i < VEHICLE_COUNT; i++) {
                const x = Math.random() * CANVAS_WIDTH;
                const y = Math.random() * CANVAS_HEIGHT;
                const vx = (Math.random() - 0.5) * VEHICLE_SPEED_RANGE * 2;
                const vy = (Math.random() - 0.5) * VEHICLE_SPEED_RANGE * 2;
                const color = `rgb(${Math.floor(Math.random() * 255)}, ${Math.floor(Math.random() * 255)}, ${Math.floor(Math.random() * 255)})`;
                vehicles.push(new Vehicle(x, y, vx, vy, color));
            }

            // Clear explosion particles
            explosionParticles = [];
            simulationState = 'RUNNING';
        }

        // Trigger explosion at a point
        function triggerExplosion(x, y) {
            explosionCenter = { x, y };
            explosionStartTime = performance.now();
            simulationState = 'EXPLODING';

            // Create explosion particles
            explosionParticles = [];
            for (let i = 0; i < EXPLOSION_PARTICLE_COUNT; i++) {
                // Random direction and speed
                const angle = Math.random() * Math.PI * 2;
                const speed = 5 + Math.random() * 10;
                const vx = Math.cos(angle) * speed;
                const vy = Math.sin(angle) * speed;
                const color = getRandomColor();
                const lifespan = 2000 + Math.random() * 1000; // 2-3 seconds
                explosionParticles.push(new ExplosionParticle(x, y, vx, vy, color, lifespan));
            }

            // Mark all vehicles as inactive
            vehicles.forEach(v => v.isActive = false);
        }

        // Check for collisions
        function checkCollisions() {
            for (let i = 0; i < vehicles.length; i++) {
                for (let j = i + 1; j < vehicles.length; j++) {
                    if (vehicles[i].collidesWith(vehicles[j])) {
                        // Trigger explosion at midpoint
                        const cx = (vehicles[i].x + vehicles[j].x) / 2;
                        const cy = (vehicles[i].y + vehicles[j].y) / 2;
                        triggerExplosion(cx, cy);
                        return true; // Exit after first collision
                    }
                }
            }
            return false;
        }

        // Draw "BOOM" text on explosion
        function drawBoomText(x, y) {
            ctx.save();
            ctx.font = 'bold 48px Arial';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillStyle = 'rgba(255, 255, 0, 0.9)';
            ctx.fillText('BOOM!', x, y);
            ctx.restore();
        }

        // Main animation loop
        function animate(currentTime) {
            const dt = currentTime - lastTime;
            lastTime = currentTime;

            ctx.clearRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);

            switch (simulationState) {
                case 'RUNNING':
                    // Update vehicles
                    vehicles.forEach(v => v.update(dt));

                    // Check for collisions
                    if (checkCollisions()) {
                        // Collision detected, switch to explosion state
                        break;
                    }

                    // Draw vehicles
                    vehicles.forEach(v => {
                        if (v.isActive) {
                            v.draw();
                        }
                    });
                    break;

                case 'EXPLODING':
                    // Update explosion particles
                    explosionParticles.forEach(p => p.update(dt));

                    // Remove expired particles
                    explosionParticles = explosionParticles.filter(p => !p.isExpired());

                    // Draw particles
                    explosionParticles.forEach(p => p.draw());

                    // Draw "BOOM" text at explosion center
                    drawBoomText(explosionCenter.x, explosionCenter.y);

                    // Check if explosion is over
                    if (explosionParticles.length === 0 || 
                        (performance.now() - explosionStartTime) > EXPLOSION_DURATION) {
                        simulationState = 'RESTARTING';
                    }
                    break;

                case 'RESTARTING':
                    // Delay before restarting (1 second)
                    if (performance.now() - explosionStartTime > EXPLOSION_DURATION + 1000) {
                        initSimulation();
                    } else {
                        // Draw a fading "Restarting..." message
                        ctx.save();
                        ctx.font = '24px Arial';
                        ctx.textAlign = 'center';
                        ctx.textBaseline = 'middle';
                        ctx.fillStyle = 'rgba(255, 255, 255, 0.5)';
                        ctx.fillText('Restarting in 1 sec...', CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2);
                        ctx.restore();
                    }
                    break;
            }

            requestAnimationFrame(animate);
        }

        // Start simulation
        initSimulation();
        requestAnimationFrame(animate);

        // Optional notes
        // ---
        // Developer notes:
        // - Collision detection uses distance-based method for simplicity.
        // - Vehicles wrap around canvas edges using simple boundary checks.
        // - Explosion particles fade out over time using alpha blending.
        // - State machine manages simulation flow: RUNNING -> EXPLODING -> RESTARTING -> RUNNING.
        // - Added visual feedback with "BOOM" text during explosion.
        // - Smooth animation achieved with delta time calculation.
        // ---
    </script>

    <!-- Optional section for notes -->
    <section id="notes">
        Developer notes regarding collision detection method, state management, design choices, etc.
        - Collision detection uses distance-based method for simplicity.
        - Vehicles wrap around canvas edges using simple boundary checks.
        - Explosion particles fade out over time using alpha blending.
        - State machine manages simulation flow: RUNNING -> EXPLODING -> RESTARTING -> RUNNING.
        - Added visual feedback with "BOOM" text during explosion.
        - Smooth animation achieved with delta time calculation.
    </section>
</body>
</html>
```

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: Qwen3-VL-32B-Instruct-UD-Q6_K_XL.gguf -->
<!-- Prompt: vehicles.md -->
<!-- Time: 132.62s -->
<!-- Fallback: False -->