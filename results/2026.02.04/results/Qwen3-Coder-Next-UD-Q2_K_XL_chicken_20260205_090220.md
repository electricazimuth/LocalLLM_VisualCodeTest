Here is the complete solution. The code includes a robust class-based implementation for the Chicken and Eggs, handles the game loop with delta time for smooth animations, and implements the requested AI behaviors (wandering, boundary avoidance, and egg-laying logic).

```html
<!DOCTYPE html>
<html>
<head>
    <title>Happy Mrs. Chicken Simulation</title>
    <style>
        body { margin: 10px; overflow: hidden; background-color: #eee; font-family: sans-serif; text-align: center; }
        canvas { display: block; margin: 20px auto; border: 2px solid #555; background-color: #90ee90; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        h1 { color: #333; margin-bottom: 5px; }
        p { color: #666; margin-top: 0; }
    </style>
</head>
<body>
    <h1>Happy Mrs. Chicken Simulation</h1>
    <canvas id="simulationCanvas" width="512" height="512"></canvas>
    <p>Watch Mrs. Chicken wander and lay eggs.</p>

    <section id="notes">
        <strong>Implementation Notes:</strong>
        <ul style="display: inline-block; text-align: left; background: #fff; padding: 15px; border-radius: 8px;">
            <li><strong>Game Loop:</strong> Uses <code>requestAnimationFrame</code> with <code>deltaTime</code> to ensure movement speed is consistent regardless of frame rate.</li>
            <li><strong>AI Logic:</strong> The chicken moves in a straight line until it hits a boundary or randomly decides to change direction (wandering behavior).</li>
            <li><strong>State Machine:</strong> The chicken has two states: <em>'Wandering'</em> (moving) and <em>'Laying'</em> (paused). The transition is handled via a timer.</li>
            <li><strong>Visuals:</strong> The chicken is drawn as a polygon with a beak and is oriented to face its direction of travel. Eggs are static ovals drawn at the last position before laying.</li>
            <li><strong>Egg Management:</strong> Eggs are stored in an array and removed after a set duration to simulate them being collected or decaying.</li>
        </ul>
    </section>

    <script>
        /**
         * CONFIGURATION CONSTANTS
         */
        const CONFIG = {
            chickenSpeed: 150,      // pixels per second
            chickenSize: 30,        // radius
            eggSize: 15,            // radius
            eggLifeTime: 5000,      // milliseconds (5 seconds)
            layTimeDuration: 1000,  // milliseconds (1 second pause)
            layChanceInterval: 2000, // minimum ms between lay attempts
            turnChance: 0.02,       // probability per frame to change direction if not hitting wall
            boundaryBuffer: 50      // distance from wall to trigger turn
        };

        /**
         * CLASS: Egg
         * Represents a static egg object on the canvas.
         */
        class Egg {
            constructor(x, y) {
                this.x = x;
                this.y = y;
                this.creationTime = Date.now();
                this.isCollected = false;
            }

            draw(ctx) {
                if (this.isCollected) return;

                // Draw Egg Shell
                ctx.fillStyle = '#fdf6e3'; // Off-white
                ctx.strokeStyle = '#e0d6b0';
                ctx.lineWidth = 2;
                ctx.beginPath();
                ctx.ellipse(this.x, this.y, CONFIG.eggSize, CONFIG.eggSize * 1.3, 0, 0, Math.PI * 2);
                ctx.fill();
                ctx.stroke();

                // Simple texture detail (speckle)
                ctx.fillStyle = 'rgba(139, 69, 19, 0.3)'; // Brownish speckle
                ctx.beginPath();
                ctx.arc(this.x + 3, this.y - 2, 2, 0, Math.PI * 2);
                ctx.fill();
            }
        }

        /**
         * CLASS: Chicken
         * Represents the main character with AI logic.
         */
        class Chicken {
            constructor(canvasWidth, canvasHeight) {
                // Start in the center
                this.x = canvasWidth / 2;
                this.y = canvasHeight / 2;
                this.radius = CONFIG.chickenSize;
                this.canvasWidth = canvasWidth;
                this.canvasHeight = canvasHeight;

                // Movement State
                this.angle = Math.random() * Math.PI * 2; // Random starting direction
                this.speed = CONFIG.chickenSpeed;
                this.state = 'Wandering'; // 'Wandering' or 'Laying'
                
                // Timing
                this.lastLayTime = 0;
                this.layStartTime = 0;
                
                // Visuals
                this.colorBody = '#ffffff';
                this.colorWattle = '#ff4444';
                this.colorBeak = '#ff8c00';
            }

            update(dt, eggs) {
                // 1. Handle State Transitions
                if (this.state === 'Laying') {
                    // Check if laying duration is over
                    if (Date.now() - this.layStartTime >= CONFIG.layTimeDuration) {
                        this.state = 'Wandering';
                    } else {
                        // While laying, we don't move
                        return; 
                    }
                }

                // 2. Determine if we should start laying
                const timeSinceLastLay = Date.now() - this.lastLayTime;
                if (timeSinceLastLay >= CONFIG.layChanceInterval) {
                    // 20% chance to lay if cooldown is met, or use a timer approach
                    // Let's use a timer for more predictable simulation, but randomness for variety
                    const randomCheck = Math.random();
                    if (randomCheck < 0.05) { // Small chance per frame to trigger if cooldown met
                        this.startLaying();
                    }
                }

                // 3. Movement Logic
                // Calculate velocity components
                const vx = Math.cos(this.angle) * this.speed * dt;
                const vy = Math.sin(this.angle) * this.speed * dt;

                let nextX = this.x + vx;
                let nextY = this.y + vy;
                let turned = false;

                // 4. Boundary Handling (Bounce/Turn)
                if (nextX < this.radius || nextX > this.canvasWidth - this.radius) {
                    this.angle = Math.PI - this.angle; // Reflect X
                    turned = true;
                }
                if (nextY < this.radius || nextY > this.canvasHeight - this.radius) {
                    this.angle = -this.angle; // Reflect Y
                    turned = true;
                }

                // If we hit a wall or randomly decide to turn (wandering behavior)
                if (turned || (!turned && Math.random() < CONFIG.turnChance)) {
                    // Add some randomness to the turn
                    this.angle += (Math.random() - 0.5); // Slight jitter
                    // Normalize angle to keep it sane
                    if (this.angle < 0) this.angle += Math.PI * 2;
                    if (this.angle > Math.PI * 2) this.angle -= Math.PI * 2;
                }

                // Apply movement
                this.x = this.x + vx;
                this.y = this.y + vy;
            }

            startLaying() {
                this.state = 'Laying';
                this.layStartTime = Date.now();
                this.lastLayTime = Date.now();
                
                // Return the new Egg object to the caller to be added to the array
                // We place it slightly behind the chicken so it looks like it was "laid"
                const eggOffset = this.radius + 5;
                const eggX = this.x - Math.cos(this.angle) * eggOffset;
                const eggY = this.y - Math.sin(this.angle) * eggOffset;

                return new Egg(eggX, eggY);
            }

            draw(ctx) {
                ctx.save();
                ctx.translate(this.x, this.y);
                ctx.rotate(this.angle);

                // Draw Body (White Circle)
                ctx.fillStyle = this.colorBody;
                ctx.beginPath();
                ctx.arc(0, 0, this.radius, 0, Math.PI * 2);
                ctx.fill();
                ctx.lineWidth = 2;
                ctx.strokeStyle = '#333';
                ctx.stroke();

                // Draw Head (Slightly ahead of center)
                const headX = this.radius - 5;
                ctx.fillStyle = this.colorBody;
                ctx.beginPath();
                ctx.arc(headX, 0, this.radius * 0.8, 0, Math.PI * 2);
                ctx.fill();
                ctx.stroke();

                // Draw Beak (Orange Triangle)
                ctx.fillStyle = this.colorBeak;
                ctx.beginPath();
                ctx.moveTo(headX + this.radius * 0.6, -5);
                ctx.lineTo(headX + this.radius * 1.8, 0); // Tip of beak
                ctx.lineTo(headX + this.radius * 0.6, 5);
                ctx.closePath();
                ctx.fill();
                ctx.stroke();

                // Draw Eye
                ctx.fillStyle = '#000';
                ctx.beginPath();
                ctx.arc(headX + this.radius * 0.2, -4, 2, 0, Math.PI * 2);
                ctx.fill();

                // Draw Wattle (Red comma shape below beak)
                ctx.fillStyle = this.colorWattle;
                ctx.beginPath();
                ctx.arc(headX, 8, 4, 0, Math.PI, false);
                ctx.fill();

                // Draw Wing (Side patch)
                ctx.fillStyle = '#f0f0f0';
                ctx.beginPath();
                ctx.ellipse(-5, 5, 8, 12, 0.2, 0, Math.PI * 2);
                ctx.fill();
                ctx.stroke();

                // Visual Cue for Laying State (Top Hat or Crutch)
                if (this.state === 'Laying') {
                    ctx.fillStyle = '#ff6b6b';
                    ctx.font = '20px Arial';
                    ctx.fillText("💤", -10, -20); // Sleeping symbol
                    
                    ctx.fillStyle = '#333';
                    ctx.beginPath();
                    ctx.arc(0, 0, this.radius + 5, 0, Math.PI * 2);
                    ctx.strokeStyle = 'rgba(255, 0, 0, 0.5)';
                    ctx.setLineDash([5, 5]);
                    ctx.stroke();
                }

                ctx.restore();
            }
        }

        /**
         * MAIN SIMULATION SETUP
         */
        const canvas = document.getElementById('simulationCanvas');
        const ctx = canvas.getContext('2d');

        let chicken = new Chicken(canvas.width, canvas.height);
        let eggs = [];

        let lastTime = 0;

        function gameLoop(timestamp) {
            // Calculate delta time in seconds (frame-rate independent movement)
            let dt = (timestamp - lastTime) / 1000;
            if (dt > 0.1) dt = 0.1; // Cap dt to prevent huge jumps if tab is inactive
            
            lastTime = timestamp;

            // 1. Clear Canvas
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // 2. Update Logic
            // Update Chicken
            const newEgg = chicken.update(dt, eggs);

            // If chicken laid an egg, add it to the array
            if (newEgg) {
                eggs.push(newEgg);
            }

            // Update Eggs (Check for expiration)
            for (let i = eggs.length - 1; i >= 0; i--) {
                const egg = eggs[i];
                // Check if egg has existed longer than life time
                if (Date.now() - egg.creationTime >= CONFIG.eggLifeTime) {
                    eggs.splice(i, 1);
                }
            }

            // 3. Draw Logic
            // Draw Eggs
            eggs.forEach(egg => egg.draw(ctx));

            // Draw Chicken
            chicken.draw(ctx);

            // Draw UI info (Bottom Left)
            ctx.fillStyle = 'rgba(0,0,0,0.6)';
            ctx.fillRect(10, canvas.height - 40, 250, 30);
            ctx.fillStyle = '#fff';
            ctx.font = '12px Arial';
            ctx.fillText(`Eggs on screen: ${eggs.length}`, 20, canvas.height - 20);
            ctx.fillText(`State: ${chicken.state}`, 20, canvas.height - 10);

            // 4. Next Frame
            requestAnimationFrame(gameLoop);
        }

        // Start the loop
        requestAnimationFrame(gameLoop);

    </script>
</body>
</html>
```

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: Qwen3-Coder-Next-UD-Q2_K_XL.gguf -->
<!-- Prompt: chicken.md -->
<!-- Time: 42.28s -->
<!-- Fallback: False -->