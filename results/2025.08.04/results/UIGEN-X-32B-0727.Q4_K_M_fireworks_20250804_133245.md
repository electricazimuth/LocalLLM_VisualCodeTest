We are going to create a fireworks simulation with the following structure:

1. **Particle System**: We'll have two types of particles: rockets and explosion particles.
2. **Rockets**: 
   - Launched from the bottom center.
   - Move upwards with a decreasing velocity (due to gravity).
   - Have a fuse that counts down to explosion (or explode when velocity becomes too slow).
   - Upon explosion, they generate multiple explosion particles.
3. **Explosion Particles**:
   - Created at the rocket's position when it explodes.
   - Have random velocities in all directions.
   - Are affected by gravity and fade out over time.

We'll use a single array to manage all active particles. Each particle will have properties to distinguish between a rocket and an explosion particle.

**Design Choices**:
- We'll use a dark background (#000) to make the fireworks stand out.
- Colors for explosion particles will be randomized but with a base color per rocket (e.g., red, green, blue, yellow).
- We'll use the Canvas API for drawing.

**Implementation**:

1. **Particle Class/Structure**:
   - We'll create a base structure for a particle with:
        - `x`, `y`: position
        - `vx`, `vy`: velocity
        - `color`: for explosion particles (rockets might have a fixed color or none)
        - `size`: radius for drawing
        - `life`: for explosion particles (rocket might have a timer for explosion)

2. **Rocket**:
   - We'll create a function to generate a rocket particle.
   - The rocket will have:
        - `x`: starting near center at bottom (W/2)
        - `y`: starting at H - 20
        - `vx`: small random horizontal velocity (e.g., -0.5 to 0.5)
        - `vy`: initial upward velocity (e.g., -5 to -8)
        - `color`: not used for drawing the rocket? We can draw it as a bright color (e.g., white) and then the explosion particles will use the color.
        - `size`: 2
        - `life`: time until explosion (e.g., 1 to 2 seconds) OR we can check when the rocket stops moving upward (vy becomes positive) and then explode.

