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
        const canvasWidth = canvas.width;
        const canvasHeight = canvas.height;

        // Chicken Class
        class Chicken {
            constructor(x, y) {
                this.x = x;
                this.y = y;
                this.speed = 2;
                this.direction = Math.random() * 2 * Math.PI; // Random initial direction
                this.wanderInterval = 50; // Time in frames to change direction
                this.wanderTimer = 0;
                this.layingInterval = 150; // Time in frames to lay an egg
                this.layingTimer = 0;
                this.laying = false;
                this.radius = 20;
                this.color = 'brown';
            }

            update(deltaTime) {
                if (this.laying) {
                    this.layingTimer += deltaTime;
                    if (this.layingTimer >= 15) { // 15 frames for laying animation
                        this.laying = false;
                        this.layingTimer = 0;
                    }
                } else {
                    this.wanderTimer += deltaTime;
                    if (this.wanderTimer >= this.wanderInterval) {
                        this.direction = Math.random() * 2 * Math.PI;
                        this.wanderTimer = 0;
                    }

                    this.x += Math.cos(this.direction) * this.speed * deltaTime;
                    this.y += Math.sin(this.direction) * this.speed * deltaTime;

                    // Boundary collision detection and response
                    if (this.x - this.radius < 0) {
                        this.x = this.radius;
                        this.direction = Math.PI - this.direction;
                    } else if (this.x + this.radius > canvasWidth) {
                        this.x = canvasWidth - this.radius;
                        this.direction = Math.PI - this.direction;
                    }

                    if (this.y - this.radius < 0) {
                        this.y = this.radius;
                        this.direction = 2 * Math.PI - this.direction;
                    } else if (this.y + this.radius > canvasHeight) {
                        this.y = canvasHeight - this.radius;
                        this.direction = 2 * Math.PI - this.direction;
                    }

                    this.layingTimer += deltaTime;
                    if (this.layingTimer >= this.layingInterval) {
                        this.laying = true;
                        this.layingTimer = 0;
                    }
                }
            }

            draw() {
                ctx.save();
                ctx.translate(this.x, this.y);
                ctx.rotate(this.direction);

                if (this.laying) {
                    ctx.fillStyle = 'red'; // Indicate laying state
                } else {
                    ctx.fillStyle = this.color;
                }
                ctx.beginPath();
                ctx.arc(0, 0, this.radius, 0, 2 * Math.PI);
                ctx.fill();

                // Beak
                ctx.fillStyle = 'orange';
                ctx.beginPath();
                ctx.moveTo(this.radius, 0);
                ctx.lineTo(this.radius + 5, -5);
                ctx.lineTo(this.radius + 5, 5);
                ctx.closePath();
                ctx.fill();

                ctx.restore();
            }
        }

        // Egg Class
        class Egg {
            constructor(x, y) {
                this.x = x;
                this.y = y;
                this.radius = 10;
                this.color = 'white';
                this.fadeTime = 60; // Frames to fade out
                this.fadeTimer = 0;
                this.alpha = 1;
            }

            update(deltaTime) {
                this.fadeTimer += deltaTime;
                this.alpha = Math.max(0, 1 - this.fadeTimer / this.fadeTime);
            }

            draw() {
                ctx.fillStyle = `${this.color} (${this.alpha})`;
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.radius, 0, 2 * Math.PI);
                ctx.fill();
            }
        }

        let chicken = new Chicken(canvasWidth / 2, canvasHeight / 2);
        let eggs = [];

        let lastTime = 0;

        function animate(currentTime) {
            const deltaTime = (currentTime - lastTime) / 1000;
            lastTime = currentTime;

            ctx.clearRect(0, 0, canvasWidth, canvasHeight);

            chicken.update(deltaTime);
            chicken.draw();

            for (let i = eggs.length - 1; i >= 0; i--) {
                eggs[i].update(deltaTime);
                eggs[i].draw();
            }

            if (chicken.laying) {
                // Create egg slightly behind the chicken
                let eggX = chicken.x + Math.cos(chicken.direction) * (chicken.radius + 5);
                let eggY = chicken.y + Math.sin(chicken.direction) * (chicken.radius + 5);
                eggs.push(new Egg(eggX, eggY));
            }

            requestAnimationFrame(animate);
        }

        requestAnimationFrame(animate);
    </script>

    <!-- Optional section for notes -->
    <section id="notes">
        This simulation features a wandering Chicken object that periodically lays Eggs.  The Chicken's movement is governed by a simple AI that includes boundary collision detection and a random direction change timer.  Eggs are created at the chicken's location when the laying timer expires and fade out over time.  Delta time is used to ensure frame-rate independent movement and animation.  Classes for Chicken and Egg objects are used for better organization and code reusability.
    </section>
</body>
</html>
```

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: gemma-3-12b-it-qat-UD-Q4_K_XL.gguf -->
<!-- Prompt: chicken.md -->
<!-- Generation Time: 23.35s -->
<!-- Fallback Used: False -->