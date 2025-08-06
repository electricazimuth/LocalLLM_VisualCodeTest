<|channel|>analysis<|message|>We need to produce final code within the provided template. Provide a single HTML file containing all code. Use best practices: classes for Rocket and ExplosionParticle. Use a single particles array with different types. Use delta time. Use requestAnimationFrame. Use launch interval random between 0.5-2 sec. Use gravity constant. Use rocket fuse time random 1-2 sec or altitude threshold. We'll implement rocket explosion on time. Use simple rocket as bright dot or small line.

Also implement removal of dead particles: we can filter array each frame or use for loop backwards removal. Use efficient removal by swapping with last and pop. Provide good performance.

Add notes section for explanation.

Let's design.

We will define:

class Rocket {
  constructor(x, y) { this.x = x; this.y = y; this.vx = random(-20, 20); this.vy = random(-300, -400); this.color = randomColor(); this.exploded = false; this.fuseTime = random(1, 2) * 1000; this.elapsed = 0; }
  update(dt) { this.elapsed += dt; this.vy += GRAVITY * dt; this.x += this.vx * dt; this.y += this.vy * dt; if (this.elapsed > this.fuseTime) { this.exploded = true; } }
  draw(ctx) { ctx.fillStyle = this.color; ctx.beginPath(); ctx.arc(this.x, this.y, 2, 0, Math.PI * 2); ctx.fill(); }
}

class ExplosionParticle {
  constructor(x, y, color) { this.x = x; this.y = y; let angle = Math.random() * Math.PI * 2; let speed = Math.random() * 200 + 50; this.vx = Math.cos(angle) * speed; this.vy = Math.sin(angle) * speed; this.life = Math.random() * 1 + 1; this.remaining = this.life; this.size = Math.random() * 2 + 1; this.color = color; }
  update(dt) { this.vy += GRAVITY * dt; this.x += this.vx * dt; this.y += this.vy * dt; this.remaining -= dt; }
  draw(ctx) { const alpha = Math.max(this.remaining / this.life, 0); ctx.fillStyle = hexToRGBA(this.color, alpha); ctx.beginPath(); ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2); ctx.fill(); }
}

We will keep array particles = []; each element can be rocket or explosion particle. We will also maintain a separate array for rockets maybe but we can just store all in single array and differentiate by property type: 'rocket' or 'particle' or by instanceof.

Simpler: Use array of objects; we can store rockets in rockets array; but requirement: store all active particles efficiently, likely in a single array. So we can store all. Use property type: 'rocket' or 'explosion'.

Alternatively, we can push rockets and explosion particles into same array; each will have update and draw methods. For removal, we can filter. But we can also iterate backwards and if dead then remove.

We'll implement:

class ParticleBase { update(dt) {} draw(ctx) {} isAlive() {} }

But for simplicity, we can just use classes with update/draw and property "alive".

We can create function createRandomColor() to return color string.

Also we need to handle launching new rockets automatically: maintain lastLaunchTime, nextLaunchInterval.

When rocket explodes, create explosion particles: e.g., 50.

Define constants:

const GRAVITY = 200; // pixels per second^2 (downwards positive)
const RADIUS_ROCKET = 2;

Set up:

let particles = [];
let lastLaunch = 0; // timestamp
let nextLaunchIn = random(500, 2000);

In gameLoop(timestamp), compute dt = (timestamp - lastTimestamp) / 1000; lastTimestamp = timestamp;

Update logic:

// Launch rockets
if (timestamp - lastLaunch > nextLaunchIn) {
  launchRocket();
  lastLaunch = timestamp;
  nextLaunchIn = random(500, 2000);
}

Update each particle: iterate backwards for removal.

for (let i = particles.length - 1; i >= 0; i--) {
  const p = particles[i];
  p.update(dt);
  if (!p.isAlive()) {
    // If rocket exploded, we create explosion particles
    if (p.type === 'rocket' && p.exploded) {
        createExplosion(p.x, p.y, p.color);
    }
    // Remove from array
    particles.splice(i, 1);
  }
}

But we want to create explosion at same time as removal. So we can check before removal.

Alternatively, we can maintain property 'explode' triggered by rocket. We'll handle inside update: rocket.update returns boolean exploded. Then we can handle after update.

