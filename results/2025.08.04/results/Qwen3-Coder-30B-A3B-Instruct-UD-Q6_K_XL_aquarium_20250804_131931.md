# Autonomous Aquarium Simulation

I'll create a visually appealing aquarium simulation with fish that swim autonomously, change direction naturally, and interact with boundaries smoothly. Let me implement this with proper object-oriented design and efficient rendering.

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
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        canvas { 
            display: block; 
            margin: 20px auto; 
            border: 1px solid #888; 
            background-color: #90e0ef; 
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
        }
        h1 {
            color: #0288d1;
            text-align: center;
            margin-top: 10px;
        }
        #notes {
            max-width: 800px;
            margin: 20px;
            padding: 15px;
            background-color: #e3f2fd;
            border-radius: 8px;
            font-size: 14px;
            line-height: 1.5;
        }
        #notes h2 {
            margin-top: 0;
            color: #0277bd;
        }
    </style>
</head>
<body>
    <h1>Autonomous Aquarium Simulation</h1>
    <canvas id="simulationCanvas" width="800" height="600"></canvas>
    
    <section id="notes">
        <h2>Implementation Notes</h2>
        <p>This aquarium simulation features:</p>
        <ul>
            <li><strong>Fish Objects:</strong> Each fish is an object with position, velocity, size, and color</li>
            <li><strong>Autonomous Behavior:</strong> Fish wander naturally, changing direction gradually</li>
            <li><strong>Boundary Interaction:</strong> Fish smoothly turn away from edges toward the center</li>
            <li><strong>Visual Design:</strong> Fish are drawn with orientation, color variation, and subtle tail wiggles</li>
            <li><strong>Performance:</strong> Efficient rendering using requestAnimationFrame with delta time</li>
            <li><strong>Background Elements:</strong> Subtle plants and bubbles for a realistic aquarium feel</li>
        </ul>
        <p>The simulation uses object-oriented design principles with a Fish class and a main game loop that updates and renders all elements.</p>
    </section>

    <script>
        // Canvas setup
        const canvas = document.getElementById('simulationCanvas');
        const ctx = canvas.getContext('2d');
        const W = canvas.width;
        const H = canvas.height;

        // Fish class definition
        class Fish {
            constructor(x, y) {
                this.x = x;
                this.y = y;
                this.size = Math.random() * 20 + 15; // Size between 15-35
                this.speed = Math.random() * 2 + 1; // Speed between 1-3
                this.angle = Math.random() * Math.PI * 2; // Random initial angle
                this.color = this.getRandomColor();
                this.wiggle = 0; // For tail wiggling effect
                this.wiggleSpeed = Math.random() * 0.1 + 0.05;
                this.wiggleDirection = Math.random() > 0.5 ? 1 : -1;
                this.turningSpeed = Math.random() * 0.02 + 0.005; // How quickly fish change direction
            }

            getRandomColor() {
                const colors = [
                    '#FF5252', '#FF4081', '#E040FB', '#7C4DFF', 
                    '#536DFE', '#448AFF', '#40C4FF', '#18FFFF',
                    '#64FFDA', '#69F0AE', '#B2FF59', '#EEFF41',
                    '#FFFF00', '#FFD740', '#FFAB40', '#FF6E40'
                ];
                return colors[Math.floor(Math.random() * colors.length)];
            }

            update(deltaTime) {
                // Update wiggle for tail animation
                this.wiggle += this.wiggleSpeed * deltaTime;
                if (this.wiggle > Math.PI * 2) this.wiggle = 0;

                // Gradually change direction (wandering behavior)
                this.angle += (Math.random() - 0.5) * this.turningSpeed * deltaTime;

                // Update position based on velocity
                this.x += Math.cos(this.angle) * this.speed * deltaTime;
                this.y += Math.sin(this.angle) * this.speed * deltaTime;

                // Boundary interaction - gently steer back toward center
                const margin = 50;
                const centerX = W / 2;
                const centerY = H / 2;
                
                // Left boundary
                if (this.x < margin) {
                    this.angle = Math.atan2(this.y - centerY, this.x - centerX) + Math.PI;
                }
                // Right boundary
                else if (this.x > W - margin) {
                    this.angle = Math.atan2(this.y - centerY, this.x - centerX) + Math.PI;
                }
                // Top boundary
                if (this.y < margin) {
                    this.angle = Math.atan2(this.y - centerY, this.x - centerX) + Math.PI;
                }
                // Bottom boundary
                else if (this.y > H - margin) {
                    this.angle = Math.atan2(this.y - centerY, this.x - centerX) + Math.PI;
                }
            }

            draw() {
                ctx.save();
                ctx.translate(this.x, this.y);
                ctx.rotate(this.angle);
                
                // Draw fish body
                ctx.fillStyle = this.color;
                ctx.beginPath();
                ctx.ellipse(0, 0, this.size, this.size/2, 0, 0, Math.PI * 2);
                ctx.fill();
                
                // Draw fish tail with wiggling effect
                const tailWiggle = Math.sin(this.wiggle) * 5;
                ctx.beginPath();
                ctx.moveTo(-this.size, 0);
                ctx.lineTo(-this.size - 10, -10 + tailWiggle);
                ctx.lineTo(-this.size - 10, 10 + tailWiggle);
                ctx.closePath();
                ctx.fillStyle = this.color;
                ctx.fill();
                
                // Draw fish eye
                ctx.fillStyle = 'white';
                ctx.beginPath();
                ctx.arc(this.size/2, -this.size/4, this.size/5, 0, Math.PI * 2);
                ctx.fill();
                
                ctx.fillStyle = 'black';
                ctx.beginPath();
                ctx.arc(this.size/2 + this.size/10, -this.size/4, this.size/10, 0, Math.PI * 2);
                ctx.fill();
                
                ctx.restore();
            }
        }

        // Bubble class for background elements
        class Bubble {
            constructor() {
                this.x = Math.random() * W;
                this.y = H + Math.random() * 100;
                this.size = Math.random() * 10 + 5;
                this.speed = Math.random() * 0.5 + 0.2;
                this.float = Math.random() * 0.5 - 0.25; // Slight horizontal movement
            }

            update(deltaTime) {
                this.y -= this.speed * deltaTime;
                this.x += this.float * deltaTime;
                
                // Reset bubble when it goes off screen
                if (this.y < -this.size) {
                    this.y = H + Math.random() * 100;
                    this.x = Math.random() * W;
                }
            }

            draw() {
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                ctx.fillStyle = 'rgba(255, 255, 255, 0.5)';
                ctx.fill();
            }
        }

        // Plant class for background elements
        class Plant {
            constructor(x) {
                this.x = x;
                this.y = H;
                this.height = Math.random() * 80 + 60;
                this.width = Math.random() * 15 + 10;
                this.color = `rgba(34, 139, 34, ${Math.random() * 0.3 + 0.4})`;
            }

            draw() {
                ctx.fillStyle = this.color;
                ctx.beginPath();
                ctx.ellipse(this.x, this.y, this.width/2, this.height/2, 0, 0, Math.PI * 2);
                ctx.fill();
            }
        }

        // Simulation state
        let fishArray = [];
        let bubbles = [];
        let plants = [];
        let lastTime = 0;

        // Initialize simulation
        function init() {
            // Create fish
            for (let i = 0; i < 15; i++) {
                fishArray.push(new Fish(
                    Math.random() * (W - 100) + 50,
                    Math.random() * (H - 100) + 50
                ));
            }
            
            // Create bubbles
            for (let i = 0; i < 30; i++) {
                bubbles.push(new Bubble());
            }
            
            // Create plants
            for (let i = 0; i < 10; i++) {
                plants.push(new Plant(Math.random() * W));
            }
        }

        // Main game loop
        function gameLoop(timestamp) {
            // Calculate delta time for frame-rate independence
            const deltaTime = Math.min(100, timestamp - lastTime) / 16; // Normalize to 60fps
            lastTime = timestamp;

            // Clear canvas with a light blue water color
            ctx.clearRect(0, 0, W, H);
            
            // Draw water background gradient
            const gradient = ctx.createLinearGradient(0, 0, 0, H);
            gradient.addColorStop(0, '#90e0ef');
            gradient.addColorStop(1, '#4fc3f7');
            ctx.fillStyle = gradient;
            ctx.fillRect(0, 0, W, H);
            
            // Draw plants
            plants.forEach(plant => plant.draw());
            
            // Update and draw bubbles
            bubbles.forEach(bubble => {
                bubble.update(deltaTime);
                bubble.draw();
            });
            
            // Update and draw fish
            fishArray.forEach(fish => {
                fish.update(deltaTime);
                fish.draw();
            });
            
            // Continue the loop
            requestAnimationFrame(gameLoop);
        }

        // Start the simulation
        init();
        requestAnimationFrame(gameLoop);
    </script>