3. **Explosion Particle**:
   - Created when a rocket explodes.
   - `x`, `y`: same as rocket at explosion.
   - `vx`, `vy`: random in a circle (e.g., radius 3 to 5) and then add a vertical component to make it spread out.
   - `color`: random from a set of colors (or based on rocket's color)
   - `size`: 1 to 3
   - `life`: 1 to 3 seconds (with alpha decreasing over time)

4. **Game Loop**:
   - We'll use `requestAnimationFrame` and track delta time.
   - Update:
        - For each particle, update position (x += vx * dt, y += vy * dt)
        - Apply gravity: vy += gravity * dt (gravity is positive because y increases downward)
        - For rockets: 
            - Check if it should explode (e.g., when vy > 0 (start falling) OR when a timer runs out). 
            - When it explodes, remove the rocket and create explosion particles.
        - For explosion particles: decrease their life (life -= dt). If life <= 0, remove.
   - Draw:
        - Clear the canvas (dark background)
        - For rockets: draw a line from the starting point to current position? Or just a dot? We can draw a trail by storing previous positions? 
          But for simplicity, we'll draw a circle for the rocket and for explosion particles.
        - Rockets: white circle, size 2.
        - Explosion particles: circle with color and alpha = (life / maxLife) to fade out.

5. **Autonomous Launching**:
   - We'll set an interval (or use a timer) to create a new rocket every 0.5 to 2 seconds.

6. **Optimization**:
   - We'll remove particles when they explode (rockets) or when they die (explosion particles) to keep the array size manageable.

Let's code accordingly.

Note: We are using a single array for all particles. We can have a property `isRocket` to distinguish.

We'll create:
- `particles` array.
- `addRocket()` function to add a rocket particle.
- `addExplosionParticles(x, y, count, color)` to add explosion particles.

In the game loop:
- Update and draw all particles.
- Remove rockets when they explode (and then add explosion particles).
- Remove explosion particles when their life is over.

We'll also handle the autonomous launching with a timer.

Let's code accordingly.
</think>

# Autonomous Fireworks Particle Simulation

I'll create a visually striking fireworks simulation with realistic physics, colorful explosions, and efficient particle management. The solution will demonstrate JavaScript best practices for object-oriented design and animation.

```html
<!DOCTYPE html>
<html>
<head>
    <title>Autonomous Fireworks Simulation</title>
    <style>
        body { 
            margin: 0; 
            overflow: hidden; 
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); 
            color: white; 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            text-align: center;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
            text-shadow: 0 0 10px rgba(255, 255, 255, 0.7);
        }
        
        p {
            color: #a0a0c0;
            margin-bottom: 20px;
        }
        
        .controls {
            display: flex;
            justify-content: center;
            gap: 15px;
            margin: 20px 0;
        }
        
        button {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid #4a4a7c;
            color: white;
            padding: 8px 15px;
            border-radius: 4px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        button:hover {
            background: rgba(255, 255, 255, 0.2);
            transform: translateY(-2px);
        }
        
        .stats {
            background: rgba(0, 0, 0, 0.7);
            padding: 10px 20px;
            border-radius: 8px;
            margin: 20px 0;
            text-align: left;
            max-width: 400px;
            margin-left: auto;
            margin-right: auto;
        }
        
        .stat-item {
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
            font-size: 0.9rem;
        }
        
        .stat-label {
            color: #a0a0c0;
        }
        
        .stat-value {
            font-weight: bold;
            color: #ffcc00;
        }
        
        canvas {
            background: rgba(0, 0, 0, 0.8);
            border-radius: 8px;
            box-shadow: 0 0 30px rgba(0, 0, 0, 0.5);
            border: 1px solid rgba(255, 255, 255, 0.1);
            display: block;
            margin: 0 auto 30px;
        }
        
        .footer {
            color: #a0a0c0;
            font-size: 0.9rem;
            margin-top: 30px;
        }
        
        @media (max-width: 768px) {
            h1 {
                font-size: 1.8rem;
            }
            
            .controls {
                flex-direction: column;
                align-items: center;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Autonomous Fireworks Simulation</h1>
        <p>Experience a stunning display of physics-based fireworks with realistic explosions and particle effects</p>
        
        <div class="controls">
            <button id="launchBtn">Launch Fireworks</button>
            <button id="resetBtn">Reset Simulation</button>
        </div>
        
        <div class="stats">
            <div class="stat-item">
                <span class="stat-label">Active Particles:</span>
                <span class="stat-value" id="particleCount">0</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">Fireworks Launched:</span>
                <span class="stat-value" id="fireworkCount">0</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">FPS:</span>
                <span class="stat-value" id="fps">0</span>
            </div>
        </div>
        
        <canvas id="fireworksCanvas" width="800" height="600"></canvas>
        
        <div class="footer">
            <p>Click "Launch Fireworks" to start the simulation. Particles are automatically managed with efficient physics calculations.</p>
        </div>
    </div>

    <script>
        // Canvas setup
        const canvas = document.getElementById('fireworksCanvas');
        const ctx = canvas.getContext('2d');
        const width = canvas.width;
        const height = canvas.height;
        
        // Performance stats
        const particleCountEl = document.getElementById('particleCount');
        const fireworkCountEl = document.getElementById('fireworkCount');
        const fpsEl = document.getElementById('fps');
        
        // Physics constants
        const GRAVITY = 0.1;
        const PARTICLE_LIFESPAN = 3000; // 3 seconds
        const ROCKET_LIFESPAN = 2000; // 2 seconds
        const EXPLOSION_RADIUS = 3;
        
        // Color palette
        const COLORS = [
            '#ff2a6d', '#05d9e8', '#d1f7ff', '#ffbe0b', '#fb5607', 
            '#8338ec', '#3a0ca3', '#4cc9f0', '#f72585', '#4361ee'
        ];
        
        // Particle types
        const PARTICLE_TYPE = {
            ROCKET: 'rocket',
            EXPLOSION: 'explosion'
        };
        
        // Base Particle class
        class Particle {
            constructor(x, y, type) {
                this.x = x;
                this.y = y;
                this.type = type;
                this.lifespan = type === PARTICLE_TYPE.ROCKET ? ROCKET_LIFESPAN : PARTICLE_LIFESPAN;
                this.birthTime = Date.now();
                this.size = type === PARTICLE_TYPE.ROCKET ? 3 : Math.random() * 2 + 1;
                this.rotation = Math.random() * Math.PI * 2;
                this.rotationSpeed = Math.random() * 0.02 - 0.01;
            }
            
            update(deltaTime) {
                this.lifespan -= deltaTime;
                this.rotation += this.rotationSpeed;
            }
            
            isAlive() {
                return this.lifespan > 0;
            }
        }
        
        // Rocket class (inherits from Particle)
        class Rocket extends Particle {
            constructor(x, y) {
                super(x, y, PARTICLE_TYPE.ROCKET);
                this.vx = (Math.random() - 0.5) * 0.5;
                this.vy = -Math.random() * 3 - 1.5;
                this.color = COLORS[Math.floor(Math.random() * COLORS.length)];
                this.trail = [];
            }
            
            update(deltaTime) {
                super.update(deltaTime);
                this.vy += GRAVITY * deltaTime * 0.7;
                
                // Update position
                this.x += this.vx * deltaTime;
                this.y += this.vy * deltaTime;
                
                // Add to trail
                this.trail.push({x: this.x, y: this.y});
                if (this.trail.length > 20) {
                    this.trail.shift();
                }
            }
            
            draw(ctx) {
                // Draw rocket body
                ctx.save();
                ctx.translate(this.x, this.y);
                ctx.rotate(this.rotation);
                
                // Rocket body
                ctx.fillStyle = this.color;
                ctx.beginPath();
                ctx.moveTo(0, -this.size);
                ctx.lineTo(this.size, 0);
                ctx.lineTo(0, this.size);
                ctx.closePath();
                ctx.fill();
                
                // Rocket flame
                ctx.fillStyle = '#ff5500';
                ctx.beginPath();
                ctx.moveTo(0, 0);
                ctx.lineTo(-this.size, -this.size);
                ctx.lineTo(-this.size*2, 0);
                ctx.lineTo(-this.size, this.size);
                ctx.closePath();
                ctx.fill();
                
                ctx.restore();
                
                // Draw trail
                if (this.trail.length > 1) {
                    ctx.beginPath();
                    ctx.moveTo(this.trail[0].x, this.trail[0].y);
                    
                    for (let i = 1; i < this.trail.length; i++) {
                        const point = this.trail[i];
                        ctx.lineTo(point.x, point.y);
                    }
                    
                    const gradient = ctx.createLinearGradient(0, 0, 0, height);
                    gradient.addColorStop(0, this.color + '80');
                    gradient.addColorStop(1, this.color + '00');
                    
                    ctx.strokeStyle = gradient;
                    ctx.lineWidth = 1;
                    ctx.stroke();
                }
            }
        }
        
        // ExplosionParticle class (inherits from Particle)
        class ExplosionParticle extends Particle {
            constructor(x, y, color) {
                super(x, y, PARTICLE_TYPE.EXPLOSION);
                this.color = color;
                this.vx = (Math.random() - 0.5) * 10;
                this.vy = (Math.random() - 0.5) * 10;
                this.alpha = 1;
                this.size = Math.random() * 3 + 1;
            }
            
            update(deltaTime) {
                super.update(deltaTime);
                this.vy += GRAVITY * deltaTime;
                
                // Update position
                this.x += this.vx * deltaTime;
                this.y += this.vy * deltaTime;
                
                // Update alpha (fade out)
                this.alpha = this.lifespan / PARTICLE_LIFESPAN;
            }
            
            draw(ctx) {
                ctx.save();
                ctx.globalAlpha = this.alpha;
                
                // Draw particle with glow effect
                const gradient = ctx.createRadialGradient(
                    this.x, this.y, 0, 
                    this.x, this.y, this.size
                );
                gradient.addColorStop(0, this.color + 'ff');
                gradient.addColorStop(1, this.color + '00');
                
                ctx.fillStyle = gradient;
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                ctx.fill();
                
                ctx.restore();
            }
        }
        
        // Main simulation class
        class FireworksSimulation {
            constructor() {
                this.particles = [];
                this.rocketsLaunched = 0;
                this.explodedRockets = 0;
                this.lastTime = Date.now();
                this.fps = 0;
                this.simulationRunning = false;
                this.nextRocketTime = 0;
                this.rocketInterval = 1500; // 1.5 seconds between launches
            }
            
            start() {
                this.simulationRunning = true;
                this.lastTime = Date.now();
                this.nextRocketTime = this.lastTime + this.rocketInterval;
                requestAnimationFrame(this.loop.bind(this));
            }
            
            stop() {
                this.simulationRunning = false;
            }
            
            reset() {
                this.stop();
                this.particles = [];
                this.rocketsLaunched = 0;
                this.explodedRockets = 0;
                this.updateStats();
            }
            
            loop(timestamp) {
                const now = Date.now();
                const deltaTime = now - this.lastTime;
                this.lastTime = now;
                
                // Update FPS
                this.fps = Math.round(1000 / deltaTime);
                
                // Update stats
                this.updateStats();
                
                // Launch new rockets
                if (this.simulationRunning && now >= this.nextRocketTime) {
                    this.launchRocket();
                    this.nextRocketTime = now + this.rocketInterval;
                }
                
                // Update particles
                for (let i = this.particles.length - 1; i >= 0; i--) {
                    const particle = this.particles[i];
                    particle.update(deltaTime);
                    
                    // Handle rocket explosion
                    if (particle.type === PARTICLE_TYPE.ROCKET) {
                        const rocket = particle;
                        
                        // Explosion conditions
                        if (rocket.vy > 0 || rocket.y > height * 0.8) {
                            this.explodeRocket(rocket);
                            this.particles.splice(i, 1);
                        }
                    } 
                    // Remove dead particles
                    else if (!particle.isAlive()) {
                        this.particles.splice(i, 1);
                    }
                }
                
                // Draw
                this.draw();
                
                // Continue loop
                if (this.simulationRunning) {
                    requestAnimationFrame(this.loop.bind(this));
                }
            }
            
            launchRocket() {
                const x = width / 2;
                const y = height - 20;
                const rocket = new Rocket(x, y);
                this.particles.push(rocket);
                this.rocketsLaunched++;
            }
            
            explodeRocket(rocket) {
                this.explodedRockets++;
                
                // Create explosion particles
                for (let i = 0; i < 80; i++) {
                    const particle = new ExplosionParticle(
                        rocket.x, 
                        rocket.y, 
                        rocket.color
                    );
                    this.particles.push(particle);
                }
            }
            
            draw() {
                // Clear canvas with gradient
                ctx.save();
                ctx.fillStyle = 'linear-gradient(to top, #0f0c29, #302b63, #24243e)';
                ctx.fillRect(0, 0, width, height);
                ctx.restore();
                
                // Draw stars for background
                if (this.particles.length === 0) {
                    this.drawStars();
                }
                
                // Draw particles
                for (const particle of this.particles) {
                    if (particle.isAlive()) {
                        particle.draw(ctx);
                    }
                }
            }
            
            drawStars() {
                ctx.fillStyle = '#a0a0c0';
                for (let i = 0; i < 50; i++) {
                    const x = Math.random() * width;
                    const y = Math.random() * height;
                    const size = Math.random() * 1.5;
                    ctx.beginPath();
                    ctx.arc(x, y, size, 0, Math.PI * 2);
                    ctx.fill();
                }
            }
            
            updateStats() {
                particleCountEl.textContent = this.particles.length;
                fireworkCountEl.textContent = this.rocketsLaunched;
                fpsEl.textContent = this.fps;
            }
        }
        
        // Initialize simulation
        const simulation = new FireworksSimulation();
        
        // Event listeners
        document.getElementById('launchBtn').addEventListener('click', () => {
            simulation.start();
        });
        
        document.getElementById('resetBtn').addEventListener('click', () => {
            simulation.reset();
        });
        
        // Start with some fireworks
        setTimeout(() => {
            simulation.start();
        }, 1000);
    </script>
</body>
</html>
```

## Key Features of the Implementation

1. **Object-Oriented Design**:
   - Created a base `Particle` class with common properties
   - Specialized `Rocket` and `ExplosionParticle` classes
   - `FireworksSimulation` class to manage the entire system

2. **Realistic Physics**:
   - Gravity simulation with acceleration
   - Rocket trajectory with upward velocity decreasing over time
   - Explosion particles with random directions and realistic fall
   - Particle trails for rockets

3. **Visual Effects**:
   - Colorful explosions with radial gradients
   - Rocket trails with fading gradients
   - Particle fading over time
   - Dynamic background with stars
   - Smooth animations with requestAnimationFrame

4. **Performance Optimizations**:
   - Efficient particle management with array operations
   - Delta time calculation for frame-rate independence
   - Canvas clearing with gradients instead of full clear
   - Early removal of dead particles

5. **User Interaction**:
   - Launch and reset controls
   - Real-time statistics display
   - Responsive design for different screen sizes

The simulation creates a visually stunning fireworks display with realistic physics, colorful explosions, and efficient particle management. The design follows modern JavaScript best practices with a clean object hierarchy and separation of concerns.

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: UIGEN-X-32B-0727.Q4_K_M.gguf -->
<!-- Prompt: fireworks.md -->
<!-- Generation Time: 158.16s -->
<!-- Fallback Used: False -->