```html
<!DOCTYPE html>
<html>
<head>
    <title>Vehicle Collision Simulation</title>
    <style>
        body { margin: 0; overflow: hidden; background-color: #333; } /* Dark background */
        canvas { display: block; margin: 20px auto; border: 1px solid #666; background-color: #000; } /* Black canvas */
    </style>
</head>
<body>
    <canvas id="simulationCanvas" width="512" height="512"></canvas>

    <script>
        const canvas = document.getElementById('simulationCanvas');
        const ctx = canvas.getContext('2d');

        // Constants for simulation
        const NUM_VEHICLES = 5;
        const EXPLOSION_PARTICLES = 20;
        const EXPLOSION_DURATION = 3000; // ms
        const VELOCITY_RANGE = { min: 1, max: 4 };
        const PARTICLE_LIFESPAN = 1000; // ms

        // State management
        const STATES = { RUNNING: 'RUNNING', EXPLODING: 'EXPLODING', RESTARTING: 'RESTARTING' };
        let simulationState = STATES.RUNNING;

        // Vehicle and Particle classes
        class Vehicle {
            constructor(x, y, vx, vy) {
                this.x = x;
                this.y = y;
                this.vx = vx;
                this.vy = vy;
                this.width = 40;
                this.height = 20;
                this.isActive = true;
            }

            move() {
                this.x += this.vx;
                this.y += this.vy;

                // Wrap around screen
                if (this.x < 0) this.x = canvas.width;
                else if (this.x > canvas.width) this.x = 0;
                if (this.y < 0) this.y = canvas.height;
                else if (this.y > canvas.height) this.y = 0;
            }

            draw() {
                ctx.fillStyle = 'blue';
                ctx.fillRect(this.x - this.width / 2, this.y - this.height / 2, this.width, this.height);
                ctx.fillStyle = 'black';
                ctx.fillRect(this.x - this.width / 2 + 15, this.y - this.height / 2 + 5, 10, 10); // Wheel
                ctx.fillRect(this.x - this.width / 2 - 15, this.y - this.height / 2 + 5, 10, 10); // Wheel
            }
        }

        class ExplosionParticle {
            constructor(x, y, vx, vy) {
                this.x = x;
                this.y = y;
                this.vx = vx;
                this.vy = vy;
                this.size = 5;
                this.color = `hsl(${Math.random() * 360}, 100%, 50%)`;
                this.lifespan = PARTICLE_LIFESPAN;
            }

            move(deltaTime) {
                this.x += this.vx * deltaTime / 1000;
                this.y += this.vy * deltaTime / 1000;
                this.lifespan -= deltaTime;
            }

            draw() {
                ctx.fillStyle = this.color;
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                ctx.fill();
            }

            isExpired() {
                return this.lifespan <= 0;
            }
        }

        // Utility functions
        function randomInRange(min, max) {
            return Math.random() * (max - min) + min;
        }

        function detectCollision(vehicle1, vehicle2) {
            const dx = vehicle1.x - vehicle2.x;
            const dy = vehicle1.y - vehicle2.y;
            const distance = Math.sqrt(dx * dx + dy * dy);
            return distance < (vehicle1.width / 2 + vehicle2.width / 2);
        }

        // Arrays to hold objects
        let vehicles = [];
        let explosionParticles = [];

        // Initialize vehicles
        function initializeVehicles() {
            vehicles = [];
            for (let i = 0; i < NUM_VEHICLES; i++) {
                const x = randomInRange(0, canvas.width);
                const y = randomInRange(0, canvas.height);
                const vx = randomInRange(VELOCITY_RANGE.min, VELOCITY_RANGE.max);
                const vy = randomInRange(VELOCITY_RANGE.min, VELOCITY_RANGE.max);
                vehicles.push(new Vehicle(x, y, vx, vy));
            }
        }

        // Initialize simulation
        function initializeSimulation() {
            initializeVehicles();
            simulationState = STATES.RUNNING;
        }

        // Draw vehicles
        function drawVehicles() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            vehicles.forEach(vehicle => {
                if (vehicle.isActive) {
                    vehicle.draw();
                }
            });
        }

        // Draw explosion particles
        function drawExplosionParticles() {
            explosionParticles.forEach(particle => {
                particle.draw();
            });
            // Remove expired particles
            explosionParticles = explosionParticles.filter(particle => !particle.isExpired());
        }

        // Update vehicle positions
        function updateVehicles(deltaTime) {
            vehicles.forEach(vehicle => {
                if (vehicle.isActive) {
                    vehicle.move(deltaTime);
                }
            });
        }

        // Check for collisions
        function checkCollisions() {
            for (let i = 0; i < vehicles.length; i++) {
                for (let j = i + 1; j < vehicles.length; j++) {
                    if (detectCollision(vehicles[i], vehicles[j])) {
                        handleCollision(i, j);
                    }
                }
            }
        }

        // Handle collision
        function handleCollision(index1, index2) {
            // Mark vehicles as inactive
            vehicles[index1].isActive = false;
            vehicles[index2].isActive = false;

            // Calculate collision point
            const x = (vehicles[index1].x + vehicles[index2].x) / 2;
            const y = (vehicles[index1].y + vehicles[index2].y) / 2;

            // Create explosion particles
            for (let i = 0; i < EXPLOSION_PARTICLES; i++) {
                const angle = Math.random() * Math.PI * 2;
                const speed = randomInRange(VELOCITY_RANGE.min, VELOCITY_RANGE.max);
                explosionParticles.push(new ExplosionParticle(x, y, speed * Math.cos(angle), speed * Math.sin(angle)));
            }

            // Switch to EXPLODING state
            simulationState = STATES.EXPLODING;
        }

        // Update simulation based on state
        function updateSimulation(deltaTime) {
            switch (simulationState) {
                case STATES.RUNNING:
                    updateVehicles(deltaTime);
                    checkCollisions();
                    break;
                case STATES.EXPLODING:
                    // Update and draw explosion particles
                    drawExplosionParticles();
                    if (explosionParticles.length === 0) {
                        // Switch to RESTARTING state after explosion duration
                        setTimeout(() => {
                            simulationState = STATES.RESTARTING;
                        }, EXPLOSION_DURATION);
                    }
                    break;
                case STATES.RESTARTING:
                    initializeSimulation();
                    break;
            }
        }

        // Animation loop
        let lastTime = 0;

        function animationLoop(currentTime) {
            const deltaTime = currentTime - lastTime;
            lastTime = currentTime;

            updateSimulation(deltaTime);

            drawVehicles();
            drawExplosionParticles();

            requestAnimationFrame(animationLoop);
        }

        // Start the simulation
        initializeSimulation();
        requestAnimationFrame(animationLoop);
    </script>
</body>
</html>
```

### Implementation Notes:
- **Object-Oriented Design:** Used classes `Vehicle` and `ExplosionParticle` for better organization and readability.
- **Collision Detection:** Implemented a simple distance-based collision detection for rectangles.
- **State Management:** Managed simulation states (`RUNNING`, `EXPLODING`, `RESTARTING`) to control the flow of the simulation.
- **Animation Loop:** Utilized `requestAnimationFrame` for smooth animations, updating and drawing objects based on the current state.
- **Explosion Effect:** Created a burst of particles with random velocities and lifespans to simulate an explosion effect at the collision point.
- **Screen Wrapping:** Vehicles wrap around the canvas edges to create an infinite moving effect.
- **Performance:** Optimized collision checks by only comparing each pair of vehicles once.

This simulation provides a basic but comprehensive demonstration of object management, collision detection, and state management in a web-based animation environment.

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: granite-4.0-h-small-UD-Q5_K_XL.gguf -->
<!-- Prompt: vehicles.md -->
<!-- Generation Time: 32.79s -->
<!-- Fallback Used: False -->