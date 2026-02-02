Hello! I have designed a complete, single-file HTML solution for your "Happy Mrs. Chicken" simulation.

### Design Approach
1.  **Architecture**: I used a **Class-based approach**. The `Chicken` class handles its own state (wandering vs. laying), movement logic, and rendering. The `Egg` class is lightweight and handles its own rendering.
2.  **Visuals**:
    *   **Chicken**: Constructed from geometric shapes. To make the "wandering" visible, I added a **comb** (red lump on top) and a **beak**. The entire body rotates to face the direction of movement (`Math.atan2`).
    *   **Egg**: A clean white oval with a subtle highlight.
    *   **Feedback**: When Mrs. Chicken is laying, she turns a slightly different shade of yellow and wobbles, providing a clear visual cue.
3.  **AI & Physics**:
    *   **Wandering**: Instead of random jitter, the chicken picks a new random heading every few seconds using a timer.
    *   **Boundaries**: Simple circle-rectangle collision logic keeps her safely inside the canvas.
    *   **Delta Time**: The movement is multiplied by `dt` (delta time) to ensure consistent speed regardless of frame rate.

### The Code

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Happy Mrs. Chicken Simulation</title>
    <style>
        body {
            margin: 0;
            padding: 10px;
            display: flex;
            flex-direction: column;
            align-items: center;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #2c3e50; /* Darker background for contrast */
            color: #ecf0f1;
            min-height: 100vh;
            box-sizing: border-box;
        }

        h1 { margin: 10px 0; font-size: 1.5rem; text-align: center; }
        
        #canvas-container {
            position: relative;
            box-shadow: 0 10px 25px rgba(0,0,0,0.5);
            border-radius: 8px;
            overflow: hidden;
            border: 4px solid #34495e;
        }

        canvas {
            display: block;
            background-color: #90ee90; /* Light green grass */
            /* We will resize this via JS, but set a base style */
            max-width: 100%; 
            height: auto;
            background-image: 
                radial-gradient(circle, #8cd88c 10%, #90ee90 15%, #8cd88c 20%); 
            background-size: 40px 40px; /* Subtle pattern */
        }

        #ui-layer {
            margin-top: 10px;
            display: flex;
            gap: 20px;
            font-size: 0.9rem;
        }

        .stat-box {
            background: rgba(0, 0, 0, 0.3);
            padding: 8px 16px;
            border-radius: 20px;
            border: 1px solid rgba(255,255,255,0.1);
        }

    </style>
