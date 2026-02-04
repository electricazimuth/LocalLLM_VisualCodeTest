```html
<!DOCTYPE html>
<html>
<head>
    <title>Aquarium Simulation</title>
    <style>
        body { margin: 0; overflow: hidden; background-color: #e0f7fa; } /* Light blue background */
        canvas { display: block; margin: 20px auto; border: 1px solid #888; background-color: rgb(207, 247, 255); } /* blue water */
    </style>
</head>
<body>
    <canvas id="simulationCanvas" width="800" height="600"></canvas>

    <script>
        const canvas = document.getElementById('simulationCanvas');
        const ctx = canvas.getContext('2d');
        const W = canvas.width;
        const H = canvas.height;

        // Fish class to represent individual fish with autonomous behavior
        class Fish {
            constructor(x, y, size, color) {
                this.x = x || Math.random() * W;
                this.y = y || Math.random() * H;
                this.size = size || 15 + Math.random() * 20; // Random size between 15-35
                this.color = color || this.getRandomColor();
                this.speed = 1.5 + Math.random() * 1.5; // Speed between 1.5-3
                this.angle = Math.random() * Math.PI * 2; // Random starting angle
                this.turnRate = 0.01 + Math.random() * 0.03; // Random turning sensitivity
                this.wiggle = 0; // For tail wiggle animation
                this.wiggleSpeed = 0.1 + Math.random() * 0.2; // Different wiggle speeds for realism
                this.wiggleAmplitude = 0.1 + Math.random() * 0.2; // Different wiggle amplitude
                
                // For boundary avoidance
                this.boundaryAvoidance = 50; // Distance to start avoiding boundaries
                this.avoidanceStrength = 0.03;
                
                // For wandering behavior
                this.wanderAngle = 0;
                this.wanderRadius = 30;
                this.wanderDistance = 40;
            }

            getRandomColor() {
                const colors = [
                    '#FFB347', '#FF8000', '#FF6666', '#FFB366',
                    '#99CCFF', '#6699CC', '#336699', '#88CCFF',
                    '#99CC99', '#4D9480', '#B3E6B3', '#FFE5B4'
                ];
                return colors[Math.floor(Math.random() * colors.length)];
            }

            update(deltaTime) {
                // Update wiggle for tail animation
                this.wiggle += this.wiggleSpeed * deltaTime;
                
                // Wander behavior - slowly change direction
                this.wanderAngle += Math.random() * 0.01 - 0.005; // Small random variation
                const wanderOffsetX = Math.cos(this.wanderAngle) * this.wanderRadius;
                const wanderOffsetY = Math.sin(this.wanderAngle) * this.wanderRadius;
                
                // Add wandering component to current direction
                this.angle += this.turnRate * (wanderOffsetX / this.wanderRadius);
                
                // Boundary avoidance
                let avoidX = 0;
                let avoidY = 0;
                
                if (this.x < this.boundaryAvoidance) {
                    avoidX = this.avoidanceStrength;
                } else if (this.x > W - this.boundaryAvoidance) {
                    avoidX = -this.avoidanceStrength;
                }
                
                if (this.y < this.boundaryAvoidance) {
                    avoidY = this.avoidanceStrength;
                } else if (this.y > H - this.boundaryAvoidance) {
                    avoidY = -this.avoidanceStrength;
                }
                
                // Apply boundary avoidance to angle
                this.angle += avoidX * deltaTime + avoidY * deltaTime;
                
                // Update position based on angle and speed
                this.x += Math.cos(this.angle) * this.speed * deltaTime;
                this.y += Math.sin(this.angle) * this.speed * deltaTime;
                
                // Ensure fish stays within canvas bounds
                if (this.x < 0) this.x = 0;
                if (this.x > W) this.x = W;
                if (this.y < 0) this.y = 0;
                if (this.y > H) this.y = H;
                
                // Ensure the fish doesn't get too close to the edge (soft bounce)
                const borderMargin = 2;
                if (this.x < borderMargin) this.angle = Math.PI - this.angle;
                if (this.x > W - borderMargin) this.angle = Math.PI - this.angle;
                if (this.y < borderMargin) this.angle = -this.angle;
                if (this.y > H - borderMargin) this.angle = -this.angle;
            }

            draw() {
                ctx.save();
                
                // Translate and rotate to fish's position and direction
                ctx.translate(this.x, this.y);
                ctx.rotate(this.angle);
                
                // Draw fish body (a fish-shaped oval)
                ctx.beginPath();
                
                // Body: oval shape
                ctx.ellipse(0, 0, this.size * 0.4, this.size * 0.25, 0, 0, Math.PI * 2);
                
                // Fill with color
                ctx.fillStyle = this.color;
                ctx.fill();
                
                // Tail wiggle effect
                ctx.save();
                ctx.translate(this.size * -0.4, 0);
                ctx.rotate(Math.sin(this.wiggle) * this.wiggleAmplitude);
                
                // Tail
                ctx.beginPath();
                ctx.moveTo(0, 0);
                ctx.bezierCurveTo(
                    -this.size * 0.1, -this.size * 0.05,
                    -this.size * 0.3, -this.size * 0.1,
                    -this.size * 0.5, 0
                );
                ctx.bezierCurveTo(
                    -this.size * 0.3, this.size * 0.1,
                    -this.size * 0.1, this.size * 0.05,
                    0, 0
                );
                ctx.fillStyle = this.color;
                ctx.fill();
                ctx.restore();
                
                // Eye
                ctx.beginPath();
                ctx.arc(this.size * 0.25, -this.size * 0.05, this.size * 0.05, 0, Math.PI * 2);
                ctx.fillStyle = 'white';
                ctx.fill();
                
                // Pupil
                ctx.beginPath();
                ctx.arc(this.size * 0.27, -this.size * 0.05, this.size * 0.02, 0, Math.PI * 2);
                ctx.fillStyle = 'black';
                ctx.fill();
                
                // Fins
                ctx.beginPath();
                ctx.moveTo(this.size * 0.15, this.size * 0.15);
                ctx.bezierCurveTo(
                    this.size * 0.2, this.size * 0.25,
                    this.size * 0.25, this.size * 0.2,
                    this.size * 0.25, this.size * 0.2
                );
                ctx.fillStyle = this.color;
                ctx.fill();
                
                ctx.beginPath();
                ctx.moveTo(this.size * 0.15, -this.size * 0.15);
                ctx.bezierCurveTo(
                    this.size * 0.2, -this.size * 0.25,
                    this.size * 0.25, -this.size * 0.2,
                    this.size * 0.25, -this.size * 0.2
                );
                ctx.fillStyle = this.color;
                ctx.fill();
                
                ctx.restore();
            }
        }

        // Create fish array
        const fishCount = 12;
        const fish = [];

        // Initialize fish with random positions and properties
        for (let i = 0; i < fishCount; i++) {
            fish.push(new Fish());
        }

        // Add some static background elements
        const plants = [];
        for (let i = 0; i < 6; i++) {
            plants.push({
                x: Math.random() * W,
                y: H - 20 - Math.random() * 80,
                height: 30 + Math.random() * 60,
                width: 3 + Math.random() * 7,
                color: 'rgb(0, 128, 0)'
            });
        }

        const rocks = [];
        for (let i = 0; i < 8; i++) {
            rocks.push({
                x: Math.random() * W,
                y: H - 50 - Math.random() * 100,
                size: 10 + Math.random() * 20,
                color: 'rgb(128, 128, 128)'
            });
        }

        let lastTimestamp = 0;
        let deltaTime = 16; // Default to ~60 FPS

        function gameLoop(timestamp) {
            // Calculate delta time for frame-rate independent movement
            deltaTime = (timestamp - lastTimestamp) / 16.666; // Normalize to ~60fps
            lastTimestamp = timestamp;
            
            // Limit delta time to prevent large jumps
            deltaTime = Math.min(deltaTime, 5);

            // Clear canvas with water color
            ctx.clearRect(0, 0, W, H);
            
            // Draw background elements
            drawBackground();

            // Update and draw each fish
            for (const f of fish) {
                f.update(deltaTime);
                f.draw();
            }
            
            // Continue animation loop
            requestAnimationFrame(gameLoop);
        }

        function drawBackground() {
            // Draw water texture with subtle gradient (optional)
            const gradient = ctx.createLinearGradient(0, 0, 0, H);
            gradient.addColorStop(0, 'rgba(190, 230, 255, 0.8)');
            gradient.addColorStop(1, 'rgba(150, 200, 230, 0.6)');
            ctx.fillStyle = gradient;
            ctx.fillRect(0, 0, W, H);
            
            // Draw plants
            for (const plant of plants) {
                ctx.save();
                ctx.translate(plant.x, plant.y);
                ctx.rotate(Math.sin(Date.now() * 0.001) * 0.05); // Slight swaying motion
                
                ctx.fillStyle = plant.color;
                ctx.beginPath();
                ctx.moveTo(0, 0);
                ctx.bezierCurveTo(
                    -plant.width, -plant.height * 0.6,
                    plant.width, -plant.height * 0.4,
                    0, -plant.height
                );
                ctx.bezierCurveTo(
                    plant.width, -plant.height * 0.4,
                    -plant.width, -plant.height * 0.6,
                    0, 0
                );
                ctx.fill();
                
                // Draw leaf details
                ctx.fillStyle = 'rgba(0, 100, 0, 0.5)';
                ctx.beginPath();
                ctx.moveTo(-plant.width * 0.3, -plant.height * 0.2);
                ctx.bezierCurveTo(
                    -plant.width * 0.2, -plant.height * 0.6,
                    plant.width * 0.2, -plant.height * 0.6,
                    plant.width * 0.3, -plant.height * 0.2
                );
                ctx.lineTo(0, 0);
                ctx.fill();
                
                ctx.restore();
            }
            
            // Draw rocks
            for (const rock of rocks) {
                ctx.fillStyle = rock.color;
                ctx.beginPath();
                ctx.ellipse(rock.x, rock.y, rock.size, rock.size * 0.7, 0, 0, Math.PI * 2);
                ctx.fill();
                
                // Add some subtle highlight to rocks
                ctx.fillStyle = 'rgba(255, 255, 255, 0.2)';
                ctx.beginPath();
                ctx.ellipse(rock.x - rock.size * 0.2, rock.y - rock.size * 0.2, rock.size * 0.3, rock.size * 0.2, 0, 0, Math.PI * 2);
                ctx.fill();
            }
            
            // Add some air bubbles
            const bubbles = Math.min(8, Math.floor(Date.now() / 500) % 8);
            for (let i = 0; i < bubbles; i++) {
                const x = Math.random() * W;
                const y = H - 50 - Math.random() * 100;
                const size = 2 + Math.random() * 5;
                const alpha = 0.3 + Math.random() * 0.4;
                
                ctx.fillStyle = `rgba(255, 255, 255, ${alpha})`;
                ctx.beginPath();
                ctx.arc(x, y, size, 0, Math.PI * 2);
                ctx.fill();
            }
        }

        // Start the animation loop
        requestAnimationFrame(gameLoop);
    </script>

    <section id="notes">
        <h3>Aquarium Simulation Notes</h3>
        <p><strong>Implementation Approach:</strong></p>
        <ul>
            <li><strong>Object-Oriented Design:</strong> Created a Fish class to encapsulate state and behavior, promoting code reusability and maintainability.</li>
            <li><strong>Autonomous Movement:</strong> Implemented wandering behavior with a sinusoidal component to generate natural direction changes, avoiding linear motion.</li>
            <li><strong>Boundary Handling:</strong> Used avoidance zones with smooth directional adjustments instead of hard flips, creating more natural turning at edges.</li>
            <li><strong>Delta Time:</strong> Implemented frame-rate independent movement by calculating deltaTime from requestAnimationFrame timestamps, ensuring consistent speed across different devices.</li>
            <li><strong>Visual Realism:</strong> Added tail wiggle animation synchronized with fish movement, detailed fish anatomy (eyes, fins), and subtle background elements (plants, rocks, bubbles) for a calming aquarium atmosphere.</li>
            <li><strong>Performance:</strong> All rendering and updates occur within a single animation loop using requestAnimationFrame for optimal performance.</li>
            <li><strong>Visual Variation:</strong> Each fish has randomized size, color, speed, and wiggle properties for realistic diversity.</li>
        </ul>
    </section>
</body>
</html>
```

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: Qwen3-Next-80B-A3B-Instruct-UD-Q3_K_XL.gguf -->
<!-- Prompt: aquarium.md -->
<!-- Time: 47.81s -->
<!-- Fallback: False -->