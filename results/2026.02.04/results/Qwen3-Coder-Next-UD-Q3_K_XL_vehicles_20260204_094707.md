Here is the complete simulation in a single HTML file, following all your requirements for object management, state transitions, collision detection, and smooth animation.

```html
<!DOCTYPE html>
<html>
<head>
    <title>Vehicle Collision & Restart Simulation</title>
    <style>
        body { 
            margin: 0; 
            overflow: hidden; 
            background-color: #333; 
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            font-family: sans-serif;
            color: white;
        }
        canvas { 
            display: block; 
            margin: 20px auto; 
            border: 2px solid #666; 
            background-color: #000;
            box-shadow: 0 0 20px rgba(0,0,0,0.5);
        }
        #instructions {
            text-align: center;
            margin-bottom: 10px;
        }
        h1 { margin: 0; font-size: 1.5rem; color: #ddd; }
        p { margin: 5px 0 0; font-size: 0.9rem; color: #aaa; }
    </style>
</head>
<body>

    <div id="instructions">
        <h1>Vehicle Collision Simulation</h1>
        <p>Vehicles wrap around edges. Collisions trigger explosions. Simulation resets automatically.</p>
    </div>

    <canvas id="simulationCanvas" width="512" height="512"></canvas>

    <script>
        /**
         * SIMULATION CONSTANTS
         */
        const CANVAS_WIDTH = 512;
        const CANVAS_HEIGHT = 512;
        const VEHICLE_COUNT = 8;
        const VEHICLE_SIZE = 20; // Radius for collision
        const VEHICLE_SPEED_MIN = 100;
        const VEHICLE_SPEED_MAX = 250;
        
        const EXPLOSION_PARTICLE_COUNT = 30;
        const EXPLOSION_DURATION = 1.5; // Seconds particles live
        const RESTART_DELAY = 2.0; // Seconds after explosion before reset
        
        // State Enum
        const STATE = {
            RUNNING: 'RUNNING',
            EXPLODING: 'EXPLODING',
            RESTARTING: 'RESTARTING'
        };

        /**
         * UTILITIES
         */
        function randomRange(min, max) {
            return Math.random() * (max - min) + min;
        }

        function randomColor() {
            const colors = ['#FF5733', '#33FF57', '#3357FF', '#FF33F6', '#F6FF33', '#33FFF6'];
            return colors[Math.floor(Math.random() * colors.length)];
        }

        /**
         * VEHICLE CLASS
         * Handles movement, wrapping, and drawing a simple vehicle shape.
         */
        class Vehicle {
            constructor(x, y) {
                this.x = x;
                this.y = y;
                // Random velocity vector
                const angle = Math.random() * Math.PI * 2;
                const speed = randomRange(VEHICLE_SPEED_MIN, VEHICLE_SPEED_MAX);
                this.vx = Math.cos(angle) * speed;
                this.vy = Math.sin(angle) * speed;
                
                this.radius = VEHICLE_SIZE;
                this.color = randomColor();
                this.isActive = true;
                this.width = this.radius * 2.5;
                this.height = this.radius * 1.2;
            }

            update(dt) {
                if (!this.isActive) return;

                // Move based on velocity and delta time
                this.x += this.vx * dt;
                this.y += this.vy * dt;

                // Screen Wrapping
                if (this.x < -this.radius) this.x = CANVAS_WIDTH + this.radius;
                if (this.x > CANVAS_WIDTH + this.radius) this.x = -this.radius;
                if (this.y < -this.radius) this.y = CANVAS_HEIGHT + this.radius;
                if (this.y > CANVAS_HEIGHT + this.radius) this.y = -this.radius;
            }

            draw(ctx) {
                if (!this.isActive) return;

                ctx.save();
                ctx.translate(this.x, this.y);
                
                // Calculate rotation angle based on velocity
                const angle = Math.atan2(this.vy, this.vx);
                ctx.rotate(angle);

                // Draw Body (Truck/Cart shape)
                ctx.fillStyle = this.color;
                ctx.shadowBlur = 10;
                ctx.shadowColor = this.color;
                
                // Main chassis
                ctx.fillRect(-this.width/2, -this.height/2, this.width, this.height);
                
                // Cabin
                ctx.fillStyle = '#000'; // Window
                ctx.fillRect(0, -this.height/3, this.width/3, this.height/1.5);
                
                // Wheels
                ctx.fillStyle = '#222';
                ctx.beginPath();
                ctx.arc(-this.width/3, this.height/2, this.radius/3, 0, Math.PI*2);
                ctx.arc(this.width/3, this.height/2, this.radius/3, 0, Math.PI*2);
                ctx.fill();

                ctx.restore();
            }

            getBounds() {
                // Return a circle object for collision check
                return { x: this.x, y: this.y, r: this.radius };
            }
        }

        /**
         * EXPLOSION PARTICLE CLASS
         * Handles physics, fading, and drawing of explosion debris.
         */
        class ExplosionParticle {
            constructor(x, y, color) {
                this.x = x;
                this.y = y;
                this.color = color;
                
                // Random outward velocity
                const angle = Math.random() * Math.PI * 2;
                const speed = randomRange(50, 300);
                this.vx = Math.cos(angle) * speed;
                this.vy = Math.sin(angle) * speed;

                this.life = 1.0; // 100% life
                this.decay = randomRange(0.4, 0.8); // Life loss per second
                this.size = randomRange(2, 6);
                this.gravity = 100; // Slight gravity effect
                this.friction = 0.95; // Velocity decay
            }

            update(dt) {
                // Apply physics
                this.vx *= this.friction;
                this.vy *= this.friction;
                this.vy += this.gravity * dt;

                this.x += this.vx * dt;
                this.y += this.vy * dt;

                // Decrease lifespan
                this.life -= this.decay * dt;
            }

            draw(ctx) {
                if (this.life <= 0) return;

                ctx.save();
                ctx.globalAlpha = this.life; // Fade out
                ctx.fillStyle = this.color;
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                ctx.fill();
                
                // Add a small trail effect
                ctx.fillStyle = 'rgba(255, 255, 0, 0.5)';
                ctx.fillRect(this.x - this.size/2, this.y - this.size/2, this.size, this.size);
                
                ctx.restore();
            }

            isDead() {
                return this.life <= 0;
            }
        }

        /**
         * SIMULATION MANAGER
         */
        const canvas = document.getElementById('simulationCanvas');
        const ctx = canvas.getContext('2d');

        let simulationState = STATE.RUNNING;
        let vehicles = [];
        let explosionParticles = [];
        let collisionPoint = { x: 0, y: 0 };
        
        // Timing
        let lastTime = 0;
        let explosionStartTime = 0;
        let restartTimer = 0;

        // Initialization
        function initVehicles() {
            vehicles = [];
            for (let i = 0; i < VEHICLE_COUNT; i++) {
                // Ensure vehicles spawn away from edges slightly
                const x = randomRange(VEHICLE_SIZE, CANVAS_WIDTH - VEHICLE_SIZE);
                const y = randomRange(VEHICLE_SIZE, CANVAS_HEIGHT - VEHICLE_SIZE);
                vehicles.push(new Vehicle(x, y));
            }
        }

        function triggerExplosion(v1, v2) {
            simulationState = STATE.EXPLODING;
            
            // Calculate average collision point
            collisionPoint.x = (v1.x + v2.x) / 2;
            collisionPoint.y = (v1.y + v2.y) / 2;

            // Deactivate vehicles
            v1.isActive = false;
            v2.isActive = false;

            // Create explosion particles
            explosionParticles = [];
            const colors = ['#FFD700', '#FF4500', '#FF6347', '#808080', '#FFFFFF'];
            
            for (let i = 0; i < EXPLOSION_PARTICLE_COUNT; i++) {
                const color = colors[Math.floor(Math.random() * colors.length)];
                explosionParticles.push(new ExplosionParticle(collisionPoint.x, collisionPoint.y, color));
            }

            explosionStartTime = Date.now();
        }

        function checkCollisions() {
            // Simple O(N^2) check, acceptable for < 50 objects
            for (let i = 0; i < vehicles.length; i++) {
                const v1 = vehicles[i];
                if (!v1.isActive) continue;

                for (let j = i + 1; j < vehicles.length; j++) {
                    const v2 = vehicles[j];
                    if (!v2.isActive) continue;

                    // Distance check (Circle collision)
                    const dx = v1.x - v2.x;
                    const dy = v1.y - v2.y;
                    const distance = Math.sqrt(dx * dx + dy * dy);
                    const minDistance = v1.radius + v2.radius;

                    if (distance < minDistance) {
                        triggerExplosion(v1, v2);
                        return; // Only handle one collision per frame to prevent complex chain reactions
                    }
                }
            }
        }

        // Drawing Helpers
        function drawBoomText(x, y, timeSinceExplosion) {
            // Calculate scale factor: starts big, shrinks to normal
            const progress = timeSinceExplosion / 1.0; // 1 second to disappear
            let scale = 1 + (3 * (1 - progress)); // Start at 4x size
            if (scale < 1) scale = 1;

            const alpha = 1 - progress;
            if (alpha <= 0) return;

            ctx.save();
            ctx.translate(x, y);
            ctx.scale(scale, scale);
            ctx.globalAlpha = alpha;
            
            ctx.fillStyle = '#FFF';
            ctx.font = 'bold 80px Arial';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.shadowColor = 'red';
            ctx.shadowBlur = 20;
            ctx.fillText('BOOM!', 0, 0);
            
            ctx.restore();
        }

        // Main Loop
        function loop(timestamp) {
            // Calculate Delta Time (in seconds)
            if (!lastTime) lastTime = timestamp;
            const dt = (timestamp - lastTime) / 1000;
            lastTime = timestamp;

            // 1. Clear Canvas
            ctx.fillStyle = '#000000';
            ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);

            // 2. State Management
            if (simulationState === STATE.RUNNING) {
                // Update & Draw Vehicles
                vehicles.forEach(v => {
                    v.update(dt);
                    v.draw(ctx);
                });

                // Check for collisions
                checkCollisions();

            } else if (simulationState === STATE.EXPLODING) {
                const timeSinceExplosion = (Date.now() - explosionStartTime) / 1000;

                // Update & Draw Particles
                explosionParticles.forEach(p => {
                    p.update(dt);
                    p.draw(ctx);
                });

                // Draw BOOM Text (only for first 1 second)
                if (timeSinceExplosion < 1.0) {
                    drawBoomText(collisionPoint.x, collisionPoint.y, timeSinceExplosion);
                }

                // Check if explosion is finished
                const allDead = explosionParticles.every(p => p.isDead());
                if (allDead && timeSinceExplosion > 1.0) {
                    simulationState = STATE.RESTARTING;
                    restartTimer = 0;
                }

            } else if (simulationState === STATE.RESTARTING) {
                // Wait for delay
                restartTimer += dt;
                if (restartTimer >= RESTART_DELAY) {
                    initVehicles();
                    simulationState = STATE.RUNNING;
                } else {
                    // While waiting, show a "Resetting..." message or just black screen
                    ctx.fillStyle = 'rgba(255, 255, 255, 0.5)';
                    ctx.font = '20px Arial';
                    ctx.textAlign = 'center';
                    ctx.fillText('Resetting Simulation...', CANVAS_WIDTH/2, CANVAS_HEIGHT/2);
                }
            }

            requestAnimationFrame(loop);
        }

        // Start the simulation
        initVehicles();
        requestAnimationFrame(loop);

    </script>
</body>
</html>
```

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: Qwen3-Coder-Next-UD-Q3_K_XL.gguf -->
<!-- Prompt: vehicles.md -->
<!-- Time: 42.43s -->
<!-- Fallback: False -->