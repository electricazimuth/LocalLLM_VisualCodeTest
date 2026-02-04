Here is the complete solution contained within a single HTML file. The code implements a robust state machine, object-oriented vehicle and particle management, and a smooth animation loop using delta time.

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
            color: white;
        }
        canvas { 
            display: block; 
            border: 2px solid #666; 
            background-color: #000; 
            box-shadow: 0 0 20px rgba(0,0,0,0.5);
        }
        #ui-layer {
            margin-top: 10px;
            text-align: center;
            pointer-events: none;
        }
        .state-text {
            font-size: 1.2rem;
            font-weight: bold;
            text-transform: uppercase;
            opacity: 0.8;
        }
        .instructions {
            font-size: 0.9rem;
            color: #aaa;
            margin-top: 5px;
        }
    </style>
</head>
<body>
    <canvas id="simulationCanvas" width="800" height="600"></canvas>
    
    <div id="ui-layer">
        <div class="state-text" id="stateDisplay">State: INITIALIZING</div>
        <div class="instructions">Simulation runs autonomously. Collisions trigger explosions and resets.</div>
    </div>

    <section id="notes" style="display: none;">
        <h3>Implementation Notes</h3>
        <ul>
            <li><strong>State Machine:</strong> The simulation uses a simple state machine (`RUNNING`, `EXPLODING`, `RESTARTING`) to control the flow of updates and rendering.</li>
            <li><strong>Object Pooling/Management:</strong> Arrays are used for `vehicles` and `particles`. Objects are removed from arrays when they become inactive to prevent memory leaks and improve performance.</li>
            <li><strong>Collision Detection:</strong> Uses a Circle-Circle distance check (Euclidean distance) which is more suitable for rotating or organic movement than AABB (Axis-Aligned Bounding Box).</li>
            <li><strong>Delta Time:</strong> Movement calculations are multiplied by `dt` (delta time in seconds) to ensure the simulation runs at the same speed regardless of the monitor's refresh rate.</li>
            <li><strong>Visuals:</strong> Vehicles are drawn using composite canvas paths. Explosion particles use `globalCompositeOperation = 'lighter'` to create a glowing effect when particles overlap.</li>
        </ul>
    </section>

    <script>
        // --- CONFIGURATION & CONSTANTS ---
        const CONFIG = {
            vehicleCount: 8,
            vehicleSpeedMin: 100, // pixels per second
            vehicleSpeedMax: 250,
            vehicleRadius: 20,
            particleCount: 40,
            particleSpeed: 150,
            particleLife: 1.5, // seconds
            explosionDuration: 0.5, // time particles exist after collision
            restartDelay: 2.5, // seconds before new vehicles spawn
            canvasWidth: 800,
            canvasHeight: 600
        };

        const STATE = {
            RUNNING: 'RUNNING',
            EXPLODING: 'EXPLODING',
            RESTARTING: 'RESTARTING'
        };

        // --- CLASSES ---

        class Vehicle {
            constructor(x, y, canvasWidth, canvasHeight) {
                this.x = x;
                this.y = y;
                this.radius = CONFIG.vehicleRadius;
                this.canvasWidth = canvasWidth;
                this.canvasHeight = canvasHeight;
                
                // Random velocity
                const angle = Math.random() * Math.PI * 2;
                const speed = CONFIG.vehicleSpeedMin + Math.random() * (CONFIG.vehicleSpeedMax - CONFIG.vehicleSpeedMin);
                this.vx = Math.cos(angle) * speed;
                this.vy = Math.sin(angle) * speed;

                // Visual properties
                this.colors = ['#FF5733', '#33FF57', '#3357FF', '#F333FF', '#FF33A8'];
                this.color = this.colors[Math.floor(Math.random() * this.colors.length)];
                this.rotation = angle;
                this.isActive = true;
            }

            update(dt) {
                if (!this.isActive) return;

                // Move
                this.x += this.vx * dt;
                this.y += this.vy * dt;

                // Update rotation based on velocity
                this.rotation = Math.atan2(this.vy, this.vx);

                // Wrap Logic
                if (this.x < -this.radius) this.x = this.canvasWidth + this.radius;
                if (this.x > this.canvasWidth + this.radius) this.x = -this.radius;
                if (this.y < -this.radius) this.y = this.canvasHeight + this.radius;
                if (this.y > this.canvasHeight + this.radius) this.y = -this.radius;
            }

            draw(ctx) {
                if (!this.isActive) return;

                ctx.save();
                ctx.translate(this.x, this.y);
                ctx.rotate(this.rotation);

                // Body
                ctx.fillStyle = this.color;
                ctx.shadowBlur = 10;
                ctx.shadowColor = this.color;
                ctx.fillRect(-this.radius, -this.radius / 1.5, this.radius * 2, this.radius * 4/3);

                // Windshield
                ctx.fillStyle = '#333'; // Dark glass
                ctx.fillRect(0, -this.radius / 2, this.radius / 2, this.radius * 2/3);

                // Headlights
                ctx.fillStyle = '#FFFF00'; // Yellow lights
                ctx.shadowBlur = 5;
                ctx.shadowColor = '#FFFF00';
                ctx.beginPath();
                ctx.arc(this.radius, -this.radius / 2, 3, 0, Math.PI * 2);
                ctx.arc(this.radius, this.radius / 2, 3, 0, Math.PI * 2);
                ctx.fill();

                // Wheels
                ctx.fillStyle = '#000';
                ctx.shadowBlur = 0;
                ctx.fillRect(-this.radius - 2, -this.radius, 4, this.radius / 1.5); // Front Left
                ctx.fillRect(this.radius - 2, -this.radius, 4, this.radius / 1.5);  // Front Right
                ctx.fillRect(-this.radius - 2, this.radius/3, 4, this.radius / 1.5); // Back Left
                ctx.fillRect(this.radius - 2, this.radius/3, 4, this.radius / 1.5);   // Back Right

                ctx.restore();
            }

            // Check collision with another vehicle (Circle-Circle)
            checkCollision(other) {
                if (!this.isActive || !other.isActive) return false;
                
                const dx = this.x - other.x;
                const dy = this.y - other.y;
                const distance = Math.sqrt(dx * dx + dy * dy);
                return distance < (this.radius + other.radius);
            }
        }

        class ExplosionParticle {
            constructor(x, y, color) {
                this.x = x;
                this.y = y;
                this.color = color;
                
                // Random direction
                const angle = Math.random() * Math.PI * 2;
                const speed = Math.random() * CONFIG.particleSpeed;
                
                this.vx = Math.cos(angle) * speed;
                this.vy = Math.sin(angle) * speed;
                
                this.life = CONFIG.particleLife; // Start full life
                this.maxLife = CONFIG.particleLife;
                this.size = Math.random() * 5 + 2;
                this.decay = Math.random() * 0.5 + 0.5; // How fast it fades
                this.isActive = true;
            }

            update(dt) {
                if (!this.isActive) return;

                // Move
                this.x += this.vx * dt;
                this.y += this.vy * dt;

                // Shrink and Fade
                this.life -= dt;
                if (this.life <= 0) {
                    this.life = 0;
                    this.isActive = false;
                }
            }

            draw(ctx) {
                if (!this.isActive) return;

                const alpha = this.life / this.maxLife;
                ctx.globalAlpha = alpha;
                ctx.fillStyle = this.color;
                
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                ctx.fill();
                
                // Reset alpha for other drawings
                ctx.globalAlpha = 1.0;
            }
        }

        // --- SIMULATION MANAGER ---

        const canvas = document.getElementById('simulationCanvas');
        const ctx = canvas.getContext('2d');
        const stateDisplay = document.getElementById('stateDisplay');

        // Global State
        let currentState = STATE.RUNNING;
        let vehicles = [];
        let explosionParticles = [];
        let explosionOrigin = { x: 0, y: 0 };
        let timeSinceExplosion = 0;
        let timeSinceRestart = 0;
        let lastTime = 0;
        let boomTextAlpha = 0;

        function initVehicles() {
            vehicles = [];
            for (let i = 0; i < CONFIG.vehicleCount; i++) {
                // Ensure vehicles don't spawn on top of each other
                let x, y, tooClose;
                let attempts = 0;
                do {
                    tooClose = false;
                    x = Math.random() * (CONFIG.canvasWidth - 100) + 50;
                    y = Math.random() * (CONFIG.canvasHeight - 100) + 50;

                    for (let v of vehicles) {
                        const dist = Math.hypot(x - v.x, y - v.y);
                        if (dist < CONFIG.vehicleRadius * 3) {
                            tooClose = true;
                            break;
                        }
                    }
                    attempts++;
                } while (tooClose && attempts < 50);

                vehicles.push(new Vehicle(x, y, CONFIG.canvasWidth, CONFIG.canvasHeight));
            }
        }

        function createExplosion(x, y, colorSource) {
            currentState = STATE.EXPLODING;
            explosionOrigin.x = x;
            explosionOrigin.y = y;
            timeSinceExplosion = 0;
            boomTextAlpha = 1.0;

            // Create particles
            const colors = ['#FFD700', '#FF4500', '#FFFFFF', '#8B4513']; // Gold, Orange, White, Brown
            for (let i = 0; i < CONFIG.particleCount; i++) {
                const randomColor = colors[Math.floor(Math.random() * colors.length)];
                explosionParticles.push(new ExplosionParticle(x, y, randomColor));
            }
        }

        function resetSimulation() {
            currentState = STATE.RESTARTING;
            vehicles = [];
            explosionParticles = [];
            timeSinceRestart = 0;
            stateDisplay.innerText = "State: RESTARTING (Preparing new vehicles...)";
            
            // Clear canvas for clean look during reset
            ctx.fillStyle = '#000';
            ctx.fillRect(0, 0, CONFIG.canvasWidth, CONFIG.canvasHeight);
        }

        // --- MAIN LOOP ---

        function gameLoop(timestamp) {
            // Calculate Delta Time (in seconds)
            if (!lastTime) lastTime = timestamp;
            const dt = (timestamp - lastTime) / 1000;
            lastTime = timestamp;

            // Cap dt to prevent huge jumps if tab is inactive
            const safeDt = Math.min(dt, 0.1);

            // 1. Update Logic based on State
            if (currentState === STATE.RUNNING) {
                stateDisplay.innerText = "State: RUNNING";
                
                // Update Vehicles
                let collisionOccurred = false;
                
                // Check collisions (O(N^2) - acceptable for N < 50)
                for (let i = 0; i < vehicles.length; i++) {
                    vehicles[i].update(safeDt);
                    
                    for (let j = i + 1; j < vehicles.length; j++) {
                        if (vehicles[i].checkCollision(vehicles[j])) {
                            collisionOccurred = true;
                            // Calculate midpoint for explosion
                            const midX = (vehicles[i].x + vehicles[j].x) / 2;
                            const midY = (vehicles[i].y + vehicles[j].y) / 2;
                            
                            // Mark vehicles as inactive (they will disappear on next draw)
                            vehicles[i].isActive = false;
                            vehicles[j].isActive = false;
                            
                            createExplosion(midX, midY);
                            break; // Handle one collision per vehicle pair logic
                        }
                    }
                    if (collisionOccurred) break;
                }

            } else if (currentState === STATE.EXPLODING) {
                stateDisplay.innerText = "State: EXPLODING";
                timeSinceExplosion += safeDt;
                
                // Update Particles
                explosionParticles.forEach(p => p.update(safeDt));

                // Fade out BOOM text
                if (boomTextAlpha > 0) {
                    boomTextAlpha -= safeDt * 1.5; // Fade speed
                    if (boomTextAlpha < 0) boomTextAlpha = 0;
                }

                // Check if explosion is done
                const allDead = explosionParticles.every(p => !p.isActive);
                if (timeSinceExplosion > 1.0 && allDead) { // 1.0 second buffer after last particle dies
                    resetSimulation();
                }

            } else if (currentState === STATE.RESTARTING) {
                stateDisplay.innerText = "State: RESTARTING";
                timeSinceRestart += safeDt;
                
                if (timeSinceRestart >= CONFIG.restartDelay) {
                    initVehicles();
                    currentState = STATE.RUNNING;
                    lastTime = timestamp; // Reset time base to prevent huge dt jump
                }
            }

            // 2. Draw Logic
            ctx.clearRect(0, 0, CONFIG.canvasWidth, CONFIG.canvasHeight);

            // Draw Background Grid (Optional visual flair)
            ctx.strokeStyle = '#1a1a1a';
            ctx.lineWidth = 1;
            ctx.beginPath();
            for(let x=0; x<CONFIG.canvasWidth; x+=50) { ctx.moveTo(x,0); ctx.lineTo(x,CONFIG.canvasHeight); }
            for(let y=0; y<CONFIG.canvasHeight; y+=50) { ctx.moveTo(0,y); ctx.lineTo(CONFIG.canvasWidth,y); }
            ctx.stroke();

            if (currentState === STATE.RUNNING) {
                vehicles.forEach(v => v.draw(ctx));

            } else if (currentState === STATE.EXPLODING) {
                // Draw Explosion Particles
                ctx.globalCompositeOperation = 'lighter'; // Additive blending for glow
                explosionParticles.forEach(p => p.draw(ctx));
                ctx.globalCompositeOperation = 'source-over'; // Reset to default

                // Draw BOOM Text
                if (boomTextAlpha > 0) {
                    ctx.save();
                    ctx.fillStyle = `rgba(255, 255, 255, ${boomTextAlpha})`;
                    ctx.font = "bold 100px Arial";
                    ctx.textAlign = "center";
                    ctx.textBaseline = "middle";
                    // Pulsing effect
                    const scale = 1 + Math.sin(timeSinceExplosion * 10) * 0.1;
                    ctx.translate(explosionOrigin.x, explosionOrigin.y);
                    ctx.scale(scale, scale);
                    ctx.fillText("BOOM!", 0, 0);
                    ctx.restore();
                }
            }

            requestAnimationFrame(gameLoop);
        }

        // --- INITIALIZATION ---
        initVehicles();
        requestAnimationFrame(gameLoop);

    </script>
</body>
</html>
```

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: Qwen3-Coder-Next-UD-Q4_K_XL.gguf -->
<!-- Prompt: vehicles.md -->
<!-- Time: 56.83s -->
<!-- Fallback: False -->