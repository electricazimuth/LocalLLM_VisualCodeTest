Here is the complete, autonomous firework simulation implemented in a single HTML file.

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
        }
        canvas { 
            border: 1px solid #444; 
            background-color: #000; 
            display: block; 
            box-shadow: 0 0 20px rgba(0,0,0,0.8);
            margin-top: 20px;
        }
        #info {
            color: #888;
            font-family: sans-serif;
            font-size: 14px;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <canvas id="gameCanvas" width="800" height="600"></canvas>
    <div id="info">Autonomous Fireworks Particle Simulation</div>
    
    <section id="notes">
        <h3>Implementation Notes</h3>
        <ul>
            <li><strong>Physics Engine:</strong> The simulation uses a delta-time calculation (`dt`) to ensure particle movement speed remains consistent regardless of the monitor's refresh rate (60Hz vs 144Hz).</li>
            <li><strong>Object Pooling Strategy:</strong> While not using a strict pre-allocated pool to keep the code readable for this task, particles are removed from the array immediately upon death to prevent memory leaks and maintain performance.</li>
            <li><strong>Visuals:</strong> The rockets are rendered as short trails. The explosion particles use additive color blending (`globalCompositeOperation = 'lighter'`) to simulate the bright light of sparks, creating a glowing effect where colors overlap.</li>
            <li><strong>Autonomy:</strong> A separate timer controls the launch frequency (randomized between 0.5s and 2.0s) to create a natural, non-mechanical rhythm.</li>
        </ul>
    </section>

    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const W = canvas.width;
        const H = canvas.height;

        // --- Configuration ---
        const CONFIG = {
            gravity: 0.15,
            friction: 0.96, // Air resistance for particles
            rocketSpeed: 8,
            launchIntervalMin: 500, // ms
            launchIntervalMax: 2000, // ms
            minParticlesPerExplosion: 40,
            maxParticlesPerExplosion: 80
        };

        // --- State Management ---
        let particles = [];
        let lastLaunchTime = 0;
        let nextLaunchDelay = CONFIG.launchIntervalMin;

        // --- Utility Functions ---
        function randomRange(min, max) {
            return Math.random() * (max - min) + min;
        }

        function randomColor() {
            // Generate vibrant colors using HSL
            const hue = randomRange(0, 360);
            return `hsl(${hue}, 100%, 60%)`;
        }

        // --- Classes ---

        class Rocket {
            constructor(x, y) {
                this.x = x;
                this.y = y;
                
                // Calculate velocity to reach roughly the top half of the screen
                // vx: slight randomness for drift, vy: strong upward force
                this.vx = randomRange(-1.5, 1.5);
                this.vy = -randomRange(CONFIG.rocketSpeed * 0.8, CONFIG.rocketSpeed * 1.2);
                
                this.color = randomColor();
                this.active = true;
                this.trail = []; // Store previous positions for visual streak
                
                // Random fuse time (frames) to determine when it explodes
                // Faster rockets (higher vy) might explode slightly sooner, but we keep it random for variety
                this.fuse = randomRange(40, 80); 
            }

            update(dt) {
                // Apply Physics
                this.x += this.vx * dt;
                this.y += this.vy * dt;

                // Apply Gravity (slows the rocket down until it falls)
                this.vy += CONFIG.gravity * dt;
                
                // Record trail
                this.trail.push({x: this.x, y: this.y});
                if (this.trail.length > 5) {
                    this.trail.shift(); // Keep trail short
                }

                // Explosion Logic
                // 1. If velocity becomes positive (falling down) -> Explode
                // 2. If fuse runs out -> Explode
                // 3. If goes off screen top -> Explode
                if (this.vy > 0 || this.fuse <= 0 || this.y < H * 0.2) {
                    this.explode();
                }

                this.fuse -= 1 * dt;
            }

            draw(ctx) {
                if (this.trail.length < 2) return;

                ctx.beginPath();
                ctx.moveTo(this.trail[0].x, this.trail[0].y);
                for (let i = 1; i < this.trail.length; i++) {
                    ctx.lineTo(this.trail[i].x, this.trail[i].y);
                }
                
                ctx.strokeStyle = this.color;
                ctx.lineWidth = 2;
                ctx.lineCap = 'round';
                ctx.shadowBlur = 10;
                ctx.shadowColor = this.color;
                ctx.stroke();
                
                // Reset shadow for other elements
                ctx.shadowBlur = 0;
            }

            explode() {
                this.active = false;
                // Create explosion particles
                const particleCount = randomRange(CONFIG.minParticlesPerExplosion, CONFIG.maxParticlesPerExplosion);
                
                for (let i = 0; i < particleCount; i++) {
                    particles.push(new ExplosionParticle(this.x, this.y, this.color));
                }
            }
        }

        class ExplosionParticle {
            constructor(x, y, baseColor) {
                this.x = x;
                this.y = y;
                this.baseColor = baseColor;
                
                // Random velocity in all directions (Cone or Circle distribution)
                const angle = randomRange(0, Math.PI * 2);
                // Speed varies from fast (close to explosion) to slow (outer edge)
                const speed = randomRange(1, 6); 
                
                this.vx = Math.cos(angle) * speed;
                this.vy = Math.sin(angle) * speed;
                
                this.life = 1.0; // 1.0 = 100% life
                this.decay = randomRange(0.01, 0.03); // How fast it fades
                this.size = randomRange(2, 4);
                this.active = true;
            }

            update(dt) {
                // Apply Physics
                this.x += this.vx * dt;
                this.y += this.vy * dt;

                // Gravity affects falling sparks
                this.vy += CONFIG.gravity * dt;

                // Air resistance (sparks slow down over time)
                this.vx *= CONFIG.friction;
                this.vy *= CONFIG.friction;

                // Update Life
                this.life -= this.decay * dt;
                
                if (this.life <= 0) {
                    this.active = false;
                }
            }

            draw(ctx) {
                ctx.save();
                ctx.globalAlpha = this.life; // Fade out based on remaining life
                ctx.fillStyle = this.baseColor;
                
                // Optional: Add a slight glow to particles
                ctx.shadowBlur = 5;
                ctx.shadowColor = this.baseColor;

                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                ctx.fill();
                ctx.restore();
            }
        }

        // --- Core Game Loop ---

        function spawnRocket() {
            // Launch from bottom center area with some randomness
            const x = randomRange(W * 0.2, W * 0.8);
            const y = H; // Start exactly at bottom
            particles.push(new Rocket(x, y));
        }

        function handleAutonomousLaunch(timestamp) {
            if (timestamp - lastLaunchTime > nextLaunchDelay) {
                spawnRocket();
                lastLaunchTime = timestamp;
                // Randomize next interval
                nextLaunchDelay = randomRange(CONFIG.launchIntervalMin, CONFIG.launchIntervalMax);
            }
        }

        function gameLoop(timestamp) {
            // Calculate Delta Time (in seconds)
            // We assume 60fps is standard, but this scales it for other rates
            const dt = (timestamp - lastTime) / 16.67;
            lastTime = timestamp;

            // 1. Clear Canvas
            // Using a semi-transparent fillRect to create a "motion blur" / trail effect
            // If you want crisp movement, change to ctx.clearRect(0, 0, W, H);
            ctx.fillStyle = 'rgba(0, 0, 0, 0.3)'; 
            ctx.fillRect(0, 0, W, H);

            // 2. Autonomous Launch Logic
            handleAutonomousLaunch(timestamp);

            // 3. Update and Draw Particles
            // Use additive blending for explosions to make them look bright
            ctx.globalCompositeOperation = 'lighter';

            for (let i = particles.length - 1; i >= 0; i--) {
                const p = particles[i];

                // Update
                p.update(dt);

                // Draw
                p.draw(ctx);

                // Remove inactive particles
                if (!p.active) {
                    particles.splice(i, 1);
                }
            }

            // Reset composite operation for next frame background clear
            ctx.globalCompositeOperation = 'source-over';

            requestAnimationFrame(gameLoop);
        }

        // --- Initialization ---
        let lastTime = performance.now();
        
        // Start the loop
        requestAnimationFrame(gameLoop);

        // Initial launch to show something immediately
        setTimeout(spawnRocket, 500);
        setTimeout(spawnRocket, 1200);

    </script>
</body>
</html>
```

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: Qwen3-Coder-Next-UD-Q4_K_XL.gguf -->
<!-- Prompt: fireworks.md -->
<!-- Time: 39.83s -->
<!-- Fallback: False -->