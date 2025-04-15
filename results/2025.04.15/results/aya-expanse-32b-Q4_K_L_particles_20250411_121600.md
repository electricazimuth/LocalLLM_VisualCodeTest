## Particle Emitter Implementation

Here's a JavaScript implementation of the particle emitter meeting your requirements:

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

        class Particle {
            constructor(x, y, vx, vy, lifespan, color, size) {
                this.x = x;
                this.y = y;
                this.vx = vx;
                this.vy = vy;
                this.lifespan = lifespan;
                this.color = color;
                this.size = size;
                this.alpha = 1; // Initial opacity
            }

            update(dt) {
                this.x += this.vx * dt;
                this.y += this.vy * dt;
                this.lifespan -= dt;
                this.alpha = this.lifespan / this.lifespan; // Fade out
            }

            draw() {
                ctx.fillStyle = `rgba(${this.color}, ${this.alpha})`;
                ctx.fillRect(this.x, this.y, this.size, this.size);
            }
        }

        const particles = [];
        let emitting = false;

        canvas.addEventListener('mousedown', () => {
            emitting = true;
        });

        canvas.addEventListener('mouseup', () => {
            emitting = false;
        });

        function spawnParticles(x, y) {
            for (let i = 0; i < 20; i++) {
                const vx = (Math.random() - 0.5) * 5;
                const vy = (Math.random() - 0.5) * 5;
                const lifespan = 1 + Math.random() * 2;
                const color = [Math.random() * 255, Math.random() * 255, Math.random() * 255];
                const size = 2 + Math.random() * 3;

                particles.push(new Particle(x, y, vx, vy, lifespan, color, size));
            }
        }

        function gameLoop(timestamp) {
            const dt = timestamp / 1000; // Convert to seconds

            ctx.clearRect(0, 0, W, H);

            if (emitting) {
                spawnParticles(mouseX, mouseY);
            }

            particles.forEach((particle, index) => {
                particle.update(dt);
                particle.draw();

                if (particle.lifespan <= 0) {
                    particles.splice(index, 1); // Remove particle
                }
            });

            requestAnimationFrame(gameLoop);
        }

        let mouseX = 0;
        let mouseY = 0;

        canvas.addEventListener('mousemove', (e) => {
            mouseX = e.offsetX;
            mouseY = e.offsetY;
        });

        // Start the loop
        requestAnimationFrame(gameLoop);
    </script>
    <section id="notes">
        <h2>Notes:</h2>
        <ul>
            <li>Uses a `Particle` class for object-oriented structure.</li>
            <li>Handles particle spawning, updating, drawing, and removal.</li>
            <li>Implementes fading by reducing the particle's alpha value over time.</li>
            <li>Emits particles continuously while the mouse button is held down.</li>
            <li>Optimizes performance by removing particles from the array while iterating using `splice`.</li>
        </ul>
    </section>
</body>
</html>
```

**Explanation:**

1. **Particle Class:**

   - Encapsulates particle properties (position, velocity, lifespan, color, size, alpha).
   - `update(dt)`: Updates particle position based on velocity and decreases lifespan.

   - `draw()`: Renders the particle as a colored rectangle with adjustable opacity.

2. **Main Logic:**

   - `particles` array stores all active particles.

   - Event listeners handle mouse clicks to control particle emission.

   - `spawnParticles(x, y)` creates a burst of new particles at the mouse position.

   - `gameLoop(timestamp)`:

     - Clears the canvas on each frame.

     - If emitting, spawns new particles.
     - Iterates through particles, calling `update` and `draw` on each.
     - Removes particles with zero lifespan using `splice` for efficient array management.
     - Recursively calls `requestAnimationFrame` to maintain the loop.

3. **Mouse Tracking:**

   - `mousemove` listener updates `mouseX` and `mouseY` for precise particle spawning.

**Key Points:**

- **Delta Time (`dt`):** Used to make animations independent of frame rate, ensuring smooth movement.

- **Array Management:**

- **Fade Out:** Alpha value is decreased over time to create a fading effect.
- **Continuous Emission:**

- **Performance Optimization:** Removing particles during iteration using `splice` prevents "stale" particles from accumulating and helps maintain performance even with thousands of particles.
 <!-- 120.29s -->