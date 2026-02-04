Here is the complete simulation code in a single HTML file. It includes the CSS styling, the Canvas setup, and the JavaScript logic with Classes for `Vehicle` and `ExplosionParticle`, state management, and a robust game loop.

```html
<!DOCTYPE html>
<html>
<head>
    <title>Vehicle Collision Simulation</title>
    <style>
        body { 
            margin: 0; 
            overflow: hidden; 
            background-color: #333; 
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            font-family: sans-serif;
            color: #eee;
        }
        canvas { 
            display: block; 
            margin: 20px auto; 
            border: 4px solid #666; 
            background-color: #1a1a1a; 
            box-shadow: 0 0 20px rgba(0,0,0,0.5);
        }
        #status {
            margin-top: 10px;
            font-size: 1.2rem;
            font-weight: bold;
            color: #aaa;
            text-transform: uppercase;
            letter-spacing: 2px;
        }
    </style>
</head>
<body>
    <canvas id="simulationCanvas" width="640" height="480"></canvas>
    <div id="status">Simulation Running</div>

    <script>
        /**
         * Vehicle Collision & Restart Simulation
         * 
         * Implementation Notes:
         * 1. Classes: Vehicle and ExplosionParticle classes are used for encapsulation.
         * 2. State Machine: A global 'simulationState' variable controls the update/draw logic.
         * 3. Game Loop: Uses requestAnimationFrame with Date.now() delta time calculation for smooth animation regardless of frame rate.
         * 4. Collision: Uses Circle collision detection (distance < r1 + r2) for reliable collision checks.
         * 5. Wrapping: Vehicles wrap around edges using modulo arithmetic for seamless teleportation.
         * 6. Explosion: Triggered on collision, it spawns particles and text, then transitions to RESTART state after a delay.
         */

        // --- CONFIGURATION ---
        const CONFIG = {
            vehicleCount: 8,
            vehicleSizeRange: { min: 15, max: 25 },
            vehicleSpeedRange: { min: 2, max: 5 },
            explosionDuration: 1000, // How long the explosion is visible (ms)
            restartDelay: 2000,      // How long to wait after explosion before restarting (ms)
            colors: ['#FF4136', '#FF851B', '#FFDC00', '#2ECC40', '#0074D9', '#B11DCB']
        };

        // --- ENUMS ---
        const STATE = {
            RUNNING: 'RUNNING',
            EXPLODING: 'EXPLODING',
            RESTARTING: 'RESTARTING'
        };

        // --- GLOBAL VARIABLES ---
        const canvas = document.getElementById('simulationCanvas');
        const ctx = canvas.getContext('2d');
        const statusDiv = document.getElementById('status');

        let simulationState = STATE.RUNNING;
        let vehicles = [];
        let explosionParticles = [];
        let explosionStartTime = 0;
        let nextRestartTime = 0;
        let lastTime = 0;

        // --- CLASSES ---

        class Vehicle {
            constructor(x, y, radius) {
                this.x = x;
                this.y = y;
                this.radius = radius || Math.floor(Math.random() * (CONFIG.vehicleSizeRange.max - CONFIG.vehicleSizeRange.min) + CONFIG.vehicleSizeRange.min);
                this.color = CONFIG.colors[Math.floor(Math.random() * CONFIG.colors.length)];
                
                // Random Velocity
                const speed = Math.floor(Math.random() * (CONFIG.vehicleSpeedRange.max - CONFIG.vehicleSpeedRange.min) + CONFIG.vehicleSpeedRange.min);
                const angle = Math.random() * Math.PI * 2;
                this.vx = Math.cos(angle) * speed;
                this.vy = Math.sin(angle) * speed;
                
                this.isActive = true;
                this.angle = 0;
                this.rotationSpeed = (Math.random() - 0.5) * 0.1;
            }

            update(dt) {
                this.x += this.vx;
                this.y += this.vy;
                this.angle += this.rotationSpeed;

                // Screen Wrapping (Topology: Torus)
                if (this.x < -this.radius) this.x = canvas.width + this.radius;
                if (this.x > canvas.width + this.radius) this.x = -this.radius;
                if (this.y < -this.radius) this.y = canvas.height + this.radius;
                if (this.y > canvas.height + this.radius) this.y = -this.radius;
            }

            draw(ctx) {
                ctx.save();
                ctx.translate(this.x, this.y);
                ctx.rotate(this.angle);
                
                // Car Body (Rectangle)
                ctx.fillStyle = this.color;
                ctx.fillRect(-this.radius, -this.radius, this.radius * 2, this.radius * 2);

                // Windshield (Black)
                ctx.fillStyle = '#000';
                ctx.fillRect(-this.radius + 4, -this.radius + 4, this.radius * 2 - 8, this.radius / 2);

                // Wheels (Simple circles)
                ctx.fillStyle = '#333';
                ctx.beginPath();
                ctx.arc(-this.radius/2, -this.radius/2, 4, 0, Math.PI * 2); // Top Left
                ctx.fill();
                ctx.beginPath();
                ctx.arc(this.radius/2, -this.radius/2, 4, 0, Math.PI * 2); // Top Right
                ctx.fill();
                ctx.beginPath();
                ctx.arc(-this.radius/2, this.radius/2, 4, 0, Math.PI * 2); // Bottom Left
                ctx.fill();
                ctx.beginPath();
                ctx.arc(this.radius/2, this.radius/2, 4, 0, Math.PI * 2); // Bottom Right
                ctx.fill();

                ctx.restore();
            }
        }

        class ExplosionParticle {
            constructor(x, y, color) {
                this.x = x;
                this.y = y;
                this.color = color;
                this.radius = Math.random() * 4 + 2;
                const velocityMag = Math.random() * 4 + 2;
                const angle = Math.random() * Math.PI * 2;
                this.vx = Math.cos(angle) * velocityMag;
                this.vy = Math.sin(angle) * velocityMag;
                this.life = Math.random() * 60 + 60; // Frames (approx 2-4 seconds at 30fps)
                this.maxLife = this.life;
                this.gravity = 0.15;
                this.decay = Math.random() * 0.05 + 0.02;
            }

            update() {
                this.x += this.vx;
                this.y += this.vy;
                this.life -= 1;
                this.vy += this.gravity;
                this.radius = Math.max(0, this.radius - this.decay);
            }

            draw(ctx) {
                if (this.life <= 0) return;
                
                ctx.save();
                ctx.globalAlpha = this.life / this.maxLife;
                ctx.fillStyle = this.color;
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
                ctx.fill();
                ctx.restore();
            }
        }

        // --- CORE FUNCTIONS ---

        function initSimulation() {
            vehicles = [];
            explosionParticles = [];
            
            // Spawn vehicles
            for (let i = 0; i < CONFIG.vehicleCount; i++) {
                const r = Math.floor(Math.random() * (CONFIG.vehicleSizeRange.max - CONFIG.vehicleSizeRange.min) + CONFIG.vehicleSizeRange.min);
                const x = Math.random() * (canvas.width - r * 2) + r;
                const y = Math.random() * (canvas.height - r * 2) + r;
                vehicles.push(new Vehicle(x, y, r));
            }
        }

        function checkCollisions() {
            for (let i = 0; i < vehicles.length; i++) {
                // Optimization: Only check against vehicles with higher index to avoid duplicate checks
                for (let j = i + 1; j < vehicles.length; j++) {
                    const v1 = vehicles[i];
                    const v2 = vehicles[j];

                    if (!v1.isActive || !v2.isActive) continue;

                    const dx = v1.x - v2.x;
                    const dy = v1.y - v2.y;
                    const distance = Math.sqrt(dx * dx + dy * dy);

                    // Collision threshold: sum of radii
                    if (distance < (v1.radius + v2.radius)) {
                        triggerExplosion(v1.x, v1.y, [v1, v2]);
                        return true; // Collision found, stop checking
                    }
                }
            }
            return false;
        }

        function triggerExplosion(x, y, affectedVehicles) {
            // Mark vehicles as inactive so they aren't drawn in next frame (or we can just not update them)
            affectedVehicles.forEach(v => v.isActive = false);

            // Spawn explosion particles
            const colors = ['#FF4136', '#FF851B', '#FFDC00', '#FFFFFF']; // Fire colors
            for (let p = 0; p < 40; p++) {
                const color = colors[Math.floor(Math.random() * colors.length)];
                explosionParticles.push(new ExplosionParticle(x, y, color));
            }

            simulationState = STATE.EXPLODING;
            explosionStartTime = Date.now();
            statusDiv.innerText = "KABOOM!";
            statusDiv.style.color = "#FF4136";
        }

        function update(dt) {
            const now = Date.now();

            // State: Running
            if (simulationState === STATE.RUNNING) {
                // Update Vehicles
                vehicles.forEach(v => v.update(dt));

                // Check Collisions
                if (checkCollisions()) {
                    // Collision detected, trigger explosion logic
                    simulationState = STATE.EXPLODING;
                    explosionStartTime = now;
                    statusDiv.innerText = "KABOOM!";
                    statusDiv.style.color = "#FF4136";
                }
            }
            // State: Exploding (Particles only)
            else if (simulationState === STATE.EXPLODING) {
                // Update particles
                for (let i = explosionParticles.length - 1; i >= 0; i--) {
                    explosionParticles[i].update();
                    if (explosionParticles[i].life <= 0) {
                        explosionParticles.splice(i, 1);
                    }
                }

                // Check if we should restart
                if (now > explosionStartTime + CONFIG.explosionDuration && explosionParticles.length === 0) {
                    simulationState = STATE.RESTARTING;
                    nextRestartTime = now + CONFIG.restartDelay;
                    statusDiv.innerText = "Resetting...";
                    statusDiv.style.color = "#FFF";
                }
            }
            // State: Restarting (Wait for timer then reset)
            else if (simulationState === STATE.RESTARTING) {
                if (now > nextRestartTime) {
                    initSimulation();
                    simulationState = STATE.RUNNING;
                    statusDiv.innerText = "Simulation Running";
                    statusDiv.style.color = "#AAA";
                }
            }
        }

        function draw() {
            // Clear Canvas
            ctx.fillStyle = '#1a1a1a';
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            // Draw based on State
            if (simulationState === STATE.RUNNING || simulationState === STATE.RESTARTING) {
                // Draw Vehicles (that are active)
                vehicles.forEach(v => {
                    if (v.isActive) v.draw(ctx);
                });
            }

            if (simulationState === STATE.EXPLODING || simulationState === STATE.RESTARTING) {
                // Draw Particles
                // Draw "BOOM" text if particles exist or just because we are exploding
                if (explosionParticles.length > 0 || simulationState === STATE.RESTARTING) {
                    
                    // Draw Particles
                    explosionParticles.forEach(p => p.draw(ctx));

                    // Draw Text Explosion
                    if (simulationState === STATE.EXPLODING) {
                        ctx.save();
                        ctx.textAlign = "center";
                        ctx.fillStyle = "#FFDC00";
                        ctx.font = "bold 80px Arial";
                        ctx.shadowBlur = 15;
                        ctx.shadowColor = "red";
                        
                        // Pulsating text effect
                        const time = Date.now() - explosionStartTime;
                        const scale = 1 + Math.sin(time / 100) * 0.1;
                        const alpha = 1 - (time / 2000); // Fade out over 2 seconds
                        
                        ctx.globalAlpha = Math.max(0, alpha);
                        ctx.scale(scale, scale);
                        
                        ctx.fillText("BOOM!", canvas.width / 2, canvas.height / 2);
                        ctx.restore();
                    }
                }
            }
        }

        // --- MAIN LOOP ---

        function loop(timestamp) {
            const dt = timestamp - lastTime;
            lastTime = timestamp;

            update(dt);
            draw();

            requestAnimationFrame(loop);
        }

        // --- INITIALIZATION ---
        initSimulation();
        lastTime = performance.now();
        requestAnimationFrame(loop);

    </script>

    <section id="notes">
        <h4>Implementation Notes</h4>
        <ul>
            <li><strong>State Management:</strong> Uses a simple string-based state machine (<code>'RUNNING'</code>, <code>'EXPLODING'</code>, <code>'RESTARTING'</code>) to control the game flow.</li>
            <li><strong>Collision Detection:</strong> Uses Euclidean distance check between vehicle centers. This is more accurate than rectangle intersection for circular vehicles.</li>
            <li><strong>Animation Loop:</strong> Uses <code>requestAnimationFrame</code> with <code>performance.now()</code> to calculate delta time (<code>dt</code>). This ensures smooth movement regardless of screen refresh rate.</li>
            <li><strong>Explosion System:</strong> When a collision is detected, the involved vehicles are deactivated immediately. An explosion effect is spawned at the collision point. The simulation enters the <code>EXPLODING</code> state.</li>
            <li><strong>Restart Logic:</strong> After the explosion animation completes (particles fade out), the simulation enters the <code>RESTARTING</code> state for a brief pause before completely re-initializing the vehicle array.</li>
            <li><strong>Visuals:</strong> Vehicles are drawn using canvas primitives (rectangles for bodies, circles for wheels) to create a retro arcade feel.</li>
        </ul>
    </section>
</body>
</html>
```

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: Qwen3-Coder-Next-UD-IQ1_M.gguf -->
<!-- Prompt: vehicles.md -->
<!-- Time: 47.18s -->
<!-- Fallback: False -->