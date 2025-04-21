Below is a complete HTML file with JavaScript and CSS that implements the described turret shooting game. The game includes a turret that aims at the mouse cursor, fires projectiles upon clicking, and manages active projectiles.

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

        const turretPos = { x: W / 2, y: H - 50 };
        const projectileSpeed = 5;
        const firingCooldown = 200; // milliseconds
        const projectileLifespan = 3000; // milliseconds

        let mousePos = { x: 0, y: 0 };
        let lastFired = 0;
        let projectiles = [];

        class Projectile {
            constructor(x, y, vx, vy) {
                this.x = x;
                this.y = y;
                this.vx = vx;
                this.vy = vy;
                this.size = 5;
                this.color = 'red';
                this.createdAt = Date.now();
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
                ctx.closePath();
            }

            isOffScreen() {
                return this.x < 0 || this.x > W || this.y < 0 || this.y > H;
            }

            isExpired() {
                return Date.now() - this.createdAt > projectileLifespan;
            }
        }

        function drawTurret() {
            ctx.save();
            ctx.translate(turretPos.x, turretPos.y);
            ctx.rotate(Math.atan2(mousePos.y - turretPos.y, mousePos.x - turretPos.x));
            ctx.fillStyle = 'black';
            ctx.fillRect(-10, -20, 20, 40); // Base
            ctx.fillRect(0, -40, 2, 20); // Barrel
            ctx.restore();
        }

        function updateProjectiles() {
            projectiles = projectiles.filter(p => !p.isOffScreen() && !p.isExpired());
            projectiles.forEach(p => p.update());
        }

        function drawProjectiles() {
            projectiles.forEach(p => p.draw());
        }

        function handleMouseMove(event) {
            const rect = canvas.getBoundingClientRect();
            mousePos = { x: event.clientX - rect.left, y: event.clientY - rect.top };
        }

        function handleMouseClick() {
            if (Date.now() - lastFired < firingCooldown) return;

            const directionX = mousePos.x - turretPos.x;
            const directionY = mousePos.y - turretPos.y;
            const magnitude = Math.sqrt(directionX * directionX + directionY * directionY);
            const normalizedX = directionX / magnitude;
            const normalizedY = directionY / magnitude;

            const velocityX = normalizedX * projectileSpeed;
            const velocityY = normalizedY * projectileSpeed;

            const projectile = new Projectile(turretPos.x, turretPos.y, velocityX, velocityY);
            projectiles.push(projectile);

            lastFired = Date.now();
        }

        function gameLoop(timestamp) {
            ctx.clearRect(0, 0, W, H);

            updateProjectiles();
            drawTurret();
            drawProjectiles();

            requestAnimationFrame(gameLoop);
        }

        canvas.addEventListener('mousemove', handleMouseMove);
        canvas.addEventListener('click', handleMouseClick);

        requestAnimationFrame(gameLoop);
    </script>
    <section id="notes">
        <!-- Notes: -->
        <!-- The turret aims at the mouse cursor and fires projectiles when clicked. -->
        <!-- Projectiles have a lifespan and are removed if they go off-screen or expire. -->
        <!-- Firing rate is limited by a cooldown period. -->
    </section>
</body>
</html>
```

### Explanation:
1. **Turret Position:** The turret is positioned at the bottom center of the canvas.
2. **Projectile Class:** Defines a projectile with position, velocity, size, color, and lifespan.
3. **Mouse Position Tracking:** Handles mouse movement to update the turret's aim direction.
4. **Game Loop:** Updates and draws the turret and projectiles, and handles removing off-screen or expired projectiles.
5. **Mouse Click Event:** Fires a projectile towards the mouse position with a cooldown to limit firing rate.

This code provides a basic framework for the game, adhering to the specified requirements and desirable features.
 <!-- 77.16s -->