<think>
Okay, I need to create a fireworks simulation using HTML, CSS, and JavaScript. Let's start by understanding the requirements. The main goal is to have fireworks that launch from the bottom, explode into particles, and those particles fall under gravity while fading out. The code should run in a single HTML file with no external libraries.

First, I'll structure the code. The HTML has a canvas element, and I need to handle the game loop with requestAnimationFrame. The particles (rockets and explosion fragments) should be managed in a single array for efficiency.

I should start by creating classes for Rocket and Particle (explosion particles). Using classes will help in organizing the code and managing their different behaviors.

For the Rocket class:
- Position starts at the bottom center, maybe with some random x offset.
- Velocity is upwards (vy negative), with some horizontal randomness (vx).
- Apply gravity to slow it down as it rises.
- Check if it's time to explode, either based on time or when the velocity is low enough.

For the ExplosionParticle class:
- Spawned at the rocket's position when it explodes.
- Random velocities in all directions.
- Apply gravity to make them fall.
- Have a lifespan and fade out as they age.

The game loop needs to handle:
- Updating all particles: moving them, applying gravity, checking for explosions, removing dead particles.
- Drawing all particles on the canvas.
- Periodically launching new rockets. Maybe using a timer that resets each time a rocket is launched.

Let's outline the steps:

1. Set up the canvas and context.
2. Create a particles array to hold all active particles.
3. Define the Rocket class with update and draw methods.
4. Define the ExplosionParticle class with update and draw methods.
5. In the game loop:
   a. Calculate delta time.
   b. Update each particle (move, apply gravity, check lifespan, etc.).
   c. Check if it's time to launch a new rocket (using a timer).
   d. Remove dead particles (exploded rockets, expired particles).
   e. Draw all particles.
   f. Request the next frame.

For launching rockets periodically, I can track the time since the last launch. For example, every 0.5 to 2 seconds. So in the game loop, check if the current time minus the last launch time is greater than a random interval. If so, create a new rocket and reset the timer.

Gravity should be a constant that affects all particles. For rockets, gravity will slow their ascent (since vy is negative, adding a positive gravity will reduce the magnitude of vy, making them rise slower and eventually fall). For explosion particles, gravity will make their vy increase (they fall down).

When a rocket explodes, create a bunch of explosion particles at its position. The rocket is then removed from the particles array.

For the explosion particles, each has a lifespan. As they age, their alpha decreases, making them fade out.

Efficient array management: When a particle is dead (rocket exploded or lifespan <=0), mark it for removal. But removing elements from the middle of an array can be inefficient. One approach is to use a "graveyard" array and then filter them out at the end of each frame, or swap and pop. Alternatively, since particles are added and removed frequently, perhaps using a pool or a linked list structure, but for simplicity, maybe just check each particle's alive status and remove them by creating a new array each frame. However, that could be inefficient for large numbers. Alternatively, iterate backward and remove elements, but that complicates the loop.

Alternatively, use two arrays: one for active particles and another for new particles to add, and then merge them each frame. But perhaps for simplicity, during the update phase, we can check each particle and collect those that are still alive, and replace the array each frame. That way, we don't have to shift elements. For example, in each frame, create a new array that includes only particles that are still active. But this could be memory intensive if there are many particles. However, given that the number of particles is in the hundreds or thousands, this might be manageable.

Alternatively, during the update loop, iterate through the particles array, and for each particle, update it. If it's dead, mark it (e.g., with a flag), and then after processing all, filter out the dead ones. That way, the array is cleaned up once per frame.

So during the update step:

for (let i = 0; i < particles.length; i++) {
    particles[i].update(deltaTime);
}

Then, after updating all, filter the array to remove dead particles.

particles = particles.filter(p => p.alive);

But this creates a new array each time. For performance, perhaps better to do it in place. But for simplicity, this approach is acceptable.

Now, for the Rocket's explosion condition. The rocket should explode when it reaches a certain height or after a certain time. Let's say after a random time between 1 and 2 seconds. So each rocket has a fuseTime (e.g., 1000-2000 ms), and when the elapsed time since launch exceeds that, it explodes.

Alternatively, check if the rocket's velocity is low enough (since as it rises, gravity reduces vy until it starts falling). But that might be more complex. Using a fuse time is simpler.

So each Rocket will have a creationTime (timestamp when it was created), and a fuseDuration (random between 1 and 2 seconds). When the current time minus creationTime exceeds fuseDuration, it's time to explode.

When a rocket explodes, we need to remove it from the particles array and create a bunch of explosion particles.

Now, for the explosion particles:

Each explosion creates, say, 30-80 particles. Each has:

- Position same as the rocket's position at explosion.
- Random velocity in all directions (but radiating outwards). So, for example, generate a random angle and speed.
- Lifespan (e.g., 1-3 seconds).
- Color, maybe random or based on the rocket.
- Size.

