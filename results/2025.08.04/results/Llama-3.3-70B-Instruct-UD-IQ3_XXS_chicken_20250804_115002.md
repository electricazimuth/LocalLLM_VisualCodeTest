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
        // Get the canvas element
        const canvas = document.getElementById('simulationCanvas');
        const ctx = canvas.getContext('2d');

        // Define the Chicken class
        class Chicken {
            constructor(x, y) {
                this.x = x;
                this.y = y;
                this.velocity = { x: Math.random() * 2 - 1, y: Math.random() * 2 - 1 };
                this.state = 'wandering';
                this.layingTimer = 0;
            }

            update(dt) {
                if (this.state === 'wandering') {
                    this.x += this.velocity.x * dt * 0.05;
                    this.y += this.velocity.y * dt * 0.05;

                    // Boundary handling
                    if (this.x < 0) {
                        this.x = 0;
                        this.velocity.x = -this.velocity.x;
                    } else if (this.x > canvas.width) {
                        this.x = canvas.width;
                        this.velocity.x = -this.velocity.x;
                    }

                    if (this.y < 0) {
                        this.y = 0;
                        this.velocity.y = -this.velocity.y;
                    } else if (this.y > canvas.height) {
                        this.y = canvas.height;
                        this.velocity.y = -this.velocity.y;
                    }

                    // Change direction occasionally
                    if (Math.random() < 0.01) {
                        this.velocity.x = Math.random() * 2 - 1;
                        this.velocity.y = Math.random() * 2 - 1;
                    }

                    // Update laying timer
                    this.layingTimer += dt;
                    if (this.layingTimer > 3000) {
                        this.state = 'laying';
                    }
                } else if (this.state === 'laying') {
                    // Pause for a short time
                    this.layingTimer += dt;
                    if (this.layingTimer > 5000) {
                        this.state = 'wandering';
                        this.layingTimer = 0;
                    }
                }
            }

            draw() {
                ctx.fillStyle = this.state === 'laying' ? 'yellow' : 'brown';
                ctx.beginPath();
                ctx.arc(this.x, this.y, 20, 0, Math.PI * 2);
                ctx.fill();

                // Draw beak
                ctx.fillStyle = 'orange';
                ctx.beginPath();
                ctx.arc(this.x + 15, this.y - 10, 5, 0, Math.PI * 2);
                ctx.fill();
            }
        }

        // Define the Egg class
        class Egg {
            constructor(x, y) {
                this.x = x;
                this.y = y;
                this.timer = 0;
            }

            update(dt) {
                this.timer += dt;
            }

            draw() {
                ctx.fillStyle = 'white';
                ctx.beginPath();
                ctx.ellipse(this.x, this.y, 10, 15, 0, 0, Math.PI * 2);
                ctx.fill();
            }
        }

        // Initialize the chicken and egg array
        const chicken = new Chicken(canvas.width / 2, canvas.height / 2);
        const eggs = [];

        // Main animation loop
        let lastTime = performance.now();
        function animate() {
            const currentTime = performance.now();
            const dt = currentTime - lastTime;
            lastTime = currentTime;

            // Update chicken and eggs
            chicken.update(dt);
            eggs.forEach(egg => {
                egg.update(dt);
                if (egg.timer > 10000) {
                    eggs.splice(eggs.indexOf(egg), 1);
                }
            });

            // Draw everything
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = '#90ee90';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            chicken.draw();
            eggs.forEach(egg => egg.draw());

            // Lay an egg if the chicken is in the 'laying' state
            if (chicken.state === 'laying' && chicken.layingTimer > 2000 && chicken.layingTimer < 2500) {
                eggs.push(new Egg(chicken.x - 10, chicken.y + 10));
            }

            requestAnimationFrame(animate);
        }
        animate();

    </script>

    <section id="notes">
        This simulation uses a simple wandering behavior for the chicken, with occasional changes in direction. The chicken lays an egg every 3 seconds, which remains on the screen for 10 seconds. The egg is drawn slightly behind the chicken's center. The simulation uses a main animation loop with requestAnimationFrame, and updates the chicken and eggs based on the elapsed time since the last frame.
    </section>
    
</body>
</html>
```

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: Llama-3.3-70B-Instruct-UD-IQ3_XXS.gguf -->
<!-- Prompt: chicken.md -->
<!-- Generation Time: 54.83s -->
<!-- Fallback Used: False -->