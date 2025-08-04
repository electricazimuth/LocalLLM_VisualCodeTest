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
        // Get the canvas and its context
        const canvas = document.getElementById('simulationCanvas');
        const ctx = canvas.getContext('2d');

        // Define simulation constants
        const SIMULATION_WIDTH = canvas.width;
        const SIMULATION_HEIGHT = canvas.height;
        const VEHICLE_COUNT = 10;
        const EXPLOSION_PARTICLE_COUNT = 20;
        const EXPLOSION_DURATION = 3000; // milliseconds

        // Define vehicle class
        class Vehicle {
            constructor(x, y, vx, vy, radius, color) {
                this.x = x;
                this.y = y;
                this.vx = vx;
                this.vy = vy;
                this.radius = radius;
                this.color = color;
                this.isActive = true;
            }

            update(deltaTime) {
                this.x += this.vx * deltaTime;
                this.y += this.vy * deltaTime;

                // Wrap around edges
                if (this.x - this.radius < 0) {
                    this.x = SIMULATION_WIDTH - this.radius;
                } else if (this.x + this.radius > SIMULATION_WIDTH) {
                    this.x = this.radius;
                }

                if (this.y - this.radius < 0) {
                    this.y = SIMULATION_HEIGHT - this.radius;
                } else if (this.y + this.radius > SIMULATION_HEIGHT) {
                    this.y = this.radius;
                }
            }

            draw() {
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.radius, 0, 2 * Math.PI);
                ctx.fillStyle = this.color;
                ctx.fill();
            }
        }

        // Define explosion particle class
        class ExplosionParticle {
            constructor(x, y, vx, vy, radius, color) {
                this.x = x;
                this.y = y;
                this.vx = vx;
                this.vy = vy;
                this.radius = radius;
                this.color = color;
                this.lifespan = 1000; // milliseconds
            }

            update(deltaTime) {
                this.x += this.vx * deltaTime;
                this.y += this.vy * deltaTime;
                this.lifespan -= deltaTime;
            }

            draw() {
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.radius, 0, 2 * Math.PI);
                ctx.fillStyle = this.color;
                ctx.fill();
            }
        }

        // Initialize simulation state and objects
        let simulationState = 'RUNNING';
        let vehicles = [];
        let explosionParticles = [];
        let explosionStartTime = 0;

        // Initialize vehicles
        for (let i = 0; i < VEHICLE_COUNT; i++) {
            const x = Math.random() * SIMULATION_WIDTH;
            const y = Math.random() * SIMULATION_HEIGHT;
            const vx = Math.random() * 2 - 1;
            const vy = Math.random() * 2 - 1;
            const radius = 10;
            const color = `hsl(${i * 36}, 100%, 50%)`;
            vehicles.push(new Vehicle(x, y, vx, vy, radius, color));
        }

        // Main animation loop
        function animate() {
            const currentTime = performance.now();
            const deltaTime = (currentTime - (vehicles[0] ? vehicles[0].lastUpdateTime : 0)) / 1000;

            // Update simulation state
            switch (simulationState) {
                case 'RUNNING':
                    // Update vehicles
                    vehicles.forEach(vehicle => {
                        vehicle.update(deltaTime);
                        vehicle.lastUpdateTime = currentTime;
                    });

                    // Check for collisions
                    for (let i = 0; i < vehicles.length; i++) {
                        for (let j = i + 1; j < vehicles.length; j++) {
                            const distance = Math.hypot(vehicles[i].x - vehicles[j].x, vehicles[i].y - vehicles[j].y);
                            if (distance < vehicles[i].radius + vehicles[j].radius) {
                                // Collision detected, switch to EXPLODING state
                                simulationState = 'EXPLODING';
                                explosionStartTime = currentTime;

                                // Create explosion particles
                                const collisionX = (vehicles[i].x + vehicles[j].x) / 2;
                                const collisionY = (vehicles[i].y + vehicles[j].y) / 2;
                                for (let k = 0; k < EXPLOSION_PARTICLE_COUNT; k++) {
                                    const vx = Math.random() * 2 - 1;
                                    const vy = Math.random() * 2 - 1;
                                    const radius = 2;
                                    const color = `hsl(${k * 36}, 100%, 50%)`;
                                    explosionParticles.push(new ExplosionParticle(collisionX, collisionY, vx, vy, radius, color));
                                }
                            }
                        }
                    }

                    break;
                case 'EXPLODING':
                    // Update explosion particles
                    explosionParticles.forEach(particle => {
                        particle.update(deltaTime);
                    });

                    // Check if explosion particles have expired
                    if (currentTime - explosionStartTime > EXPLOSION_DURATION) {
                        // Switch to RESTARTING state
                        simulationState = 'RESTARTING';
                    }

                    break;
                case 'RESTARTING':
                    // Reset simulation
                    vehicles = [];
                    explosionParticles = [];

                    // Initialize new vehicles
                    for (let i = 0; i < VEHICLE_COUNT; i++) {
                        const x = Math.random() * SIMULATION_WIDTH;
                        const y = Math.random() * SIMULATION_HEIGHT;
                        const vx = Math.random() * 2 - 1;
                        const vy = Math.random() * 2 - 1;
                        const radius = 10;
                        const color = `hsl(${i * 36}, 100%, 50%)`;
                        vehicles.push(new Vehicle(x, y, vx, vy, radius, color));
                    }

                    // Switch back to RUNNING state
                    simulationState = 'RUNNING';

                    break;
            }

            // Draw simulation
            ctx.clearRect(0, 0, SIMULATION_WIDTH, SIMULATION_HEIGHT);

            switch (simulationState) {
                case 'RUNNING':
                    vehicles.forEach(vehicle => {
                        vehicle.draw();
                    });
                    break;
                case 'EXPLODING':
                    explosionParticles.forEach(particle => {
                        if (particle.lifespan > 0) {
                            particle.draw();
                        }
                    });
                    break;
            }

            // Request next frame
            requestAnimationFrame(animate);
        }

        // Start animation loop
        animate();
    </script>

    <!-- Optional section for notes -->
    <!--
    <section id="notes">
        Developer notes regarding collision detection method, state management, design choices, etc.
    </section>
    -->
</body>
</html>
```

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: Llama-3.3-70B-Instruct-UD-IQ3_XXS.gguf -->
<!-- Prompt: vehicles.md -->
<!-- Generation Time: 77.20s -->
<!-- Fallback Used: False -->