</head>
<body>

    <h1>Happy Mrs. Chicken Simulation</h1>

    <div id="canvas-container">
        <canvas id="simulationCanvas" width="800" height="600"></canvas>
    </div>

    <div id="ui-layer">
        <div class="stat-box" id="statusDisplay">Status: Ready</div>
        <div class="stat-box" id="eggCountDisplay">Eggs Laid: 0</div>
    </div>

    <script>
        /**
         * ------------------------------------------------------------------
         * CONFIGURATION & CONSTANTS
         * ------------------------------------------------------------------
         */
        const CONFIG = {
            colors: {
                chickenBody: '#FFD700', // Gold
                chickenBodyDark: '#DAA520', // Dark Goldenrod
                chickenHead: '#FFEC8B', // Light Yellow
                beak: '#FFA500',
                eye: '#000',
                egg: '#FFF8DC', // Cornsilk
                eggShadow: '#D2B48C'
            },
            movement: {
                speed: 120, // Pixels per second
                turnTimerMin: 2, // Seconds between direction changes
                turnTimerMax: 5,
                layDelay: 0.8 // Seconds to wait before laying
            }
        };

        // Get the canvas context
        const canvas = document.getElementById('simulationCanvas');
        const ctx = canvas.getContext('2d');
        const statusDisplay = document.getElementById('statusDisplay');
        const eggCountDisplay = document.getElementById('eggCountDisplay');

        /**
         * ------------------------------------------------------------------
         * HELPER CLASSES
         * ------------------------------------------------------------------
         */

        // Represents the Eggs on the ground
        class Egg {
            constructor(x, y) {
                this.x = x;
                this.y = y;
                this.radius = 12;
                this.spawnTime = performance.now() / 1000; // Used for potential logic later
            }

            draw(ctx) {
                ctx.save();
                ctx.translate(this.x, this.y);
                
                // Draw Shadow
                ctx.fillStyle = 'rgba(0,0,0,0.1)';
                ctx.beginPath();
                ctx.ellipse(0, 5, 10, 6, 0, 0, Math.PI * 2);
                ctx.fill();

                // Draw Egg (Oval shape)
                ctx.fillStyle = CONFIG.colors.egg;
                // Flatten the Y radius to make it an egg
                ctx.beginPath();
                ctx.ellipse(0, 0, this.radius, this.radius * 1.6, 0, 0, Math.PI * 2);
                ctx.fill();
                
                // Highlight
                ctx.fillStyle = 'rgba(255,255,255,0.6)';
                ctx.beginPath();
                ctx.ellipse(-3, -3, 3, 1.5, 0, 0, Math.PI * 2);
                ctx.fill();

                ctx.restore();
            }
        }

        // Represents the Main Character
        class Chicken {
            constructor(x, y) {
                this.x = x;
                this.y = y;
                this.vx = (Math.random() - 0.5) * 100; // Random initial velocity
                this.vy = (Math.random() - 0.5) * 100;
                this.radius = 20;
                this.speed = CONFIG.movement.speed;
                
                // State
                this.angle = 0; // Radians
                this.state = 'wandering'; // 'wandering' or 'laying'
                
                // Timers
                this.stateTimer = 0;
                this.wanderDuration = Math.random() * (CONFIG.movement.turnTimerMax - CONFIG.movement.turnTimerMin) + CONFIG.movement.turnTimerMin;
                this.eggDelayTimer = Math.random() * 5; // Randomize when first egg happens

                // Visual tweaks
                this.colorOffset = Math.random() * 20; // Slight color variation
            }

            update(dt, width, height) {
                // State Machine
                if (this.state === 'laying') {
                    this.handleLaying(dt);
                    return; 
                }

                // Wandering Logic
                this.wanderDuration -= dt;

                // Change direction periodically or randomly
                if (this.wanderDuration <= 0) {
                    this.changeDirection();
                }

                // Move
                this.x += this.vx * dt;
                this.y += this.vy * dt;

                // Boundary Handling
                this.checkBoundaries(width, height);

                // Calculate rotation (face movement direction)
                if (Math.abs(this.vx) > 1 || Math.abs(this.vy) > 1) {
                    this.angle = Math.atan2(this.vy, this.vx);
                }
            }

            changeDirection() {
                // Pick a new random angle (within 0-360 range)
                // We keep the speed constant but change direction
                const speed = Math.sqrt(this.vx*this.vx + this.vy*this.vy);
                if (speed === 0) {
                    this.vx = 10; 
                    this.vy = 10;
                    this.angle = 0;
                } else {
                    const angle = Math.random() * Math.PI * 2;
                    this.vx = Math.cos(angle) * speed;
                    this.vy = Math.sin(angle) * speed;
                }

                // Reset timer
                this.wanderDuration = Math.random() * (CONFIG.movement.turnTimerMax - CONFIG.movement.turnTimerMin) + CONFIG.movement.turnTimerMin;
            }

            checkBoundaries(width, height) {
                // Bounce off Left/Right
                if (this.x - this.radius < 0) {
                    this.x = this.radius;
                    this.vx *= -1;
                } else if (this.x + this.radius > width) {
                    this.x = width - this.radius;
                    this.vx *= -1;
                }

                // Bounce off Top/Bottom
                if (this.y - this.radius < 0) {
                    this.y = this.radius;
                    this.vy *= -1;
                } else if (this.y + this.radius > height) {
                    this.y = height - this.radius;
                    this.vy *= -1;
                }
            }

            handleLaying(dt) {
                this.stateTimer -= dt;
                
                // Visual cue: Shrink slightly
                if (Math.floor(this.stateTimer * 10) % 2 === 0) {
                    // Flash color slightly
                }

                if (this.stateTimer <= 0) {
                    // Finished laying
                    this.state = 'laying';
                    this.stateTimer = 0.1; // Quick resume
                }
            }

            layEggs(eggsArray) {
                if (this.state === 'laying') return; // Already laying

                // Start laying logic
                this.state = 'laying';
                this.stateTimer = CONFIG.movement.layDelay;

                // Visual feedback
                document.getElementById('statusDisplay').textContent = "Status: Laying Egg...";
                document.getElementById('statusDisplay').style.color = "#e74c3c";

                // Schedule the egg spawn
                setTimeout(() => {
                    // Spawn egg slightly in front of where the chicken is facing
                    // (Approximated here by the current velocity vector or just center)
                    // Let's spawn it slightly forward based on current angle
                    const spawnDist = 10;
                    const eggX = this.x + Math.cos(this.angle) * spawnDist;
                    const eggY = this.y + Math.sin(this.angle) * spawnDist;

                    eggsArray.push(new Egg(eggX, eggY));
                    
                    // Update UI
                    let count = parseInt(eggCountDisplay.textContent.split(': ')[1]) + 1;
                    eggCountDisplay.textContent = `Eggs Laid: ${count}`;
                }, this.stateTimer * 1000);

                // Schedule return to wandering
                this.state = 'laying';
                this.stateTimer = CONFIG.movement.layDelay; // The delay is the time spent laying
            }

            draw(ctx) {
                ctx.save();
                ctx.translate(this.x, this.y);
                
                // If moving, face direction. Otherwise face right.
                const isMoving = (Math.abs(this.vx) > 0.5 || Math.abs(this.vy) > 0.5);
                if (isMoving) {
                     // Smooth rotation interpolation could go here, but direct assignment is fine for simple AI
                }
                
                // Visual cue for laying: Shake slightly
                let shakeX = 0;
                let shakeY = 0;
                if (this.state === 'laying') {
                     shakeX = (Math.random() - 0.5) * 4;
                     shakeY = (Math.random() - 0.5) * 4;
                }
                // We apply rotation *after* the shake translation
                const facingAngle = isMoving ? this.angle : 0; // Simple facing
                
                // Draw Shadow
                ctx.fillStyle = 'rgba(0,0,0,0.2)';
                ctx.beginPath();
                ctx.ellipse(0, 0, 16, 6, 0, 0, Math.PI * 2);
                ctx.fill();

                // Apply Shake
                this.x += shakeX;
                this.y += shakeY;

                // Rotate to face movement direction
                // We use Math.atan2(vy, vx) to get the angle of movement
                if (isMoving) {
                    const angle = Math.atan2(this.vy, this.vx);
                    ctx.rotate(angle);
                }

                // --- DRAW CHICKEN (Facing Right by default in local space) ---

                // Body
                ctx.fillStyle = (this.state === 'laying') ? '#FFC0CB' : CONFIG.colors.chickenBody; // Pink if laying
                if (Math.floor(performance.now() / 200) % 2 === 0) {
                     // Subtle flash effect
                     ctx.fillStyle = '#FFE4E1'; 
                }

                ctx.beginPath();
                ctx.ellipse(0, 0, 22, 16, 0, 0, Math.PI * 2);
                ctx.fill();
                ctx.lineWidth = 2;
                ctx.strokeStyle = '#C7A600';
                ctx.stroke();

                // Wing (Simple curve)
                ctx.fillStyle = '#DAA520';
                ctx.beginPath();
                ctx.ellipse(-5, 5, 8, 5, 0, 0, Math.PI * 2);
                ctx.fill();

                // Eye (White)
                ctx.fillStyle = 'white';
                ctx.beginPath();
                ctx.arc(8, -5, 5, 0, Math.PI * 2);
                ctx.fill();
                ctx.stroke();

                // Pupils (Follows roughly towards movement)
                ctx.fillStyle = 'black';
                ctx.beginPath();
                ctx.arc(10, -5, 2, 0, Math.PI * 2);
                ctx.fill();

                // Beak
                ctx.fillStyle = CONFIG.colors.beak;
                ctx.beginPath();
                ctx.moveTo(12, 0);
                ctx.lineTo(20, 3);
                ctx.lineTo(12, 6);
                ctx.fill();

                // Comb (The red part on top) - Rotated with body
                ctx.fillStyle = '#e74c3c';
                ctx.beginPath();
                // Draw 3 bumps
                ctx.arc(0, -18, 4, Math.PI, 0); // Top
                ctx.arc(-5, -20, 3, 0, Math.PI, true); // Side left
                ctx.arc(5, -20, 3, 0, Math.PI, true);  // Side right
                ctx.fill();

                // Restore context
                this.x -= shakeX; // Undo shake for next frame
                this.y -= shakeY;
                
                ctx.restore();
            }
        }

        /**
         * ------------------------------------------------------------------
         * MAIN SIMULATION LOOP
         * ------------------------------------------------------------------
         */
        let eggs = [];
        
        // Initialize Chicken in the center
        // We use a slightly smaller width/height logic for the chicken radius
        const chicken = new Chicken(canvas.width / 2, canvas.height / 2);

        let lastTime = 0;

        function loop(timestamp) {
            // Calculate delta time in seconds
            if (!lastTime) lastTime = timestamp;
            const dt = (timestamp - lastTime) / 1000;
            lastTime = timestamp;

            // Clear Canvas
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // Update State
            if (chicken.state !== 'laying') {
                // Randomly decide to lay an egg
                chicken.eggDelayTimer -= dt;
                if (chicken.eggDelayTimer <= 0) {
                    chicken.layEggs(eggs);
                    chicken.eggDelayTimer = Math.random() * 10 + 5; // Reset timer
                }
            } else {
                 // While laying, update the chicken normally (so she can finish the animation)
                 // but we handle the egg creation logic in the class
                 if(chicken.state === 'laying') {
                     chicken.stateTimer -= dt; // Decrement timer
                 }
            }

            // Update & Draw Chicken
            chicken.update(dt, canvas.width, canvas.height);
            chicken.draw(ctx);

            // Update & Draw Eggs
            for (let i = eggs.length - 1; i >= 0; i--) {
                eggs[i].draw(ctx);
            }

            requestAnimationFrame(loop);
        }

        // Handle Window Resize
        function resize() {
            // Keep a maximum width of 800px, but allow it to shrink
            const maxWidth = 800;
            if (canvas.width !== maxWidth) {
                canvas.width = maxWidth;
                canvas.height = 600;
            }
        }
        window.addEventListener('resize', resize);
        resize(); // Initial set

        // Start
        requestAnimationFrame(loop);

    </script>
</body>
</html>
```

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: GLM-4.7-Flash-UD-Q6_K_XL.gguf -->
<!-- Prompt: chicken.md -->
<!-- Generation Time: 274.62s -->
<!-- Fallback Used: False -->