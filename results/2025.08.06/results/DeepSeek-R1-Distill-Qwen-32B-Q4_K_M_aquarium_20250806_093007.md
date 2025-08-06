```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Aquarium Simulation</title>
<style>
    body { margin:0; overflow:hidden; background:#e0f7fa; }
    canvas { display:block; margin:20px auto; border:1px solid #888; background:#c7f7ff; }
</style>
</head>
<body>
<canvas id="simulationCanvas" width="512" height="512"></canvas>

<script>
/* -------------------------------------------------------------
   Aquarium Simulation – Pure JS + Canvas
   -------------------------------------------------------------
   * Object‑oriented Fish class
   * Delta‑time based animation loop
   * Simple wandering + boundary avoidance
   * Tail wiggle for extra realism
   ------------------------------------------------------------- */

const canvas = document.getElementById('simulationCanvas');
const ctx = canvas.getContext('2d');
const W = canvas.width, H = canvas.height;

// ---------- Utility helpers ----------
const random = (min, max) => Math.random() * (max - min) + min;
const clamp = (val, min, max) => Math.max(min, Math.min(max, val));

// ---------- Fish Class ----------
class Fish {
    constructor() {
        // Random initial state
        this.x = random(0, W);
        this.y = random(0, H);
        this.size = random(15, 35);            // radius
        this.speed = random(30, 80);           // pixels per second
        this.angle = random(0, Math.PI * 2);   // direction in radians
        this.color = `hsl(${Math.floor(random(0, 360))}, 70%, 60%)`;
        this.wander = 0;                       // current wander offset
        this.tailPhase = 0;                    // for tail wiggle
    }

    // Update position & behaviour
    update(dt) {
        // 1. Wandering – slowly change direction
        const wanderChange = random(-0.5, 0.5) * dt; // radians per second
        this.wander += wanderChange;
        const targetAngle = this.angle + this.wander;

        // 2. Boundary avoidance – if close to edge, steer back
        const margin = 30; // distance from edge to start turning
        let desired = targetAngle;

        if (this.x < margin) {
            desired = Math.PI / 2; // face right
        } else if (this.x > W - margin) {
            desired = -Math.PI / 2; // face left
        }
        if (this.y < margin) {
            desired = Math.PI; // face down
        } else if (this.y > H - margin) {
            desired = 0; // face up
        }

        // Smoothly rotate towards desired angle
        const angleDiff = ((desired - this.angle + Math.PI) % (2 * Math.PI)) - Math.PI;
        const turnSpeed = 2; // radians per second
        this.angle += clamp(angleDiff, -turnSpeed * dt, turnSpeed * dt);

        // 3. Move forward
        this.x += Math.cos(this.angle) * this.speed * dt;
        this.y += Math.sin(this.angle) * this.speed * dt;

        // 4. Keep inside canvas (just in case)
        this.x = clamp(this.x, 0, W);
        this.y = clamp(this.y, 0, H);

        // 5. Tail wiggle phase
        this.tailPhase += dt * 4; // 4 cycles per second
    }

    // Draw the fish
    draw(ctx) {
        ctx.save();
        ctx.translate(this.x, this.y);
        ctx.rotate(this.angle);

        // Body – simple ellipse
        ctx.beginPath();
        ctx.ellipse(0, 0, this.size, this.size * 0.6, 0, 0, Math.PI * 2);
        ctx.fillStyle = this.color;
        ctx.fill();

        // Tail – two triangles wiggling
        const tailLen = this.size * 0.6;
        const tailWidth = this.size * 0.4;
        const wiggle = Math.sin(this.tailPhase) * 0.2;

        ctx.beginPath();
        ctx.moveTo(-this.size, 0);
        ctx.lineTo(-this.size - tailLen, -tailWidth * (1 + wiggle));
        ctx.lineTo(-this.size - tailLen, tailWidth * (1 + wiggle));
        ctx.closePath();
        ctx.fillStyle = this.color;
        ctx.fill();

        // Eye – small circle
        ctx.beginPath();
        ctx.arc(this.size * 0.3, -this.size * 0.2, this.size * 0.05, 0, Math.PI * 2);
        ctx.fillStyle = '#000';
        ctx.fill();

        ctx.restore();
    }
}

// ---------- Simulation setup ----------
const fishCount = 12;
const fishes = Array.from({length: fishCount}, () => new Fish());

// ---------- Animation loop ----------
let lastTime = 0;
function gameLoop(timestamp) {
    const dt = (timestamp - lastTime) / 1000; // seconds
    lastTime = timestamp;

    // Clear canvas
    ctx.clearRect(0, 0, W, H);

    // Update & draw each fish
    for (const fish of fishes) {
        fish.update(dt);
        fish.draw(ctx);
    }

    requestAnimationFrame(gameLoop);
}

// Start the simulation
requestAnimationFrame(gameLoop);
</script>

<section id="notes">
    <h2>Developer Notes</h2>
    <ul>
        <li>Fish are represented by an <code>Fish</code> class that encapsulates position, velocity, size, color, and a simple wandering behaviour.</li>
        <li>Delta time (<code>dt</code>) is used to keep movement frame‑rate independent.</li>
        <li>Boundary avoidance is handled by steering the fish back toward the centre when it gets within a margin of the canvas edges.</li>
        <li>A tail wiggle effect adds a subtle secondary motion, using a sine wave based on the elapsed time.</li>
        <li>All fish are stored in a single array and updated/drawn in each frame, keeping the code simple and efficient.</li>
    </ul>
</section>
</body>
</html>
```

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: DeepSeek-R1-Distill-Qwen-32B-Q4_K_M.gguf -->
<!-- Prompt: aquarium.md -->
<!-- Generation Time: 12.70s -->
<!-- Fallback Used: False -->