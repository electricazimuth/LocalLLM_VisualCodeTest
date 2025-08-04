Certainly! Below is the complete implementation of the "Happy Mrs. Chicken" simulation using plain JavaScript and the Canvas API. The code is encapsulated within a single HTML file.

```html
<!DOCTYPE html>
<html>
<head>
    <title>Chicken Simulation</title>
    <style>
        body { margin: 10px; overflow: hidden; background-color: #eee; }
        canvas { display: block; margin: 20px auto; border: 1px solid #999; background-color: #90ee90; } /* Light green grass background */
    </style>
</head>
<body>
    <canvas id="simulationCanvas" width="512" height="512"></canvas>

    <script>
        const canvas = document.getElementById('simulationCanvas');
        const ctx = canvas.getContext('2d');

        // Configuration constants
        const CHICKEN_SIZE = 20;
        const EGG_SIZE = 10;
        const CHICKEN_COLOR = '#FFCC00';
        const EGG_COLOR = '#FFFFFF';
        const CHICKEN_SPEED = 1;
        const LAY_EGG_INTERVAL = 2000; // milliseconds
        const PAUSE_DURATION = 500; // milliseconds

        class Chicken {
            constructor(x, y) {
                this.x = x;
                this.y = y;
                this.direction = Math.random() * Math.PI * 2;
                this.speed = CHICKEN_SPEED;
                this.state = 'wandering';
                this.lastLayTime = 0;
                this.pauseEndTime = 0;
            }

            update(deltaTime) {
                if (this.state === 'laying') {
                    if (performance.now() > this.pauseEndTime) {
                        this.state = 'wandering';
                        this.direction = Math.random() * Math.PI * 2;
                    }
                } else if (this.state === 'wandering') {
                    this.x += Math.cos(this.direction) * this.speed * deltaTime;
                    this.y += Math.sin(this.direction) * this.speed * deltaTime;

                    // Boundary checking and direction change on collision
                    if (this.x < CHICKEN_SIZE / 2 || this.x > canvas.width - CHICKEN_SIZE / 2) {
                        this.direction = Math.PI - this.direction;
                    }
                    if (this.y < CHICKEN_SIZE / 2 || this.y > canvas.height - CHICKEN_SIZE / 2) {
                        this.direction = -this.direction;
                    }

                    // Randomly change direction
                    if (Math.random() < 0.01) {
                        this.direction = Math.random() * Math.PI * 2;
                    }

                    // Check if it's time to lay an egg
                    if (performance.now() - this.lastLayTime > LAY_EGG_INTERVAL) {
                        this.state = 'laying';
                        this.pauseEndTime = performance.now() + PAUSE_DURATION;
                        eggs.push(new Egg(this.x, this.y));
                        this.lastLayTime = performance.now();
                    }
                }
            }

            draw() {
                ctx.save();
                ctx.translate(this.x, this.y);
                ctx.rotate(this.direction);
                ctx.fillStyle = this.state === 'laying' ? '#FF9900' : CHICKEN_COLOR;
                ctx.beginPath();
                ctx.ellipse(0, 0, CHICKEN_SIZE, CHICKEN_SIZE, 0, 0, Math.PI * 2);
                ctx.fill();
                ctx.beginPath();
                ctx.moveTo(CHICKEN_SIZE, 0);
                ctx.lineTo(CHICKEN_SIZE + CHICKEN_SIZE / 2, CHICKEN_SIZE / 2);
                ctx.lineTo(CHICKEN_SIZE + CHICKEN_SIZE / 2, -CHICKEN_SIZE / 2);
                ctx.fill();
                ctx.restore();
            }
        }

        class Egg {
            constructor(x, y) {
                this.x = x;
                this.y = y;
            }

            draw() {
                ctx.fillStyle = EGG_COLOR;
                ctx.beginPath();
                ctx.ellipse(this.x, this.y, EGG_SIZE, EGG_SIZE, 0, 0, Math.PI * 2);
                ctx.fill();
            }
        }

        const chicken = new Chicken(canvas.width / 2, canvas.height / 2);
        const eggs = [];

        let lastTime = performance.now();

        function animate() {
            const currentTime = performance.now();
            const deltaTime = (currentTime - lastTime) / 1000;
            lastTime = currentTime;

            ctx.clearRect(0, 0, canvas.width, canvas.height);

            chicken.update(deltaTime);
            chicken.draw();

            eggs.forEach(egg => egg.draw());

            requestAnimationFrame(animate);
        }

        animate();
    </script>

    <!-- Optional section for notes -->
    <section id="notes">
        <p>The simulation runs a chicken character that wanders around the canvas and lays eggs at random intervals. The chicken changes direction randomly and avoids the canvas boundaries. Each egg is drawn at the chicken's position when it lays an egg and remains static.</p>
    </section>
</body>
</html>
```

### Explanation:
1. **Chicken Class:**
   - Represents the chicken character.
   - Contains properties for position, direction, speed, state, and timestamps for egg-laying.
   - The `update` method handles movement, boundary checking, direction changes, and egg-laying.
   - The `draw` method renders the chicken, with a color change during the laying state.

2. **Egg Class:**
   - Represents an egg object.
   - Contains properties for position.
   - The `draw` method renders the egg.

3. **Animation Loop:**
   - Uses `requestAnimationFrame` for smooth animation.
   - Calculates delta time for frame-rate independent movement.
   - Updates and draws the chicken and eggs in each frame.

4. **Visual Elements:**
   - The chicken is drawn as an ellipse with a beak.
   - Eggs are drawn as ellipses.

5. **Boundary Handling:**
   - The chicken changes direction upon hitting the canvas boundaries.

6. **Egg Laying:**
   - The chicken lays an egg at random intervals and pauses briefly during the laying action.

This implementation provides a simple yet engaging simulation of a chicken wandering around the canvas and laying eggs.

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: microsoft_NextCoder-32B-Q6_K_L.gguf -->
<!-- Prompt: chicken.md -->
<!-- Generation Time: 53.77s -->
<!-- Fallback Used: False -->