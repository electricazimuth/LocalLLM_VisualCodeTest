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
        const vehicleCount = 8;
        const explosionParticleCount = 30;

        let vehicles = [];
        let explosionParticles = [];
        let boomText = null;

        let simulationState = 'RUNNING'; // Possible states: 'RUNNING', 'EXPLODING', 'RESTARTING'
        let startTime = null;

        const vehicleSize = 30;
        const explosionLifespan = 1000;

        // Vehicle class
        class Vehicle {
            constructor(x, y, vx, vy) {
                this.x = x;
                this.y = y;
                this.vx = vx;
                this.vy = vy;
                this.width = vehicleSize;
                this.height = vehicleSize;
                this.isActive = true;
                this.color = `hsl(${Math.random() * 360}, 100%, 50%)`;
            }

            draw() {
                ctx.fillStyle = this.color;
                ctx.fillRect(this.x, this.y, this.width, this.height);

                // Simple wheels
                ctx.fillStyle = 'black';
                ctx.fillRect(this.x + 5, this.y + this.height / 2 - 5, 10, 5);
                ctx.fillRect(this.x + this.width - 15, this.y + this.height / 2 - 5, 10, 5);
            }

            update(dt) {
                this.x += this.vx * dt;
                this.y += this.vy * dt;

                // Wrapping
                if (this.x < 0) this.x = canvas.width;
                if (this.x > canvas.width) this.x = 0;
                if (this.y < 0) this.y = canvas.height;
                if (this.y > canvas.height) this.y = 0;
            }
        }


        // ExplosionParticle class
        class ExplosionParticle {
            constructor(x, y, vx, vy, lifespan) {
                this.x = x;
                this.y = y;
                this.vx = vx;
                this.vy = vy;
                this.lifespan = lifespan;
                this.size = Math.random() * 5 + 2;
                this.color = 'white';
            }

            draw() {
                ctx.fillStyle = this.color;
                ctx.fillRect(this.x, this.y, this.size, this.size);
            }

            update(dt) {
                this.x += this.vx * dt;
                this.y += this.vy * dt;
                this.lifespan -= dt;
            }
        }


        function initialize() {
            vehicles = [];
            for (let i = 0; i < vehicleCount; i++) {
                const x = Math.random() * canvas.width;
                const y = Math.random() * canvas.height;
                const vx = (Math.random() - 0.5) * 100;
                const vy = (Math.random() - 0.5) * 100;
                vehicles.push(new Vehicle(x, y, vx, vy));
            }

            explosionParticles = [];
            simulationState = 'RUNNING';
        }


        function checkCollision() {
            for (let i = 0; i < vehicles.length; i++) {
                if (!vehicles[i].isActive) continue;
                for (let j = i + 1; j < vehicles.length; j++) {
                    if (!vehicles[j].isActive) continue;

                    const dx = vehicles[i].x - vehicles[j].x;
                    const dy = vehicles[i].y - vehicles[j].y;
                    const distance = Math.sqrt(dx * dx + dy * dy);

                    if (distance < vehicles[i].width / 2 + vehicles[j].width / 2) {
                        return { i, j };
                    }
                }
            }
            return null;
        }

        function triggerExplosion(collisionIndex1, collisionIndex2) {
            const vehicle1 = vehicles[collisionIndex1];
            const vehicle2 = vehicles[collisionIndex2];

            const collisionX = (vehicle1.x + vehicle2.x) / 2;
            const collisionY = (vehicle1.y + vehicle2.y) / 2;

            vehicle1.isActive = false;
            vehicle2.isActive = false;

            for (let i = 0; i < explosionParticleCount; i++) {
                const angle = Math.random() * 2 * Math.PI;
                const speed = Math.random() * 100 + 50;
                explosionParticles.push(new ExplosionParticle(
                    collisionX,
                    collisionY,
                    Math.cos(angle) * speed,
                    Math.sin(angle) * speed,
                    explosionLifespan
                ));
            }
            simulationState = 'EXPLODING';
            startTime = Date.now();
            boomText = {
                text: "BOOM!",
                x: canvas.width / 2,
                y: canvas.height / 2,
                size: 50,
                expansionRate: 2
            }
        }

        function update(dt) {
            if (simulationState === 'RUNNING') {
                for (const vehicle of vehicles) {
                    if (vehicle.isActive) {
                        vehicle.update(dt);
                    }
                }

                const collision = checkCollision();
                if (collision) {
                    triggerExplosion(collision.i, collision.j);
                }
            } else if (simulationState === 'EXPLODING') {
                for (const particle of explosionParticles) {
                    particle.update(dt);
                }

                explosionParticles = explosionParticles.filter(particle => particle.lifespan > 0);

                if (explosionParticles.length === 0) {
                    simulationState = 'RESTARTING';
                    startTime = Date.now();
                }
            } else if (simulationState === 'RESTARTING') {
                if (Date.now() - startTime >= 3000) {
                    initialize();
                }
            }
        }

        function draw() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            if (simulationState === 'RUNNING') {
                for (const vehicle of vehicles) {
                    if (vehicle.isActive) {
                        vehicle.draw();
                    }
                }
            } else if (simulationState === 'EXPLODING') {
                for (const particle of explosionParticles) {
                    particle.draw();
                }
                if(boomText) {
                    ctx.font = `${boomText.size}px sans-serif`;
                    ctx.fillStyle = 'white';
                    ctx.textAlign = 'center';
                    ctx.fillText(boomText.text, boomText.x, boomText.y);
                }
            }
        }

        function gameLoop(timestamp) {
            const dt = (timestamp - (startTime || timestamp)) / 1000; // Delta time in seconds

            update(dt);
            draw();

            startTime = timestamp;
            requestAnimationFrame(gameLoop);
        }

        initialize();
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

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: gemma-3-12b-it-qat-UD-Q4_K_XL.gguf -->
<!-- Prompt: vehicles.md -->
<!-- Generation Time: 29.69s -->
<!-- Fallback Used: False -->