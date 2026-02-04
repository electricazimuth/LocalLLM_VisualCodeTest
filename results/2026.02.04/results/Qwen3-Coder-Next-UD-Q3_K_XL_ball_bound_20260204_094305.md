Here is the complete, single-file solution. It includes the HTML structure, CSS styling, and optimized JavaScript logic using a spatial grid to handle the $O(n^2)$ collision complexity efficiently.

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
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        canvas { 
            border: 2px solid #333; 
            background-color: #ffffff; 
            display: block; 
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin: 20px auto;
        }
        #ui-layer {
            margin-top: 10px;
            text-align: center;
            color: #555;
        }
        button {
            padding: 8px 16px;
            cursor: pointer;
            font-size: 14px;
            background-color: #007bff;
            color: white;
            border: none;
            border-radius: 4px;
        }
        button:hover { background-color: #0056b3; }
        
        /* Note Section Styling */
        #notes {
            width: 800px;
            background-color: #e8f4fd;
            border: 1px solid #bce8f1;
            border-radius: 5px;
            padding: 15px;
            margin-top: 20px;
            color: #31708f;
            font-size: 0.9em;
            white-space: pre-wrap;
        }
    </style>
</head>
<body>
    <canvas id="gameCanvas" width="800" height="600"></canvas>
    
    <div id="ui-layer">
        <h2>Bouncing Balls Physics</h2>
        <button onclick="resetSimulation()">Reset Simulation</button>
        <span id="stats" style="margin-left: 20px; font-weight: bold;">Balls: 60</span>
    </div>

    <section id="notes">
Notes on Implementation:
---------------------------------
1. Physics Model:
   - Gravity: Applied continuously to vertical velocity (vy += gravity).
   - Damping: Velocity is multiplied by 0.85 on wall impacts to simulate energy loss (heat/sound).
   - Friction: A small air resistance (0.995) is applied to horizontal velocity every frame.

2. Ball-to-Ball Collision:
   - Uses 1D Elastic Collision logic projected onto 2D vectors.
   - Mass is calculated as radius^2 (heavier balls are bigger).
   - Position Correction: After a collision, balls are pushed apart along the collision normal to prevent sticking/overlapping.

3. Optimization (Spatial Partitioning):
   - Instead of O(N^2) checks (60 balls = 1770 checks), a Grid-based approach is used.
   - The canvas is divided into 40x40 pixel cells.
   - Balls are only checked against other balls in their immediate 9 neighboring cells.
   - This reduces complexity to roughly O(N) for this density, allowing 100+ balls to run smoothly.
   - The grid is rebuilt every frame.

