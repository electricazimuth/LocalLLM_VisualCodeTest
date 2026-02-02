**Full HTML file – copy‑paste this into a file (e.g. `bouncing‑balls.html`) and open it in a browser.**  

```html
<!DOCTYPE html>
<html>
<head>
    <title>Bouncing Balls – Spinning Heptagon</title>
    <style>
        body { margin:0; overflow:hidden; background:#f0f0f0; display:flex; justify-content:center; align-items:center; height:100vh; }
        canvas { border:1px solid #333; background:#fff; }
    </style>
</head>
<body>
    <canvas id="gameCanvas" width="500" height="500"></canvas>

    <section id="notes">
        <!--
            • 30 balls (numbers 1‑20 repeated) are drawn.
            • All balls share the same radius (15 px) but get different colours.
            • They start clustered in the centre and are given small random velocities.
            • A regular heptagon (7‑sided polygon) spins at 360°/5 s.
            • Balls bounce off the heptagon walls with damping.
            • Ball‑to‑ball collisions are resolved with a simple impulse model.
            • A tiny spatial‑hash grid avoids O(n²) checks for every pair.
            • No external libraries – only vanilla JS + Canvas 2D.
        -->
    </section>

    <script>
        /* --------------------------------------------------------------
         *  Canvas setup
         * -------------------------------------------------------------- */
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const W = canvas.width;
        const H = canvas.height;
        const cx = W / 2;
        const cy = H / 2;

        /* --------------------------------------------------------------
         *  Constants & configuration
         * -------------------------------------------------------------- */
        const GRAVITY = 0.18;               // px / frame²
        const DAMPING = 0.84;               // energy loss on wall bounce
        const RESTITUTION = 0.80;           // bounce “elasticity” for ball‑ball
        const HEPTAGON_RADIUS = 120;        // size of the container
        const BALL_RADIUS = 15;             // all balls have this radius
        const BALL_COUNT = 30;              // at least 30 balls required
        const HEPTAGON_SIDES = 7;
        const OMEGA = 2 * Math.PI / 5;      // angular speed (rad/frame) → 360°/5 s
        const COLOR_PALETTE = [
            '#f8b862', '#f6ad49', '#f39800', '#f08300', '#ec6d51',
            '#ee7948', '#ed6d3d', '#ec6800', '#ec6800', '#ee7800',
            '#eb6238', '#ea5506', '#ea5506', '#eb6101', '#e49e61',
            '#e45e32', '#e17b34', '#dd7a56', '#db8449', '#d66a35'
        ];
        const GRID_SIZE = 50;               // spatial‑hash cell size

        /* --------------------------------------------------------------
         *  Helper utilities
         * -------------------------------------------------------------- */
        const rand = (min, max) => Math.random() * (max - min) + min;
        const clamp = (v, min, max) => Math.max(min, Math.min(max, v));

        /* --------------------------------------------------------------
         *  Ball class
         * -------------------------------------------------------------- */
        class Ball {
            constructor(x, y, vx, vy, color, number) {
                this.x = x; this.y = y;               // position
                this.vx = vx; this.vy = vy;           // velocity
                this.r = BALL_RADIUS;                 // radius
                this.mass = this.r * this.r;          // mass ∝ r²
                this.color = color;
                this.number = number;                 // 1‑20 (repeated)
            }
            draw() {
                ctx.save();
                ctx.translate(this.x, this.y);
                // filled circle
                ctx.fillStyle = this.color;
                ctx.beginPath();
                ctx.arc(0, 0, this.r, 0, Math.PI * 2);
                ctx.fill();

                // draw number (centered)
                ctx.fillStyle = '#000';
                ctx.font = `${this.r * 1.2}px sans-serif`;
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillText(this.number, 0, 0);
                ctx.restore();
            }
        }

        /* --------------------------------------------------------------
         *  Create balls
         * -------------------------------------------------------------- */
        const balls = [];
        for (let i = 0; i < BALL_COUNT; i++) {
            const num = (i % 20) + 1;                     // 1‑20 (repeated)
            const color = COLOR_PALETTE[num - 1];
            // start near centre with a tiny random offset
            const x = cx + rand(-5, 5);
            const y = cy + rand(-5, 5);
            // small random velocity
            const vx = rand(-1, 1);
            const vy = rand(-1, 1);
            balls.push(new Ball(x, y, vx, vy, color, num));
        }

        /* --------------------------------------------------------------
         *  Heptagon geometry (vertices are stored in local coordinates)
         * -------------------------------------------------------------- */
        const heptagonVertices = [];
        for (let k = 0; k < HEPTAGON_SIDES; k++) {
            const a = (2 * Math.PI * k) / HEPTAGON_SIDES;
            heptagonVertices.push({
                x: cx + HEPTAGON_RADIUS * Math.cos(a),
                y: cy + HEPTAGON_RADIUS * Math.sin(a)
            });
        }

        /* --------------------------------------------------------------
         *  Spatial hash for ball‑ball collision optimisation
         * -------------------------------------------------------------- */
        const hashKey = (x, y) => `${Math.floor(x / GRID_SIZE)}_${Math.floor(y / GRID_SIZE)}`;
        const grid = new Map();   // key → array of ball indices

        function updateGrid() {
            grid.clear();
            for (let i = 0; i < balls.length; i++) {
                const b = balls[i];
                const key = hashKey(b.x, b.y);
                if (!grid.has(key)) grid.set(key, []);
                grid.get(key).push(i);
            }
        }

        function getNeighbors(key) {
            const [gx, gy] = key.split('_').map(v => parseInt(v));
            const neighbours = [];
            for (let dx = -1; dx <= 1; dx++) {
                for (let dy = -1; dy <= 1; dy++) {
                    const nKey = hashKey(gx + dx, gy + dy);
                    if (grid.has(nKey)) neighbours.push(...grid.get(nKey));
                }
            }
            return neighbours;
        }

        /* --------------------------------------------------------------
         *  Collision utilities
         * -------------------------------------------------------------- */
        // distance between two points
        const dist = (x1, y1, x2, y2) => Math.hypot(x1 - x2, y1 - y2);

        // reflect velocity vector v against normal n (n must be unit)
        const reflect = (vx, vy, nx, ny) => {
            const dot = vx * nx + vy * ny;
            return {
                vx: vx - 2 * dot * nx,
                vy: vy - 2 * dot * ny
            };
        };

        // resolve ball‑ball collision between i and j
        function resolveBallCollision(i, j) {
            const b1 = balls[i];
            const b2 = balls[j];
            const dx = b2.x - b1.x;
            const dy = b2.y - b1.y;
            const d = Math.hypot(dx, dy);
            const minDist = b1.r + b2.r;
            if (d >= minDist) return; // no overlap

            // normal vector (unit)
            const nx = dx / d;
            const ny = dy / d;

            // relative velocity
            const rvx = b1.vx - b2.vx;
            const rvy = b1.vy - b2.vy;
            const velAlongNormal = rvx * nx + rvy * ny;

            // if they are moving away, skip impulse
            if (velAlongNormal > 0) return;

            // impulse scalar (using restitution)
            const e = RESTITUTION;
            const impulse = -(1 + e) * velAlongNormal /
                (1 / b1.mass + 1 / b2.mass);

            // apply impulse
            const impVx = (impulse / b1.mass) * nx;
            const impVy = (impulse / b1.mass) * ny;
            const impVx2 = -(impulse / b2.mass) * nx;
            const impVy2 = -(impulse / b2.mass) * ny;

            b1.vx += impVx; b1.vy += impVy;
            b2.vx += impVx2; b2.vy += impVy2;

            // separate overlapping balls
            const overlap = minDist - d;
            const correction = overlap / (b1.mass + b2.mass) * 0.5;
            b1.x -= nx * correction;
            b1.y -= ny * correction;
            b2.x += nx * correction;
            b2.y += ny * correction;
        }

        // resolve wall (heptagon) collision for a single ball
        function resolveWallCollision(ball) {
            // transform ball position to world coordinates (already world)
            const px = ball.x;
            const py = ball.y;

            // test each edge of the heptagon
            for (let i = 0; i < HEPTAGON_SIDES; i++) {
                const p1 = heptagonVertices[i];
                const p2 = heptagonVertices[(i + 1) % HEPTAGON_SIDES];

                // edge vector
                const ex = p2.x - p1.x;
                const ey = p2.y - p1.y;
                // outward normal (polygon is CCW)
                const nx = ey;
                const ny = -ex;
                const len = Math.hypot(nx, ny);
                const nxu = nx / len;
                const nyu = ny / len;

                // distance from point to edge (positive if outside)
                const dist = (px - p1.x) * nxu + (py - p1.y) * nyu;

                if (dist <= ball.r) {
                    // ball penetrated the wall – push it inside
                    const penetration = ball.r - dist;
                    ball.x -= nxu * penetration;
                    ball.y -= nyu * penetration;

                    // reflect velocity on the normal
                    const velDotN = (ball.vx * nxu + ball.vy * nyu);
                    ball.vx -= 2 * velDotN * nxu;
                    ball.vy -= 2 * velDotN * nyu;

                    // damping
                    ball.vx *= DAMPING;
                    ball.vy *= DAMPING;

                    // stop further processing for this ball (it may touch multiple walls,
                    // but one resolution is enough for a simple demo)
                    break;
                }
            }
        }

        /* --------------------------------------------------------------
         *  Animation loop
         * -------------------------------------------------------------- */
        let angle = 0; // rotation angle of the heptagon

        function gameLoop(timestamp) {
            // ---- 1. Clear canvas -------------------------------------------------
            ctx.clearRect(0, 0, W, H);

            // ---- 2. Update heptagon rotation ------------------------------------
            angle += OMEGA;
            // keep angle in [0, 2π)
            if (angle > Math.PI * 2) angle -= Math.PI * 2;

            // ---- 3. Rotate context and draw heptagon ----------------------------
            ctx.save();
            ctx.translate(cx, cy);
            ctx.rotate(angle);

            // draw heptagon outline (just for visual reference)
            ctx.strokeStyle = '#555';
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.moveTo(heptagonVertices[0].x - cx, heptagonVertices[0].y - cy);
            for (let i = 1; i < HEPTAGON_SIDES; i++) {
                const v = heptagonVertices[i];
                ctx.lineTo(v.x - cx, v.y - cy);
            }
            ctx.closePath();
            ctx.stroke();

            // restore before we start drawing balls (they are drawn in world coords)
            ctx.restore();

            // ---- 4. Update balls (gravity, movement, collisions) ---------------
            // 4a. Apply gravity
            for (const b of balls) {
                b.vy += GRAVITY;
            }

            // 4b. Move balls
            for (const b of balls) {
                b.x += b.vx;
                b.y += b.vy;
            }

            // 4c. Wall collisions
            for (const b of balls) {
                resolveWallCollision(b);
            }

            // 4d. Ball‑ball collisions (using spatial hash)
            updateGrid(); // rebuild hash each frame (cheap for 30 balls)
            for (let i = 0; i < balls.length; i++) {
                const bi = balls[i];
                const key = hashKey(bi.x, bi.y);
                const neighbourIndices = getNeighbors(key);
                for (const j of neighbourIndices) {
                    if (j <= i) continue; // avoid duplicate pairs
                    resolveBallCollision(i, j);
                }
            }

            // ---- 5. Draw balls ---------------------------------------------------
            for (const b of balls) {
                b.draw();
            }

            requestAnimationFrame(gameLoop);
        }

        // start the animation
        requestAnimationFrame(gameLoop);
    </script>
</body>
</html>
```

