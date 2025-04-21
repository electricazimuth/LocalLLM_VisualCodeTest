```
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

        const turret = { x: W / 2, y: H - 30 };
        const projectiles = [];
        const projectileSpeed = 5;
        const projectileLifespan = 500;
        const cooldown = 200;
        let lastShotTime = 0;

        let mouseX = 0;
        let mouseY = 0;

        canvas.addEventListener('mousemove', (event) => {
            const rect = canvas.getBoundingClientRect();
            mouseX = event.clientX - rect.left;
            mouseY = event.clientY - rect.top;
        });

        canvas.addEventListener('click', (event) => {
            const now = Date.now();
            if (now - lastShotTime > cooldown) {
                lastShotTime = now;
                const dx = mouseX - turret.x;
                const dy = mouseY - turret.y;
                const distance = Math.sqrt(dx * dx + dy * dy);
                const vx = (dx / distance) * projectileSpeed;
                const vy = (dy / distance) * projectileSpeed;
                projectiles.push({ x: turret.x, y: turret.y, vx, vy, birthTime: now });
            }
        });

        function gameLoop(timestamp) {
            ctx.clearRect(0, 0, W, H);

            const dx = mouseX - turret.x;
            const dy = mouseY - turret.y;
            const angle = Math.atan2(dy, dx);

            ctx.translate(turret.x, turret.y);
            ctx.rotate(angle);
            ctx.fillStyle = 'black';
            ctx.fillRect(-10, -5, 20, 10);
            ctx.rotate(-angle);
            ctx.translate(-turret.x, -turret.y);

            const now = Date.now();
            for (let i = projectiles.length - 1; i >= 0; i--) {
                const projectile = projectiles[i];
                projectile.x += projectile.vx;
                projectile.y += projectile.vy;

                ctx.fillStyle = 'red';
                ctx.beginPath();
                ctx.arc(projectile.x, projectile.y, 3, 0, Math.PI * 2);
                ctx.fill();

                if (now - projectile.birthTime > projectileLifespan ||
                    projectile.x < 0 || projectile.x > W || projectile.y < 0 || projectile.y > H) {
                    projectiles.splice(i, 1);
                }
            }

            requestAnimationFrame(gameLoop);
        }

        requestAnimationFrame(gameLoop);
    </script>
    <section id="notes">
        This is a simple turret shooting game where the turret aims towards the mouse cursor and fires projectiles when clicked.
        The game includes features such as cooldown, projectile lifespan, and collision detection with the screen boundaries.
    </section>
</body>
</html>
```
 <!-- 92.01s -->