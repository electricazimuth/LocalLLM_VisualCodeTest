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

        // Constants
        const TURRET_X = W / 2;
        const TURRET_Y = H - 10;
        const PROJECTILE_RADIUS = 5;
        const PROJECTILE_SPEED = 5;
        const FIRE_COOLDOWN = 500; // ms
        const PROJECTILE_LIFESPAN = 2000; // ms

        // Game state
        let turretAngle = 0;
        let canFire = true;
        let lastFiredTime = 0;
        const projectiles = [];

        // Turret class
        class Turret {
            constructor(x, y) {
                this.x = x;
                this.y = y;
            }

            draw() {
                ctx.fillStyle = 'brown';
                ctx.fillRect(this.x - 20, this.y - 10, 40, 20);
                ctx.beginPath();
                ctx.moveTo(this.x, this.y);
                ctx.lineTo(
                    this.x + Math.cos(turretAngle) * 50,
                    this.y - Math.sin(turretAngle) * 50
                );
                ctx.strokeStyle = 'black';
                ctx.stroke();
            }
        }

        // Projectile class
        class Projectile {
            constructor(x, y, vx, vy) {
                this.x = x;
                this.y = y;
                this.vx = vx;
                this.vy = vy;
                this.timeCreated = Date.now();
            }

            update() {
                this.x += this.vx;
                this.y += this.vy;
            }

            draw() {
                ctx.fillStyle = 'red';
                ctx.beginPath();
                ctx.arc(this.x, this.y, PROJECTILE_RADIUS, 0, Math.PI * 2);
                ctx.fill();
            }
        }

        // Event listeners
        canvas.addEventListener('mousemove', (e) => {
            const rect = canvas.getBoundingClientRect();
            const mouseX = e.clientX - rect.left;
            const mouseY = e.clientY - rect.top;

            turretAngle = Math.atan2(mouseY - TURRET_Y, mouseX - TURRET_X);
        });

        canvas.addEventListener('click', (e) => {
            if (!canFire) return;

            const rect = canvas.getBoundingClientRect();
            const mouseX = e.clientX - rect.left;
            const mouseY = e.clientY - rect.top;
            const direction = { x: mouseX - TURRET_X, y: mouseY - TURRET_Y };
            const length = Math.hypot(direction.x, direction.y);
            const normalized = { x: direction.x / length, y: direction.y / length };
            const velocity = { x: normalized.x * PROJECTILE_SPEED, y: normalized.y * PROJECTILE_SPEED };
            const projectile = new Projectile(TURRET_X, TURRET_Y, velocity.x, velocity.y);
            projectiles.push(projectile);
            lastFiredTime = Date.now();
            canFire = false;
            setTimeout(() => { canFire = true; }, FIRE_COOLDOWN);
        });

        function gameLoop(timestamp) {
            ctx.clearRect(0, 0, W, H);

            // Update
            projectiles.forEach((projectile, index) => {
                projectile.update();
                if (Date.now() - projectile.timeCreated > PROJECTILE_LIFESPAN) {
                    projectiles.splice(index, 1);
                }
            });

            // Draw
            const turret = new Turret(TURRET_X, TURRET_Y);
            turret.draw();
            projectiles.forEach((projectile) => {
                projectile.draw();
            });

            requestAnimationFrame(gameLoop);
        }

        requestAnimationFrame(gameLoop);

    </script>
    <section id="notes">
        <!-- Notes go here -->
    </section>
</body>
</html>
```

This HTML file creates a simple turret shooting game using only HTML, CSS, and JavaScript. The turret at the bottom of the canvas aims towards the mouse cursor and fires a projectile when clicked. Projectiles move until they go off-screen or their lifespan expires. The firing rate is limited by a cooldown.
 <!-- 52.67s -->