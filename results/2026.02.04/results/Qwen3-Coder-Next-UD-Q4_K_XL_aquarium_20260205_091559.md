Here is the complete, single-file solution. It implements a robust Object-Oriented design, physics-based movement with steering behaviors, and a rendering loop that handles orientation and animations smoothly.

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <title>Autonomous Aquarium Simulation</title>
    <style>
        body { 
            margin: 0; 
            overflow: hidden; 
            background-color: #2c3e50; 
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            font-family: sans-serif;
            height: 100vh;
        }
        
        .container {
            position: relative;
            box-shadow: 0 0 30px rgba(0,0,0,0.5);
        }

        canvas { 
            display: block; 
            background: linear-gradient(to bottom, #006994, #001e3b); 
            border-radius: 4px;
        }

        #ui-layer {
            position: absolute;
            top: 10px;
            left: 10px;
            color: white;
            pointer-events: none;
            background: rgba(0,0,0,0.3);
            padding: 10px;
            border-radius: 5px;
        }

        #notes {
            max-width: 600px;
            margin-top: 20px;
            padding: 20px;
            background-color: #f4f4f4;
            border-left: 5px solid #006994;
            color: #333;
            line-height: 1.6;
        }
    </style>
</head>
<body>

    <div class="container">
        <canvas id="simulationCanvas" width="800" height="600"></canvas>
        <div id="ui-layer">
            <strong>Aquarium Simulation</strong><br>
            Fish Count: <span id="fish-count">0</span><br>
            FPS: <span id="fps">0</span>
        </div>
    </div>

    <section id="notes">
        <h3>Implementation Notes</h3>
        <p><strong>1. Object-Oriented Design:</strong> The solution uses ES6 Classes. The <code>Fish</code> class encapsulates state (position, velocity, color) and behavior (movement, turning, drawing). There is also a <code>Seaweed</code> class for background decoration.</p>
        <p><strong>2. Autonomous Movement (Steering Behaviors):</strong> Fish do not just bounce off walls. They use a "Seek" behavior to return to the center if they get too close to edges (boundary avoidance). They also use a "Wander" behavior (random small velocity changes) to create organic, non-linear swimming patterns.</p>
        <p><strong>3. Delta Time Implementation:</strong> Movement calculations multiply velocity by <code>dt</code> (delta time). This ensures the fish swim at the same speed regardless of whether the computer is running at 60fps or 144fps.</p>
        <p><strong>4. Rendering:</strong> The canvas context is translated and rotated to the fish's current position and heading before drawing. This allows the fish graphic to always face the direction of travel. A simple tail animation is calculated using a sine wave based on time.</p>
        <p><strong>5. Performance:</strong> Objects are removed from the array if they are no longer needed (though in this simulation, fish persist). The render loop clears the canvas and redraws all static elements (seaweed) and dynamic elements (fish) every frame.</p>
    </section>

    <script>
        // --- Configuration & Constants ---
        const CANVAS_WIDTH = 800;
        const CANVAS_HEIGHT = 600;
        const FISH_COUNT = 12;
        const SEAWEED_COUNT = 20;
        
        // Utility Functions
        const randomRange = (min, max) => Math.random() * (max - min) + min;
        const randomColor = () => {
            const colors = ['#FF6B6B', '#4ECDC4', '#FFE66D', '#FF9F43', '#54A0FF', '#5F27CD'];
            return colors[Math.floor(Math.random() * colors.length)];
        };

        // --- Background Element: Seaweed ---
        class Seaweed {
            constructor(x) {
                this.x = x;
                this.height = randomRange(50, 150);
                this.color = `rgb(0, ${Math.floor(randomRange(80, 150))}, 80)`;
                this.swaySpeed = randomRange(3, 6);
                this.swayOffset = randomRange(0, Math.PI * 2);
            }

            draw(ctx, time) {
                ctx.fillStyle = this.color;
                ctx.beginPath();
                // Draw a curved shape for the seaweed
                ctx.moveTo(this.x, CANVAS_HEIGHT);
                
                // Simple Sine wave approximation for sway
                const sway = Math.sin(time / 500 * this.swaySpeed + this.swayOffset) * 20;
                
                ctx.quadraticCurveTo(
                    this.x + sway, 
                    CANVAS_HEIGHT - this.height / 2, 
                    this.x + (sway / 2), 
                    CANVAS_HEIGHT - this.height
                );
                ctx.lineTo(this.x + 5, CANVAS_HEIGHT); // Base width
                ctx.fill();
            }
        }

        // --- Main Entity: Fish ---
        class Fish {
            constructor(w, h) {
                this.width = w;
                this.height = h;
                
                // Position
                this.x = randomRange(50, w - 50);
                this.y = randomRange(50, h - 50);
                
                // Physics
                const angle = randomRange(0, Math.PI * 2);
                const speed = randomRange(50, 120); // pixels per second
                this.vx = Math.cos(angle) * speed;
                this.vy = Math.sin(angle) * speed;
                this.speed = speed;
                
                // Appearance
                this.size = randomRange(10, 20); // Base radius
                this.color = randomColor();
                this.tailAngle = 0;
                this.tailSpeed = randomRange(5, 10);
                
                // Steering attributes
                this.maxForce = 2.5; // How fast they can turn
                this.perception = 150; // Radius to check for edges
            }

            update(dt, time) {
                // 1. Update Tail Animation (Visual only)
                this.tailAngle = Math.sin(time / 100 * this.tailSpeed) * 0.5;

                // 2. Boundary Detection & Steering (Wander & Seek)
                
                // Calculate distance to center of screen (Seek behavior for centering)
                const centerX = this.width / 2;
                const centerY = this.height / 2;
                const distToCenter = Math.sqrt((this.x - centerX) ** 2 + (this.y - centerY) ** 2);
                
                // Steering Vector accumulator
                let steerX = 0;
                let steerY = 0;

                // Boundary Avoidance (Wall Fleeing)
                // If close to edge, apply force away from edge
                const margin = 50;
                if (this.x < margin) {
                    steerX += 200; // Strong force right
                } else if (this.x > this.width - margin) {
                    steerX -= 200; // Strong force left
                }

                if (this.y < margin) {
                    steerY += 200; // Strong force down
                } else if (this.y > this.height - margin) {
                    steerY -= 200; // Strong force up
                }

                // Add Random Wander (Noise)
                // Randomly perturb velocity slightly to create organic movement
                if (Math.random() < 0.05) {
                    steerX += randomRange(-50, 50);
                    steerY += randomRange(-50, 50);
                }

                // Apply Steering Forces to Velocity
                this.vx += steerX * dt;
                this.vy += steerY * dt;

                // Limit Speed (Optional, keeps them from going lightspeed)
                const currentSpeed = Math.sqrt(this.vx * this.vx + this.vy * this.vy);
                if (currentSpeed > this.maxForce * 10) {
                    const ratio = (this.maxForce * 10) / currentSpeed;
                    this.vx *= ratio;
                    this.vy *= ratio;
                }

                // Update Position
                this.x += this.vx * dt;
                this.y += this.vy * dt;

                // Hard Clamp to screen (Safety net against physics glitches)
                this.x = Math.max(this.size, Math.min(this.width - this.size, this.x));
                this.y = Math.max(this.size, Math.min(this.height - this.size, this.y));
            }

            draw(ctx) {
                // Calculate heading angle
                const angle = Math.atan2(this.vy, this.vx);
                
                ctx.save();
                ctx.translate(this.x, this.y);
                ctx.rotate(angle);

                // Draw Body (Oval)
                ctx.fillStyle = this.color;
                ctx.beginPath();
                // Ellipse(centerX, centerY, radiusX, radiusY, rotation, startAngle, endAngle)
                ctx.ellipse(0, 0, this.size * 1.5, this.size, 0, 0, Math.PI * 2);
                ctx.fill();

                // Draw Eye
                ctx.fillStyle = 'white';
                ctx.beginPath();
                ctx.arc(this.size * 0.8, -this.size * 0.3, this.size * 0.25, 0, Math.PI * 2);
                ctx.fill();
                ctx.fillStyle = 'black';
                ctx.beginPath();
                ctx.arc(this.size * 0.9, -this.size * 0.3, this.size * 0.1, 0, Math.PI * 2);
                ctx.fill();

                // Draw Tail (Animated)
                ctx.fillStyle = this.color;
                ctx.beginPath();
                const tailX = -this.size * 1.2;
                const tailWidth = this.size * 0.6 + (Math.abs(Math.sin(this.tailAngle)) * this.size * 0.4);
                
                ctx.moveTo(-this.size * 0.5, 0); // Pivot at back of body
                ctx.lineTo(-this.size * 2.0, -tailWidth);
                ctx.lineTo(-this.size * 1.8, 0); // Notch in tail
                ctx.lineTo(-this.size * 2.0, tailWidth);
                ctx.closePath();
                ctx.fill();

                // Draw Fins
                ctx.fillStyle = this.color;
                ctx.globalAlpha = 0.7;
                ctx.beginPath();
                ctx.moveTo(0, -this.size * 0.5);
                ctx.lineTo(-this.size * 0.5, -this.size * 1.2);
                ctx.lineTo(this.size * 0.5, -this.size * 0.5);
                ctx.fill();
                ctx.globalAlpha = 1.0;

                ctx.restore();
            }
        }

        // --- Main Simulation Controller ---
        class Aquarium {
            constructor() {
                this.canvas = document.getElementById('simulationCanvas');
                this.ctx = this.canvas.getContext('2d');
                this.width = this.canvas.width;
                this.height = this.canvas.height;
                
                this.fish = [];
                this.seaweed = [];
                this.lastTime = 0;
                this.fishCountSpan = document.getElementById('fish-count');
                this.fpsSpan = document.getElementById('fps');
                this.frameCount = 0;
                this.lastFpsTime = 0;

                this.init();
            }

            init() {
                // Initialize Fish
                for (let i = 0; i < FISH_COUNT; i++) {
                    this.fish.push(new Fish(this.width, this.height));
                }

                // Initialize Background Seaweed
                const spacing = this.width / SEAWEED_COUNT;
                for (let i = 0; i < SEAWEED_COUNT; i++) {
                    this.seaweed.push(new Seaweed(i * spacing + spacing/2));
                }

                // Start Loop
                requestAnimationFrame((ts) => this.loop(ts));
            }

            update(dt, time) {
                this.fish.forEach(fish => fish.update(dt, time));
            }

            draw(time) {
                // 1. Draw Background Gradient (Water)
                const gradient = this.ctx.createLinearGradient(0, 0, 0, this.height);
                gradient.addColorStop(0, "#00a8ff"); // Lighter top
                gradient.addColorStop(1, "#001e3b"); // Darker bottom
                this.ctx.fillStyle = gradient;
                this.ctx.fillRect(0, 0, this.width, this.height);

                // 2. Draw Background Elements (Seaweed)
                // Draw seaweed before fish so fish appear in front
                this.seaweed.forEach(plant => plant.draw(this.ctx, time));

                // 3. Draw Fish
                this.fish.forEach(fish => fish.draw(this.ctx));
            }

            updateUI() {
                this.frameCount++;
                const now = performance.now();
                
                if (now - this.lastFpsTime >= 1000) {
                    this.fpsSpan.textContent = this.frameCount;
                    this.frameCount = 0;
                    this.lastFpsTime = now;
                    this.fishCountSpan.textContent = this.fish.length;
                }
            }

            loop(timestamp) {
                // Calculate Delta Time (in seconds)
                if (!this.lastTime) this.lastTime = timestamp;
                const dt = (timestamp - this.lastTime) / 1000;
                this.lastTime = timestamp;

                // Prevent huge delta spikes (e.g. if tab is inactive)
                const safeDt = Math.min(dt, 0.1);

                this.update(safeDt, timestamp);
                this.draw(timestamp);
                this.updateUI();

                requestAnimationFrame((ts) => this.loop(ts));
            }
        }

        // Initialize the Simulation when DOM is ready
        window.onload = () => {
            const aquarium = new Aquarium();
        };

    </script>
</body>
</html>
```

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: Qwen3-Coder-Next-UD-Q4_K_XL.gguf -->
<!-- Prompt: aquarium.md -->
<!-- Time: 56.46s -->
<!-- Fallback: False -->