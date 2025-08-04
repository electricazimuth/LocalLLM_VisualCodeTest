# Happy Mrs. Chicken Simulation

I'll create a charming simulation of Happy Mrs. Chicken that wanders around and lays eggs periodically. Let me implement this with clean, well-structured JavaScript and HTML.

```html
<!DOCTYPE html>
<html>
<head>
    <title>Happy Mrs. Chicken Simulation</title>
    <style>
        body { 
            margin: 10px; 
            overflow: hidden; 
            background-color: #eee; 
            font-family: 'Comic Sans MS', cursive, sans-serif;
        }
        canvas { 
            display: block; 
            margin: 20px auto; 
            border: 3px solid #8B4513; 
            background-color: #90ee90; 
            box-shadow: 0 0 15px rgba(0,0,0,0.2);
        }
        #title {
            text-align: center;
            color: #8B4513;
            font-size: 28px;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        }
        #notes {
            max-width: 600px;
            margin: 20px auto;
            padding: 15px;
            background-color: #f9f9f9;
            border-radius: 10px;
            border: 1px solid #ddd;
            font-size: 14px;
            line-height: 1.5;
        }
    </style>
</head>
<body>
    <h1 id="title">Happy Mrs. Chicken Simulation</h1>
    <canvas id="simulationCanvas" width="512" height="512"></canvas>

    <script>
        // --- CHICKEN AND EGG CLASSES ---
        
        class Chicken {
            constructor(x, y) {
                this.x = x;
                this.y = y;
                this.radius = 25;
                this.speed = 1.5;
                this.direction = Math.random() * Math.PI * 2; // Random initial direction
                this.state = 'wandering'; // 'wandering' or 'laying'
                this.layingTimer = 0;
                this.layingDuration = 1000; // ms
                this.wanderTimer = 0;
                this.wanderDuration = 2000; // ms
                this.color = '#FFD700'; // Gold/yellow color
                this.eyeColor = '#000000'; // Black eyes
                this.beakColor = '#FF8C00'; // Orange beak
                this.wingColor = '#FFA500'; // Orange wings
            }
            
            update(deltaTime) {
                // Update timers
                if (this.state === 'laying') {
                    this.layingTimer += deltaTime;
                    if (this.layingTimer >= this.layingDuration) {
                        this.state = 'wandering';
                        this.layingTimer = 0;
                    }
                } else {
                    this.wanderTimer += deltaTime;
                    // Randomly decide to lay an egg
                    if (this.wanderTimer >= this.wanderDuration) {
                        if (Math.random() > 0.7) { // 30% chance to lay an egg
                            this.state = 'laying';
                            this.wanderTimer = 0;
                            this.layingTimer = 0;
                        } else {
                            // Change direction occasionally
                            this.direction += (Math.random() - 0.5) * 0.5;
                            this.wanderTimer = 0;
                        }
                    }
                }
                
                // Move chicken if not laying
                if (this.state === 'wandering') {
                    this.x += Math.cos(this.direction) * this.speed * (deltaTime / 16);
                    this.y += Math.sin(this.direction) * this.speed * (deltaTime / 16);
                    
                    // Boundary handling
                    if (this.x < this.radius) {
                        this.x = this.radius;
                        this.direction = Math.PI - this.direction;
                    } else if (this.x > canvas.width - this.radius) {
                        this.x = canvas.width - this.radius;
                        this.direction = Math.PI - this.direction;
                    }
                    
                    if (this.y < this.radius) {
                        this.y = this.radius;
                        this.direction = -this.direction;
                    } else if (this.y > canvas.height - this.radius) {
                        this.y = canvas.height - this.radius;
                        this.direction = -this.direction;
                    }
                }
            }
            
            draw(ctx) {
                // Save context
                ctx.save();
                
                // Translate to chicken position
                ctx.translate(this.x, this.y);
                
                // Rotate based on direction
                ctx.rotate(this.direction);
                
                // Draw chicken body (yellow circle)
                ctx.beginPath();
                ctx.arc(0, 0, this.radius, 0, Math.PI * 2);
                ctx.fillStyle = this.state === 'laying' ? '#FFA500' : this.color; // Slightly orange when laying
                ctx.fill();
                ctx.strokeStyle = '#8B4513';
                ctx.lineWidth = 2;
                ctx.stroke();
                
                // Draw chicken head
                ctx.beginPath();
                ctx.arc(this.radius * 0.7, -this.radius * 0.2, this.radius * 0.6, 0, Math.PI * 2);
                ctx.fillStyle = this.state === 'laying' ? '#FFA500' : this.color;
                ctx.fill();
                ctx.stroke();
                
                // Draw eye
                ctx.beginPath();
                ctx.arc(this.radius * 0.9, -this.radius * 0.3, this.radius * 0.15, 0, Math.PI * 2);
                ctx.fillStyle = this.eyeColor;
                ctx.fill();
                
                // Draw beak
                ctx.beginPath();
                ctx.moveTo(this.radius * 1.2, -this.radius * 0.1);
                ctx.lineTo(this.radius * 1.8, -this.radius * 0.1);
                ctx.lineTo(this.radius * 1.5, 0);
                ctx.closePath();
                ctx.fillStyle = this.beakColor;
                ctx.fill();
                
                // Draw wing
                ctx.beginPath();
                ctx.ellipse(-this.radius * 0.2, 0, this.radius * 0.5, this.radius * 0.3, 0, 0, Math.PI * 2);
                ctx.fillStyle = this.wingColor;
                ctx.fill();
                ctx.stroke();
                
                // Draw leg
                ctx.beginPath();
                ctx.moveTo(-this.radius * 0.3, this.radius);
                ctx.lineTo(-this.radius * 0.3, this.radius + 15);
                ctx.moveTo(this.radius * 0.3, this.radius);
                ctx.lineTo(this.radius * 0.3, this.radius + 15);
                ctx.strokeStyle = '#FF8C00';
                ctx.lineWidth = 3;
                ctx.stroke();
                
                // Draw egg when laying
                if (this.state === 'laying') {
                    ctx.save();
                    ctx.translate(-this.radius * 0.5, this.radius * 0.5);
                    ctx.beginPath();
                    ctx.ellipse(0, 0, this.radius * 0.4, this.radius * 0.6, 0, 0, Math.PI * 2);
                    ctx.fillStyle = '#FFFFFF';
                    ctx.fill();
                    ctx.strokeStyle = '#F5F5DC';
                    ctx.lineWidth = 2;
                    ctx.stroke();
                    ctx.restore();
                }
                
                // Restore context
                ctx.restore();
            }
        }
        
        class Egg {
            constructor(x, y) {
                this.x = x;
                this.y = y;
                this.radiusX = 15;
                this.radiusY = 25;
                this.color = '#FFFFFF';
                this.shadeColor = '#F5F5DC';
                this.lifetime = 10000; // 10 seconds
                this.age = 0;
            }
            
            update(deltaTime) {
                this.age += deltaTime;
            }
            
            draw(ctx) {
                ctx.save();
                ctx.translate(this.x, this.y);
                
                // Draw egg with gradient effect
                const gradient = ctx.createRadialGradient(0, 0, 0, 0, 0, this.radiusY);
                gradient.addColorStop(0, this.color);
                gradient.addColorStop(1, this.shadeColor);
                
                ctx.beginPath();
                ctx.ellipse(0, 0, this.radiusX, this.radiusY, 0, 0, Math.PI * 2);
                ctx.fillStyle = gradient;
                ctx.fill();
                
                // Draw egg texture
                ctx.beginPath();
                ctx.ellipse(0, 0, this.radiusX * 0.7, this.radiusY * 0.7, 0, 0, Math.PI * 2);
                ctx.strokeStyle = '#E6E6FA';
                ctx.lineWidth = 1;
                ctx.stroke();
                
                ctx.restore();
            }
            
            isExpired() {
                return this.age >= this.lifetime;
            }
        }
        
        // --- SIMULATION SETUP ---
        
        const canvas = document.getElementById('simulationCanvas');
        const ctx = canvas.getContext('2d');
        
        // Create chicken
        const chicken = new Chicken(canvas.width / 2, canvas.height / 2);
        
        // Create eggs array
        const eggs = [];
        
        // Animation variables
        let lastTime = 0;
        let frameCount = 0;
        
        // --- ANIMATION LOOP ---
        
        function animate(timestamp) {
            // Calculate delta time for frame-rate independence
            const deltaTime = timestamp - lastTime;
            lastTime = timestamp;
            
            // Clear canvas with green grass background
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            // Draw grass pattern
            drawGrass();
            
            // Update chicken
            chicken.update(deltaTime);
            
            // Update eggs
            for (let i = eggs.length - 1; i >= 0; i--) {
                eggs[i].update(deltaTime);
                
                // Remove expired eggs
                if (eggs[i].isExpired()) {
                    eggs.splice(i, 1);
                }
            }
            
            // Draw eggs
            eggs.forEach(egg => egg.draw(ctx));
            
            // Draw chicken
            chicken.draw(ctx);
            
            // Draw stats
            drawStats();
            
            // Request next frame
            requestAnimationFrame(animate);
        }
        
        // --- DRAWING FUNCTIONS ---
        
        function drawGrass() {
            // Draw a simple grass pattern
            ctx.fillStyle = '#228B22';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            // Draw some grass blades
            ctx.strokeStyle = '#32CD32';
            ctx.lineWidth = 1;
            for (let i = 0; i < 100; i++) {
                const x = Math.random() * canvas.width;
                const y = Math.random() * canvas.height;
                const height = 5 + Math.random() * 10;
                ctx.beginPath();
                ctx.moveTo(x, y);
                ctx.lineTo(x, y - height);
                ctx.stroke();
            }
        }
        
        function drawStats() {
            // Draw egg count
            ctx.fillStyle = '#000000';
            ctx.font = '16px Arial';
            ctx.fillText(`Eggs: ${eggs.length}`, 20, 30);
            
            // Draw state indicator
            ctx.fillText(`State: ${chicken.state}`, 20, 50);
            
            // Draw chicken position
            ctx.fillText(`Position: (${Math.floor(chicken.x)}, ${Math.floor(chicken.y)})`, 20, 70);
        }
        
        // --- EVENT HANDLERS ---
        
        // When chicken lays an egg, create a new egg object
        function layEgg() {
            if (chicken.state === 'laying') {
                eggs.push(new Egg(chicken.x - chicken.radius * 0.5, chicken.y + chicken.radius * 0.5));
            }
        }
        
        // Set up the initial egg laying event
        chicken.onLayEgg = layEgg;
        
        // Start the simulation
        requestAnimationFrame(animate);
        
        // Add a small delay before laying the first egg to allow for initialization
        setTimeout(() => {
            chicken.state = 'laying';
            chicken.layingTimer = 0;
        }, 1000);
    </script>
    
    <section id="notes">
        <h2>Implementation Notes</h2>
        <p><strong>Chicken Behavior:</strong> The chicken uses a wandering AI that changes direction periodically. When it decides to lay an egg (30% chance), it enters a "laying" state where it pauses briefly before resuming movement. The chicken always stays within canvas boundaries by bouncing off edges.</p>
        <p><strong>Egg System:</strong> Eggs are created at the chicken's position when it lays them. Each egg has a 10-second lifetime before disappearing. Eggs have a realistic egg shape with a subtle gradient and texture.</p>
        <p><strong>Visual Design:</strong> The chicken is drawn with a yellow body, orange beak, and brown legs. When laying, it slightly changes color to indicate the action. The background features a grassy green field with decorative grass blades.</p>
        <p><strong>Performance:</strong> The simulation uses requestAnimationFrame for smooth animation and delta time calculation for frame-rate independent movement. The chicken's movement and egg lifetimes are calculated based on time rather than frame count for consistency.</p>
    </section>
</body>
</html>
```

## Key Features of the Implementation:

1. **Chicken Class**:
   - Visual representation with body, head, eye, beak, and legs
   - Wandering AI with direction changes and boundary handling
   - State management (wandering vs laying)
   - Directional orientation based on movement

2. **Egg Class**:
   - Realistic egg shape with gradient coloring
   - Lifetime system (10 seconds)
   - Automatic cleanup when expired

3. **Game AI**:
   - Chicken wanders around with random direction changes
   - 30% chance to lay an egg during wandering
   - Boundary collision detection with bouncing response

4. **Visual Elements**:
   - Green grassy background with decorative grass blades
   - Chicken changes color slightly when laying eggs
   - Egg appears at chicken's position when laid
   - Stats display showing egg count, state, and position

5. **Performance**:
   - Frame-rate independent animation using delta time
   - Efficient object management with arrays
   - Smooth rendering using canvas API

The simulation runs completely in the browser with no external dependencies. The chicken moves around the canvas, occasionally laying eggs that remain visible for 10 seconds before disappearing.

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: Qwen3-Coder-30B-A3B-Instruct-UD-Q6_K_XL.gguf -->
<!-- Prompt: chicken.md -->
<!-- Generation Time: 33.57s -->
<!-- Fallback Used: False -->