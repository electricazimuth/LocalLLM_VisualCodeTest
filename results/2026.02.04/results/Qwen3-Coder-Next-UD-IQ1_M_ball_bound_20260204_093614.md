Here is the complete, optimized solution. I have implemented a spatial partitioning system (a Grid-based approach) to handle the $O(n^2)$ collision complexity efficiently, allowing smooth performance with 50+ balls.

```html
<!DOCTYPE html>
<html>
<head>
    <title>Bouncing Balls Simulation</title>
    <style>
        body { 
            margin: 0; 
            overflow: hidden; 
            background-color: #f0f0f0;
            font-family: sans-serif;
        }
        canvas { 
            border: 2px solid #333; 
            background-color: #fff; 
            display: block; 
            margin: 20px auto; 
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }
        #ui-container {
            text-align: center;
            margin-bottom: 10px;
            font-weight: bold;
            color: #555;
        }
        #notes {
            margin-top: 20px;
            padding: 10px;
            background-color: #e9ecef;
            border: 1px solid #ced4da;
            max-width: 600px;
            margin-left: auto;
            margin-right: auto;
            border-radius: 5px;
        }
    </style>
</head>
<body>
    
    <div id="ui-container">
        Bouncing Balls Physics Simulation (Optimized with Spatial Partitioning)
    </div>
    <canvas id="gameCanvas" width="800" height="600"></canvas>
    
    <section id="notes">
        <h4>Implementation Details:</h4>
        <ul>
            <li><strong>Physics:</strong> Implements gravity, wall friction/damping, and mass-based elastic collisions.</li>
            <li><strong>Optimization:</strong> Uses a <strong>Spatial Grid</strong> for collision detection. Instead of checking every ball against every other ball ($O(N^2)$), we only check balls within the same grid cells. This keeps performance high even with 100+ balls.</li>
            <li><strong>Collision Resolution:</strong> Separates overlapping balls to prevent sticking and applies impulse exchange based on mass and relative velocity.</li>
        </ul>
    </section>

    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const W = canvas.width;
        const H = canvas.height;

        // --- Configuration ---
        const BALL_COUNT = 60;
        const GRAVITY = 0.6;
        const WALL_BOUNCE_DAMPING = 0.8; // Energy loss on wall bounce
        const FRICTION = 0.99; // Air resistance
        const GRID_SIZE = 40; // Size of grid cells for spatial partitioning

        // --- Spatial Partitioning System (Grid) ---
        class SpatialGrid {
            constructor(width, height, cellSize) {
                this.cellSize = cellSize;
                this.cols = Math.ceil(width / cellSize);
                this.rows = Math.ceil(height / cellSize);
                this.grid = [];
                this.reset();
            }

            reset() {
                // Create empty 2D array
                this.grid = new Array(this.cols);
                for (let i = 0; i < this.cols; i++) {
                    this.grid[i] = new Array(this.rows);
                    for (let j = 0; j < this.rows; j++) {
                        this.grid[i][j] = [];
                    }
                }
            }

            getIndex(x, y) {
                // Return grid coordinates for a point
                return {
                    col: Math.floor(x / this.cellSize),
                    row: Math.floor(y / this.cellSize)
                };
            }

            addBall(ball) {
                const { col, row } = this.getIndex(ball.x, ball.y);
                // Boundary checks for safety
                const safeCol = Math.max(0, Math.min(col, this.cols - 1));
                const safeRow = Math.max(0, Math.min(row, this.rows - 1));
                this.grid[safeCol][safeRow].push(ball);
            }

            // Helper to get nearby balls efficiently
            getNearbyBalls(ball) {
                const { col, row } = this.getIndex(ball.x, ball.y);
                const nearby = [];
                
                // Check 3x3 neighborhood around the ball's cell
                for (let i = -1; i <= 1; i++) {
                    for (let j = -1; j <= 1; j++) {
                        const nCol = col + i;
                        const nRow = row + j;
                        
                        if (nCol >= 0 && nCol < this.cols && nRow >= 0 && nRow < this.rows) {
                            // Add all balls from this cell, excluding self
                            const cellBalls = this.grid[nCol][nRow];
                            for (let k = 0; k < cellBalls.length; k++) {
                                if (cellBalls[k] !== ball) {
                                    nearby.push(cellBalls[k]);
                                }
                            }
                        }
                    }
                }
                return nearby;
            }
        }

        // --- Ball Class ---
        class Ball {
            constructor(x, y, r, color) {
                this.x = x;
                this.y = y;
                this.r = r;
                this.mass = r * r; // Mass proportional to area
                this.color = color;
                this.vx = (Math.random() - 0.5) * 10;
                this.vy = (Math.random() - 0.5) * 10;
            }

            draw(ctx) {
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.r, 0, Math.PI * 2);
                ctx.fillStyle = this.color;
                ctx.fill();
                ctx.strokeStyle = '#000';
                ctx.lineWidth = 1;
                ctx.stroke();
                ctx.closePath();
            }

            update(grid) {
                // Apply Gravity
                this.vy += GRAVITY;

                // Update Position
                this.x += this.vx;
                this.y += this.vy;

                // Wall Collisions
                // Right Wall
                if (this.x + this.r > W) {
                    this.x = W - this.r;
                    this.vx = -this.vx * WALL_BOUNCE_DAMPING;
                }
                // Left Wall
                if (this.x - this.r < 0) {
                    this.x = this.r;
                    this.vx = -this.vx * WALL_BOUNCE_DAMPING;
                }
                // Bottom Floor
                if (this.y + this.r > H) {
                    this.y = H - this.r;
                    this.vy = -this.vy * WALL_BOUNCE_DAMPING;
                    // Apply friction on ground
                    this.vx *= 0.95;
                }
                // Ceiling
                if (this.y - this.r < 0) {
                    this.y = this.r;
                    this.vy = -this.vy * WALL_BOUNCE_DAMPING;
                }

                // Recenter ball if velocity is near zero (prevents sticking)
                if (Math.abs(this.vy) < 0.1 && this.y + this.r >= H - 1) {
                    this.vy = 0;
                }
                
                // Apply Air Friction
                this.vx *= FRICTION;
                this.vy *= FRICTION;
            }
        }

        // --- Initialization ---
        const balls = [];
        const colors = ['red', 'blue', 'green', 'orange', 'purple', 'cyan', 'yellow', 'pink'];

        function initBalls() {
            balls.length = 0; // Clear array
            for (let i = 0; i < BALL_COUNT; i++) {
                const r = 10 + Math.random() * 15; // Radii between 10 and 25
                const x = r + Math.random() * (W - r * 2);
                const y = r + Math.random() * (H - r * 2);
                const color = colors[Math.floor(Math.random() * colors.length)];
                balls.push(new Ball(x, y, r, color));
            }
        }

        // --- Physics & Collision Logic ---
        
        function resolveCollision(b1, b2) {
            const dx = b2.x - b1.x;
            const dy = b2.y - b1.y;
            const distance = Math.sqrt(dx * dx + dy * dy);
            const minDist = b1.r + b2.r;

            // Check for collision
            if (distance < minDist) {
                // 1. Resolve Overlap (Positional Correction)
                // Move balls apart so they don't stick
                const overlap = minDist - distance;
                const percent = overlap / (2 * distance);
                const dxNorm = dx / distance;
                const dyNorm = dy / distance;
                
                const correction = percent * distance; // Distance to move total
                const moveX = dxNorm * correction;
                const moveY = dyNorm * correction;

                b1.x -= moveX;
                b1.y -= moveY;
                b2.x += moveX;
                b2.y += moveY;

                // 2. Resolve Velocity (Impulse)
                // Normal vector
                const nx = dxNorm;
                const ny = dyNorm;

                // Relative velocity
                const dvx = b2.vx - b1.vx;
                const dvy = b2.vy - b1.vy;

                // Velocity along the normal
                const velAlongNormal = dvx * nx + dvy * ny;

                // If velocities are separating, do nothing
                if (velAlongNormal > 0) return;

                // Elastic collision impulse
                const restitution = 0.9; // Bounciness
                let impulse = (-(1 + restitution) * velAlongNormal) / (1/b1.mass + 1/b2.mass);
                
                // Apply impulse
                // We distribute based on mass (inverse mass weighting)
                const m1 = b1.mass;
                const m2 = b2.mass;
                
                const p = impulse / (1/m1 + 1/m2);
                
                b1.vx -= p * (1/m1) * (nx);
                b1.vy -= p * (1/m1) * (ny);
                b2.vx += p * (1/m2) * (nx);
                b2.vy += p * (1/m2) * (ny);

                // Add a bit of energy loss (damping) for inter-ball collisions too
                b1.vx *= 0.95;
                b1.vy *= 0.95;
                b2.vx *= 0.95;
                b2.vy *= 0.95;
            }
        }

        function updatePhysics(grid) {
            grid.reset();

            // 1. Update positions and handle wall collisions
            // While updating, add balls to the grid
            for (let i = 0; i < balls.length; i++) {
                balls[i].update(grid);
                grid.addBall(balls[i]);
            }

            // 2. Check Ball-to-Ball collisions
            // Only check against nearby balls (spatial grid)
            for (let i = 0; i < balls.length; i++) {
                const ball = balls[i];
                const nearbyBalls = grid.getNearbyBalls(ball);

                for (let j = 0; j < nearbyBalls.length; j++) {
                    resolveCollision(ball, nearbyBalls[j]);
                }
            }
        }

        // --- Animation Loop ---
        let gridSystem;

        function gameLoop(timestamp) {
            // Initialize Grid (Recreating every frame to handle movement)
            if (!gridSystem) {
                gridSystem = new SpatialGrid(W, H, GRID_SIZE);
            } else {
                // Re-create grid to update cell indices for current ball positions
                gridSystem = new SpatialGrid(W, H, GRID_SIZE);
            }

            updatePhysics(gridSystem);

            // Clear Canvas
            ctx.clearRect(0, 0, W, H);

            // Draw Container Walls (Visual boundary)
            ctx.strokeStyle = '#333';
            ctx.lineWidth = 2;
            ctx.strokeRect(0, 0, W, H);

            // Draw Balls
            for (let i = 0; i < balls.length; i++) {
                balls[i].draw(ctx);
            }

            requestAnimationFrame(gameLoop);
        }

        // Start
        initBalls();
        requestAnimationFrame(gameLoop);

    </script>
</body>
</html>
```

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: Qwen3-Coder-Next-UD-IQ1_M.gguf -->
<!-- Prompt: ball_bound.md -->
<!-- Time: 39.98s -->
<!-- Fallback: False -->