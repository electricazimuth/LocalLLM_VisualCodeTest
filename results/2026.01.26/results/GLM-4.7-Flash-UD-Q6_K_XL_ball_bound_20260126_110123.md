Here is a complete, standalone HTML file containing the Bouncing Balls simulation. I have implemented a physics engine with gravity, damping, and elastic collisions. I also included a **Spatial Grid** optimization to ensure the simulation runs smoothly even with 100+ balls.

I added a control panel to interact with the simulation (add balls, clear, pause) and a mouse interaction feature where moving the mouse creates a repulsion field.

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bouncing Balls Physics Simulation</title>
    <style>
        :root {
            --bg-color: #1a1a2e;
            --panel-bg: rgba(255, 255, 255, 0.1);
            --text-color: #e0e0e0;
            --accent-color: #4cc9f0;
            --btn-hover: #4361ee;
        }

        body {
            margin: 0;
            overflow: hidden;
            background-color: var(--bg-color);
            color: var(--text-color);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }

        /* Container for the canvas to handle centering and shadows */
        #simulation-container {
            position: relative;
            box-shadow: 0 0 50px rgba(0, 0, 0, 0.5);
        }

        canvas {
            background-color: #0f3460;
            border-radius: 4px;
            cursor: crosshair;
            display: block;
        }

        /* Control Panel */
        #controls {
            position: absolute;
            top: 20px;
            left: 20px;
            background: var(--panel-bg);
            backdrop-filter: blur(10px);
            padding: 15px;
            border-radius: 8px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            display: flex;
            flex-direction: column;
            gap: 10px;
            width: 220px;
            z-index: 10;
        }

        h1 {
            font-size: 1.2rem;
            margin: 0 0 10px 0;
            color: var(--accent-color);
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .control-group {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.9rem;
        }

        button {
            background-color: var(--accent-color);
            color: #000;
            border: none;
            padding: 8px 12px;
            border-radius: 4px;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.2s ease;
            width: 100%;
            margin-top: 5px;
        }

        button:hover {
            background-color: var(--btn-hover);
            color: white;
        }

        button.secondary {
            background-color: transparent;
            border: 1px solid var(--accent-color);
            color: var(--accent-color);
        }

        button.secondary:hover {
            background-color: rgba(76, 201, 240, 0.1);
        }

        /* Status Indicator */
        #stats {
            font-size: 0.8rem;
            opacity: 0.7;
            margin-top: 10px;
            text-align: center;
        }

        /* Note Section */
        #notes {
            margin-top: 20px;
            padding: 20px;
            max-width: 800px;
            background-color: #fff;
            color: #333;
            border-radius: 8px;
            display: none; /* Hidden by default as per structure, shown if needed */
        }
    </style>
