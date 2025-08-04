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

        class Particle {
            constructor(x, y, vx, vy, color, size, lifespan) {
                this.x = x;
                this.y = y;
                this.vx = vx;
                this.vy = vy;
                this.color = color;
                this.size = size;
                this.lifespan = lifespan;
                this.alpha = 1; // Transparency
            }

            update(dt) {
                this.x += this.vx * dt;
                this.y += this.vy * dt;
                this.alpha -= dt / this.lifespan; // Fade out
            }

            draw() {
                ctx.fillStyle = `rgba(${this.color[0]}, ${this.color[1]}, ${this.color[2]}, ${this.alpha})`;
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size, 0, 2 * Math.PI);
                ctx.fill();
            }
        }

        class Rocket {
            constructor(x, y, vx, vy, explosionHeight, explosionParticles) {
                this.x = x;
                this.y = y;
                this.vx = vx;
                this.vy = vy;
                this.explosionHeight = explosionHeight;
                this.explosionParticles = explosionParticles;
                this.fuse = 1.5; // Seconds
                this.explosionTriggered = false;
            }

            update(dt) {
                this.x += this.vx * dt;
                this.y += this.vy * dt;
                this.fuse -= dt;

                if (this.y >= this.explosionHeight && !this.explosionTriggered) {
                    this.explode();
                }
            }

            draw() {
                ctx.fillStyle = 'yellow'; // Simple rocket representation
                ctx.beginPath();
                ctx.arc(this.x, this.y, 5, 0, 2 * Math.PI);
                ctx.fill();
            }

            explode() {
                this.explosionTriggered = true;
                for (let i = 0; i < this.explosionParticles; i++) {
                    const x = this.x + (Math.random() - 0.5) * 50;
                    const y = this.y + (Math.random() - 0.5) * 50;
                    const vx = (Math.random() - 0.5) * 10 - 5;
                    const vy = (Math.random() - 0.5) * 10 - 5;
                    const color = [Math.floor(Math.random() * 256), Math.floor(Math.random() * 256), Math.floor(Math.random() * 256)];
                    const size = Math.floor(Math.random() * 3) + 2;
                    const lifespan = Math.floor(Math.random() * 2) + 1;
                    const particle = new Particle(x, y, vx, vy, color, size, lifespan);
                    particles.push(particle);
                }
                rockets.splice(rockets.indexOf(this), 1); // Remove rocket
            }
        }

        let rockets = [];
        let particles = [];
        const particleCount = 500; // Adjust for performance
        const explosionParticleCount = 40;
        const minLaunchHeight = 0;
        const maxLaunchHeight = H;
        const minFuse = 1;
        const maxFuse = 2;

        function spawnRocket() {
            const x = Math.random() * W;
            const y = minLaunchHeight;
            const vx = (Math.random() - 0.5) * 8;
            const vy = -Math.random() * 10;
            const explosionHeight = Math.floor(Math.random() * H);
            const explosionParticles = explosionParticleCount;
            const fuse = Math.floor(Math.random() * (maxFuse - minFuse + 1)) + minFuse;

            const rocket = new Rocket(x, y, vx, vy, explosionHeight, explosionParticles);
            rockets.push(rocket);
        }

        function gameLoop(timestamp) {
            const dt = (timestamp - lastTimestamp) / 1000; // Delta time in seconds
            lastTimestamp = timestamp;

            // Launch new rockets
            if (Math.random() < 0.01) { // Adjust launch frequency
                spawnRocket();
            }

            // Update all particles
            for (let i = particles.length - 1; i >= 0; i--) {
                particles[i].update(dt);
                particles[i].draw();
                if (particles[i].alpha < 0) {
                    particles.splice(i, 1);
                }
            }

            // Update rockets
            for (let i = rockets.length - 1; i >= 0; i--) {
                rockets[i].update(dt);
                rockets[i].draw();
                if (rockets[i].explosionTriggered) {
                    // No need to manage explosion particles here, they are created in explode()
                }
                if (rockets[i].y > H) {
                    rockets.splice(i, 1);
                }
            }

            // Clear canvas
            ctx.fillStyle = '#000';
            ctx.fillRect(0, 0, W, H);

            requestAnimationFrame(gameLoop);
        }

        let lastTimestamp = 0;
        // Start the loop
        requestAnimationFrame(gameLoop);

        // Add any initial setup or event listeners here

    </script>
    <section id="notes">
        <!-- Notes about the implementation and potential improvements -->
        <h3>Notes:</h3>
        <ul>
            <li>**Object-Oriented Approach:** Using classes for `Particle` and `Rocket` provides better structure and organization.</li>
            <li>**Delta Time:** Calculating delta time ensures consistent animation speed regardless of the frame rate.</li>
            <li>**Array Management:** Iterating through particle and rocket arrays in reverse order before removing elements prevents index shifting issues.</li>
            <li>**Performance:** The `particleCount` variable allows adjusting the number of particles to balance visual effect and performance.</li>
            <li>**Launch Frequency:** The `Math.random() < 0.01` condition controls how often new rockets are launched.</li>
            <li>**Fading:** The `alpha` property and its gradual decrease create a realistic fading effect for the explosion particles.</li>
            <li>**Explosion Logic:** The `explode()` method creates a burst of particles at the rocket's explosion location.</li>
            <li>**Randomness:**  Randomness is used for particle positions, velocities, colors, and lifespans to create a diverse and unpredictable fireworks display.</li>
            <li>**Canvas Size:** The canvas size is set to 512x512. Adjust this as needed.</li>
        </ul>
    </section>
</body>
</html>
```

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: gemma-3n-E4B-it-UD-Q4_K_XL.gguf -->
<!-- Prompt: fireworks.md -->
<!-- Generation Time: 20.65s -->
<!-- Fallback Used: False -->