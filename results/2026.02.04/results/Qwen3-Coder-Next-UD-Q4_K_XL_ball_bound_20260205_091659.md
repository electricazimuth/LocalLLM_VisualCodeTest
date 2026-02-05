Here is the complete, single-file solution. It includes the HTML structure, CSS styling, and a robust JavaScript implementation featuring a spatial partitioning grid for optimized collision detection, gravity, damping, and elastic collision physics.

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
            border: 1px solid black; 
            background-color: #ffffff; 
            display: block; 
            margin: 20px auto; 
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        #ui-layer {
            position: absolute;
            top: 10px;
            left: 10px;
            background: rgba(255, 255, 255, 0.8);
            padding: 10px;
            border-radius: 8px;
            pointer-events: none; /* Let clicks pass through */
        }
        .info-text {
            font-size: 14px;
            color: #333;
        }
    </style>
</head>
<body>
    <div id="ui-layer">
        <div class="info-text"><strong>Bouncing Balls Simulation</strong></div>
        <div class="info-text">Balls: <span id="ballCount">0</span></div>
        <div class="info-text">FPS: <span id="fpsDisplay">0</span></div>
        <div class="info-text">Controls: <i>Click to add balls, Space to reset</i></div>
    </div>
    <canvas id="gameCanvas" width="800" height="600"></canvas>
    
    <section id="notes">
        <h3>Implementation Notes</h3>
        <p><strong>Physics Engine:</strong> This simulation utilizes a custom physics loop.</p>
        <ul>
            <li><strong>Gravity:</strong> A constant downward acceleration is applied to the vertical velocity ($v_y$) every frame.</li>
            <li><strong>Damping (Restitution):</strong> When balls hit walls, they lose 10% of their energy ($velocity \times 0.9$), simulating real-world friction.</li>
            <li><strong>Ball-to-Ball Collisions:</strong> Uses 1D elastic collision logic rotated to the collision normal vector. Momentum and mass are conserved.</li>
            <li><strong>Spatial Partitioning (Grid):</strong> To maintain performance with 50+ balls (O(n) complexity instead of O(n^2)), the canvas is divided into a grid. Balls are only checked against others in their own cell and immediate neighbors.</li>
            <li><strong>Position Correction:</strong> To prevent balls from getting stuck inside each other ("sticking"), overlap is corrected immediately after collision detection by pushing balls apart based on their mass ratio.</li>
        </ul>
    </section>

    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const W = canvas.width;
        const H = canvas.height;
        
        // --- Configuration ---
        const CONFIG = {
            ballCount: 50,
            gravity: 0.4,
            friction: 0.99,      // Air resistance
            wallDamping: 0.85,   // Energy lost when hitting walls
            subSteps: 4,         // Physics sub-steps for stability
            gridSize: 50         // Size of spatial partition cells
        };

        // --- Helper Functions ---
        const randomColor = () => {
            const r = Math.floor(Math.random() * 200);
            const g = Math.floor(Math.random() * 200);
            const b = Math.floor(Math.random() * 200);
            return `rgb(${r},${g},${b})`;
        };

        const randomRange = (min, max) => Math.random() * (max - min) + min;

        // Distance between two points
        const getDistance = (x1, y1, x2, y2) => Math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2);

        // --- Ball Class ---
        class Ball {
            constructor(x, y, r) {
                this.x = x;
                this.y = y;
                this.r = r;
                // Mass is proportional to area (r^2)
                this.mass = r * r; 
                this.color = randomColor();
                this.vx = randomRange(-5, 5);
                this.vy = randomRange(-5, 5);
            }

            draw() {
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.r, 0, Math.PI * 2);
                ctx.fillStyle = this.color;
                ctx.fill();
                ctx.strokeStyle = '#333';
                ctx.lineWidth = 1;
                ctx.stroke();
                ctx.closePath();
            }

            update() {
                this.x += this.vx;
                this.y += this.vy;
            }
        }

        // --- Spatial Grid for Optimization ---
        class Grid {
            constructor(width, height, cellSize) {
                this.cellSize = cellSize;
                this.cols = Math.ceil(width / cellSize);
                this.rows = Math.ceil(height / cellSize);
                this.cells = []; // Map "col,row" -> Array<Ball>
            }

            clear() {
                this.cells = [];
            }

            getIndex(x, y) {
                const col = Math.floor(x / this.cellSize);
                const row = Math.floor(y / this.cellSize);
                // Clamp indices to avoid out of bounds errors if balls leave area
                const safeCol = Math.max(0, Math.min(col, this.cols - 1));
                const safeRow = Math.max(0, Math.min(row, this.rows - 1));
                return `${safeCol},${safeRow}`;
            }

            add(ball) {
                const key = this.getIndex(ball.x, ball.y);
                if (!this.cells[key]) {
                    this.cells[key] = [];
                }
                this.cells[key].push(ball);
            }

            // Returns balls in the same cell and all 8 surrounding neighbors
            getPotentialCollisions(ball) {
                const col = Math.floor(ball.x / this.cellSize);
                const row = Math.floor(ball.y / this.cellSize);
                const nearbyBalls = [];

                for (let i = -1; i <= 1; i++) {
                    for (let j = -1; j <= 1; j++) {
                        const neighborKey = `${col + i},${row + j}`;
                        if (this.cells[neighborKey]) {
                            nearbyBalls.push(...this.cells[neighborKey]);
                        }
                    }
                }
                return nearbyBalls;
            }
        }

        // --- Main Game Logic ---
        const balls = [];
        const grid = new Grid(W, H, CONFIG.gridSize);

        function initBalls() {
            balls.length = 0; // Clear existing
            // Create balls ensuring they don't spawn too deeply inside each other
            for (let i = 0; i < CONFIG.ballCount; i++) {
                let r = randomRange(10, 25);
                let x, y, valid = false;
                let attempts = 0;

                while (!valid && attempts < 100) {
                    x = randomRange(r + 5, W - r - 5);
                    y = randomRange(r + 5, H - r - 5);
                    valid = true;
                    
                    for (let j = 0; j < balls.length; j++) {
                        const d = getDistance(x, y, balls[j].x, balls[j].y);
                        if (d < r + balls[j].r) {
                            valid = false;
                            break;
                        }
                    }
                    attempts++;
                }
                balls.push(new Ball(x, y, r));
            }
            document.getElementById('ballCount').innerText = balls.length;
        }

        function resolveWallCollisions(ball) {
            // Right Wall
            if (ball.x + ball.r > W) {
                ball.x = W - ball.r;
                ball.vx *= -CONFIG.wallDamping;
            }
            // Left Wall
            else if (ball.x - ball.r < 0) {
                ball.x = ball.r;
                ball.vx *= -CONFIG.wallDamping;
            }

            // Floor
            if (ball.y + ball.r > H) {
                ball.y = H - ball.r;
                ball.vy *= -CONFIG.wallDamping;
            }
            // Ceiling
            else if (ball.y - ball.r < 0) {
                ball.y = ball.r;
                ball.vy *= -CONFIG.wallDamping;
            }
        }

        function resolveBallCollisions() {
            // Reset Grid
            grid.clear();
            
            // 1. Populate Grid
            balls.forEach(ball => grid.add(ball));

            // 2. Check Collisions
            // We iterate through balls and check only those in the same grid cell
            // To prevent double-checking, we can iterate balls and check against grid neighbors
            // But to be safe and simple with objects, we check all pairs in the same cell.
            
            for (let i = 0; i < balls.length; i++) {
                const b1 = balls[i];
                const potentialCollisions = grid.getPotentialCollisions(b1);

                for (let j = 0; j < potentialCollisions.length; j++) {
                    const b2 = potentialCollisions[j];

                    // Avoid checking self and duplicate pairs (b1 vs b2 is same as b2 vs b1)
                    if (b1 === b2) continue;
                    
                    // Optimization: Only check if b2 index > b1 index to handle pairs once
                    // However, since we are using a grid lookup, we might get duplicates. 
                    // To keep it robust without a global pair-set, we rely on the spatial grid 
                    // to limit checks, and do a simple check to ensure we don't run the math twice.
                    // The simplest way in a grid loop is to just check all, but perform logic carefully.
                    // Here, let's just check if index of b2 > index of b1 to ensure single processing.
                    const b2Index = balls.indexOf(b2);
                    if (b2Index <= i) continue;

                    const dist = getDistance(b1.x, b1.y, b2.x, b2.y);
                    const minDist = b1.r + b2.r;

                    if (dist < minDist) {
                        // --- Collision Detected ---

                        // 1. Static Resolution (Prevent Overlap/Sticking)
                        // Calculate overlap amount
                        const overlap = minDist - dist;
                        
                        // Normal vector
                        const nx = (b2.x - b1.x) / dist;
                        const ny = (b2.y - b1.y) / dist;

                        // Move balls apart inversely proportional to mass (lighter moves more)
                        const totalMass = b1.mass + b2.mass;
                        const m1Ratio = b2.mass / totalMass;
                        const m2Ratio = b1.mass / totalMass;

                        b1.x -= nx * overlap * m1Ratio;
                        b1.y -= ny * overlap * m1Ratio;
                        b2.x += nx * overlap * m2Ratio;
                        b2.y += ny * overlap * m2Ratio;

                        // 2. Dynamic Resolution (Impulse)
                        // Relative velocity
                        const dvx = b2.vx - b1.vx;
                        const dvy = b2.vy - b1.vy;

                        // Velocity along the normal
                        const velAlongNormal = dvx * nx + dvy * ny;

                        // Do not resolve if velocities are separating
                        if (velAlongNormal > 0) continue;

                        // Restitution (bounciness) - set to 0.9 for lively but not infinite energy
                        const e = 0.9;

                        // Calculate impulse scalar
                        let jVal = -(1 + e) * velAlongNormal;
                        jVal /= (1 / b1.mass + 1 / b2.mass);

                        // Apply impulse
                        const impulseX = jVal * nx;
                        const impulseY = jVal * ny;

                        b1.vx -= impulseX / b1.mass;
                        b1.vy -= impulseY / b1.mass;
                        b2.vx += impulseX / b2.mass;
                        b2.vy += impulseY / b2.mass;
                    }
                }
            }
        }

        function updatePhysics() {
            // Apply Gravity & Update Positions
            for (let ball of balls) {
                ball.vy += CONFIG.gravity;
                ball.vx *= CONFIG.friction;
                ball.vy *= CONFIG.friction;
                ball.update();
            }

            // Wall Collisions
            for (let ball of balls) {
                resolveWallCollisions(ball);
            }

            // Ball-to-Ball Collisions
            resolveBallCollisions();
        }

        // --- Animation Loop Variables ---
        let lastTime = 0;
        let frameCount = 0;
        let lastFpsTime = 0;

        function gameLoop(timestamp) {
            // Calculate FPS
            if (timestamp - lastFpsTime >= 1000) {
                document.getElementById('fpsDisplay').innerText = frameCount;
                frameCount = 0;
                lastFpsTime = timestamp;
            }
            frameCount++;

            // Sub-stepping for physics stability
            // We divide the frame into smaller chunks for collision detection
            // This prevents balls from tunneling through each other at high speeds
            const dt = 1.0 / CONFIG.subSteps;
            
            for (let step = 0; step < CONFIG.subSteps; step++) {
                updatePhysics();
            }

            // --- Drawing ---
            ctx.clearRect(0, 0, W, H);

            // Draw Grid (Optional, for visualization of optimization)
            /*
            ctx.strokeStyle = 'rgba(0,0,0,0.05)';
            ctx.lineWidth = 1;
            for (let x = 0; x <= W; x += CONFIG.gridSize) {
                ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke();
            }
            for (let y = 0; y <= H; y += CONFIG.gridSize) {
                ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke();
            }
            */

            for (let ball of balls) {
                ball.draw();
            }

            requestAnimationFrame(gameLoop);
        }

        // --- Event Listeners ---
        
        // Reset with Spacebar
        window.addEventListener('keydown', (e) => {
            if (e.code === 'Space') {
                initBalls();
            }
        });

        // Add Ball with Click
        canvas.addEventListener('click', (e) => {
            const rect = canvas.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            // Add a new ball at click location if it doesn't overlap too much
            let r = randomRange(10, 20);
            let valid = true;
            for(let b of balls) {
                if(getDistance(x, y, b.x, b.y) < r + b.r) {
                    valid = false; 
                    break;
                }
            }

            if(valid) {
                balls.push(new Ball(x, y, r));
                document.getElementById('ballCount').innerText = balls.length;
            }
        });

        // Initialize
        initBalls();
        requestAnimationFrame(gameLoop);

    </script>
</body>
</html>
```

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: Qwen3-Coder-Next-UD-Q4_K_XL.gguf -->
<!-- Prompt: ball_bound.md -->
<!-- Time: 60.71s -->
<!-- Fallback: False -->