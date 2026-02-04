```html
<!DOCTYPE html>
<html>
<head>
    <title>Vehicle Collision Simulation</title>
    <style>
        body { margin: 0; overflow: hidden; background-color: #333; }
        canvas { display: block; margin: 20px auto; border: 1px solid #666; background-color: #000; }
    </style>
</head>
<body>
    <canvas id="simulationCanvas" width="512" height="512"></canvas>

    <script>
        // --- YOUR JAVASCRIPT CODE GOES HERE ---
        // Setup canvas, context, vehicle array, particle array, state variable,
        // initialization function, animation loop, etc.

        // Canvas setup
        const canvas = document.getElementById('simulationCanvas');
        const ctx = canvas.getContext('2d');
        
        // Simulation constants
        const CANVAS_WIDTH = canvas.width;
        const CANVAS_HEIGHT = canvas.height;
        const VEHICLE_COUNT = 8; // Number of vehicles to start with
        const EXPLOSION_PARTICLE_COUNT = 25; // Number of particles per explosion
        const EXPLOSION_DURATION = 3000; // milliseconds before restart
        const RESTART_DELAY = 1500; // milliseconds delay before restart
        
        // Simulation state
        let simulationState = 'RUNNING'; // 'RUNNING', 'EXPLODING', 'RESTARTING'
        let vehicles = [];
        let explosionParticles = [];
        let explosionStartTime = 0;
        let restartTimer = 0;
        
        // Vehicle class
        class Vehicle {
            constructor() {
                this.x = Math.random() * CANVAS_WIDTH;
                this.y = Math.random() * CANVAS_HEIGHT;
                this.vx = (Math.random() - 0.5) * 4; // Random velocity between -2 and 2
                this.vy = (Math.random() - 0.5) * 4;
                this.width = 20;
                this.height = 12;
                this.color = `hsl(${Math.random() * 360}, 70%, 60%)`;
                this.isActive = true;
                this.rotation = 0; // For visual orientation
            }
            
            update(deltaTime) {
                if (!this.isActive) return;
                
                // Update position based on velocity and delta time
                this.x += this.vx * deltaTime;
                this.y += this.vy * deltaTime;
                
                // Screen wrapping - check all four edges
                if (this.x < 0) this.x = CANVAS_WIDTH;
                if (this.x > CANVAS_WIDTH) this.x = 0;
                if (this.y < 0) this.y = CANVAS_HEIGHT;
                if (this.y > CANVAS_HEIGHT) this.y = 0;
                
                // Update rotation to match movement direction
                if (Math.abs(this.vx) > 0.1 || Math.abs(this.vy) > 0.1) {
                    this.rotation = Math.atan2(this.vy, this.vx);
                }
            }
            
            draw() {
                if (!this.isActive) return;
                
                ctx.save();
                ctx.translate(this.x, this.y);
                ctx.rotate(this.rotation);
                
                // Draw car body (rectangle)
                ctx.fillStyle = this.color;
                ctx.fillRect(-this.width/2, -this.height/2, this.width, this.height);
                
                // Draw wheels (circles)
                ctx.fillStyle = '#111';
                ctx.beginPath();
                ctx.arc(-this.width/3, -this.height/2, 3, 0, Math.PI * 2);
                ctx.fill();
                
                ctx.beginPath();
                ctx.arc(this.width/3, -this.height/2, 3, 0, Math.PI * 2);
                ctx.fill();
                
                ctx.beginPath();
                ctx.arc(-this.width/3, this.height/2, 3, 0, Math.PI * 2);
                ctx.fill();
                
                ctx.beginPath();
                ctx.arc(this.width/3, this.height/2, 3, 0, Math.PI * 2);
                ctx.fill();
                
                ctx.restore();
            }
            
            // Check collision with another vehicle using axis-aligned bounding box
            collidesWith(other) {
                if (!this.isActive || !other.isActive) return false;
                
                // Simple bounding box collision detection
                const thisLeft = this.x - this.width/2;
                const thisRight = this.x + this.width/2;
                const thisTop = this.y - this.height/2;
                const thisBottom = this.y + this.height/2;
                
                const otherLeft = other.x - other.width/2;
                const otherRight = other.x + other.width/2;
                const otherTop = other.y - other.height/2;
                const otherBottom = other.y + other.height/2;
                
                return thisLeft < otherRight && thisRight > otherLeft &&
                       thisTop < otherBottom && thisBottom > otherTop;
            }
        }
        
        // ExplosionParticle class
        class ExplosionParticle {
            constructor(x, y, color) {
                this.x = x;
                this.y = y;
                this.vx = (Math.random() - 0.5) * 10; // Random velocity between -5 and 5
                this.vy = (Math.random() - 0.5) * 10;
                this.life = 1.0; // Full life
                this.maxLife = 1.0;
                this.size = 2 + Math.random() * 5;
                this.color = color || `hsl(${Math.random() * 360}, 80%, 60%)`;
                this.decayRate = 0.02 + Math.random() * 0.03; // Random decay rate
            }
            
            update(deltaTime) {
                this.x += this.vx * deltaTime;
                this.y += this.vy * deltaTime;
                
                // Apply a bit of gravity (upward particles should fall down)
                this.vy += 0.05 * deltaTime;
                
                // Decrease life based on decay rate
                this.life -= this.decayRate * deltaTime;
                
                // Remove if life is gone
                if (this.life <= 0) {
                    return false; // Indicates particle should be removed
                }
                
                return true; // Particle is still alive
            }
            
            draw() {
                ctx.globalAlpha = this.life;
                ctx.fillStyle = this.color;
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                ctx.fill();
                ctx.globalAlpha = 1.0;
            }
        }
        
        // Initialize the simulation
        function initSimulation() {
            vehicles = [];
            explosionParticles = [];
            simulationState = 'RUNNING';
            explosionStartTime = 0;
            restartTimer = 0;
            
            // Create initial vehicles
            for (let i = 0; i < VEHICLE_COUNT; i++) {
                vehicles.push(new Vehicle());
            }
        }
        
        // Check for collisions between vehicles
        function checkCollisions() {
            for (let i = 0; i < vehicles.length; i++) {
                for (let j = i + 1; j < vehicles.length; j++) {
                    if (vehicles[i].collidesWith(vehicles[j])) {
                        // Collision detected! Create explosion
                        createExplosion(vehicles[i].x, vehicles[i].y, vehicles[i].color);
                        
                        // Mark both vehicles as inactive
                        vehicles[i].isActive = false;
                        vehicles[j].isActive = false;
                        
                        // Switch to EXPLODING state
                        simulationState = 'EXPLODING';
                        explosionStartTime = Date.now();
                        
                        // We can break here since we only need one explosion to trigger the reset
                        // But we'll let the loop continue to handle any other collisions
                    }
                }
            }
        }
        
        // Create explosion at specified position
        function createExplosion(x, y, color) {
            explosionParticles = [];
            
            // Create explosion particles
            for (let i = 0; i < EXPLOSION_PARTICLE_COUNT; i++) {
                explosionParticles.push(new ExplosionParticle(x, y, color));
            }
            
            // Add "BOOM" text at center of explosion
            explosionParticles.push({
                x: x,
                y: y,
                life: 1.0,
                maxLife: 1.5,
                decayRate: 0.015,
                size: 20,
                text: 'BOOM',
                font: 'bold 40px Arial',
                color: '#fff',
                fadeOut: true,
                draw: function() {
                    ctx.globalAlpha = this.life;
                    ctx.font = this.font;
                    ctx.fillStyle = this.color;
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    ctx.fillText(this.text, this.x, this.y);
                    ctx.globalAlpha = 1.0;
                },
                update: function(deltaTime) {
                    this.life -= this.decayRate * deltaTime;
                    if (this.life <= 0) {
                        return false;
                    }
                    // Make text slightly expand
                    this.size += 0.5 * deltaTime;
                    this.font = `bold ${this.size}px Arial`;
                    return true;
                }
            });
        }
        
        // Update all game objects based on current state
        function update(deltaTime) {
            if (simulationState === 'RUNNING') {
                // Update vehicles
                vehicles.forEach(vehicle => vehicle.update(deltaTime));
                
                // Check for collisions
                checkCollisions();
                
            } else if (simulationState === 'EXPLODING') {
                // Update explosion particles
                explosionParticles = explosionParticles.filter(particle => particle.update(deltaTime));
                
                // Check if explosion has lasted long enough
                if (Date.now() - explosionStartTime > EXPLOSION_DURATION) {
                    simulationState = 'RESTARTING';
                    restartTimer = Date.now();
                }
                
            } else if (simulationState === 'RESTARTING') {
                // Wait for restart delay
                if (Date.now() - restartTimer > RESTART_DELAY) {
                    initSimulation();
                }
            }
        }
        
        // Draw all game objects based on current state
        function draw() {
            // Clear canvas
            ctx.clearRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);
            
            if (simulationState === 'RUNNING') {
                // Draw active vehicles
                vehicles.forEach(vehicle => vehicle.draw());
                
            } else if (simulationState === 'EXPLODING') {
                // Draw explosion particles
                explosionParticles.forEach(particle => {
                    if (particle.draw) {
                        particle.draw();
                    } else {
                        particle.draw();
                    }
                });
                
                // Add glowing effect at center of explosion
                if (explosionParticles.length > 0) {
                    const centerX = explosionParticles[0].x;
                    const centerY = explosionParticles[0].y;
                    const gradient = ctx.createRadialGradient(centerX, centerY, 0, centerX, centerY, 50);
                    gradient.addColorStop(0, 'rgba(255, 200, 100, 0.8)');
                    gradient.addColorStop(0.5, 'rgba(255, 100, 0, 0.4)');
                    gradient.addColorStop(1, 'rgba(255, 0, 0, 0)');
                    
                    ctx.fillStyle = gradient;
                    ctx.beginPath();
                    ctx.arc(centerX, centerY, 50, 0, Math.PI * 2);
                    ctx.fill();
                }
                
            } else if (simulationState === 'RESTARTING') {
                // Clear canvas for new vehicles
                ctx.clearRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);
            }
        }
        
        // Animation loop
        let lastTime = 0;
        let animationId;
        
        function animate(currentTime) {
            const deltaTime = (currentTime - lastTime) / 16.67; // Normalize to 60fps
            lastTime = currentTime;
            
            update(deltaTime);
            draw();
            
            // Continue animation loop
            if (simulationState !== 'RESTARTING' || vehicles.length === 0) {
                animationId = requestAnimationFrame(animate);
            } else {
                // If we're in RESTARTING state and timer is done, restart animation
                // This case is handled by initSimulation, which will restart the loop
                animationId = requestAnimationFrame(animate);
            }
        }
        
        // Initialize and start the simulation
        initSimulation();
        animationId = requestAnimationFrame(animate);
        
        // Optional: Pause/resume on blur/focus for performance
        window.addEventListener('blur', () => {
            cancelAnimationFrame(animationId);
        });
        
        window.addEventListener('focus', () => {
            animationId = requestAnimationFrame(animate);
        });
    </script>

    <!-- Optional section for notes -->
    <section id="notes">
        <h3>Implementation Notes</h3>
        <ul>
            <li><strong>Class Design:</strong> Vehicle and ExplosionParticle are implemented as ES6 classes for better organization and encapsulation.</li>
            <li><strong>Collision Detection:</strong> Uses axis-aligned bounding box (AABB) collision detection for simplicity and performance. This works well with the rectangular vehicle shapes.</li>
            <li><strong>State Management:</strong> Uses a simple state machine (RUNNING, EXPLODING, RESTARTING) to control game logic flow and prevent concurrent updates.</li>
            <li><strong>Animation Loop:</strong> Uses requestAnimationFrame with delta time for smooth, consistent animations regardless of frame rate.</li>
            <li><strong>Particle System:</strong> Explosion particles use random velocity, color, and lifespan with a slight gravity effect for more natural movement.</li>
            <li><strong>Wrapping Logic:</strong> Screen wrapping is implemented for all four edges to create a seamless toroidal world.</li>
            <li><strong>Performance:</strong> Uses array filtering to remove expired particles efficiently and avoids unnecessary checks for inactive vehicles.</li>
            <li><strong>Visual Effects:</strong> Explosion includes both particles and animated "BOOM" text with a radial gradient glow effect.</li>
            <li><strong>Reset Timing:</strong> Explosion lasts 3 seconds, followed by a 1.5 second delay before restarting to give user time to see the effect.</li>
        </ul>
    </section>
</body>
</html>
```

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: Qwen3-Next-80B-A3B-Instruct-UD-Q3_K_XL.gguf -->
<!-- Prompt: vehicles.md -->
<!-- Time: 46.73s -->
<!-- Fallback: False -->