Simpler: In rocket.update, we set this.exploded = true; and we can set this.exploded = true; and also we set this.dead = this.exploded; Then after update, we check if dead and type 'rocket', create explosion.

But we can just handle inside update: if this.exploded, we can create explosion particles and return true to indicate removal. But we cannot create explosion inside rocket.update because we need access to global particles array.

Simpler: In gameLoop, after updating each particle, if rocket.exploded, we create explosion and mark to remove.

Pseudo:

for (let i = particles.length - 1; i >= 0; i--) {
  const p = particles[i];
  p.update(dt);
  if (p.type === 'rocket') {
    if (p.exploded) {
      createExplosion(p.x, p.y, p.color);
      particles.splice(i, 1);
      continue;
    }
  } else { // explosion particle
    if (!p.isAlive()) {
      particles.splice(i, 1);
    }
  }
}

Define createExplosion(x, y, color) { const count = randomInt(30, 80); for (let i=0; i<count; i++) particles.push(new ExplosionParticle(x, y, color)); }

Define random and randomInt functions.

Define hexToRGBA.

Implementation details:

- Use canvas width and height W, H.

- Launch rocket from bottom center: x = W/2 + random(-W/20, W/20) maybe small random offset. y = H + 5 (just below canvas). vy negative: random(-350, -450) maybe.

- Add horizontal randomness: vx random(-80, 80).

- fuseTime: random(1, 2) seconds.

- Use delta time dt in seconds.

- Gravity: 200 px/s^2 downward.

- Explosion particle speed: random(50, 200) maybe.

- Lifespan: random(1, 3) seconds.

- Colors: random color: use random hue: `hsl(Math.random()*360, 80%, 60%)`.

- For rocket color: random color.

- For explosion color: same as rocket color maybe.

- For explosion particle, use color with alpha.

- For rocket, we can draw small circle.

- For explosion, we can draw small circle.

- We can optionally draw rocket as line trailing: we can store previous positions? Not necessary.

- Use performance: avoid heavy operations inside loops.

- Use requestAnimationFrame loop.

- Setup: requestAnimationFrame(gameLoop) at bottom.

- In gameLoop, we need to clear canvas: ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H);

- Or use ctx.clearRect but then fill.

- Use ctx.globalCompositeOperation? Not needed.

- Provide notes section with explanation.

- Ensure script runs on load.

- Provide random functions.

- Provide hexToRGBA for color with alpha.

- Provide small functions.

- Provide code inside script.

Now produce final HTML file.

Let's write code step by step.

We'll implement randomInRange(min, max) returning float.

randomInt(min, max) returning integer.

function randomColor() returns `hsl(hue, 80%, 60%)`.

Define hexToRGBA: but we can just use `rgba(${r},${g},${b},alpha)` with r,g,b from color string? But easier: use `ctx.fillStyle = `${color},${alpha}`? Actually color string from hsl can't combine with alpha easily. We can convert to `rgba` by using hsl to rgb conversion. But we can also use `ctx.fillStyle = `hsla(${hue},80%,60%,${alpha})`. So we can generate color as hsl string with alpha.

Simpler: For rocket color: generate hue.

For explosion particle: color string like `hsla(${hue},80%,60%,${alpha})`. But we need hue value. We can store hue property.

So in Rocket: this.hue = randomInt(0, 360); this.color = `hsl(${this.hue},80%,60%)`.

In ExplosionParticle: this.color = `hsla(${hue},80%,60%,${alpha})` where alpha variable.

But we need to compute alpha each frame: we can set this.alpha = 1; but we will compute dynamic.

Simpler: In draw, we compute alpha = Math.max(this.remaining / this.life, 0); and set ctx.fillStyle = `hsla(${this.hue},80%,60%,${alpha})`.

Thus we store hue in ExplosionParticle.

Implementation:

class Rocket {
  constructor(x, y) {
    this.x = x;
    this.y = y;
    this.vx = randomInRange(-80, 80);
    this.vy = randomInRange(-400, -350);
    this.hue = randomInt(0, 360);
    this.fuseTime = randomInRange(1, 2); // seconds
    this.elapsed = 0;
    this.exploded = false;
    this.type = 'rocket';
  }

