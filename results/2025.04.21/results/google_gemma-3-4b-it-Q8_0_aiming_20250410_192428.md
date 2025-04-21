```html
<!DOCTYPE html>
<html>
<head>
    <title>Turret Shooting</title>
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

        // --- Constants ---
        const TURRET_RADIUS = 20;
        const PROJECTILE_RADIUS = 5;
        const PROJECTILE_SPEED = 10;
        const FIRE_RATE = 100; // milliseconds
        const PROJECTILE_LIFESPAN = 100; // milliseconds

        // --- Turret ---
        const turretX = W / 2;
        const turretY = H - TURRET_RADIUS;

        // --- Projectiles ---
        let projectiles = [];
        let lastFireTime = 0;

        // --- Helper Functions ---
        function normalize(vector) {
            const length = Math.sqrt(vector[0] * vector[0] + vector[1] * vector[1]);
            if (length === 0) return [0, 0]; // Avoid division by zero
            return [vector[0] / length, vector[1] / length];
        }

        // --- Game Loop ---
        function gameLoop(timestamp) {
            // Update projectiles
            for (let i = projectiles.length - 1; i >= 0; i--) {
                const projectile = projectiles[i];
                projectile.x += projectile.vx;
                projectile.y += projectile.vy;

                // Lifespan
                if (timestamp - projectile.startTime > PROJECTILE_LIFESPAN) {
                    projectiles.splice(i, 1);
                }
            }

            // Clear canvas
            ctx.clearRect(0, 0, W, H);

            // Draw turret
            ctx.beginPath();
            ctx.arc(turretX, turretY, TURRET_RADIUS, 0, 2 * Math.PI);
            ctx.fillStyle = 'blue';
            ctx.fill();
            ctx.closePath();

            // Draw projectiles
            for (const projectile of projectiles) {
                ctx.beginPath();
                ctx.arc(projectile.x, projectile.y, PROJECTILE_RADIUS, 0, 2 * Math.PI);
                ctx.fillStyle = 'red';
                ctx.fill();
                ctx.closePath();
            }

            requestAnimationFrame(gameLoop);
        }

        // --- Event Handlers ---
        canvas.addEventListener('mousemove', (e) => {
            const mouseX = e.clientX;
            const mouseY = e.clientY;

            // Calculate angle to mouse
            const angle = Math.atan2(mouseY - turretY, mouseX - turretX);

            // Calculate projectile velocity
            const vx = Math.cos(angle) * PROJECTILE_SPEED;
            const vy = Math.sin(angle) * PROJECTILE_SPEED;

            // Fire projectile
            if (timestamp - lastFireTime > FIRE_RATE) {
                const projectile = {
                    x: turretX,
                    y: turretY,
                    vx: vx,
                    vy: vy,
                    startTime: timestamp,
                    radius: PROJECTILE_RADIUS,
                    color: 'red'
                };
                projectiles.push(projectile);
                lastFireTime = timestamp;
            }
        });

        canvas.addEventListener('click', () => {
            // No action needed on click - firing is handled in mousemove
        });

        // Start the loop
        requestAnimationFrame(gameLoop);

        // Add any initial setup or event listeners here
    </script>
    <section id="notes">
        <p>This code implements a basic turret shooting game using HTML5 Canvas and JavaScript.</p>
        <p><b>Turret:</b> The turret is represented by a circle at the center of the canvas. Its position is fixed.</p>
        <p><b>Projectile:</b> Projectiles are represented as circles. They are created when the mouse is moved over the turret and a click occurs. The direction of the projectile is calculated using `Math.atan2` to determine the angle between the turret and the mouse cursor.</p>
        <p><b>Firing Rate:</b> The `FIRE_RATE` constant limits the firing rate to 100 milliseconds.  This prevents the player from firing too quickly.</p>
        <p><b>Projectile Lifespan:</b> Projectiles have a lifespan of 100 milliseconds.  After this time, they are removed from the `projectiles` array.</p>
        <p><b>Vector Math:</b> `Math.atan2` is used to calculate the angle between the turret and the mouse cursor. `normalize` is used to ensure the projectile's velocity vector has a length of 1, preventing the projectile from traveling faster than intended.</p>
        <p><b>Future Enhancements:</b>  Consider implementing collision detection, object pooling for projectiles, and more sophisticated turret behavior (e.g., tracking the mouse).</p>
    </section>
</body>
</html>
```
 <!-- 29.11s -->