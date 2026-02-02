```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bouncing Balls Simulation</title>
    <style>
        body { 
            margin: 0; 
            overflow: hidden; 
            background-color: #1a1a1a; 
            display: flex; 
            justify-content: center; 
            align-items: center; 
            height: 100vh; 
            font-family: sans-serif;
        }
        canvas { 
            border: 1px solid #444; 
            background-color: #ffffff; 
            box-shadow: 0 0 20px rgba(0,0,0,0.5);
            display: block;
        }
        #notes {
            position: absolute;
            bottom: 10px;
            left: 10px;
            background: rgba(0, 0, 0, 0.7);
            color: #00ff00;
            padding: 10px;
            border-radius: 5px;
            font-size: 12px;
            pointer-events: none;
            max-width: 400px;
            line-height: 1.4;
        }
    </style>
</head>
<body>
    <canvas id="gameCanvas" width="800" height="600"></canvas>
    <div id="notes">
        <strong>Simulation Info:</strong><br>
        - 100 Balls with Gravity & Damping<br>
        - Spatial Partitioning (Grid) for optimization<br>
        - Ball-Ball Elastic Collisions
    </div>

    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        
        // --- Constants ---
        const GRAVITY = 0.5;        // Gravity force
        const DAMPING = 0.75;       // Wall energy loss (0.0 to 1.0)
        const FRICTION = 0.995;     // Air resistance
        const BALL_COUNT = 100;     // Target number of balls
        const MIN_RADIUS = 5;
        const MAX_RADIUS = 15;
        // Cell size for spatial partitioning (Grid Optimization)
        // We make it a multiple of MAX_RADIUS to ensure balls only check neighbors
        const CELL_SIZE = 60;       

        // Colors for balls
        const COLORS = [
            '#FF5733', '#33FF57', '#3357FF', '#FF33A1', '#33FFF5', 
            '#F5FF33', '#FF8C33', '#8C33FF', '#33FF8C', '#FF3333'
        ];

        let balls = [];
        let width, height;

        /**
         * Utility: Random integer between min and max
         */
        function randomInt(min, max) {
            return Math.floor(Math.random() * (max - min + 1) + min);
        }

        /**
         * Utility: Random color from our palette
         */
        function randomColor() {
            return COLORS[Math.floor(Math.random() * COLORS.length)];
        }

        // --- Spatial Grid Class ---
        // Optimizes collision detection by only checking balls in the same or adjacent cells
        class SpatialGrid {
            constructor(cellSize) {
                this.cellSize = cellSize;
                this.cols = 0;
                this.rows = 0;
                this.grid = [];
            }

            clear() {
                this.grid = [];
            }

            // Convert world coordinates to grid cell coordinates
            _getCellIndex(x, y) {
                const col = Math.floor(x / this.cellSize);
                const row = Math.floor(y / this.cellSize);
                return { col, row };
            }

            // Get the index in the flat array
            getKey(col, row) {
                return `${col},${row}`;
            }

            // Add a ball to the grid
            addToGrid(ball) {
                const { col, row } = this._getCellIndex(ball.x, ball.y);
                const key = this.getKey(col, row);
                
                if (!this.grid[key]) {
                    this.grid[key] = [];
                }
                this.grid[key].push(ball);
            }

            // Get balls to check against this ball
            getNeighbors(ball) {
                const { col, row } = this._getCellIndex(ball.x, ball.y);
                let neighbors = [];

                // Check 3x3 area (current cell + neighbors)
                for (let i = -1; i <= 1; i++) {
                    for (let j = -1; j <= 1; j++) {
                        if (i === 0 && j === 0) continue;
                        
                        const c = col + i;
                        const r = row + j;
                        const key = this.getKey(c, r);
                        
                        if (this.grid[key]) {
                            neighbors = neighbors.concat(this.grid[key]);
                        }
                    }
                }
                return neighbors;
            }
        }

        // Initialize global grid
        const spatialGrid = new SpatialGrid(CELL_SIZE);


        /**
         * Ball Class
         * Handles individual physics and rendering of a single ball
         */
        class Ball {
            constructor(x, y, r) {
                this.x = x;
                this.y = y;
                this.r = r;
                this.color = randomColor();
                
                // Mass proportional to area (r^2)
                this.mass = r * r;
                
                // Random velocity
                this.vx = randomInt(-4, 4);
                this.vy = randomInt(-4, 4);
            }

            draw() {
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.r, 0, Math.PI * 2);
                ctx.fillStyle = this.color;
                ctx.fill();
                ctx.closePath();
            }

        }

        // --- Physics Functions ---

        // 1. Initialize Simulation
        function init() {
            width = canvas.width;
            height = canvas.height;
            balls = [];

            for (let i = 0; i < BALL_COUNT; i++) {
                const r = randomInt(MIN_RADIUS, MAX_RADIUS);
                // Keep spawning inside bounds, but away from extreme edges
                const x = randomInt(r + 5, width - r - 5);
                const y = randomInt(r + 5, height / 2 - 100); // Spawn mostly top half initially
                
                balls.push(new Ball(x, y, r));
            }
        }

        // 2. Collision Resolution (Impulse-based)
        function resolveCollision(b1, b2) {
            const dx = b2.x - b1.x;
            const dy = b2.y - b1.y;
            const distance = Math.sqrt(dx * dx + dy * dy);

            // Check if overlapping
            if (distance < b1.r + b2.r) {
                // --- A. Positional Correction (prevent sinking/sticking) ---
                // Move balls apart so they don't overlap
                const overlap = (b1.r + b2.r - distance) / 2;
                const offsetX = (dx / distance) * overlap;
                const offsetY = (dy / distance) * overlap;

                b1.x -= offsetX;
                b1.y -= offsetY;
                b2.x += offsetX;
                b2.y += offsetY;

                // --- B. Velocity Resolution (Elastic Collision) ---
                // Normal vector
                const nx = dx / distance;
                const ny = dy / distance;

                // Tangent vector
                const tx = -ny;
                const ty = nx;

                // Dot Product Tangent
                const dpTan1 = b1.vx * tx + b1.vy * ty;
                const dpTan2 = b2.vx * tx + b2.vy * ty;

                // Dot Product Normal
                const dpNorm1 = b1.vx * nx + b1.vy * ny;
                const dpNorm2 = b2.vx * nx + b2.vy * ny;

            // Conservation of momentum in 1D
            const m1 = b1.mass;
            const m2 = b2.mass;
            const p1 = (dpNorm1 * (m1 - m2) + 2 * m2 * dpNorm2) / (m1 + m2);
            const p2 = (dpNorm2 * (m2 - m1) + 2 * m1 * dpNorm1) / (m1 + m2);

            // Update velocities
            b1.vx = tx * dpTan1 + nx * p1;
            b1.vy = ty * dpTan1 + ny * p1;
            b2.vx = tx * dpTan2 + nx * p2;
            b2.vy = ty * dpTan2 + ny * p2;
            }
        }

        // 3. Update Physics State
        function update() {
            // 1. Clear the grid for this frame
            spatialGrid.clear();

            // 2. Move balls and update positions
            for (let i = 0; i < balls.length; i++) {
                let b = balls[i];

                // Apply Gravity
                b.vy += GRAVITY;
                
                // Apply Friction/Air Resistance
                b.vx *= FRICTION;
                b.vy *= FRICTION;

                // Update Position
                b.x += b.vx;
                b.y += b.vy;

                // Wall Collision - Floor
                if (b.y + b.r > height) {
                    b.y = height - b.r;
                    b.vy *= -DAMPING;
                    // Friction on floor
                    b.vx *= 0.95; 
                } 
                // Wall Collision - Ceiling
                else if (b.y - b.r < 0) {
                    b.y = b.r;
                    b.vy *= -DAMPING;
                }

                // Wall Collision - Right
                if (b.x + b.r > width) {
                    b.x = width - b.r;
                    b.vx *= -DAMPING;
                } 
                // Wall Collision - Left
                else if (b.x - b.r < 0) {
                    b.x = b.r;
                    b.vx *= -DAMPING;
                }

                // Add ball to spatial grid for collision checking
                spatialGrid.addToGrid(b);
            }

            // 3. Ball-to-Ball Collision (Optimized)
            for (let i = 0; i < balls.length; i++) {
                const b1 = balls[i];
                // Only check balls after grid population to avoid self-check
                // Get neighbors from grid
                // Note: We pass the ball itself. The grid method returns neighbors.
                // Since we populated the grid inside the loop, we can just get neighbors.
                // However, to make it thread-safe or cleaner, we can just use the neighbors list.
                // The spatialGrid object's internal state was just updated, so we can query it.
                // But wait, spatialGrid needs to be cleared first (done) and filled first (done).
                // However, we filled it *after* clearing, then immediately asking for neighbors?
                // We need to re-fill or fill, then query. 
                // Better: Fill all first, then query.
            }
            
            // Re-fill grid just for checking (Cleaner logic separation)
            // Actually, the previous loop did fill it, but let's be explicit.
            // Actually, the previous loop filled it. 
            // Let's re-fill grid first to ensure we have everyone's position
            for (let b of balls) {
                spatialGrid.addToGrid(b);
            }

            // Check collisions
            for (let i = 0; i < balls.length; i++) {
                const b1 = balls[i];
                // Get neighbors only, don't check self
                // We need to get unique neighbors. 
                // A simple way:
                const neighbors = spatialGrid.getNeighbors(b1);
                
                for (let j = 0; j < neighbors.length; j++) {
                    const b2 = neighbors[j];
                    // Ensure we don't process the same pair twice
                    // We can optimize this check by only checking if j > index of b1, 
                    // but for 100 balls, O(N) check is fine.
                    if (b1 === b2) continue;
                    
                    resolveCollision(b1, b2);
                }
            }
        }

        // 4. Draw Frame
        function draw() {
            // Clear canvas
            ctx.clearRect(0, 0, width, height);

            // Draw Grid (Optional debug, but requested for "square container" look)
            // We aren't drawing the grid lines, just using the structure.
            
            // Draw Balls
            for (let b of balls) {
                b.draw();
            }
        }

        // 5. Game Loop
        function gameLoop() {
            update();
            draw();
            requestAnimationFrame(gameLoop);
        }

        // Start
        init();
        gameLoop();

        // Handle Window Resize (Optional but good practice)
        window.addEventListener('resize', () => {
            // In a real app, we might re-init balls or adjust canvas size
            // Here we just let the fixed size remain
        });

    </script>
</body>
</html>
```

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: GLM-4.7-Flash-UD-Q6_K_XL.gguf -->
<!-- Prompt: ball_bound.md -->
<!-- Generation Time: 186.42s -->
<!-- Fallback Used: False -->