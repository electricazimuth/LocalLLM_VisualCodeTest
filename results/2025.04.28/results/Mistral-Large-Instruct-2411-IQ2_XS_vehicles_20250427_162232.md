Sure! Below is the complete solution for the vehicle collision and restart simulation. I've included the necessary HTML, CSS, and JavaScript code to achieve the described functionality. The JavaScript code covers the initialization of the simulation, vehicle movement, collision detection, explosion effects, and the state management for restarting the simulation.

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

        const simulationStates = {
            RUNNING: 'RUNNING',
            EXPLODING: 'EXPLODING',
            RESTARTING: 'RESTARTING'
        };

        let simulationState = simulationStates.RUNNING;
        let vehicles = [];
        let explosionParticles = [];
        let explosionTime = 0;
        let restartDelay = 3000; // 3 seconds

        class Vehicle {
            constructor(x, y, vx, vy, width, height) {
                this.x = x;
                this.y = y;
                this.vx = vx;
                this.vy = vy;
                this.width = width;
                this.height = height;
                this.isActive = true;
            }

            draw(ctx) {
                ctx.fillStyle = 'white';
                ctx.fillRect(this.x - this.width / 2, this.y - this.height / 2, this.width, this.height);
                ctx.fillStyle = 'gray';
                ctx.fillRect(this.x - this.width / 2, this.y + this.height / 2, this.width, this.height / 4);
            }

            update(deltaTime) {
                this.x += this.vx * deltaTime;
                this.y += this.vy * deltaTime;

                if (this.x > canvas.width) this.x = 0;
                if (this.x < 0) this.x = canvas.width;
                if (this.y > canvas.height) this.y = 0;
                if (this.y < 0) this.y = canvas.height;
            }
        }

        class ExplosionParticle {
            constructor(x, y, vx, vy, size, lifespan) {
                this.x = x;
                this.y = y;
                this.vx = vx;
                this.vy = vy;
                this.size = size;
                this.lifespan = lifespan;
                this.isActive = true;
            }

            draw(ctx) {
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size, 0, 2 * Math.PI);
                ctx.fillStyle = 'orange';
                ctx.fill();
            }

            update(deltaTime) {
                this.x += this.vx * deltaTime;
                this.y += this.vy * deltaTime;
                this.lifespan -= deltaTime;
                if (this.lifespan <= 0) this.isActive = false;
            }
        }

        function initializeVehicles(numVehicles) {
            vehicles = [];
            for (let i = 0; i < numVehicles; i++) {
                let x = Math.random() * canvas.width;
                let y = Math.random() * canvas.height;
                let vx = (Math.random() - 0.5) * 2; // Random velocity between -1 and 1
                let vy = (Math.random() - 0.5) * 2; // Random velocity between -1 and 1
                let width = 20;
                let height = 10;
                vehicles.push(new Vehicle(x, y, vx, vy, width, height));
            }
        }

        function checkCollisions() {
            for (let i = 0; i < vehicles.length; i++) {
                for (let j = i + 1; j < vehicles.length; j++) {
                    let vehicle1 = vehicles[i];
                    let vehicle2 = vehicles[j];
                    if (vehicle1.isActive && vehicle2.isActive &&
                        vehicle1.x < vehicle2.x + vehicle2.width && vehicle1.x + vehicle1.width > vehicle2.x &&
                        vehicle1.y < vehicle2.y + vehicle2.height && vehicle1.y + vehicle1.height > vehicle2.y) {
                        let collisionX = (vehicle1.x + vehicle2.x) / 2;
                        let collisionY = (vehicle1.y + vehicle2.y) / 2;
                        createExplosion(collisionX, collisionY);
                        vehicle1.isActive = false;
                        vehicle2.isActive = false;
                        simulationState = simulationStates.EXPLODING;
                        return;
                    }
                }
            }
        }

        function createExplosion(x, y) {
            explosionParticles = [];
            for (let i = 0; i < 30; i++) {
                let angle = Math.random() * 2 * Math.PI;
                let speed = Math.random() * 2;
                let vx = Math.cos(angle) * speed;
                let vy = Math.sin(angle) * speed;
                let size = Math.random() * 5 + 2;
                let lifespan = Math.random() + 1;
                explosionParticles.push(new ExplosionParticle(x, y, vx, vy, size, lifespan));
            }
            explosionTime = Date.now();
        }

        function update(deltaTime) {
            if (simulationState === simulationStates.RUNNING) {
                vehicles.forEach(vehicle => {
                    if (vehicle.isActive) vehicle.update(deltaTime);
                });
                checkCollisions();
            } else if (simulationState === simulationStates.EXPLODING) {
                explosionParticles.forEach(particle => {
                    particle.update(deltaTime);
                });
                explosionParticles = explosionParticles.filter(particle => particle.isActive);
                if (explosionParticles.length === 0 && Date.now() - explosionTime > restartDelay) {
                    simulationState = simulationStates.RESTARTING;
                }
            } else if (simulationState === simulationStates.RESTARTING) {
                initializeVehicles(5);
                simulationState = simulationStates.RUNNING;
            }
        }

        function draw() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            if (simulationState === simulationStates.RUNNING) {
                vehicles.forEach(vehicle => {
                    if (vehicle.isActive) vehicle.draw(ctx);
                });
            } else if (simulationState === simulationStates.EXPLODING) {
                explosionParticles.forEach(particle => {
                    particle.draw(ctx);
                });
                ctx.fillStyle = 'red';
                ctx.font = '30px Arial';
                ctx.fillText('BOOM', canvas.width / 2 - 50, canvas.height / 2);
            }
        }

        function animationLoop(timestamp) {
            let deltaTime = (timestamp - lastTime) / 1000;
            update(deltaTime);
            draw();
            lastTime = timestamp;
            requestAnimationFrame(animationLoop);
        }

        let lastTime = performance.now();
        initializeVehicles(5);
        requestAnimationFrame(animationLoop);
    </script>
</body>
</html>
```

### Notes:
1. **Vehicle Management:** Vehicles are initialized with random positions and velocities. They are updated and drawn based on the simulation state.
2. **Collision Detection:** Collisions are detected using simple rectangle intersection checks. When a collision occurs, vehicles are marked as inactive, and an explosion is created.
3. **Explosion Effect:** Explosion particles are created and updated. Once all particles have expired, the simulation state changes to `RESTARTING`.
4. **State Management:** The simulation state is managed to control the flow of the simulation, ensuring that the correct actions are taken at each stage.
5. **Animation Loop:** The `requestAnimationFrame` is used for smooth animations, and delta time is calculated to ensure consistent updates.

This code should run directly in a modern web browser and meet the specified requirements.

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: Mistral-Large-Instruct-2411-IQ2_XS.gguf -->
<!-- Prompt: vehicles.md -->
<!-- Generation Time: 884.24s -->
<!-- Fallback Used: False -->