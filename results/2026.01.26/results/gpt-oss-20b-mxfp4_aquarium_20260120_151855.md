```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Aquarium Simulation</title>
    <style>
        body {
            margin: 0;
            overflow: hidden;
            background-color: #e0f7fa;          /* Light blue sky */
        }
        canvas {
            display: block;
            margin: 20px auto;
            border: 1px solid #888;
            background-color: rgb(207, 247, 255); /* Water colour */
        }
    </style>
</head>
<body>
    <canvas id="simulationCanvas" width="512" height="512"></canvas>

    <script>
        /* -------------------- 1. Setup -------------------- */
        const canvas = document.getElementById('simulationCanvas');
        const ctx = canvas.getContext('2d');
        const W = canvas.width;
        const H = canvas.height;

        /* -------------------- 2. Utility helpers -------------------- */
        // Convert degrees to radians
        const degToRad = d => d * Math.PI / 180;

        // Random number in [min, max]
        const rand = (min, max) => Math.random() * (max - min) + min;

        // Vector normalization (returns {x, y} with length 1)
        const normalize = (x, y) => {
            const len = Math.hypot(x, y);
            return {x: x / len, y: y / len};
        };

        /* -------------------- 3. Fish class -------------------- */
        class Fish {
            constructor() {
                // Initial random position inside the canvas
                this.x = rand(0, W);
                this.y = rand(0, H);

                // Random size (scale factor)
                this.size = rand(0.8, 1.5);

                // Random color
                const h = rand(180, 240); // blueish hues
                const s = rand(60, 90);
                const l = rand(40, 60);
                this.color = `hsl(${h}, ${s}%, ${l}%)`;

                // Random speed (pixels per second)
                this.speed = rand(40, 120);

                // Base heading (radians)
                this.angle = Math.atan2(rand(-1, 1), rand(-1, 1));

                // Wander behaviour
                this.wanderAngle = 0;            // current wander offset
                this.wanderStrength = 0.6;       // radians per second
                this.wanderChangeSpeed = 0.3;    // how fast wander angle changes

                // Boundary steering
                this.boundarySteer = 2.0;        // steering speed multiplier

                // Tail wiggle (for visual interest)
                this.tailWiggleSpeed = 4;        // wiggles per second
                this.tailWiggleAmplitude = 0.2;  // radians
            }

            update(dt, globalTime) {
                /* ---- Wandering ---- */
                // Randomly change the wander angle gradually
                const wanderChange = (Math.random() - 0.5) * this.wanderChangeSpeed * dt;
                this.wanderAngle += wanderChange;

                // Clamp wanderAngle to a reasonable range
                const maxWander = Math.PI / 4; // 45°
                if (this.wanderAngle > maxWander) this.wanderAngle = maxWander;
                if (this.wanderAngle < -maxWander) this.wanderAngle = -maxWander;

                /* ---- Boundary detection & steering ---- */
                const margin = 20; // distance from edge that triggers steering
                let steer = 0;

                if (this.x < margin) steer += 1;
                if (this.x > W - margin) steer -= 1;
                if (this.y < margin) steer += 1;
                if (this.y > H - margin) steer -= 1;

                // If near a boundary, steer towards the centre
                if (steer !== 0) {
                    const toCenterX = (W / 2) - this.x;
                    const toCenterY = (H / 2) - this.y;
                    const desiredAngle = Math.atan2(toCenterY, toCenterX);
                    const angleDiff = this._angleDifference(desiredAngle, this.angle);
                    // Apply steering proportionally
                    this.angle += angleDiff * this.boundarySteer * dt;
                }

                /* ---- Update heading with wander ---- */
                this.angle += this.wanderAngle;

                /* ---- Update position ---- */
                this.x += Math.cos(this.angle) * this.speed * dt;
                this.y += Math.sin(this.angle) * this.speed * dt;

                /* ---- Keep fish inside canvas (just in case) ---- */
                if (this.x < 0) this.x = 0;
                if (this.x > W) this.x = W;
                if (this.y < 0) this.y = 0;
                if (this.y > H) this.y = H;
            }

            // Helper to calculate smallest difference between two angles
            _angleDifference(a, b) {
                let diff = a - b;
                while (diff > Math.PI) diff -= 2 * Math.PI;
                while (diff < -Math.PI) diff += 2 * Math.PI;
                return diff;
            }

            draw(ctx, globalTime) {
                ctx.save();
                ctx.translate(this.x, this.y);
                ctx.rotate(this.angle);

                /* ---- Body (triangle) ---- */
                ctx.beginPath();
                ctx.moveTo(0, 0);                         // tip
                ctx.lineTo(-20 * this.size, 10 * this.size);   // bottom back
                ctx.lineTo(-20 * this.size, -10 * this.size);  // top back
                ctx.closePath();

                ctx.fillStyle = this.color;
                ctx.fill();

                /* ---- Eye (small circle on the front) ---- */
                ctx.beginPath();
                ctx.arc(5 * this.size, 0, 2 * this.size, 0, 2 * Math.PI);
                ctx.fillStyle = 'white';
                ctx.fill();
                ctx.beginPath();
                ctx.arc(5 * this.size, 0, 1 * this.size, 0, 2 * Math.PI);
                ctx.fillStyle = 'black';
                ctx.fill();

                /* ---- Tail wiggle (small triangle) ---- */
                const tailAngle = Math.sin(globalTime * this.tailWiggleSpeed) * this.tailWiggleAmplitude;
                ctx.save();
                ctx.translate(-20 * this.size, 0);
                ctx.rotate(tailAngle);
                ctx.beginPath();
                ctx.moveTo(0, 0);
                ctx.lineTo(-10 * this.size, 5 * this.size);
                ctx.lineTo(-10 * this.size, -5 * this.size);
                ctx.closePath();
                ctx.fillStyle = this.color;
                ctx.fill();
                ctx.restore();

                ctx.restore();
            }
        }

        /* -------------------- 4. Simulation setup -------------------- */
        const fishCount = 12;
        const fishArray = [];

        for (let i = 0; i < fishCount; i++) {
            fishArray.push(new Fish());
        }

        /* -------------------- 5. Animation loop -------------------- */
        let lastTimestamp = 0;

        function gameLoop(timestamp) {
            if (!lastTimestamp) lastTimestamp = timestamp;
            const dt = (timestamp - lastTimestamp) / 1000; // delta time in seconds
            lastTimestamp = timestamp;

            // Clear canvas
            ctx.fillStyle = '#cfefff'; // water colour
            ctx.fillRect(0, 0, W, H);

            // Update & draw each fish
            for (const fish of fishArray) {
                fish.update(dt, timestamp / 1000);
                fish.draw(ctx, timestamp / 1000);
            }

            requestAnimationFrame(gameLoop);
        }

        requestAnimationFrame(gameLoop);
    </script>

    <section id="notes">
        <h2>Developer Notes</h2>
        <ul>
            <li>All fish are instances of the <code>Fish</code> class, encapsulating position, velocity, size, colour, and behaviour.</li>
            <li>Wandering is achieved by slowly varying a “wander angle” that is added to the fish’s heading.</li>
            <li>Boundary steering gently nudges fish back toward the centre when they get close to the edge.</li>
            <li>Delta‑time (dt) ensures frame‑rate independent movement.</li>
            <li>Tail wiggle uses a sine wave tied to global time for a subtle natural motion.</li>
            <li>The canvas background is a light blue to represent water; fish are rendered as simple rotated triangles.</li>
        </ul>
    </section>
</body>
</html>
```

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: gpt-oss-20b-mxfp4.gguf -->
<!-- Prompt: aquarium.md -->
<!-- Generation Time: 18.58s -->
<!-- Fallback Used: False -->