</head>
<body>

    <div id="simulation-container">
        <!-- Canvas -->
        <canvas id="gameCanvas" width="800" height="600"></canvas>

        <!-- UI Controls -->
        <aside id="controls">
            <h1>Physics Lab</h1>
            
            <div class="control-group">
                <label for="ballCount">Balls:</label>
                <span id="ballCountDisplay">60</span>
            </div>

            <button id="addBallBtn">Add Ball</button>
            <button id="resetBtn" class="secondary">Clear & Reset</button>
            <button id="pauseBtn" class="secondary">Pause</button>

            <div id="stats">FPS: 60</div>
        </aside>
    </div>

    <script>
        /**
         * Configuration & Constants
         */
        const CONFIG = {
            gravity: 0.5,
            friction: 0.8,      // Energy loss on wall bounce
            ballDamping: 0.99,  // Air resistance
            restitution: 0.9,   // Ball-to-ball bounce elasticity
            minRadius: 10,
            maxRadius: 25,
            initialCount: 60,
            spatialGridSize: 50 // Optimization: Size of grid cells
        };

        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const W = canvas.width;
        const H = canvas.height;

        // UI Elements
        const statsEl = document.getElementById('stats');
        const ballCountDisplay = document.getElementById('ballCountDisplay');
        const addBallBtn = document.getElementById('addBallBtn');
        const resetBtn = document.getElementById('resetBtn');
        const pauseBtn = document.getElementById('pauseBtn');

        // State
        let balls = [];
        let isPaused = false;
        let animationId;
        
        // Mouse interaction
        const mouse = { x: -1000, y: -1000, active: false };

        /**
         * Helper: Random Range
         */
        function randomRange(min, max) {
            return Math.random() * (max - min) + min;
        }

        function randomColor() {
            const hue = Math.floor(Math.random() * 360);
            return `hsl(${hue}, 70%, 60%)`;
        }

        /**
         * Class: Ball
         * Handles individual physics and rendering
         */
        class Ball {
            constructor(x, y, r, color) {
                this.x = x;
                this.y = y;
                this.vx = randomRange(-5, 5);
                this.vy = randomRange(-5, 5);
                this.radius = r;
                this.color = color;
                this.mass = r * r; // Mass proportional to area
            }

            draw() {
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
                ctx.fillStyle = this.color;
                ctx.fill();
                
                // Add a subtle shine for 3D effect
                ctx.fillStyle = 'rgba(255, 255, 255, 0.3)';
                ctx.beginPath();
                ctx.arc(this.x - this.radius * 0.3, this.y - this.radius * 0.3, this.radius * 0.3, 0, Math.PI * 2);
                ctx.fill();
                
                ctx.closePath();
            }

            update() {
                // Apply Gravity
                this.vy += CONFIG.gravity;

                // Apply Friction (Air resistance)
                this.vx *= CONFIG.ballDamping;
                this.vy *= CONFIG.ballDamping;

                // Apply Velocity
                this.x += this.vx;
                this.y += this.vy;

                // Mouse Repulsion (Interactive Feature)
                if (mouse.active) {
                    const dx = this.x - mouse.x;
                    const dy = this.y - mouse.y;
                    const dist = Math.sqrt(dx*dx + dy*dy);
                    if (dist < 150) {
                        const forceDirectionX = dx / dist;
                        const forceDirectionY = dy / dist;
                        const force = (150 - dist) / 150;
                        const repulsionStrength = 2;
                        this.vx += forceDirectionX * force * repulsionStrength;
                        this.vy += forceDirectionY * force * repulsionStrength;
                    }
                }

                this.checkWallCollisions();
            }

            checkWallCollisions() {
                // Right Wall
                if (this.x + this.radius > W) {
                    this.x = W - this.radius;
                    this.vx *= -CONFIG.friction;
                }
                // Left Wall
                else if (this.x - this.radius < 0) {
                    this.x = this.radius;
                    this.vx *= -CONFIG.friction;
                }

                // Floor
                if (this.y + this.radius > H) {
                    this.y = H - this.radius;
                    this.vy *= -CONFIG.friction;
                    
                    // Prevent endless micro-bouncing when near rest
                    if (Math.abs(this.vy) < CONFIG.gravity * 2) {
                        this.vy = 0;
                    }
                }
                // Ceiling
                else if (this.y - this.radius < 0) {
                    this.y = this.radius;
                    this.vy *= -CONFIG.friction;
                }
            }
        }

        /**
         * Optimization: Spatial Grid
         * Divides the canvas into cells to reduce collision checks from O(N^2) to O(N)
         */
        class SpatialGrid {
            constructor(cellSize) {
                this.cellSize = cellSize;
                this.clear();
            }

            clear() {
                this.cells = new Map();
            }

            getKey(x, y) {
                // Determine which cell the point belongs to
                const col = Math.floor(x / this.cellSize);
                const row = Math.floor(y / this.cellSize);
                return `${col},${row}`;
            }

            insert(ball) {
                const key = this.getKey(ball.x, ball.y);
                if (!this.cells.has(key)) {
                    this.cells.set(key, []);
                }
                this.cells.get(key).push(ball);
            }

            // Returns an array of balls that might collide with the given ball
            getNeighbors(ball) {
                const neighbors = [];
                const col = Math.floor(ball.x / this.cellSize);
                const row = Math.floor(ball.y / this.cellSize);

                // Check current cell and adjacent 8 cells
                for (let i = -1; i <= 1; i++) {
                    for (let j = -1; j <= 1; j++) {
                        const key = `${col + i},${row + j}`;
                        if (this.cells.has(key)) {
                            const cellBalls = this.cells.get(key);
                            for (let other of cellBalls) {
                                if (other !== ball) {
                                    neighbors.push(other);
                                }
                            }
                        }
                    }
                }
                return neighbors;
            }
        }

        const grid = new SpatialGrid(CONFIG.spatialGridSize);

        /**
         * Physics Engine: Collision Resolution
         */
        function resolveCollisions(balls) {
            // 1. Update Grid
            grid.clear();
            for (let ball of balls) {
                grid.insert(ball);
            }

            // 2. Check collisions only against neighbors in grid
            for (let ball of balls) {
                const potentialCollisions = grid.getNeighbors(ball);
                
                for (let other of potentialCollisions) {
                    // Simple check: don't check same ball twice
                    if (ball === other) continue;

                    const dx = other.x - ball.x;
                    const dy = other.y - ball.y;
                    const distance = Math.sqrt(dx * dx + dy * dy);
                    const minDist = ball.radius + other.radius;

                    if (distance < minDist) {
                        // Collision detected
                        handleBallCollision(ball, other, dx, dy, distance);
                    }
                }
            }
        }

        function handleBallCollision(b1, b2, dx, dy, distance) {
            // 1. Positional Correction (prevent sticking)
            // Calculate overlap
            const overlap = (b1.radius + b2.radius - distance);
            // Avoid division by zero
            if (distance === 0) return; 
            
            // Normal vector
            const nx = dx / distance;
            const ny = dy / distance;

            // Move balls apart proportional to inverse mass (lighter ball moves more)
            const totalMass = b1.mass + b2.mass;
            const m1Ratio = b2.mass / totalMass;
            const m2Ratio = b1.mass / totalMass;

            b1.x -= nx * overlap * m1Ratio;
            b1.y -= ny * overlap * m1Ratio;
            b2.x += nx * overlap * m2Ratio;
            b2.y += ny * overlap * m2Ratio;

            // 2. Velocity Resolution (Elastic Collision)
            // Normal Velocity components
            const v1n = b1.vx * nx + b1.vy * ny;
            const v2n = b2.vx * nx + b2.vy * ny;

            // Tangent Velocity components (unchanged by collision)
            const tx = -ny;
            const ty = nx;
            const v1t = b1.vx * tx + b1.vy * ty;
            const v2t = b2.vx * tx + b2.vy * ty;

            // 1D Elastic Collision formula for Normal components
            const v1nFinal = (v1n * (b1.mass - b2.mass) + 2 * b2.mass * v2n) / totalMass;
            const v2nFinal = (v2n * (b2.mass - b1.mass) + 2 * b1.mass * v1n) / totalMass;

            // Apply restitution (energy loss)
            const v1nNew = v1nFinal * CONFIG.restitution;
            const v2nNew = v2nFinal * CONFIG.restitution;

            // Convert scalar normal/tangent velocities back to vectors
            b1.vx = v1nNew * nx + v1t * tx;
            b1.vy = v1nNew * ny + v1t * ty;
            b2.vx = v2nNew * nx + v2t * tx;
            b2.vy = v2nNew * ny + v2t * ty;
        }

        /**
         * Initialization
         */
        function init() {
            balls = [];
            for (let i = 0; i < CONFIG.initialCount; i++) {
                addBall();
            }
        }

        function addBall() {
            const r = randomRange(CONFIG.minRadius, CONFIG.maxRadius);
            // Ensure ball spawns inside canvas
            const x = randomRange(r, W - r);
            const y = randomRange(r, H / 3); // Start in top third
            
            balls.push(new Ball(x, y, r, randomColor()));
            ballCountDisplay.textContent = balls.length;
        }

        /**
         * Main Animation Loop
         */
        let lastTime = 0;
        function gameLoop(timestamp) {
            if (!isPaused) {
                // Calculate FPS (optional)
                const dt = timestamp - lastTime;
                lastTime = timestamp;
                if (timestamp % 10 === 0) { // Update stats occasionally
                    statsEl.textContent = `Balls: ${balls.length} | FPS: ${Math.round(1000/dt)}`;
                }

                // 1. Clear Canvas
                ctx.clearRect(0, 0, W, H);

                // 2. Update Physics
                for (let ball of balls) {
                    ball.update();
                }
                
                // 3. Solve Collisions
                resolveCollisions(balls);

                // 4. Draw
                for (let ball of balls) {
                    ball.draw();
                }
            }

            animationId = requestAnimationFrame(gameLoop);
        }

        /**
         * Event Listeners
         */
        addBallBtn.addEventListener('click', () => {
            addBall();
            // Visual feedback
            addBallBtn.style.transform = "scale(0.95)";
            setTimeout(() => addBallBtn.style.transform = "scale(1)", 100);
        });

        resetBtn.addEventListener('click', () => {
            balls = [];
            ballCountDisplay.textContent = 0;
            // Give a moment before resetting count so UI updates
            setTimeout(init, 100); 
        });

        pauseBtn.addEventListener('click', () => {
            isPaused = !isPaused;
            pauseBtn.textContent = isPaused ? "Resume" : "Pause";
            pauseBtn.classList.toggle('secondary');
        });

        // Mouse Interaction
        canvas.addEventListener('mousemove', (e) => {
            const rect = canvas.getBoundingClientRect();
            mouse.x = e.clientX - rect.left;
            mouse.y = e.clientY - rect.top;
            mouse.active = true;
        });

        canvas.addEventListener('mouseleave', () => {
            mouse.active = false;
        });

        // Touch Interaction (Basic support)
        canvas.addEventListener('touchmove', (e) => {
            e.preventDefault();
            const rect = canvas.getBoundingClientRect();
            mouse.x = e.touches[0].clientX - rect.left;
            mouse.y = e.touches[0].clientY - rect.top;
            mouse.active = true;
        }, { passive: false });
        
        canvas.addEventListener('touchend', () => {
            mouse.active = false;
        });

        // Start
        init();
        requestAnimationFrame(gameLoop);

    </script>
</body>
</html>
```

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: GLM-4.7-Flash-UD-Q6_K_XL.gguf -->
<!-- Prompt: ball_bound.md -->
<!-- Time: 63.87s -->
<!-- Fallback: False -->