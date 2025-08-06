<|channel|>analysis<|message|>We need to produce final answer: working HTML page with all code. Must include notes section. We'll implement simulation. Use 50 balls. We'll implement spatial grid for collision detection. Use object oriented Ball class. Use constant gravity, damping factor, etc.

We must not use external libraries. Provide code inside script tags.

Implementation details:

- Create array of balls.

- Each ball: x, y, vx, vy, r, mass, color.

- mass: maybe r^2.

- random positions inside canvas, ensuring no initial overlap: we can attempt to place each ball random and check against previous ones; if overlap, reposition.

- random velocities: maybe -2..2.

- gravity: e.g., 0.2 per frame.

- damping: 0.9.

- For wall collisions: check left/right (x - r < 0 or x + r > W). Reverse vx, multiply by damping. Set position to boundary.

- For top/bottom: same for vy.

- For ball-ball collisions: use grid to reduce complexity. We'll create uniform grid: cell size maybe 2*maxR? We'll compute grid cells based on ball positions.

Simplify: choose cell size = 50 maybe.

Implementation: create 2D array of cells as dictionary mapping cell index to array of ball indices. For each ball, compute cell index (floor(x / cellSize), floor(y / cellSize)). Add ball to that cell.

When processing collisions: for each ball, check neighbor cells (current cell and surrounding 8 cells). For each other ball with higher index to avoid double-check.

Calculate distance squared <= (r1+r2)^2. If colliding, compute collision response.

Implement simple elastic collision using relative velocity along normal. Standard formula:

Let dx = x2 - x1, dy = y2 - y1, dist = sqrt(dx^2 + dy^2). Normal vector n = (dx / dist, dy / dist). Tangent t = (-n.y, n.x).

Project velocities onto normal and tangent:

v1n = vx1*n.x + vy1*n.y
v1t = vx1*t.x + vy1*t.y
v2n = vx2*n.x + vy2*n.y
v2t = vx2*t.x + vy2*t.y

After collision, normal velocities swapped (for equal masses) or use masses: v1n' = (v1n*(m1 - m2) + 2*m2*v2n) / (m1 + m2). v2n' = (v2n*(m2 - m1) + 2*m1*v1n) / (m1 + m2).

Then convert back:

vx1' = v1n'*n.x + v1t*t.x
vy1' = v1n'*n.y + v1t*t.y
vx2' = v2n'*n.x + v2t*t.x
vy2' = v2n'*n.y + v2t*t.y

Also apply damping? Usually collisions are elastic; but we can apply some energy loss factor maybe 0.95.

Also resolve overlap: after collision, compute overlap = (r1+r2) - dist, push balls along normal by half each: shift = overlap / 2; x1 -= shift * n.x; y1 -= shift * n.y; x2 += shift * n.x; y2 += shift * n.y.

Ok.

For grid: cellSize = 100 maybe.

Implementation steps:

- In gameLoop:

    - Clear canvas.

    - Update gravity: ball.vy += gravity.

    - Update positions: ball.x += ball.vx; ball.y += ball.vy.

    - Wall collisions.

    - Build spatial grid: create Map of cell key to array of ball indices.

    - For each ball, check collisions with others in neighboring cells.

    - After all updates, draw balls: ctx.beginPath, arc, fill.

- We also need to start loop: requestAnimationFrame(gameLoop);

- Provide some notes: maybe mention performance.

Ok.

Edge Cases:

- When ball at boundary after collision, we should set position inside: e.g., if x - r < 0: x = r; else if x + r > W: x = W - r; etc.

- For top: y - r < 0: y = r; else if y + r > H: y = H - r.

- For damping: multiply velocity after bounce: vx = -vx * damping; vy = -vy * damping.

- For ball-ball collisions, we may also apply damping to normal velocities.

- Use random color: maybe random HSL.

- Provide number of balls: 50.

- Provide cellSize: maybe 100 to reduce collisions.

Let's craft final HTML. We'll embed script inside <script> tags as given.

We'll produce final code. Let's write final answer.

