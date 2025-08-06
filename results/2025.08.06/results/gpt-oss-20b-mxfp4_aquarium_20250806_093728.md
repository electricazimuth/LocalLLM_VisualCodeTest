```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Aquarium Simulation</title>
    <style>
        body { margin:0; overflow:hidden; background:#e0f7fa; }
        canvas { display:block; margin:20px auto; border:1px solid #888;
                 background:#c7f7ff; }
    </style>
</head>
<body>
    <!-- The aquarium canvas -->
    <canvas id="simulationCanvas" width="800" height="600"></canvas>

    <script>
        /* -------------------------------------------------------------
           Aquarium Simulation – vanilla JS + Canvas
           ------------------------------------------------------------- */

        const canvas = document.getElementById('simulationCanvas');
        const ctx    = canvas.getContext('2d');
        const W      = canvas.width;
        const H      = canvas.height;

        /* Utility ----------------------------------------------------- */
        function rand(min, max) {
            return Math.random() * (max - min) + min;
        }

        /* Fish class --------------------------------------------------- */
        class Fish {
            constructor() {
                // ---------- Appearance ----------
                this.size   = rand(12, 30);                // half‑width of the triangle
                this.color  = `hsl(${Math.floor(rand(0,360))},70%,50%)`;
                this.tail   = rand(0, Math.PI * 2);        // phase for tail wiggle

                // ---------- Position & Motion ----------
                this.x      = rand(this.size, W - this.size);
                this.y      = rand(this.size, H - this.size);
                this.speed  = rand(30, 80);                // pixels per second
                this.angle  = rand(0, Math.PI * 2);        // heading in radians
                this.updateVelocity();
            }

            /* Convert angle → velocity components */
            updateVelocity() {
                this.vx = Math.cos(this.angle) * this.speed;
                this.vy = Math.sin(this.angle) * this.speed;
            }

            /* Called every frame */
            update(dt) {
                /* 1️⃣  Wandering – small random turn each frame */
                const wander = 0.5;                // max radians per second
                this.angle += rand(-wander, wander) * dt;

                /* 2️⃣  Boundary avoidance – gentle steering back to center */
                const margin = this.size + 20;     // how close to edge before turning
                let steerX = 0, steerY = 0;
                if (this.x < margin)      steerX = 1;
                if (this.x > W - margin)  steerX = -1;
                if (this.y < margin)      steerY = 1;
                if (this.y > H - margin)  steerY = -1;

                if (steerX !== 0 || steerY !== 0) {
                    const desired = Math.atan2(steerY, steerX);
                    let diff = desired - this.angle;
                    diff = ((diff + Math.PI) % (Math.PI*2)) - Math.PI; // [-π,π]
                    const turnRate = 0.5;          // how fast to turn toward center
                    this.angle += diff * turnRate;
                }

                /* 3️⃣  Update velocity & position */
                this.updateVelocity();
                this.x += this.vx * dt;
                this.y += this.vy * dt;

                /* Clamp to canvas (prevent tiny overshoot) */
                this.x = Math.max(this.size, Math.min(W - this.size, this.x));
                this.y = Math.max(this.size, Math.min(H - this.size, this.y));

                /* 4️⃣  Tail wiggle phase */
                this.tail += dt * 8;               // 8 wiggles per second
            }

            /* Draw the fish */
            draw(ctx) {
                ctx.save();
                ctx.translate(this.x, this.y);
                ctx.rotate(this.angle);

                /* Body – triangle */
                ctx.beginPath();
                ctx.moveTo(-this.size * 0.6, 0);                     // tail tip
                ctx.lineTo(this.size * 0.6, -this.size * 0.4);        // front right
                ctx.lineTo(this.size * 0.6,  this.size * 0.4);        // front left
                ctx.closePath();
                ctx.fillStyle = this.color;
                ctx.fill();
                ctx.strokeStyle = '#222';
                ctx.stroke();

                /* Tail wiggle – a tiny offset on the tail tip */
                const tailX = Math.sin(this.tail) * this.size * 0.1;
                const tailY = Math.cos(this.tail) * this.size * 0.1;
                ctx.beginPath();
                ctx.moveTo(-this.size * 0.6, 0);
                ctx.lineTo(-this.size * 0.6 + tailX, tailY);
                ctx.stroke();

                ctx.restore();
            }
        }

        /* ---------- Create fish ---------- */
        const fishCount = 12;               // number of fish
        const fishes = Array.from({length: fishCount}, () => new Fish());

        /* ---------- Animation loop ---------- */
        let lastTime = 0;
        function gameLoop(timestamp) {
            if (!lastTime) lastTime = timestamp;
            const dt = (timestamp - lastTime) / 1000;   // seconds
            lastTime = timestamp;

            /* Clear canvas */
            ctx.fillStyle = '#c7f7ff';
            ctx.fillRect(0, 0, W, H);

            /* Update & draw each fish */
            for (const f of fishes) {
                f.update(dt);
                f.draw(ctx);
            }

            requestAnimationFrame(gameLoop);
        }

        requestAnimationFrame(gameLoop);
    </script>

    <section id="notes">
        <h2>Developer Notes</h2>
        <ul>
            <li>Each fish is a triangle that always points in its motion direction.</li>
            <li>Wandering is implemented by a small random change to the heading each frame.</li>
            <li>When a fish nears a canvas edge it smoothly steers back toward the center instead of a hard bounce.</li>
            <li>Delta‑time (`dt`) ensures the animation is frame‑rate independent.</li>
            <li>A tail wiggle is simulated with a sinusoidal offset that oscillates over time.</li>
            <li>The entire simulation uses only vanilla JavaScript and the Canvas API – no external libraries.</li>
        </ul>
    </section>
</body>
</html>
```

**How it works**

1. **Fish class** – encapsulates position, speed, heading, color, size and the logic for wandering, boundary avoidance and tail wiggle.  
2. **Update** – each frame the fish receives a small random heading change, checks if it’s near a wall and gently turns toward the center, then moves according to its velocity.  
3. **Draw** – the fish is rendered as a rotated triangle. The tail wiggle is a small sinusoidal offset added to the tail tip.  
4. **Animation loop** – uses `requestAnimationFrame`. The canvas is cleared, every fish is updated with the proper `deltaTime`, and then drawn.  

Open the file in a modern browser and watch a calm, autonomous aquarium animation. No user interaction is required.

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: gpt-oss-20b-mxfp4.gguf -->
<!-- Prompt: aquarium.md -->
<!-- Generation Time: 26.43s -->
<!-- Fallback Used: False -->