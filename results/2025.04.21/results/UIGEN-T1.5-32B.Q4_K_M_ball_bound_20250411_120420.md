```html
<!DOCTYPE html>
<html>
<head>
    <title>Bouncing Balls Simulation</title>
    <style>
        body { margin: 0; overflow: hidden; background-color: #f0f0f0; }
        canvas { display: block; margin: 0 auto; background-color: #000; }
        section { color: #fff; text-align: center; padding: 10px; position: fixed; top: 0; left: 0; width: 100%; background: rgba(0,0,0,0.5); }
    </style>
</head>
<body>
    <section id="notes">
        <h1>Bouncing Balls Simulation</h1>
        <p>Press the spacebar to pause/resume the simulation.</p>
        <p>Click and drag to create a new ball.</p>
        <p>Use arrow keys to adjust ball count (up/down) or ball radius (left/right).</p>
    </section>
    <canvas id="gameCanvas"></canvas>
    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;

        const balls = [];
        const numBalls = 50;
        let paused = false;
        let dragStart = null;
        let newBall = null;
        let ballCount = numBalls;
        let ballRadius = 10;

        const GRAVITY = 0.2;
        const DAMPING = 0.8;
        const ELASTICITY = 0.8;

        class Ball {
            constructor(x, y, vx, vy, radius, color) {
                this.x = x;
                this.y = y;
                this.vx = vx;
                this.vy = vy;
                this.radius = radius;
                this.color = color;
            }

            draw() {
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
                ctx.fillStyle = this.color;
                ctx.fill();
            }

            update() {
                this.vy += GRAVITY;
                this.x += this.vx;
                this.y += this.vy;

                if (this.x + this.radius > canvas.width || this.x - this.radius < 0) {
                    this.vx *= -DAMPING;
                    if (this.x + this.radius > canvas.width) this.x = canvas.width - this.radius;
                    if (this.x - this.radius < 0) this.x = this.radius;
                }

                if (this.y + this.radius > canvas.height || this.y - this.radius < 0) {
                    this.vy *= -DAMPING;
                    if (this.y + this.radius > canvas.height) this.y = canvas.height - this.radius;
                    if (this.y - this.radius < 0) this.y = this.radius;
                }
            }

            collide(other) {
                const dx = other.x - this.x;
                const dy = other.y - this.y;
                const distance = Math.sqrt(dx * dx + dy * dy);
                const minDistance = this.radius + other.radius;

                if (distance < minDistance) {
                    const overlap = minDistance - distance;
                    const angle = Math.atan2(dy, dx);

                    this.x -= overlap * Math.cos(angle);
                    this.y -= overlap * Math.sin(angle);

                    const ax = (this.vx * (this.radius - other.radius) + 2 * other.radius * other.vx) / (this.radius + other.radius);
                    const ay = (this.vy * (this.radius - other.radius) + 2 * other.radius * other.vy) / (this.radius + other.radius);
                    const bx = (other.vx * (other.radius - this.radius) + 2 * this.radius * this.vx) / (this.radius + other.radius);
                    const by = (other.vy * (other.radius - this.radius) + 2 * this.radius * this.vy) / (this.radius + other.radius);

                    this.vx = ax * ELASTICITY;
                    this.vy = ay * ELASTICITY;
                    other.vx = bx * ELASTICITY;
                    other.vy = by * ELASTICITY;
                }
            }
        }

        function createBalls(count) {
            for (let i = 0; i < count; i++) {
                const radius = Math.random() * 10 + 5;
                const x = Math.random() * (canvas.width - 2 * radius) + radius;
                const y = Math.random() * (canvas.height - 2 * radius) + radius;
                const vx = Math.random() * 5 - 2.5;
                const vy = Math.random() * 5 - 2.5;
                const color = `hsl(${Math.random() * 360}, 100%, 50%)`;
                balls.push(new Ball(x, y, vx, vy, radius, color));
            }
        }

        createBalls(ballCount);

        function gameLoop(timestamp) {
            if (!paused) {
                ctx.clearRect(0, 0, canvas.width, canvas.height);

                for (const ball of balls) {
                    ball.update();
                    for (const other of balls) {
                        if (ball !== other) ball.collide(other);
                    }
                    ball.draw();
                }

                if (newBall) newBall.draw();
            }

            requestAnimationFrame(gameLoop);
        }

        gameLoop();

        canvas.addEventListener('mousedown', (e) => {
            dragStart = { x: e.clientX, y: e.clientY };
            newBall = new Ball(e.clientX, e.clientY, 0, 0, ballRadius, 'white');
        });

        canvas.addEventListener('mousemove', (e) => {
            if (dragStart && newBall) {
                newBall.x = e.clientX;
                newBall.y = e.clientY;
            }
        });

        canvas.addEventListener('mouseup', (e) => {
            if (dragStart && newBall) {
                newBall.vx = (e.clientX - dragStart.x) / 10;
                newBall.vy = (e.clientY - dragStart.y) / 10;
                balls.push(newBall);
                newBall = null;
            }
            dragStart = null;
        });

        document.addEventListener('keydown', (e) => {
            if (e.code === 'Space') {
                paused = !paused;
            } else if (e.code === 'ArrowUp') {
                if (balls.length < 100) {
                    createBalls(1);
                }
            } else if (e.code === 'ArrowDown' && balls.length > 0) {
                balls.pop();
            } else if (e.code === 'ArrowLeft') {
                ballRadius = Math.max(5, ballRadius - 1);
                if (newBall) newBall.radius = ballRadius;
            } else if (e.code === 'ArrowRight') {
                ballRadius = Math.min(20, ballRadius + 1);
                if (newBall) newBall.radius = ballRadius;
            }
        });
    </script>
</body>
</html>
```