  update(dt) {
    this.elapsed += dt;
    this.vy += GRAVITY * dt;
    this.x += this.vx * dt;
    this.y += this.vy * dt;
    if (this.elapsed > this.fuseTime) {
      this.exploded = true;
    }
  }

  draw(ctx) {
    ctx.fillStyle = `hsl(${this.hue},80%,60%)`;
    ctx.beginPath();
    ctx.arc(this.x, this.y, 2, 0, Math.PI*2);
    ctx.fill();
  }
}

class ExplosionParticle {
  constructor(x, y, hue) {
    this.x = x;
    this.y = y;
    const angle = Math.random() * Math.PI * 2;
    const speed = randomInRange(50, 200);
    this.vx = Math.cos(angle) * speed;
    this.vy = Math.sin(angle) * speed;
    this.life = randomInRange(1, 3);
    this.remaining = this.life;
    this.size = randomInRange(1, 3);
    this.hue = hue;
    this.type = 'particle';
  }

  update(dt) {
    this.vy += GRAVITY * dt;
    this.x += this.vx * dt;
    this.y += this.vy * dt;
    this.remaining -= dt;
  }

  isAlive() {
    return this.remaining > 0;
  }

  draw(ctx) {
    const alpha = Math.max(this.remaining / this.life, 0);
    ctx.fillStyle = `hsla(${this.hue},80%,60%,${alpha})`;
    ctx.beginPath();
    ctx.arc(this.x, this.y, this.size, 0, Math.PI*2);
    ctx.fill();
  }
}

Now create functions:

function launchRocket() {
  const x = W/2 + randomInRange(-W/20, W/20);
  const y = H + 5; // below canvas
  particles.push(new Rocket(x, y));
}

function createExplosion(x, y, hue) {
  const count = randomInt(30, 80);
  for (let i = 0; i < count; i++) {
    particles.push(new ExplosionParticle(x, y, hue));
  }
}

Now main loop:

let lastTimestamp = performance.now();

function gameLoop(timestamp) {
  const dt = (timestamp - lastTimestamp) / 1000; // seconds
  lastTimestamp = timestamp;

  // Launch rockets
  if (!lastLaunchTime) lastLaunchTime = timestamp;
  if (timestamp - lastLaunchTime > nextLaunchInterval) {
    launchRocket();
    lastLaunchTime = timestamp;
    nextLaunchInterval = randomInRange(500, 2000); // ms
  }

  // Update particles
  for (let i = particles.length - 1; i >= 0; i--) {
    const p = particles[i];
    p.update(dt);
    if (p.type === 'rocket' && p.exploded) {
      createExplosion(p.x, p.y, p.hue);
      particles.splice(i, 1);
    } else if (p.type === 'particle' && !p.isAlive()) {
      particles.splice(i, 1);
    }
  }

  // Draw
  ctx.fillStyle = '#000';
  ctx.fillRect(0, 0, W, H);

  for (const p of particles) {
    p.draw(ctx);
  }

  requestAnimationFrame(gameLoop);
}

But we need variables lastLaunchTime, nextLaunchInterval.

Let lastLaunchTime = 0; let nextLaunchInterval = randomInRange(500, 2000);

But we need to ensure first launch occurs soon: we can set lastLaunchTime = 0; In first iteration, timestamp - 0 > nextLaunchInterval? Actually if timestamp is ~0, then timestamp - 0 > interval? Not. So we need to set lastLaunchTime = timestamp; So we can set lastLaunchTime = timestamp in gameLoop first call. But we can also set lastLaunchTime = performance.now().

Simpler: let lastLaunchTime = 0; let nextLaunchInterval = randomInRange(500, 2000);

Then inside loop: if (timestamp - lastLaunchTime >= nextLaunchInterval) { ... }

But if lastLaunchTime = 0 and timestamp ~ 16ms, 16-0 < interval. So not launched until interval passes. So first launch after 0.5-2 seconds. That's fine.

Now we need to define randomInRange(min, max): returns random float.

function randomInRange(min, max) { return Math.random() * (max - min) + min; }

function randomInt(min, max) { return Math.floor(Math.random() * (max - min + 1)) + min; }

Now we need to handle scaling with canvas size: we set rocket speed and explosion speed relative to canvas height.

Instead of constants, we can compute speeds relative to H: e.g., base speed = H/2 maybe. But we can keep fixed.

