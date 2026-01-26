```html
<!DOCTYPE html>
<html>
<head>
    <title>Chicken Simulation</title>
    <style>
        body { margin: 10px; overflow: hidden; background-color: #eee; }
        canvas { display: block; margin: 20px auto; border: 1px solid #999; background-color: #90ee90; }
    </style>
</head>
<body>
    <canvas id="simulationCanvas" width="512" height="512"></canvas>

    <script>
        /* --------------------
         *  Chicken Simulation
         *  --------------------
         *
         *  The simulation runs a single chicken that wanders around the
         *  canvas.  Every few seconds it pauses, "lays" an egg, and
         *  resumes its wandering.  Eggs are static once laid.
         *
         *  Key features:
         *  - Delta‑time based animation for frame‑rate independent motion.
         *  - Simple wandering AI (random direction changes, wall reflection).
         *  - State machine for chicken: 'wandering' vs 'laying'.
         *  - Eggs stored in an array; each egg is drawn as a small oval.
         *  - Chicken faces the direction of travel; a small beak shows the
         *    direction.
         *  - During laying the chicken briefly changes color.
         */

        const canvas = document.getElementById('simulationCanvas');
        const ctx = canvas.getContext('2d');

        // ----- Egg class -----
        class Egg {
            constructor(x, y) {
                this.x = x;
                this.y = y;
                this.width = 12;
                this.height = 16;
                this.color = '#fff8dc'; // light yellow
            }

            draw(ctx) {
                ctx.save();
                ctx.translate(this.x, this.y);
                ctx.scale(this.width / 20, this.height / 20); // base size 20x20
                ctx.fillStyle = this.color;
                ctx.beginPath();
                ctx.ellipse(0, 0, 10, 10, 0, 0, Math.PI * 2);
                ctx.fill();
                ctx.restore();
            }
        }

        // ----- Chicken class -----
        class Chicken {
            constructor(x, y) {
                this.x = x;
                this.y = y;
                this.radius = 20;          // body radius
                this.speed = 80;           // pixels per second
                this.direction = Math.random() * Math.PI * 2; // radians
                this.state = 'wandering';  // or 'laying'
                this.layTimer = 0;         // countdown to next lay
                this.layCooldown = this._randomBetween(2, 5); // seconds
                this.layDuration = 0.6;    // seconds chicken pauses
                this.layElapsed = 0;
                this.color = '#f5deb3';    // wheat color
                this.layColor = '#ffe4c4'; // lighter during laying
            }

            _randomBetween(min, max) {
                return min + Math.random() * (max - min);
            }

            update(delta, eggs) {
                if (this.state === 'laying') {
                    this.layElapsed += delta;
                    if (this.layElapsed >= this.layDuration) {
                        // Laying finished: create egg and go back to wandering
                        const eggOffset = 0.8 * this.radius;
                        const layX = this.x - Math.cos(this.direction) * eggOffset;
                        const layY = this.y - Math.sin(this.direction) * eggOffset;
                        eggs.push(new Egg(layX, layY));

                        this.state = 'wandering';
                        this.layElapsed = 0;
                        this.layTimer = this.layCooldown;
                        this.layCooldown = this._randomBetween(2, 5);
                    }
                    // No movement while laying
                    return;
                }

                // Wandering state
                this.layTimer -= delta;
                if (this.layTimer <= 0) {
                    // Start laying
                    this.state = 'laying';
                    this.layElapsed = 0;
                    return;
                }

                // Randomly change direction every 1–3 seconds
                if (!this.nextDirChangeTime) this.nextDirChangeTime = 0;
                this.nextDirChangeTime -= delta;
                if (this.nextDirChangeTime <= 0) {
                    this.direction += this._randomBetween(-Math.PI / 4, Math.PI / 4);
                    this.nextDirChangeTime = this._randomBetween(1, 3);
                }

                // Move
                const dx = Math.cos(this.direction) * this.speed * delta;
                const dy = Math.sin(this.direction) * this.speed * delta;
                this.x += dx;
                this.y += dy;

                // Boundary handling: bounce off walls
                if (this.x - this.radius < 0) {
                    this.x = this.radius;
                    this.direction = Math.PI - this.direction;
                }
                if (this.x + this.radius > canvas.width) {
                    this.x = canvas.width - this.radius;
                    this.direction = Math.PI - this.direction;
                }
                if (this.y - this.radius < 0) {
                    this.y = this.radius;
                    this.direction = -this.direction;
                }
                if (this.y + this.radius > canvas.height) {
                    this.y = canvas.height - this.radius;
                    this.direction = -this.direction;
                }
            }

            draw(ctx) {
                ctx.save();
                ctx.translate(this.x, this.y);
                ctx.rotate(this.direction);

                // Body
                ctx.fillStyle = this.state === 'laying' ? this.layColor : this.color;
                ctx.beginPath();
                ctx.arc(0, 0, this.radius, 0, Math.PI * 2);
                ctx.fill();

                // Beak (triangle pointing forward)
                ctx.fillStyle = '#ffcc00';
                ctx.beginPath();
                ctx.moveTo(this.radius, 0);
                ctx.lineTo(this.radius + 8, -4);
                ctx.lineTo(this.radius + 8, 4);
                ctx.closePath();
                ctx.fill();

                // Optional: small eye
                ctx.fillStyle = '#000';
                ctx.beginPath();
                ctx.arc(this.radius / 2, -this.radius / 2, 2, 0, Math.PI * 2);
                ctx.fill();

                ctx.restore();
            }
        }

        // ----- Simulation setup -----
        const chicken = new Chicken(canvas.width / 2, canvas.height / 2);
        const eggs = [];

        let lastTime = performance.now();

        function animate(now) {
            const delta = (now - lastTime) / 1000; // seconds
            lastTime = now;

            // Update
            chicken.update(delta, eggs);

            // Draw
            ctx.fillStyle = '#90ee90'; // grass background
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            eggs.forEach(e => e.draw(ctx));
            chicken.draw(ctx);

            requestAnimationFrame(animate);
        }

        requestAnimationFrame(animate);
    </script>

    <section id="notes">
        <h3>Developer Notes</h3>
        <ul>
            <li>Delta time is used throughout to keep movement and timers frame‑rate independent.</li>
            <li>The chicken's wandering AI uses a simple random direction change timer and wall‑reflection logic.</li>
            <li>Eggs are stored in an array and are never removed; you could extend the simulation to fade them out after a set time.</li>
            <li>The chicken faces its movement direction; a small beak triangle shows the forward direction.</li>
            <li>During the laying state the chicken changes color to indicate the action.</li>
        </ul>
    </section>
</body>
</html>
```

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: gpt-oss-20b-mxfp4.gguf -->
<!-- Prompt: chicken.md -->
<!-- Generation Time: 14.36s -->
<!-- Fallback Used: False -->