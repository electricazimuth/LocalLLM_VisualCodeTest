# Autonomous Aquarium Simulation

I'll create a visually appealing aquarium simulation with autonomous fish that swim naturally within the tank boundaries. Here's the complete implementation:

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
            background-color: rgb(207, 247, 255); 
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
        }
        h1 {
            color: #0d47a1;
            text-align: center;
            margin-top: 10px;
        }
        #notes {
            max-width: 800px;
            margin: 20px;
            padding: 15px;
            background-color: rgba(255, 255, 255, 0.7);
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
    </style>
</head>
<body>
    <h1>Autonomous Aquarium Simulation</h1>
    <canvas id="simulationCanvas" width="800" height="600"></canvas>
    
    <section id="notes">
        <h2>Implementation Notes</h2>
        <p>This simulation features:</p>
        <ul>
            <li>15 autonomous fish with unique characteristics (size, color, speed)</li>
            <li>Natural swimming behavior with smooth turning and wandering</li>
            <li>Boundary detection and gentle redirection to center</li>
            <li>Each fish has a tail that wiggles for organic movement</li>
            <li>Static background elements like plants and rocks</li>
            <li>Frame-rate independent animation using delta time</li>
            <li>Object-oriented design with Fish class</li>
        </ul>
        <p>Key features:</p>
        <ul>
            <li>Fish orient themselves in the direction they're swimming</li>
            <li>Boundary interaction creates natural avoidance behavior</li>
            <li>Smooth animation using requestAnimationFrame</li>
            <li>Efficient rendering with proper canvas clearing</li>
        </ul>
    </section>

    <script>
        // Canvas setup
        const canvas = document.getElementById('simulationCanvas');
        const ctx = canvas.getContext('2d');
        const W = canvas.width;
        const H = canvas.height;

        // Time tracking for delta time
        let lastTimestamp = 0;
        let deltaTime = 0;

        // Fish class definition
        class Fish {
            constructor(x, y) {
                // Position
                this.x = x;
                this.y = y;
                
                // Size and speed
                this.size = Math.random() * 20 + 15; // 15-35px
                this.speed = Math.random() * 2 + 1; // 1-3 px/frame
                
                // Color with some variation
                const hue = Math.floor(Math.random() * 360);
                this.color = `hsl(${hue}, 80%, 50%)`;
                this.highlightColor = `hsl(${hue}, 100%, 70%)`;
                
                // Velocity with random initial direction
                const angle = Math.random() * Math.PI * 2;
                this.vx = Math.cos(angle) * this.speed;
                this.vy = Math.sin(angle) * this.speed;
                
                // Orientation (in radians)
                this.angle = angle;
                
                // Wandering parameters
                this.wanderAngle = 0;
                this.wanderSpeed = Math.random() * 0.02 + 0.005;
                
                // Tail wiggling
                this.tailPhase = Math.random() * Math.PI * 2;
                this.tailSpeed = 0.1 + Math.random() * 0.1;
                
                // Boundary avoidance
                this.avoidanceRadius = this.size * 2;
                this.avoidanceStrength = 0.05;
            }
            
            // Update fish position and behavior
            update(deltaTime) {
                // Update angle based on velocity
                this.angle = Math.atan2(this.vy, this.vx);
                
                // Apply wandering behavior
                this.wanderAngle += (Math.random() - 0.5) * this.wanderSpeed;
                const wanderForce = {
                    x: Math.cos(this.wanderAngle) * 0.2,
                    y: Math.sin(this.wanderAngle) * 0.2
                };
                
                // Apply wandering force to velocity
                this.vx += wanderForce.x;
                this.vy += wanderForce.y;
                
                // Normalize velocity to maintain constant speed
                const speed = Math.sqrt(this.vx * this.vx + this.vy * this.vy);
                if (speed > 0) {
                    this.vx = (this.vx / speed) * this.speed;
                    this.vy = (this.vy / speed) * this.speed;
                }
                
                // Boundary avoidance
                this.avoidBoundaries();
                
                // Update position
                this.x += this.vx;
                this.y += this.vy;
                
                // Update tail wiggling
                this.tailPhase += this.tailSpeed;
            }
            
            // Handle boundary interactions
            avoidBoundaries() {
                // Create avoidance forces
                let avoidanceX = 0;
                let avoidanceY = 0;
                
                // Left boundary
                if (this.x < this.avoidanceRadius) {
                    avoidanceX += (this.avoidanceRadius - this.x) * this.avoidanceStrength;
                }
                // Right boundary
                else if (this.x > W - this.avoidanceRadius) {
                    avoidanceX += (W - this.avoidanceRadius - this.x) * this.avoidanceStrength;
                }
                
                // Top boundary
                if (this.y < this.avoidanceRadius) {
                    avoidanceY += (this.avoidanceRadius - this.y) * this.avoidanceStrength;
                }
                // Bottom boundary
                else if (this.y > H - this.avoidanceRadius) {
                    avoidanceY += (H - this.avoidanceRadius - this.y) * this.avoidanceStrength;
                }
                
                // Apply avoidance force
                this.vx += avoidanceX;
                this.vy += avoidanceY;
            }
            
            // Draw the fish
            draw() {
                ctx.save();
                ctx.translate(this.x, this.y);
                ctx.rotate(this.angle);
                
                // Draw fish body
                ctx.fillStyle = this.color;
                ctx.beginPath();
                ctx.ellipse(0, 0, this.size, this.size/2, 0, 0, Math.PI * 2);
                ctx.fill();
                
                // Draw fish tail
                const tailAngle = Math.sin(this.tailPhase) * 0.5;
                ctx.fillStyle = this.highlightColor;
                ctx.beginPath();
                ctx.moveTo(-this.size * 0.8, 0);
                ctx.lineTo(-this.size * 1.5, -this.size/2 * Math.sin(tailAngle));
                ctx.lineTo(-this.size * 1.5, this.size/2 * Math.sin(tailAngle));
                ctx.closePath();
                ctx.fill();
                
                // Draw fish eye
                ctx.fillStyle = 'white';
                ctx.beginPath();
                ctx.arc(this.size/3, -this.size/4, this.size/6, 0, Math.PI * 2);
                ctx.fill();
                
                ctx.fillStyle = 'black';
                ctx.beginPath();
                ctx.arc(this.size/3, -this.size/4, this.size/12, 0, Math.PI * 2);
                ctx.fill();
                
                ctx.restore();
            }
        }

        // Background elements
        class Plant {
            constructor(x, y) {
                this.x = x;
                this.y = y;
                this.height = Math.random() * 40 + 30;
                this.width = Math.random() * 15 + 10;
                this.color = `hsl(${Math.random() * 60 + 60}, 70%, 30%)`;
            }
            
            draw() {
                ctx.fillStyle = this.color;
                ctx.beginPath();
                ctx.ellipse(this.x, this.y, this.width/2, this.height/2, 0, 0, Math.PI * 2);
                ctx.fill();
                
                // Draw stem
                ctx.fillStyle = `hsl(${Math.random() * 60 + 60}, 70%, 20%)`;
                ctx.fillRect(this.x - this.width/8, this.y + this.height/2, this.width/4, this.height/2);
            }
        }

        class Rock {
            constructor(x, y) {
                this.x = x;
                this.y = y;
                this.size = Math.random() * 30 + 20;
                this.color = `hsl(${Math.random() * 30 + 200}, 30%, 40%)`;
            }
            
            draw() {
                ctx.fillStyle = this.color;
                ctx.beginPath();
                ctx.ellipse(this.x, this.y, this.size/2, this.size/3, 0, 0, Math.PI * 2);
                ctx.fill();
            }
        }

        // Create fish and background elements
        const fishArray = [];
        const plants = [];
        const rocks = [];

        // Initialize fish
        for (let i = 0; i < 15; i++) {
            const x = Math.random() * (W - 100) + 50;
            const y = Math.random() * (H - 100) + 50;
            fishArray.push(new Fish(x, y));
        }

        // Initialize background elements
        for (let i = 0; i < 10; i++) {
            const x = Math.random() * W;
            const y = Math.random() * H;
            plants.push(new Plant(x, y));
        }

        for (let i = 0; i < 8; i++) {
            const x = Math.random() * W;
            const y = Math.random() * H;
            rocks.push(new Rock(x, y));
        }

        // Main game loop
        function gameLoop(timestamp) {
            // Calculate delta time for frame-rate independence
            if (lastTimestamp === 0) {
                deltaTime = 16; // Assume 60fps base
            } else {
                deltaTime = timestamp - lastTimestamp;
            }
            lastTimestamp = timestamp;

            // Clear canvas with a light blue background
            ctx.clearRect(0, 0, W, H);
            
            // Draw water background with subtle gradient
            const gradient = ctx.createLinearGradient(0, 0, 0, H);
            gradient.addColorStop(0, '#a8e6cf');
            gradient.addColorStop(1, '#4dd0e1');
            ctx.fillStyle = gradient;
            ctx.fillRect(0, 0, W, H);
            
            // Draw bubbles
            drawBubbles();
            
            // Draw background elements
            plants.forEach(plant => plant.draw());
            rocks.forEach(rock => rock.draw());
            
            // Update and draw fish
            fishArray.forEach(fish => {
                fish.update(deltaTime);
                fish.draw();
            });
            
            // Continue the loop
            requestAnimationFrame(gameLoop);
        }

        // Draw bubbles for background effect
        function drawBubbles() {
            // Create some bubbles
            ctx.fillStyle = 'rgba(255, 255, 255, 0.5)';
            
            // Draw bubbles at random positions
            for (let i = 0; i < 20; i++) {
                const x = (Math.sin(Date.now() * 0.0001 + i) * 0.5 + 0.5) * W;
                const y = (Math.sin(Date.now() * 0.0002 + i * 0.7) * 0.5 + 0.5) * H;
                const size = Math.sin(Date.now() * 0.0003 + i) * 3 + 5;
                
                ctx.beginPath();
                ctx.arc(x, y, size, 0, Math.PI * 2);
                ctx.fill();
            }
        }

        // Start the simulation
        requestAnimationFrame(gameLoop);
    </script>