But we can compute:

rocket.vy = -randomInRange(H * 0.8, H * 1.0). But we need to adjust.

Simpler: Keep fixed speeds but ensure they scale with canvas size.

Let's compute:

const GRAVITY = H * 0.5; // px/s^2

But we need to compute after canvas loaded.

We set const GRAVITY = 200; but we can set variable after W and H known.

Better: const GRAVITY = H * 0.5; but we need to compute after we know H.

Let's set:

const GRAVITY = H * 0.5; // 0.5 pixel per ms? Wait we need units. We are using dt in seconds. So gravity in px/s^2.

If H = 512, GRAVITY = 256 px/s^2, which is moderate.

Now rocket initial vy: -randomInRange(H * 0.9, H * 1.1). For H=512, vy = -460 to -560 px/s. That might be too high but okay.

But we can just keep 400-500.

Simplify: Use constants relative to H.

Set:

const GRAVITY = H * 0.5;

class Rocket:

constructor:

this.vy = -randomInRange(H * 0.8, H * 1.0);

this.vx = randomInRange(-H * 0.1, H * 0.1); // small horizontal.

But we may want to keep speed less. Let's just keep as earlier.

Now we need to ensure rocket travels at least half height. With vy ~ -400 px/s, dt ~ 0.016s, rocket moves ~6.4 px per frame. After 1 sec, ~64 px. Not enough.

But with dt 0.016, 1 sec is 60 frames. 400 * 1 = 400 px. That's good.

So rocket travels 400 px upward: at least half height.

Ok.

Now we need to compute explosion radius: 20-30% of width/height: but we can random number of particles to approximate.

Now we need to ensure performance: For each frame, we update all particles. We can limit max number of particles: but not necessary.

Now we need to add comments.

Also we need to add notes section.

Now produce final HTML with code.

Let's craft final code.

Also we need to call requestAnimationFrame(gameLoop) at bottom.

Now produce final answer.

