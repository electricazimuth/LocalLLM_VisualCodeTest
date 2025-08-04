```html
<!DOCTYPE html>
<html>
<head>
    <title>Chicken Simulation</title>
    <style>
        body { margin: 10px; overflow: hidden; background-color: #eee; }
        canvas { display: block; margin: 20px auto; border: 1px solid #999; background-color: #90ee90; } /* Light green grass background */
    </style>
</head>
<body>
    <canvas id="simulationCanvas" width="512" height="512"></canvas>

    <script>
        // --- YOUR JAVASCRIPT CODE GOES HERE ---

        // Get canvas and context
        const canvas = document.getElementById('simulationCanvas');
        const ctx = canvas.getContext('2d');

        // Constants
        const CHICKEN_RADIUS = 20;
        const EGG_WIDTH = 24;
        const EGG_HEIGHT = 32;
        const CHICKEN_SPEED = 1.5; // pixels per frame
        const MIN_WANDER_TIME = 100; // minimum time between direction changes (frames)
        const MAX_WANDER_TIME = 300; // maximum time between direction changes (frames)
        const LAYING_DURATION = 30; // frames for laying animation
        const EGG_LIFETIME = 120; // frames before egg disappears

        // Chicken class
        class Chicken {
            constructor(x, y) {
                this.x = x;
                this.y = y;
                this.radius = CHICKEN_RADIUS;
                this.vx = 0;
                this.vy = 0;
                this.direction = Math.random() * Math.PI * 2; // radians
                this.state = 'wandering'; // 'wandering', 'laying'
                this.layingTimer = 0;
                this.nextDirectionTime = 0;
                this.layTimer = 0;
                this.layInterval = 120; // frames between egg laying attempts
                this.isLaying = false;
                this.layingFrame = 0;
            }

            // Update chicken state and position
            update(deltaTime, eggs) {
                // Update laying timer
                this.layTimer += 1;

                // Check if it's time to lay an egg (random chance with interval)
                if (this.layTimer >= this.layInterval && Math.random() < 0.02) {
                    this.state = 'laying';
                    this.layingTimer = 0;
                    this.isLaying = true;
                    this.layTimer = 0;
                    this.layingFrame = 0;
                    return; // Skip movement during laying
                }

                // If laying, update laying animation
                if (this.state === 'laying') {
                    this.layingTimer += 1;
                    this.layingFrame += 1;

                    if (this.layingTimer >= LAYING_DURATION) {
                        // Create egg at position behind chicken
                        const eggX = this.x - Math.cos(this.direction) * 10;
                        const eggY = this.y - Math.sin(this.direction) * 10;

                        eggs.push(new Egg(eggX, eggY, this.layingFrame));

                        this.state = 'wandering';
                        this.isLaying = false;
                        this.layingFrame = 0;
                        this.nextDirectionTime = Date.now() + Math.random() * (MAX_WANDER_TIME - MIN_WANDER_TIME) + MIN_WANDER_TIME;
                        return;
                    }
                }

                // Wandering: change direction occasionally
                if (Date.now() >= this.nextDirectionTime) {
                    this.direction = Math.random() * Math.PI * 2;
                    this.nextDirectionTime = Date.now() + Math.random() * (MAX_WANDER_TIME - MIN_WANDER_TIME) + MIN_WANDER_TIME;
                }

                // Update velocity based on direction
                this.vx = Math.cos(this.direction) * CHICKEN_SPEED;
                this.vy = Math.sin(this.direction) * CHICKEN_SPEED;

                // Update position
                this.x += this.vx;
                this.y += this.vy;

                // Boundary handling - keep chicken within canvas
                const padding = this.radius;
                if (this.x < padding) {
                    this.x = padding;
                    this.direction = Math.PI - this.direction; // Reflect
                } else if (this.x > canvas.width - padding) {
                    this.x = canvas.width - padding;
                    this.direction = Math.PI - this.direction;
                }

                if (this.y < padding) {
                    this.y = padding;
                    this.direction = -this.direction;
                } else if (this.y > canvas.height - padding) {
                    this.y = canvas.height - padding;
                    this.direction = -this.direction;
                }
            }

            // Draw chicken with orientation
            draw() {
                ctx.save();
                ctx.translate(this.x, this.y);

                // Chicken body (yellow circle)
                ctx.fillStyle = '#FFD700';
                ctx.beginPath();
                ctx.arc(0, 0, this.radius, 0, Math.PI * 2);
                ctx.fill();

                // Chicken head (smaller circle)
                ctx.fillStyle = '#FFB6C1';
                ctx.beginPath();
                ctx.arc(0, -this.radius * 0.5, this.radius * 0.6, 0, Math.PI * 2);
                ctx.fill();

                // Beak (triangle pointing in direction of movement)
                ctx.fillStyle = '#FF4500';
                const beakLength = this.radius * 0.4;
                const beakWidth = this.radius * 0.3;
                ctx.beginPath();
                ctx.moveTo(0, -this.radius * 0.5);
                ctx.lineTo(beakLength * Math.cos(this.direction), -this.radius * 0.5 + beakLength * Math.sin(this.direction));
                ctx.lineTo(beakLength * Math.cos(this.direction) - beakWidth * Math.sin(this.direction), 
                          -this.radius * 0.5 + beakLength * Math.sin(this.direction) + beakWidth * Math.cos(this.direction));
                ctx.closePath();
                ctx.fill();

                // Eye
                ctx.fillStyle = 'black';
                ctx.beginPath();
                ctx.arc(-this.radius * 0.3, -this.radius * 0.3, this.radius * 0.15, 0, Math.PI * 2);
                ctx.fill();

                // Pupil
                ctx.fillStyle = 'white';
                ctx.beginPath();
                ctx.arc(-this.radius * 0.3, -this.radius * 0.3, this.radius * 0.08, 0, Math.PI * 2);
                ctx.fill();

                // Check if laying - change color slightly
                if (this.isLaying) {
                    ctx.globalAlpha = 0.7;
                    ctx.fillStyle = '#FFA500';
                    ctx.beginPath();
                    ctx.arc(0, 0, this.radius, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.globalAlpha = 1;
                }

                ctx.restore();
            }
        }

        // Egg class
        class Egg {
            constructor(x, y, frame) {
                this.x = x;
                this.y = y;
                this.width = EGG_WIDTH;
                this.height = EGG_HEIGHT;
                this.life = EGG_LIFETIME;
                this.frame = frame;
            }

            // Update egg state
            update() {
                this.life -= 1;
            }

            // Draw egg
            draw() {
                ctx.save();
                ctx.translate(this.x, this.y);
                
                // Egg shape - oval with slight tilt based on laying frame
                const tilt = (this.frame % 10) / 10 * 0.2; // slight wobble
                ctx.rotate(tilt);
                
                ctx.fillStyle = '#FFFACD'; // Light yellow
                ctx.beginPath();
                ctx.ellipse(0, 0, this.width / 2, this.height / 2, 0, 0, Math.PI * 2);
                ctx.fill();
                
                // Egg details - small dark spots
                ctx.fillStyle = '#A0522D';
                ctx.beginPath();
                ctx.arc(-this.width * 0.3, -this.height * 0.2, this.width * 0.1, 0, Math.PI * 2);
                ctx.fill();
                
                ctx.beginPath();
                ctx.arc(this.width * 0.3, this.height * 0.2, this.width * 0.08, 0, Math.PI * 2);
                ctx.fill();
                
                ctx.restore();
            }
        }

        // Initialize simulation
        let chicken = new Chicken(canvas.width / 2, canvas.height / 2);
        let eggs = [];

        // Animation loop
        let lastTime = 0;
        function animate(time) {
            const deltaTime = time - lastTime;
            lastTime = time;

            // Clear canvas with green background
            ctx.fillStyle = '#90ee90';
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            // Update chicken and eggs
            chicken.update(deltaTime, eggs);
            eggs.forEach(egg => {
                egg.update();
            });

            // Remove expired eggs
            eggs = eggs.filter(egg => egg.life > 0);

            // Draw chicken and eggs
            chicken.draw();
            eggs.forEach(egg => egg.draw());

            // Continue animation loop
            requestAnimationFrame(animate);
        }

        // Start animation loop
        requestAnimationFrame(animate);

        // Optional: Add a simple restart button for testing
        // Uncomment below if you want to add a restart button
        /*
        const restartBtn = document.createElement('button');
        restartBtn.textContent = 'Restart Simulation';
        restartBtn.style.position = 'absolute';
        restartBtn.style.top = '10px';
        restartBtn.style.left = '10px';
        restartBtn.onclick = () => {
            chicken = new Chicken(canvas.width / 2, canvas.height / 2);
            eggs = [];
        };
        document.body.appendChild(restartBtn);
        */
    </script>

    <!-- Optional section for notes -->
    <section id="notes">
        <h3>Implementation Notes</h3>
        <ul>
            <li><strong>Object Management:</strong> Used classes for Chicken and Egg with an array to track active eggs.</li>
            <li><strong>Chicken AI:</strong> Implemented wandering behavior with random direction changes, boundary handling via reflection, and a probabilistic egg-laying system.</li>
            <li><strong>Egg Laying:</strong> Triggered by a timer with a small probability (2%) per frame, creating an egg slightly behind the chicken's center.</li>
            <li><strong>Visuals:</strong> Chicken has a yellow body, red beak, and eye details. The beak points in the direction of movement. During laying, the chicken appears slightly darker (orange) and has a visual cue.</li>
            <li><strong>Animation:</strong> Uses requestAnimationFrame with frame-rate independent movement and timing. Delta time is used for smoothness.</li>
            <li><strong>Egg Lifecycle:</strong> Eggs have a lifetime of 120 frames before disappearing.</li>
            <li><strong>Chicken Orientation:</strong> The beak and overall body orientation follow the direction of movement.</li>
            <li><strong>Boundary Handling:</strong> Chicken reflects off canvas edges to stay within bounds.</li>
        </ul>
    </section>
    
</body>
</html>
```

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: Qwen3-30B-A3B-Instruct-2507-UD-Q4_K_XL.gguf -->
<!-- Prompt: chicken.md -->
<!-- Generation Time: 22.46s -->
<!-- Fallback Used: False -->