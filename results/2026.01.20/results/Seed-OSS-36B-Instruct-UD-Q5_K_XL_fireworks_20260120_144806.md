Here's the complete implementation of the autonomous fireworks simulation with all requirements addressed:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Fireworks Simulation</title>
    <style>
        body { margin: 0; overflow: hidden; background-color: #111; }
        canvas { border: 1px solid #444; background-color: #000; display: block; margin: 20px auto; }
    </style>
</head>
<body>
    <canvas id="gameCanvas" width="800" height="600"></canvas>
    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const W = canvas.width;
        const H = canvas.height;
        const GRAVITY = 800; // Pixel per second squared
        let activeParticles = [];
        let nextLaunchTime = 0;
        let lastTime = 0;

        // Base Particle class with common physics
        class Particle {
            constructor(x, y) {
                this.x = x;
                this.y = y;
                this.active = true;
            }

            update(delta) {
                // Apply gravity
                this.vy += GRAVITY * delta;
                // Update position
                this.x += this.vx * delta;
                this.y += this.vy * delta;
            }
        }

        // Firework Rocket class
        class Rocket extends Particle {
            constructor() {
                super(W / 2, H); // Start at bottom center
                this.vx = (Math.random() - 0.5) * 100; // Slight horizontal drift (-50 to 50 px/s)
                this.vy = -Math.random() * 300 - 500; // Upward velocity (-500 to -800 px/s)
                this.r = Math.floor(Math.random() * 255);
                this.g = Math.floor(Math.random() * 255);
                this.b = Math.floor(Math.random() * 255);
                this.timeUntilExplode = 1 + Math.random() * 1; // Fuse: 1-2 seconds
                this.size = 2; // Small rocket visual
            }

            update(delta) {
                super.update(delta);
                
                // Check if fuse expired
                this.timeUntilExplode -= delta;
                if (this.timeUntilExplode <= 0) {
                    this.explode();
                    this.active = false;
                    return;
                }

                // Remove if off-screen top
                if (this.y < 0) this.active = false;
            }

            explode() {
                const particleCount = 30 + Math.random() * 50; // 30-80 explosion particles
                for (let i = 0; i < particleCount; i++) {
                    const angle = Math.random() * Math.PI * 2; // Random direction
                    const speed = 50 + Math.random() * 100; // 50-150 px/s initial speed
                    const vx = speed * Math.cos(angle);
                    const vy = speed * Math.sin(angle);
                    const size = 2 + Math.random() * 2; // 2-4px size
                    const lifespan = 1 + Math.random() * 2; // 1-3s lifespan

                    activeParticles.push(new ExplosionParticle(
                        this.x, this.y, vx, vy, size, lifespan,
                        this.r, this.g, this.b
                    ));
                }
            }
        }

        // Explosion Particle class
        class ExplosionParticle extends Particle {
            constructor(x, y, vx, vy, size, lifespan, r, g, b) {
                super(x, y);
                this.vx = vx;
                this.vy = vy;
                this.size = size;
                this.lifespan = lifespan;
                this.initialLifespan = lifespan;
                this.r = r;
                this.g = g;
                this.b = b;
                this.alpha = 1;
            }

            update(delta) {
                super.update(delta);

                // Manage lifespan and fading
                this.lifespan -= delta;
                this.alpha = Math.max(0, this.lifespan / this.initialLifespan);
                this.active = this.lifespan > 0;

                // Remove if off-screen bottom
                if (this.y > H + this.size * 2) this.active = false;
            }
        }

        // Main game loop
        function gameLoop(timestamp) {
            // Initialize delta time
            if (lastTime === 0) lastTime = timestamp;
            const delta = (timestamp - lastTime) / 1000; // Convert to seconds
            lastTime = timestamp;

            // 1. Launch new rocket if scheduled
            if (timestamp > nextLaunchTime) {
                activeParticles.push(new Rocket());
                // Schedule next launch (500ms to 2000ms interval)
                nextLaunchTime = timestamp + 500 + Math.random() * 1500;
            }

            // 2. Update and clean up particles
            for (let i = activeParticles.length - 1; i >= 0; i--) {
                const particle = activeParticles[i];
                particle.update(delta);
                
                if (!particle.active) {
                    activeParticles.splice(i, 1);
                }
            }

            // 3. Render frame
            ctx.clearRect(0, 0, W, H); // Clear canvas

            activeParticles.forEach(particle => {
                ctx.beginPath();
                ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
                
                if (particle instanceof Rocket) {
                    ctx.fillStyle = `rgb(${particle.r}, ${particle.g}, ${particle.b})`;
                } else {
                    ctx.fillStyle = `rgba(${particle.r}, ${particle.g}, ${particle.b}, ${particle.alpha})`;
                }
                
                ctx.fill();
            });

            requestAnimationFrame(gameLoop);
        }

        // Start simulation
        requestAnimationFrame(gameLoop);
    </script>
    <section id="notes">
        <h3>Simulation Notes:</h3>
        <ul>
            <li>Canvas size: 800x600 (adjustable via HTML width/height attributes)</li>
            <li>Gravity: 800 px/s² (realistic downward acceleration)</li>
            <li>Rocket launch interval: 0.5-2 seconds (randomized)</li>
            <li>Explosion particles: 30-80 per rocket (random count)</li>
            <li>Particle lifespan: 1-3 seconds (with fade-out effect)</li>
            <li>Colors: Random RGB values for each rocket/explosion</li>
            <li>Optimizations: Efficient particle removal (reverse iteration) and delta-time based movement</li>
        </ul>
    </section>
</body>
</html>
```

### Key Features Implemented:

1. **Particle System Architecture**:
   - Base `Particle` class with shared physics (gravity, position updates)
   - `Rocket` subclass for ascending projectiles with fuse mechanics
   - `ExplosionParticle` subclass for post-explosion fragments with fading

2. **Physics Simulation**:
   - Delta-time independent movement using `requestAnimationFrame` timestamps
   - Realistic gravity application to all particles
   - Velocity-based trajectory for both rockets and explosion fragments

3. **Autonomous Behavior**:
   - Randomized rocket launch intervals (0.5-2 seconds)
   - Automatic explosion at fuse expiration (1-2 seconds)
   - Spontaneous particle generation from explosions

4. **Visual Effects**:
   - Fading explosion particles using alpha channel
   - Randomized colors for visual variety
   - Smooth trajectory arcs due to gravity simulation
   - Dark background for contrast (black canvas with dark body)

5. **Performance Optimizations**:
   - Efficient particle removal using reverse array iteration
   - Single particle array for all active entities
   - Minimal DOM operations (only canvas drawing)

### How to Use:
1. Save as an HTML file
2. Open in a modern web browser (Chrome, Firefox, Edge)
3. The simulation runs automatically with no user input required

### Customization Options (Modify These Constants/Values):
- `GRAVITY`: Adjust for stronger/weaker gravitational effect
- Rocket `vy` values: Change initial upward speed
- Explosion particle `speed`: Adjust explosion spread diameter
- `nextLaunchTime` interval: Modify rocket launch frequency
- Particle `lifespan`: Change how long explosion fragments persist
- Canvas `width`/`height` attributes: Adjust display size

The simulation creates a continuous, dynamic fireworks display with realistic physics and visual effects, meeting all specified requirements while maintaining smooth performance even with hundreds of active particles.

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: Seed-OSS-36B-Instruct-UD-Q5_K_XL.gguf -->
<!-- Prompt: fireworks.md -->
<!-- Generation Time: 463.69s -->
<!-- Fallback Used: False -->