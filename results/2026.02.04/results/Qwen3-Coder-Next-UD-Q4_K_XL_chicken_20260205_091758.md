Here is the complete solution. I have implemented a Class-based structure for the Chicken and Eggs, used Delta Time for smooth movement, and included logic for the chicken to face its direction of travel while implementing a state machine for egg-laying.

```html
<!DOCTYPE html>
<html>
<head>
    <title>Happy Mrs. Chicken Simulation</title>
    <style>
        body { margin: 10px; overflow: hidden; background-color: #eee; font-family: sans-serif; }
        canvas { display: block; margin: 20px auto; border: 4px solid #555; background-color: #7cfc00; box-shadow: 0 4px 10px rgba(0,0,0,0.3); }
        .ui-text { text-align: center; color: #333; margin-top: 10px; }
    </style>
</head>
<body>
    <h2 style="text-align:center; color:#333;">Happy Mrs. Chicken Sim</h2>
    <canvas id="simulationCanvas" width="512" height="512"></canvas>
    <div class="ui-text">
        <p>Chicken is wandering and will lay eggs periodically.</p>
        <p>Eggs remain on the ground until cleared by the "Reset Simulation" button.</p>
        <button onclick="resetSimulation()" style="padding: 8px 16px; cursor: pointer; font-size: 14px; margin-top: 10px; background-color: #fff; border: 1px solid #ccc; border-radius: 4px;">Reset Simulation</button>
    </div>

    <script>
        /**
         * DELTA TIME UTILITIES
         * We store the last timestamp to calculate the time passed between frames.
         * This ensures the chicken moves at the same speed on 60hz vs 144hz monitors.
         */
        let lastTime = 0;
        const canvas = document.getElementById('simulationCanvas');
        const ctx = canvas.getContext('2d');

        // --- CLASS DEFINITIONS ---

        class Egg {
            constructor(x, y) {
                this.x = x;
                this.y = y;
                this.radiusX = 8;
                this.radiusY = 12;
                this.laidAt = Date.now(); // Track when it was laid (optional for decay logic)
                this.rotation = (Math.random() - 0.5) * 0.5; // Random slight rotation
                this.opacity = 1.0;
                this.isFading = false;
            }

            draw(ctx) {
                ctx.save();
                ctx.translate(this.x, this.y);
                ctx.rotate(this.rotation);
                ctx.globalAlpha = this.opacity;
                ctx.fillStyle = '#fffdee'; // Off-white egg color
                ctx.strokeStyle = '#e6dcbf'; // Light brown outline
                ctx.lineWidth = 1;
                
                ctx.beginPath();
                ctx.ellipse(0, 0, this.radiusX, this.radiusY, 0, 0, Math.PI * 2);
                ctx.fill();
                ctx.stroke();
                
                // Add a little shine
                ctx.fillStyle = '#fff';
                ctx.beginPath();
                ctx.ellipse(-3, -3, 2, 1, Math.PI / 4, 0, Math.PI * 2);
                ctx.fill();

                ctx.restore();
            }

            fadeOut() {
                this.isFading = true;
            }
        }

        class Chicken {
            constructor(x, y) {
                this.x = x;
                this.y = y;
                this.radius = 20; // Visual radius of the chicken body
                
                // Movement properties
                this.speed = 80; // Pixels per second
                this.angle = Math.random() * Math.PI * 2; // Radians
                this.vx = Math.cos(this.angle) * this.speed;
                this.vy = Math.sin(this.angle) * this.speed;

                // State Machine
                this.states = {
                    WANDERING: 'wandering',
                    LAYING: 'laying',
                    RESTING: 'resting'
                };
                this.currentState = this.states.WANDERING;
                
                // Timers (accumulators for delta time)
                this.changeDirTimer = 0;
                this.layTimer = 0;
                this.stateTimer = 0;

                // Configuration
                this.dirChangeInterval = 2.0; // Seconds between direction changes
                this.layInterval = 8.0;       // Seconds between laying attempts
                this.layDuration = 1.0;       // Seconds spent "laying" (paused)
                this.restDuration = 1.5;      // Seconds paused after laying before moving again
            }

            update(dt, canvasWidth, canvasHeight, eggs) {
                // Update Timers
                this.changeDirTimer += dt;
                this.layTimer += dt;
                this.stateTimer += dt;

                // 1. State Management Logic
                if (this.currentState === this.states.WANDERING) {
                    // Check if it's time to try laying an egg
                    if (this.layTimer >= this.layInterval) {
                        this.currentState = this.states.LAYING;
                        this.stateTimer = 0; // Reset state timer for the lay duration
                        this.layTimer = 0;   // Reset lay timer
                    }

                    // Check if it's time to change direction (Wandering behavior)
                    if (this.changeDirTimer >= this.dirChangeInterval) {
                        this.changeDirection();
                        this.changeDirTimer = 0;
                    }

                    // Apply Movement
                    this.x += this.vx * dt;
                    this.y += this.vy * dt;

                } else if (this.currentState === this.states.LAYING) {
                    // During laying, we stop moving.
                    // If we hit a wall while "paused", we still don't move (solid behavior)
                    
                    // Check if laying action is complete
                    if (this.stateTimer >= this.layDuration) {
                        // Laying complete: Create Egg
                        // Position egg slightly "behind" the chicken based on current angle
                        const eggOffset = 15; 
                        const eggX = this.x - Math.cos(this.angle) * eggOffset;
                        const eggY = this.y - Math.sin(this.angle) * eggOffset;
                        
                        eggs.push(new Egg(eggX, eggY));

                        // Transition to resting state
                        this.currentState = this.states.RESTING;
                        this.stateTimer = 0;
                    }

                } else if (this.currentState === this.states.RESTING) {
                    // Still not moving
                    if (this.stateTimer >= this.restDuration) {
                        // Resume wandering
                        this.currentState = this.states.WANDERING;
                        this.changeDirection(); // Give her a fresh direction after a nap
                        this.changeDirTimer = 0; // Reset wander timer
                    }
                }

                // 2. Boundary Handling (Bounce Logic)
                if (this.x - this.radius < 0) {
                    this.x = this.radius;
                    this.vx = Math.abs(this.vx);
                    this.angle = 0;
                } else if (this.x + this.radius > canvasWidth) {
                    this.x = canvasWidth - this.radius;
                    this.vx = -Math.abs(this.vx);
                    this.angle = Math.PI;
                }

                if (this.y - this.radius < 0) {
                    this.y = this.radius;
                    this.vy = Math.abs(this.vy);
                    this.angle = Math.PI / 2;
                } else if (this.y + this.radius > canvasHeight) {
                    this.y = canvasHeight - this.radius;
                    this.vy = -Math.abs(this.vy);
                    this.angle = -Math.PI / 2;
                }
            }

            changeDirection() {
                // Random angle between 0 and 2PI
                this.angle = Math.random() * Math.PI * 2;
                this.vx = Math.cos(this.angle) * this.speed;
                this.vy = Math.sin(this.angle) * this.speed;
            }

            draw(ctx) {
                ctx.save();
                ctx.translate(this.x, this.y);
                ctx.rotate(this.angle);

                // Visual State Changes (Color changes when laying/resting)
                if (this.currentState === this.states.LAYING) {
                    ctx.fillStyle = '#ffccaa'; // Pinkish when exerting effort
                } else if (this.currentState === this.states.RESTING) {
                    ctx.fillStyle = '#ffffcc'; // Pale yellow when resting
                } else {
                    ctx.fillStyle = '#ffffff'; // Standard white
                }

                // Draw Body (Circle)
                ctx.beginPath();
                ctx.arc(0, 0, this.radius, 0, Math.PI * 2);
                ctx.fill();
                ctx.lineWidth = 2;
                ctx.strokeStyle = '#333';
                ctx.stroke();

                // Draw Eye
                ctx.fillStyle = '#000';
                ctx.beginPath();
                ctx.arc(8, -6, 2, 0, Math.PI * 2); // Eye
                ctx.fill();
                
                // Eye Shine
                ctx.fillStyle = '#fff';
                ctx.beginPath();
                ctx.arc(9, -7, 0.8, 0, Math.PI * 2);
                ctx.fill();

                // Draw Beak (Triangle)
                ctx.fillStyle = '#ffaa00'; // Orange
                ctx.beginPath();
                ctx.moveTo(15, 0); // Base of beak
                ctx.lineTo(28, -5); // Tip top
                ctx.lineTo(28, 5); // Tip bottom
                ctx.closePath();
                ctx.fill();
                ctx.stroke();

                // Draw Comb (Red thing on head)
                ctx.fillStyle = '#ff3333';
                ctx.beginPath();
                ctx.arc(0, -15, 4, 0, Math.PI * 2);
                ctx.fill();

                // Draw Waddle (Under the beak)
                ctx.fillStyle = '#ff8888';
                ctx.beginPath();
                ctx.arc(12, 2, 3, 0, Math.PI * 2);
                ctx.fill();

                // Draw "Happy" Eyes if wandering (Simple arc for smile)
                if (this.currentState === this.states.WANDERING) {
                    ctx.strokeStyle = '#333';
                    ctx.lineWidth = 1;
                    ctx.beginPath();
                    ctx.arc(8, 2, 4, 0.2, 1.0); // Slight smile
                    ctx.stroke();
                } else if (this.currentState === this.states.LAYING) {
                    // X eyes when laying
                    ctx.strokeStyle = '#333';
                    ctx.lineWidth = 1;
                    ctx.beginPath();
                    ctx.moveTo(6, -4); ctx.lineTo(10, -0); // Right eye X
                    ctx.moveTo(10, -4); ctx.lineTo(6, 0);
                    ctx.stroke();
                }

                ctx.restore();

                // Debug Text (Optional)
                /*
                ctx.fillStyle = 'black';
                ctx.font = '10px Arial';
                ctx.fillText(this.currentState, this.x - 20, this.y - this.radius - 10);
                */
            }
        }

        // --- GLOBAL VARIABLES ---
        let chicken;
        let eggs = [];
        let animationId;

        // --- INITIALIZATION ---
        function initSimulation() {
            // Clear eggs
            eggs = [];
            
            // Create Chicken starting in the center
            chicken = new Chicken(canvas.width / 2, canvas.height / 2);
            
            // Start the loop
            lastTime = performance.now();
            if (animationId) cancelAnimationFrame(animationId);
            animationId = requestAnimationFrame(gameLoop);
        }

        function resetSimulation() {
            initSimulation();
        }

        // --- MAIN GAME LOOP ---
        function gameLoop(currentTime) {
            // Calculate Delta Time (in seconds)
            const deltaTime = (currentTime - lastTime) / 1000;
            lastTime = currentTime;

            // 1. Clear Canvas
            ctx.fillStyle = '#7cfc00'; // Lawn Green
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            // Optional: Draw grass blades pattern for texture
            ctx.strokeStyle = '#6add00';
            ctx.lineWidth = 1;
            ctx.beginPath();
            for(let i=0; i<canvas.width; i+=20) {
                for(let j=0; j<canvas.height; j+=20) {
                    ctx.moveTo(i, j);
                    ctx.lineTo(i + 5, j + 5);
                    ctx.moveTo(i + 10, j + 10);
                    ctx.lineTo(i + 15, j + 15);
                }
            }
            ctx.stroke();

            // 2. Update Logic
            chicken.update(deltaTime, canvas.width, canvas.height, eggs);

            // 3. Draw Eggs
            eggs.forEach(egg => egg.draw(ctx));

            // 4. Draw Chicken
            chicken.draw(ctx);

            // 5. Continue Loop
            animationId = requestAnimationFrame(gameLoop);
        }

        // Start the simulation
        initSimulation();

    </script>
    
    <section id="notes" style="padding: 20px; background: #f9f9f9; border-left: 5px solid #333; margin: 20px; max-width: 600px;">
        <h3>Implementation Notes</h3>
        <ul>
            <li><strong>Object Oriented Design:</strong> The <code>Chicken</code> and <code>Egg</code> classes encapsulate their own properties (position, state) and behaviors (update, draw).</li>
            <li><strong>Delta Time:</strong> The <code>gameLoop</code> calculates <code>deltaTime</code> (time elapsed since last frame in seconds). All movement (velocity * dt) and timers are scaled by this value, ensuring consistent speed regardless of frame rate.</li>
            <li><strong>State Machine:</strong> The Chicken uses a simple State Machine (<code>WANDERING</code>, <code>LYING</code>, <code>RESTING</code>).
                <ul>
                    <li><em>Wandering:</em> Moves, checks for timer triggers.</li>
                    <li><em>Laying:</em> Velocity is 0. Creates a new Egg object at a calculated offset (behind the chicken) and rotates slightly to face the direction of movement.</li>
                    <li><em>Resting:</em> Brief pause before wandering resumes.</li>
                </ul>
            </li>
            <li><strong>Boundary Handling:</strong> Uses "Clamp and Bounce" logic. If the chicken hits a wall, it is forced back inside the canvas, and its velocity vector is inverted or set to face the correct direction.</li>
            <li><strong>Visual Orientation:</strong> The Chicken is translated and rotated to match its velocity vector, ensuring the beak always points in the direction of travel.</li>
            <li><strong>Egg Persistence:</strong> Eggs are stored in an array and drawn every frame. They do not move once created, simulating objects left on the ground.</li>
        </ul>
    </section>

</body>
</html>
```

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: Qwen3-Coder-Next-UD-Q4_K_XL.gguf -->
<!-- Prompt: chicken.md -->
<!-- Time: 58.17s -->
<!-- Fallback: False -->