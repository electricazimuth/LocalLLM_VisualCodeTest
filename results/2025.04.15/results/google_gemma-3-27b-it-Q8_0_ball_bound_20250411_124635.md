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

        const numBalls = 50;
        const gravityValue = 0.2;
        const dampingFactor = 0.8;

        class Ball {
            constructor(x, y, r, color) {
                this.x = x;
                this.y = y;
                this.r = r;
                this.color = color;
                this.vx = (Math.random() - 0.5) * 5;
                this.vy = (Math.random() - 0.5) * 5;
                this.mass = Math.PI * r * r;
            }

            draw() {
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.r, 0, 2 * Math.PI);
                ctx.fillStyle = this.color;
                ctx.fill();
                ctx.closePath();
            }

            update() {
                this.vy += gravityValue;
                this.x += this.vx;
                this.y += this.vy;

                // Wall collision
                if (this.x + this.r > W || this.x - this.r < 0) {
                    this.vx = -this.vx * dampingFactor;
                    this.x = Math.max(this.r, Math.min(this.x, W - this.r));
                }
                if (this.y + this.r > H || this.y - this.r < 0) {
                    this.vy = -this.vy * dampingFactor;
                    this.y = Math.max(this.r, Math.min(this.y, H - this.r));
                }
            }
        }

        let balls = [];
        for (let i = 0; i < numBalls; i++) {
            let r = Math.random() * 15 + 5;
            let x = Math.random() * (W - 2 * r) + r;
            let y = Math.random() * (H - 2 * r) + r;
            let color = `hsl(${Math.random() * 360}, 100%, 50%)`;
            balls.push(new Ball(x, y, r, color));
        }

        function detectCollision(ball1, ball2) {
            const dx = ball2.x - ball1.x;
            const dy = ball2.y - ball1.y;
            const distance = Math.sqrt(dx * dx + dy * dy);
            return distance <= ball1.r + ball2.r;
        }

        function resolveCollision(ball1, ball2) {
            const dx = ball2.x - ball1.x;
            const dy = ball2.y - ball1.y;
            const distance = Math.sqrt(dx * dx + dy * dy);
            const overlap = ball1.r + ball2.r - distance;
            const nx = dx / distance;
            const ny = dy / distance;

            const impulse = (1 + dampingFactor) * (ball1.vx - ball2.vx) * nx + (ball1.vy - ball2.vy) * ny;
            impulse /= (1 / ball1.mass + 1 / ball2.mass);

            ball1.vx += impulse / ball1.mass * nx;
            ball1.vy += impulse / ball1.mass * ny;
            ball2.vx -= impulse / ball2.mass * nx;
            ball2.vy -= impulse / ball2.mass * ny;

            // Move balls apart to resolve overlap
            ball1.x -= overlap / 2 * nx;
            ball1.y -= overlap / 2 * ny;
            ball2.x += overlap / 2 * nx;
            ball2.y += overlap / 2 * ny;
        }

        function gameLoop(timestamp) {
            ctx.clearRect(0, 0, W, H);

            // Update and draw balls
            for (let i = 0; i < balls.length; i++) {
                balls[i].update();
                balls[i].draw();
            }

            // Collision detection
            for (let i = 0; i < balls.length; i++) {
                for (let j = i + 1; j < balls.length; j++) {
                    if (detectCollision(balls[i], balls[j])) {
                        resolveCollision(balls[i], balls[j]);
                    }
                }
            }

            requestAnimationFrame(gameLoop);
        }

        // Start the loop
        requestAnimationFrame(gameLoop);

    </script>
    <section id="notes">
        <p>This simulation creates bouncing balls with gravity, wall collisions (with damping), and ball-to-ball collisions.  The collision resolution uses a simple impulse-based approach to transfer momentum.  The collision detection is O(n^2), which could be improved with spatial partitioning (e.g., a grid) for a larger number of balls. The damping factor reduces energy loss on collisions to create a more realistic effect.  HSL colors are used for variety.</p>
    </section>
</body>
</html>
```
 <!-- 156.22s -->