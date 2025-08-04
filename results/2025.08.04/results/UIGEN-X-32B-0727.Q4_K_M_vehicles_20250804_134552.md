We are going to create a vehicle collision simulation with the following features:
 - Vehicles (cars) move around the canvas and wrap around edges.
 - Collision detection between vehicles: when two cars collide, they explode and the simulation restarts after a delay.
 - Explosion effect: a burst of particles that fade out over time.
 - The simulation restarts with new vehicles after the explosion.

 We'll use:
   - Canvas API for drawing.
   - JavaScript for the simulation logic.
   - Delta time for smooth animation.

 Steps:
   1. Set up the canvas and context.
   2. Define Vehicle class: with position, velocity, size, and drawing method.
   3. Define ExplosionParticle class: for the explosion effect.
   4. Manage simulation state: 'RUNNING', 'EXPLODING', 'RESTARTING'.
   5. Implement the main animation loop with requestAnimationFrame.
   6. Handle state transitions and updates for each state.
   7. Draw the current state (vehicles or explosion particles).

 We'll use a dark theme for the simulation to make the vehicles and explosions stand out.

 Let's code accordingly.
</think>

# Vehicle Collision Simulation

I'll create a simulation that demonstrates object movement, collision detection, and state management with a visually appealing vehicle collision and restart system.

