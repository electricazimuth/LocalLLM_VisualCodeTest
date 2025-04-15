```html
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

        // Particle class
        class Particle {
            constructor(x, y, lifespan, color, size) {
                this.x = x;
                this.y = y;
                this.vx = Math.random() * 2 - 1; // Random velocity x
                this.vy = Math.random() * 2 - 1; // Random velocity y
                this.lifespan = lifespan; // Lifespan in seconds
                this.color = color;
                this.size = size;
            }

            update() {
                this.x += this.vx;
                this.y += this.vy;
                this.lifespan -= 0.01; // Decrease lifespan
            }

            draw() {
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                ctx.fillStyle = this.color;
                ctx.fill();
            }

            isDead() {
                return this.lifespan <= 0;
            }
        }

        let particles = [];

        function createParticles(x, y) {
            for (let i = 0; i < 20; i++) {
                const lifespan = Math.random() * 2 + 1; // Random lifespan between 1 and 3 seconds
                const color = `rgba(0, 0, 0, ${Math.random() * 0.5 + 0.5})`; // Random alpha between 0.5 and 1
                const size = Math.random() * 3 + 2; // Random size between 2 and 5
                particles.push(new Particle(x, y, lifespan, color, size));
            }
        }

        function gameLoop(timestamp) {
            ctx.clearRect(0, 0, W, H);

            // Update particles
            particles.forEach(particle => {
                particle.update();
                particle.draw();
            });

            // Remove dead particles
            particles = particles.filter(particle => !particle.isDead());

            requestAnimationFrame(gameLoop);
        }

        // Add event listener for mouse click
        canvas.addEventListener('click', (event) => {
            const x = event.clientX;
            const y = event.clientY;
            createParticles(x, y);
        });

        // Start the loop
        requestAnimationFrame(gameLoop);

        // Add any initial setup or event listeners here

    </script>
    <section id="notes">
        <p>This simple particle emitter demonstrates basic particle creation and management using JavaScript and the HTML5 Canvas API. Particles are spawned on mouse click, move randomly, and fade out over time. The game loop updates particle positions and checks for lifespan expiration to remove particles that have run out of time.</p>
    </section>
</body>
</html>
```
 <!-- 17.58s -->