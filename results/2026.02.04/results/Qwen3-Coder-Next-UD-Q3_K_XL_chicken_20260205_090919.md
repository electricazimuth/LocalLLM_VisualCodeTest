Here is the complete simulation solution. It includes the HTML structure, CSS styling, and the JavaScript logic implementing the Chicken AI, Egg management, and Canvas rendering.

```html
<!DOCTYPE html>
<html>
<head>
    <title>Happy Mrs. Chicken Simulation</title>
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            margin: 10px; 
            overflow: hidden; 
            background-color: #eee; 
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        canvas { 
            display: block; 
            margin: 20px auto; 
            border: 3px solid #555; 
            box-shadow: 0 10px 20px rgba(0,0,0,0.2);
            background-color: #8fbc8f; /* Darker green grass */
            cursor: crosshair;
        }
        #ui-container {
            text-align: center;
            color: #444;
            background: rgba(255,255,255,0.8);
            padding: 10px;
            border-radius: 8px;
            max-width: 512px;
        }
        h1 { margin: 0 0 5px 0; color: #333; }
        p { margin: 5px 0; font-size: 0.9rem; }
        .stat-box { font-weight: bold; color: #d32f2f; }
    </style>
</head>
<body>
    <div id="ui-container">
        <h1>Happy Mrs. Chicken Simulation</h1>
        <p>Current State: <span id="chickenState" class="stat-box">Wandering</span></p>
        <p>Eggs on Ground: <span id="eggCount" class="stat-box">0</span></p>
        <p><em>The chicken wanders freely, changes direction at boundaries, and periodically lays eggs.</em></p>
    </div>

    <canvas id="simulationCanvas" width="512" height="512"></canvas>

    <section id="notes">
        <h3>Implementation Notes</h3>
        <ul>
            <li><strong>Game Loop:</strong> Uses <code>requestAnimationFrame</code> with Delta Time calculation to ensure movement speed is consistent regardless of frame rate.</li>
            <li><strong>AI Behavior:</strong> The chicken has a "Wandering" state. It moves in a straight line until it hits a boundary or randomly decides to change direction (wander).</li>
            <li><strong>State Machine:</strong> The chicken transitions between <code>WANDERING</code> and <code>LAYING</code>. The laying state pauses movement and triggers a visual animation.</li>
            <li><strong>Object Management:</strong> Eggs are stored in an array. They are static objects that remain on the canvas. For this simulation, eggs persist forever to demonstrate accumulation, but a cleanup timer could be added.</li>
            <li><strong>Rendering:</strong> The chicken is drawn using arcs and paths. Its rotation is calculated using <code>Math.atan2</code> to face its velocity vector.</li>
        </ul>
    </section>

    <script>
        // --- Configuration Constants ---
        const CONFIG = {
            chickenSpeed: 100, // pixels per second
            chickenSize: 20,   // radius
            layDuration: 1.5,  // seconds the chicken stays in one spot to lay
            layProbability: 0.008, // chance per second to decide to lay (approx every 1-2 minutes usually)
            wanderProbability: 0.02, // chance per second to pick a new random direction
            eggColor: '#fdf5e6', // Old Lace
            chickenColor: '#ffffff',
            combColor: '#dc143c', // Crimson
            beakColor: '#ffa500', // Orange
            legColor: '#ffa500'
        };

        // --- Egg Class ---
        class Egg {
            constructor(x, y) {
                this.x = x;
                this.y = y;
                this.width = 12;
                this.height = 16;
                this.rotation = Math.random() * Math.PI * 2;
                // Random slight variation in size
                this.scale = 0.9 + Math.random() * 0.2;
                
                // Visual texture: slightly speckled
                this.speckles = [];
                const numSpeckles = Math.floor(Math.random() * 5) + 2;
                for(let i=0; i<numSpeckles; i++) {
                    this.speckles.push({
                        x: (Math.random() - 0.5) * 8,
                        y: (Math.random() - 0.5) * 10,
                        size: Math.random() * 1.5
                    });
                }
            }

            draw(ctx) {
                ctx.save();
                ctx.translate(this.x, this.y);
                ctx.rotate(this.rotation);
                ctx.scale(this.scale, this.scale);

                // Draw Egg Shape
                ctx.beginPath();
                ctx.fillStyle = this.eggColor;
                ctx.strokeStyle = '#eee';
                ctx.lineWidth = 1;
                
                // Create an oval path
                ctx.ellipse(0, 0, this.width / 2, this.height / 2, 0, 0, Math.PI * 2);
                ctx.fill();
                ctx.stroke();

                // Draw Speckles
                ctx.fillStyle = '#dcd0c0';
                this.speckles.forEach(speckle => {
                    ctx.beginPath();
                    ctx.arc(speckle.x, speckle.y, speckle.size, 0, Math.PI * 2);
                    ctx.fill();
                });

                ctx.restore();
            }
        }

        // --- Chicken Class ---
        class Chicken {
            constructor(x, y) {
                this.x = x;
                this.y = y;
                this.radius = CONFIG.chickenSize;
                
                // Movement properties
                this.angle = -Math.PI / 2; // Start facing up
                this.velocityX = Math.cos(this.angle) * CONFIG.chickenSpeed;
                this.velocityY = Math.sin(this.angle) * CONFIG.chickenSpeed;
                
                // State properties
                this.state = 'WANDERING'; // 'WANDERING', 'LAYING'
                this.stateTimer = 0;
                this.eggsLaidCount = 0;
            }

            update(dt, canvasWidth, canvasHeight, eggsArray) {
                // 1. Determine State Logic
                if (this.state === 'WANDERING') {
                    // Randomly decide to change direction (Wander)
                    if (Math.random() < CONFIG.wanderProbability) {
                        this.setRandomDirection();
                    }

                    // Randomly decide to lay an egg
                    if (Math.random() < CONFIG.layProbability) {
                        this.state = 'LAYING';
                        this.stateTimer = 0;
                        return; // Skip movement calculation this frame
                    }

                    // Move
                    this.x += this.velocityX * dt;
                    this.y += this.velocityY * dt;

                } else if (this.state === 'LAYING') {
                    // Increment timer for laying action
                    this.stateTimer += dt;

                    // If laying time is up, resume wandering
                    if (this.stateTimer >= CONFIG.layDuration) {
                        this.state = 'WANDERING';
                        this.setRandomDirection(); // Pick a new direction after laying
                    }
                    
                    // Do not move during laying
                    return; 
                }

                // 2. Boundary Handling (Bounce)
                if (this.x - this.radius < 0) {
                    this.x = this.radius;
                    this.velocityX = -this.velocityX;
                } else if (this.x + this.radius > canvasWidth) {
                    this.x = canvasWidth - this.radius;
                    this.velocityX = -this.velocityX;
                }

                if (this.y - this.radius < 0) {
                    this.y = this.radius;
                    this.velocityY = -this.velocityY;
                } else if (this.y + this.radius > canvasHeight) {
                    this.y = canvasHeight - this.radius;
                    this.velocityY = -this.velocityY;
                }
            }

            setRandomDirection() {
                // Random angle between 0 and 2PI
                this.angle = Math.random() * Math.PI * 2;
                this.velocityX = Math.cos(this.angle) * CONFIG.chickenSpeed;
                this.velocityY = Math.sin(this.angle) * CONFIG.chickenSpeed;
            }

            layEgg(eggsArray) {
                if (this.state === 'LAYING') {
                    // Create egg slightly behind the center based on current angle
                    // Offset by radius + 5 pixels
                    const eggOffset = this.radius + 5;
                    const eggX = this.x + Math.cos(this.angle) * eggOffset;
                    const eggY = this.y + Math.sin(this.angle) * eggOffset;

                    const newEgg = new Egg(eggX, eggY);
                    eggsArray.push(newEgg);
                    this.eggsLaidCount++;
                    return true;
                }
                return false;
            }

            draw(ctx) {
                ctx.save();
                ctx.translate(this.x, this.y);
                ctx.rotate(this.angle);

                // Shadow
                ctx.fillStyle = 'rgba(0,0,0,0.2)';
                ctx.beginPath();
                ctx.ellipse(0, 5, this.radius, this.radius * 0.8, 0, 0, Math.PI * 2);
                ctx.fill();

                // Legs (Back)
                ctx.strokeStyle = CONFIG.legColor;
                ctx.lineWidth = 3;
                ctx.beginPath();
                ctx.moveTo(-5, this.radius - 2);
                ctx.lineTo(-5, this.radius + 8);
                ctx.moveTo(5, this.radius - 2);
                ctx.lineTo(5, this.radius + 8);
                ctx.stroke();

                // Body
                ctx.fillStyle = CONFIG.chickenColor;
                ctx.beginPath();
                ctx.arc(0, 0, this.radius, 0, Math.PI * 2);
                ctx.fill();
                
                // Body Outline
                ctx.strokeStyle = '#ddd';
                ctx.lineWidth = 2;
                ctx.stroke();

                // Comb (Red thing on head)
                ctx.fillStyle = CONFIG.combColor;
                ctx.beginPath();
                ctx.arc(0, -10, 6, 0, Math.PI * 2);
                ctx.arc(6, -8, 5, 0, Math.PI * 2);
                ctx.arc(-6, -8, 5, 0, Math.PI * 2);
                ctx.fill();

                // Beak
                ctx.fillStyle = CONFIG.beakColor;
                ctx.beginPath();
                ctx.moveTo(this.radius - 5, 0);
                ctx.lineTo(this.radius + 10, 5);
                ctx.lineTo(this.radius - 5, 10);
                ctx.fill();
                ctx.stroke();

                // Eye
                ctx.fillStyle = '#000';
                ctx.beginPath();
                ctx.arc(5, -5, 2, 0, Math.PI * 2);
                ctx.fill();

                // Wings
                ctx.fillStyle = '#f0f0f0';
                ctx.beginPath();
                // Left Wing
                ctx.ellipse(-10, 5, 8, 5, Math.PI / 4, 0, Math.PI * 2);
                // Right Wing
                ctx.ellipse(-10, -5, 8, 5, -Math.PI / 4, 0, Math.PI * 2);
                ctx.fill();
                ctx.stroke();

                // Laying Visual Cue
                if (this.state === 'LAYING') {
                    // Visual indicator that chicken is doing something special
                    ctx.strokeStyle = 'rgba(255, 0, 0, 0.5)';
                    ctx.lineWidth = 2;
                    ctx.beginPath();
                    ctx.arc(0, 0, this.radius + 5, 0, Math.PI * 2);
                    ctx.stroke();

                    // Plop animation text
                    const pulse = Math.sin(this.stateTimer * 5) * 5;
                    ctx.fillStyle = '#333';
                    ctx.font = '10px Arial';
                    ctx.textAlign = 'center';
                    ctx.fillText("Plop!", 0, this.radius + 15 + pulse);
                }

                ctx.restore();
            }
        }

        // --- Main Simulation Logic ---
        const canvas = document.getElementById('simulationCanvas');
        const ctx = canvas.getContext('2d');
        const stateDisplay = document.getElementById('chickenState');
        const eggDisplay = document.getElementById('eggCount');

        // Initialize Objects
        const chicken = new Chicken(canvas.width / 2, canvas.height / 2);
        const eggs = [];

        // Helper to update UI
        function updateUI() {
            stateDisplay.textContent = chicken.state + (chicken.state === 'LAYING' ? ` (${(CONFIG.layDuration - chicken.stateTimer).toFixed(1)}s)` : '');
            eggDisplay.textContent = eggs.length;
        }

        // Main Loop
        let lastTime = 0;

        function gameLoop(timestamp) {
            // Calculate Delta Time (in seconds)
            if (!lastTime) lastTime = timestamp;
            const dt = (timestamp - lastTime) / 1000;
            lastTime = timestamp;

            // 1. Update Logic
            chicken.update(dt, canvas.width, canvas.height, eggs);

            // Check if we should spawn an egg during this frame
            if (chicken.layEgg(eggs)) {
                // Logic handled inside update, but we can trigger specific UI updates here if needed
            }

            // 2. Draw Logic
            // Clear Canvas
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // Draw Background Pattern (Simple Grass Blades)
            ctx.fillStyle = '#8fbc8f';
            ctx.fillRect(0,0, canvas.width, canvas.height);
            
            ctx.strokeStyle = '#7ab97a';
            ctx.lineWidth = 2;
            for(let i=0; i<canvas.width; i+=20) {
                for(let j=0; j<canvas.height; j+=20) {
                    if ((i+j)%3 === 0) {
                        ctx.beginPath();
                        ctx.moveTo(i, j);
                        ctx.lineTo(i+5, j+5);
                        ctx.stroke();
                    }
                }
            }

            // Draw Eggs
            eggs.forEach(egg => egg.draw(ctx));

            // Draw Chicken
            chicken.draw(ctx);

            // Update UI
            updateUI();

            // Request next frame
            requestAnimationFrame(gameLoop);
        }

        // Start the simulation
        requestAnimationFrame(gameLoop);

    </script>
</body>
</html>
```

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: Qwen3-Coder-Next-UD-Q3_K_XL.gguf -->
<!-- Prompt: chicken.md -->
<!-- Time: 49.28s -->
<!-- Fallback: False -->