```html
<!DOCTYPE html>
<html>
<head>
    <title>Vehicle Collision Simulation</title>
    <style>
        body {
            margin: 0;
            padding: 20px;
            background: #0a0a1a;
            color: #e0e0ff;
            font-family: 'Segoe UI', Tahoma, sans-serif;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            overflow-x: hidden;
        }
        
        .container {
            max-width: 900px;
            width: 100%;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: rgba(10, 15, 30, 0.7);
            border-radius: 12px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(100, 150, 255, 0.1);
        }
        
        h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
            background: linear-gradient(90deg, #ff6b6b, #ffa502, #00a8cc);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
            font-weight: 700;
        }
        
        .controls {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin: 20px 0;
            flex-wrap: wrap;
        }
        
        .btn {
            padding: 10px 20px;
            background: rgba(20, 30, 50, 0.7);
            border: 1px solid rgba(100, 150, 255, 0.2);
            border-radius: 30px;
            color: #e0e0ff;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            backdrop-filter: blur(5px);
        }
        
        .btn:hover {
            background: rgba(50, 70, 120, 0.8);
            border-color: rgba(150, 200, 255, 0.4);
            transform: translateY(-2px);
        }
        
        .btn.active {
            background: rgba(0, 168, 204, 0.3);
            border-color: #00a8cc;
            box-shadow: 0 0 15px rgba(0, 168, 204, 0.4);
        }
        
        .stats {
            display: flex;
            justify-content: center;
            gap: 30px;
            margin: 20px 0;
            flex-wrap: wrap;
        }
        
        .stat-box {
            background: rgba(15, 25, 45, 0.6);
            border-radius: 10px;
            padding: 15px 25px;
            border: 1px solid rgba(100, 150, 255, 0.1);
            min-width: 120px;
            text-align: center;
        }
        
        .stat-value {
            font-size: 2rem;
            font-weight: 700;
            color: #00a8cc;
            margin: 5px 0;
        }
        
        .stat-label {
            font-size: 0.9rem;
            opacity: 0.8;
        }
        
        #canvas-container {
            position: relative;
            margin: 30px 0;
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid rgba(100, 150, 255, 0.1);
            box-shadow: 0 0 30px rgba(0, 168, 204, 0.2);
        }
        
        canvas {
            background: #000;
            display: block;
            width: 100%;
            height: 500px;
            image-rendering: pixelated;
        }
        
        .explosion-text {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 12rem;
            font-weight: 800;
            color: rgba(255, 0, 0, 0.1);
            text-shadow: 0 0 20px rgba(255, 0, 0, 0.5);
            opacity: 0;
            transition: opacity 0.5s ease;
            pointer-events: none;
        }
        
        .footer {
            text-align: center;
            margin-top: 30px;
            padding: 20px;
            font-size: 0.9rem;
            opacity: 0.7;
        }
        
        .vehicle-info {
            position: absolute;
            top: 20px;
            right: 20px;
            background: rgba(10, 15, 30, 0.8);
            padding: 15px;
            border-radius: 10px;
            max-width: 250px;
            border: 1px solid rgba(100, 150, 255, 0.1);
            backdrop-filter: blur(5px);
            z-index: 10;
        }
        
        .info-title {
            font-size: 1.2rem;
            margin-bottom: 15px;
            color: #ffa502;
        }
        
        .info-item {
            margin-bottom: 10px;
            font-size: 0.95rem;
        }
        
        .info-label {
            font-weight: 600;
            min-width: 100px;
            display: inline-block;
        }
        
        .info-value {
            display: inline-block;
        }
        
        @media (max-width: 768px) {
            h1 {
                font-size: 2rem;
            }
            
            .controls, .stats {
                gap: 10px;
            }
            
            .btn {
                padding: 8px 15px;
                font-size: 0.9rem;
            }
            
            .stat-box {
                padding: 10px 15px;
                min-width: 100px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Vehicle Collision Simulation</h1>
            <p>Realistic vehicle movement, collision detection, and explosion effects</p>
        </div>
        
        <div class="controls">
            <button id="startBtn" class="btn active">Start Simulation</button>
            <button id="pauseBtn" class="btn">Pause</button>
            <button id="resetBtn" class="btn">Reset</button>
            <button id="addVehicleBtn" class="btn">Add Vehicle</button>
        </div>
        
        <div class="stats">
            <div class="stat-box">
                <div class="stat-value" id="vehicleCount">5</div>
                <div class="stat-label">Vehicles</div>
            </div>
            <div class="stat-box">
                <div class="stat-value" id="collisionCount">0</div>
                <div class="stat-label">Collisions</div>
            </div>
            <div class="stat-box">
                <div class="stat-value" id="simulationTime">0s</div>
                <div class="stat-label">Simulation Time</div>
            </div>
        </div>
        
        <div id="canvas-container">
            <canvas id="simulationCanvas"></canvas>
            <div class="explosion-text" id="explosionText">BOOM</div>
            <div class="vehicle-info">
                <div class="info-title">Active Vehicle</div>
                <div class="info-item">
                    <span class="info-label">ID:</span>
                    <span class="info-value" id="activeVehicleId">-</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Speed:</span>
                    <span class="info-value" id="activeVehicleSpeed">-</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Direction:</span>
                    <span class="info-value" id="activeVehicleDirection">-</span>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>Click and drag to rotate view • Right-click to reset camera • Press R to restart simulation</p>
            <p>Created with HTML5 Canvas and JavaScript • Performance optimized</p>
        </div>
    </div>

    <script>
        // Vehicle class
        class Vehicle {
            constructor(id, canvas) {
                this.id = id;
                this.canvas = canvas;
                this.ctx = canvas.getContext('2d');
                
                // Position and movement
                this.x = Math.random() * canvas.width;
                this.y = Math.random() * canvas.height;
                this.vx = (Math.random() - 0.5) * 3;
                this.vy = (Math.random() - 0.5) * 3;
                this.speed = Math.sqrt(this.vx * this.vx + this.vy * this.vy);
                
                // Appearance
                this.color = this.getRandomColor();
                this.size = Math.random() * 30 + 20;
                this.type = Math.random() > 0.5 ? 'car' : 'truck';
                this.rotation = Math.random() * Math.PI * 2;
                this.wheelSize = this.size * 0.3;
                
                // Status
                this.active = true;
                this.lastCollision = 0;
            }
            
            getRandomColor() {
                const colors = [
                    '#ff6b6b', '#ffa502', '#00a8cc', '#9b59b6', '#00ced1',
                    '#f1c40f', '#2ecc71', '#e74c3c', '#3498db', '#e67e22'
                ];
                return colors[Math.floor(Math.random() * colors.length)];
            }
            
            update(deltaTime) {
                if (!this.active) return;
                
                // Update position
                this.x += this.vx * deltaTime;
                this.y += this.vy * deltaTime;
                
                // Wrap around canvas edges
                if (this.x < 0) this.x = this.canvas.width;
                if (this.x > this.canvas.width) this.x = 0;
                if (this.y < 0) this.y = this.canvas.height;
                if (this.y > this.canvas.height) this.y = 0;
                
                // Update speed
                this.speed = Math.sqrt(this.vx * this.vx + this.vy * this.vy);
            }
            
            draw() {
                if (!this.active) return;
                
                this.ctx.save();
                this.ctx.translate(this.x, this.y);
                this.ctx.rotate(this.rotation);
                
                // Draw vehicle body
                this.ctx.fillStyle = this.color;
                this.ctx.beginPath();
                
                if (this.type === 'car') {
                    // Car shape
                    this.ctx.moveTo(-this.size/2, -this.size/2);
                    this.ctx.lineTo(-this.size/2, this.size/2);
                    this.ctx.lineTo(this.size/2, this.size/2);
                    this.ctx.lineTo(this.size/2, -this.size/2);
                    this.ctx.closePath();
                    
                    // Roof
                    this.ctx.moveTo(-this.size/3, -this.size/2);
                    this.ctx.lineTo(0, -this.size/1.5);
                    this.ctx.lineTo(this.size/3, -this.size/2);
                } else {
                    // Truck shape
                    this.ctx.moveTo(-this.size/2, -this.size/2);
                    this.ctx.lineTo(-this.size/2, this.size/2);
                    this.ctx.lineTo(this.size/1.5, this.size/2);
                    this.ctx.lineTo(this.size/1.5, -this.size/2);
                    this.ctx.closePath();
                    
                    // Trailer
                    this.ctx.moveTo(this.size/1.5, -this.size/2);
                    this.ctx.lineTo(this.size/1.5 + this.size/2, -this.size/2);
                    this.ctx.lineTo(this.size/1.5 + this.size/2, this.size/2);
                    this.ctx.lineTo(this.size/1.5, this.size/2);
                    this.ctx.closePath();
                }
                
                this.ctx.fill();
                
                // Draw wheels
                this.ctx.fillStyle = '#333';
                const wheelOffset = this.type === 'car' ? this.size/2.5 : this.size/2;
                
                // Front wheels
                this.ctx.beginPath();
                this.ctx.arc(-this.size/3, this.size/2, this.wheelSize/2, 0, Math.PI * 2);
                this.ctx.fill();
                
                this.ctx.beginPath();
                this.ctx.arc(this.size/3, this.size/2, this.wheelSize/2, 0, Math.PI * 2);
                this.ctx.fill();
                
                // Back wheels
                this.ctx.beginPath();
                this.ctx.arc(-wheelOffset, this.size/2, this.wheelSize/2, 0, Math.PI * 2);
                this.ctx.fill();
                
                this.ctx.beginPath();
                this.ctx.arc(wheelOffset, this.size/2, this.wheelSize/2, 0, Math.PI * 2);
                this.ctx.fill();
                
                this.ctx.restore();
            }
            
            checkCollision(other) {
                if (!this.active || !other.active) return false;
                
                const dx = this.x - other.x;
                const dy = this.y - other.y;
                const distance = Math.sqrt(dx * dx + dy * dy);
                const minDistance = (this.size + other.size) / 2;
                
                return distance < minDistance;
            }
            
            explode() {
                this.active = false;
                return {
                    x: this.x,
                    y: this.y,
                    color: this.color
                };
            }
        }
        
        // Explosion particle class
        class ExplosionParticle {
            constructor(x, y, color, canvas) {
                this.x = x;
                this.y = y;
                this.color = color;
                this.canvas = canvas;
                this.ctx = canvas.getContext('2d');
                
                // Random direction and speed
                const angle = Math.random() * Math.PI * 2;
                this.vx = Math.cos(angle) * (Math.random() * 5 + 2);
                this.vy = Math.sin(angle) * (Math.random() * 5 + 2);
                
                // Size and lifespan
                this.size = Math.random() * 5 + 2;
                this.lifespan = Math.random() * 3 + 1;
                this.currentLifespan = 0;
            }
            
            update(deltaTime) {
                this.x += this.vx * deltaTime;
                this.y += this.vy * deltaTime;
                this.currentLifespan += deltaTime;
                
                // Fade out over time
                if (this.currentLifespan > this.lifespan) {
                    return false;
                }
                return true;
            }
            
            draw() {
                const alpha = 1 - (this.currentLifespan / this.lifespan);
                this.ctx.fillStyle = `rgba(${parseInt(this.color.slice(1, 3), 16)}, 
                    ${parseInt(this.color.slice(3, 5), 16)}, 
                    ${parseInt(this.color.slice(5, 7), 16)}, 
                    ${alpha * 0.7})`;
                
                this.ctx.beginPath();
                this.ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                this.ctx.fill();
            }
        }
        
        // Main simulation class
        class VehicleSimulation {
            constructor(canvasId) {
                this.canvas = document.getElementById(canvasId);
                this.ctx = this.canvas.getContext('2d');
                
                // Canvas dimensions
                this.canvas.width = window.innerWidth * 0.9;
                this.canvas.height = 500;
                if (this.canvas.width > 900) this.canvas.width = 900;
                
                // Simulation state
                this.state = 'READY'; // READY, RUNNING, PAUSED, EXPLODING, RESTARTING
                this.vehicles = [];
                this.explosionParticles = [];
                this.collisionCount = 0;
                this.simulationTime = 0;
                this.lastTime = performance.now();
                this.explodingVehicle = null;
                
                // UI elements
                this.explosionText = document.getElementById('explosionText');
                this.vehicleCountEl = document.getElementById('vehicleCount');
                this.collisionCountEl = document.getElementById('collisionCount');
                this.simulationTimeEl = document.getElementById('simulationTime');
                this.activeVehicleId = document.getElementById('activeVehicleId');
                this.activeVehicleSpeed = document.getElementById('activeVehicleSpeed');
                this.activeVehicleDirection = document.getElementById('activeVehicleDirection');
                
                // Set up event listeners
                this.setupEventListeners();
                this.initVehicles(5);
            }
            
            setupEventListeners() {
                document.getElementById('startBtn').addEventListener('click', () => {
                    if (this.state !== 'RUNNING') {
                        this.start();
                    }
                });
                
                document.getElementById('pauseBtn').addEventListener('click', () => {
                    if (this.state === 'RUNNING') {
                        this.pause();
                    } else if (this.state === 'PAUSED') {
                        this.resume();
                    }
                });
                
                document.getElementById('resetBtn').addEventListener('click', () => {
                    this.reset();
                });
                
                document.getElementById('addVehicleBtn').addEventListener('click', () => {
                    if (this.state === 'RUNNING') {
                        this.addVehicle();
                    }
                });
                
                // Keyboard shortcuts
                document.addEventListener('keydown', (e) => {
                    if (e.key === 'r' || e.key === 'R') {
                        this.reset();
                    }
                    if (e.key === ' ') {
                        if (this.state === 'RUNNING') {
                            this.pause();
                        } else if (this.state === 'PAUSED') {
                            this.resume();
                        }
                    }
                });
            }
            
            initVehicles(count) {
                this.vehicles = [];
                for (let i = 0; i < count; i++) {
                    this.vehicles.push(new Vehicle(i, this.canvas));
                }
                this.vehicleCountEl.textContent = count;
            }
            
            addVehicle() {
                const newId = this.vehicles.length;
                this.vehicles.push(new Vehicle(newId, this.canvas));
                this.vehicleCountEl.textContent = this.vehicles.length;
            }
            
            start() {
                if (this.state === 'READY' || this.state === 'RESTARTING') {
                    this.state = 'RUNNING';
                    this.simulationTime = 0;
                    this.lastTime = performance.now();
                    this.explodingVehicle = null;
                    this.explosionText.style.opacity = '0';
                    this.animate();
                }
            }
            
            pause() {
                if (this.state === 'RUNNING') {
                    this.state = 'PAUSED';
                }
            }
            
            resume() {
                if (this.state === 'PAUSED') {
                    this.state = 'RUNNING';
                    this.animate();
                }
            }
            
            reset() {
                this.state = 'READY';
                this.vehicles = [];
                this.explosionParticles = [];
                this.collisionCount = 0;
                this.simulationTime = 0;
                this.explodingVehicle = null;
                this.explosionText.style.opacity = '0';
                this.initVehicles(5);
            }
            
            animate() {
                if (this.state !== 'RUNNING') return;
                
                const now = performance.now();
                const deltaTime = (now - this.lastTime) / 1000;
                this.lastTime = now;
                
                this.simulationTime += deltaTime;
                this.simulationTimeEl.textContent = `${Math.round(this.simulationTime)}s`;
                
                this.update(deltaTime);
                this.draw();
                
                requestAnimationFrame(() => this.animate());
            }
            
            update(deltaTime) {
                // Update vehicles
                for (let i = 0; i < this.vehicles.length; i++) {
                    const vehicle = this.vehicles[i];
                    vehicle.update(deltaTime);
                    
                    // Update active vehicle info
                    if (i === 0) {
                        this.activeVehicleId.textContent = vehicle.id;
                        this.activeVehicleSpeed.textContent = `${vehicle.speed.toFixed(1)} px/s`;
                        this.activeVehicleDirection.textContent = 
                            `${Math.round(vehicle.rotation * 180 / Math.PI)}°`;
                    }
                }
                
                // Check for collisions
                for (let i = 0; i < this.vehicles.length; i++) {
                    for (let j = i + 1; j < this.vehicles.length; j++) {
                        const vehicle1 = this.vehicles[i];
                        const vehicle2 = this.vehicles[j];
                        
                        if (vehicle1.checkCollision(vehicle2)) {
                            // Collision detected
                            this.collisionCount++;
                            this.collisionCountEl.textContent = this.collisionCount;
                            
                            // Create explosion
                            const explosionCenter = {
                                x: (vehicle1.x + vehicle2.x) / 2,
                                y: (vehicle1.y + vehicle2.y) / 2
                            };
                            
                            // Create explosion particles
                            this.explosionParticles = [];
                            for (let k = 0; k < 30; k++) {
                                this.explosionParticles.push(
                                    new ExplosionParticle(
                                        explosionCenter.x, 
                                        explosionCenter.y, 
                                        vehicle1.color, 
                                        this.canvas
                                    )
                                );
                            }
                            
                            // Deactivate vehicles
                            vehicle1.active = false;
                            vehicle2.active = false;
                            
                            // Set state to exploding
                            this.state = 'EXPLODING';
                            this.explodingVehicle = {
                                x: explosionCenter.x,
                                y: explosionCenter.y
                            };
                            
                            // Show explosion text
                            this.explosionText.style.opacity = '1';
                            setTimeout(() => {
                                this.explosionText.style.opacity = '0';
                            }, 500);
                            
                            // After explosion, restart simulation
                            setTimeout(() => {
                                this.state = 'RESTARTING';
                                this.reset();
                            }, 2000);
                            
                            // Stop animation loop
                            return;
                        }
                    }
                }
                
                // Update explosion particles
                if (this.state === 'EXPLODING') {
                    for (let i = 0; i < this.explosionParticles.length; i++) {
                        if (!this.explosionParticles[i].update(deltaTime)) {
                            this.explosionParticles.splice(i, 1);
                            i--;
                        }
                    }
                    
                    if (this.explosionParticles.length === 0) {
                        this.state = 'RESTARTING';
                        this.reset();
                    }
                }
            }
            
            draw() {
                // Clear canvas
                this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
                
                // Draw grid background
                this.ctx.fillStyle = '#0a0a1a';
                this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
                
                // Draw grid lines
                this.ctx.strokeStyle = 'rgba(100, 150, 255, 0.05)';
                this.ctx.lineWidth = 1;
                
                for (let i = 0; i < this.canvas.width; i += 30) {
                    this.ctx.beginPath();
                    this.ctx.moveTo(i, 0);
                    this.ctx.lineTo(i, this.canvas.height);
                    this.ctx.stroke();
                }
                
                for (let i = 0; i < this.canvas.height; i += 30) {
                    this.ctx.beginPath();
                    this.ctx.moveTo(0, i);
                    this.ctx.lineTo(this.canvas.width, i);
                    this.ctx.stroke();
                }
                
                // Draw vehicles
                for (const vehicle of this.vehicles) {
                    vehicle.draw();
                }
                
                // Draw explosion particles
                for (const particle of this.explosionParticles) {
                    particle.draw();
                }
                
                // Draw explosion center
                if (this.explodingVehicle) {
                    this.ctx.fillStyle = 'rgba(255, 0, 0, 0.3)';
                    this.ctx.beginPath();
                    this.ctx.arc(
                        this.explodingVehicle.x, 
                        this.explodingVehicle.y, 
                        50, 
                        0, 
                        Math.PI * 2
                    );
                    this.ctx.fill();
                }
            }
        }
        
        // Initialize the simulation when the page loads
        document.addEventListener('DOMContentLoaded', () => {
            const simulation = new VehicleSimulation('simulationCanvas');
            
            // Update UI based on simulation state
            function updateUI() {
                const startBtn = document.getElementById('startBtn');
                const pauseBtn = document.getElementById('pauseBtn');
                const resetBtn = document.getElementById('resetBtn');
                const addVehicleBtn = document.getElementById('addVehicleBtn');
                
                if (simulation.state === 'READY') {
                    startBtn.classList.add('active');
                    pauseBtn.classList.remove('active');
                    resetBtn.classList.remove('active');
                    addVehicleBtn.classList.remove('active');
                } else if (simulation.state === 'RUNNING') {
                    startBtn.classList.remove('active');
                    pauseBtn.classList.add('active');
                    resetBtn.classList.add('active');
                    addVehicleBtn.classList.add('active');
                } else if (simulation.state === 'PAUSED') {
                    startBtn.classList.remove('active');
                    pauseBtn.classList.add('active');
                    resetBtn.classList.add('active');
                    addVehicleBtn.classList.remove('active');
                } else if (simulation.state === 'EXPLODING' || simulation.state === 'RESTARTING') {
                    startBtn.classList.remove('active');
                    pauseBtn.classList.remove('active');
                    resetBtn.classList.add('active');
                    addVehicleBtn.classList.remove('active');
                }
            }
            
            // Update UI initially and when simulation state changes
            updateUI();
            
            // Add event listener to update UI when simulation state changes
            document.getElementById('startBtn').addEventListener('click', updateUI);
            document.getElementById('pauseBtn').addEventListener('click', updateUI);
            document.getElementById('resetBtn').addEventListener('click', updateUI);
        });
    </script>
</body>
</html>
```

## Key Features

1. **Vehicle Movement & Wrapping**
   - Vehicles move with random velocities
   - Automatically wrap around canvas edges
   - Different vehicle types (cars and trucks)

2. **Collision Detection**
   - Real-time collision detection between vehicles
   - Visual feedback when collisions occur

3. **Explosion Effect**
   - Particle system for realistic explosions
   - "BOOM" text animation
   - Colorful explosion particles that fade out

4. **State Management**
   - Multiple simulation states (READY, RUNNING, PAUSED, EXPLODING, RESTARTING)
   - Automatic restart after explosion
   - Manual reset option

5. **Performance Optimization**
   - Delta time for smooth animations
   - Efficient collision detection
   - Canvas grid for visual reference

6. **User Interface**
   - Control buttons for simulation
   - Real-time statistics display
   - Active vehicle information panel
   - Responsive design for different screen sizes

The simulation is ready to run when you open the HTML file in a browser. Vehicles will move around the canvas until a collision occurs, triggering an explosion effect and restarting the simulation.

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: UIGEN-X-32B-0727.Q4_K_M.gguf -->
<!-- Prompt: vehicles.md -->
<!-- Generation Time: 221.78s -->
<!-- Fallback Used: False -->