When drawing, explosion particles can be drawn as small circles with varying alpha based on their remaining lifespan.

Now, the game loop:

The gameLoop function is called with a timestamp. We need to calculate the delta time between frames to make movement frame-rate independent.

But since requestAnimationFrame passes the current timestamp, we can track the previous time and compute delta.

Wait, in the initial code, the gameLoop function is set up as:

function gameLoop(timestamp) {
    // ...
    requestAnimationFrame(gameLoop);
}

So the first time it's called, timestamp is the current time. Then, in the loop, we can keep track of the previous timestamp to calculate delta.

But perhaps better to have a variable that holds the previous time, and compute delta as timestamp - previousTime, then set previousTime to timestamp.

Alternatively, in the loop:

let deltaTime = timestamp - previousTimestamp;
previousTimestamp = timestamp;

But how to handle the first frame? Maybe initialize previousTimestamp to 0, and then on first frame, delta will be the time since the page loaded, but that's okay.

So in the code:

let previousTime = 0;

function gameLoop(timestamp) {
    let deltaTime = timestamp - previousTime;
    previousTime = timestamp;

    // update logic using deltaTime

    requestAnimationFrame(gameLoop);
}

But deltaTime is in milliseconds. So when updating positions, we need to convert that into a factor. For example, velocity is in pixels per second, so multiply by deltaTime / 1000 to get the change in position.

Now, for the particles:

Each particle (rocket or explosion) should have an update method that takes deltaTime.

For the Rocket:

In update:

- Apply gravity: vy += gravity * deltaTime / 1000 (since gravity is in pixels per second squared)
- Update position: x += vx * deltaTime / 1000; y += vy * deltaTime / 1000;
- Check if it's time to explode (current time - creationTime >= fuseDuration)
- If so, explode: create explosion particles, mark rocket as dead (so it's removed from the array)

For ExplosionParticle:

In update:

- Apply gravity (vy += gravity * deltaTime / 1000)
- Update position
- Decrease lifespan by deltaTime
- If lifespan <=0, mark as dead

Drawing:

For rockets, maybe draw a small white or yellow dot, or a streak. For explosion particles, draw circles with color and alpha based on lifespan.

Now, the autonomous launching:

We need a variable to track the last launch time. For example:

let lastLaunchTime = 0;
const minLaunchInterval = 500; // 0.5 seconds
const maxLaunchInterval = 2000; // 2 seconds

In the game loop, check if (timestamp - lastLaunchTime) >= randomInterval. But how to handle the random interval? Maybe generate a new interval each time a rocket is launched.

So:

if (timestamp - lastLaunchTime >= launchInterval) {
    launchRocket();
    lastLaunchTime = timestamp;
    launchInterval = Math.random() * (maxLaunchInterval - minLaunchInterval) + minLaunchInterval;
}

Wait, but launchInterval should be a variable that is set each time a rocket is launched. So:

let launchInterval = Math.random() * (maxLaunchInterval - minLaunchInterval) + minLaunchInterval;

Then, in the loop:

if (timestamp - lastLaunchTime >= launchInterval) {
    launchRocket();
    lastLaunchTime = timestamp;
    launchInterval = Math.random() * (maxLaunchInterval - minLaunchInterval) + minLaunchInterval;
}

But how to initialize launchInterval? Maybe set it once outside the loop.

Now, the launchRocket function creates a new Rocket instance and adds it to the particles array.

For the Rocket's initial position: bottom center. So x is W/2 plus some random offset. y starts at H (bottom of canvas), but maybe slightly above to make it look like it's launched from the ground. Or perhaps y starts at H, and vy is negative (upwards).

Wait, in canvas coordinates, (0,0) is top-left. So the bottom of the canvas is y=H. So the rocket starts at (x, H), with a slight horizontal variation.

So for the Rocket's initial position:

x: W/2 + (Math.random() - 0.5) * 20 (for example, some randomness)
y: H

Velocity: vx is small random, vy is negative (upwards). For example, vx between -0.5 and 0.5, vy between -3 and -2 (but need to adjust based on gravity and desired speed).

Gravity: let's define a gravity constant. Since velocity is in pixels per second, gravity can be a positive value (since it acts downward). For example, gravity = 0.5 (pixels per second squared). So each second, the velocity in y direction increases by 0.5 (so for a rocket going up, vy is negative, so adding gravity (positive) reduces the magnitude of vy, slowing it down until it starts falling).

Now, for the explosion particles:

When a rocket explodes, create a number of particles (e.g., 50). Each particle has:

- position same as the rocket's position at explosion.
- velocity: random direction and speed. For example, generate a random angle (0 to 2π) and speed (e.g., 2-5 pixels per second), then convert to vx and vy.
- lifespan: random between 1 and 3 seconds.
- color: random HSL color, maybe with some saturation and lightness.
- size: small, like 2-4 pixels.

In their update method, apply gravity (so they start with some velocity, then gravity pulls them down).

Now, for the drawing part:

Clear the canvas each frame with a dark background (ctx.fillStyle = '#000'; ctx.fillRect(0,0,W,H);). Then, for each particle, draw it.

For rockets, maybe a small white circle or a streak. For explosion particles, a circle with the color and alpha based on their lifespan.

For fading, the alpha can be (lifespanRemaining / initialLifespan). For example, if a particle has 2 seconds lifespan, and has 1 second left, alpha is 0.5.

But since the lifespan is in seconds, and each frame we subtract deltaTime (in seconds?), maybe track the remaining lifespan in milliseconds or seconds.

Alternatively, each ExplosionParticle has a lifespan (in milliseconds), and a birthTime. Then, remaining = (currentTimestamp - birthTime) / lifespan (but that might complicate). Alternatively, track the remaining time in seconds, and subtract deltaTime each frame.

Let me think:

When creating an ExplosionParticle, it has a lifespan (e.g., 2000 ms). Then, in each update, we subtract deltaTime (converted to seconds?) from the lifespan. Or track in milliseconds:

particle.lifespan -= deltaTime;

if (particle.lifespan <=0) { dead }

But deltaTime is in milliseconds. So yes, that works.

For the alpha:

alpha = particle.lifespan / initialLifespan;

But since the initialLifespan varies per particle, perhaps store the initial lifespan when creating the particle.

Alternatively, track the age and compute alpha as (1 - age / lifespan).

But perhaps easier to track remaining time.

So for each ExplosionParticle:

this.lifespan = random between 1000 and 3000 ms (1-3 seconds)
this.age = 0;

In update:

this.age += deltaTime;
if (this.age >= this.lifespan) {
    this.alive = false;
}
alpha = 1 - (this.age / this.lifespan);

But then, for drawing, set the context's globalAlpha to this alpha before drawing.

But modifying globalAlpha affects all subsequent draws, so need to save and restore the context state.

Alternatively, set the alpha in the fillStyle for each particle.

For example:

ctx.fillStyle = `hsla(${color}, 1, 1, ${alpha})`;

But that could be more efficient.

Alternatively, for each particle, when drawing, set the fillStyle with the computed alpha.

So for the ExplosionParticle's draw method:

ctx.fillStyle = this.color; // which includes the alpha?

Wait, perhaps better to compute the alpha based on remaining lifespan.

So:

const alpha = this.lifespan - this.age > 0 ? (this.lifespan - this.age) / this.lifespan : 0;

But perhaps more accurately, compute as (1 - this.age / this.lifespan), but clamp to 0.

But during update, we can compute the alpha as part of the particle's state.

Alternatively, during the draw phase, compute it.

But to avoid recomputing, maybe store the initial lifespan and compute alpha each frame.

Now, putting it all together.

Let's outline the classes.

Rocket class:

class Rocket {
    constructor(x, y) {
        this.x = x;
        this.y = y;
        this.vx = (Math.random() - 0.5) * 0.5; // slight horizontal movement
        this.vy = -2 - Math.random(); // upwards velocity
        this.gravity = 0.05; // gravity applied each frame (but need to multiply by deltaTime)
        this.fuseDuration = 1000 + Math.random() * 1000; // 1-2 seconds
        this.created = performance.now();
        this.alive = true;
    }

    update(deltaTime) {
        // apply gravity
        this.vy += this.gravity * deltaTime / 1000; // since deltaTime is in ms, divide by 1000 to get seconds
        this.x += this.vx * deltaTime / 1000;
        this.y += this.vy * deltaTime / 1000;

        // check if it's time to explode
        const now = performance.now();
        if (now - this.created >= this.fuseDuration) {
            this.explode();
        }
    }

    explode() {
        // create explosion particles
        const particles = [];
        const count = 50 + Math.random() * 30; // 50-80 particles
        for (let i = 0; i < count; i++) {
            particles.push(new ExplosionParticle(this.x, this.y));
        }
        // add particles to the main array
        // but how? Maybe the explode method adds them to the global particles array
        // So perhaps the Rocket has a reference to the particles array, but that's not ideal.
        // Alternatively, when a rocket explodes, it's removed from the array, and the explosion particles are added.
        // So in the game loop, after updating all particles, we check for explosions and add the new particles.
        // Hmm, but how to handle that. Maybe the Rocket's explode method creates the particles and adds them to the array, then marks itself as dead.

        // So in the game loop, during update, when a rocket explodes, it creates the particles and adds them to the particles array, then sets alive to false.

        // So in the Rocket's explode method:
        for (let i = 0; i < count; i++) {
            particlesArray.push(new ExplosionParticle(this.x, this.y));
        }
        this.alive = false;
    }

    draw(ctx) {
        ctx.beginPath();
        ctx.arc(this.x, this.y, 2, 0, Math.PI * 2);
        ctx.fillStyle = 'white';
        ctx.fill();
    }
}

Wait, but how does the Rocket know about the particles array? That's a problem. The Rocket shouldn't have to know about the global array. So perhaps when a rocket explodes, it returns the explosion particles, and the game loop adds them.

Alternatively, during the update loop, when a rocket is processed, if it explodes, create the particles and add them to the array, then mark the rocket as dead.

But how to structure that.

Maybe during the update phase:

for (let i = 0; i < particles.length; i++) {
    particles[i].update(deltaTime);
    if (particles[i] instanceof Rocket && particles[i].exploded) {
        // create explosion particles and add to array
        // but how to check if it exploded in this frame?
    }
}

Alternatively, during the Rocket's update, when it explodes, it creates the particles and adds them to the array, then marks itself as dead.

But then the Rocket needs a reference to the particles array, which is not ideal. So perhaps better to have a central manager that handles this.

Alternatively, during the update loop, after updating each particle, check if it's a rocket that needs to explode. For example:

for (let i = 0; i < particles.length; i++) {
    particles[i].update(deltaTime);
    if (particles[i] instanceof Rocket) {
        if (particles[i].shouldExplode()) {
            // create explosion particles and add to array
            const explosionParticles = particles[i].explode();
            particles.push(...explosionParticles);
            particles[i].alive = false;
        }
    }
}

But this requires checking each particle's type, which may not be efficient, but for the scope of this project, it's acceptable.

Alternatively, the Rocket's update method can return whether it exploded, and then the main loop can handle adding the particles.

But perhaps the Rocket's explode method creates the particles and returns them. Then, during the update loop, after updating a rocket, if it's time to explode, call explode and add the particles.

But how to structure this.

Let me think. Each Rocket has an update method. When the fuse time is reached, it explodes. The explode method creates the particles and adds them to the global particles array.

But the Rocket needs access to the particles array. That's not good design. So perhaps the game loop should handle this.

Alternative approach:

In the game loop, during the update phase:

for (let i = 0; i < particles.length; i++) {
    const p = particles[i];
    p.update(deltaTime);

    if (p instanceof Rocket && p.shouldExplode()) {
        // create explosion particles
        const explosionParticles = createExplosionParticles(p.x, p.y);
        particles.push(...explosionParticles);
        // mark rocket to be removed
        p.alive = false;
    }
}

But how does the Rocket know if it should explode? The Rocket's update method would have already checked the time and set a flag, like this.exploded = true.

Alternatively, in the Rocket's update method, after checking the time, set a flag like this.exploded = true. Then, in the loop above, check if it's a Rocket and exploded.

So:

class Rocket {
    // ...
    update(deltaTime) {
        // ... movement and gravity
        const now = performance.now();
        if (now - this.created >= this.fuseDuration) {
            this.exploded = true;
        }
    }

    // ...
}

Then in the game loop:

for (let i = 0; i < particles.length; i++) {
    const p = particles[i];
    p.update(deltaTime);

    if (p instanceof Rocket && p.exploded) {
        // create explosion particles
        const count = 50 + Math.random() * 30;
        for (let j = 0; j < count; j++) {
            particles.push(new ExplosionParticle(p.x, p.y));
        }
        p.alive = false;
    }
}

But this requires that the Rocket has an 'exploded' flag that is set during update. Then, during the loop, after updating all particles, we check for any rockets that have exploded and create the particles.

But this approach may have a problem: during the same frame, the rocket is updated, the exploded flag is set, and then in the same loop iteration, the particles are added. However, since the loop is processing each particle in order, and the rocket is at index i, adding new particles to the array will not affect the current loop (since we're iterating up to the original length). But after the loop, the particles array will have the new particles, which will be processed in the next frame.

This seems acceptable.

So the steps during the game loop's update phase:

1. Update all particles (apply movement, gravity, check for explosion conditions).
2. For each particle, if it's a Rocket that has exploded (exploded flag is true), create explosion particles and add to the array, then mark the rocket as dead (alive = false).
3. After updating all particles, filter out the dead ones (alive === false).

Wait, but in step 2, when we add the explosion particles to the array, they are added during the loop. However, since we are iterating over the original array (particles.length at the start of the loop), the new particles added will not be processed in this frame, which is correct.

But then, after processing all particles, we need to filter out the dead ones (those with alive === false). However, the Rocket that exploded is marked as alive = false during step 2, so during the filtering step, it will be removed.

But how to handle the filtering.

So after updating all particles, we can filter the array:

particles = particles.filter(p => p.alive);

This will remove all particles (including rockets that exploded and particles whose lifespan is up).

But the ExplosionParticles also have an alive flag. So during their update, they set alive to false when lifespan is reached.

So the ExplosionParticle class:

class ExplosionParticle {
    constructor(x, y) {
        this.x = x;
        this.y = y;
        this.vx = (Math.random() - 0.5) * 4; // random horizontal velocity
        this.vy = (Math.random() - 0.5) * 4; // random vertical velocity, could be upwards or downwards
        this.gravity = 0.05;
        this.lifespan = 1000 + Math.random() * 2000; // 1-3 seconds
        this.age = 0;
        this.color = `hsla(${Math.random() * 360}, 100%, 70%, 1)`;
        this.size = 2 + Math.random() * 2;
        this.alive = true;
    }

    update(deltaTime) {
        this.age += deltaTime;
        if (this.age >= this.lifespan) {
            this.alive = false;
            return;
        }

        // apply gravity
        this.vy += this.gravity * deltaTime / 1000;
        this.x += this.vx * deltaTime / 1000;
        this.y += this.vy * deltaTime / 1000;
    }

    draw(ctx) {
        const alpha = 1 - (this.age / this.lifespan);
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.fillStyle = this.color.replace(')', `, ${alpha})`);
        ctx.fill();
    }
}

Wait, the color is initially hsla with alpha 1. Then, during draw, we replace the alpha part. For example, original color is hsla(120, 100%, 70%, 1), and we replace the last part with alpha. So using replace(')', `, ${alpha})') would work if the original string ends with ')'. Alternatively, split and reconstruct.

Alternatively, create the color string dynamically each time. But for performance, perhaps better to precompute the hue and then use it with varying alpha.

Alternatively, during draw:

ctx.fillStyle = `hsla(${this.hue}, 100%, 70%, ${alpha})`;

But in the constructor, we can store the hue instead of the full color string.

Let me adjust that:

class ExplosionParticle {
    constructor(x, y) {
        this.x = x;
        this.y = y;
        this.vx = (Math.random() - 0.5) * 4;
        this.vy = (Math.random() - 0.5) * 4;
        this.gravity = 0.05;
        this.lifespan = 1000 + Math.random() * 2000;
        this.age = 0;
        this.hue = Math.random() * 360;
        this.size = 2 + Math.random() * 2;
        this.alive = true;
    }

    draw(ctx) {
        const alpha = 1 - (this.age / this.lifespan);
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.fillStyle = `hsla(${this.hue}, 100%, 70%, ${alpha})`;
        ctx.fill();
    }
}

This way, the hue is stored, and alpha is computed each frame.

Now, back to the game loop.

Putting it all together:

In the script section:

const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const W = canvas.width;
const H = canvas.height;

let particles = [];
let lastLaunchTime = 0;
let launchInterval = Math.random() * (2000 - 500) + 500; // between 0.5 and 2 seconds

function gameLoop(timestamp) {
    // Calculate delta time
    let deltaTime = timestamp - (previousTime || timestamp);
    previousTime = timestamp;

    // Update logic
    // Update all particles
    for (let i = 0; i < particles.length; i++) {
        particles[i].update(deltaTime);
    }

    // Check for rockets that exploded and create explosion particles
    for (let i = 0; i < particles.length; i++) {
        const p = particles[i];
        if (p instanceof Rocket && p.exploded) {
            // Create explosion particles
            const count = 50 + Math.random() * 30;
            for (let j = 0; j < count; j++) {
                particles.push(new ExplosionParticle(p.x, p.y));
            }
            p.alive = false; // mark for removal
        }
    }

    // Remove dead particles
    particles = particles.filter(p => p.alive);

    // Check if it's time to launch a new rocket
    if (timestamp - lastLaunchTime >= launchInterval) {
        launchRocket();
        lastLaunchTime = timestamp;
        launchInterval = Math.random() * (2000 - 500) + 500;
    }

    // Draw logic
    ctx.fillStyle = '#000';
    ctx.fillRect(0, 0, W, H);

    for (const p of particles) {
        p.draw(ctx);
    }

    requestAnimationFrame(gameLoop);
}

// Start the loop
let previousTime = 0;
requestAnimationFrame(gameLoop);

function launchRocket() {
    const x = W / 2 + (Math.random() - 0.5) * 20; // some horizontal variation
    const y = H; // starts at the bottom
    particles.push(new Rocket(x, y));
}

But wait, the Rocket class isn't defined yet. Need to define it.

Also, in the Rocket's update method, we need to set the exploded flag.

So the Rocket class:

class Rocket {
    constructor(x, y) {
        this.x = x;
        this.y = y;
        this.vx = (Math.random() - 0.5) * 0.5;
        this.vy = -2 - Math.random(); // upwards
        this.gravity = 0.05;
        this.fuseDuration = 1000 + Math.random() * 1000; // 1-2 seconds
        this.created = performance.now();
        this.exploded = false;
        this.alive = true;
    }

    update(deltaTime) {
        // Apply gravity
        this.vy += this.gravity * deltaTime / 1000;
        this.x += this.vx * deltaTime / 1000;
        this.y += this.vy * deltaTime / 1000;

        // Check if it's time to explode
        const now = performance.now();
        if (now - this.created >= this.fuseDuration) {
            this.exploded = true;
        }
    }

    draw(ctx) {
        ctx.beginPath();
        ctx.arc(this.x, this.y, 2, 0, Math.PI * 2);
        ctx.fillStyle = 'white';
        ctx.fill();
    }
}

Wait, but in the game loop, after updating all particles, we have a second loop that checks for rockets that exploded. However, in the current setup, the Rocket's update method sets exploded to true, but the alive flag is still true until the game loop's second loop marks it as false. But in the code above, in the second loop, when a rocket has exploded, we set p.alive = false. So that should work.

But there's a problem: in the game loop, during the first loop (updating all particles), the Rocket's update sets exploded to true. Then, in the second loop, we check for exploded rockets and create the particles, then set alive to false. Then, during the filtering step, the rocket is removed.

But what if the rocket explodes and is processed in the second loop, but during the same frame, another particle is updated? Not sure, but this should be okay.

But there's a possible issue: the second loop iterates over particles.length, which includes the newly added explosion particles from previous iterations. For example, if during the loop, a rocket at index i explodes, and we add 50 particles to the array, then when i increments, the loop will process those new particles in the same frame. However, those new particles are explosion particles, which are not rockets, so the check (p instanceof Rocket) will be false, so they are not processed. This should be okay.

But this could lead to a longer loop time if many rockets explode in the same frame, but for the purposes of this simulation, it's acceptable.

Another thing to consider: the initial launch interval. The first rocket is launched after launchInterval milliseconds. But initially, lastLaunchTime is 0, so timestamp - lastLaunchTime will be the time since the page loaded. So if the first frame's timestamp is, say, 100ms, and launchInterval is 1500ms, then the first rocket will launch after 1500ms from the start.

But perhaps better to set lastLaunchTime to the current timestamp when starting the loop. Alternatively, initialize lastLaunchTime to performance.now() when starting.

Wait, in the current code:

let lastLaunchTime = 0;
let launchInterval = ...;

Then, in the gameLoop:

if (timestamp - lastLaunchTime >= launchInterval) {
    launchRocket();
    lastLaunchTime = timestamp;
    launchInterval = ...;
}

But initially, lastLaunchTime is 0. So if the first timestamp is, say, 100, and launchInterval is 500, then 100 - 0 >= 500? No. So the first launch will happen after launchInterval time.

But perhaps better to initialize lastLaunchTime to the current time when starting the loop. For example:

let previousTime = 0;
let lastLaunchTime = performance.now();
let launchInterval = Math.random() * (2000 - 500) + 500;

Then, in the gameLoop:

if (timestamp - lastLaunchTime >= launchInterval) {
    launchRocket();
    lastLaunchTime = timestamp;
    launchInterval = ...;
}

This way, the first rocket launches after launchInterval time from the start.

Now, testing this code.

Potential issues:

1. The Rocket's gravity is applied as this.vy += this.gravity * deltaTime / 1000. But gravity is a acceleration in m/s², and deltaTime is in milliseconds. So the units are correct.

But the values may need tuning. For example, the Rocket's vy starts at -2 (upwards), and gravity is 0.05. So each second, the vy increases by 0.05. So after 1 second, vy is -2 + 0.05 * 1 = -1.95. So the Rocket slows down.

But the fuseDuration is 1-2 seconds, so the Rocket will reach its peak and start falling.

The ExplosionParticle's velocity is random, and gravity is applied.

Another thing: the canvas is cleared with ctx.fillRect(0, 0, W, H) each frame, which is correct.

Now, putting all the code together.

Also, need to define the ExplosionParticle class.

Now, the complete code:

In the script section:

const canvas = document.getElementById('gameLoop');
const ctx = canvas.getContext('2d');
const W = canvas.width;
const H = canvas.height;

let particles = [];
let previousTime = 0;
let lastLaunchTime = performance.now();
let launchInterval = Math.random() * (2000 - 500) + 500; // 0.5 to 2 seconds

class Rocket {
    constructor(x, y) {
        this.x = x;
        this.y = y;
        this.vx = (Math.random() - 0.5) * 0.5;
        this.vy = -2 - Math.random(); // upwards
        this.gravity = 0.05;
        this.fuseDuration = 1000 + Math.random() * 1000; // 1-2 seconds
        this.created = performance.now();
        this.exploded = false;
        this.alive = true;
    }

    update(deltaTime) {
        // Apply gravity
        this.vy += this.gravity * deltaTime / 1000;
        this.x += this.vx * deltaTime / 1000;
        this.y += this.vy * deltaTime / 1000;

        // Check if it's time to explode
        const now = performance.now();
        if (now - this.created >= this.fuseDuration) {
            this.exploded = true;
        }
    }

    draw(ctx) {
        ctx.beginPath();
        ctx.arc(this.x, this.y, 2, 0, Math.PI * 2);
        ctx.fillStyle = 'white';
        ctx.fill();
    }
}

class ExplosionParticle {
    constructor(x, y) {
        this.x = x;
        this.y = y;
        this.vx = (Math.random() - 0.5) * 4;
        this.vy = (Math.random() - 0.5) * 4;
        this.gravity = 0.05;
        this.lifespan = 1000 + Math.random() * 2000; // 1-3 seconds
        this.age = 0;
        this.hue = Math.random() * 360;
        this.size = 2 + Math.random() * 2;
        this.alive = true;
    }

    update(deltaTime) {
        this.age += deltaTime;
        if (this.age >= this.lifespan) {
            this.alive = false;
            return;
        }

        // Apply gravity
        this.vy += this.gravity * deltaTime / 1000;
        this.x += this.vx * deltaTime / 1000;
        this.y += this.vy * deltaTime / 1000;
    }

    draw(ctx) {
        const alpha = 1 - (this.age / this.lifespan);
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.fillStyle = `hsla(${this.hue}, 100%, 70%, ${alpha})`;
        ctx.fill();
    }
}

function launchRocket() {
    const x = W / 2 + (Math.random() - 0.5) * 20;
    const y = H;
    particles.push(new Rocket(x, y));
}

function gameLoop(timestamp) {
    // Calculate delta time
    let deltaTime = timestamp - (previousTime || timestamp);
    previousTime = timestamp;

    // Update all particles
    for (let i = 0; i < particles.length; i++) {
        particles[i].update(deltaTime);
    }

    // Check for rockets that exploded and create explosion particles
    for (let i = 0; i < particles.length; i++) {
        const p = particles[i];
        if (p instanceof Rocket && p.exploded) {
            const count = 50 + Math.random() * 30;
            for (let j = 0; j < count; j++) {
                particles.push(new ExplosionParticle(p.x, p.y));
            }
            p.alive = false;
        }
    }

    // Remove dead particles
    particles = particles.filter(p => p.alive);

    // Check if it's time to launch a new rocket
    if (timestamp - lastLaunchTime >= launchInterval) {
        launchRocket();
        lastLaunchTime = timestamp;
        launchInterval = Math.random() * (2000 - 500) + 500;
    }

    // Draw
    ctx.fillStyle = '#000';
    ctx.fillRect(0, 0, W, H);

    for (const p of particles) {
        p.draw(ctx);
    }

    requestAnimationFrame(gameLoop);
}

// Start the loop
requestAnimationFrame(gameLoop);

This should work.

Potential issues:

1. The initial canvas size: if the canvas is not resized, but the code uses W and H as the initial width and height. If the canvas is resized, it won't adjust, but for this example, it's fine.

2. Performance: with many particles, the filter and loops may be slow, but for the scope of this question, it's acceptable.

3. The Rocket's explosion particles are added in the same frame as the Rocket's update, which may cause the particles to be added and then filtered in the same frame. But since the Rocket is marked as alive = false during the second loop, and then filtered out, it should be fine.

Testing this code should show rockets launching, exploding into colored particles that fall due to gravity and fade out.

Now, to write the final answer with the code.
</think>
To create a visually appealing and dynamic fireworks simulation using JavaScript and the HTML5 Canvas, we'll follow a structured approach. The simulation will include rockets that launch, explode into colorful particles, and then fade away. The implementation will use object-oriented programming for clarity and maintainability.

### **Step-by-Step Explanation**

1. **Setup the Canvas**: 
   - We start by getting a reference to the canvas element and its context.
   - Define the width and height of the canvas.

2. **Global Variables**:
   - `particles`: An array to hold all active particles (rockets and explosion particles).
   - `previousTime`: Tracks the time of the last frame to calculate delta time.
   - `lastLaunchTime`: Tracks when the last rocket was launched.
   - `launchInterval`: The time interval between rocket launches.

3. **Rocket Class**:
   - Represents a rocket that launches upwards.
   - Includes properties for position, velocity, gravity, fuse duration, and explosion status.
   - The `update` method handles movement and checks if the rocket should explode based on its fuse duration.

4. **Explosion Particle Class**:
   - Represents a particle from an explosion.
   - Includes properties for position, velocity, gravity, lifespan, hue, size, and alpha.
   - The `update` method handles movement and checks if the particle should be removed based on its lifespan.
   - The `draw` method renders the particle with a color based on its hue and current alpha.

5. **Game Loop**:
   - The main loop that updates and renders all particles.
   - Calculates delta time for smooth animations.
   - Updates all particles and checks for rockets that have exploded to create new explosion particles.
   - Removes dead particles from the array.
   - Checks if it's time to launch a new rocket.
   - Clears the canvas and redraws all active particles.

### **Complete Code**

```html
<canvas id="gameCanvas" width="800" height="600"></canvas>

<script>
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const W = canvas.width;
const H = canvas.height;

let particles = [];
let previousTime = 0;
let lastLaunchTime = performance.now();
let launchInterval = Math.random() * (2000 - 500) + 500; // 0.5 to 2 seconds

class Rocket {
    constructor(x, y) {
        this.x = x;
        this.y = y;
        this.vx = (Math.random() - 0.5) * 0.5;
        this.vy = -2 - Math.random(); // upwards
        this.gravity = 0.05;
        this.fuseDuration = 1000 + Math.random() * 1000; // 1-2 seconds
        this.created = performance.now();
        this.exploded = false;
        this.alive = true;
    }

    update(deltaTime) {
        // Apply gravity
        this.vy += this.gravity * deltaTime / 1000;
        this.x += this.vx * deltaTime / 1000;
        this.y += this.vy * deltaTime / 1000;

        // Check if it's time to explode
        const now = performance.now();
        if (now - this.created >= this.fuseDuration) {
            this.exploded = true;
        }
    }

    draw(ctx) {
        ctx.beginPath();
        ctx.arc(this.x, this.y, 2, 0, Math.PI * 2);
        ctx.fillStyle = 'white';
        ctx.fill();
    }
}

class ExplosionParticle {
    constructor(x, y) {
        this.x = x;
        this.y = y;
        this.vx = (Math.random() - 0.5) * 4;
        this.vy = (Math.random() - 0.5) * 4;
        this.gravity = 0.05;
        this.lifespan = 1000 + Math.random() * 2000; // 1-3 seconds
        this.age = 0;
        this.hue = Math.random() * 360;
        this.size = 2 + Math.random() * 2;
        this.alive = true;
    }

    update(deltaTime) {
        this.age += deltaTime;
        if (this.age >= this.lifespan) {
            this.alive = false;
            return;
        }

        // Apply gravity
        this.vy += this.gravity * deltaTime / 1000;
        this.x += this.vx * deltaTime / 1000;
        this.y += this.vy * deltaTime / 1000;
    }

    draw(ctx) {
        const alpha = 1 - (this.age / this.lifespan);
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.fillStyle = `hsla(${this.hue}, 100%, 70%, ${alpha})`;
        ctx.fill();
    }
}

function launchRocket() {
    const x = W / 2 + (Math.random() - 0.5) * 20;
    const y = H;
    particles.push(new Rocket(x, y));
}

function gameLoop(timestamp) {
    // Calculate delta time
    let deltaTime = timestamp - (previousTime || timestamp);
    previousTime = timestamp;

    // Update all particles
    for (let i = 0; i < particles.length; i++) {
        particles[i].update(deltaTime);
    }

    // Check for rockets that exploded and create explosion particles
    for (let i = 0; i < particles.length; i++) {
        const p = particles[i];
        if (p instanceof Rocket && p.exploded) {
            const count = 50 + Math.random() * 30;
            for (let j = 0; j < count; j++) {
                particles.push(new ExplosionParticle(p.x, p.y));
            }
            p.alive = false;
        }
    }

    // Remove dead particles
    particles = particles.filter(p => p.alive);

    // Check if it's time to launch a new rocket
    if (timestamp - lastLaunchTime >= launchInterval) {
        launchRocket();
        lastLaunchTime = timestamp;
        launchInterval = Math.random() * (2000 - 500) + 500;
    }

    // Draw
    ctx.fillStyle = '#000';
    ctx.fillRect(0, 0, W, H);

    for (const p of particles) {
        p.draw(ctx);
    }

    requestAnimationFrame(gameLoop);
}

// Start the loop
requestAnimationFrame(gameLoop);
</script>
```

### **How It Works**

1. **Rocket Launch**: 
   - Rockets are launched at random intervals between 0.5 and 2 seconds.
   - Each rocket starts at the bottom center of the canvas and moves upwards.

2. **Rocket Explosion**:
   - After a random fuse duration (1-2 seconds), the rocket explodes.
   - Upon explosion, it creates 50-80 explosion particles.

3. **Explosion Particles**:
   - Each particle has a random velocity, hue, size, and lifespan.
   - Particles are affected by gravity and fade out as their lifespan expires.

4. **Rendering**:
   - The canvas is cleared each frame and all active particles are redrawn.
   - Explosion particles use the `hsla` color format to dynamically adjust their alpha (transparency) based on their remaining lifespan.

This implementation provides a visually engaging and dynamic fireworks simulation using JavaScript and the HTML5 Canvas.

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: Nemotron-Super-49B-v1_5-IQ4_XS.gguf -->
<!-- Prompt: fireworks.md -->
<!-- Generation Time: 444.08s -->
<!-- Fallback Used: False -->