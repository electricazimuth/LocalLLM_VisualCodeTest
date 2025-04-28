<think>
Okay, I need to create an autonomous fireworks simulation using HTML, JS, and CSS. The goal is to have fireworks launch automatically, explode, and create a nice visual effect. Let me break down the requirements and figure out how to approach this.

First, I'll start by setting up the HTML structure. The boilerplate already has a canvas element, so I'll use that. The CSS needs to make the canvas look good, probably with a dark background for contrast. I'll adjust the body and canvas styles to ensure it's centered and has a dark background.

Next, the JavaScript part. I'll need to handle the game loop using requestAnimationFrame. The loop will handle updating the particles and drawing them each frame. I'll need to manage two types of particles: rockets and explosion particles. Each will have different properties and behaviors.

For the rockets, they start at the bottom, move upwards with some horizontal randomness, and are affected by gravity. They should explode after a certain time or height. When they explode, they create a burst of particles. I'll create a Rocket class with properties like position, velocity, time alive, and color.

Explosion particles will have similar properties but with a lifespan and will be affected by gravity as well. They'll start at the explosion point and spread out in random directions. I'll create an ExplosionParticle class for these.

I'll store all active particles in an array, including both rockets and explosion particles. This way, I can update and draw them all in a single loop. However, I'll need to handle them differently based on their type.

The game loop will have an update phase and a draw phase. In the update, I'll check if it's time to launch a new rocket. Then, for each particle, I'll update their positions, velocities, and check if they should explode or be removed. For rockets, I'll check if their time alive exceeds the fuse time, and if so, create explosion particles and remove the rocket.

In the draw phase, I'll clear the canvas each frame to prevent trails. Then, I'll draw each particle, adjusting the alpha based on their remaining lifespan for a fading effect.

I'll also need to handle performance efficiently. Since particles are added and removed frequently, I'll process the particles in reverse order when removing to avoid shifting issues in the array.

Testing will be important. I'll make sure the fireworks launch at random intervals, explode correctly, and the particles fall and fade as expected. I'll adjust parameters like gravity, explosion particle count, and colors to get the best visual effect.

Finally, I'll ensure the code is clean and well-structured, using classes for rockets and particles, and keeping the update and draw logic separate for clarity.
</think>

```html
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

        const PARTICLES = [];
        let LAST_LAUNCH = 0;
        const GRAVITY = 0.2;
        const ROCKET_SPEED = -8;
        const EXPLOSION_PARTICLES = 50;

        class Rocket {
            constructor(x, y) {
                this.x = x;
                this.y = y;
                this.vx = (Math.random() - 0.5) * 3;
                this.vy = ROCKET_SPEED;
                this.timeAlive = 0;
                this.color = `hsl(${Math.random() * 360}, 100%, 50%)`;
            }
        }

        class ExplosionParticle {
            constructor(x, y) {
                this.x = x;
                this.y = y;
                this.vx = (Math.random() - 0.5) * 8;
                this.vy = (Math.random() - 0.5) * 8;
                this.vy *= -1; // Ensure initial upward movement
                this.life = 1;
                this.color = `hsl(${Math.random() * 360}, 100%, 50%)`;
            }
        }

        function launchRocket() {
            const rocket = new Rocket(W / 2, H - 10);
            PARTICLES.push(rocket);
        }

        function updateParticles(deltaTime) {
            for (let i = PARTICLES.length - 1; i >= 0; i--) {
                const particle = PARTICLES[i];
                
                if (particle instanceof Rocket) {
                    particle.vy += GRAVITY * deltaTime;
                    particle.x += particle.vx * deltaTime;
                    particle.y += particle.vy * deltaTime;
                    particle.timeAlive += deltaTime;

                    if (particle.timeAlive > 1.5 || particle.y < 0) {
                        // Explode
                        for (let j = 0; j < EXPLOSION_PARTICLES; j++) {
                            PARTICLES.push(new ExplosionParticle(particle.x, particle.y));
                        }
                        PARTICLES.splice(i, 1);
                    }
                } else if (particle instanceof ExplosionParticle) {
                    particle.vy += GRAVITY * deltaTime;
                    particle.x += particle.vx * deltaTime;
                    particle.y += particle.vy * deltaTime;
                    particle.life -= deltaTime * 0.5;

                    if (particle.life <= 0) {
                        PARTICLES.splice(i, 1);
                    }
                }
            }
        }

        function drawParticles() {
            ctx.clearRect(0, 0, W, H);
            
            for (const particle of PARTICLES) {
                ctx.beginPath();
                ctx.arc(particle.x, particle.y, 2, 0, Math.PI * 2);
                ctx.fillStyle = particle.color;
                ctx.globalAlpha = particle.life;
                ctx.fill();
                ctx.globalAlpha = 1;
            }
        }

        function gameLoop(timestamp) {
            if (!LAST_LAUNCH) LAST_LAUNCH = timestamp;
            const deltaTime = (timestamp - LAST_LAUNCH) / 1000;
            LAST_LAUNCH = timestamp;

            if (Math.random() < 0.05) { // ~20% chance every frame to launch
                launchRocket();
            }

            updateParticles(deltaTime);
            drawParticles();

            requestAnimationFrame(gameLoop);
        }

        requestAnimationFrame(gameLoop);
    </script>
    <section id="notes">
        <h2>Notes</h2>
        <p>This simulation creates a continuous fireworks display with:</p>
        <ul>
            <li>Rockets launching automatically from the bottom center</li>
            <li>Gravity affecting all particles</li>
            <li>Explosions creating colorful particle bursts</li>
            <li>Particles fading out over time</li>
            <li>Efficient particle management using arrays</li>
        </ul>
        <p>Features:</p>
        <ul>
            <li>Random launch intervals</li>
            <li>Colorful explosions</li>
            <li>Realistic physics simulation</li>
            <li>Smooth animation using requestAnimationFrame</li>
        </ul>
    </section>
</body>
</html>
```

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: DeepSeek-R1-Distill-Qwen-32B-Q4_K_M.gguf -->
<!-- Prompt: fireworks.md -->
<!-- Generation Time: 164.85s -->
<!-- Fallback Used: False -->