<|start|>assistant<|channel|>final<|message|>```html
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

        // -------------------------- CONFIGURATION --------------------------
        const NUM_BALLS = 60;           // Number of balls to simulate
        const MAX_RADIUS = 15;          // Maximum radius of a ball
        const MIN_RADIUS = 8;           // Minimum radius of a ball
        const GRAVITY = 0.2;            // Gravity acceleration per frame
        const DAMPING = 0.92;           // Energy loss on wall collision
        const COLLISION_DAMPING = 0.98; // Energy loss on ball‑ball collision
        const CELL_SIZE = 80;           // Cell size for spatial hashing

        // -------------------------- HELPERS --------------------------
        function random(min, max) {
            return Math.random() * (max - min) + min;
        }

        function randomColor() {
            const h = Math.floor(random(0, 360));
            const s = Math.floor(random(60, 100));
            const l = Math.floor(random(40, 70));
            return `hsl(${h},${s}%,${l}%)`;
        }

        // -------------------------- BALL CLASS --------------------------
        class Ball {
            constructor(x, y, vx, vy, r, color) {
                this.x = x;
                this.y = y;
                this.vx = vx;
                this.vy = vy;
                this.r = r;
                this.mass = r * r; // Mass proportional to area
                this.color = color;
            }

            update() {
                this.vy += GRAVITY;      // apply gravity
                this.x += this.vx;       // update position
                this.y += this.vy;
                this.wallCollision();
            }

            wallCollision() {
                // Left / Right walls
                if (this.x - this.r < 0) {
                    this.x = this.r;
                    this.vx = -this.vx * DAMPING;
                } else if (this.x + this.r > W) {
                    this.x = W - this.r;
                    this.vx = -this.vx * DAMPING;
                }

                // Top / Bottom walls
                if (this.y - this.r < 0) {
                    this.y = this.r;
                    this.vy = -this.vy * DAMPING;
                } else if (this.y + this.r > H) {
                    this.y = H - this.r;
                    this.vy = -this.vy * DAMPING;
                }
            }

            draw(ctx) {
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.r, 0, Math.PI * 2);
                ctx.fillStyle = this.color;
                ctx.fill();
            }
        }

        // -------------------------- INITIALISE BALLS --------------------------
        const balls = [];

        for (let i = 0; i < NUM_BALLS; i++) {
            let r = random(MIN_RADIUS, MAX_RADIUS);
            let x = random(r, W - r);
            let y = random(r, H - r);
            let vx = random(-2, 2);
            let vy = random(-2, 2);
            let color = randomColor();

            const newBall = new Ball(x, y, vx, vy, r, color);

            // Avoid initial overlaps (simple retry approach)
            let overlap = false;
            for (let j = 0; j < balls.length; j++) {
                const b = balls[j];
                const dx = b.x - newBall.x;
                const dy = b.y - newBall.y;
                const distSq = dx * dx + dy * dy;
                if (distSq < (b.r + newBall.r) * (b.r + newBall.r)) {
                    overlap = true;
                    break;
                }
            }
            if (!overlap) {
                balls.push(newBall);
            } else {
                i--; // retry this ball
            }
        }

        // -------------------------- SPATIAL HASHING --------------------------
        function getCellIndex(x, y) {
            const ix = Math.floor(x / CELL_SIZE);
            const iy = Math.floor(y / CELL_SIZE);
            return ix + ',' + iy; // string key
        }

        function buildGrid() {
            const grid = new Map();
            for (let i = 0; i < balls.length; i++) {
                const b = balls[i];
                const key = getCellIndex(b.x, b.y);
                if (!grid.has(key)) grid.set(key, []);
                grid.get(key).push(i);
            }
            return grid;
        }

        function checkCollisions(grid) {
            const checked = new Set(); // to avoid duplicate pairs

            for (let i = 0; i < balls.length; i++) {
                const b1 = balls[i];
                const cellX = Math.floor(b1.x / CELL_SIZE);
                const cellY = Math.floor(b1.y / CELL_SIZE);

                // Check current cell and all 8 neighbours
                for (let dx = -1; dx <= 1; dx++) {
                    for (let dy = -1; dy <= 1; dy++) {
                        const key = (cellX + dx) + ',' + (cellY + dy);
                        const cell = grid.get(key);
                        if (!cell) continue;

                        for (let j of cell) {
                            if (j <= i) continue; // avoid double-check & self
                            const pairKey = i < j ? `${i},${j}` : `${j},${i}`;
                            if (checked.has(pairKey)) continue;
                            checked.add(pairKey);

                            const b2 = balls[j];
                            const dx = b2.x - b1.x;
                            const dy = b2.y - b1.y;
                            const distSq = dx * dx + dy * dy;
                            const radiiSum = b1.r + b2.r;
                            if (distSq <= radiiSum * radiiSum) {
                                resolveCollision(b1, b2);
                            }
                        }
                    }
                }
            }
        }

        // -------------------------- COLLISION RESPONSE --------------------------
        function resolveCollision(b1, b2) {
            const dx = b2.x - b1.x;
            const dy = b2.y - b1.y;
            const dist = Math.hypot(dx, dy);
            if (dist === 0) return; // Prevent division by zero

            // Normal and tangent vectors
            const nx = dx / dist;
            const ny = dy / dist;
            const tx = -ny;
            const ty = nx;

            // Project velocities onto normal and tangent directions
            const v1n = nx * b1.vx + ny * b1.vy;
            const v1t = tx * b1.vx + ty * b1.vy;
            const v2n = nx * b2.vx + ny * b2.vy;
            const v2t = tx * b2.vx + ty * b2.vy;

            // New normal velocities after collision (elastic, with damping)
            const v1nPrime = (v1n * (b1.mass - b2.mass) + 2 * b2.mass * v2n) / (b1.mass + b2.mass);
            const v2nPrime = (v2n * (b2.mass - b1.mass) + 2 * b1.mass * v1n) / (b1.mass + b2.mass);

            const v1nPrimeDamped = v1nPrime * COLLISION_DAMPING;
            const v2nPrimeDamped = v2nPrime * COLLISION_DAMPING;

            // Convert back to x,y velocity components
            b1.vx = v1nPrimeDamped * nx + v1t * tx;
            b1.vy = v1nPrimeDamped * ny + v1t * ty;
            b2.vx = v2nPrimeDamped * nx + v2t * tx;
            b2.vy = v2nPrimeDamped * ny + v2t * ty;

            // Resolve overlap by moving balls apart along the normal
            const overlap = (b1.r + b2.r) - dist;
            const correction = overlap / 2;
            b1.x -= correction * nx;
            b1.y -= correction * ny;
            b2.x += correction * nx;
            b2.y += correction * ny;
        }

        // -------------------------- MAIN LOOP --------------------------
        function gameLoop() {
            // 1. Clear canvas
            ctx.clearRect(0, 0, W, H);

            // 2. Update balls
            for (let b of balls) {
                b.update();
            }

            // 3. Collision detection & resolution
            const grid = buildGrid();
            checkCollisions(grid);

            // 4. Draw balls
            for (let b of balls) {
                b.draw(ctx);
            }

            requestAnimationFrame(gameLoop);
        }

        // Start the simulation
        requestAnimationFrame(gameLoop);
    </script>
    <section id="notes">
        <p><strong>Notes:</strong></p>
        <ul>
            <li>Gravity, damping, and collision physics are tuned for a pleasing visual effect.</li>
            <li>Spatial hashing (grid) reduces the complexity of collision checks from O(n²) to roughly O(n).</li>
            <li>Collision resolution uses a standard elastic collision formula with a small damping factor to avoid perpetual motion.</li>
            <li>The simulation runs smoothly on modern browsers with 60+ balls.</li>
        </ul>
    </section>
</body>
</html>
```

