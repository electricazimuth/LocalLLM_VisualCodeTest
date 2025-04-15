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

        const gravity = 0.2;
        const damping = 0.8;
        const numBalls = 50;

        // Ball class
        class Ball {
            constructor(x, y, vx, vy, r, color) {
                this.x = x;
                this.y = y;
                this.vx = vx;
                this.vy = vy;
                this.r = r;
                this.color = color;
            }

            draw() {
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.r, 0, Math.PI * 2);
                ctx.fillStyle = this.color;
                ctx.fill();
            }

            update() {
                this.vy += gravity;
                this.x += this.vx;
                this.y += this.vy;

                // Wall collisions
                if (this.x + this.r > W || this.x - this.r < 0) {
                    this.vx = -this.vx * damping;
                    this.x += this.vx; // Correct position
                }
                if (this.y + this.r > H || this.y - this.r < 0) {
                    this.vy = -this.vy * damping;
                    this.y += this.vy; // Correct position
                }
            }
        }

        // Create balls
        const balls = [];
        for (let i = 0; i < numBalls; i++) {
            let x = Math.random() * W;
            let y = Math.random() * H;
            let r = Math.random() * 15 + 5; // Random radius
            let vx = (Math.random() - 0.5) * 4;
            let vy = (Math.random() - 0.5) * 4;
            let color = `hsl(${Math.random() * 360}, 100%, 50%)`; // Random color

            balls.push(new Ball(x, y, vx, vy, r, color));
        }

        function checkCollision(ball1, ball2) {
            const distance = Math.sqrt(Math.pow(ball2.x - ball1.x, 2) + Math.pow(ball2.y - ball1.y, 2));
            return distance <= ball1.r + ball2.r;
        }

        function handleCollision(ball1, ball2) {
            // Simple collision response - reverse velocities on collision
            const tempVx = ball1.vx;
            const tempVy = ball1.vy;
            ball1.vx = ball2.vx;
            ball1.vy = ball2.vy;
            ball2.vx = tempVx;
            ball2.vy = tempVy;
        }

        function gameLoop(timestamp) {
            ctx.clearRect(0, 0, W, H);

            for (let i = 0; i < balls.length; i++) {
                balls[i].update();
                balls[i].draw();

                // Ball-ball collision detection (naive approach)
                for (let j = i + 1; j < balls.length; j++) {
                    if (checkCollision(balls[i], balls[j])) {
                        handleCollision(balls[i], balls[j]);
                    }
                }
            }

            requestAnimationFrame(gameLoop);
        }

        requestAnimationFrame(gameLoop);

    </script>
    <section id="notes">
    
    </section>
</body>
</html>
```

**Explanation:**

1.  **Ball Class:** A `Ball` class is defined to represent each ball, holding properties like position (`x`, `y`), velocity (`vx`, `vy`), radius (`r`), and color.

2.  **Initialization:**
    *   An array `balls` is created to store all the ball objects.
    *   50 ball objects are created with random positions, velocities, radii, and colors.

3.  **Game Loop:**
    *   `gameLoop` is the main animation loop using `requestAnimationFrame`.

4.  **Update:**
    *   Inside the loop, each ball's `update()` method is called:
        *   Gravity is applied to the vertical velocity (`vy`).
        *   Position is updated based on velocity.
        *   Wall collisions are detected, and if a collision occurs:
            *   The corresponding velocity component is reversed.
            *   Damping is applied to reduce the velocity after the bounce.
            *   The ball's position is corrected to ensure it's fully inside the boundary.

5.  **Collision Detection:**
    *   The `checkCollision` function calculates the distance between the centers of two balls. If the distance is less than or equal to the sum of their radii, a collision is detected.

6.  **Collision Response:**
    *   The `handleCollision` function simply reverses the velocities of the colliding balls. This is a basic collision response, and more sophisticated physics-based responses could be implemented for a more realistic simulation.

7.  **Drawing:**
    *   Each ball's `draw()` method is called to draw it on the canvas as a filled circle.

8.  **Optimization:**

    *   The code includes a naive collision detection approach (checking every ball pair). For a large number of balls, this can become inefficient. In a more optimized solution, you could use spatial partitioning techniques (like grids or quadtrees) to reduce the number of collision checks.



Let me know if you'd like to explore adding more advanced features or optimization techniques!
 <!-- 127.51s -->