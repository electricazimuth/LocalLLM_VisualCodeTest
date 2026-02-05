Here is the complete, self-contained solution. I have implemented a robust particle system using modern ES6 classes, delta-time physics for smooth animation, and an autonomous launch system.

```html
<!DOCTYPE html>
<html>
<head>
    <title>Autonomous Fireworks Simulation</title>
    <style>
        body { 
            margin: 0; 
            overflow: hidden; 
            background-color: #111; 
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            font-family: sans-serif;
            color: #aaa;
        }
        canvas { 
            border: 1px solid #444; 
            background-color: #050505; /* Almost black for better contrast */
            box-shadow: 0 0 20px rgba(0,0,0,0.8);
            display: block; 
        }
        .controls {
            margin-top: 10px;
            text-align: center;
        }
        button {
            padding: 8px 16px;
            background: #333;
            color: white;
            border: 1px solid #555;
            cursor: pointer;
            border-radius: 4px;
        }
        button:hover { background: #555; }
    </style>
</head>
<body>
    <canvas id="gameCanvas"></canvas>
    
    <div class="controls">
        <p>System: Autonomous Fireworks</p>
        <button id="resizeBtn">Reset Canvas to Default (512x512)</button>
    </div>

    <script>
        /**
         * SENIOR DEVELOPER NOTES:
         * 
         * 1. Architecture: We use a single array `particles` to manage both Rocket and Particle objects.
         *    This simplifies the render loop but requires polymorphism (shared update/draw methods).
         * 
         * 2. Physics: We use a fixed time step approach scaled by `dt` (delta time). This ensures
         *    physics behave the same way on high-refresh-rate monitors (144hz) as they do on standard (60hz).
         * 
         * 3. Optimization: 
         *    - Object pooling is not strictly used here (simple creation/destruction) as the total count
         *      remains low enough (< 1000 active objects) to not stress the GC in modern browsers.
         *    - We iterate arrays backwards when removing items to prevent index skipping issues.
         * 
         * 4. Visuals: We use 'lighter' composite operation for explosions to create a glowing effect
         *    where colors overlap, simulating light intensity.
         */

        // --- Configuration Constants ---
        const CONFIG = {
            gravity: 900,            // Pixels per second squared
            rocketDrag: 0.99,        // Air resistance for rockets
            rocketUpwardForce: 400,  // Initial upward velocity
            rocketLaunchFreq: 1200,  // Milliseconds between launches (avg)
            rocketExplosionHeight: 0.55, // Explode when reaching X% of screen height
            particleCount: 60,       // Particles per explosion
            particleLife: 2.0,       // Seconds
            particleDrag: 0.96,      // Air resistance for sparks
            colors: [
                '#FF004C', // Red
                '#00FFA3', // Green
                '#00CCFF', // Blue
                '#FFD400', // Yellow
                '#FF00FF', // Magenta
                '#FFFFFF', // White
                '#FF8C00'  // Orange
            ]
        };

        // --- Helper Functions ---
        const random = (min, max) => Math.random() * (max - min) + min;
        const randomColor = () => CONFIG.colors[Math.floor(Math.random() * CONFIG.colors.length)];

        // --- Base Particle Class ---
        class Particle {
            constructor(x, y, color) {
                this.x = x;
                this.y = y;
                this.color = color;
                this.alpha = 1.0;
                this.markedForDeletion = false;
            }

            update(dt) {
                // Base update - to be overridden
            }

            draw(ctx) {
                // Base draw - to be overridden
            }
        }

        // --- Firework Rocket Class ---
        class Rocket extends Particle {
            constructor(x, y) {
                super(x, y, '#FFF');
                this.vx = random(-20, 20); // Slight horizontal drift
                this.vy = -CONFIG.rocketUpwardForce; // Upward velocity
                this.accelerationY = CONFIG.gravity; 
                this.exploded = false;
                this.trail = [];
            }

            update(dt) {
                // Apply Physics
                this.vy += this.accelerationY * dt;
                this.x += this.vx * dt;
                this.y += this.vy * dt;

                // Trail effect logic (simple history)
                if (this.trail.length > 5) this.trail.shift();
                this.trail.push({x: this.x, y: this.y});

                // Check Explosion Conditions
                // 1. Reached target height (top half of screen)
                // 2. Started falling down (vy > 0)
                if (this.y < canvas.height * CONFIG.rocketExplosionHeight || this.vy > 0) {
                    // Random chance to explode if it passed the height threshold
                    if (Math.random() > 0.1) { // 90% chance to explode at height
                        this.explode();
                    }
                }

                // Check if fell off screen (failure to launch)
                if (this.y > canvas.height) {
                    this.markedForDeletion = true;
                }
            }

            draw(ctx) {
                // Draw Rocket Body
                ctx.beginPath();
                ctx.strokeStyle = '#FFF';
                ctx.lineWidth = 2;
                ctx.moveTo(this.trail[0]?.x || this.x, this.trail[0]?.y || this.y);
                for (let p of this.trail) {
                    ctx.lineTo(p.x, p.y);
                }
                ctx.lineTo(this.x, this.y);
                ctx.stroke();

                // Draw Head
                ctx.fillStyle = '#FFF';
                ctx.beginPath();
                ctx.arc(this.x, this.y, 3, 0, Math.PI * 2);
                ctx.fill();
            }

            explode() {
                this.markedForDeletion = true;
                this.exploded = true;
                
                // Create Explosion Particles
                for (let i = 0; i < CONFIG.particleCount; i++) {
                    const angle = random(0, Math.PI * 2);
                    const speed = random(50, 250); // Explosion spread force
                    const vx = Math.cos(angle) * speed;
                    const vy = Math.sin(angle) * speed;
                    
                    particles.push(new ExplosionParticle(this.x, this.y, randomColor(), vx, vy));
                }
            }
        }

        // --- Explosion Particle Class ---
        class ExplosionParticle extends Particle {
            constructor(x, y, color, vx, vy) {
                super(x, y, color);
                this.vx = vx;
                this.vy = vy;
                this.life = CONFIG.particleLife;
                this.maxLife = this.life;
                this.size = random(1.5, 3.5);
            }

            update(dt) {
                // Apply Gravity
                this.vy += CONFIG.gravity * dt;
                
                // Apply Air Resistance (Drag)
                this.vx *= CONFIG.particleDrag;
                this.vy *= CONFIG.particleDrag;

                // Update Position
                this.x += this.vx * dt;
                this.y += this.vy * dt;

                // Update Lifespan
                this.life -= dt;
                
                // Calculate Alpha based on remaining life (fade out)
                this.alpha = Math.max(0, this.life / this.maxLife);

                if (this.life <= 0 || this.y > canvas.height) {
                    this.markedForDeletion = true;
                }
            }

            draw(ctx) {
                ctx.save();
                ctx.globalAlpha = this.alpha;
                ctx.fillStyle = this.color;
                
                // Add glow effect
                ctx.shadowBlur = 10;
                ctx.shadowColor = this.color;

                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                ctx.fill();
                ctx.restore();
            }
        }

        // --- Main Simulation Setup ---
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        
        // Resize Canvas to fit window, but keep internal resolution reasonable
        function resizeCanvas() {
            // Determine a suitable size (max 1024, or window size)
            const maxWidth = Math.min(window.innerWidth - 40, 1024);
            const maxHeight = Math.min(window.innerHeight - 200, 1024);
            
            canvas.width = maxWidth;
            canvas.height = maxHeight;
            
            // Ensure we have at least some height to launch
            if (canvas.height < 300) canvas.height = 300;
        }
        
        // Initial resize
        resizeCanvas();

        // Global State
        let particles = [];
        let lastTime = performance.now();
        let launchTimer = 0;

        // Event Listeners
        document.getElementById('resizeBtn').addEventListener('click', () => {
            canvas.width = 512;
            canvas.height = 512;
        });

        window.addEventListener('resize', resizeCanvas);

        // --- Game Loop ---
        function gameLoop(timestamp) {
            // Calculate Delta Time (in seconds)
            const dt = (timestamp - lastTime) / 1000;
            lastTime = timestamp;

            // Cap dt to prevent physics explosions on lag spikes
            const safeDt = Math.min(dt, 0.1);

            // 1. Clear Canvas
            // Use a slight fillRect with low alpha to create trails/motion blur for rockets
            ctx.fillStyle = 'rgba(5, 5, 5, 0.3)'; // Dark fade effect
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            // 2. Auto-Launch Logic
            if (launchTimer <= 0) {
                // Launch a rocket from bottom center area
                const launchX = canvas.width / 2 + random(-canvas.width/4, canvas.width/4);
                particles.push(new Rocket(launchX, canvas.height));
                
                // Reset timer (random interval between 0.5s and 2s)
                launchTimer = random(500, 2000) / 1000; 
            }
            launchTimer -= safeDt;

            // 3. Update & Draw Particles
            
            // Use additive blending for fireworks to make them look like light
            ctx.globalCompositeOperation = 'lighter';

            // Iterate backwards to allow safe removal
            for (let i = particles.length - 1; i >= 0; i--) {
                const p = particles[i];
                
                // Update Physics
                p.update(safeDt);

                // Draw
                p.draw(ctx);

                // Remove dead particles
                if (p.markedForDeletion) {
                    particles.splice(i, 1);
                }
            }

            // Reset blending for next frame background clear
            ctx.globalCompositeOperation = 'source-over';

            // Continue Loop
            requestAnimationFrame(gameLoop);
        }

        // Start
        requestAnimationFrame(gameLoop);

    </script>
    <section id="notes">
        <h3>Implementation Details</h3>
        <ul>
            <li><strong>Object Structure:</strong> A base <code>Particle</code> class defines the interface. <code>Rocket</code> and <code>ExplosionParticle</code> extend this. This allows us to store them in a single array and iterate them uniformly.</li>
            <li><strong>Physics:</strong> Velocity is updated based on <code>gravity * dt</code>. This ensures the fireworks fall at the same speed regardless of whether the browser runs at 60fps or 144fps.</li>
            <li><strong>Explosion Logic:</strong> Rockets check their Y position against <code>CONFIG.rocketExplosionHeight</code> (55% up the screen). Once reached, they spawn 60 particles with randomized radial velocities.</li>
            <li><strong>Visual Polish:</strong>
                <ul>
                    <li>Rockets leave a trail history to create a streak effect.</li>
                    <li>Explosion particles use `globalAlpha` to fade out as they age.</li>
                    <li>`globalCompositeOperation = 'lighter'` creates an additive color blend. When red and green sparks overlap, they create yellow light, simulating real fireworks brightness.</li>
                    <li>The background clear uses `rgba(5, 5, 5, 0.3)` instead of `clearRect`. This creates a "ghosting" trail effect for moving objects without complex path tracking.</li>
                </ul>
            </li>
            <li><strong>Performance:</strong> Arrays are iterated backwards (`i--`) when removing elements to avoid skipping the next item due to index shifting.</li>
        </ul>
    </section>
</body>
</html>
```

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: Qwen3-Coder-Next-UD-Q3_K_XL.gguf -->
<!-- Prompt: fireworks.md -->
<!-- Time: 42.45s -->
<!-- Fallback: False -->