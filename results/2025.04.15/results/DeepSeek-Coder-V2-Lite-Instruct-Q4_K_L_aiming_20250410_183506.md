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

        // Turret position
        const turret = {
            x: W / 2,
            y: H - 50,
            width: 50,
            height: 10,
            color: 'black'
        };

        // Projectile class
        class Projectile {
            constructor(x, y, vx, vy, radius, color) {
                this.x = x;
                this.y = y;
                this.vx = vx;
                this.vy = vy;
                this.radius = radius;
                this.color = color;
            }

            update() {
                this.x += this.vx;
                this.y += this.vy;
            }

            draw() {
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
                ctx.fillStyle = this.color;
                ctx.fill();
            }

            offScreen() {
                return this.x < 0 || this.x > W || this.y < 0 || this.y > H;
            }
        }

        let projectiles = [];
        const projectileSpeed = 5;
        const projectileRadius = 5;
        const projectileColor = 'red';
        let lastFireTime = 0;
        const cooldown = 200; // ms

        // Mouse event listener
        canvas.addEventListener('click', (event) => {
            const mouseX = event.clientX;
            const mouseY = event.clientY;
            const angle = Math.atan2(mouseY - turret.y, mouseX - turret.x);
            const vx = Math.cos(angle) * projectileSpeed;
            const vy = Math.sin(angle) * projectileSpeed;

            // Check cooldown
            if (Date.now() - lastFireTime < cooldown) return;
            lastFireTime = Date.now();

            // Create and add projectile
            const projectile = new Projectile(turret.x, turret.y, vx, vy, projectileRadius, projectileColor);
            projectiles.push(projectile);
        });

        function gameLoop() {
            // Clear canvas
            ctx.clearRect(0, 0, W, H);

            // Draw turret
            ctx.fillStyle = turret.color;
            ctx.fillRect(turret.x - turret.width / 2, turret.y - turret.height / 2, turret.width, turret.height);

            // Update and draw projectiles
            projectiles.forEach(projectile => {
                projectile.update();
                projectile.draw();
                if (projectile.offScreen()) {
                    projectiles = projectiles.filter(p => p !== projectile);
                }
            });

            requestAnimationFrame(gameLoop);
        }

        // Start the loop
        requestAnimationFrame(gameLoop);

    </script>
    <section id="notes">
        <p>This game includes a turret that aims at the mouse cursor and fires projectiles when clicked. Projectiles move in the direction they are fired and are removed when they go off-screen. The turret's position is fixed at the bottom center of the canvas.</p>
        <p>The cooldown feature prevents the turret from firing too rapidly, and the projectile class handles the movement and rendering of each projectile.</p>
    </section>
</body>
</html>
```
 <!-- 22.83s -->