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

        // --- YOUR CODE GOES HERE ---

        const turret = {
            x: W / 2,
            y: H - 50,
            rotation: 0,
            barrelLength: 30,
            fireCooldown: 500, // milliseconds
            lastFireTime: 0
        };

        const projectiles = [];

        function Projectile(x, y, vx, vy, size, color) {
            this.x = x;
            this.y = y;
            this.vx = vx;
            this.vy = vy;
            this.size = size;
            this.color = color;
            this.lifetime = 100; // in frames
        }

        function calculateAngle(turretX, turretY, mouseX, mouseY) {
            return Math.atan2(mouseY - turretY, mouseX - turretX);
        }

        function normalizeVector(x, y) {
            const length = Math.sqrt(x * x + y * y);
            if (length === 0) return { x: 0, y: 0 };
            return { x: x / length, y: y / length };
        }

        function gameLoop(timestamp) {
            const deltaTime = (timestamp - (gameLoop.lastTime || timestamp)) / 1000;
            gameLoop.lastTime = timestamp;

            // Clear canvas
            ctx.clearRect(0, 0, W, H);

            // Update turret rotation
            let mouseX = canvas.clientWidth / 2;
            let mouseY = canvas.clientHeight / 2;
            turret.rotation = calculateAngle(turret.x, turret.y, mouseX, mouseY);

            // Draw turret
            ctx.save();
            ctx.translate(turret.x, turret.y);
            ctx.rotate(turret.rotation);

            ctx.fillStyle = 'gray';
            ctx.fillRect(-20, -10, 40, 20); // Base

            ctx.strokeStyle = 'black';
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.moveTo(0, 0);
            ctx.lineTo(turret.barrelLength, 0);
            ctx.stroke();

            ctx.restore();

            // Update and draw projectiles
            for (let i = projectiles.length - 1; i >= 0; i--) {
                const projectile = projectiles[i];
                projectile.x += projectile.vx * deltaTime * 60;
                projectile.y += projectile.vy * deltaTime * 60;
                projectile.lifetime--;

                ctx.fillStyle = projectile.color;
                ctx.beginPath();
                ctx.arc(projectile.x, projectile.y, projectile.size, 0, 2 * Math.PI);
                ctx.fill();

                if (projectile.lifetime <= 0 || projectile.x < 0 || projectile.x > W || projectile.y < 0 || projectile.y > H) {
                    projectiles.splice(i, 1);
                }
            }

            requestAnimationFrame(gameLoop);
        }

        canvas.addEventListener('click', (event) => {
            const rect = canvas.getBoundingClientRect();
            const mouseX = event.clientX - rect.left;
            const mouseY = event.clientY - rect.top;

            const angle = calculateAngle(turret.x, turret.y, mouseX, mouseY);
            const direction = normalizeVector(mouseX - turret.x, mouseY - turret.y);
            const projectileSpeed = 200; // pixels per second

            const vx = direction.x * projectileSpeed;
            const vy = direction.y * projectileSpeed;

            const now = Date.now();
            if (now - turret.lastFireTime > turret.fireCooldown) {
                const projectile = new Projectile(turret.x + turret.barrelLength, turret.y, vx, vy, 5, 'red');
                projectiles.push(projectile);
                turret.lastFireTime = now;
            }
        });

        gameLoop.lastTime = null;
        requestAnimationFrame(gameLoop);

    </script>
    <section id="notes">
        <p>
            This code implements a basic turret shooting game using HTML5 Canvas. 
            Key features include: turret aiming, projectile firing, projectile movement, 
            projectile lifespan, and a firing cooldown. 
            The turret aims at the mouse cursor, and clicking fires a projectile in that direction.
        </p>
        <p>
            Vector math (`atan2`, `normalizeVector`) is used for aiming and projectile velocity.
            The game loop updates and draws all game elements.
        </p>
    </section>
</body>
</html>
```
 <!-- 69.60s -->