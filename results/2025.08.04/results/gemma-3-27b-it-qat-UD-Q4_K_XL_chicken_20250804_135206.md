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
        const canvas = document.getElementById('simulationCanvas');
        const ctx = canvas.getContext('2d');

        const canvasWidth = canvas.width;
        const canvasHeight = canvas.height;

        // Chicken Class
        class Chicken {
            constructor() {
                this.x = canvasWidth / 2;
                this.y = canvasHeight / 2;
                this.speed = 2;
                this.direction = Math.random() * 2 * Math.PI; // Random initial direction
                this.layingTimer = 0;
                this.layingDuration = 100; // Frames to spend laying
                this.laying = false;
                this.eggOffset = 10; // Offset for egg laying position
            }

            update(deltaTime) {
                if (this.laying) {
                    this.layingTimer -= deltaTime;
                    if (this.layingTimer <= 0) {
                        this.laying = false;
                    }
                } else {
                    this.x += Math.cos(this.direction) * this.speed;
                    this.y += Math.sin(this.direction) * this.speed;

                    // Boundary handling
                    if (this.x < 0) {
                        this.x = 0;
                        this.direction = Math.PI - this.direction;
                    } else if (this.x > canvasWidth) {
                        this.x = canvasWidth;
                        this.direction = Math.PI - this.direction;
                    }

                    if (this.y < 0) {
                        this.y = 0;
                        this.direction = -this.direction;
                    } else if (this.y > canvasHeight) {
                        this.y = canvasHeight;
                        this.direction = -this.direction;
                    }

                    // Egg laying trigger (probability check)
                    if (Math.random() < 0.005) { // 0.5% chance per frame
                        this.layEgg();
                    }
                }
            }

            draw() {
                ctx.save();
                ctx.translate(this.x, this.y);
                ctx.rotate(this.direction);

                ctx.fillStyle = this.laying ? 'yellow' : 'orange';
                ctx.beginPath();
                ctx.ellipse(0, 0, 20, 15, 0, 0, 2 * Math.PI);
                ctx.fill();

                // Beak
                ctx.fillStyle = 'black';
                ctx.beginPath();
                ctx.moveTo(20, 0);
                ctx.lineTo(30, 5);
                ctx.lineTo(30, -5);
                ctx.closePath();
                ctx.fill();

                ctx.restore();
            }

            layEgg() {
                this.laying = true;
                this.layingTimer = this.layingDuration;
                eggs.push(new Egg(this.x - Math.cos(this.direction) * this.eggOffset, this.y - Math.sin(this.direction) * this.eggOffset));
            }
        }

        // Egg Class
        class Egg {
            constructor(x, y) {
                this.x = x;
                this.y = y;
                this.size = 10;
                this.life = 100; // Frames to live
            }

            update(deltaTime) {
                this.life -= deltaTime;
            }

            draw() {
                ctx.fillStyle = 'brown';
                ctx.beginPath();
                ctx.ellipse(this.x, this.y, this.size, this.size / 2, 0, 0, 2 * Math.PI);
                ctx.fill();
            }
        }

        const chicken = new Chicken();
        const eggs = [];

        let lastTime = 0;

        function gameLoop(timestamp) {
            const deltaTime = (timestamp - lastTime) / 1000; // Seconds since last frame
            lastTime = timestamp;

            ctx.clearRect(0, 0, canvasWidth, canvasHeight);

            // Update
            chicken.update(deltaTime);
            for (let i = 0; i < eggs.length; i++) {
                eggs[i].update(deltaTime);
            }

            // Draw
            chicken.draw();
            for (let i = 0; i < eggs.length; i++) {
                eggs[i].draw();
            }

            // Remove dead eggs
            eggs = eggs.filter(egg => egg.life > 0);

            requestAnimationFrame(gameLoop);
        }

        requestAnimationFrame(gameLoop);
    </script>

    <!-- Optional section for notes -->
    
    <section id="notes">
        Developer notes regarding the simulation logic, AI choices, etc.
        <ul>
            <li><b>Object Management:</b> Chicken is a single object. Eggs are managed in an array.</li>
            <li><b>Chicken AI:</b>  Wandering behavior using random direction changes.</li>
            <li><b>Egg Laying:</b> Triggered by a probability check per frame.</li>
            <li><b>Delta Time:</b> Used for frame-rate independent movement and timing.</li>
            <li><b>Boundary Handling:</b> Chicken bounces off canvas edges.</li>
            <li><b>Egg Position:</b> Eggs are laid slightly behind the chicken's center.</li>
            <li><b>Egg Lifespan:</b> Eggs disappear after a certain number of frames.</li>
            <li><b>Classes:</b> Utilized classes for Chicken and Egg objects to encapsulate their properties and methods.</li>
        </ul>
    </section>
    
</body>
</html>
```

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: gemma-3-27b-it-qat-UD-Q4_K_XL.gguf -->
<!-- Prompt: chicken.md -->
<!-- Generation Time: 41.63s -->
<!-- Fallback Used: False -->