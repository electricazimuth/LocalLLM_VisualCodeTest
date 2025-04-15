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

        // --- Your Code Goes Here ---

        let turretX = 50;
        let turretY = 50;
        let turretWidth = 30;
        let turretHeight = 30;
        let turretColor = 'blue';
        let projectileSpeed = 5;
        let projectileLifetime = 2;

        // --- Initial Setup ---
        function init() {
            // Set turret position
             turretX = W / 2;
             turretY = H / 2;
             turretWidth = 30;
            turretHeight = 30;
            turretColor = 'blue';

            // Initialize projectiles
            let projectiles = [];
            for (let i = 0; i < 10; i++) {
                projectiles.push({
                    x: turretX + i * projectileSpeed * 1.5,
                    y: turretY + i * projectileSpeed * 0.5,
                    vx: 0,
                    vy: 0,
                    color: 'red'
                });
            }
        }

        // --- Game Loop ---
        function gameLoop(timestamp) {
            // Clear canvas
            ctx.clearRect(0, 0, W, H);

            // --- Draw Logic ---
            ctx.fillStyle = turretColor;
            ctx.fillRect(turretX, turretY, turretWidth, turretHeight);

            // --- Update Logic ---

            // --- Calculate Angle ---
            let angle = Math.atan2(turretY - turretX, turretX - turretY);

            // --- Projectile Movement ---
            for (let i = 0; i < projectiles.length; i++) {
                projectiles[i].x += angle;
                projectiles[i].y += projectileSpeed;
                projectiles[i].vx += projectileSpeed;
                projectiles[i].vy += projectileSpeed;
            }

            // --- Collision Detection ---
            for (let i = 0; i < projectiles.length; i++) {
                for (let j = 0; j < canvas.width; j++) {
                    if (projectiles[i].x <= j && projectiles[i].x + projectiles[i].width >= W && projectiles[i].y <= j && projectiles[i].y + projectiles[i].height >= H) {
                        // Collision detected
                        // Destroy projectile
                        projectiles.splice(i, 1);
                        break;
                    }
                }
            }

            // --- Remove Projectiles ---
            projectiles = [];
            // --- Add Projectiles ---
            for (let i = 0; i < projectiles.length; i++) {
                if (projectiles[i].x < 0) {
                    projectiles.push(projectiles[i]);
                } else if (projectiles[i].x > W) {
                    projectiles.splice(i, 1);
                }
            }
        }

        // --- Initial Setup ---
        init();

        // --- Mouse Click Event ---
        document.addEventListener('mousemove', function(event) {
            const mouseX = event.clientX;
            const mouseY = event.clientY;

            // Normalize vector
            let nx = mouseX / W;
            let ny = mouseY / H;

            // Calculate direction
            let dx = nx;
            let dy = ny;

            // Normalize
            let normalizedDx = dx / (10);
            let normalizedDy = dy / (10);

            // Calculate velocity
            let vx = normalizedDx;
            let vy = normalizedDy;

            // Create new projectile
            let newProjectile = {
                x: turretX + vx * 1.5,
                y: turretY + vy * 0.5,
                vx: 0,
                vy: 0,
                color: 'red'
            };

            // Add to array
            projectiles.push(newProjectile);
        });

        // Start the loop
        requestAnimationFrame(gameLoop);
    </script>
</body>
</html>
```
 <!-- 12.98s -->