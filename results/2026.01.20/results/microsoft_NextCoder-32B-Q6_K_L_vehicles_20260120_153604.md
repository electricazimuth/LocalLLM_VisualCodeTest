To create the Vehicle Collision & Restart Simulation, we'll follow a structured approach. We'll use the Canvas API for rendering and JavaScript for the logic. Here's the detailed implementation:

1. **Setup the Canvas and Context**.
2. **Define Vehicle and ExplosionParticle Classes**.
3. **Initialize the Simulation**.
4. **Implement Movement and Wrapping for Vehicles**.
5. **Implement Collision Detection**.
6. **Implement Explosion Effect**.
7. **Manage Simulation States**.
8. **Create the Animation Loop**.

Let's go through the code step-by-step.

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
        const width = canvas.width;
        const height = canvas.height;

        let simulationState = 'RUNNING'; // Possible states: 'RUNNING', 'EXPLODING', 'RESTARTING'
        let vehicles = [];
        let explosionParticles = [];
        let lastTime = 0;
        const vehicleCount = 5;

        class Vehicle {
            constructor(x, y, vx, vy) {
                this.x = x;
                this.y = y;
                this.vx = vx;
                this.vy = vy;
                this.width = 20;
                this.height = 10;
                this.color = `hsl(${Math.random() * 360}, 100%, 50%)`;
                this.isActive = true;
            }

            draw() {
                if (this.isActive) {
                    ctx.fillStyle = this.color;
                    ctx.fillRect(this.x, this.y, this.width, this.height);
                    ctx.fillStyle = 'black';
                    ctx.beginPath();
                    ctx.arc(this.x + this.width / 4, this.y + this.height, 4, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.beginPath();
                    ctx.arc(this.x + this.width * 3 / 4, this.y + this.height, 4, 0, Math.PI * 2);
                    ctx.fill();
                }
            }

            update(deltaTime) {
                if (this.isActive) {
                    this.x += this.vx * deltaTime;
                    this.y += this.vy * deltaTime;

                    // Wrap around the screen
                    if (this.x < -this.width) this.x = width;
                    if (this.x > width) this.x = -this.width;
                    if (this.y < -this.height) this.y = height;
                    if (this.y > height) this.y = -this.height;
                }
            }
        }

        class ExplosionParticle {
            constructor(x, y) {
                this.x = x;
                this.y = y;
                this.vx = (Math.random() - 0.5) * 10;
                this.vy = (Math.random() - 0.5) * 10;
                this.lifespan = 2;
                this.size = 3;
                this.color = `rgba(255, 165, 0, ${this.lifespan})`;
            }

            draw() {
                ctx.fillStyle = this.color;
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                ctx.fill();
            }

            update(deltaTime) {
                this.x += this.vx * deltaTime;
                this.y += this.vy * deltaTime;
                this.lifespan -= deltaTime;
                this.color = `rgba(255, 165, 0, ${this.lifespan})`;
                this.size += deltaTime * 2;
            }
        }

        function init() {
            vehicles = [];
            for (let i = 0; i < vehicleCount; i++) {
                const x = Math.random() * width;
                const y = Math.random() * height;
                const vx = (Math.random() - 0.5) * 5;
                const vy = (Math.random() - 0.5) * 5;
                vehicles.push(new Vehicle(x, y, vx, vy));
            }
            simulationState = 'RUNNING';
        }

        function checkCollisions() {
            for (let i = 0; i < vehicles.length; i++) {
                for (let j = i + 1; j < vehicles.length; j++) {
                    const vehicle1 = vehicles[i];
                    const vehicle2 = vehicles[j];
                    if (vehicle1.isActive && vehicle2.isActive) {
                        const dx = vehicle1.x - vehicle2.x;
                        const dy = vehicle1.y - vehicle2.y;
                        const distance = Math.sqrt(dx * dx + dy * dy);
                        if (distance < (vehicle1.width + vehicle2.width) / 2) {
                            vehicle1.isActive = false;
                            vehicle2.isActive = false;
                            const explosionX = (vehicle1.x + vehicle2.x) / 2;
                            const explosionY = (vehicle1.y + vehicle2.y) / 2;
                            for (let k = 0; k < 20; k++) {
                                explosionParticles.push(new ExplosionParticle(explosionX, explosionY));
                            }
                            simulationState = 'EXPLODING';
                        }
                    }
                }
            }
        }

        function drawExplosion() {
            ctx.font = '30px Arial';
            ctx.fillStyle = 'white';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText('BOOM!', width / 2, height / 2);
            explosionParticles.forEach(particle => particle.draw());
        }

        function update(deltaTime) {
            if (simulationState === 'RUNNING') {
                vehicles.forEach(vehicle => vehicle.update(deltaTime));
                checkCollisions();
            } else if (simulationState === 'EXPLODING') {
                explosionParticles.forEach(particle => particle.update(deltaTime));
                explosionParticles = explosionParticles.filter(particle => particle.lifespan > 0);
                if (explosionParticles.length === 0) {
                    simulationState = 'RESTARTING';
                }
            } else if (simulationState === 'RESTARTING') {
                init();
            }
        }

        function draw() {
            ctx.clearRect(0, 0, width, height);
            if (simulationState === 'RUNNING') {
                vehicles.forEach(vehicle => vehicle.draw());
            } else if (simulationState === 'EXPLODING') {
                drawExplosion();
            }
        }

        function animate(time) {
            const deltaTime = (time - lastTime) / 1000;
            lastTime = time;
            update(deltaTime);
            draw();
            requestAnimationFrame(animate);
        }

        init();
        requestAnimationFrame(animate);
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
1. **Canvas Setup**: We initialize the canvas and get its 2D context.
2. **Vehicle and ExplosionParticle Classes**: These classes handle the properties and behaviors of the vehicles and explosion particles.
3. **Initialization**: The `init` function initializes the vehicles with random positions and velocities.
4. **Movement and Wrapping**: The `update` method in the `Vehicle` class updates the vehicle positions and wraps them around the canvas edges.
5. **Collision Detection**: The `checkCollisions` function checks for collisions between vehicles using a simple distance-based method.
6. **Explosion Effect**: The `ExplosionParticle` class handles the creation and updating of explosion particles. The `drawExplosion` function draws the explosion effect.
7. **State Management**: The simulation state is managed using the `simulationState` variable, which can be `RUNNING`, `EXPLODING`, or `RESTARTING`.
8. **Animation Loop**: The `animate` function is the main loop that updates and draws the simulation using `requestAnimationFrame`.

This implementation ensures a smooth and efficient simulation with clear state transitions and visual effects.

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: microsoft_NextCoder-32B-Q6_K_L.gguf -->
<!-- Prompt: vehicles.md -->
<!-- Generation Time: 94.82s -->
<!-- Fallback Used: False -->