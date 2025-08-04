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
                this.direction = Math.random() * 2 * Math.PI; // Random direction in radians
                this.layingTimer = 0;
                this.layingDuration = 50; // Frames to spend laying
                this.layingCooldown = 100; // Frames before being able to lay again
                this.layingTimerMax = this.layingCooldown;
                this.state = 'wandering';
            }

            update(deltaTime) {
                if (this.state === 'wandering') {
                    this.x += Math.cos(this.direction) * this.speed * deltaTime;
                    this.y += Math.sin(this.direction) * this.speed * deltaTime;

                    // Boundary Handling
                    if (this.x < 0 || this.x > canvasWidth) {
                        this.direction = Math.PI - this.direction;
                        this.x = Math.max(0, Math.min(this.x, canvasWidth)); // Keep within bounds
                    }
                    if (this.y < 0 || this.y > canvasHeight) {
                        this.direction = -this.direction;
                        this.y = Math.max(0, Math.min(this.y, canvasHeight)); // Keep within bounds
                    }

                    // Laying logic
                    this.layingTimer++;
                    if (this.layingTimer >= this.layingTimerMax) {
                        this.state = 'laying';
                        this.layingTimer = 0;
                    }
                } else if (this.state === 'laying') {
                    this.layingTimer++;
                    if (this.layingTimer >= this.layingDuration) {
                        this.state = 'wandering';
                    }
                }
            }

            draw(ctx) {
                ctx.save();
                ctx.translate(this.x, this.y);
                ctx.rotate(this.direction);

                // Chicken body
                ctx.fillStyle = 'yellow';
                ctx.beginPath();
                ctx.ellipse(0, 0, 20, 15, 0, 0, 2 * Math.PI);
                ctx.fill();

                // Beak
                ctx.fillStyle = 'orange';
                ctx.beginPath();
                ctx.moveTo(20, 0);
                ctx.lineTo(30, 5);
                ctx.lineTo(30, -5);
                ctx.closePath();
                ctx.fill();

                // Eye
                ctx.fillStyle = 'black';
                ctx.beginPath();
                ctx.arc(-5, -5, 2, 0, 2 * Math.PI);
                ctx.fill();

                ctx.restore();
            }
        }

        // Egg Class
        class Egg {
            constructor(x, y) {
                this.x = x;
                this.y = y;
                this.lifespan = 60; // Frames before disappearing
                this.timer = 0;
            }

            update(deltaTime) {
                this.timer++;
            }

            draw(ctx) {
                ctx.fillStyle = 'white';
                ctx.beginPath();
                ctx.ellipse(this.x, this.y, 10, 7, 0, 0, 2 * Math.PI);
                ctx.fill();
            }

            isExpired() {
                return this.timer >= this.lifespan;
            }
        }


        let chicken = new Chicken();
        let eggs = [];

        let lastTime = 0;

        function gameLoop(timestamp) {
            const deltaTime = (timestamp - lastTime) / 1000; // Convert to seconds
            lastTime = timestamp;

            // Update
            chicken.update(deltaTime);

            if (chicken.state === 'laying') {
                eggs.push(new Egg(chicken.x, chicken.y));
            }

            for (let i = 0; i < eggs.length; i++) {
                eggs[i].update(deltaTime);
            }

            // Remove expired eggs
            eggs = eggs.filter(egg => !egg.isExpired());


            // Draw
            ctx.clearRect(0, 0, canvasWidth, canvasHeight);
            ctx.fillStyle = '#90ee90'; // Light Green
            ctx.fillRect(0, 0, canvasWidth, canvasHeight);

            chicken.draw(ctx);

            for (const egg of eggs) {
                egg.draw(ctx);
            }

            requestAnimationFrame(gameLoop);
        }

        requestAnimationFrame(gameLoop);

    </script>

    <!-- Optional section for notes -->
    <section id="notes">
        Developer notes regarding the simulation logic, AI choices, etc.
        <br>
        - Used classes for Chicken and Egg to encapsulate data and behavior.
        - Implemented wandering behavior with boundary handling.
        - Added a laying state with a timer and cooldown.
        - Used requestAnimationFrame and deltaTime for smooth animation.
        - Eggs have a lifespan and are removed when expired.
    </section>

</body>
</html>
```

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: google_gemma-3-27b-it-Q8_0.gguf -->
<!-- Prompt: chicken.md -->
<!-- Generation Time: 59.93s -->
<!-- Fallback Used: False -->