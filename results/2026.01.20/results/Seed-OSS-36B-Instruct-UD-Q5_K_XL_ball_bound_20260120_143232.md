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
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const W = canvas.width;
        const H = canvas.height;

        // Ball class representing each bouncing ball
        class Ball {
            constructor(index) {
                this.index = index; // Unique identifier for collision pairing
                this.r = Math.random() * 20 + 10; // Radius: 10-30px
                this.mass = this.r ** 2; // Mass proportional to radius squared
                this.color = `hsl(${Math.random() * 360}, 50%, 50%)`; // Random color

                // Random initial position (ensure full containment within canvas)
                this.x = Math.random() * (W - 2 * this.r) + this.r;
                this.y = Math.random() * (H - 2 * this.r) + this.r;

                // Random initial velocity (pixels per second)
                this.vx = (Math.random() - 0.5) * 200;
                this.vy = (Math.random() - 0.5) * 200;
            }

            // Draw the ball on the canvas
            draw() {
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.r, 0, Math.PI * 2);
                ctx.fillStyle = this.color;
                ctx.fill();
                ctx.closePath();
            }
        }

        // Simulation constants
        const NUM_BALLS = 50;
        const GRAVITY = 300; // Gravitational acceleration (px/s²)
        const DAMPING = 0.9; // Velocity damping factor (wall collisions)
        const CELL_SIZE = 60; // Spatial grid cell size for collision optimization
        let lastTime = 0; // For delta time calculation
        let balls = []; // Array to hold all balls

        // Initialize balls with unique indices
        function initBalls() {
            balls = [];
            for (let i = 0; i < NUM_BALLS; i++) {
                balls.push(new Ball(i));
            }
        }

        // Create spatial grid to optimize collision detection
        function createSpatialGrid() {
            const grid = {};
            balls.forEach(ball => {
                const cellX = Math.floor(ball.x / CELL_SIZE);
                const cellY = Math.floor(ball.y / CELL_SIZE);
                const key = `${cellX}-${cellY}`;
                if (!grid[key]) grid[key] = [];
                grid[key].push(ball);
            });
            return grid;
        }

        // Check collisions between a single pair of balls
        function checkBallPair(a, b) {
            const dx = b.x - a.x;
            const dy = b.y - a.y;
            const distSq = dx * dx + dy * dy;
            const sumRadii = a.r + b.r;
            const sumRadiiSq = sumRadii * sumRadii;

            // No collision if distance exceeds sum of radii
            if (distSq > sumRadiiSq) return;

            // Prevent division by zero (identical positions)
            if (distSq === 0) {
                a.x += a.r * 0.1;
                b.x -= b.r * 0.1;
                return;
            }

            const dist = Math.sqrt(distSq);
            const overlap = sumRadii - dist; // Amount of overlap

            // Unit normal vector from A to B
            const nx = dx / dist;
            const ny = dy / dist;

            // Relative velocity along the collision normal
            const vRelX = b.vx - a.vx;
            const vRelY = b.vy - a.vy;
            const vRelNorm = vRelX * nx + vRelY * ny;

            // Skip if balls are moving apart
            if (vRelNorm > 0) return;

            // Calculate collision impulse (elastic collision)
            const impulse = -(2 * vRelNorm) / (1 / a.mass + 1 / b.mass);

            // Update velocities
            a.vx -= impulse * nx / a.mass;
            a.vy -= impulse * ny / a.mass;
            b.vx += impulse * nx / b.mass;
            b.vy += impulse * ny / b.mass;

            // Separate balls to resolve overlap
            a.x += (overlap * b.mass) / (a.mass + b.mass) * nx;
            a.y += (overlap * b.mass) / (a.mass + b.mass) * ny;
            b.x -= (overlap * a.mass) / (a.mass + b.mass) * nx;
            b.y -= (overlap * a.mass) / (a.mass + b.mass) * ny;
        }

        // Check all ball-to-ball collisions using spatial grid
        function checkAllBallCollisions(grid) {
            for (let i = 0; i < balls.length; i++) {
                const a = balls[i];
                const cellX = Math.floor(a.x / CELL_SIZE);
                const cellY = Math.floor(a.y / CELL_SIZE);

                // Check current cell and 8 adjacent cells
                for (let dx = -1; dx <= 1; dx++) {
                    for (let dy = -1; dy <= 1; dy++) {
                        const neighbors = grid[`${cellX + dx}-${cellY + dy}`] || [];
                        neighbors.forEach(b => {
                            if (b.index > a.index) checkBallPair(a, b); // Avoid duplicate checks
                        });
                    }
                }
            }
        }

        // Handle wall collisions with damping
        function checkWallCollisions() {
            balls.forEach(ball => {
                // Left wall
                if (ball.x - ball.r < 0) {
                    ball.x = ball.r;
                    ball.vx = -ball.vx * DAMPING;
                }
                // Right wall
                if (ball.x + ball.r > W) {
                    ball.x = W - ball.r;
                    ball.vx = -ball.vx * DAMPING;
                }
                // Top wall
                if (ball.y - ball.r < 0) {
                    ball.y = ball.r;
                    ball.vy = -ball.vy * DAMPING;
                }
                // Bottom wall
                if (ball.y + ball.r > H) {
                    ball.y = H - ball.r;
                    ball.vy = -ball.vy * DAMPING;
                }
            });
        }

        // Main animation loop
        function gameLoop(timestamp) {
            const deltaTime = (timestamp - lastTime) / 1000; // Convert to seconds
            lastTime = timestamp;

            // Clear canvas
            ctx.clearRect(0, 0, W, H);

            // 1. Apply gravity and update positions
            balls.forEach(ball => {
                ball.vy += GRAVITY * deltaTime; // Gravitational acceleration
                ball.x += ball.vx * deltaTime;
                ball.y += ball.vy * deltaTime;
            });

            // 2. Check wall collisions
            checkWallCollisions();

            // 3. Check ball-to-ball collisions (with spatial grid optimization)
            const grid = createSpatialGrid();
            checkAllBallCollisions(grid);

            // 4. Draw all balls
            balls.forEach(ball => ball.draw());

            // Request next frame
            requestAnimationFrame(gameLoop);
        }

        // Initialize and start the simulation
        initBalls();
        requestAnimationFrame(gameLoop);

    </script>
    <section id="notes">
        <h3>Simulation Notes:</h3>
        <ul>
            <li><strong>Spatial Grid Optimization:</strong> Uses a grid-based spatial partitioning system to reduce ball-to-ball collision checks from O(n²) to O(n) on average.</li>
            <li><strong>Delta Time:</strong> Physics calculations use delta time to ensure consistent behavior across different frame rates.</li>
            <li><strong>Mass Proportionality:</strong> Ball mass is proportional to the square of its radius (m = r²), simulating real-world density consistency.</li>
            <li><strong>Energy Damping:</strong> Wall collisions apply a damping factor (0.9) to velocity, causing balls to lose energy over time.</li>
            <li><strong>Collision Resolution:</strong> Ball-to-ball collisions use elastic collision physics with overlap resolution to prevent sticking.</li>
            <li><strong>Initialization:</strong> 50 balls with random sizes (10-30px), colors, and initial velocities, ensuring full containment in the canvas.</li>
        </ul>
    </section>
</body>
</html>
``` 

### Key Features Explained:
1. **Spatial Grid Optimization**: Reduces collision checks by only evaluating balls in the same or adjacent grid cells, crucial for performance with 50+ balls.
2. **Delta Time**: Ensures physics (gravity, movement) are consistent regardless of frame rate by scaling updates with elapsed time.
3. **Elastic Collisions**: Ball-to-ball interactions use realistic physics with momentum conservation and overlap resolution to prevent sticking.
4. **Energy Damping**: Wall collisions reduce velocity magnitude by 10% (damping factor = 0.9), simulating energy loss (e.g., friction).
5. **Randomization**: Balls have random sizes, colors, and initial velocities for visual variety and dynamic behavior.

### How to Use:
- Open the HTML file in a modern browser (Chrome, Firefox, Edge).
- Observe balls bouncing with gravity, colliding with walls (losing height over time), and interacting realistically with each other.
- The simulation runs smoothly even with 50+ balls due to spatial grid optimization.

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: Seed-OSS-36B-Instruct-UD-Q5_K_XL.gguf -->
<!-- Prompt: ball_bound.md -->
<!-- Generation Time: 464.12s -->
<!-- Fallback Used: False -->