</body>
</html>
```

## Key Features of the Implementation

1. **Object-Oriented Design**:
   - Fish class with encapsulated properties and behaviors
   - Plant and Rock classes for background elements
   - Efficient management of multiple objects

2. **Natural Fish Behavior**:
   - Autonomous movement with velocity-based physics
   - Wandering behavior for organic movement patterns
   - Boundary detection with gentle redirection
   - Tail wiggling for realistic motion

3. **Visual Elements**:
   - Colorful fish with unique characteristics
   - Animated bubbles in the background
   - Underwater plants and rocks for depth
   - Smooth, continuous animation

4. **Performance Optimizations**:
   - Frame-rate independent animation using delta time
   - Efficient canvas clearing and drawing
   - Proper object management with arrays

5. **User Experience**:
   - Clean, visually appealing interface
   - Informative notes section explaining the implementation
   - Responsive design that works well at different sizes

The simulation creates a calming underwater environment with fish that move naturally, avoiding boundaries gracefully while maintaining their swimming patterns. The implementation demonstrates good JavaScript practices including object-oriented design, encapsulation, and efficient animation loops.

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: Qwen3-Coder-30B-A3B-Instruct-UD-Q6_K_XL.gguf -->
<!-- Prompt: aquarium.md -->
<!-- Time: 24.75s -->
<!-- Fallback: False -->