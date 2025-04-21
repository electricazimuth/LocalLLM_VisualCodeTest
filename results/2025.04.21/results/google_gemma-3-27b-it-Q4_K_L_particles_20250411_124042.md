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

        // --- YOUR CODE GOES HERE ---

        class Particle {
            constructor(x, y) {
                this.x = x;
                this.y = y;
                this.vx = (Math.random() - 0.5) * 5; // Random horizontal velocity
                this.vy = (Math.random() - 0.5) * 5; // Random vertical velocity
                this.lifespan = (Math.random() * 2) + 1; // Lifespan between 1 and 3 seconds
                this.color = `rgba(0, 100, 255, ${Math.random()})`; // Random blueish color with random alpha
                this.size = Math.random() * 3 + 2; // Size between 2 and 5 pixels
                this.gravity = 0.05; // Apply a small downward force
            }

            update(deltaTime) {
                this.x += this.vx;
                this.y += this.vy;
                this.vy += this.gravity; // Apply gravity
                this.lifespan -= deltaTime;
            }

            draw() {
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                ctx.fillStyle = this.color;
                ctx.fill();
                ctx.closePath();
            }

            isDead() {
                return this.lifespan <= 0;
            }
        }

        let particles = [];
        let isEmitting = false;

        canvas.addEventListener('mousedown', (e) => {
            isEmitting = true;
            emitParticles(e.clientX, e.clientY);
        });

        canvas.addEventListener('mouseup', () => {
            isEmitting = false;
        });

        canvas.addEventListener('mousemove', (e) => {
            if (isEmitting) {
                emitParticles(e.clientX, e.clientY);
            }
        });

        function emitParticles(x, y) {
            const numParticles = Math.floor(Math.random() * 10) + 10; // 10-20 particles
            for (let i = 0; i < numParticles; i++) {
                particles.push(new Particle(x, y));
            }
        }
        
        let lastTime = 0;

        function gameLoop(timestamp) {
            const deltaTime = (timestamp - lastTime) / 1000; // Calculate delta time in seconds
            lastTime = timestamp;

            ctx.clearRect(0, 0, W, H);

            // Update and draw particles
            for (let i = particles.length - 1; i >= 0; i--) {
                const particle = particles[i];
                particle.update(deltaTime);
                particle.draw();

                if (particle.isDead()) {
                    particles.splice(i, 1); // Remove dead particles
                }
            }

            if (isEmitting) {
                //Emit particles continuously while mouse is held down
                emitParticles(canvas.getBoundingClientRect().left + Math.random() * canvas.width, canvas.getBoundingClientRect().top + Math.random() * canvas.height);
            }

            requestAnimationFrame(gameLoop);
        }

        // Start the loop
        requestAnimationFrame(gameLoop);

        // Add any initial setup or event listeners here

    </script>
    <section id="notes">
        <p>Key improvements and explanations:</p>
        <ul>
            <li><b>Particle Class:</b> Encapsulates particle properties and behavior for better organization.</li>
            <li><b>Delta Time:</b>  Uses `deltaTime` to ensure consistent animation speed regardless of frame rate.  Calculated using `requestAnimationFrame` timestamps.</li>
            <li><b>Particle Lifespan:</b> Each particle has a lifespan, and they are removed when it reaches zero.</li>
            <li><b>Randomness:</b> Random velocities, colors, and sizes create a more natural look.</li>
            <li><b>Gravity:</b> A simple gravity effect is added to make the particles fall.</li>
            <li><b>Array Management:</b>  Particles are stored in an array, and dead particles are removed using `splice` while iterating backwards to avoid index issues.</li>
            <li><b>Continuous Emission:</b> The emitter now emits particles continuously while the mouse button is held down and the mouse moves.  Mouse position is used to emit.</li>
            <li><b>Event Listeners:</b>  Uses `mousedown`, `mouseup`, and `mousemove` event listeners to control emission.</li>
            <li><b>Performance:</b> Removing dead particles helps to maintain performance, especially with a large number of particles.</li>
        </ul>
    </section>
</body>
</html>
```
 <!-- 107.58s -->