Sure, I'll provide you with a complete solution for the vehicle collision and restart simulation using HTML, CSS, and JavaScript. The solution will adhere to the requirements and best practices for smooth animation and efficient state management.

Here's the complete implementation within a single HTML file:

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
    <canvas id="simulationCanvas" width="800" height="600"></canvas>

    <script>
        // --- Vehicle Class ---
        class Vehicle {
            constructor(x, y, vx, vy, color) {
                this.x = x;
                this.y = y;
                this.vx = vx;
                this.vy = vy;
                this.color = color;
                this.width = 30;
                this.height = 15;
                this.radius = 15;
                this.isActive = true;
            }

            draw(ctx) {
                ctx.fillStyle = this.color;
                ctx.fillRect(this.x - this.width / 2, this.y - this.height / 2, this.width, this.height);
                // Draw wheels
                ctx.beginPath();
                ctx.arc(this.x - this.width / 3, this.y, this.radius / 3, 0, Math.PI * 2);
                ctx.arc(this.x + this.width / 3, this.y, this.radius / 3, 0, Math.PI * 2);
                ctx.fill();
            }

            update(deltaTime) {
                this.x += this.vx * deltaTime;
                this.y += this.vy * deltaTime;

                // Wrap around screen edges
                if (this.x > canvas.width) this.x = 0;
                if (this.x < 0) this.x = canvas.width;
                if (this.y > canvas.height) this.y = 0;
                if (this.y < 0) this.y = canvas.height;
            }
        }

        // --- ExplosionParticle Class ---
        class ExplosionParticle {
            constructor(x, y, vx, vy, color, lifespan) {
                this.x = x;
                this.y = y;
                this.vx = vx;
                this.vy = vy;
                this.color = color;
                this.lifespan = lifespan;
            }

            update(deltaTime) {
                this.x += this.vx * deltaTime;
                this.y += this.vy * deltaTime;
                this.lifespan -= deltaTime;
            }

            draw(ctx) {
                ctx.fillStyle = this.color;
                ctx.beginPath();
                ctx.arc(this.x, this.y, 2, 0, Math.PI * 2);
                ctx.fill();
            }
        }

        // --- Simulation Setup ---
        const canvas = document.getElementById('simulationCanvas');
        const ctx = canvas.getContext('2d');
        let vehicles = [];
        let explosionParticles = [];
        let simulationState = 'RUNNING';
        let lastTime = 0;

        function init() {
            vehicles = [];
            for (let i = 0; i < 10; i++) {
                const x = Math.random() * canvas.width;
                const y = Math.random() * canvas.height;
                const vx = (Math.random() - 0.5) * 200;
                const vy = (Math.random() - 0.5) * 200;
                const color = `hsl(${Math.random() * 360}, 100%, 50%)`;
                vehicles.push(new Vehicle(x, y, vx, vy, color));
            }
        }

        function checkCollisions() {
            for (let i = 0; i < vehicles.length; i++) {
                for (let j = i + 1; j < vehicles.length; j++) {
                    const v1 = vehicles[i];
                    const v2 = vehicles[j];
                    const dx = v1.x - v2.x;
                    const dy = v1.y - v2.y;
                    const distance = Math.sqrt(dx * dx + dy * dy);

                    if (distance < v1.radius + v2.radius) {
                        handleCollision(v1, v2);
                        return true;
                    }
                }
            }
            return false;
        }

        function handleCollision(v1, v2) {
            v1.isActive = false;
            v2.isActive = false;
            const midX = (v1.x + v2.x) / 2;
            const midY = (v1.y + v2.y) / 2;

            for (let i = 0; i < 30; i++) {
                const vx = (Math.random() - 0.5) * 400;
                const vy = (Math.random() - 0.5) * 400;
                const color = `hsl(${Math.random() * 360}, 100%, 50%)`;
                explosionParticles.push(new ExplosionParticle(midX, midY, vx, vy, color, 1));
            }
            simulationState = 'EXPLODING';
        }

        function update(deltaTime) {
            if (simulationState === 'RUNNING') {
                for (let vehicle of vehicles) {
                    if (vehicle.isActive) {
                        vehicle.update(deltaTime);
                    }
                }
                if (checkCollisions()) {
                    simulationState = 'EXPLODING';
                }
            } else if (simulationState === 'EXPLODING') {
                for (let particle of explosionParticles) {
                    particle.update(deltaTime);
                }
                explosionParticles = explosionParticles.filter(particle => particle.lifespan > 0);
                if (explosionParticles.length === 0) {
                    simulationState = 'RESTARTING';
                }
            } else if (simulationState === 'RESTARTING') {
                setTimeout(() => {
                    init();
                    simulationState = 'RUNNING';
                }, 3000);
            }
        }

        function draw() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            if (simulationState === 'RUNNING') {
                for (let vehicle of vehicles) {
                    if (vehicle.isActive) {
                        vehicle.draw(ctx);
                    }
                }
            } else if (simulationState === 'EXPLODING') {
                for (let particle of explosionParticles) {
                    particle.draw(ctx);
                }
                ctx.fillStyle = 'red';
                ctx.font = '48px Arial';
                ctx.fillText('BOOM', canvas.width / 2 - 50, canvas.height / 2);
            }
        }

        function gameLoop(timestamp) {
            const deltaTime = (timestamp - lastTime) / 1000;
            lastTime = timestamp;
            update(deltaTime);
            draw();
            requestAnimationFrame(gameLoop);
        }

        init();
        requestAnimationFrame(gameLoop);
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

### Explanation:

1. **Vehicle Class:**
    - Manages the position, velocity, and appearance of each vehicle.
    - Includes methods to update the vehicle's position and draw it on the canvas.

2. **ExplosionParticle Class:**
    - Manages the position, velocity, lifespan, and appearance of each explosion particle.
    - Includes methods to update the particle's position and draw it on the canvas.

3. **Simulation Setup:**
    - Initializes the canvas and context.
    - Manages the array of vehicles and explosion particles.
    - Manages the simulation state (`RUNNING`, `EXPLODING`, `RESTARTING`).

4. **Collision Detection:**
    - Checks for collisions between vehicles.
    - If a collision is detected, handles the collision by deactivating the vehicles and creating explosion particles.

5. **Animation Loop:**
    - Uses `requestAnimationFrame` to create a smooth animation loop.
    - Calculates and uses delta time for smooth updates.
    - Updates and draws based on the current simulation state.

This implementation adheres to the requirements and provides a smooth, autonomous simulation of vehicle movement, collision detection, and explosion effects.

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: mistralai_Mistral-Small-3.1-24B-Instruct-2503-Q6_K_L.gguf -->
<!-- Prompt: vehicles.md -->
<!-- Generation Time: 52.21s -->
<!-- Fallback Used: False -->