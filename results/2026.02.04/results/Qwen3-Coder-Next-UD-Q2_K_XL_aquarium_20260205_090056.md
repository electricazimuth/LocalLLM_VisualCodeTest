Here is the complete, autonomous aquarium simulation. I have implemented this using a modern ES6 Class-based approach for the Fish objects and a robust `requestAnimationFrame` loop with delta time calculation for smooth animation regardless of frame rate.

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
            font-family: sans-serif;
        }
        h1 {
            color: #01579b;
            margin-bottom: 10px;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
        }
        .container {
            position: relative;
            box-shadow: 0 10px 25px rgba(0,0,0,0.2);
        }
        canvas { 
            display: block; 
            border-radius: 8px;
            background-color: rgb(207, 247, 255); 
            border: 2px solid #0277bd;
        }
        #controls {
            margin-top: 10px;
            color: #555;
            font-size: 0.9rem;
        }
    </style>
</head>
<body>
    <h1>Autonomous Aquarium Simulation</h1>
    
    <div class="container">
        <canvas id="simulationCanvas" width="800" height="600"></canvas>
    </div>
    
    <div id="controls">
        <p>Move your mouse over the tank to scare the fish (pressure wave simulation).</p>
    </div>

    <script>
        /**
         * CONSTANTS & CONFIGURATION
         */
        const CONFIG = {
            fishCount: 15,
            baseSpeed: 80, // pixels per second
            turnSpeed: 2.5, // radians per second
            boundaryBuffer: 50, // how far from edge to start turning
            colors: ['#FF6F61', '#6B5B95', '#88B04B', '#F7CAC9', '#92A8D1', '#F5821F'],
            bgColor: '#006994', // Deep water color
            bgColorTop: '#00a6d4', // Lighter water color
            bubbleCount: 30
        };

        // Mouse interaction state
        const mouse = { x: -1000, y: -1000, active: false };
        
        /**
         * UTILITIES
         */
        class Utils {
            static random(min, max) {
                return Math.random() * (max - min) + min;
            }

            static randomColor(arr) {
                return arr[Math.floor(Math.random() * arr.length)];
            }

            // Calculate angle between two points
            static angleTo(x1, y1, x2, y2) {
                return Math.atan2(y2 - y1, x2 - x1);
            }
        }

        /**
         * FISH CLASS
         * Handles autonomous movement, boundary avoidance, and rendering.
         */
        class Fish {
            constructor(canvasWidth, canvasHeight) {
                this.canvasW = canvasWidth;
                this.canvasH = canvasHeight;
                
                // 1. Initialization
                this.x = Utils.random(50, canvasWidth - 50);
                this.y = Utils.random(50, canvasHeight - 50);
                
                // Random direction (0 to 2PI)
                this.angle = Utils.random(0, Math.PI * 2);
                
                // Velocity properties
                this.speed = Utils.random(60, 120); // Vary speeds for organic feel
                this.size = Utils.random(10, 20);   // Vary sizes
                
                // Appearance
                this.color = Utils.randomColor(CONFIG.colors);
                this.tailWiggleSpeed = Utils.random(5, 10);
                this.tailPhase = Utils.random(0, Math.PI * 2);
                
                // State
                this.maxTurnRate = CONFIG.turnSpeed;
            }

            update(deltaTime, mouseX, mouseY) {
                // 2. Autonomous Movement Logic
                
                // A. Wander Behavior (Steering)
                // Randomly change direction slightly to create organic "wandering"
                this.angle += Utils.random(-0.5, 0.5) * deltaTime;

                // B. Boundary Interaction (Avoidance)
                let turnForce = 0;

                // If too close to Left Wall
                if (this.x < CONFIG.boundaryBuffer) {
                    turnForce = 1.5; // Strong turn right
                }
                // If too close to Right Wall
                else if (this.x > this.canvasW - CONFIG.boundaryBuffer) {
                    turnForce = -1.5; // Strong turn left
                }

                // If too close to Top Wall
                if (this.y < CONFIG.boundaryBuffer) {
                    turnForce += 1.5; // Strong turn down
                }
                // If too close to Bottom Wall
                else if (this.y > this.canvasH - CONFIG.boundaryBuffer) {
                    turnForce -= 1.5; // Strong turn up
                }

                // Apply turns
                this.angle += turnForce * this.maxTurnRate * deltaTime;

                // C. Mouse Avoidance (Predator Interaction)
                // If mouse is on screen, fish try to swim away from it
                const distToMouse = Math.hypot(this.x - mouseX, this.y - mouseY);
                if (distToMouse < 150 && distToMouse > 0) {
                    const angleAway = Utils.angleTo(this.x, this.y, mouseX, mouseY);
                // Smoothly steer away from mouse
                    const diff = angleAway - this.angle;
                // Normalize angle
                    let normalizedDiff = Math.atan2(Math.sin(diff), Math.cos(diff));
                    
                // Apply strong escape turn
                    this.angle += normalizedDiff * 2.0 * deltaTime;
                }

                // 3. Apply Velocity
                this.x += Math.cos(this.angle) * this.speed * deltaTime;
                this.y += Math.sin(this.angle) * this.speed * deltaTime;

                // 4. Hard Boundary Clamp (Safety net)
                if (this.x < 0) this.x = 0;
                if (this.x > this.canvasW) this.x = this.canvasW;
                if (this.y < 0) this.y = 0;
                if (this.y > this.canvasH) this.y = this.canvasH;
                
                // Update tail phase for animation
                this.tailPhase += this.tailWiggleSpeed * deltaTime;
            }

            draw(ctx) {
                ctx.save();
                ctx.translate(this.x, this.y);
                ctx.rotate(this.angle);

                // Draw Body (Oval)
                ctx.fillStyle = this.color;
                ctx.beginPath();
                // Scale x by size, y by size/2
                ctx.ellipse(0, 0, this.size, this.size / 2.5, 0, 0, Math.PI * 2);
                ctx.fill();

                // Draw Eye
                ctx.fillStyle = 'white';
                ctx.beginPath();
                ctx.arc(this.size / 2, -this.size / 6, this.size / 6, 0, Math.PI * 2);
                ctx.fill();
                ctx.fillStyle = 'black';
                ctx.beginPath();
                ctx.arc(this.size / 2 + 2, -this.size / 6, this.size / 12, 0, Math.PI * 2);
                ctx.fill();

                // Draw Tail (Triangle that wiggles)
                ctx.fillStyle = this.color;
                ctx.globalAlpha = 0.8; // Tail is slightly transparent
                
                // Calculate wiggle using sine wave
                const wiggle = Math.sin(this.tailPhase) * 0.2; // 0.2 radians wiggle
                
                ctx.save();
                ctx.translate(-this.size, 0);
                ctx.rotate(wiggle);
                
                ctx.beginPath();
                ctx.moveTo(0, 0);
                ctx.lineTo(-this.size * 1.5, this.size / 2);
                ctx.lineTo(-this.size * 1.5, -this.size / 2);
                ctx.closePath();
                ctx.fill();
                ctx.restore();

                ctx.restore();
            }
        }

        class Bubble {
            constructor(w, h) {
                this.w = w;
                this.h = h;
                this.reset();
            }

            reset() {
                this.x = Utils.random(0, this.w);
                this.y = Utils.random(0, this.h);
                this.size = Utils.random(2, 6);
                this.speed = Utils.random(10, 40);
                this.opacity = Utils.random(0.1, 0.5);
            }

            update(deltaTime) {
                this.y -= this.speed * deltaTime; // Move Up
                if (this.y < -10) {
                    this.y = this.h + 10;
                    this.x = Utils.random(0, this.w);
                }
            }

            draw(ctx) {
                ctx.fillStyle = `rgba(255, 255, 255, ${this.opacity})`;
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                ctx.fill();
            }
        }

        /**
         * BACKGROUND DECORATION (Seaweed)
         */
        class Seaweed {
            constructor(x, h) {
                this.x = x;
                this.h = h;
                this.color = '#2e7d32';
                this.segments = 5;
                this.waveOffset = Utils.random(0, 100);
            }

            draw(ctx, time) {
                const wave = Math.sin(time * 0.002 + this.waveOffset) * 15;
                
                ctx.fillStyle = this.color;
                ctx.beginPath();
                ctx.moveTo(this.x, this.h);
                
                // Draw jagged top and waving body
                for (let i = 0; i <= this.segments; i++) {
                    const y = this.h - (i * 40);
                    const sway = Math.sin(time * 0.003 + i + this.waveOffset) * 20;
                    ctx.quadraticCurveTo(this.x + sway, y - 20, this.x + (sway * 0.5), y);
                }
                
                ctx.lineTo(this.x + 10, this.h);
                ctx.fill();
            }
        }

        /**
         * MAIN SIMULATION CONTROLLER
         */
        const canvas = document.getElementById('simulationCanvas');
        const ctx = canvas.getContext('2d');
        const W = canvas.width;
        const H = canvas.height;

        // Arrays to hold objects
        const fishes = [];
        const bubbles = [];
        const seaweeds = [];

        // Time tracking
        let lastTime = 0;
        let gameTime = 0;

        // Initialize Simulation
        function init() {
            // Create Fish
            for (let i = 0; i < CONFIG.fishCount; i++) {
                fishes.push(new Fish(W, H));
            }

            // Create Bubbles
            for (let i = 0; i < CONFIG.bubbleCount; i++) {
                bubbles.push(new Bubble(W, H));
            }

            // Create Seaweed
            for (let x = 50; x < W - 50; x += 60) {
                seaweeds.push(new Seaweed(x, H));
            }

            // Mouse Listeners
            canvas.addEventListener('mousemove', (e) => {
                const rect = canvas.getBoundingClientRect();
                mouse.x = e.clientX - rect.left;
                mouse.y = e.clientY - rect.top;
                mouse.active = true;
            });

            canvas.addEventListener('mouseleave', () => {
                mouse.x = -1000;
                mouse.y = -1000;
                mouse.active = false;
            });
        }

        function drawBackground(time) {
            // Gradient Water Background
            const gradient = ctx.createLinearGradient(0, 0, 0, H);
            gradient.addColorStop(0, CONFIG.bgColorTop);
            gradient.addColorStop(1, CONFIG.bgColor);
            ctx.fillStyle = gradient;
            ctx.fillRect(0, 0, W, H);

            // Draw Seaweed
            seaweeds.forEach(plant => plant.draw(ctx, time));
        }

        function gameLoop(timestamp) {
            // Calculate Delta Time (seconds passed since last frame)
            // This ensures physics behaves consistently on 60hz, 120hz, or lagging screens
            if (!lastTime) lastTime = timestamp;
            const deltaTime = (timestamp - lastTime) / 1000;
            lastTime = timestamp;
            gameTime += deltaTime * 1000;

            // 1. Clear Canvas
            ctx.clearRect(0, 0, W, H);

            // 2. Draw Background
            drawBackground(timestamp);

            // 3. Update & Draw Fish
            fishes.forEach(fish => {
                fish.update(deltaTime, mouse.x, mouse.y);
                fish.draw(ctx);
            });

            // 4. Update & Draw Bubbles
            bubbles.forEach(bubble => {
                bubble.update(deltaTime);
                bubble.draw(ctx);
            });

            // Request next frame
            requestAnimationFrame(gameLoop);
        }

        // Start
        init();
        requestAnimationFrame(gameLoop);

    </script>

    <section id="notes">
        <h3>Implementation Notes</h3>
        <ul>
            <li><strong>Object-Oriented Design:</strong> The <code>Fish</code> class encapsulates state (position, angle, speed) and behavior (update, draw). This allows for easy scaling to hundreds of fish.</li>
            <li><strong>Delta Time:</strong> The <code>gameLoop</code> calculates <code>deltaTime</code> in seconds. Movement is multiplied by this value, ensuring fish swim at the same speed on high-refresh-rate monitors as they do on standard 60hz screens.</li>
            <li><strong>Autonomous Steering:</strong> Fish use a wander behavior (random angle perturbations) and boundary avoidance forces. If the fish gets too close to a wall, a steering force is applied to turn it back toward the center.</li>
            <li><strong>Visual Polish:</strong>
                <ul>
                    <li>Fish rotate graphics to face movement direction.</li>
                    <li>Tail wiggling uses a sine wave phase accumulator.</li>
                    <li>Background includes a gradient and waving seaweed for depth.</li>
                    <li>Mouse interaction creates a "pressure wave" effect, simulating a predator or hand entering the water.</li>
                </ul>
            </li>
            <li><strong>Boundary Clamping:</strong> A hard clamp is applied after physics updates to ensure fish never get stuck outside the canvas if delta time is very large (frame drop).</li>
        </ul>
    </section>
</body>
</html>
```

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: Qwen3-Coder-Next-UD-Q2_K_XL.gguf -->
<!-- Prompt: aquarium.md -->
<!-- Time: 49.13s -->
<!-- Fallback: False -->