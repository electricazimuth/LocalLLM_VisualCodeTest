```html
<!DOCTYPE html>
<html>
<head>
    <title>Fireworks Simulation</title>
    <style>
        body { margin: 0; overflow: hidden; background-color: #111; } /* Dark background suggested */
        canvas { border: 1px solid #444; background-color: #000; display: block; margin: 20px auto; } /* Dark canvas bg */
    </style>
</head>
<body>
    <canvas id="gameCanvas" width="512" height="512"></canvas>
    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const W = canvas.width;
        const H = canvas.height;

        class Particle {
            constructor(x, y, vx, vy, color, size, lifespan) {
                this.x = x;
                this.y = y;
                this.vx = vx;
                this.vy = vy;
                this.color = color;
                this.size = size;
                this.lifespan = lifespan;
                this.alpha = 1;
            }

            update(deltaTime) {
                this.x += this.vx * deltaTime;
                this.y += this.vy * deltaTime;
                this.vy += 0.5 * deltaTime; // Gravity
                this.lifespan -= deltaTime;
                this.alpha = Math.max(0, this.lifespan / 3); // Fade out effect
            }

            draw() {
                ctx.fillStyle = this.color;
                ctx.globalAlpha = this.alpha;
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size, 0, 2 * Math.PI);
                ctx.fill();
                ctx.globalAlpha = 1;
            }
        }

        class Rocket extends Particle {
            constructor(x, y, vx, vy, color, size, fuseTime) {
                super(x, y, vx, vy, color, size, fuseTime);
                this.exploded = false;
            }

            update(deltaTime) {
                super.update(deltaTime);
                this.lifespan -= deltaTime;
                if (this.lifespan <= 0 && !this.exploded) {
                    this.exploded = true;
                    return 'explode';
                }
            }
        }

        let particles = [];

        function launchRocket() {
            const x = W / 2;
            const y = H;
            const vx = (Math.random() - 0.5) * 2;
            const vy = -(5 + Math.random() * 5);
            const color = `rgb(${Math.random() * 255}, ${Math.random() * 255}, ${Math.random() * 255})`;
            const size = 2 + Math.random() * 2;
            const fuseTime = 1 + Math.random() * 1;
            particles.push(new Rocket(x, y, vx, vy, color, size, fuseTime));
        }

        function explodeRocket(rocket) {
            const x = rocket.x;
            const y = rocket.y;
            const numParticles = 30 + Math.floor(Math.random() * 50);
            const color = rocket.color;

            for (let i = 0; i < numParticles; i++) {
                const vx = (Math.random() - 0.5) * 5;
                const vy = (Math.random() - 0.5) * 5;
                const size = 2 + Math.random() * 2;
                const lifespan = 1 + Math.random() * 2;
                particles.push(new Particle(x, y, vx, vy, color, size, lifespan));
            }
        }

        let lastTime = performance.now();

        function gameLoop(timestamp) {
            const deltaTime = (timestamp - lastTime) / 1000;
            lastTime = timestamp;

            ctx.clearRect(0, 0, W, H);

            particles = particles.filter(particle => {
                if (particle instanceof Rocket) {
                    const result = particle.update(deltaTime);
                    if (result === 'explode') {
                        explodeRocket(particle);
                        return false;
                    }
                } else {
                    particle.update(deltaTime);
                }
                return particle.lifespan > 0;
            });

            particles.forEach(particle => particle.draw());

            if (Math.random() < 0.01) {
                launchRocket();
            }

            requestAnimationFrame(gameLoop);
        }

        // Start the loop
        requestAnimationFrame(gameLoop);

        // Add any initial setup or event listeners here

    </script>
    <section id="notes">
        <!-- Add any notes here -->
    </section>
</body>
</html>
```

### Notes:
1. **Particle Management:** The `particles` array stores all active particles, including rockets and explosion fragments.
2. **Autonomous Launching:** New rockets are launched periodically using a random condition in the game loop.
3. **Firework Rocket:** The `Rocket` class inherits from `Particle` and includes additional properties and methods specific to rockets.
4. **Explosion Particles:** When a rocket explodes, it creates a burst of `Particle` objects with random velocities and lifespans.
5. **Game Loop:** The `requestAnimationFrame` function is used to create a smooth animation loop. The `deltaTime` is calculated to ensure frame-rate independent animation.
6. **Update Logic:** The update logic handles the position updates, gravity effects, and lifespan decrements for all particles.
7. **Draw Logic:** The draw logic renders each particle on the canvas, with fading effects based on remaining lifespan.
8. **Efficient Array Management:** The `filter` method is used to remove particles whose lifespan has run out, optimizing array management.

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: Mistral-Large-Instruct-2411-IQ2_XS.gguf -->
<!-- Prompt: fireworks.md -->
<!-- Generation Time: 595.00s -->
<!-- Fallback Used: False -->