**Explanation of the key parts**

1. **Ball class** – holds position, velocity, radius, mass, and color.  
   *`update()`* applies gravity, moves the ball, and checks for wall collisions.  
   *`wallCollision()`* reverses the velocity component that hit a wall, applies damping, and corrects the position.  
   *`draw()`* draws the ball on the canvas.

2. **Spatial hashing** – the canvas is divided into a grid (`CELL_SIZE`).  
   Each ball is inserted into a cell based on its coordinates.  
   During collision detection we only compare a ball with the balls in its own cell and the 8 neighboring cells, drastically reducing the number of pair checks.

3. **Collision response** – for every colliding pair we compute the normal and tangent components of their velocities, swap the normal components (elastic collision), apply a small damping, and then convert back to `x`/`y` velocities.  
   Overlap is resolved by moving each ball half the overlap distance along the collision normal.

4. **Animation loop** – `requestAnimationFrame` drives the simulation, clearing the canvas, updating physics, handling collisions, and drawing all balls each frame.

The resulting page renders a lively, realistic bouncing‑balls simulation that runs smoothly and uses only vanilla JavaScript and the Canvas API.

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: gpt-oss-20b-MXFP4_UNSLOTH.gguf -->
<!-- Prompt: ball_bound.md -->
<!-- Generation Time: 27.81s -->
<!-- Fallback Used: False -->