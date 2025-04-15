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

        // --- Helper Functions ---

        function createParticle(x, y, size, color, lifespan) {
            const particle = {
                x: x,
                y: y,
                velocity: { x: 0, y: 0 },
                lifespan: lifespan,
                color: color,
                size: size
            };

            // Apply physics
            particle.velocity.x += particle.velocity.y;
            particle.velocity.y += particle.velocity.x;

            // Update particle position
            particle.x += particle.velocity.x;
            particle.y += particle.velocity.y;

            // Fade out particle
            particle.color = color;
            particle.size = size - 2; // Reduce size by 2 pixels

            return particle;
        }

        // --- Game Logic ---

        let particles = [];
        let currentParticle = null;
        let particleCount = 0;

        // --- Initial Particle Generation ---
        for (let i = 0; i < 100; i++) {
            particles.push(createParticle(W / 2, H / 2, 1, "red", 1)); // Random position
        }

        // --- Game Loop ---
        function gameLoop(timestamp) {
            // Clear canvas (usually needed)
            // ctx.clearRect(0, 0, W, H);

            // --- Update logic ---

            // --- Draw logic ---

            requestAnimationFrame(gameLoop);
        }

        // --- Start the loop ---
        // requestAnimationFrame(gameLoop);

        // Add any initial setup or event listeners here
    </script>
    <section id="notes">
    
    </section>
</body>
</html>
```
 <!-- 6.74s -->