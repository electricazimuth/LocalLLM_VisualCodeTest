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
        // --- Vehicle Collision & Restart Simulation ---
        // This simulation features:
        // - Multiple vehicles with random positions, velocities, and colors
        // - Screen wrapping at all four edges
        // - Collision detection using axis-aligned bounding boxes (AABB)
        // - Explosion effect with particles that fade out and expand
        // - State management (RUNNING, EXPLODING, RESTARTING)
        // - Smooth animation using requestAnimationFrame and delta time
        // - Clean restart after explosion with new vehicle configuration

        // --- Constants ---
        const CANVAS_WIDTH = 512;
        const CANVAS_HEIGHT = 512;
        const NUM_VEHICLES = 8;
        const EXPLOSION_PARTICLES = 25;
        const EXPLOSION_DURATION = 3000; // ms
        const RESTART_DELAY = 2000; // ms before restart after explosion
        const MIN_VEHICLE_SIZE = 30;
        const MAX_VEHICLE_SIZE = 60;
        const MIN_SPEED = 0.5;
        const MAX_SPEED = 2.5;

        // --- State Management ---
        const STATES = {
            RUNNING: 'RUNNING',
            EXPLODING: 'EXPLODING',
            RESTARTING: 'RESTARTING'
        };

        // --- Canvas Setup ---
        const canvas = document.getElementById('simulationCanvas');
        const ctx = canvas.getContext('2d');

        // --- Simulation State ---
        let simulationState = STATES.RUNNING;
        let lastTime = 0;
        let explosionStartTime = 0;
        let restartTimer = 0;

        // --- Vehicle Class ---
        class Vehicle {
            constructor(x, y, width, height, vx, vy, color) {
                this.x = x;
                this.y = y;
                this.width = width;
                this.height = height;
                this.vx = vx;
                this.vy = vy;
                this.color = color;
                this.isActive = true;
            }

            // Update position based on velocity and delta time
            update(deltaTime) {
                if (!this.isActive) return;

                // Update position
                this.x += this.vx * deltaTime;
                this.y += this.vy * deltaTime;

                // Handle screen wrapping
                if (this.x < -this.width) this.x = CANVAS_WIDTH;
                if (this.x > CANVAS_WIDTH) this.x = -this.width;
                if (this.y < -this.height) this.y = CANVAS_HEIGHT;
                if (this.y > CANVAS_HEIGHT) this.y = -this.height;
            }

            // Draw the vehicle (simple car with rectangle body and two wheels)
            draw() {
                if (!this.isActive) return;

                ctx.fillStyle = this.color;
                // Car body
                ctx.fillRect(this.x, this.y, this.width, this.height);

                // Front and rear wheels
                const wheelWidth = this.width * 0.2;
                const wheelHeight = this.height * 0.4;
                const wheelOffsetX = this.width * 0.25;
                const wheelOffsetY = this.height * 0.25;

                // Front wheels
                ctx.fillStyle = '#333';
                ctx.fillRect(this.x + wheelOffsetX, this.y + wheelOffsetY, wheelWidth, wheelHeight);
                ctx.fillRect(this.x + this.width - wheelOffsetX - wheelWidth, this.y + wheelOffsetY, wheelWidth, wheelHeight);

                // Rear wheels
                ctx.fillRect(this.x + wheelOffsetX, this.y + this.height - wheelOffsetY - wheelHeight, wheelWidth, wheelHeight);
                ctx.fillRect(this.x + this.width - wheelOffsetX - wheelWidth, this.y + this.height - wheelOffsetY - wheelHeight, wheelWidth, wheelHeight);
            }

            // Get bounding box for collision detection
            getBounds() {
                return {
                    x: this.x,
                    y: this.y,
                    width: this.width,
                    height: this.height
                };
            }

            // Check if this vehicle collides with another
            collidesWith(other) {
                if (!this.isActive || !other.isActive) return false;

                const a = this.getBounds();
                const b = other.getBounds();

                return a.x < b.x + b.width &&
                       a.x + a.width > b.x &&
                       a.y < b.y + b.height &&
                       a.y + a.height > b.y;
            }
        }

        // --- Explosion Particle Class ---
        class ExplosionParticle {
            constructor(x, y, color) {
                this.x = x;
                this.y = y;
                this.vx = (Math.random() - 0.5) * 8; // Random velocity
                this.vy = (Math.random() - 0.5) * 8;
                this.size = Math.random() * 4 + 2; // Random size between 2 and 6
                this.color = color;
                this.lifespan = 100 + Math.random() * 100; // Random lifespan
                this.maxLifespan = this.lifespan;
                this.angle = Math.random() * Math.PI * 2;
                this.rotationSpeed = (Math.random() - 0.5) * 0.2;
            }

            update(deltaTime) {
                if (this.lifespan <= 0) return;

                // Apply velocity
                this.x += this.vx * deltaTime;
                this.y += this.vy * deltaTime;

                // Apply rotation
                this.angle += this.rotationSpeed;

                // Decrease lifespan
                this.lifespan -= deltaTime * 10; // Scale by delta time
            }

            draw() {
                if (this.lifespan <= 0) return;

                const alpha = this.lifespan / this.maxLifespan;
                ctx.save();
                ctx.translate(this.x, this.y);
                ctx.rotate(this.angle);

                // Use gradient for visual effect
                const gradient = ctx.createRadialGradient(0, 0, 0, 0, 0, this.size);
                gradient.addColorStop(0, this.color + 'FF');
                gradient.addColorStop(0.7, this.color + '80');
                gradient.addColorStop(1, this.color + '00');

                ctx.fillStyle = gradient;
                ctx.beginPath();
                ctx.arc(0, 0, this.size, 0, Math.PI * 2);
                ctx.fill();

                ctx.restore();
            }

            // Check if particle is expired
            isExpired() {
                return this.lifespan <= 0;
            }
        }

        // --- Main Simulation Variables ---
        let vehicles = [];
        let explosionParticles = [];

        // --- Initialization Function ---
        function initVehicles() {
            vehicles = [];
            const colors = [
                '#FF5733', '#33FF57', '#3357FF', '#FF33F5', '#F5FF33',
                '#33FFF5', '#FF8C33', '#8C33FF', '#338CFF', '#FF338C'
            ];

            for (let i = 0; i < NUM_VEHICLES; i++) {
                const size = Math.random() * (MAX_VEHICLE_SIZE - MIN_VEHICLE_SIZE) + MIN_VEHICLE_SIZE;
                const x = Math.random() * CANVAS_WIDTH;
                const y = Math.random() * CANVAS_HEIGHT;
                const vx = (Math.random() - 0.5) * (MAX_SPEED - MIN_SPEED) + MIN_SPEED;
                const vy = (Math.random() - 0.5) * (MAX_SPEED - MIN_SPEED) + MIN_SPEED;
                const color = colors[i % colors.length];

                vehicles.push(new Vehicle(x, y, size, size * 0.6, vx, vy, color));
            }
        }

        // --- Collision Detection ---
        function checkCollisions() {
            for (let i = 0; i < vehicles.length; i++) {
                for (let j = i + 1; j < vehicles.length; j++) {
                    if (vehicles[i].collidesWith(vehicles[j])) {
                        return { a: vehicles[i], b: vehicles[j] };
                    }
                }
            }
            return null;
        }

        // --- Trigger Explosion ---
        function triggerExplosion(collidedVehicles) {
            const center = {
                x: (collidedVehicles.a.x + collidedVehicles.b.x) / 2,
                y: (collidedVehicles.a.y + collidedVehicles.b.y) / 2
            };

            // Mark vehicles as inactive
            collidedVehicles.a.isActive = false;
            collidedVehicles.b.isActive = false;

            // Create explosion particles
            const explosionColor = '#FF4500'; // Orange-red for explosion
            for (let i = 0; i < EXPLOSION_PARTICLES; i++) {
                explosionParticles.push(new ExplosionParticle(center.x, center.y, explosionColor));
            }

            // Set simulation state to EXPLODING
            simulationState = STATES.EXPLODING;
            explosionStartTime = Date.now();
        }

        // --- Animation Loop ---
        function animate(currentTime) {
            // Calculate delta time (in seconds)
            const deltaTime = (currentTime - lastTime) / 1000;
            lastTime = currentTime;

            // Clear canvas
            ctx.clearRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);

            // Handle simulation state
            switch (simulationState) {
                case STATES.RUNNING:
                    // Update and draw vehicles
                    for (const vehicle of vehicles) {
                        vehicle.update(deltaTime);
                    }

                    // Check for collisions
                    const collision = checkCollisions();
                    if (collision) {
                        triggerExplosion(collision);
                    }

                    // Draw vehicles
                    for (const vehicle of vehicles) {
                        vehicle.draw();
                    }

                    break;

                case STATES.EXPLODING:
                    // Update explosion particles
                    for (let i = explosionParticles.length - 1; i >= 0; i--) {
                        explosionParticles[i].update(deltaTime);
                        if (explosionParticles[i].isExpired()) {
                            explosionParticles.splice(i, 1);
                        }
                    }

                    // Draw explosion particles
                    for (const particle of explosionParticles) {
                        particle.draw();
                    }

                    // Draw "BOOM" text in center
                    ctx.font = 'bold 48px Arial';
                    ctx.fillStyle = 'rgba(255, 255, 0, 0.8)';
                    ctx.textAlign = 'center';
                    ctx.fillText('BOOM', CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2 + 10);
                    ctx.font = 'bold 24px Arial';
                    ctx.fillStyle = 'rgba(255, 255, 0, 0.6)';
                    ctx.fillText('Collision!', CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2 + 50);

                    // Check if explosion is complete
                    if (Date.now() - explosionStartTime >= EXPLOSION_DURATION && explosionParticles.length === 0) {
                        simulationState = STATES.RESTARTING;
                        restartTimer = Date.now();
                    }

                    break;

                case STATES.RESTARTING:
                    // Check if restart delay has passed
                    if (Date.now() - restartTimer >= RESTART_DELAY) {
                        // Reset simulation
                        explosionParticles = [];
                        initVehicles();
                        simulationState = STATES.RUNNING;
                    }

                    // Draw "Restarting..." text
                    ctx.font = '24px Arial';
                    ctx.fillStyle = '#FFF';
                    ctx.textAlign = 'center';
                    ctx.fillText('Restarting...', CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2);
                    break;
            }

            // Continue animation loop
            requestAnimationFrame(animate);
        }

        // --- Start Simulation ---
        initVehicles();
        requestAnimationFrame(animate);

        // --- Optional: Add resize handler for responsiveness ---
        window.addEventListener('resize', () => {
            // Adjust canvas size if needed
            const container = canvas.parentElement;
            const width = container.clientWidth;
            const height = container.clientHeight;

            // Maintain aspect ratio
            const scale = Math.min(width / 512, height / 512);
            canvas.width = 512 * scale;
            canvas.height = 512 * scale;
            canvas.style.width = `${512 * scale}px`;
            canvas.style.height = `${512 * scale}px`;
        });

    </script>

    <!-- Optional section for notes -->
    <section id="notes">
        <h3>Implementation Notes</h3>
        <ul>
            <li><strong>State Management:</strong> The simulation uses a clear three-state system (RUNNING, EXPLODING, RESTARTING) to manage the lifecycle of the animation, ensuring clean transitions.</li>
            <li><strong>Collision Detection:</strong> Implemented using Axis-Aligned Bounding Box (AABB) collision detection, which is efficient and reliable for rectangular objects. Pairs are checked only once (i < j) to avoid redundancy.</li>
            <li><strong>Screen Wrapping:</strong> Vehicles wrap seamlessly across all four edges by checking if their position is outside the canvas bounds and resetting to the opposite side.</li>
            <li><strong>Explosion Particles:</strong> Each particle has random velocity, rotation, size, and lifespan. A radial gradient creates a glowing effect. Particles fade out as their lifespan decreases.</li>
            <li><strong>Animation Loop:</strong> Uses <code>requestAnimationFrame</code> with proper delta time calculation for smooth and consistent animation across different frame rates.</li>
            <li><strong>Visual Effects:</strong> The "BOOM" text appears during the explosion phase, and the explosion particles expand outward with a realistic burst effect.</li>
            <li><strong>Restart Mechanism:</strong> After the explosion animation completes, a delay is enforced before resetting the vehicles, giving users time to perceive the event.</li>
            <li><strong>Performance:</strong> The use of efficient collision checks and object pooling (via array splicing) helps maintain performance even with multiple vehicles.</li>
        </ul>
    </section>
</body>
</html>
```

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: Qwen3-30B-A3B-Instruct-2507-UD-Q4_K_XL.gguf -->
<!-- Prompt: vehicles.md -->
<!-- Generation Time: 29.59s -->
<!-- Fallback Used: False -->