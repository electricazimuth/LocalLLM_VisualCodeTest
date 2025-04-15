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
                this.vx = (Math.random() - 0.5) * 2; // Random velocity between -1 and 1
                this.vy = (Math.random() - 0.5) * 2;
                this.lifespan = Math.random() * 2 + 1; // Lifespan between 1 and 3 seconds
                this.color = `rgba(0, 150, 255, ${Math.random()})`; // Semi-transparent blue
                this.size = Math.random() * 3 + 2; // Size between 2 and 5 pixels
                this.alpha = 1;
            }

            update(dt) {
                this.x += this.vx * dt;
                this.y += this.vy * dt;
                this.lifespan -= dt;
                this.alpha = Math.max(0, this.lifespan / (Math.random() * 2 + 1)); // Fade out
                // Simple gravity
                this.vy += 0.2 * dt;
            }

            draw() {
                ctx.fillStyle = this.color;
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                ctx.fill();
            }
        }

        let particles = [];
        let mouseX = 0;
        let mouseY = 0;
        let isMouseDown = false;

        canvas.addEventListener('mousedown', (e) => {
            isMouseDown = true;
            mouseX = e.clientX - canvas.offsetLeft;
            mouseY = e.clientY - canvas.offsetTop;
            emitParticles(mouseX, mouseY, 15); // Emit 15 particles
        });

        canvas.addEventListener('mouseup', () => {
            isMouseDown = false;
        });

        canvas.addEventListener('mousemove', (e) => {
            if (isMouseDown) {
                mouseX = e.clientX - canvas.offsetLeft;
                mouseY = e.clientY - canvas.offsetTop;
                emitParticles(mouseX, mouseY, 5); // Continuous emission while mouse down
            }
        });

        function emitParticles(x, y, numParticles) {
            for (let i = 0; i < numParticles; i++) {
                particles.push(new Particle(x, y));
            }
        }

        let lastTime = 0;

        function gameLoop(timestamp) {
            const dt = (timestamp - lastTime) / 1000; // Delta time in seconds
            lastTime = timestamp;

            // Clear canvas
            ctx.clearRect(0, 0, W, H);

            // Update and draw particles
            for (let i = particles.length - 1; i >= 0; i--) {
                particles[i].update(dt);
                particles[i].draw();

                if (particles[i].lifespan <= 0 || particles[i].alpha <= 0) {
                    particles.splice(i, 1);
                }
            }

            requestAnimationFrame(gameLoop);
        }

        // Start the loop
        requestAnimationFrame(gameLoop);

        // Add any initial setup or event listeners here

    </script>
    <section id="notes">
        <p>
            This code implements a particle emitter that spawns particles on mouse click.
            Each particle has a random velocity, lifespan, color, and size.  
            The particles fade out over their lifespan and are removed from the array when they die.
            Delta time is used for smooth animations.
            Continuous emission is enabled while the mouse button is held down.
            The array is iterated backwards when removing elements to avoid index issues.
        </p>
    </section>
</body>
</html>
```
 <!-- 58.76s -->