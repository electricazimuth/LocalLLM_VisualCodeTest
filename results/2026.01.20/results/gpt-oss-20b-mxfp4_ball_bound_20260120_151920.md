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
    <canvas id="gameCanvas" width="800" height="600"></canvas>
    <script>
        "use strict";

        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const W = canvas.width;
        const H = canvas.height;

        /* ------------------------------------------------------------------
           Configuration
        ------------------------------------------------------------------ */
        const NUM_BALLS = 50;          // Number of balls to create
        const GRAVITY = 0.3;           // Gravity acceleration (pixels/frame²)
        const DAMPING = 0.8;           // Energy loss when hitting walls
        const RESTITUTION = 0.9;       // Energy loss in ball‑ball collisions
        const CELL_SIZE = 50;          // Cell size for spatial partitioning

        /* ------------------------------------------------------------------
           Ball class
        ------------------------------------------------------------------ */
        class Ball {
            constructor(id, x, y, vx, vy, r, color) {
                this.id = id;          // Unique identifier – useful for collision checks
                this.x = x;            // Current x position
                this.y = y;            // Current y position
                this.vx = vx;          // Current velocity x
                this.vy = vy;          // Current velocity y
                this.r = r;            // Radius
                this.mass = r * r;     // Mass proportional to area (or use a constant)
                this.color = color;    // Fill color
            }

            /* Update ball physics */
            update() {
                // Apply gravity
                this.vy += GRAVITY;

                // Update position
                this.x += this.vx;
                this.y += this.vy;

                // Wall collision – left/right
                if (this.x - this.r < 0) {
                    this.x = this.r;
                    this.vx = -this.vx * DAMPING;
                } else if (this.x + this.r > W) {
                    this.x = W - this.r;
                    this.vx = -this.vx * DAMPING;
                }

                // Wall collision – top/bottom
                if (this.y - this.r < 0) {
                    this.y = this.r;
                    this.vy = -this.vy * DAMPING;
                } else if (this.y + this.r > H) {
                    this.y = H - this.r;
                    this.vy = -this.vy * DAMPING;
                }
            }

            /* Draw the ball */
            draw(ctx) {
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.r, 0, Math.PI * 2);
                ctx.fillStyle = this.color;
                ctx.fill();
            }
        }

        /* ------------------------------------------------------------------
           Helper functions
        ------------------------------------------------------------------ */

        // Random number in [min, max)
        function rand(min, max) {
            return Math.random() * (max - min) + min;
        }

        // Random color using HSL for nice variety
        function randomColor() {
            const hue = rand(0, 360);
            const sat = rand(50, 90);
            const light = rand(40, 70);
            return `hsl(${hue},${sat}%,${light}%)`;
        }

        // Create balls without initial overlaps (approximate)
        function createBalls() {
            const balls = [];
            let attempts = 0;
            while (balls.length < NUM_BALLS && attempts < NUM_BALLS * 20) {
                const r = rand(10, 20);
                const x = rand(r, W - r);
                const y = rand(r, H - r);
                const vx = rand(-3, 3);
                const vy = rand(-3, 3);
                const color = randomColor();

                const newBall = new Ball(balls.length, x, y, vx, vy, r, color);

                // Check for overlap with existing balls
                let overlap = false;
                for (const b of balls) {
                    const dx = b.x - newBall.x;
                    const dy = b.y - newBall.y;
                    const dist = Math.hypot(dx, dy);
                    if (dist < b.r + newBall.r) {
                        overlap = true;
                        break;
                    }
                }

                if (!overlap) {
                    balls.push(newBall);
                }
                attempts++;
            }
            return balls;
        }

        /* Spatial grid for collision detection */
        const gridCols = Math.ceil(W / CELL_SIZE);
        const gridRows = Math.ceil(H / CELL_SIZE);
        const gridSize = gridCols * gridRows;

        function clearGrid(grid) {
            for (let i = 0; i < gridSize; i++) {
                grid[i] = [];
            }
        }

        function addToGrid(grid, ball) {
            const cellX = Math.floor(ball.x / CELL_SIZE);
            const cellY = Math.floor(ball.y / CELL_SIZE);
            const index = cellY * gridCols + cellX;
            grid[index].push(ball);
        }

        /* Collision resolution between two balls */
        function resolveCollision(a, b) {
            const dx = b.x - a.x;
            const dy = b.y - a.y;
            const dist = Math.hypot(dx, dy);
            const minDist = a.r + b.r;

            if (dist === 0 || dist >= minDist) {
                return; // No collision
            }

            // Normal vector
            const nx = dx / dist;
            const ny = dy / dist;

            // Relative velocity
            const dvx = a.vx - b.vx;
            const dvy = a.vy - b.vy;
            const relVelAlongNormal = dvx * nx + dvy * ny;

            // Skip if balls are moving apart
            if (relVelAlongNormal > 0) {
                return;
            }

            // Impulse scalar
            const impulse = -(1 + RESTITUTION) * relVelAlongNormal / (1 / a.mass + 1 / b.mass);

            // Apply impulse to velocities
            a.vx += (impulse / a.mass) * nx;
            a.vy += (impulse / a.mass) * ny;
            b.vx -= (impulse / b.mass) * nx;
            b.vy -= (impulse / b.mass) * ny;

            // Positional correction to avoid sinking
            const overlap = 0.5 * (minDist - dist);
            a.x -= overlap * nx;
            a.y -= overlap * ny;
            b.x += overlap * nx;
            b.y += overlap * ny;
        }

        /* ------------------------------------------------------------------
           Main simulation
        ------------------------------------------------------------------ */

        const balls = createBalls();
        const grid = new Array(gridSize);

        function gameLoop() {
            // 1. Clear canvas
            ctx.clearRect(0, 0, W, H);

            // 2. Clear grid
            clearGrid(grid);

            // 3. Update positions and add to grid
            for (const ball of balls) {
                ball.update();
                addToGrid(grid, ball);
            }

            // 4. Collision detection & response
            for (let cellY = 0; cellY < gridRows; cellY++) {
                for (let cellX = 0; cellX < gridCols; cellX++) {
                    const cellIndex = cellY * gridCols + cellX;
                    const cellBalls = grid[cellIndex];

                    // Check each pair inside this cell
                    for (let i = 0; i < cellBalls.length; i++) {
                        const a = cellBalls[i];

                        // Check against neighboring cells
                        for (let offsetY = -1; offsetY <= 1; offsetY++) {
                            const ny = cellY + offsetY;
                            if (ny < 0 || ny >= gridRows) continue;

                            for (let offsetX = -1; offsetX <= 1; offsetX++) {
                                const nx = cellX + offsetX;
                                if (nx < 0 || nx >= gridCols) continue;

                                const neighborIndex = ny * gridCols + nx;
                                const neighborBalls = grid[neighborIndex];

                                for (const b of neighborBalls) {
                                    // Avoid double checking
                                    if (a.id >= b.id) continue;
                                    resolveCollision(a, b);
                                }
                            }
                        }
                    }
                }
            }

            // 5. Draw all balls
            for (const ball of balls) {
                ball.draw(ctx);
            }

            // 6. Request next frame
            requestAnimationFrame(gameLoop);
        }

        // Start simulation
        requestAnimationFrame(gameLoop);

    </script>
    <section id="notes">
        <h3>Notes</h3>
        <ul>
            <li>Collision detection uses a uniform grid (cell size = 50px). This reduces the complexity from O(n²) to roughly O(n).</li>
            <li>Ball‑to‑ball collision response is based on impulse and conservation of momentum. A restitution coefficient of 0.9 keeps the simulation lively but realistic.</li>
            <li>Gravity and wall damping are applied each frame. The damping factor is 0.8, giving a noticeable energy loss on each bounce.</li>
            <li>Initial ball placement attempts to avoid overlaps. If the desired number of balls cannot be placed without overlap after many attempts, the loop stops early.</li>
        </ul>
    </section>
</body>
</html>
```

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: gpt-oss-20b-mxfp4.gguf -->
<!-- Prompt: ball_bound.md -->
<!-- Generation Time: 24.44s -->
<!-- Fallback Used: False -->