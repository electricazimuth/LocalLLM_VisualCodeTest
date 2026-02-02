Here's a complete implementation of the Autonomous Aquarium Simulation that meets all requirements and includes desirable features:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Aquarium Simulation</title>
    <style>
        body { margin: 0; overflow: hidden; background-color: #e0f7fa; }
        canvas { display: block; margin: 20px auto; border: 1px solid #888; background-color: rgb(207, 247, 255); }
    </style>
</head>
<body>
    <canvas id="simulationCanvas" width="800" height="600"></canvas>

    <script>
        const canvas = document.getElementById('simulationCanvas');
        const ctx = canvas.getContext('2d');
        const W = canvas.width;
        const H = canvas.height;

        class Fish {
            constructor() {
                this.x = Math.random() * W;
                this.y = Math.random() * H;
                this.size = Math.random() * 10 + 10;
                this.hue = Math.random() * 360;
                this.speed = Math.random() * 100 + 50;
                this.direction = Math.random() * Math.PI * 2;
                this.wigglePhase = 0;
            }

            update(delta) {
                // Wandering behavior
                this.direction += (Math.random() - 0.5) * 0.2;

                // Boundary correction
                const buffer = this.size * 2;
                let desiredDir = this.direction;

                if (this.x < buffer || this.x > W - buffer || 
                    this.y < buffer || this.y > H - buffer) {
                    const dx = W/2 - this.x;
                    const dy = H/2 - this.y;
                    desiredDir = Math.atan2(dy, dx);
                    this.direction += (desiredDir - this.direction) * 0.05;
                }

                // Update position
                this.x += this.speed * Math.cos(this.direction) * delta;
                this.y += this.speed * Math.sin(this.direction) * delta;

                // Tail wiggle animation
                this.wigglePhase += this.speed * delta * 0.1;
            }

            draw() {
                ctx.save();
                ctx.translate(this.x, this.y);
                ctx.rotate(this.direction);

                // Body
                ctx.beginPath();
                ctx.fillStyle = `hsl(${this.hue}, 70%, 50%)`;
                ctx.ellipse(0, 0, this.size*1.2, this.size, 0, 0, Math.PI*2);
                ctx.fill();

                // Tail with wiggle
                const wiggle = Math.sin(this.wigglePhase) * 0.3;
                ctx.beginPath();
                ctx.fillStyle = `hsl(${this.hue}, 80%, 40%)`;
                ctx.moveTo(-this.size*1.5, 0);
                ctx.lineTo(-this.size*0.8, -this.size*0.5 + wiggle);
                ctx.lineTo(-this.size*0.8, this.size*0.5 - wiggle);
                ctx.closePath();
                ctx.fill();

                ctx.restore();
            }
        }

        const fishArray = [];
        const NUM_FISH = 12;
        let lastTime = 0;

        function init() {
            for (let i = 0; i < NUM_FISH; i++) {
                fishArray.push(new Fish());
            }
        }

        function gameLoop(timestamp) {
            const delta = (timestamp - lastTime) / 1000;
            lastTime = timestamp;

            ctx.clearRect(0, 0, W, H);
            fishArray.forEach(fish => {
                fish.update(delta);
                fish.draw();
            });

            requestAnimationFrame(gameLoop);
        }

        init();
        requestAnimationFrame(gameLoop);
    </script>

    <section id="notes">
        <h3>Implementation Details:</h3>
        <ul>
            <li><strong>OOP Design:</strong> Fish class encapsulates all state (position, size, color) and behavior (movement, drawing)</li>
            <li><strong>Frame Independence:</strong> Uses delta time for consistent movement across all frame rates</li>
            <li><strong>Natural Behavior:</strong>
                <ul>
                    <li>Wandering: Small random direction changes per frame</li>
                    <li>Smooth Boundaries: Gradual turns toward center when near edges</li>
                    <li>Tail Wiggle: Subtle oscillation based on speed</li>
                </ul>
            </li>
            <li><strong>Visual Variety:</strong> Random size (10-20px), color (HSL hue variation), and speed (50-150px/s)</li>
            <li><strong>Efficiency:</strong> Optimized for 12 fish (easily scalable) using Canvas API directly</li>
        </ul>
    </section>
</body>
</html>
```

### Key Features Explained:

1. **Object-Oriented Design**:
   - `Fish` class encapsulates all fish properties (position, size, color, speed) and behaviors (update, draw)
   - Each fish maintains its own state and animation state (wiggle phase)

2. **Natural Movement**:
   - **Wandering**: Small random direction changes (`(Math.random() - 0.5) * 0.2`) create organic pathing
   - **Boundary Handling**: Fish turn gradually toward the center using smooth interpolation when approaching edges (no instant direction flips)
   - **Frame-Independent Animation**: Delta time calculation ensures consistent speed across all devices/frame rates

3. **Visual Appeal**:
   - **Fish Shape**: Elliptical body with triangular tail for realistic appearance
   - **Tail Wiggle**: Subtle oscillation using sine wave animation tied to fish speed
   - **Color Variety**: HSL color scheme with random hue values for natural color variation
   - **Orientation**: Canvas rotation makes fish face their direction of movement

4. **Efficiency**:
   - Uses Canvas API directly (no external libraries)
   - Minimal DOM operations
   - 12 fish (easily configurable) maintain smooth performance

### How to Use:
1. Save this file as an HTML file
2. Open it in any modern web browser
3. Observe the autonomous fish swimming with natural behavior:
   - Fish wander gradually changing direction
   - Smoothly turn away from edges
   - Display subtle tail wiggles
   - Maintain consistent speed regardless of frame rate

The simulation runs continuously without user interaction, creating a calming aquarium effect with varied fish behavior and visual characteristics.

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: Seed-OSS-36B-Instruct-UD-Q5_K_XL.gguf -->
<!-- Prompt: aquarium.md -->
<!-- Generation Time: 339.04s -->
<!-- Fallback Used: False -->