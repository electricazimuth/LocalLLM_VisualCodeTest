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
        // Constants for chicken and egg appearance
        const CHICKEN_SIZE = 20;
        const EGG_SIZE = 10;

        // Helper function to draw the chicken
        function drawChicken(ctx, x, y, direction) {
            ctx.save();
            ctx.translate(x, y);
            ctx.rotate(direction);
            ctx.beginPath();
            ctx.arc(0, 0, CHICKEN_SIZE, 0, Math.PI * 2);
            ctx.fillStyle = 'orange';
            ctx.fill();
            // Drawing beak
            ctx.fillStyle = 'yellow';
            ctx.beginPath();
            ctx.moveTo(CHICKEN_SIZE / 2, 0);
            ctx.lineTo(CHICKEN_SIZE / 2 + 5, -5);
            ctx.lineTo(CHICKEN_SIZE / 2 + 5, 5);
            ctx.closePath();
            ctx.fill();
            ctx.restore();
        }

        // Helper function to draw the egg
        function drawEgg(ctx, x, y) {
            ctx.beginPath();
            ctx.ellipse(x, y, EGG_SIZE, EGG_SIZE / 2, 0, 0, 2 * Math.PI);
            ctx.fillStyle = 'white';
            ctx.fill();
        }

        // Chicken class definition
        class Chicken {
            constructor() {
                this.x = 256; // Start in the middle of the canvas
                this.y = 256;
                this.direction = 0; // Facing right
                this.speed = 2; // Movement speed
                this.lastLay = 0; // Time when the chicken last laid an egg
                this.layInterval = 2000; // Interval for laying an egg (ms)
                this.state = 'wandering'; // State of the chicken
            }

            // Update the chicken's position and state
            update(deltaTime, eggs) {
                // Update laying egg timer and state
                if (this.state === 'laying') {
                    if (Date.now() - this.lastLay >= this.layInterval) {
                        // Lay an egg and switch back to wandering
                        eggs.push({ x: this.x, y: this.y - 10 });
                        this.state = 'wandering';
                    }
                } else {
                    // Update position based on speed and direction
                    this.x += this.speed * Math.cos(this.direction) * deltaTime;
                    this.y += this.speed * Math.sin(this.direction) * deltaTime;

                    // Boundary handling
                    if (this.x < CHICKEN_SIZE) this.x = CHICKEN_SIZE;
                    else if (this.x > 512 - CHICKEN_SIZE) this.x = 512 - CHICKEN_SIZE;
                    if (this.y < CHICKEN_SIZE) this.y = CHICKEN_SIZE;
                    else if (this.y > 512 - CHICKEN_SIZE) this.y = 512 - CHICKEN_SIZE;

                    // Occasionally change direction
                    if (Math.random() < 0.01) this.direction += (Math.random() - 0.5) * Math.PI / 8;

                    // Check if it's time to lay an egg
                    if (Date.now() - this.lastLay >= this.layInterval) {
                        this.state = 'laying';
                        this.lastLay = Date.now();
                    }
                }
            }
        }

        // Egg class definition
        class Egg {
            constructor(x, y) {
                this.x = x;
                this.y = y;
            }
        }

        // Simulation setup
        const canvas = document.getElementById('simulationCanvas');
        const ctx = canvas.getContext('2d');
        const chicken = new Chicken();
        const eggs = [];

        // Main animation loop
        let lastTime = 0;
        function animate(time) {
            if (lastTime !== 0) {
                const deltaTime = (time - lastTime) / 1000; // Convert to seconds
                chicken.update(deltaTime, eggs);
            }
            lastTime = time;

            // Clear canvas
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = '#90ee90'; // Light green grass background
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            // Draw chicken
            drawChicken(ctx, chicken.x, chicken.y, chicken.direction);

            // Draw eggs
            eggs.forEach(egg => drawEgg(ctx, egg.x, egg.y));

            // Request next animation frame
            requestAnimationFrame(animate);
        }

        // Start animation
        requestAnimationFrame(animate);
    </script>

    <!-- Optional section for notes -->
    <section id="notes">
        Developer notes regarding the simulation logic, AI choices, etc.
        - The chicken moves at a constant speed and changes direction occasionally to create a wandering effect.
        - The chicken lays an egg every 2 seconds, pausing its movement briefly to do so.
        - Boundary handling ensures the chicken stays within the canvas.
        - The simulation uses requestAnimationFrame for smooth animation, calculating deltaTime for frame-rate independent movement.
    </section>
</body>
</html>
```

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: granite-4.0-h-small-UD-Q5_K_XL.gguf -->
<!-- Prompt: chicken.md -->
<!-- Generation Time: 21.26s -->
<!-- Fallback Used: False -->