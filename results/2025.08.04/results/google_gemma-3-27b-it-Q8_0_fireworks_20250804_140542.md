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

        // Particle classes
        class Rocket {
            constructor() {
                this.x = W / 2;
                this.y = H;
                this.vx = (Math.random() - 0.5) * 2; // Slight horizontal variation
                this.vy = -Math.random() * 5 - 3; // Upward velocity
                this.gravity = 0.05;
                this.fuseTime = Math.random() * 1 + 1; // 1-2 seconds
                this.startTime = performance.now();
                this.exploded = false;
                this.color = '#' + Math.floor(Math.random()*16777215).toString(16);
            }

            update(deltaTime) {
                this.vy += this.gravity * deltaTime;
                this.y += this.vy * deltaTime;

                const timeElapsed = (performance.now() - this.startTime) / 1000;
                if (timeElapsed >= this.fuseTime) {
                    this.exploded = true;
                }
            }

            draw() {
                ctx.beginPath();
                ctx.arc(this.x, this.y, 2, 0, 2 * Math.PI);
                ctx.fillStyle = this.color;
                ctx.fill();
            }
        }

        class ExplosionParticle {
            constructor(x, y, vx, vy, color, size, lifespan) {
                this.x = x;
                this.y = y;
                this.vx = vx;
                this.vy = vy;
                this.gravity = 0.05;
                this.color = color;
                this.size = size;
                this.lifespan = lifespan;
                this.startTime = performance.now();
            }

            update(deltaTime) {
                this.vy += this.gravity * deltaTime;
                this.x += this.vx * deltaTime;
                this.y += this.vy * deltaTime;
                this.lifespan -= deltaTime;
            }

            draw() {
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size, 0, 2 * Math.PI);
                ctx.fillStyle = this.color;
                ctx.globalAlpha = this.lifespan > 0 ? this.lifespan : 0;
                ctx.fill();
                ctx.globalAlpha = 1; // Reset alpha
            }
        }


        // Particle management
        let particles = [];
        let launchTimer = 0;
        const launchIntervalMin = 0.5;
        const launchIntervalMax = 2;

        function launchRocket() {
            particles.push(new Rocket());
        }

        function createExplosion(x, y) {
            const numParticles = Math.floor(Math.random() * 50) + 30;
            for (let i = 0; i < numParticles; i++) {
                const angle = Math.random() * 2 * Math.PI;
                const speed = Math.random() * 5;
                const vx = Math.cos(angle) * speed;
                const vy = Math.sin(angle) * speed;
                const size = Math.random() * 2 + 1;
                const lifespan = Math.random() * 1 + 1;
                const rocketColor = particles[particles.length -1].color
                particles.push(new ExplosionParticle(x, y, vx, vy, rocketColor, size, lifespan));
            }
        }

        let lastTimestamp = 0;

        function gameLoop(timestamp) {
            const deltaTime = (timestamp - lastTimestamp) / 1000; // Convert to seconds
            lastTimestamp = timestamp;

            // Clear canvas
            ctx.clearRect(0, 0, W, H);

            // Update and draw particles
            for (let i = particles.length - 1; i >= 0; i--) {
                const particle = particles[i];

                if (particle instanceof Rocket) {
                    particle.update(deltaTime);
                    particle.draw();

                    if (particle.exploded) {
                        createExplosion(particle.x, particle.y);
                        particles.splice(i, 1); // Remove rocket after explosion
                    }
                } else if (particle instanceof ExplosionParticle) {
                    particle.update(deltaTime);
                    particle.draw();

                    if (particle.lifespan <= 0) {
                        particles.splice(i, 1); // Remove particle when lifespan is over
                    }
                }
            }

            // Launch new rockets
            launchTimer += deltaTime;
            if (launchTimer >= (Math.random() * (launchIntervalMax - launchIntervalMin) + launchIntervalMin)) {
                launchRocket();
                launchTimer = 0;
            }

            requestAnimationFrame(gameLoop);
        }

        // Start the loop
        requestAnimationFrame(gameLoop);

    </script>
    <section id="notes">
        <p>
            This code implements a fireworks simulation using JavaScript and the Canvas API.
            It features Rocket and ExplosionParticle classes for managing particles.
            The simulation includes autonomous rocket launches, realistic gravity,
            and fading explosion effects. The game loop is driven by requestAnimationFrame
            for smooth animation.  Delta time is used for frame-rate independence.
            Particles are removed from the array when their lifespan expires or the rocket explodes.
        </p>
    </section>
</body>
</html>
```

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: google_gemma-3-27b-it-Q8_0.gguf -->
<!-- Prompt: fireworks.md -->
<!-- Generation Time: 62.30s -->
<!-- Fallback Used: False -->