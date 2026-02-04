```html
<!DOCTYPE html>
<html>
<head>
    <title>Aquarium Simulation</title>
    <style>
        body { margin: 0; overflow: hidden; background-color: #e0f7fa; } /* Light blue background */
        canvas { display: block; margin: 20px auto; border: 1px solid #888; background-color: rgb(207, 247, 255); } /* blue water */
        #notes {
            font-family: Arial, sans-serif;
            margin: 20px;
            padding: 15px;
            background-color: #f5f5f5;
            border: 1px solid #ddd;
            border-radius: 8px;
            color: #333;
        }
    </style>
</head>
<body>
    <canvas id="simulationCanvas" width="800" height="600"></canvas>

    <script>
        // --- SETUP ---
        const canvas = document.getElementById('simulationCanvas');
        const ctx = canvas.getContext('2d');
        const W = canvas.width;
        const H = canvas.height;

        // --- FISH CLASS ---
        class Fish {
            constructor(x, y, speed, color, size) {
                this.x = x;
                this.y = y;
                this.speed = speed || 1.5;
                this.color = color || getRandomColor();
                this.size = size || 20;
                this.angle = Math.random() * Math.PI * 2;
                this.velocityX = Math.cos(this.angle) * this.speed;
                this.velocityY = Math.sin(this.angle) * this.speed;
                this.wobbleAngle = 0;
                this.wobbleSpeed = 0.1;
                this.wobbleAmplitude = 0.1;
                this.boundaryAvoidance = 0.05; // Smoother turning near edges
                this.turningFactor = 0.02; // How much direction changes per frame
            }

            // Update position and direction
            update(dt) {
                // Gradual random wandering
                this.angle += (Math.random() - 0.5) * this.turningFactor * dt;

                // Update velocity based on new angle
                this.velocityX = Math.cos(this.angle) * this.speed;
                this.velocityY = Math.sin(this.angle) * this.speed;

                // Update position
                this.x += this.velocityX * dt;
                this.y += this.velocityY * dt;

                // Boundary detection and smooth avoidance
                const margin = this.size / 2;
                if (this.x < margin) {
                    // Left boundary: turn right
                    this.angle += this.boundaryAvoidance * dt;
                    this.x = margin;
                } else if (this.x > W - margin) {
                    // Right boundary: turn left
                    this.angle -= this.boundaryAvoidance * dt;
                    this.x = W - margin;
                }

                if (this.y < margin) {
                    // Top boundary: turn down
                    this.angle += this.boundaryAvoidance * dt;
                    this.y = margin;
                } else if (this.y > H - margin) {
                    // Bottom boundary: turn up
                    this.angle -= this.boundaryAvoidance * dt;
                    this.y = H - margin;
                }

                // Update wobble for tail animation
                this.wobbleAngle += this.wobbleSpeed;
            }

            // Draw fish with orientation
            draw(ctx) {
                ctx.save();
                ctx.translate(this.x, this.y);
                ctx.rotate(this.angle);

                // Draw fish body (oval)
                ctx.beginPath();
                ctx.ellipse(0, 0, this.size * 0.7, this.size * 0.4, 0, 0, Math.PI * 2);
                ctx.fillStyle = this.color;
                ctx.fill();

                // Draw tail (triangle)
                const tailWidth = this.size * 0.3;
                const tailLength = this.size * 0.6;
                ctx.beginPath();
                ctx.moveTo(0, 0);
                ctx.lineTo(tailWidth, tailLength);
                ctx.lineTo(-tailWidth, tailLength);
                ctx.closePath();

                // Add slight wobble to tail
                const wobbleX = Math.sin(this.wobbleAngle) * this.wobbleAmplitude * this.size;
                ctx.translate(wobbleX, 0);
                ctx.fillStyle = this.color;
                ctx.fill();

                // Draw eye
                const eyeSize = this.size * 0.1;
                ctx.beginPath();
                ctx.ellipse(-this.size * 0.3, -this.size * 0.1, eyeSize, eyeSize, 0, 0, Math.PI * 2);
                ctx.fillStyle = '#000';
                ctx.fill();

                ctx.restore();
            }
        }

        // Helper function to generate random color
        function getRandomColor() {
            const hue = Math.random() * 120; // Limit to blue-green range for aquatic feel
            const saturation = 70 + Math.random() * 30;
            const lightness = 60 + Math.random() * 20;
            return `hsl(${hue}, ${saturation}%, ${lightness}%)`;
        }

        // --- SIMULATION ---
        const fishCount = 15;
        const fishArray = [];

        // Initialize fish
        for (let i = 0; i < fishCount; i++) {
            const x = Math.random() * (W - 50) + 25;
            const y = Math.random() * (H - 50) + 25;
            const speed = 1.0 + Math.random() * 2.0;
            const size = 15 + Math.random() * 25;
            fishArray.push(new Fish(x, y, speed, getRandomColor(), size));
        }

        // --- GAME LOOP ---
        let lastTime = 0;

        function gameLoop(timestamp) {
            // Calculate delta time
            const dt = timestamp - lastTime;
            lastTime = timestamp;

            // Clear canvas
            ctx.clearRect(0, 0, W, H);

            // Update and draw all fish
            fishArray.forEach(fish => {
                fish.update(dt);
                fish.draw(ctx);
            });

            // Request next frame
            requestAnimationFrame(gameLoop);
        }

        // Start animation loop
        requestAnimationFrame(gameLoop);

        // --- OPTIONAL: Add simple background elements ---
        function drawBackground() {
            // Draw simple plants (optional)
            const plantCount = 5;
            const plantSize = 10;
            for (let i = 0; i < plantCount; i++) {
                const x = Math.random() * W;
                const y = H - 50 - Math.random() * 50;
                ctx.save();
                ctx.translate(x, y);
                ctx.fillStyle = 'rgba(0, 100, 0, 0.5)';
                ctx.beginPath();
                ctx.ellipse(0, 0, plantSize * 0.5, plantSize * 1.5, 0, 0, Math.PI * 2);
                ctx.fill();
                ctx.restore();
            }
        }

        // Uncomment to enable background plants
        // drawBackground();

    </script>

    <!-- Developer Notes -->
    <section id="notes">
        <h3>Implementation Notes</h3>
        <p><strong>Object-Oriented Design:</strong> Fish are encapsulated in a class with state and behavior. Each fish manages its own position, velocity, angle, and animation.</p>
        <p><strong>Frame-Rate Independent Animation:</strong> Uses delta time (dt) to ensure consistent movement regardless of frame rate.</p>
        <p><strong>Smooth Boundary Interaction:</strong> Fish gently turn away from boundaries instead of bouncing, creating natural movement.</p>
        <p><strong>Wandering Behavior:</strong> Fish gradually change direction with small random perturbations to avoid straight-line paths.</p>
        <p><strong>Visuals:</strong> Fish are drawn as oriented ellipses with triangular tails that wiggle. Colors are randomized in blue-green spectrum.</p>
        <p><strong>Efficiency:</strong> Uses simple array for fish management and efficient canvas operations. No external libraries.</p>
        <p><strong>Optional Features:</strong> Background plants can be added (currently commented out) for enhanced visual appeal.</p>
    </section>
</body>
</html>
```

---

### ✅ Key Features Implemented:

- **Object-Oriented Design:** `Fish` class with encapsulated state and behavior.
- **Delta Time:** Animation is frame-rate independent using `dt`.
- **Smooth Boundary Handling:** Fish turn gradually when near edges.
- **Natural Movement:** Random wandering via small directional perturbations.
- **Visuals:** Oriented fish with wiggling tails and realistic colors.
- **Efficiency:** Array-based management, minimal DOM interaction.
- **Background:** Light blue water with optional plants (commented out for simplicity).

### 🎯 Why This Works Well:

- Uses `requestAnimationFrame` for smooth, browser-optimized animation.
- Fish are initialized with random positions, colors, sizes, and speeds for variety.
- Tail wobble adds a subtle biological feel.
- The boundary avoidance is gentle, preventing "jittery" or "unrealistic" bouncing.

This simulation is ready to run in any modern browser — no external libraries required!

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: Qwen3-VL-32B-Instruct-UD-Q6_K_XL.gguf -->
<!-- Prompt: aquarium.md -->
<!-- Time: 100.94s -->
<!-- Fallback: False -->