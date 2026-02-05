Here is the complete, single-file solution. It includes the HTML structure, CSS styling, and a robust Vanilla JavaScript implementation featuring vector physics, collision resolution, and a spatial grid for performance optimization.

```html
<!DOCTYPE html>
<html>
<head>
    <title>Bouncing Balls in Spinning Heptagon</title>
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
            background-color: #e0e0e0; 
            display: block; 
            box-shadow: 0 0 20px rgba(0,0,0,0.2);
        }
        .controls {
            margin-top: 10px;
            text-align: center;
            color: #555;
        }
        button {
            padding: 8px 16px;
            font-size: 14px;
            cursor: pointer;
            background-color: #333;
            color: white;
            border: none;
            border-radius: 4px;
            margin: 0 5px;
        }
        button:hover { background-color: #555; }
    </style>
</head>
<body>
    <canvas id="gameCanvas" width="600" height="600"></canvas>
    
    <div class="controls">
        <p>Spinning Heptagon Physics Simulation</p>
        <button onclick="resetSimulation()">Reset Balls</button>
        <button onclick="togglePause()">Pause/Resume</button>
    </div>

    <script>
        // --- CONFIGURATION ---
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const W = canvas.width;
        const H = canvas.height;
        const CENTER_X = W / 2;
        const CENTER_Y = H / 2;

        // Physics Constants
        const GRAVITY = 0.5;
        const FRICTION = 0.99; // Air resistance
        const WALL_DAMPING = 0.85; // Energy loss on wall bounce
        const BALL_DAMPING = 0.9; // Energy loss on ball bounce
        const SUB_STEPS = 8; // Physics sub-steps for stability
        
        // Container Constants
        const HEPTAGON_RADIUS = 220;
        const ROTATION_SPEED_DEG = 360 / 5; // 360 degrees per 5 seconds
        const ROTATION_SPEED_RAD = (2 * Math.PI) / 5; // Radians per second
        
        // Ball Constants
        const BALL_RADIUS = 18;
        const COLORS = [
            "#f8b862", "#f6ad49", "#f39800", "#f08300", "#ec6d51", 
            "#ee7948", "#ed6d3d", "#ec6800", "#ec6800", "#ee7800", 
            "#eb6238", "#ea5506", "#ea5506", "#eb6101", "#e49e61", 
            "#e45e32", "#e17b34", "#dd7a56", "#db8449", "#d66a35"
        ];

        // --- UTILITIES (Vector Math) ---
        class Vector {
            constructor(x, y) { this.x = x; this.y = y; }
            add(v) { return new Vector(this.x + v.x, this.y + v.y); }
            sub(v) { return new Vector(this.x - v.x, this.y - v.y); }
            mult(n) { return new Vector(this.x * n, this.y * n); }
            dot(v) { return this.x * v.x + this.y * v.y; }
            mag() { return Math.sqrt(this.x * this.x + this.y * this.y); }
            normalize() {
                const m = this.mag();
                return m === 0 ? new Vector(0, 0) : new Vector(this.x / m, this.y / m);
            }
            dist(v) { return Math.sqrt(Math.pow(this.x - v.x, 2) + Math.pow(this.y - v.y, 2)); }
        }

        // --- BALL CLASS ---
        class Ball {
            constructor(id, x, y, color) {
                this.id = id;
                this.pos = new Vector(x, y);
                this.vel = new Vector((Math.random() - 0.5) * 10, (Math.random() - 0.5) * 10);
                this.radius = BALL_RADIUS;
                this.color = color;
                this.mass = 1; // Since radius is same, mass is constant
                this.angle = 0;
                this.angularVel = 0;
            }

            update() {
                // Apply Gravity
                this.vel.y += GRAVITY;
                
                // Apply Air Friction
                this.vel = this.vel.mult(FRICTION);
                
                // Update Position
                this.pos = this.pos.add(this.vel);
                
                // Update Rotation based on velocity (visual effect)
                this.angularVel = this.vel.x * 0.05;
                this.angle += this.angularVel;
            }

            draw(ctx) {
                ctx.save();
                ctx.translate(this.pos.x, this.pos.y);
                ctx.rotate(this.angle);

                // Draw Ball Body
                ctx.beginPath();
                ctx.arc(0, 0, this.radius, 0, Math.PI * 2);
                ctx.fillStyle = this.color;
                ctx.fill();
                ctx.strokeStyle = "#333";
                ctx.lineWidth = 2;
                ctx.stroke();

                // Draw Number
                ctx.fillStyle = "#fff";
                ctx.font = "bold 16px Arial";
                ctx.textAlign = "center";
                ctx.textBaseline = "middle";
                ctx.fillText(this.id, 0, 0);
                
                // Draw a line to indicate spin direction
                ctx.beginPath();
                ctx.strokeStyle = "rgba(255,255,255,0.8)";
                ctx.moveTo(0, 0);
                ctx.lineTo(this.radius - 2, 0);
                ctx.stroke();

                ctx.restore();
            }
        }

        // --- GAME STATE ---
        let balls = [];
        let heptagonAngle = 0;
        let isPaused = false;
        let lastTime = 0;

        // --- SPATIAL GRID FOR OPTIMIZATION ---
        class SpatialGrid {
            constructor(cellSize) {
                this.cellSize = cellSize;
                this.grid = new Map();
            }

            clear() {
                this.grid.clear();
            }

            getKey(x, y) {
                const gx = Math.floor(x / this.cellSize);
                const gy = Math.floor(y / this.cellSize);
                return `${gx},${gy}`;
            }

            insert(ball) {
                const key = this.getKey(ball.pos.x, ball.pos.y);
                if (!this.grid.has(key)) {
                    this.grid.set(key, []);
                }
                this.grid.get(key).push(ball);
            }

            getPotentialCollisions(ball) {
                const key = this.getKey(ball.pos.x, ball.pos.y);
                let neighbors = [];
                
                // Check current cell and 8 surrounding cells
                for (let i = -1; i <= 1; i++) {
                    for (let j = -1; j <= 1; j++) {
                        const checkKey = `${parseInt(key.split(',')[0]) + i},${parseInt(key.split(',')[1]) + j}`;
                        if (this.grid.has(checkKey)) {
                            neighbors = neighbors.concat(this.grid.get(checkKey));
                        }
                    }
                }
                return neighbors;
            }
        }

        // --- INITIALIZATION ---
        function initBalls() {
            balls = [];
            // Try to spawn balls near center without massive initial overlap
            for (let i = 0; i < 20; i++) {
                let x, y, valid = false;
                // Simple retry logic to keep them somewhat clustered in center
                for(let attempt=0; attempt<10; attempt++){
                    x = CENTER_X + (Math.random() - 0.5) * 50;
                    y = CENTER_Y + (Math.random() - 0.5) * 50;
                    
                    let overlap = false;
                    for (let b of balls) {
                        if (new Vector(x, y).dist(b.pos) < BALL_RADIUS * 2.2) {
                            overlap = true;
                            break;
                        }
                    }
                    if (!overlap) {
                        valid = true;
                        break;
                    }
                }
                
                // Fallback if couldn't find perfect spot
                if (!valid) {
                    x = CENTER_X + (Math.random() - 0.5) * 100;
                    y = CENTER_Y + (Math.random() - 0.5) * 100;
                }

                balls.push(new Ball(i + 1, x, y, COLORS[i % COLORS.length]));
            }
        }

        function getHeptagonVertices(angle) {
            const vertices = [];
            const sides = 7;
            for (let i = 0; i < sides; i++) {
                const theta = angle + (i * 2 * Math.PI / sides) - (Math.PI / 2); // -PI/2 to start at top
                const x = CENTER_X + HEPTAGON_RADIUS * Math.cos(theta);
                const y = CENTER_Y + HEPTAGON_RADIUS * Math.sin(theta);
                vertices.push(new Vector(x, y));
            }
            return vertices;
        }

        // Closest point on a line segment to a point
        function closestPointOnSegment(p, a, b) {
            const ap = p.sub(a);
            const ab = b.sub(a);
            let t = ap.dot(ab) / ab.dot(ab);
            t = Math.max(0, Math.min(1, t));
            return a.add(ab.mult(t));
        }

        // --- PHYSICS ENGINE ---
        function updatePhysics(dt) {
            // 1. Update Heptagon Rotation
            heptagonAngle += ROTATION_SPEED_RAD * dt;

            const vertices = getHeptagonVertices(heptagonAngle);
            const grid = new SpatialGrid(BALL_RADIUS * 2.5); // Cell size approx 2 balls wide

            // 2. Sub-stepping for stability
            const subStepDt = dt / SUB_STEPS;
            
            for (let step = 0; step < SUB_STEPS; step++) {
                // Clear Grid
                grid.clear();
                
                // Update Balls & Insert into Grid
                balls.forEach(ball => {
                    // Apply forces (scaled for sub-step)
                    ball.vel.y += (GRAVITY / SUB_STEPS);
                    ball.pos = ball.pos.add(ball.vel.mult(subStepDt));
                    
                    // Air friction
                    ball.vel = ball.vel.mult(Math.pow(FRICTION, 1/SUB_STEPS));
                    
                    grid.insert(ball);
                });

                // Ball-to-Ball Collisions
                balls.forEach(ball => {
                    const potentialColliders = grid.getPotentialCollisions(ball);
                    
                    potentialColliders.forEach(other => {
                        if (ball === other) return;

                        const distVec = ball.pos.sub(other.pos);
                        const dist = distVec.mag();
                        const minDist = ball.radius + other.radius;

                        if (dist < minDist) {
                            const n = distVec.normalize();
                            const overlap = minDist - dist;

                            // Position Correction (prevent sticking)
                            const correction = n.mult(overlap / 2);
                            ball.pos = ball.pos.add(correction);
                            other.pos = other.pos.sub(correction);

                            // Velocity Resolution
                            const relVel = ball.vel.sub(other.vel);
                            const velAlongNormal = relVel.dot(n);

                            // Do not resolve if velocities are separating
                            if (velAlongNormal > 0) return;

                            // Simple impulse logic
                            const j = -(1 + BALL_DAMPING) * velAlongNormal;
                            const impulse = n.mult(j / 2); // Assuming equal mass

                            ball.vel = ball.vel.add(impulse);
                            other.vel = other.vel.sub(impulse);
                        }
                    });
                });

                // Wall Collisions
                balls.forEach(ball => {
                    let collided = false;
                    let normal = new Vector(0, 0);
                    let wallVelX = 0;
                    let wallVelY = 0;

                    // Check against all 7 walls
                    for (let i = 0; i < 7; i++) {
                        const p1 = vertices[i];
                        const p2 = vertices[(i + 1) % 7];
                        
                        const closest = closestPointOnSegment(ball.pos, p1, p2);
                        const distVec = ball.pos.sub(closest);
                        const dist = distVec.mag();

                        if (dist < ball.radius) {
                            // Wall collision detected
                            normal = distVec.normalize();
                            
                            // Calculate Wall Velocity at impact point for transfer
                            // V_wall = angular_velocity * radius_vector (tangential)
                            const relativePos = closest.sub(new Vector(CENTER_X, CENTER_Y));
                            const tangentDir = new Vector(-relativePos.y, relativePos.x).normalize();
                            const wallSpeed = ROTATION_SPEED_RAD * relativePos.mag();
                            wallVelX = tangentDir.x * wallSpeed;
                            wallVelY = tangentDir.y * wallSpeed;

                            collided = true;
                            break; // Handle one wall per sub-step is safer for stability
                        }
                    }

                    if (collided) {
                        // 1. Position Correction
                        const penetration = ball.radius - (ball.pos.sub(closest).mag()); // Ensure positive correction
                        // Actually closest point is inside, so we push ball in direction of normal
                        ball.pos = ball.pos.add(normal.mult(ball.radius - dist)); // dist was < radius
                        
                        // 2. Velocity Reflection with Wall Velocity Transfer
                        const relVel = new Vector(ball.vel.x - wallVelX, ball.vel.y - wallVelY);
                        const sepVel = relVel.dot(normal);
                        const newSepVel = -sepVel * WALL_DAMPING;
                        const vCorrection = normal.mult(newSepVel - sepVel);
                        
                        ball.vel.x += vCorrection.x;
                        ball.vel.y += vCorrection.y;
                    }
                });
            }
        }

        // --- RENDERING ---
        function drawHeptagon() {
            const vertices = getHeptagonVertices(heptagonAngle);
            
            ctx.save();
            ctx.beginPath();
            ctx.moveTo(vertices[0].x, vertices[0].y);
            for (let i = 1; i < vertices.length; i++) {
                ctx.lineTo(vertices[i].x, vertices[i].y);
            }
            ctx.closePath();
            
            // Fill
            const gradient = ctx.createRadialGradient(CENTER_X, CENTER_Y, HEPTAGON_RADIUS * 0.2, CENTER_X, CENTER_Y, HEPTAGON_RADIUS);
            gradient.addColorStop(0, "#f0f0f0");
            gradient.addColorStop(1, "#dcdcdc");
            ctx.fillStyle = gradient;
            ctx.fill();
            
            // Stroke
            ctx.lineWidth = 5;
            ctx.strokeStyle = "#333";
            ctx.stroke();
            
            // Draw rotation indicator (small triangle at top)
            ctx.beginPath();
            const topVertex = vertices[0];
            const nextVertex = vertices[1];
            const midPoint = new Vector((topVertex.x + nextVertex.x) / 2, (topVertex.y + nextVertex.y) / 2);
            
            ctx.fillStyle = "red";
            ctx.arc(midPoint.x, midPoint.y, 5, 0, Math.PI*2);
            ctx.fill();
            
            ctx.restore();
        }

        function gameLoop(timestamp) {
            if (isPaused) {
                requestAnimationFrame(gameLoop);
                return;
            }

            // Calculate Delta Time (in seconds)
            if (!lastTime) lastTime = timestamp;
            const dt = (timestamp - lastTime) / 1000;
            lastTime = timestamp;

            // Cap dt to prevent physics explosions on lag spikes
            const safeDt = Math.min(dt, 0.05);

            ctx.clearRect(0, 0, W, H);

            // --- Logic ---
            updatePhysics(safeDt);

            // --- Draw ---
            drawHeptagon();
            
            balls.forEach(ball => ball.draw(ctx));

            requestAnimationFrame(gameLoop);
        }

        function resetSimulation() {
            initBalls();
            heptagonAngle = 0;
            lastTime = 0;
        }

        function togglePause() {
            isPaused = !isPaused;
            if(!isPaused) {
                lastTime = performance.now();
                requestAnimationFrame(gameLoop);
            }
        }

        // Start
        initBalls();
        requestAnimationFrame(gameLoop);

    </script>
    <section id="notes">
        <h3>Implementation Details</h3>
        <ul>
            <li><strong>Physics Sub-stepping:</strong> The simulation runs 8 physics steps per frame to ensure collisions are resolved accurately, preventing balls from tunneling through walls or each other.</li>
            <li><strong>Spatial Grid:</strong> An optimization technique where the canvas is divided into a grid. Balls only check for collisions against other balls in their immediate grid cells, reducing O(n^2) complexity to roughly O(n).</li>
            <li><strong>Wall Collision:</strong> The wall velocity is calculated based on the rotation speed and the distance from the center (Tangential Velocity = Angular Velocity * Radius). This imparts momentum to the ball when it hits the moving wall.</li>
            <li><strong>Heptagon Math:</strong> Vertices are calculated using trigonometry based on the current rotation angle.</li>
            <li><strong>Visuals:</strong> Balls rotate based on their horizontal velocity to simulate friction/spin. A red dot indicates the "top" corner of the heptagon to visualize rotation.</li>
        </ul>
    </section>
</body>
</html>
```

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: Qwen3-Coder-Next-UD-Q3_K_XL.gguf -->
<!-- Prompt: heptagon.md -->
<!-- Time: 57.62s -->
<!-- Fallback: False -->