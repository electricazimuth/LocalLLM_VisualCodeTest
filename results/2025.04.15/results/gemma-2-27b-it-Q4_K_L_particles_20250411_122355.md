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

        const particles = [];
        let lastTimestamp = 0;

        class Particle {
            constructor(x, y) {
                this.x = x;
                this.y = y;
                this.vx = (Math.random() - 0.5) * 5; // Random velocity
                this.vy = (Math.random() - 0.5) * 5;
                this.lifespan = Math.random() * 2 + 1; // 1-3 seconds
                this.size = Math.random() * 3 + 2;
                this.color = `hsl(${Math.random() * 360}, 100%, 50%)`;
            }

            update(deltaTime) {
                this.x += this.vx * deltaTime;
                this.y += this.vy * deltaTime;
                this.lifespan -= deltaTime;
            }

            draw() {
                ctx.fillStyle = this.color;
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                ctx.fill();
            }
        }

        function createParticles(x, y) {
            for (let i = 0; i < 20; i++) {
                particles.push(new Particle(x, y));
            }
        }

        function updateParticles(timestamp) {
            const deltaTime = (timestamp - lastTimestamp) / 1000; // Delta time in seconds
            lastTimestamp = timestamp;

            for (let i = particles.length - 1; i >= 0; i--) {
                particles[i].update(deltaTime);

                if (particles[i].lifespan <= 0) {
                    particles.splice(i, 1);
                }
            }
        }

        function drawParticles() {
            ctx.clearRect(0, 0, W, H); // Clear canvas

            for (const particle of particles) {
                particle.draw();
            }
        }

        function gameLoop(timestamp) {
            updateParticles(timestamp);
            drawParticles();
            requestAnimationFrame(gameLoop);
        }

        canvas.addEventListener('mousedown', (event) => {
            createParticles(event.clientX, event.clientY);
        });

        canvas.addEventListener('mousemove', (event) => {
            if (canvas.getContext('2d').isPointInPath(event.clientX, event.clientY)) {
                createParticles(event.clientX, event.clientY);
            }
        });

        // Start the loop
        requestAnimationFrame(gameLoop);

        // Add any initial setup or event listeners here

    </script>
    <section id="notes">
        <h3>Notes</h3>
        <ul>
            <li>Particles are stored in an array and updated/drawn in a loop.</li>
            <li>Delta time is used to ensure smooth animations across different frame rates.</li>
            <li>Particles are removed from the array when their lifespan reaches zero.</li>
            <li>The code includes event listeners for mouse clicks and movement to spawn particles.</li>
            <li>You can adjust the number of particles, lifespan, size, and other parameters in the Particle class.</li>
        </ul>
    </section>
</body>
</html>
```

**Explanation:**

1. **Particle Class:**
   - Encapsulates particle properties (position, velocity, lifespan, size, color).
   - `update()` method updates position based on velocity and reduces lifespan using delta time.
   - `draw()` method draws the particle as a circle.

2. **Particle Management:**
   - `particles` array stores all active particles.
   - `createParticles()` adds new particles at a given location.
   - `updateParticles()` iterates through the array, updates each particle, and removes particles with lifespan <= 0.

3. **Rendering Loop:**
   - `gameLoop()` handles the animation loop using `requestAnimationFrame()`.
   - It calls `updateParticles()` to update particle states and `drawParticles()` to render them on the canvas.

4. **Event Handling:**
   - `mousedown` and `mousemove` event listeners create particles when the mouse is clicked or dragged on the canvas.

**Key Improvements:**

- **Delta Time:** Uses `deltaTime` for smooth animation regardless of frame rate.
- **Efficient Particle Removal:** Removes particles from the array while iterating backwards to avoid index issues.
- **Object-Oriented:** Uses a `Particle` class for better organization and reusability.
 <!-- 99.92s -->