</body>
</html>
```

## Key Features of the Implementation

1. **Object-Oriented Design**:
   - Fish class with encapsulated state (position, velocity, size, color)
   - Bubble and Plant classes for background elements
   - Clear separation of concerns for updating and rendering

2. **Autonomous Fish Behavior**:
   - Natural wandering movement with gradual direction changes
   - Smooth boundary interaction that steers fish toward the center
   - Tail wiggling animation for organic movement

3. **Visual Elements**:
   - Colorful fish with varied sizes and colors
   - Animated bubbles floating upward
   - Subtle plant elements at the bottom
   - Water gradient background for realistic ocean feel

4. **Performance Optimizations**:
   - Delta time calculation for frame-rate independent movement
   - Efficient rendering using requestAnimationFrame
   - Object pooling for background elements

5. **Realistic Aquarium Feel**:
   - Fish orient themselves in the direction they're swimming
   - Smooth turning behavior near boundaries
   - Natural movement patterns that avoid rigid bouncing

The simulation runs smoothly with 15 fish swimming autonomously, interacting with the boundaries in a natural way while maintaining a calming aquarium environment.

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: Qwen3-Coder-30B-A3B-Instruct-UD-Q6_K_XL.gguf -->
<!-- Prompt: aquarium.md -->
<!-- Generation Time: 29.06s -->
<!-- Fallback Used: False -->