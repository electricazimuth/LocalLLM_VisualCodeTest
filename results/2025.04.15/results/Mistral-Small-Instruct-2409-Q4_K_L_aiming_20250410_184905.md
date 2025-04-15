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

        // Turret position
        const turretX = W / 2;
        const turretY = H - 40;

        // Projectile class
        class Projectile {
            constructor(x, y, vx, vy, size, color) {
                this.x = x;
                this.y = y;
                this.vx = vx;
                this.vy = vy;
                this.size = size;
                this.color = color;
            }

            update() {
                this.x += this.vx;
                this.y += this.vy;
            }

            draw() {
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                ctx.fillStyle = this.color;
                ctx.fill();
            }
        }

        let projectiles = [];
        let firingCooldown = false;

        // Mouse event listeners
        canvas.addEventListener('mousemove', (event) => {
            const rect = canvas.getBoundingClientRect();
            const mouseX = event.clientX - rect.left;
            const mouseY = event.clientY - rect.top;
            // Update turret angle
            const dx = mouseX - turretX;
            const dy = mouseY - turretY;
            const angle = Math.atan2(dy, dx);
            // Draw turret barrel
            ctx.save();
            ctx.translate(turretX, turretY);
            ctx.rotate(angle);
            ctx.beginPath();
            ctx.moveTo(0, 0);
            ctx.lineTo(50, 0);
            ctx.strokeStyle = 'black';
            ctx.stroke();
            ctx.restore();
        });

        canvas.addEventListener('click', (event) => {
            if (firingCooldown) return;
            const rect = canvas.getBoundingClientRect();
            const mouseX = event.clientX - rect.left;
            const mouseY = event.clientY - rect.top;
            const dx = mouseX - turretX;
            const dy = mouseY - turretY;
            const dist = Math.hypot(dx, dy);
            const vx = dx / dist * 5;
            const vy = dy / dist * 5;
            const projectile = new Projectile(turretX + 50 * Math.cos(angle), turretY + 50 * Math.sin(angle), vx, vy, 5, 'blue');
            projectiles.push(projectile);
            firingCooldown = true;
            setTimeout(() => {
                firingCooldown = false;
            }, 500); // 0.5 second cooldown
        });

        function gameLoop(timestamp) {
            ctx.clearRect(0, 0, W, H);

            // Update projectiles
            projectiles.forEach((projectile, index) => {
                projectile.update();
                if (projectile.x < 0 || projectile.x > W || projectile.y < 0 || projectile.y > H) {
                    projectiles.splice(index, 1);
                }
            });

            // Draw projectiles
            projectiles.forEach(projectile => projectile.draw());

            // Draw turret base
            ctx.fillStyle = 'gray';
            ctx.fillRect(turretX - 10, turretY, 20, 40);

            requestAnimationFrame(gameLoop);
        }

        // Start the loop
        requestAnimationFrame(gameLoop);

    </script>
    <section id="notes">
        <p>This simple web game features a turret that aims towards the mouse cursor and fires projectiles upon clicking. Basic vector math and trigonometry are used for aiming and projectile movement. Projectiles are removed once they go off-screen, and there is a cooldown period between shots.</p>
        <p>Future improvements could include target detection, improved graphics, and sound effects.</p>
    </section>
</body>
</html>
```

This code sets up a basic turret shooting game using plain JavaScript and the HTML5 Canvas API. The turret aims at the mouse cursor and fires projectiles upon clicking. Projectiles are drawn as small circles that move towards the cursor's position at the time of the click.
 <!-- 93.69s -->