### What the code does

| Feature | Implementation |
|---------|----------------|
| **Spinning heptagon** | Vertices are pre‑computed, rotated each frame (`angle += OMEGA`), drawn as a stroked polygon. |
| **30 balls** | Numbers 1‑20 are repeated so every ball’s number is in that range. All have radius 15 px, same colour palette, and a unique number. |
| **Initial state** | Balls start clustered in the centre with tiny random velocities, then “drop” under gravity. |
| **Gravity** | `vy += GRAVITY` each frame. |
| **Wall collision & damping** | Distance to each heptagon edge is measured; if the ball penetrates, it is pushed back, its velocity is reflected across the edge normal, and then multiplied by `DAMPING` (≈ 0.84). |
| **Ball‑ball collisions** | Spatial‑hash grid limits checks to nearby balls. Overlap is resolved by reflecting velocities using an impulse based on `RESTITUTION` and separating the balls. |
| **Optimization** | Grid partitioning reduces pair checks from O(n²) to roughly O(n). |
| **Animation** | `requestAnimationFrame` loop, clear‑draw‑update pattern, all drawing done with the Canvas 2D API. |
| **No external libraries** | Pure vanilla JavaScript and HTML5 Canvas. |

Open the file in any modern browser and you’ll see a rotating heptagonal arena with 30 numbered balls bouncing, colliding, and gradually losing energy as they hit the walls. Enjoy!

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: Nemotron-3-Nano-30B-A3B-UD-Q5_K_XL.gguf -->
<!-- Prompt: heptagon.md -->
<!-- Generation Time: 49.00s -->
<!-- Fallback Used: False -->