<|start|>assistant<|channel|>final<|message|>```html
<!DOCTYPE html>
<html>
<head>
    <title>Fireworks Simulation</title>
    <style>
        body { margin: 0; overflow: hidden; background-color: #111; }
        canvas { border: 1px solid #444; background-color: #000; display: block; margin: 20px auto; }
    </style>
</head>
<body>
    <canvas id="gameCanvas" width="512" height="512"></canvas>
    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const W = canvas.width;
        const H = canvas.height;

        /* ---------- Utility helpers ---------- */
        function randomInRange(min, max) { return Math.random() * (max - min) + min; }
        function randomInt(min, max) { return Math.floor(Math.random() * (max - min + 1)) + min; }

        /* ---------- Physics constants ---------- */
        const GRAVITY = H * 0.5;          // pixels / s²  (downward)
        const ROCKET_MIN_VY = -H * 1.0;   // initial upward speed
        const ROCKET_MAX_VY = -H * 0.8;
        const ROCKET_MIN_VX = -H * 0.1;   // small horizontal jitter
        const ROCKET_MAX_VX = H * 0.1;

        /* ---------- Particle classes ---------- */
        class Rocket {
            constructor(x, y) {
                this.x = x;
                this.y = y;
                this.vx = randomInRange(ROCKET_MIN_VX, ROCKET_MAX_VX);
                this.vy = randomInRange(ROCKET_MIN_VY, ROCKET_MAX_VY);
                this.hue = randomInt(0, 360);
                this.fuseTime = randomInRange(1.0, 2.0); // seconds until explosion
                this.elapsed = 0;
                this.exploded = false;
                this.type = 'rocket';
            }
            update(dt) {
                this.elapsed += dt;
                this.vy += GRAVITY * dt;          // gravity slows the ascent
                this.x += this.vx * dt;
                this.y += this.vy * dt;
                if (this.elapsed > this.fuseTime) this.exploded = true;
            }
            draw(ctx) {
                ctx.fillStyle = `hsl(${this.hue},80%,60%)`;
                ctx.beginPath();
                ctx.arc(this.x, this.y, 2, 0, Math.PI * 2);
                ctx.fill();
            }
        }

        class ExplosionParticle {
            constructor(x, y, hue) {
                this.x = x;
                this.y = y;
                const angle = Math.random() * Math.PI * 2;
                const speed = randomInRange(H * 0.1, H * 0.3); // outward speed
                this.vx = Math.cos(angle) * speed;
                this.vy = Math.sin(angle) * speed;
                this.life = randomInRange(1.0, 3.0); // seconds
                this.remaining = this.life;
                this.size = randomInRange(1, 3);
                this.hue = hue;
                this.type = 'particle';
            }
            update(dt) {
                this.vy += GRAVITY * dt;      // gravity pulls particles down
                this.x += this.vx * dt;
                this.y += this.vy * dt;
                this.remaining -= dt;
            }
            isAlive() { return this.remaining > 0; }
            draw(ctx) {
                const alpha = Math.max(this.remaining / this.life, 0);
                ctx.fillStyle = `hsla(${this.hue},80%,60%,${alpha})`;
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                ctx.fill();
            }
        }

        /* ---------- Simulation state ---------- */
        const particles = [];          // holds both rockets & explosion fragments
        let lastLaunchTime = 0;
        let nextLaunchInterval = randomInRange(500, 2000); // ms

        /* ---------- Helper functions ---------- */
        function launchRocket() {
            const x = W / 2 + randomInRange(-W / 20, W / 20);
            const y = H + 5; // start just below the canvas
            particles.push(new Rocket(x, y));
        }

        function createExplosion(x, y, hue) {
            const count = randomInt(30, 80);
            for (let i = 0; i < count; i++) {
                particles.push(new ExplosionParticle(x, y, hue));
            }
        }

        /* ---------- Main loop ---------- */
        let lastTimestamp = performance.now();

        function gameLoop(timestamp) {
            const dt = (timestamp - lastTimestamp) / 1000; // delta time in seconds
            lastTimestamp = timestamp;

            /* --- Autonomous launch logic --- */
            if (timestamp - lastLaunchTime > nextLaunchInterval) {
                launchRocket();
                lastLaunchTime = timestamp;
                nextLaunchInterval = randomInRange(500, 2000);
            }

            /* --- Update particles --- */
            for (let i = particles.length - 1; i >= 0; i--) {
                const p = particles[i];
                p.update(dt);

                if (p.type === 'rocket' && p.exploded) {
                    createExplosion(p.x, p.y, p.hue);
                    particles.splice(i, 1); // remove exploded rocket
                } else if (p.type === 'particle' && !p.isAlive()) {
                    particles.splice(i, 1); // remove dead fragment
                }
            }

            /* --- Render --- */
            ctx.fillStyle = '#000';
            ctx.fillRect(0, 0, W, H);

            for (const p of particles) p.draw(ctx);

            requestAnimationFrame(gameLoop);
        }

        // Kick off the simulation
        requestAnimationFrame(gameLoop);
    </script>
    <section id="notes">
        <h2>How the simulation works</h2>
        <p>
            <strong>Particle array</strong>: All rockets and explosion fragments are stored in a single <code>particles</code> array. Each element has a <code>type</code> field to distinguish rockets from fragments.
        </p>
        <p>
            <strong>Autonomous launching</strong>: A timer controls when a new rocket is spawned. The interval is random between 0.5 and 2 seconds.
        </p>
        <p>
            <strong>Rocket physics</strong>: Rockets start below the canvas with a strong upward velocity and a small horizontal jitter. Gravity is applied each frame, slowing them until they explode after a random fuse time (1–2 s).
        </p>
        <p>
            <strong>Explosion</strong>: When a rocket explodes, 30–80 fragments are created. Their velocities radiate outward randomly, and they fall under gravity while fading out over 1–3 s.
        </p>
        <p>
            <strong>Delta‑time</strong>: The <code>dt</code> value (in seconds) is derived from the timestamps supplied by <code>requestAnimationFrame</code>, ensuring smooth animation regardless of frame rate.
        </p>
        <p>
            <strong>Performance</strong>: Particles are removed from the array in a reverse loop to avoid shifting indices. Only a few dozen particles are alive at any moment, so the simulation runs smoothly even at high frame rates.
        </p>
    </section>
</body>
</html>
```

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: gpt-oss-20b-MXFP4_UNSLOTH.gguf -->
<!-- Prompt: fireworks.md -->
<!-- Generation Time: 43.23s -->
<!-- Fallback Used: False -->