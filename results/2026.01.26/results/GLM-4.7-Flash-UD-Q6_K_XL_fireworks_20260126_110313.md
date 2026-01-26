```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Autonomous Fireworks Particle Simulation</title>
    <style>
        body { 
            margin: 0; 
            overflow: hidden; 
            background-color: #111; 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        canvas { 
            display: block; 
            margin: 0 auto; 
            background-color: #000; 
            box-shadow: 0 0 20px rgba(0,0,0,0.5);
        }
        /* Overlay for instructions */
        #ui-layer {
            position: absolute;
            top: 20px;
            left: 20px;
            color: #888;
            pointer-events: none;
            z-index: 10;
        }
    </style>
</head>
<body>
    <div id="ui-layer">
        <h3>Fireworks Simulation</h3>
        <p>Autonomous launch system active.</p>
        <p>Physics: Gravity, Drag, Alpha Decay</p>
    </div>
    <canvas id="gameCanvas"></canvas>
    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        
        // Responsive Canvas sizing
        function resizeCanvas() {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        }
        window.addEventListener('resize', resizeCanvas);
        resizeCanvas(); // Initial call

        const W = canvas.width;
        const H = canvas.height;

        // --- Configuration Constants ---
        const GRAVITY = 0.05;
        const DRAG = 0.99; // Air resistance
        const PARTICLE_DECAY = 0.015; // How fast particles fade
        
        // --- Class Definitions ---

        /**
         * Represents the rising firework rocket.
         * Travels upwards against gravity until it triggers an explosion.
         */
        class Firework {
            constructor(sx, sy, tx, ty) {
                this.x = sx;
                this.y = sy;
                this.sx = sx; // Start X
                this.sy = sy; // Start Y
                this.tx = tx; // Target X
                this.ty = ty; // Target Y
                
                // Calculate distance to target
                this.distanceToTarget = Math.sqrt(Math.pow(tx - sx, 2) + Math.pow(ty - sy, 2));
                this.distanceTraveled = 0;
                
                // Track previous coordinates for trail effect
                this.coordinates = [];
                this.coordinateCount = 3;
                while (this.coordinateCount--) {
                    this.coordinates.push([this.x, this.y]);
                }
                
                // Calculate angle and velocity
                const angle = Math.atan2(ty - sy, tx - sx);
                // Randomize speed slightly for variety
                const speed = 2 + Math.random() * 2; 
                this.vx = Math.cos(angle) * speed;
                this.vy = Math.sin(angle) * speed;
                
                // Color based on target height (random hue)
                this.hue = Math.floor(Math.random() * 360);
                
                // Autonomous state
                this.exploded = false;
            }

            update(index) {
                // Remove last coordinate, add current
                this.coordinates.pop();
                this.coordinates.unshift([this.x, this.y]);

                // Apply physics
                this.vx *= 1;
                this.vy *= 1;
                this.vy += GRAVITY * 0.5; // Less gravity effect on the rocket itself
                
                this.x += this.vx;
                this.y += this.vy;
                
                // Calculate distance traveled
                const currentDist = Math.sqrt(Math.pow(this.x - this.sx, 2) + Math.pow(this.y - this.sy, 2));

                // Check if target reached (or passed) to explode
                if (currentDist >= this.distanceToTarget) {
                    createParticles(this.tx, this.ty, this.hue);
                    // Remove this firework from main array
                    fireworks.splice(index, 1);
                }
            }

            draw() {
                ctx.beginPath();
                // Draw trail from last coordinate to current
                ctx.moveTo(this.coordinates[this.coordinates.length - 1][0], this.coordinates[this.coordinates.length - 1][1]);
                ctx.lineTo(this.x, this.y);
                ctx.strokeStyle = `hsl(${this.hue}, 100%, 50%)`;
                ctx.lineWidth = 2;
                ctx.stroke();
                
                // Draw head
                ctx.beginPath();
                ctx.arc(this.x, this.y, 2, 0, Math.PI * 2);
                ctx.fillStyle = `hsl(${this.hue}, 100%, 80%)`;
                ctx.fill();
            }
        }

        /**
         * Represents the explosion fragments.
         * Radiate outwards, affected by gravity and drag, fade over time.
         */
        class Particle {
            constructor(x, y, hue) {
                this.x = x;
                this.y = y;
                
                // Trail coordinates
                this.coordinates = [];
                this.coordinateCount = 5;
                while (this.coordinateCount--) {
                    this.coordinates.push([this.x, this.y]);
                }
                
                // Random explosion velocity (circular distribution)
                const angle = Math.random() * Math.PI * 2;
                // Random speed for variety in particle spread
                const speed = Math.random() * 10 + 2; 
                
                this.vx = Math.cos(angle) * speed;
                this.vy = Math.sin(angle) * speed;
                
                this.friction = DRAG;
                this.gravity = GRAVITY;
                
                // Visual properties
                this.hue = hue + Math.random() * 20 - 10; // Slight color variation
                this.brightness = Math.random() * 50 + 50;
                this.alpha = 1;
                this.decay = Math.random() * 0.015 + 0.005; // Random fade speed
            }

            update(index) {
                // Remove last coordinate
                this.coordinates.pop();
                this.coordinates.unshift([this.x, this.y]);
                
                // Physics
                this.vx *= this.friction;
                this.vy *= this.friction;
                this.vy += this.gravity;
                
                this.x += this.vx;
                this.y += this.vy;
                
                // Fade out
                this.alpha -= this.decay;
                
                // Remove dead particles
                if (this.alpha <= this.decay) {
                    particles.splice(index, 1);
                }
            }

            draw() {
                ctx.beginPath();
                ctx.moveTo(this.coordinates[this.coordinates.length - 1][0], this.coordinates[this.coordinates.length - 1][1]);
                ctx.lineTo(this.x, this.y);
                
                // Alpha is handled by globalAlpha or manual calculation
                ctx.strokeStyle = `hsla(${this.hue}, 100%, ${this.brightness}%, ${this.alpha})`;
                ctx.lineWidth = 2; // Thicker trails for impact
                ctx.stroke();
            }
        }

        // --- State Management ---
        
        const fireworks = [];
        const particles = [];
        
        // Autonomous Launch Logic
        let timerTotal = 80; // Frames until next launch attempt
        let timerTick = 0;
        
        /**
         * Spawns a new firework at the bottom center with a random target height.
         */
        function launchFirework() {
            const startX = W / 2;
            const startY = H;
            // Target X is random within the middle 2/3rds of screen
            const targetX = (W / 3) + Math.random() * (W / 3); 
            // Target Y is random (upper 1/3 to 1/2 of screen)
            const targetY = (H / 3) + Math.random() * (H / 3);
            
            fireworks.push(new Firework(startX, startY, targetX, targetY));
        }

        /**
         * Creates a burst of particles at the given location.
         */
        function createParticles(x, y, hue) {
            // Number of particles per explosion (configurable)
            const particleCount = 50 + Math.floor(Math.random() * 30);
            
            for (let i = 0; i < particleCount; i++) {
                particles.push(new Particle(x, y, hue));
            }
        }

        // --- Main Game Loop ---

        function gameLoop(timestamp) {
            requestAnimationFrame(gameLoop);

            // Delta Time Calculation
            // We use a simple approach here assuming 60fps roughly, 
            // but for smoother physics we can use a fixed step if necessary.
            // For this visual demo, standard frame-based physics is sufficient,
            // but we ensure the loop runs constantly.

            // 1. Clear Canvas (with trail effect)
            // Instead of clearing, we draw a semi-transparent black rectangle.
            // This creates the "fading trail" effect for all moving objects.
            ctx.globalCompositeOperation = 'source-over';
            ctx.fillStyle = 'rgba(0, 0, 0, 0.2)'; 
            ctx.fillRect(0, 0, W, H);

            // 2. Draw & Update Fireworks (Rockets)
            // Use reverse loop to safely remove items
            for (let i = fireworks.length - 1; i >= 0; i--) {
                fireworks[i].draw();
                fireworks[i].update(i);
            }

            // 3. Draw & Update Explosion Particles
            // Additive blending makes overlapping particles glow brighter
            ctx.globalCompositeOperation = 'lighter';
            for (let i = particles.length - 1; i >= 0; i--) {
                particles[i].draw();
                particles[i].update(i);
            }

            // 4. Autonomous Launch Timer
            if (timerTick >= timerTotal) {
                launchFirework();
                // Reset timer with randomness for organic feel
                timerTick = 0;
                timerTotal = 40 + Math.random() * 80; // Random interval between 40 and 120 frames
            } else {
                timerTick++;
            }
        }

        // --- Initialization ---
        
        // Start the loop
        requestAnimationFrame(gameLoop);
        
        // Optional: Launch a couple immediately for visual feedback
        setTimeout(launchFirework, 500);
        setTimeout(launchFirework, 1500);

    </script>
    <section id="notes">
        <h2>Technical Notes</h2>
        <ul>
            <li><strong>Physics Model:</strong> The simulation uses a simple Euler integration for velocity and position. Gravity is applied to the vertical velocity (vy) every frame, and drag (air resistance) is applied to both x and y velocities to simulate the slowing down of particles as they expand.</li>
            <li><strong>Rendering Loop:</strong> <code>requestAnimationFrame</code> is used for high performance. The <code>globalCompositeOperation</code> is set to 'lighter' during particle drawing. This causes colors to add up (white in the center) when particles overlap, creating a realistic glowing effect.</li>
            <li><strong>Trail Effect:</strong> Instead of clearing the canvas completely every frame (<code>clearRect</code>), we draw a semi-transparent black rectangle (<code>rgba(0,0,0,0.2)</code>). This leaves a ghost of the previous frame, creating smooth trails for both rockets and particles.</li>
            <li><strong>Object Management:</strong> Arrays <code>fireworks</code> and <code>particles</code> hold active objects. To optimize performance and prevent errors while iterating, we iterate backwards (<code>i--</code>) when removing objects from these arrays.</li>
            <li><strong>Responsive Design:</strong> The canvas automatically resizes to fit the browser window on load and on resize events.</li>
        </ul>
    </section>
</body>
</html>
```

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: GLM-4.7-Flash-UD-Q6_K_XL.gguf -->
<!-- Prompt: fireworks.md -->
<!-- Time: 52.01s -->
<!-- Fallback: False -->