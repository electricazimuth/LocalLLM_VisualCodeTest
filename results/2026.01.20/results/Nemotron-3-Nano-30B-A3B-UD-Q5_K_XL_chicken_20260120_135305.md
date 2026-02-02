```html
<!DOCTYPE html>
<html>
<head>
    <title>Chicken Simulation</title>
    <style>
        body { margin: 10px; overflow: hidden; background-color: #eee; }
        canvas { display: block; margin: 20px auto; border: 1px solid #999;
                 background-color: #90ee90; } /* light‑green “grass” */
    </style>
</head>
<body>
    <canvas id="simulationCanvas" width="512" height="512"></canvas>

    <script>
        /* -------------------------------------------------------------
         *  Chicken Simulation – single‑file HTML + plain JS + Canvas API
         * ------------------------------------------------------------- */

        const canvas = document.getElementById('simulationCanvas');
        const ctx    = canvas.getContext('2d');

        /* ----------  Chicken Class  --------------------------------- */
        class Chicken {
            constructor(x, y, width, height) {
                this.x      = x;                     // centre of chicken
                this.y      = y;
                this.radius = 20;                    // body radius (px)
                this.width  = width;
                this.height = height;

                this.speed        = 120;             // px / second (average)
                this.angle        = Math.random() * Math.PI * 2; // heading
                this.vx = Math.cos(this.angle) * this.speed;
                this.vy = Math.sin(this.angle) * this.speed;

                // egg‑laying timers
                this.layInterval   = 3000;   // ms between possible lays
                this.layDuration   = 600;    // ms “pause” after laying
                this.laying        = false;  // true while chicken is “laying”
                this.layPauseTimer = 0;
                this.nextLayTimer  = 0;

                // wandering timer
                this.dirChangeTimer   = 0;
                this.dirChangeInterval = 2000; // ms before choosing a new direction
            }

            /* ---------------------------------------------------------
             *  Update chicken state – called each frame with delta‑time
             *  (dt = seconds since last frame) and the current egg list
             * ------------------------------------------------------- */
            update(dt, now, eggs) {
                /* ---- 1) Egg‑laying logic --------------------------------- */
                if (!this.laying) {
                    this.nextLayTimer += dt * 1000; // convert to ms for comparison
                    if (this.nextLayTimer >= this.layInterval) {
                        // ---- lay an egg at a spot behind the chicken ----
                        const offset = this.radius * 0.7;               // where an egg would sit
                        const rad    = Math.atan2(this.vy, this.vx);    // direction of movement
                        const eggX   = this.x - Math.cos(rad) * offset;
                        const eggY   = this.y - Math.sin(rad) * offset;
                        eggs.push(new Egg(eggX, eggY));

                        // ---- pause briefly ---------------------------------
                        this.laying        = true;
                        this.layPauseTimer = this.layDuration;
                        this.nextLayTimer  = 0; // reset timer for next lay
                    }
                } else {
                    // count down the pause timer
                    this.layPauseTimer -= dt * 1000;
                    if (this.layPauseTimer <= 0) this.laying = false;
                }

                /* ---- 2) Wandering behaviour (only when not laying) -------- */
                if (!this.laying) {
                    // change direction every few seconds for more natural wandering
                    this.dirChangeTimer += dt * 1000;
                    if (this.dirChangeTimer >= this.dirChangeInterval) {
                        this.angle = Math.random() * Math.PI * 2;
                        this.vx = Math.cos(this.angle) * this.speed;
                        this.vy = Math.sin(this.angle) * this.speed;
                        this.dirChangeTimer = 0;
                    }

                    // move
                    this.x += this.vx * dt;
                    this.y += this.vy * dt;

                    // keep inside canvas bounds
                    if (this.x < 0) { this.x = 0; this.vx = Math.abs(this.vx); }
                    if (this.x > this.width) { this.x = this.width; this.vx = -Math.abs(this.vx); }
                    if (this.y < 0) { this.y = 0; this.vy = Math.abs(this.vy); }
                    if (this.y > this.height) { this.y = this.height; this.vy = -Math.abs(this.vy); }
                }
            }

            /* ---------------------------------------------------------
             *  Draw the chicken – respects its current heading
             * ------------------------------------------------------- */
            draw(ctx) {
                ctx.save();
                // centre on chicken
                ctx.translate(this.x, this.y);
                // rotate so the chicken faces its movement direction
                const angle = Math.atan2(this.vy, this.vx);
                ctx.rotate(angle);

                // body
                ctx.fillStyle = '#8B4513'; // brown
                ctx.beginPath();
                ctx.arc(0, 0, this.radius, 0, Math.PI * 2);
                ctx.fill();

                // comb (tiny red triangle on top)
                ctx.fillStyle = 'red';
                ctx.beginPath();
                ctx.moveTo(-this.radius * 0.6, -this.radius * 0.8);
                ctx.lineTo(-this.radius * 0.3, -this.radius * 0.9);
                ctx.lineTo(0, -this.radius * 0.7);
                ctx.lineTo(this.radius * 0.3, -this.radius * 0.9);
                ctx.lineTo(this.radius * 0.6, -this.radius * 0.8);
                ctx.closePath();
                ctx.fill();

                // beak – yellow triangle pointing forward
                ctx.fillStyle = 'gold';
                const beakLen = this.radius * 0.6;
                const beakHgt = this.radius * 0.3;
                ctx.beginPath();
                ctx.moveTo(0, 0);
                ctx.lineTo(beakLen, -beakHgt / 2);
                ctx.lineTo(beakLen, beakHgt / 2);
                ctx.closePath();
                ctx.fill();

                ctx.restore();
            }
        }

        /* ----------  Egg Class  ------------------------------------ */
        class Egg {
            constructor(x, y) {
                this.x        = x;
                this.y        = y;
                this.createdAt = performance.now();
                this.lifetime = 5000; // ms before it disappears
            }

            // remove after lifetime expires
            isDead(now) {
                return now - this.createdAt > this.lifetime;
            }

            draw(ctx) {
                ctx.fillStyle = 'white';
                ctx.beginPath();
                ctx.ellipse(this.x, this.y, 12, 8, 0, 0, Math.PI * 2);
                ctx.fill();
                // tiny speckle for realism
                ctx.fillStyle = '#555';
                ctx.beginPath();
                ctx.arc(this.x + 2, this.y - 2, 2, 0, Math.PI * 2);
                ctx.fill();
            }
        }

        /* --------------------  Initialise  ------------------------ */
        const chicken = new Chicken(canvas.width / 2,
                                    canvas.height / 2,
                                    canvas.width,
                                    canvas.height);
        const eggs    = [];

        /* --------------------  Animation Loop  -------------------- */
        let lastTime = performance.now();

        function animate(now) {
            now = now || performance.now();
            const dt = (now - lastTime) / 1000; // seconds
            lastTime = now;

            /* clear canvas – light‑green “grass” */
            ctx.fillStyle = '#90ee90';
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            /* update chicken (passes egg list so it can add new eggs) */
            chicken.update(dt, now, eggs);

            /* draw all existing eggs */
            const nowMs = now;
            for (let i = eggs.length - 1; i >= 0; i--) {
                const egg = eggs[i];
                egg.draw(ctx);
                if (egg.isDead(nowMs)) eggs.splice(i, 1); // remove expired eggs
            }

            /* draw the chicken */
            chicken.draw(ctx);

            /* schedule next frame */
            requestAnimationFrame(animate);
        }

        requestAnimationFrame(animate);

        /* -------------------------------------------------------------
         *  Developer notes (optional – shown in the page)
         * ------------------------------------------------------------- */
        <section id="notes">
            <h3>Developer notes</h3>
            <ul>
                <li><strong>Chicken AI</strong>: The chicken picks a random heading,
                    moves at a constant speed, and changes direction every ~2 seconds.
                    When it reaches a canvas edge it reflects its velocity so it stays
                    completely inside the drawing area.</li>
                <li><strong>Egg laying</strong>: A timer (`nextLayTimer`) counts up.
                    When it exceeds `layInterval` the chicken “lays” an egg at a point
                    slightly behind its centre (opposite the movement direction) –
                    this mimics where a real egg would be deposited.</li>
                <li><strong>State handling</strong>: While laying, the chicken pauses
                    for `layDuration` ms before resuming wandering. The pause is
                    accounted for in the update loop so movement is smooth.</li>
                <li><strong>Delta‑time usage</strong>: All motion and timers are
                    multiplied by the elapsed frame time (`dt`) to make the simulation
                    frame‑rate independent.</li>
                <li><strong>Rendering</strong>: The chicken is drawn as a brown circle
                    with a red comb and a gold beak that rotates to face its current
                    velocity. Eggs are simple white ellipses that fade out after 5 seconds.</li>
                <li><strong>Extensibility</strong>: The code is organised into small
                    classes (`Chicken`, `Egg`) making it easy to add features such as
                    multiple chickens, variable egg lifetimes, or visual feedback.</li>
            </ul>
        </section>

    </script>
</body>
</html>
```

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: Nemotron-3-Nano-30B-A3B-UD-Q5_K_XL.gguf -->
<!-- Prompt: chicken.md -->
<!-- Generation Time: 48.49s -->
<!-- Fallback Used: False -->