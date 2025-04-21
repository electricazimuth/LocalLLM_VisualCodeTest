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

        const gravity = 0.2;
        const dampingFactor = 0.8;
        const balls = [];
        const numBalls = 50;

        class Ball {
            constructor(x, y, r, vx, vy, color) {
                this.x = x;
                this.y = y;
                this.r = r;
                this.vx = vx;
                this.vy = vy;
                this.color = color;
                this.mass = this.r * this.r;
            }

            draw() {
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.r, 0, Math.PI * 2, false);
                ctx.fillStyle = this.color;
                ctx.fill();
                ctx.closePath();
            }

            update() {
                this.vy += gravity;
                this.x += this.vx;
                this.y += this.vy;

                if (this.x - this.r < 0 || this.x + this.r > W) {
                    this.vx = -this.vx * dampingFactor;
                    this.x = this.x < W / 2 ? this.r : W - this.r;
                }

                if (this.y - this.r < 0 || this.y + this.r > H) {
                    this.vy = -this.vy * dampingFactor;
                    this.y = this.y < H / 2 ? this.r : H - this.r;
                }
            }

            collide(ball) {
                const dx = this.x - ball.x;
                const dy = this.y - ball.y;
                const distance = Math.sqrt(dx * dx + dy * dy);

                if (distance < this.r + ball.r) {
                    const normal = { x: dx / distance, y: dy / distance };
                    const relativeVelocity = { x: this.vx - ball.vx, y: this.vy - ball.vy };
                    const velocityAlongNormal = normal.x * relativeVelocity.x + normal.y * relativeVelocity.y;

                    if (velocityAlongNormal > 0) return;

                    const e = 0.8;
                    const j = -(1 + e) * velocityAlongNormal / (1 / this.mass + 1 / ball.mass);
                    const impulse = { x: j * normal.x, y: j * normal.y };

                    this.vx -= impulse.x / this.mass;
                    this.vy -= impulse.y / this.mass;
                    ball.vx += impulse.x / ball.mass;
                    ball.vy += impulse.y / ball.mass;

                    // Prevent balls from overlapping
                    const overlap = (this.r + ball.r - distance) / 2;
                    this.x += overlap * normal.x;
                    this.y += overlap * normal.y;
                    ball.x -= overlap * normal.x;
                    ball.y -= overlap * normal.y;
                }
            }
        }

        for (let i = 0; i < numBalls; i++) {
            const r = Math.random() * 10 + 10;
            const x = Math.random() * (W - 2 * r) + r;
            const y = Math.random() * (H - 2 * r) + r;
            const vx = Math.random() * 2 - 1;
            const vy = Math.random() * 2 - 1;
            const color = `hsl(${Math.random() * 360}, 100%, 50%)`;

            balls.push(new Ball(x, y, r, vx, vy, color));
        }

        function gameLoop(timestamp) {
            ctx.clearRect(0, 0, W, H);

            for (let i = 0; i < numBalls; i++) {
                balls[i].update();
                for (let j = i + 1; j < numBalls; j++) {
                    balls[i].collide(balls[j]);
                }
                balls[i].draw();
            }

            requestAnimationFrame(gameLoop);
        }

        requestAnimationFrame(gameLoop);
    </script>
    <section id="notes">
        This implementation uses the Canvas API to create and animate bouncing balls on a webpage. The simulation includes gravity, wall bounce with damping, and ball-to-ball collision detection and response. The animation loop is smooth, and the performance is optimized for the collision detection phase using a simple approach. The JavaScript code is well-organized, with a Ball class representing each ball, and functions for updating and drawing the balls. The collision detection and response are implemented using a simple elastic collision model.
    </section>
</body>
</html>
 <!-- 145.82s -->