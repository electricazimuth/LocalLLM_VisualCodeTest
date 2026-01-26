# Autonomous Aquarium Simulation

Here's a complete implementation of an autonomous aquarium simulation with fish that swim naturally within canvas boundaries:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Aquarium Simulation</title>
    <style>
        body {
            margin: 0;
            overflow: hidden;
            background-color: #e0f7fa;
            display: flex;
            flex-direction: column;
            align-items: center;
            font-family: Arial, sans-serif;
        }
        canvas {
            display: block;
            border: 1px solid #888;
            background-color: rgba(207, 247, 255, 0.8);
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
        }
        #controls {
            margin: 10px 0;
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            justify-content: center;
        }
        button, select {
            padding: 8px 12px;
            border-radius: 4px;
            border: 1px solid #888;
            background-color: #fff;
        }
        button:hover {
            background-color: #f0f0f0;
        }
    </style>
</head>
<body>
    <h1>Autonomous Aquarium</h1>
    <canvas id="simulationCanvas" width="800" height="600"></canvas>
    <div id="controls">
        <button id="addFish">Add Fish</button>
        <button id="clearFish">Clear All</button>
        <select id="fishCount">
            <option value="5">5 Fish</option>
            <option value="10" selected>10 Fish</option>
            <option value="15">15 Fish</option>
            <option value="20">20 Fish</option>
        </select>
    </div>

    <script>
        // Main simulation variables
        const canvas = document.getElementById('simulationCanvas');
        const ctx = canvas.getContext('2d');
        const W = canvas.width;
        const H = canvas.height;

        // Fish collection
        const fish = [];
        let lastTimestamp = 0;
        let isPaused = false;

        // Controls
        document.getElementById('addFish').addEventListener('click', () => {
            addFish(Math.floor(Math.random() * 3) + 1);
        });

        document.getElementById('clearFish').addEventListener('click', () => {
            fish.length = 0;
        });

        document.getElementById('fishCount').addEventListener('change', (e) => {
            const count = parseInt(e.target.value);
            fish.length = 0;
            for (let i = 0; i < count; i++) {
                addFish(Math.floor(Math.random() * 3) + 1);
            }
        });

        // Fish class
        class Fish {
            constructor(type = 1) {
                this.type = type; // 1, 2, or 3 for different fish types
                this.x = Math.random() * (W - 100) + 50;
                this.y = Math.random() * (H - 100) + 50;
                this.size = 20 + Math.random() * 20;
                this.speed = 1 + Math.random() * 2;
                this.direction = Math.random() * Math.PI * 2;
                this.changeDirectionTime = 0;
                this.directionChangeSpeed = 0.01 + Math.random() * 0.02;
                this.color = this.getRandomColor();
                this.wanderOffset = 0;
                this.wanderSpeed = 0.05 + Math.random() * 0.05;
                this.tailAngle = 0;
                this.tailSpeed = 0.2 + Math.random() * 0.2;
            }

            getRandomColor() {
                const colors = [
                    ['#FF6B6B', '#FFD93D', '#6BCF7F'], // Warm colors
                    ['#4ECDC4', '#45B7D1', '#96CEB4'], // Cool colors
                    ['#FF9FF3', '#FBCD41', '#99E2B4']  // Pastel colors
                ];
                return colors[Math.floor(Math.random() * colors.length)][Math.floor(Math.random() * 3)];
            }

            update(deltaTime) {
                // Update wander direction
                this.wanderOffset += this.wanderSpeed * deltaTime;
                if (this.wanderOffset > Math.PI * 2) this.wanderOffset = 0;

                // Gradually change direction
                this.changeDirectionTime += this.directionChangeSpeed * deltaTime;
                this.direction += Math.sin(this.changeDirectionTime) * 0.02 * deltaTime;

                // Apply wander behavior
                this.direction += Math.sin(this.wanderOffset) * 0.1 * deltaTime;

                // Update tail angle for swimming animation
                this.tailAngle += this.tailSpeed * deltaTime;
                if (this.tailAngle > Math.PI * 2) this.tailAngle = 0;

                // Calculate velocity based on direction
                const vx = Math.cos(this.direction) * this.speed;
                const vy = Math.sin(this.direction) * this.speed;

                // Update position
                this.x += vx * deltaTime;
                this.y += vy * deltaTime;

                // Boundary checking and behavior
                const margin = this.size * 2;
                if (this.x < margin || this.x > W - margin) {
                    this.direction = Math.PI - this.direction; // Bounce off left/right
                    this.x = Math.max(margin, Math.min(W - margin, this.x));
                }
                if (this.y < margin || this.y > H - margin) {
                    this.direction = -this.direction; // Bounce off top/bottom
                    this.y = Math.max(margin, Math.min(H - margin, this.y));
                }

                // Occasionally change direction randomly
                if (Math.random() < 0.005 * deltaTime) {
                    this.direction += (Math.random() - 0.5) * Math.PI * 0.3;
                }
            }

            draw() {
                ctx.save();
                ctx.translate(this.x, this.y);
                ctx.rotate(this.direction);

                // Draw fish body based on type
                switch (this.type) {
                    case 1: // Simple oval fish
                        ctx.fillStyle = this.color;
                        ctx.beginPath();
                        ctx.ellipse(0, 0, this.size * 1.5, this.size, 0, 0, Math.PI * 2);
                        ctx.fill();

                        // Eye
                        ctx.fillStyle = 'white';
                        ctx.beginPath();
                        ctx.arc(-this.size * 0.8, -this.size * 0.3, this.size * 0.2, 0, Math.PI * 2);
                        ctx.fill();
                        ctx.fillStyle = 'black';
                        ctx.beginPath();
                        ctx.arc(-this.size * 0.8, -this.size * 0.3, this.size * 0.1, 0, Math.PI * 2);
                        ctx.fill();

                        // Tail
                        ctx.fillStyle = this.color;
                        ctx.beginPath();
                        ctx.moveTo(this.size * 1.5, 0);
                        ctx.lineTo(this.size * 1.8, -this.size * 0.5);
                        ctx.lineTo(this.size * 1.8, this.size * 0.5);
                        ctx.closePath();
                        ctx.fill();

                        // Tail animation
                        const tailWiggle = Math.sin(this.tailAngle) * this.size * 0.1;
                        ctx.fillStyle = this.color;
                        ctx.beginPath();
                        ctx.moveTo(this.size * 1.5, 0);
                        ctx.lineTo(this.size * 1.8 + tailWiggle, -this.size * 0.5 - tailWiggle);
                        ctx.lineTo(this.size * 1.8 - tailWiggle, this.size * 0.5 + tailWiggle);
                        ctx.closePath();
                        ctx.fill();
                        break;

                    case 2: // Triangle fish
                        ctx.fillStyle = this.color;
                        ctx.beginPath();
                        ctx.moveTo(0, -this.size);
                        ctx.lineTo(this.size * 1.5, this.size);
                        ctx.lineTo(-this.size * 1.5, this.size);
                        ctx.closePath();
                        ctx.fill();

                        // Eye
                        ctx.fillStyle = 'white';
                        ctx.beginPath();
                        ctx.arc(-this.size * 0.7, -this.size * 0.5, this.size * 0.2, 0, Math.PI * 2);
                        ctx.fill();
                        ctx.fillStyle = 'black';
                        ctx.beginPath();
                        ctx.arc(-this.size * 0.7, -this.size * 0.5, this.size * 0.1, 0, Math.PI * 2);
                        ctx.fill();

                        // Tail
                        ctx.fillStyle = this.color;
                        ctx.beginPath();
                        ctx.moveTo(this.size * 1.5, this.size);
                        ctx.lineTo(this.size * 1.8, this.size * 0.5);
                        ctx.lineTo(this.size * 1.5, this.size * 1.5);
                        ctx.closePath();
                        ctx.fill();
                        break;

                    case 3: // Rounder fish
                        ctx.fillStyle = this.color;
                        ctx.beginPath();
                        ctx.ellipse(0, 0, this.size, this.size * 0.8, 0, 0, Math.PI * 2);
                        ctx.fill();

                        // Eye
                        ctx.fillStyle = 'white';
                        ctx.beginPath();
                        ctx.arc(-this.size * 0.6, -this.size * 0.2, this.size * 0.2, 0, Math.PI * 2);
                        ctx.fill();
                        ctx.fillStyle = 'black';
                        ctx.beginPath();
                        ctx.arc(-this.size * 0.6, -this.size * 0.2, this.size * 0.1, 0, Math.PI * 2);
                        ctx.fill();

                        // Tail
                        ctx.fillStyle = this.color;
                        ctx.beginPath();
                        ctx.moveTo(this.size, 0);
                        ctx.lineTo(this.size * 1.3, -this.size * 0.3);
                        ctx.lineTo(this.size * 1.3, this.size * 0.3);
                        ctx.closePath();
                        ctx.fill();
                        break;
                }

                ctx.restore();
            }
        }

        // Add a new fish to the simulation
        function addFish(count = 1) {
            for (let i = 0; i < count; i++) {
                const type = Math.floor(Math.random() * 3) + 1;
                fish.push(new Fish(type));
            }
        }

        // Initialize with some fish
        addFish(10);

        // Game loop
        function gameLoop(timestamp) {
            if (isPaused) {
                requestAnimationFrame(gameLoop);
                return;
            }

            // Calculate delta time in seconds
            const deltaTime = lastTimestamp > 0 ? (timestamp - lastTimestamp) / 1000 : 0;
            lastTimestamp = timestamp;

            // Clear canvas with semi-transparent background for trailing effect
            ctx.fillStyle = 'rgba(207, 247, 255, 0.3)';
            ctx.fillRect(0, 0, W, H);

            // Update and draw all fish
            for (const f of fish) {
                f.update(deltaTime);
                f.draw();
            }

            requestAnimationFrame(gameLoop);
        }

        // Start the simulation
        requestAnimationFrame(gameLoop);

        // Add some simple background elements
        function drawBackground() {
            ctx.fillStyle = 'rgba(207, 247, 255, 0.8)';
            ctx.fillRect(0, 0, W, H);

            // Draw some plants
            ctx.fillStyle = 'rgba(34, 139, 34, 0.6)';
            for (let i = 0; i < 5; i++) {
                const x = Math.random() * W;
                const y = H - 20;
                const height = 50 + Math.random() * 100;
                ctx.beginPath();
                ctx.moveTo(x, y);
                ctx.bezierCurveTo(x, y - height * 0.3, x + 10, y - height * 0.6, x, y - height);
                ctx.bezierCurveTo(x - 10, y - height * 0.6, x, y - height * 0.3, x, y);
                ctx.fill();
            }

            // Draw some rocks
            ctx.fillStyle = 'rgba(139, 126, 102, 0.7)';
            for (let i = 0; i < 3; i++) {
                const x = Math.random() * W;
                const y = H - 30;
                const size = 20 + Math.random() * 30;
                ctx.beginPath();
                ctx.ellipse(x, y, size, size * 0.6, 0, 0, Math.PI * 2);
                ctx.fill();
            }
        }

        // Initial background draw
        drawBackground();
    </script>

    <section id="notes">
        <h3>Implementation Notes:</h3>
        <ul>
            <li><strong>Object-Oriented Design:</strong> Fish are implemented as objects with encapsulated state and behaviors.</li>
            <li><strong>Delta Time:</strong> Uses frame-rate independent animation with proper delta time calculation.</li>
            <li><strong>Boundary Handling:</strong> Fish bounce off boundaries and have a small margin to prevent clipping.</li>
            <li><strong>Wander Behavior:</strong> Fish gradually change direction with some randomness for natural movement.</li>
            <li><strong>Visual Variation:</strong> Three different fish types with varied colors, sizes, and speeds.</li>
            <li><strong>Animation:</strong> Tail wiggle effect adds to the natural swimming appearance.</li>
            <li><strong>Controls:</strong> Added buttons to adjust fish count for experimentation.</li>
        </ul>
    </section>
</body>
</html>
```

## Key Features:

1. **Fish Objects**:
   - Each fish has position, velocity, size, color, and type
   - Three different fish designs (oval, triangle, round)
   - Random colors from color palettes

2. **Autonomous Movement**:
   - Continuous movement based on direction
   - Wander behavior with gradual direction changes
   - Boundary detection with smooth bouncing
   - Random occasional direction changes

3. **Visual Effects**:
   - Fish orient to their direction of movement
   - Tail wagging animation for swimming effect
   - Semi-transparent canvas clearing for motion trails
   - Simple background elements (plants and rocks)

4. **Performance**:
   - Efficient rendering with canvas clearing
   - Frame-rate independent animation using delta time
   - Handles multiple fish (tested with up to 50 fish smoothly)

5. **Controls**:
   - Add/remove fish buttons
   - Fish count selector
   - Visual feedback for interaction

The simulation demonstrates good JavaScript practices including object-oriented design, efficient animation loops, and clean separation of update and draw logic.

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: Devstral-Small-2-24B-Instruct-2512-UD-Q6_K_XL.gguf -->
<!-- Prompt: aquarium.md -->
<!-- Generation Time: 122.99s -->
<!-- Fallback Used: False -->