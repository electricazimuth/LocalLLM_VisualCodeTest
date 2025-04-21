<!DOCTYPE html>
<html>
<head>
    <title>Particle Emitter</title>
    <style>
        body { margin: 0; overflow: hidden; background-color: #f0f0f0; }
        canvas { border: 1px solid black; background-color: #fff; display: block; margin: 20px auto; }
    </style>
</head>
<body>
    <canvas id="gameCanvas" width="800" height="600"></canvas>
    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const W = canvas.width;
        const H = canvas.height;

        // --- YOUR CODE GOES HERE ---

        class Particle {
            constructor(x, y) {
                this.x = x;
                this.y = y;
                this.vx = Math.random() * 5 - 2.5;
                this.vy = Math.random() * 5 - 2.5;
                this.lifespan = Math.random() * 3 + 1;
                this.color = `rgba(${Math.floor(Math.random() * 255)}, ${Math.floor(Math.random() * 255)}, ${Math.floor(Math.random() * 255)}, 1)`;
                this.size = Math.random() * 3 + 2;
            }

            update(deltaTime) {
                this.x += this.vx * deltaTime;
                this.y += this.vy * deltaTime;
                this.lifespan -= deltaTime;
            }

            draw() {
                ctx.fillStyle = this.color;
                ctx.fillRect(this.x, this.y, this.size, this.size);
            }
        }

        let particles = [];

        function createParticles(x, y) {
            for (let i = 0; i < 15; i++) {
                particles.push(new Particle(x, y));
            }
        }

        function gameLoop(timestamp) {
            ctx.clearRect(0, 0, W, H);

            const deltaTime = timestamp - lastTime;
            lastTime = timestamp;

            // Update and remove dead particles
            particles = particles.filter(particle => {
                particle.update(deltaTime);
                if (particle.lifespan <= 0) {
                    return false;
                }
                particle.draw();
                return true;
            });

            requestAnimationFrame(gameLoop);
        }

        let lastTime = 0;

        canvas.addEventListener('click', (e) => {
            createParticles(e.clientX, e.clientY);
        });

        canvas.addEventListener('mousedown', (e) => {
            createParticles(e.clientX, e.clientY);
            interval = setInterval(() => {
                createParticles(e.clientX, e.clientY);
            }, 100);
        });

        canvas.addEventListener('mouseup', () => {
            clearInterval(interval);
        });

        requestAnimationFrame(gameLoop);

    </script>
    <section id="notes">
        <p>This code creates a simple particle emitter that spawns particles from the mouse click position. The particles have a random velocity and lifespan, and they fade out over time.</p>
        <p>Press and hold the mouse button to create a continuous stream of particles.</p>
    </section>
</body>
</html>
```

This code creates a particle emitter that meets the given requirements. It uses the `class` syntax to define a `Particle` class with properties for position, velocity, lifespan, color, and size. The `update` method updates the particle's position and decreases its lifespan, and the `draw` method draws the particle as a small square.

The `gameLoop` function updates and removes dead particles, and then draws the remaining particles. The `createParticles` function creates a burst of particles at a given position.

The code also includes event listeners for mouse clicks and mouse button press/release, which create a burst of particles or a continuous stream of particles, respectively.
 <!-- 42.00s -->