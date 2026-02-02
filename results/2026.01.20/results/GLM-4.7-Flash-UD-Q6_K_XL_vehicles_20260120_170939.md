Here is the complete, self-contained HTML file implementing the Vehicle Collision & Restart Simulation according to your specifications.

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vehicle Collision Simulation</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            background-color: #1a1a1a; /* Dark background */
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            overflow: hidden;
            font-family: 'Courier New', Courier, monospace; /* Retro simulation feel */
            color: white;
        }

        canvas {
            background-color: #000;
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.5);
            border: 2px solid #444;
        }

        .ui-layer {
            position: absolute;
            top: 20px;
            left: 20px;
            pointer-events: none;
        }

        h1 {
            font-size: 1.2rem;
            margin: 0 0 5px 0;
            color: #ddd;
            text-transform: uppercase;
            letter-spacing: 2px;
        }

        p {
            font-size: 0.8rem;
            color: #888;
            margin: 0;
        }
    </style>
</head>
<body>

    <div class="ui-layer">
        <h1>Collision Sim</h1>
        <p>Observe: Wrap-around &middot; Collision &middot; Explosion</p>
    </div>

    <canvas id="simulationCanvas" width="800" height="600"></canvas>

    <script>
        /**
         * CONFIGURATION & CONSTANTS
         */
        const CONFIG = {
            vehicleCount: 6,
            vehicleSpeedMin: 100, // Pixels per second
            vehicleSpeedMax: 250,
            vehicleRadius: 20,
            explosionParticles: 25,
            explosionDuration: 2.0, // Seconds
            restartDelay: 1.0, // Seconds
            colors: ['#FF5733', '#33FF57', '#3357FF', '#F333FF', '#33FFF5', '#FFFF33']
        };

        // Canvas Setup
        const canvas = document.getElementById('simulationCanvas');
        const ctx = canvas.getContext('2d');
        let width, height;

        // Helper: Random integer
        const randomInt = (min, max) => Math.floor(Math.random() * (max - min + 1) + min);
        
        // Helper: Random float
        const randomFloat = (min, max) => Math.random() * (max - min) + min;

        // Helper: Random Color
        const randomColor = () => CONFIG.colors[Math.floor(Math.random() * CONFIG.colors.length)];

        // Global State
        let lastTime = 0;
        let simulationState = 'RUNNING'; // 'RUNNING', 'EXPLODING', 'RESTARTING'
        let vehicles = [];
        let particles = [];
        let collisionCooldown = false; // To prevent multi-collision triggers

        /**
         * CLASSES
         */

        class Vehicle {
            constructor() {
                this.radius = CONFIG.vehicleRadius;
                this.color = randomColor();
                this.setRandomPosition();
                this.angle = Math.random() * Math.PI * 2; // Orientation
                
                // Random velocity vector
                const speed = randomInt(CONFIG.vehicleSpeedMin, CONFIG.vehicleSpeedMax) * (Math.PI / 180); // Rads
                this.velocity = {
                    x: Math.cos(this.angle) * randomFloat(CONFIG.vehicleSpeedMin, CONFIG.vehicleSpeedMax) * 0.1,
                    y: Math.sin(this.angle) * randomFloat(CONFIG.vehicleSpeedMin, CONFIG.vehicleSpeedMax) * 0.1
                };
                
                // Make speed uniform in all directions for wrapping consistency
                const mag = Math.sqrt(this.velocity.x**2 + this.velocity.y**2);
                this.velocity.x = (this.velocity.x / mag) * randomFloat(CONFIG.vehicleSpeedMin, CONFIG.vehicleSpeedMax);
                this.velocity.y = (this.velocity.y / mag) * randomFloat(CONFIG.vehicleSpeedMin, CONFIG.vehicleSpeedMax);

                this.markedForDeletion = false;
            }

            setRandomPosition() {
                this.x = randomInt(this.radius, width - this.radius);
                this.y = randomInt(this.radius, height - this.radius);
            }

            update(dt) {
                // Move
                this.x += this.velocity.x;
                this.y += this.velocity.y;

                // Wrap horizontal
                if (this.x - this.radius > width) {
                    this.x = -this.radius;
                } else if (this.x + this.radius < 0) {
                    this.x = width + this.radius;
                }

                // Wrap vertical
                if (this.y - this.radius > height) {
                    this.y = -this.radius;
                } else if (this.y + this.radius < 0) {
                    this.y = height + this.radius;
                }
            }

            draw() {
                ctx.save();
                ctx.translate(this.x, this.y);
                
                // Draw body (simple car shape)
                ctx.fillStyle = this.color;
                // Simple rounded rect car body
                this.roundRect(0, -15, 40, 30, 5);
                ctx.fill();

                // Windshield
                ctx.fillStyle = '#333';
                this.roundRect(10, -10, 15, 10, 2);
                ctx.fill();

                // Wheels
                ctx.fillStyle = '#000';
                ctx.fillRect(-10, -15, 6, 12); // Rear Left
                ctx.fillRect(4, -15, 6, 12);  // Rear Right
                ctx.fillRect(-10, 11, 6, 12);  // Front Left
                ctx.fillRect(4, 11, 6, 12);   // Front Right

                ctx.restore();
            }

            // Helper for rounded rect drawing
            roundRect(x, y, w, h, r) {
                if (w < 2 * r) r = w / 2;
                if (h < 2 * r) r = h / 2;
                this.ctx.beginPath();
                this.ctx.moveTo(x + r, y);
                this.ctx.arcTo(x + w, y, x + w, y + h, r);
                this.ctx.arcTo(x + w, y + h, x, y + h, r);
                this.ctx.arcTo(x, y + h, x, y, r);
                this.ctx.arcTo(x, y, x + w, y, r);
                this.ctx.closePath();
            }
        }

        class Particle {
            constructor(x, y) {
                this.x = x;
                this.y = y;
                this.radius = Math.random() * 3 + 1;
                // Explosion velocity
                const angle = Math.random() * Math.PI * 2;
                const speed = Math.random() * 5 + 2;
                this.velocity = {
                    x: Math.cos(angle) * speed,
                    y: Math.sin(angle) * speed
                };
                this.alpha = 1;
                this.decay = Math.random() * 0.02 + 0.01;
                this.color = `hsl(${Math.random() * 60 + 10}, 100%, 50%)`; // Orange/Yellow fire colors
            }

            update() {
                this.velocity.x *= 0.95; // Friction
                this.velocity.y *= 0.95;
                this.x += this.velocity.x;
                this.y += this.velocity.y;
                this.alpha -= this.decay;
            }

            draw() {
                ctx.save();
                ctx.globalAlpha = this.alpha;
                ctx.fillStyle = this.color;
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
                ctx.fill();
                ctx.restore();
            }
        }

        // Explosion "Text" object
        const boomText = {
            alpha: 1,
            scale: 0.5,
            active: false,
            update() {
                if (this.active) {
                    this.scale += 0.005; // Slowly grow
                    this.alpha -= 0.015; // Fade out
                    
                    // Bounce effect
                    if (this.alpha <= 0) {
                        this.alpha = 0;
                        this.active = false;
                        // Trigger restart logic
                        setTimeout(resetSimulation, 500); // Small delay after text finishes
                    }
                }
            },
            draw() {
                if (!this.active) return;

                ctx.save();
                ctx.translate(width / 2, height / 2);
                ctx.scale(this.scale, this.scale);
                ctx.font = "bold 80px 'Courier New'";
                ctx.textAlign = "center";
                ctx.textBaseline = "middle";
                
                // Text Shadow/Glow
                ctx.shadowColor = "rgba(255, 0, 0, 0.8)";
                ctx.shadowBlur = 20;
                
                ctx.fillStyle = `rgba(255, 50, 50, ${this.alpha})`;
                ctx.fillText("BOOM!", 0, 0);
                
                ctx.restore();
            }
        };

        /**
         * CORE LOGIC
         */

        function init() {
            // Set canvas size to fill window, but keep logical size 800x600 if desired, 
            // or just fill. Let's fill window for immersion but keep aspect ratio logic simple.
            width = canvas.width;
            height = canvas.height;
            
            spawnVehicles();
            requestAnimationFrame(gameLoop);
        }

        function spawnVehicles() {
            vehicles = [];
            for (let i = 0; i < CONFIG.vehicleCount; i++) {
                vehicles.push(new Vehicle());
            }
        }

        function checkCollisions() {
            for (let i = 0; i < vehicles.length; i++) {
                for (let j = i + 1; j < vehicles.length; j++) {
                    const v1 = vehicles[i];
                    const v2 = vehicles[j];

                    if (v1.markedForDeletion || v2.markedForDeletion) continue;

                    // Simple Circle-Circle Collision Detection
                    const dx = v1.x - v2.x;
                    const dy = v1.y - v2.y;
                    const distance = Math.sqrt(dx * dx + dy * dy);

                    if (distance < v1.radius + v2.radius) {
                        handleCollision(v1, v2, dx, dy + distance);
                    }
                }
            }
        }

        function handleCollision(v1, v2, dx, dy) {
            // Mark vehicles as inactive to stop moving and drawing
            v1.markedForDeletion = true;
            v2.markedForDeletion = true;

            // Calculate collision point (midpoint)
            const midX = (v1.x + v2.x) / 2;
            const midY = (v1.y + v2.y) / 2;

            // Spawn Particles
            for (let i = 0; i < CONFIG.explosionParticles; i++) {
                particles.push(new Particle(midX, midY));
            }

            // Set State
            simulationState = 'EXPLODING';
            boomText.active = true;
        }

        function resetSimulation() {
            simulationState = 'RESTARTING';
            // Clear particles for the next explosion
            particles = [];
            
            // Short delay before respawning to make it clean
            setTimeout(() => {
                spawnVehicles();
                simulationState = 'RUNNING';
            }, 100);
        }

        function gameLoop(timestamp) {
            const dt = (timestamp - lastTime) / 1000 || 0.016;
            lastTime = timestamp;

            // Clear Canvas
            ctx.fillStyle = 'rgba(0, 0, 0, 1)'; // Opaque clear
            ctx.clearRect(0, 0, width, height);

            // Draw Grid (Optional background detail)
            drawGrid();

            if (simulationState === 'RUNNING') {
                // Update Vehicles
                let activeCount = 0;
                vehicles.forEach(v => {
                    if(!v.markedForDeletion) {
                        v.update(dt);
                        v.draw();
                        activeCount++;
                    }
                });

                // Check for collisions
                if (activeCount > 0) {
                    checkCollisions();
                } else {
                    // If all cars somehow deleted (shouldn't happen with wrapping), respawn
                    if(activeCount === 0) spawnVehicles();
                }

            } else if (simulationState === 'EXPLODING') {
                // Draw Explosion Particles
                for (let i = particles.length - 1; i >= 0; i--) {
                    particles[i].update();
                    particles[i].draw();
                    if (particles[i].alpha <= 0) {
                        particles.splice(i, 1);
                    }
                }
            }

            // Always draw Boom Text (handles its own alpha lifecycle)
            boomText.update();
            boomText.draw();

            requestAnimationFrame(gameLoop);
        }

        function drawGrid() {
            ctx.strokeStyle = '#222';
            ctx.lineWidth = 1;
            const gridSize = 50;
            
            for (let x = 0; x < width; x += gridSize) {
                ctx.beginPath();
                ctx.moveTo(x, 0);
                ctx.lineTo(x, height);
                ctx.stroke();
            }
            for (let y = 0; y < height; y += gridSize) {
                ctx.beginPath();
                ctx.moveTo(0, y);
                ctx.lineTo(width, y);
                ctx.stroke();
            }
        }

        // Handle Window Resize (Optional: keeps canvas sharp)
        window.addEventListener('resize', () => {
            // In a real app, we might adjust width/height here
        });

        // Start
        init();

    </script>
</body>
</html>
```

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: GLM-4.7-Flash-UD-Q6_K_XL.gguf -->
<!-- Prompt: vehicles.md -->
<!-- Generation Time: 258.96s -->
<!-- Fallback Used: False -->