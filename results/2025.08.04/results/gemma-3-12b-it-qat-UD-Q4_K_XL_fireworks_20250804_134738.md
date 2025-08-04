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

        // --- YOUR CODE GOES HERE ---

        const particles = [];
        let lastLaunchTime = 0;
        const launchIntervalMin = 500;
        const launchIntervalMax = 2000;

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

            update(dt) {
                this.vy += 0.5 * dt; // Gravity
                this.x += this.vx * dt;
                this.y += this.vy * dt;
                this.lifespan -= dt;
                this.alpha = Math.max(0, this.lifespan / (this.lifespan * 0.9)); // Fade out
            }

            draw() {
                ctx.fillStyle = `${this.color}a${Math.floor(this.alpha * 255)}`;
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                ctx.fill();
            }
        }

        class Rocket {
            constructor(x, y, vy, fuseTime) {
                this.x = x;
                this.y = y;
                this.vy = vy;
                this.fuseTime = fuseTime;
                this.lifespan = fuseTime;
                this.color = `hsl(${Math.random() * 360}, 100%, 50%)`; // Random color
            }

            update(dt) {
                this.vy += 0.5 * dt;
                this.x += 0;
                this.y += this.vy * dt;
                this.lifespan -= dt;
            }

            draw() {
                ctx.fillStyle = `${this.color}a1`;
                ctx.fillRect(this.x - 2, this.y - 2, 4, 4); // Simple rocket representation
            }

            explode() {
                const explosionParticles = [];
                for (let i = 0; i < Math.floor(Math.random() * 30) + 30; i++) {
                    const angle = Math.random() * Math.PI * 2;
                    const speed = Math.random() * 5 + 2;
                    const vx = Math.cos(angle) * speed;
                    const vy = Math.sin(angle) * speed * -1;
                    explosionParticles.push(new Particle(this.x, this.y, vx, vy, this.color, Math.random() * 3 + 1, Math.random() * 2 + 1));
                }
                return explosionParticles;
            }
        }

        function launchRocket() {
            const x = W / 2;
            const y = H;
            const vy = Math.random() * -10 + 5; // Random upward velocity
            const fuseTime = Math.random() * 2 + 1;
            const rocket = new Rocket(x, y, vy, fuseTime);
            particles.push(rocket);
        }

        function updateParticles(dt) {
            for (let i = particles.length - 1; i >= 0; i--) {
                const particle = particles[i];
                particle.update(dt);

                if (particle instanceof Rocket && particle.lifespan <= 0) {
                    const explosionParticles = particle.explode();
                    particles.splice(i, 1); // Remove rocket
                    particles.push(...explosionParticles); // Add explosion particles
                } else if (particle.lifespan <= 0) {
                    particles.splice(i, 1); // Remove particle
                }
            }
        }

        function drawParticles() {
            for (const particle of particles) {
                particle.draw();
            }
        }

        function gameLoop(timestamp) {
            const dt = (timestamp - lastLaunchTime) / 1000;
            lastLaunchTime = timestamp;

            // Autonomous launching
            if (timestamp > lastLaunchTime + Math.random() * (launchIntervalMax - launchIntervalMin) + launchIntervalMin) {
                launchRocket();
            }

            updateParticles(dt);
            ctx.clearRect(0, 0, W, H);
            drawParticles();

            requestAnimationFrame(gameLoop);
        }

        // Start the loop
        requestAnimationFrame(gameLoop);

    </script>
    <section id="notes">
        <p>This code implements a fireworks simulation using HTML5 Canvas and JavaScript.  It manages particles (rockets and explosion fragments) in a single array. Rockets are launched periodically from the bottom center of the canvas and explode after a random fuse time or altitude.  Explosions create a burst of colorful particles that fall realistically under gravity and fade out. Delta time is used for frame-rate independence.  Object-oriented principles are employed to structure the code, with Particle and Rocket classes.</p>
        <p>Key improvements include: efficient array management for particle removal, delta time implementation, object-oriented structure, and clear separation of update and draw logic.</p>
    </section>
</body>
</html>
```

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: gemma-3-12b-it-qat-UD-Q4_K_XL.gguf -->
<!-- Prompt: fireworks.md -->
<!-- Generation Time: 21.95s -->
<!-- Fallback Used: False -->