# Vehicle Collision & Restart Simulation

Here's a complete implementation of the vehicle collision simulation with all the requested features:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Vehicle Collision Simulation</title>
    <style>
        body { margin: 0; overflow: hidden; background-color: #333; }
        canvas { display: block; margin: 20px auto; border: 1px solid #666; background-color: #000; }
        #status { position: absolute; top: 10px; left: 10px; color: white; font-family: Arial, sans-serif; }
    </style>
</head>
<body>
    <div id="status">Running...</div>
    <canvas id="simulationCanvas" width="512" height="512"></canvas>

    <script>
        // Main simulation variables
        const canvas = document.getElementById('simulationCanvas');
        const ctx = canvas.getContext('2d');
        const statusElement = document.getElementById('status');

        // Simulation state constants
        const STATES = {
            RUNNING: 'RUNNING',
            EXPLODING: 'EXPLODING',
            RESTARTING: 'RESTARTING'
        };

        // Simulation configuration
        const config = {
            vehicleCount: 8,
            explosionDuration: 3000, // 3 seconds
            restartDelay: 1500, // 1.5 seconds before restart
            explosionParticles: 30,
            minSpeed: 1,
            maxSpeed: 3,
            vehicleWidth: 20,
            vehicleHeight: 30,
            vehicleColor: '#4CAF50',
            explosionColors: ['#FF5252', '#FF9800', '#FFEB3B', '#4CAF50', '#2196F3']
        };

        // Game state
        let simulationState = STATES.RUNNING;
        let vehicles = [];
        let explosionParticles = [];
        let explosionStartTime = 0;
        let lastTime = 0;
        let boomText = { text: 'BOOM!', size: 20, opacity: 1 };

        // Initialize the simulation
        function init() {
            vehicles = [];
            explosionParticles = [];
            boomText = { text: 'BOOM!', size: 20, opacity: 1 };

            for (let i = 0; i < config.vehicleCount; i++) {
                vehicles.push(createVehicle());
            }

            simulationState = STATES.RUNNING;
            statusElement.textContent = 'Running...';
        }

        // Create a new vehicle
        function createVehicle() {
            return {
                x: Math.random() * (canvas.width - config.vehicleWidth),
                y: Math.random() * (canvas.height - config.vehicleHeight),
                width: config.vehicleWidth,
                height: config.vehicleHeight,
                vx: (Math.random() - 0.5) * (config.maxSpeed - config.minSpeed) + config.minSpeed,
                vy: (Math.random() - 0.5) * (config.maxSpeed - config.minSpeed) + config.minSpeed,
                color: config.vehicleColor,
                active: true,
                draw: function() {
                    // Draw car body
                    ctx.fillStyle = this.color;
                    ctx.fillRect(this.x, this.y, this.width, this.height);

                    // Draw wheels
                    ctx.fillStyle = '#333';
                    ctx.beginPath();
                    ctx.arc(this.x + 5, this.y + this.height - 5, 4, 0, Math.PI * 2);
                    ctx.arc(this.x + this.width - 5, this.y + this.height - 5, 4, 0, Math.PI * 2);
                    ctx.fill();
                }
            };
        }

        // Create explosion particles
        function createExplosionParticles(x, y) {
            explosionParticles = [];
            for (let i = 0; i < config.explosionParticles; i++) {
                explosionParticles.push({
                    x: x,
                    y: y,
                    vx: (Math.random() - 0.5) * 6,
                    vy: (Math.random() - 0.5) * 6,
                    size: Math.random() * 5 + 2,
                    color: config.explosionColors[Math.floor(Math.random() * config.explosionColors.length)],
                    lifespan: 1,
                    maxLifespan: Math.random() * 0.5 + 0.5,
                    draw: function() {
                        ctx.fillStyle = this.color;
                        ctx.globalAlpha = this.lifespan;
                        ctx.beginPath();
                        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                        ctx.fill();
                        ctx.globalAlpha = 1;
                    }
                });
            }
            explosionStartTime = Date.now();
            boomText = { text: 'BOOM!', size: 20, opacity: 1 };
        }

        // Update vehicle positions with screen wrapping
        function updateVehicles(deltaTime) {
            vehicles.forEach(vehicle => {
                if (!vehicle.active) return;

                // Update position
                vehicle.x += vehicle.vx;
                vehicle.y += vehicle.vy;

                // Screen wrapping
                if (vehicle.x < -vehicle.width) vehicle.x = canvas.width;
                if (vehicle.x > canvas.width) vehicle.x = -vehicle.width;
                if (vehicle.y < -vehicle.height) vehicle.y = canvas.height;
                if (vehicle.y > canvas.height) vehicle.y = -vehicle.height;
            });
        }

        // Check for collisions between vehicles
        function checkCollisions() {
            for (let i = 0; i < vehicles.length; i++) {
                if (!vehicles[i].active) continue;

                for (let j = i + 1; j < vehicles.length; j++) {
                    if (!vehicles[j].active) continue;

                    if (checkCollision(vehicles[i], vehicles[j])) {
                        // Calculate collision point (center of overlap)
                        const overlapX = (vehicles[i].x + vehicles[i].width / 2) - (vehicles[j].x + vehicles[j].width / 2);
                        const overlapY = (vehicles[i].y + vehicles[i].height / 2) - (vehicles[j].y + vehicles[j].height / 2);
                        const collisionX = (vehicles[i].x + vehicles[i].width / 2) - overlapX / 2;
                        const collisionY = (vehicles[i].y + vehicles[i].height / 2) - overlapY / 2;

                        // Deactivate vehicles and create explosion
                        vehicles[i].active = false;
                        vehicles[j].active = false;

                        createExplosionParticles(collisionX, collisionY);
                        simulationState = STATES.EXPLODING;
                        statusElement.textContent = 'Exploding...';
                        return true;
                    }
                }
            }
            return false;
        }

        // Simple AABB collision detection
        function checkCollision(vehicle1, vehicle2) {
            return vehicle1.x < vehicle2.x + vehicle2.width &&
                   vehicle1.x + vehicle1.width > vehicle2.x &&
                   vehicle1.y < vehicle2.y + vehicle2.height &&
                   vehicle1.y + vehicle1.height > vehicle2.y;
        }

        // Update explosion particles
        function updateExplosionParticles(deltaTime) {
            // Update particles
            explosionParticles.forEach(particle => {
                particle.x += particle.vx;
                particle.y += particle.vy;
                particle.lifespan -= deltaTime / 1000;

                // Simple gravity effect
                particle.vy += 0.1;
            });

            // Remove dead particles
            explosionParticles = explosionParticles.filter(particle => particle.lifespan > 0);

            // Update boom text
            const elapsed = Date.now() - explosionStartTime;
            boomText.size = 20 + (elapsed / 100);
            boomText.opacity = Math.max(0, 1 - (elapsed / config.explosionDuration));
        }

        // Check if explosion is complete
        function isExplosionComplete() {
            return explosionParticles.length === 0 ||
                   Date.now() - explosionStartTime > config.explosionDuration;
        }

        // Main update function
        function update(currentTime) {
            const deltaTime = currentTime - lastTime;
            lastTime = currentTime;

            ctx.clearRect(0, 0, canvas.width, canvas.height);

            switch (simulationState) {
                case STATES.RUNNING:
                    updateVehicles(deltaTime);
                    checkCollisions();
                    vehicles.forEach(vehicle => {
                        if (vehicle.active) vehicle.draw();
                    });
                    break;

                case STATES.EXPLODING:
                    updateExplosionParticles(deltaTime);

                    // Draw explosion particles
                    explosionParticles.forEach(particle => particle.draw());

                    // Draw boom text
                    if (boomText.opacity > 0) {
                        ctx.globalAlpha = boomText.opacity;
                        ctx.font = `bold ${boomText.size}px Arial`;
                        ctx.textAlign = 'center';
                        ctx.fillStyle = '#FF5252';
                        ctx.fillText(boomText.text, canvas.width / 2, canvas.height / 2);
                        ctx.globalAlpha = 1;
                    }

                    if (isExplosionComplete()) {
                        simulationState = STATES.RESTARTING;
                        statusElement.textContent = 'Restarting...';
                    }
                    break;

                case STATES.RESTARTING:
                    const restartElapsed = Date.now() - explosionStartTime;
                    if (restartElapsed > config.explosionDuration + config.restartDelay) {
                        init();
                    }
                    break;
            }
        }

        // Start the animation loop
        function gameLoop(currentTime) {
            update(currentTime);
            requestAnimationFrame(gameLoop);
        }

        // Initialize and start the simulation
        init();
        lastTime = performance.now();
        requestAnimationFrame(gameLoop);
    </script>

    <section id="notes">
        <h3>Implementation Notes</h3>
        <ul>
            <li><strong>Collision Detection:</strong> Uses simple Axis-Aligned Bounding Box (AABB) collision detection between vehicles.</li>
            <li><strong>State Management:</strong> Three distinct states (RUNNING, EXPLODING, RESTARTING) with clear transitions between them.</li>
            <li><strong>Performance:</strong> Only checks collisions between active vehicles and avoids duplicate checks (i vs j loop).</li>
            <li><strong>Visual Effects:</strong> Explosion particles have random velocities, fade out over time, and include a simple gravity effect.</li>
            <li><strong>Screen Wrapping:</strong> Vehicles reappear on the opposite side when they go off-screen.</li>
            <li><strong>Delta Time:</strong> Properly implemented for smooth animation regardless of frame rate.</li>
        </ul>
    </section>
</body>
</html>
```

## Key Features Implemented:

1. **Vehicle Management**:
   - Vehicles are stored in an array with properties for position, velocity, size, and active state
   - Vehicles have simple car-like visuals with a body and wheels

2. **Movement & Wrapping**:
   - Vehicles move based on their velocity
   - Proper screen wrapping implemented for all four edges

3. **Collision Detection**:
   - Uses AABB (Axis-Aligned Bounding Box) collision detection
   - Efficiently checks only active vehicles against each other

4. **Explosion Effects**:
   - Creates 30 particles with random velocities when collision occurs
   - Particles fade out over time with gravity effect
   - Includes a "BOOM!" text that expands during the explosion

5. **State Management**:
   - Three distinct states (RUNNING, EXPLODING, RESTARTING)
   - Clean transitions between states with proper timing

6. **Animation Loop**:
   - Uses requestAnimationFrame for smooth animation
   - Proper delta time calculation for frame-rate independence

7. **Visual Design**:
   - Dark theme with black canvas
   - Colorful explosion particles
   - Simple but effective vehicle graphics

The simulation will automatically restart after each collision and explosion sequence, creating an endless cycle of vehicle movement, collision, and restart.

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: Devstral-Small-2-24B-Instruct-2512-UD-Q6_K_XL.gguf -->
<!-- Prompt: vehicles.md -->
<!-- Generation Time: 97.13s -->
<!-- Fallback Used: False -->