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
        // --- YOUR JAVASCRIPT CODE GOES HERE ---
        // Setup canvas, context, chicken object, egg array, animation loop, etc.

        // Canvas setup
        const canvas = document.getElementById('simulationCanvas');
        const ctx = canvas.getContext('2d');

        // Game constants
        const CHICKEN_SIZE = 40;
        const EGG_SIZE = 20;
        const EGG_LAY_TIME = 1500; // ms between egg lays
        const LAY_DURATION = 300; // ms for laying animation
        const MOVE_SPEED = 1.5; // pixels per ms
        const TURN_FREQUENCY = 1000; // ms for random direction change
        const BOUNDARY_PADDING = 10; // padding from edges

        // Egg class
        class Egg {
            constructor(x, y) {
                this.x = x;
                this.y = y;
                this.spawnTime = Date.now();
                this.lifespan = 10000; // 10 seconds before disappearing
            }

            draw() {
                const age = Date.now() - this.spawnTime;
                const opacity = 1 - (age / this.lifespan); // Fade out over time
                if (opacity <= 0) return; // Don't draw if expired

                ctx.save();
                ctx.globalAlpha = opacity;
                ctx.beginPath();
                ctx.ellipse(this.x, this.y, EGG_SIZE / 2, EGG_SIZE / 3, 0, 0, Math.PI * 2);
                ctx.fillStyle = '#f5f5dc'; // Beige egg color
                ctx.fill();
                ctx.strokeStyle = '#d2b48c';
                ctx.lineWidth = 2;
                ctx.stroke();
                ctx.restore();
            }
        }

        // Chicken class
        class Chicken {
            constructor(x, y) {
                this.x = x;
                this.y = y;
                this.vx = 0;
                this.vy = 0;
                this.direction = Math.random() * Math.PI * 2; // Initial random direction
                this.speed = MOVE_SPEED;
                this.state = 'wandering'; // 'wandering' or 'laying'
                this.layTimer = 0;
                this.layStartTime = 0;
                this.layDuration = LAY_DURATION;
                this.lastTurnTime = 0;
                this.turnInterval = TURN_FREQUENCY;
                this.isLaying = false;
                this.color = '#ffcc80'; // Light orange
                this.beakColor = '#ff9933';
                this.eyeColor = '#000000';
                this.eggLayInterval = EGG_LAY_TIME;
            }

            update(deltaTime) {
                // Update laying timer
                if (this.state === 'laying') {
                    this.layTimer += deltaTime;
                    if (this.layTimer >= this.layDuration) {
                        this.state = 'wandering';
                        this.layTimer = 0;
                        this.isLaying = false;
                    }
                } else {
                    // Increment timer for egg laying
                    this.layTimer += deltaTime;
                    if (this.layTimer >= this.eggLayInterval) {
                        this.startLaying();
                    }
                }

                // Handle turning randomly
                if (this.state === 'wandering') {
                    const timeSinceLastTurn = Date.now() - this.lastTurnTime;
                    if (timeSinceLastTurn > this.turnInterval) {
                        this.direction = Math.random() * Math.PI * 2;
                        this.lastTurnTime = Date.now();
                    }

                    // Calculate velocity based on direction
                    this.vx = Math.cos(this.direction) * this.speed;
                    this.vy = Math.sin(this.direction) * this.speed;
                }

                // Update position
                if (this.state === 'wandering') {
                    this.x += this.vx * deltaTime;
                    this.y += this.vy * deltaTime;

                    // Boundary collision
                    if (this.x < BOUNDARY_PADDING) {
                        this.x = BOUNDARY_PADDING;
                        this.direction = Math.PI - this.direction; // Reverse x-direction
                    }
                    if (this.x > canvas.width - BOUNDARY_PADDING) {
                        this.x = canvas.width - BOUNDARY_PADDING;
                        this.direction = Math.PI - this.direction; // Reverse x-direction
                    }
                    if (this.y < BOUNDARY_PADDING) {
                        this.y = BOUNDARY_PADDING;
                        this.direction = -this.direction; // Reverse y-direction
                    }
                    if (this.y > canvas.height - BOUNDARY_PADDING) {
                        this.y = canvas.height - BOUNDARY_PADDING;
                        this.direction = -this.direction; // Reverse y-direction
                    }
                }
            }

            startLaying() {
                this.state = 'laying';
                this.layTimer = 0;
                this.isLaying = true;
                this.layStartTime = Date.now();
                // Create egg slightly behind the chicken (towards tail)
                const tailOffset = CHICKEN_SIZE * 0.4;
                const eggX = this.x - Math.cos(this.direction) * tailOffset;
                const eggY = this.y - Math.sin(this.direction) * tailOffset;
                eggs.push(new Egg(eggX, eggY));
                this.layTimer = 0;
            }

            draw() {
                ctx.save();
                ctx.translate(this.x, this.y);
                ctx.rotate(this.direction);

                // Draw body (oval)
                ctx.beginPath();
                ctx.ellipse(0, 0, CHICKEN_SIZE / 2, CHICKEN_SIZE / 3, 0, 0, Math.PI * 2);
                ctx.fillStyle = this.isLaying ? '#ff8c00' : this.color; // Slight color change when laying
                ctx.fill();

                // Draw wings (two small ovals)
                ctx.beginPath();
                ctx.ellipse(-CHICKEN_SIZE / 3, -CHICKEN_SIZE / 4, CHICKEN_SIZE / 6, CHICKEN_SIZE / 8, 0, 0, Math.PI * 2);
                ctx.fillStyle = '#ffa07a';
                ctx.fill();

                ctx.beginPath();
                ctx.ellipse(CHICKEN_SIZE / 4, -CHICKEN_SIZE / 4, CHICKEN_SIZE / 6, CHICKEN_SIZE / 8, 0, 0, Math.PI * 2);
                ctx.fillStyle = '#ffa07a';
                ctx.fill();

                // Draw beak (triangle)
                ctx.beginPath();
                ctx.moveTo(0, 0);
                ctx.lineTo(CHICKEN_SIZE / 2, -CHICKEN_SIZE / 6);
                ctx.lineTo(CHICKEN_SIZE / 2, CHICKEN_SIZE / 6);
                ctx.closePath();
                ctx.fillStyle = this.beakColor;
                ctx.fill();

                // Draw eye (circle)
                ctx.beginPath();
                ctx.arc(CHICKEN_SIZE / 3, -CHICKEN_SIZE / 5, CHICKEN_SIZE / 10, 0, Math.PI * 2);
                ctx.fillStyle = this.eyeColor;
                ctx.fill();

                ctx.restore();
            }
        }

        // Game state
        let chicken;
        let eggs = [];
        let lastTime = 0;

        // Initialize game
        function init() {
            chicken = new Chicken(canvas.width / 2, canvas.height / 2);
            eggs = [];
        }

        // Animation loop
        function animate(currentTime) {
            const deltaTime = currentTime - lastTime;
            lastTime = currentTime;

            // Update game state
            chicken.update(deltaTime);

            // Update eggs (remove expired ones)
            eggs = eggs.filter(egg => Date.now() - egg.spawnTime < egg.lifespan);

            // Clear canvas
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // Draw everything
            chicken.draw();
            eggs.forEach(egg => egg.draw());

            // Continue animation
            requestAnimationFrame(animate);
        }

        // Start the simulation
        init();
        requestAnimationFrame(animate);

    </script>

    <!-- Optional section for notes -->
    <section id="notes">
        <h3>Developer Notes</h3>
        <p><strong>Implementation Approach:</strong></p>
        <ul>
            <li><strong>Object-Oriented Design:</strong> Used classes for <code>Chicken</code> and <code>Egg</code> to encapsulate behavior and properties.</li>
            <li><strong>State Management:</strong> Chicken has states ('wandering', 'laying') with timers to manage transitions.</li>
            <li><strong>Frame-Rate Independent Animation:</strong> Used <code>deltaTime</code> to ensure smooth movement and timing regardless of frame rate.</li>
            <li><strong>Boundary Handling:</strong> Chicken bounces off edges with direction reversal to stay within bounds.</li>
            <li><strong>Egg Lifecycle:</strong> Eggs appear at chicken's tail position, fade out over 10 seconds, and are removed from array when expired.</li>
            <li><strong>Visual Feedback:</strong> Chicken turns slightly orange during laying state for visual cue.</li>
            <li><strong>Random Wandering:</strong> Direction changes randomly every 1-2 seconds to simulate natural movement.</li>
        </ul>
        <p><strong>Visual Details:</strong></p>
        <ul>
            <li>Chicken is drawn as an oval body with wings, beak, and eye.</li>
            <li>Eggs are ellipses with a slight fade-out effect.</li>
            <li>Canvas has a light green background to simulate grass.</li>
        </ul>
    </section>

</body>
</html>
```

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: Qwen3-VL-32B-Instruct-UD-Q6_K_XL.gguf -->
<!-- Prompt: chicken.md -->
<!-- Time: 111.04s -->
<!-- Fallback: False -->