**Explanation:**

1. **HTML Structure:** The HTML file includes a `canvas` element and a `section` for notes. The `canvas` is styled to fill the viewport and have a black background for contrast. The `section` is styled to be fixed at the top of the viewport with a semi-transparent background.

2. **CSS Styling:** Basic CSS is used for layout and visual presentation. The `body` has no margin and hides overflow. The `canvas` is centered and has a block display. The `section` is styled to be fixed at the top, with padding, centered text, and a semi-transparent black background.

3. **JavaScript Logic:**
   - **Ball Class:** A `Ball` class is defined to represent each bouncing ball. It has properties for position (`x`, `y`), velocity (`vx`, `vy`), radius, and color. Methods include `draw()` to render the ball on the canvas and `update()` to handle physics updates (gravity, collisions with walls, and other balls).
   - **Collision Detection & Response:** The `collide()` method in the `Ball` class handles ball-to-ball collisions. It calculates the distance between two balls and checks if they overlap. If they do, it calculates the overlap and adjusts positions to prevent sticking. It then calculates and applies new velocities based on elasticity and conservation of momentum.
   - **Game Loop:** The `gameLoop()` function is responsible for the main animation loop. It clears the canvas, updates each ball's position and handles collisions, and redraws all balls. The loop runs smoothly using `requestAnimationFrame()`.
   - **Ball Creation and Control:** Initially, a specified number of balls (`numBalls`) are created with random properties. The user can create new balls by clicking and dragging on the canvas. The ball count and radius can be adjusted using arrow keys, and simulation can be paused/resumed with the spacebar. These interactions are handled through event listeners for mouse and keyboard events.
   - **Optimization:** The code uses a simple approach for collision detection, checking each pair of balls. For more advanced simulations, spatial partitioning techniques like grids or quadtrees could be implemented to improve collision detection efficiency, especially with a larger number of balls. However, for the current requirement of 50+ balls, this basic approach should perform reasonably well in a browser environment.

This solution meets all the specified requirements and provides a robust and interactive bouncing balls simulation using HTML, CSS, and JavaScript. It includes features for creating, updating, and drawing balls, handling physics interactions (gravity, wall collisions, and ball-to-ball collisions), and user control through keyboard and mouse interactions. The code is structured using classes and functions for clarity and maintainability, and it is optimized for performance within the constraints of a browser-based simulation.
 <!-- 227.15s -->