```html
<!DOCTYPE html>
<html>
<head>
    <title>Bouncing Balls</title>
    <style>
        body { margin: 0; overflow: hidden; background-color: #f0f0f0; }
        canvas { border: 1px solid black; background-color: #fff; display: block; margin: 20px auto; }
    </style>
</head>
<body>
    <canvas id="gameCanvas" width="500" height="500"></canvas>
    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const W = canvas.width;
        const H = canvas.height;
        const centerX = W / 2;
        const centerY = H / 2;

        // --- Constants ---
        const heptagonVertexRadius = 200; // Distance from center to heptagon vertices (px)
        const ballRadius = 10;            // Radius of all balls (px)
        const numBalls = 20;              // Number of balls
        const gravity = 500;              // Gravitational acceleration (px/s²)
        const damping = 0.8;              // Velocity damping factor (0.8 = 20% energy loss)
        const spinDamping = 0.9;          // Spin damping per second (0.9 = 10% spin loss per second)
        const omega = (2 * Math.PI) / 5000; // Heptagon angular velocity (rad/ms) - 5s per revolution
        const ballColors = [
            '#f8b862', '#f6ad49', '#f39800', '#f08300', '#ec6d51', '#ee7948', '#ed6d3d', '#ec6800', 
            '#ec6800', '#ee7800', '#eb6238', '#ea5506', '#ea5506', '#eb6101', '#e49e61', '#e45e32', 
            '#e17b34', '#dd7a56', '#db8449', '#d66a35'
        ];

        // --- Ball Class ---
        class Ball {
            constructor(id) {
                this.id = id;
                this.x = centerX;                      // Initial position (center)
                this.y = centerY;
                this.vx = (Math.random() - 0.5) * 2;  // Initial velocity (px/s) - random ±1
                this.vy = (Math.random() - 0.5) * 2;
                this.r = ballRadius;
                this.color = ballColors[id - 1];
                this.mass = 1;                        // All balls have same mass
                this.spinVel = (Math.random() - 0.5) * 0.2; // Initial spin (rad/s) - random ±0.1
                this.spinAngle = 0;                   // Current rotation angle for drawing number
            }

            update(elapsedMs) {
                // Apply gravity (convert ms to seconds)
                this.vy += gravity * (elapsedMs / 1000);

                // Update position (velocity is px/s, convert to px)
                this.x += this.vx * (elapsedMs / 1000);
                this.y += this.vy * (elapsedMs / 1000);

                // Update spin with damping (spinVel is rad/s)
                this.spinVel *= Math.pow(spinDamping, elapsedMs / 1000);
                this.spinAngle += this.spinVel * (elapsedMs / 1000);
                this.spinAngle %= (2 * Math.PI); // Keep angle within 0-2π
            }

            draw() {
                // Draw ball
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.r, 0, Math.PI * 2);
                ctx.fillStyle = this.color;
                ctx.fill();
                ctx.closePath();

                // Draw spinning number
                ctx.save();
                ctx.translate(this.x, this.y);
                ctx.rotate(this.spinAngle);
                ctx.fillStyle = 'black';
                ctx.font = '12px Arial';
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillText(this.id.toString(), 0, 0);
                ctx.restore();
            }
        }

        // --- Heptagon Utilities ---
        function getHeptagonVertices(rotationAngle) {
            const vertices = [];
            const sides = 7;
            for (let i = 0; i < sides; i++) {
                const angle = rotationAngle + (2 * Math.PI * i) / sides;
                vertices.push({
                    x: centerX + heptagonVertexRadius * Math.cos(angle),
                    y: centerY + heptagonVertexRadius * Math.sin(angle)
                });
            }
            return vertices;
        }

        function drawHeptagon(vertices) {
            ctx.beginPath();
            ctx.moveTo(vertices[0].x, vertices[0].y);
            vertices.forEach(v => ctx.lineTo(v.x, v.y));
            ctx.closePath();
            ctx.strokeStyle = 'blue';
            ctx.lineWidth = 2;
            ctx.stroke();
        }

        // --- Collision Detection/Response ---
        function checkHeptagonWallCollisions(ball, vertices) {
            const sides = vertices.length;
            for (let i = 0; i < sides; i++) {
                const v1 = vertices[i];
                const v2 = vertices[(i + 1) % sides];

                // Edge vector and vector from v1 to ball center
                const eX = v2.x - v1.x;
                const eY = v2.y - v1.y;
                const cX = ball.x - v1.x;
                const cY = ball.y - v1.y;

                // Project ball center onto edge
                const eDotE = eX * eX + eY * eY;
                if (eDotE === 0) continue;
                const t = Math.max(0, Math.min(1, (cX * eX + cY * eY) / eDotE));
                const pX = v1.x + t * eX;
                const pY = v1.y + t * eY;

                // Distance from ball center to closest edge point
                const dx = ball.x - pX;
                const dy = ball.y - pY;
                const distSq = dx * dx + dy * dy;
                if (distSq >= ball.r * ball.r) continue;

                // Resolve collision
                const dist = Math.sqrt(distSq);
                const delta = ball.r - dist;

                // Outward normal (CCW polygon)
                const nx = eY / Math.sqrt(eDotE);
                const ny = -eX / Math.sqrt(eDotE);

                // Push ball out of wall
                ball.x += nx * delta;
                ball.y += ny * delta;

                // Wall velocity at collision point (circular motion)
                const pwX = pX - centerX;
                const pwY = pY - centerY;
                const vwX = -omega * pwY;
                const vwY = omega * pwX;

                // Relative velocity and reflection
                const vrX = ball.vx - vwX;
                const vrY = ball.vy - vwY;
                const dot = vrX * nx + vrY * ny;
                if (dot > 0) continue;

                // Update velocity with damping
                ball.vx = (vrX - 2 * dot * nx) + vwX;
                ball.vy = (vrY - 2 * dot * ny) + vwY;
                ball.vx *= damping;
                ball.vy *= damping;
            }
        }

        function checkBallCollisions(balls) {
            const count = balls.length;
            for (let i = 0; i < count; i++) {
                for (let j = i + 1; j < count; j++) {
                    const a = balls[i];
                    const b = balls[j];

                    // Distance check
                    const dx = b.x - a.x;
                    const dy = b.y - a.y;
                    const distSq = dx * dx + dy * dy;
                    const minDistSq = (a.r + b.r) * (a.r + b.r);
                    if (distSq >= minDistSq) continue;

                    // Resolve overlap
                    const dist = Math.sqrt(distSq);
                    const delta = (a.r + b.r) - dist;
                    const nx = dx / dist;
                    const ny = dy / dist;
                    a.x -= nx * delta * 0.5;
                    a.y -= ny * delta * 0.5;
                    b.x += nx * delta * 0.5;
                    b.y += ny * delta * 0.5;

                    // Velocity exchange (elastic collision) with damping
                    const dot = (a.vx - b.vx) * nx + (a.vy - b.vy) * ny;
                    a.vx -= dot * nx;
                    a.vy -= dot * ny;
                    b.vx += dot * nx;
                    b.vy += dot * ny;

                    // Apply damping
                    a.vx *= damping;
                    a.vy *= damping;
                    b.vx *= damping;
                    b.vy *= damping;
                }
            }
        }

        // --- Initialization ---
        const balls = Array.from({ length: numBalls }, (_, i) => new Ball(i + 1));
        let lastTimestamp = 0;
        let rotationAngle = 0;

        // --- Animation Loop ---
        function gameLoop(timestamp) {
            const elapsedMs = timestamp - lastTimestamp || 16; // Prevent division by zero
            lastTimestamp = timestamp;

            // Clear canvas
            ctx.clearRect(0, 0, W, H);

            // Update heptagon rotation
            rotationAngle += omega * elapsedMs;
            rotationAngle %= (2 * Math.PI);
            const heptagonVertices = getHeptagonVertices(rotationAngle);

            // Update and check collisions
            balls.forEach(ball => ball.update(elapsedMs));
            balls.forEach(ball => checkHeptagonWallCollisions(ball, heptagonVertices));
            checkBallCollisions(balls);

            // Draw
            drawHeptagon(heptagonVertices);
            balls.forEach(ball => ball.draw());

            requestAnimationFrame(gameLoop);
        }

        // Start the simulation
        requestAnimationFrame(gameLoop);
    </script>
    <section id="notes">
        <h3>Simulation Notes:</h3>
        <ul>
            <li>Heptagon spins at 360°/5s (slow rotation for visible effect)</li>
            <li>Balls start at center with random initial velocity (±1 px/s)</li>
            <li>Gravity: 500 px/s² (realistic downward acceleration)</li>
            <li>Collision damping: 20% energy loss per impact (balls slow down realistically)</li>
            <li>Ball spin: Random initial spin (±0.1 rad/s) with 10% loss per second</li>
            <li>Collision detection: O(n²) pairwise check (efficient for 20 balls)</li>
            <li>For >30 balls: Add spatial partitioning (grid/quadtree) for optimization</li>
        </ul>
    </section>
</body>
</html>
```

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: Seed-OSS-36B-Instruct-UD-Q5_K_XL.gguf -->
<!-- Prompt: heptagon.md -->
<!-- Generation Time: 727.75s -->
<!-- Fallback Used: False -->