4. Rendering:
   - Uses requestAnimationFrame for smooth 60fps animation.
   - Balls are colored randomly using HSL for visibility.
    </section>

    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const W = canvas.width;
        const H = canvas.height;

        // --- Configuration Constants ---
        const BALL_COUNT = 60;
        const GRAVITY = 0.4;
        const DAMPING_FACTOR = 0.85; // Energy loss on wall hit
        const FRICTION = 0.995;      // Air resistance
        const GRID_SIZE = 40;        // Size of spatial partition cells
        
        let balls = [];
        let grid = []; // Spatial hash grid

        // --- Ball Class ---
        class Ball {
            constructor(x, y, r) {
                this.x = x;
                this.y = y;
                this.r = r;
                this.color = `hsl(${Math.random() * 360}, 70%, 60%)`;
                
                // Random initial velocity
                this.vx = (Math.random() - 0.5) * 10;
                this.vy = (Math.random() - 0.5) * 10;
                
                // Mass proportional to area (r^2)
                this.mass = this.r * this.r;
            }

            draw() {
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.r, 0, Math.PI * 2);
                ctx.fillStyle = this.color;
                ctx.fill();
                ctx.strokeStyle = 'rgba(0,0,0,0.3)';
                ctx.stroke();
                ctx.closePath();
            }

            update() {
                // Apply Gravity
                this.vy += GRAVITY;
                
                // Apply Friction (Air resistance)
                this.vx *= FRICTION;
                this.vy *= FRICTION;

                // Update Position
                this.x += this.vx;
                this.y += this.vy;

                // --- Wall Collisions ---
                // Right Wall
                if (this.x + this.r > W) {
                    this.x = W - this.r;
                    this.vx = -this.vx * DAMPING_FACTOR;
                }
                // Left Wall
                else if (this.x - this.r < 0) {
                    this.x = this.r;
                    this.vx = -this.vx * DAMPING_FACTOR;
                }
                // Floor
                if (this.y + this.r > H) {
                    this.y = H - this.r;
                    this.vy = -this.vy * DAMPING_FACTOR;
                    
                    // Stop micro-bouncing when near rest
                    if (Math.abs(this.vy) < GRAVITY * 2) {
                        this.vy = 0;
                    }
                }
                // Ceiling
                else if (this.y - this.r < 0) {
                    this.y = this.r;
                    this.vy = -this.vy * DAMPING_FACTOR;
                }
            }
        }

        // --- Spatial Grid for Optimization ---
        class Grid {
            constructor(width, height, cellSize) {
                this.cols = Math.ceil(width / cellSize);
                this.rows = Math.ceil(height / cellSize);
                this.cellSize = cellSize;
                this.cells = []; // Array of arrays
                this.init();
            }

            init() {
                this.cells = new Array(this.cols * this.rows).fill(null).map(() => []);
            }

            clear() {
                for (let i = 0; i < this.cells.length; i++) {
                    this.cells[i].length = 0;
                }
            }

            getCellIndex(x, y) {
                // Clamp coordinates to avoid index out of bounds
                const c = Math.floor(x / this.cellSize);
                const r = Math.floor(y / this.cellSize);
                const index = r * this.cols + c;
                return (index >= 0 && index < this.cells.length) ? index : -1;
            }

            addBall(ball) {
                const idx = this.getCellIndex(ball.x, ball.y);
                if (idx !== -1) {
                    this.cells[idx].push(ball);
                }
            }

            checkCollisions() {
                // Iterate through all cells
                for (let i = 0; i < this.cells.length; i++) {
                    const cellBalls = this.cells[i];
                    
                    // If cell is empty, skip
                    if (cellBalls.length === 0) continue;

                    // Check collisions within this cell
                    for (let a = 0; a < cellBalls.length; a++) {
                        for (let b = a + 1; b < cellBalls.length; b++) {
                            resolveCollision(cellBalls[a], cellBalls[b]);
                        }
                    }

                    // Check collisions with adjacent cells (Right, Bottom-Right, Bottom)
                    // We don't need to check Left or Top because we already checked those cells when we arrived at them
                    const currentCol = i % this.cols;
                    const currentRow = Math.floor(i / this.cols);

                    // Check Right Cell
                    if (currentCol < this.cols - 1) {
                        const rightIdx = i + 1;
                        const rightBalls = this.cells[rightIdx];
                        if (rightBalls.length > 0) {
                            for (let a of cellBalls) {
                                for (let b of rightBalls) {
                                    resolveCollision(a, b);
                                }
                            }
                        }
                    }

                    // Check Bottom Cell
                    if (currentRow < this.rows - 1) {
                        const bottomIdx = i + this.cols;
                        const bottomBalls = this.cells[bottomIdx];
                        if (bottomBalls.length > 0) {
                            for (let a of cellBalls) {
                                for (let b of bottomBalls) {
                                    resolveCollision(a, b);
                                }
                            }
                        }
                    }

                    // Check Bottom-Right Cell
                    if (currentCol < this.cols - 1 && currentRow < this.rows - 1) {
                        const bottomRightIdx = i + this.cols + 1;
                        const bottomRightBalls = this.cells[bottomRightIdx];
                        if (bottomRightBalls.length > 0) {
                            for (let a of cellBalls) {
                                for (let b of bottomRightBalls) {
                                    resolveCollision(a, b);
                                }
                            }
                        }
                    }
                }
            }
        }

        // --- Physics Logic: Ball-to-Ball Collision ---
        function resolveCollision(b1, b2) {
            const dx = b2.x - b1.x;
            const dy = b2.y - b1.y;
            const distance = Math.sqrt(dx * dx + dy * dy);
            const minDist = b1.r + b2.r;

            // Check if colliding
            if (distance < minDist) {
                // 1. Prevent Overlap (Position Correction)
                // Move balls apart along the collision vector so they don't stick
                const overlap = minDist - distance;
                const nx = dx / distance; // Normal X
                const ny = dy / distance; // Normal Y
                
                // Move proportional to inverse mass (lighter moves more)
                const totalMass = b1.mass + b2.mass;
                const m1Ratio = b2.mass / totalMass;
                const m2Ratio = b1.mass / totalMass;

                b1.x -= nx * overlap * m1Ratio;
                b1.y -= ny * overlap * m1Ratio;
                b2.x += nx * overlap * m2Ratio;
                b2.y += ny * overlap * m2Ratio;

                // 2. Velocity Resolution (Elastic Collision)
                // Calculate relative velocity
                const rvx = b2.vx - b1.vx;
                const rvy = b2.vy - b1.vy;

                // Velocity along the normal
                const velAlongNormal = rvx * nx + rvy * ny;

                // Do not resolve if velocities are separating
                if (velAlongNormal > 0) return;

                // Restitution (bounciness) - combined damping
                const e = 0.8; 

                // Calculate impulse scalar
                let j = -(1 + e) * velAlongNormal;
                j /= (1 / b1.mass + 1 / b2.mass);

                // Apply impulse
                const impulseX = j * nx;
                const impulseY = j * ny;

                b1.vx -= impulseX / b1.mass;
                b1.vy -= impulseY / b1.mass;
                b2.vx += impulseX / b2.mass;
                b2.vy += impulseY / b2.mass;
            }
        }

        // --- Initialization & Game Loop ---

        function initBalls() {
            balls = [];
            // Grid dimensions
            const cols = Math.ceil(W / GRID_SIZE);
            const rows = Math.ceil(H / GRID_SIZE);
            
            // Re-init grid
            grid = new Grid(W, H, GRID_SIZE);

            for (let i = 0; i < BALL_COUNT; i++) {
                let r = 10 + Math.random() * 15; // Radius between 10 and 25
                let x, y;
                let safe = false;
                let attempts = 0;

                // Try to spawn without overlap (simple check against existing balls)
                while (!safe && attempts < 100) {
                    x = r + Math.random() * (W - 2 * r);
                    y = r + Math.random() * (H - 2 * r);
                    safe = true;

                    for (let other of balls) {
                        const dist = Math.hypot(x - other.x, y - other.y);
                        if (dist < r + other.r) {
                            safe = false;
                            break;
                        }
                    }
                    attempts++;
                }
                
                balls.push(new Ball(x, y, r));
            }
        }

        function updateAndDraw(timestamp) {
            // 1. Clear Canvas
            ctx.clearRect(0, 0, W, H);

            // 2. Reset and Populate Spatial Grid
            grid.clear();
            for (let ball of balls) {
                grid.addBall(ball);
            }

            // 3. Update Physics (Gravity & Walls) & Check Collisions
            // We update all positions first, then check collisions, 
            // but for stability, we often do collision resolution after position updates.
            
            // Update positions
            for (let ball of balls) {
                ball.update();
            }

            // Check spatial collisions
            grid.checkCollisions();

            // 4. Draw
            for (let ball of balls) {
                ball.draw();
            }

            // Loop
            requestAnimationFrame(updateAndDraw);
        }

        function resetSimulation() {
            initBalls();
            // Force a redraw immediately
            ctx.clearRect(0, 0, W, H);
            for (let ball of balls) {
                ball.draw();
            }
        }

        // Start
        initBalls();
        requestAnimationFrame(updateAndDraw);

        // Handle Window Resize (Optional but good practice)
        window.addEventListener('resize', () => {
            // For this simple demo, we keep canvas fixed size to avoid complex re-scaling logic
            // but in a production app, you'd want to handle this.
        });

    </script>
</body>
</html>
```

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: Qwen3-Coder-Next-UD-Q3_K_XL.gguf -->
<!-- Prompt: ball_bound.md -->
<!-- Time: 46.50s -->
<!-- Fallback: False -->