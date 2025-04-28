<think>
Okay, so I need to create this Happy Mrs. Chicken simulation. Let me start by breaking down the requirements and figuring out how to approach each part. 

First, the main components are the Chicken and the Eggs. The Chicken moves around the canvas, changes direction when it hits the edge, and lays eggs periodically. The eggs then stay on the screen. The animation should use requestAnimationFrame for smoothness, and I need to handle delta time properly to make sure the movement and egg-laying intervals are consistent regardless of frame rate.

Let me start by setting up the HTML and canvas. The provided boilerplate has a canvas with an id of "simulationCanvas" and some basic styling. I'll use that as the starting point. The canvas is 512x512, which is a good size for a simulation like this.

Next, I need to get the canvas context. That's straightforward:

```javascript
const canvas = document.getElementById("simulationCanvas");
const ctx = canvas.getContext("2d");
```

Now, the Chicken class. Let's define a Chicken object with properties for position, velocity, direction, and state (whether it's wandering or laying an egg). The velocity will determine how fast it moves, and the direction will be a vector (maybe in x and y components) to change its movement direction when it hits a boundary or decides to change direction.

Wait, but the problem mentions "simple game AI rules" for movement. So the chicken should wander around, changing direction occasionally. Also, when it lays an egg, it should pause for a bit, then resume wandering. The egg-laying should be periodic, maybe every few seconds.

Let me think about the Chicken's movement. If I use velocity components (vx, vy), then each frame, I can update the position by vx * dt and vy * dt, where dt is the delta time. When the chicken hits the edge of the canvas, it should reverse the corresponding velocity component (so if it hits the right edge, vx becomes -vx, and similarly for the top and bottom edges). But maybe instead of just reversing direction, the chicken could choose a new random direction after a collision? Hmm, the problem says "boundary handling" so it needs to stay within the canvas. Reversing direction is a simple way, but maybe changing direction to a random angle would be more natural.

Wait, the problem says "simple game AI". Maybe reversing direction when hitting a wall is sufficient. Let's go with that for simplicity. So if the chicken hits the left or right wall, reverse the x-velocity; if it hits the top or bottom, reverse the y-velocity. That way, it bounces around like a billiard ball. But to make it wander, maybe we can occasionally add some randomness to the direction. For example, every so often, change the velocity to a new random direction with some speed.

Alternatively, maybe the chicken moves in a straight line until it either lays an egg or hits a boundary. Then, when it lays an egg, it pauses, then chooses a new direction. Hmm. Let me consider that approach.

So, when the chicken is wandering, it moves in a straight line. When it either lays an egg or collides with a boundary, it selects a new direction (possibly random) and continues. But the problem says the chicken should "periodically pause its movement to lay an egg". So the laying action is time-based, not collision-based. So the chicken is moving, then after a certain amount of time, it stops moving for a short period to lay an egg, then starts moving again in a possibly new direction.

Therefore, the chicken's state machine has states: wandering, laying. When in wandering state, it moves with velocity (vx, vy). After a certain time (egglaying interval), it transitions to laying state, where it stops moving (velocity becomes zero), creates an egg at its current position, and after a short delay (the laying duration), transitions back to wandering state with a new velocity (direction).

This seems like a good approach. Let's formalize the Chicken class:

```javascript
class Chicken {
    constructor() {
        this.position = {x: canvas.width /2, y: canvas.height/2}; // Start in the center
        this.velocity = {x: 0, y: 0}; // Initial velocity is zero
        this.state = 'wandering'; // Initial state is wandering
        this.egglayingInterval = 3; // Time between egg layings (in seconds)
        this.egglayingTimer = 0; // Timer for egg laying
        this.layingDuration = 1; // Time spent laying an egg (in seconds)
        this.layingTimer = 0; // Timer for laying duration
    }

    update(dt) {
        if (this.state === 'wandering') {
            this.egglayingTimer += dt;
            if (this.egglayingTimer >= this.egglayingInterval) {
                this.state = 'laying';
                this.layingTimer = 0;
            } else {
                this.move(dt);
                this.checkBounds();
            }
        } else if (this.state === 'laying') {
            this.layingTimer += dt;
            if (this.layingTimer >= this.layingDuration) {
                this.state = 'wandering';
                this.egglayingTimer = 0;
                this.changeDirection(); // Choose a new direction after laying
            }
        }
    }

    move(dt) {
        this.position.x += this.velocity.x * dt;
        this.position.y += this.velocity.y * dt;
    }

    checkBounds() {
        if (this.position.x <= 0 || this.position.x >= canvas.width) {
            this.velocity.x = -this.velocity.x; // Reverse x-direction
        }
        if (this.position.y <= 0 || this.position.y >= canvas.height) {
            this.velocity.y = -this.velocity.y; // Reverse y-direction
        }
    }

    changeDirection() {
        // Choose a random direction with some speed
        const speed = 100; // pixels per second
        const angle = Math.random() * 2 * Math.PI;
        this.velocity.x = speed * Math.cos(angle);
        this.velocity.y = speed * Math.sin(angle);
    }

    layEgg() {
        const egg = new Egg(this.position.x, this.position.y);
        eggs.push(egg); // Add the egg to the eggs array
    }
}
```

Now, the Egg class. Each egg is a simple object with position and maybe a visual representation. Let's define the Egg class:

```javascript
class Egg {
    constructor(x, y) {
        this.position = {x, y}; // Position where the egg is laid
        this.radius = 5; // Radius of the egg (oval shape)
    }

    draw(ctx) {
        ctx.beginPath();
        ctx.ellipse(this.position.x, this.position.y, this.radius, this.radius /2, 0, 0, 2*Math.PI); // Draw an oval
        ctx.fillStyle = 'yellow';
        ctx.fill();
        ctx.closePath();
    }
}
```

Now, the main simulation loop. We need to track the chicken and all the eggs. Let's set up the necessary variables:

```javascript
let chicken = new Chicken();
let eggs = [];
let lastTime = 0;

function animationLoop(time) {
    const dt = (time - lastTime) /1000; // Delta time in seconds
    lastTime = time;

    ctx.clearRect(0, 0, canvas.width, canvas.height); // Clear the canvas with the background color

    chicken.update(dt);

    if (chicken.state === 'laying') {
        chicken.layEgg();
    }

    chicken.draw(ctx); // Draw the chicken
    eggs.forEach(egg => egg.draw(ctx)); // Draw all eggs

    requestAnimationFrame(animationLoop);
}

function startSimulation() {
    lastTime = performance.now();
    requestAnimationFrame(animationLoop);
}
```

But wait, the Chicken class doesn't have a draw method yet. Let's add that. The chicken needs a visual representation. Since it's Happy Mrs. Chicken, maybe a simple circle with a beak. Let's represent the chicken as a circle with a triangle beak.

```javascript
Chicken.prototype.draw = function(ctx) {
    // Body: a circle
    ctx.beginPath();
    ctx.arc(this.position.x, this.position.y, 10, 0, 2*Math.PI);
    ctx.fillStyle = 'red'; // Body color
    ctx.fill();

    // Beak: a triangle pointing downwards
    ctx.beginPath();
    const beakLength = 5;
    const beakAngle = 45; // 45 degrees from the center
    const beakX = this.position.x + beakLength * Math.cos(beakAngle * Math.PI/180);
    const beakY = this.position.y + beakLength * Math.sin(beakAngle * Math.PI/180);
    ctx.moveTo(this.position.x, this.position.y);
    ctx.lineTo(beakX, beakY);
    ctx.lineTo(beakX + beakLength/2, beakY + beakLength/2); // Not sure, maybe better to use a triangle
    ctx.closePath();
    ctx.fillStyle = 'yellow'; // Beak color
    ctx.fill();
}
```

Wait, the beak might need a better drawing. Alternatively, maybe a triangle attached to the front of the circle. Let's think. If the chicken is a circle, the beak can be an isosceles triangle attached to the front. To make it face the direction of movement, we can rotate the beak according to the velocity vector.

But since the chicken changes direction when hitting the walls, the beak should point in the direction of velocity. So the beak is a triangle that points in the direction the chicken is moving. To draw this, we can compute the angle of the velocity vector and rotate the beak accordingly.

Let's adjust the draw method:

```javascript
Chicken.prototype.draw = function(ctx) {
    // Body: a circle
    ctx.beginPath();
    ctx.arc(this.position.x, this.position.y, 10, 0, 2*Math.PI);
    ctx.fillStyle = 'red'; // Body color
    ctx.fill();

    // Beak: a triangle pointing in the direction of velocity
    if (this.velocity.x === 0 && this.velocity.y === 0) return; // No beak when not moving

    let angle = Math.atan2(this.velocity.y, this.velocity.x) - Math.PI/2; // Adjust angle to point the beak in the direction of velocity

    ctx.save();
    ctx.translate(this.position.x, this.position.y);
    ctx.rotate(angle);

    // Beak is a triangle
    ctx.beginPath();
    ctx.moveTo(0, 0); // From the center of the chicken
    ctx.lineTo(10, 0); // Extend 10 units in the direction of velocity (overlapping the body)
    ctx.lineTo(5, -5); // Create a triangular beak
    ctx.closePath();
    ctx.fillStyle = 'yellow'; // Beak color
    ctx.fill();
    ctx.restore();
}
```

Hmm, this might look a bit better. The beak is a triangle that points in the direction the chicken is moving. When the chicken changes direction, the beak will rotate to face the new direction. However, when the chicken is laying an egg, it's not moving, so the beak might not be drawn? Or maybe we can still draw it in a resting position. The problem says the chicken should have a beak, so it's important to have it visible even when not moving. Maybe adjust the beak to always point upwards when not moving. Wait, but the direction of the beak is based on velocity. If velocity is zero, maybe the beak points upwards as default.

Alternatively, when the chicken is laying an egg, maybe it's in a state where it's crouching or the beak is pointing down. But given the simplicity, perhaps just having the beak point in the direction of movement, and when not moving, it can point in a default direction, say upwards. Let's adjust the code:

```javascript
Chicken.prototype.draw = function(ctx) {
    // Body: a circle
    ctx.beginPath();
    ctx.arc(this.position.x, this position.y, 10, 0, 2*Math.PI);
    ctx.fillStyle = 'red'; // Body color
    ctx.fill();

    // Beak: a triangle pointing in the direction of velocity or upwards if not moving
    if (this.velocity.x === 0 && this.velocity.y === 0) {
        angle = Math.PI/2; // Point upwards when not moving
    } else {
        angle = Math.atan2(this.velocity.y, this.velocity.x) - Math.PI/2;
    }

    ctx.save();
    ctx.translate(this.position.x, this.position.y);
    ctx.rotate(angle);

    // Beak is a triangle
    ctx.beginPath();
    ctx.moveTo(0, 0); // From the center of the chicken
    ctx.lineTo(10, 0); // Extend 10 units in the direction of velocity
    ctx.lineTo(5, -5); // Create a triangular beak
    ctx.closePath();
    ctx.fillStyle = 'yellow'; // Beak color
    ctx.fill();
    ctx.restore();
}
```

This way, when the chicken is moving, the beak points in the direction of movement, and when it's not moving (like during laying), the beak points upwards. That makes sense.

Now, the Chicken's changeDirection method should assign a new velocity with some speed. Let's adjust that to have a random direction with a speed of, say, 50 pixels per second. But maybe variable speed for more natural wandering? Hmm, the problem says "simple game AI", so constant speed is probably okay. Let's set a speed of 50.

Wait, but in the previous code, the speed was 100. Let me check. When changing direction, we set the velocity components based on a random angle. Let's choose a speed that makes the chicken move at a reasonable pace. Let's say 100 pixels per second. So:

```javascript
Chicken.prototype.changeDirection = function() {
    const speed = 100; // pixels per second
    const angle = Math.random() * 2 * Math.PI;
    this.velocity.x = speed * Math.cos(angle);
    this.velocity.y = speed * Math.sin(angle);
}
```

But when the chicken is bouncing off the walls, the velocity reverses direction. So the speed remains constant, but the direction changes. However, when the chicken lays an egg, it selects a new random direction. This combination of bouncing and random direction changes after laying should create a wandering path.

Wait, but in the current setup, when the chicken hits a wall, it reverses direction, which would mean it continues moving in the reversed direction until it either hits another wall or lays an egg. However, the problem states that the chicken should wander with occasional direction changes. Maybe instead of only reversing direction on collision, we can sometimes change direction randomly even without hitting a wall. That would make the wandering more natural.

To implement that, we can add a mechanism where every so often, the chicken randomly changes direction, regardless of walls. Let's adjust the update method:

```javascript
Chicken.prototype.update = function(dt) {
    if (this.state === 'wandering') {
        this.egglayingTimer += dt;
        if (this.egglayingTimer >= this.egglayingInterval) {
            this.state = 'laying';
            this.layingTimer = 0;
        } else {
            this.move(dt);
            this.checkBounds();
            this.checkRandomDirectionChange(dt);
        }
    } else if (this.state === 'laying') {
        this.layingTimer += dt;
        if (this.layingTimer >= this.layingDuration) {
            this.state = 'wandering';
            this.egglayingTimer = 0;
            this.changeDirection(); // Choose a new direction after laying
        }
    }
}

Chicken.prototype.checkRandomDirectionChange = function(dt) {
    const directionChangeProbability = 0.01; // 1% chance per second
    const directionChangeInterval = 1 / directionChangeProbability; // Average time between direction changes
    if (Math.random() < directionChangeProbability * dt) { // Check if random number is less than probability scaled by dt
        this.changeDirection();
    }
}
```

This adds a 1% chance every second for the chicken to change direction, creating a more wandering path. The direction change is handled by the existing `changeDirection` method. This should make the chicken's path less predictable and more life-like.

Now, let's tie everything together. The main script initializes the chicken, starts the animation loop, and handles drawing. The key parts are:

- Initializing the chicken at the center with zero velocity.
- Starting the animation loop with `requestAnimationFrame`.

But wait, in the current setup, when the chicken is in the 'laying' state, it stops moving and lays an egg. The egg is added to the eggs array, which is then drawn each frame. However, the eggs should remain on the screen even after the chicken moves away. The problem doesn't specify when to remove the eggs, so maybe they stay forever? But that would clutter the screen. Alternatively, maybe eggs disappear after some time. The problem says "eggs remain on screen", so perhaps they don't disappear unless the simulation is reset. However, since the problem doesn't specify removing eggs, we can just keep them all on the screen. But in reality, after many eggs, the screen would be filled, so maybe we need a simple mechanism to remove old eggs. But since the problem doesn't mention egg lifespan, I'll assume they stay forever.

However, for the purposes of this simulation, to prevent the screen from becoming too cluttered, maybe we can limit the number of eggs or have them disappear after a certain time. Let's check the problem statement again: "eggs remain on screen". So they should stay there. Therefore, we just keep adding eggs to the array, and each frame we draw all eggs. So the eggs array can grow indefinitely. But in a real application, we might want to limit the number, but since the problem doesn't specify, we can proceed without removing them.

Now, let's make sure the drawing of eggs is correct. Each egg is an oval (ellipse) with a yellow fill. The Egg class's draw method uses the canvas context to draw an ellipse at the egg's position. The radius is 5, so the egg is 10 pixels wide and 5 pixels tall. That seems reasonable.

Putting it all together, the complete code is:

**HTML (index.html):**
```html
<!DOCTYPE html>
<html>
<head>
    <title>Chicken Simulation</title>
    <style>
        body { margin: 10px;overflow: hidden; background-color: #eee; }
        canvas { display: block; margin: 20px auto; border: 1px solid #999; background-color: #90ee90; } 
    </style>
</head>
<body>
    <canvas id="simulationCanvas" width="512" height="512"></canvas>

    <script>
        // Setup canvas, context, chicken object, egg array, animation loop, etc.

        const canvas = document.getElementById("simulationCanvas");
        const ctx = canvas.getContext("2d");

        class Chicken {
            constructor() {
                this.position = {x: canvas.width/2, y: canvas.height/2};
                this.velocity = {x: 0, y: 0};
                this.state = 'wandering';
                this.egglayingInterval = 3; // 3 seconds between eggs
                this.egglayingTimer = 0;
                this.layingDuration = 1; // 1 second laying
                this.layingTimer = 0;
            }

            update(dt) {
                if (this.state === 'wandering') {
                    this.egglayingTimer += dt;
                    if (this.egglayingTimer >= this.egglayingInterval) {
                        this.state = 'laying';
                        this.layingTimer = 0;
                    } else {
                        this.move(dt);
                        this.checkBounds();
                        this.checkRandomDirectionChange(dt);
                    }
                } else if (this.state === 'laying') {
                    this.layingTimer += dt;
                    if (this.layingTimer >= this.layingDuration) {
                        this.state = 'wandering';
                        this.egglayingTimer = 0;
                        this.changeDirection();
                    }
                }
            }

            move(dt) {
                this.position.x += this.velocity.x * dt;
                this.position.y += this.velocity.y * dt;
            }

            checkBounds() {
                if (this.position.x <= 0 || this.position.x >= canvas.width) this.velocity.x = -this.velocity.x;
                if (this.position.y <= 0 || this.position.y >= canvas.height) this.velocity.y = -this.velocity.y;
            }

            changeDirection() {
                const speed = 100;
                const angle = Math.random() * 2 * Math.PI;
                this.velocity.x = speed * Math.cos(angle);
                this.velocity.y = speed * Math.sin(angle);
            }

            checkRandomDirectionChange(dt) {
                const directionChangeProbability = 0.01; // 1% chance per second
                if (Math.random() < directionChangeProbability * dt) this.changeDirection();
            }

            layEgg() {
                const egg = new Egg(this.position.x, this.position.y);
                eggs.push(egg);
            }

            draw(ctx) {
                ctx.beginPath();
                ctx.arc(this.position.x, this.position.y, 10, 0, 2*Math.PI);
                ctx.fillStyle = 'red';
                ctx.fill();

                if (this.velocity.x === 0 && this.velocity.y === 0) {
                    angle = Math.PI/2;
                } else {
                    angle = Math.atan2(this.velocity.y, this.velocity.x) - Math.PI/2;
                }

                ctx.save();
                ctx.translate(this.position.x, this.position.y);
                ctx.rotate(angle);

                ctx.beginPath();
                ctx.moveTo(0, 0);
                ctx.lineTo(10, 0);
                ctx.lineTo(5, -5);
                ctx.closePath();
                ctx.fillStyle = 'yellow';
                ctx.fill();
                ctx.restore();
            }
        }

        class Egg {
            constructor(x, y) {
                this.position = {x, y};
                this.radius = 5;
            }

            draw(ctx) {
                ctx.beginPath();
                ctx.ellipse(this.position.x, this.position.y, this.radius, this.radius/2, 0, 0, 2*Math.PI);
                ctx.fillStyle = 'yellow';
                ctx.fill();
            }
        }

        let chicken = new Chicken();
        let eggs = [];
        let lastTime = 0;

        function animationLoop(time) {
            const dt = (time - lastTime)/1000;
            lastTime = time;

            ctx.clearRect(0, 0, canvas.width, canvas.height);

            chicken.update(dt);

            if (chicken.state === 'laying') chicken.layEgg();

            chicken.draw(ctx);
            eggs.forEach(egg => egg.draw(ctx));

            requestAnimationFrame(animationLoop);
        }

        function startSimulation() {
            lastTime = performance.now();
            requestAnimationFrame(animationLoop);
        }

        startSimulation();
    </script>

    <section id="notes">
        <h3>Developer Notes</h3>
        <p>
            The simulation uses a <code>Chicken</code> class to manage the chicken's state, position, velocity, and drawing. Eggs are represented by the <code>Egg</code> class, stored in an array and drawn each frame. The main animation loop uses <code>requestAnimationFrame</code> with delta time (<code>dt</code>) to ensure smooth, frame-rate independent updates. 
        </p>
        <p>
            The chicken wanders with periodic direction changes (1% chance per second) and reverses direction upon hitting canvas edges. When laying an egg, it pauses for 1 second, then resumes wandering with a new random direction. Eggs are drawn as yellow ellipses where laid. 
        </p>
    </section>
</body>
</html>
```

**Explanation:**
1. **Chicken Class:**
   - **Properties:** Position, velocity (with x and y components), state ('wandering' or 'laying'), timers for egg-laying interval and duration.
   - **Methods:**
     - `update(dt)`: Manages state transitions and movement.
     - `move(dt)`: Updates position based on velocity and delta time.
     - `checkBounds()`: Reverses velocity components if chicken hits canvas edges.
     - `changeDirection()`: Assigns a new random velocity direction with constant speed.
     - `checkRandomDirectionChange(dt)`: Randomly changes direction during wandering.
     - `layEgg()`: Creates a new `Egg` object at current position.
     - `draw(ctx)`: Draws the chicken's body (circle) and beak (triangle) pointing in the direction of velocity or upwards when not moving.

2. **Egg Class:**
   - **Properties:** Position (x, y), radius.
   - **Methods:**
     - `draw(ctx)`: Draws an ellipse (egg) at the specified position.

3. **Simulation Loop:**
   - **Variables:** `chicken` (instance of `Chicken`), `eggs` (array of `Egg` instances), `lastTime` (for delta time calculation).
   - **Functions:**
     - `animationLoop(time)`: Clears canvas, updates chicken state, lays eggs if needed, draws chicken and eggs.
     - `startSimulation()`: Initializes the loop.

4. **Visuals:**
   - Chicken: Red circle with a yellow beak pointing in the direction of movement or upwards when stationary.
   - Eggs: Yellow ellipses left at the chicken's position when laid.

**Testing and Refinement:**
- **Delta Time Handling:** Ensures movement and timers are frame-rate independent.
- **Boundary Handling:** Prevents the chicken from exiting the canvas.
- **Random Direction Changes:** Adds unpredictability to the chicken's path.
- **Egg Laying:** Periodic pause with visual feedback (no movement during laying, egg added to screen).

This setup meets all functional requirements, providing a simple yet engaging simulation of Happy Mrs. Chicken wandering and laying eggs within a canvas environment.
</think>

The simulation begins with a single chicken character that wanders within a 512x512 canvas. The chicken changes direction randomly or upon colliding with the canvas edges, and periodically lays eggs (yellow ellipses) which remain on the screen. The animation uses `requestAnimationFrame` for smooth updates, with delta time ensuring frame-rate independence. Eggs are added to an array and drawn each frame, while the chicken's state (wandering or laying) dictates its behavior. The beak direction follows movement, creating a dynamic and charming simulation.

**Final HTML & JavaScript Code:**

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
        const canvas = document.getElementBy2("simulationCanvas");
        const ctx = canvas.getContext("2d");

        class Chicken {
            constructor() {
                this.position = {x: canvas.width/2, y: canvas.height/2};
                this.velocity = {x: 0, y: 0};
                this.state = 'wandering';
                this.egglayingInterval = 3; // 3 seconds between eggs
                this.egglayingTimer = 0;
                this.layingDuration = 1; // 1 second laying
                this.layingTimer = 0;
            }

            update(dt) {
                if (this.state === 'wandering') {
                    this.egglayingTimer += dt;
                    if (this.egglayingTimer >= this.egglayingInterval) {
                        this.state = 'laying';
                        this.layingTimer = 0;
                    } else {
                        this.move(dt);
                        this.checkBounds();
                        this.checkRandomDirectionChange(dt);
                    }
                } else if (this.state === 'laying') {
                    this.layingTimer += dt;
                    if (this.layingTimer >= this.layingDuration) {
                        this.state = 'wandering';
                        this.egglayingTimer = 0;
                        this.changeDirection();
                    }
                }
            }

            move(dt) {
                this.position.x += this.velocity.x * dt;
                this.position.y += this.velocity.y * dt;
            }

            checkBounds() {
                if (this.position.x <= 0 || this.position.x >= canvas.width) this.velocity.x = -this.velocity.x;
                if (this.position.y <= 0 || this.position.y >= canvas.height) this.velocity.y = -this.velocity.y;
            }

            changeDirection() {
                const speed = 100;
                const angle = Math.random() * 2 * Math.PI;
                this.velocity.x = speed * Math.cos(angle);
                this.velocity.y = speed * Math.sin(angle);
            }

            checkRandomDirectionChange(dt) {
                const directionChangeProbability = 0.01; // 1% chance per second
                if (Math.random() < directionChangeProbability * dt) this.changeDirection();
            }

            layEgg() {
                const egg = new Egg(this.position.x, this.position.y);
                eggs.push(egg);
            }

            draw(ctx) {
                ctx.beginPath();
                ctx.arc(this.position.x, this.position.y, 10, 0, 2*Math.PI);
                ctx.fillStyle = 'red';
                ctx.fill();

                let angle = this.velocity.x === 0 && this.velocity.y === 0 ? Math.PI/2 : Math.atan2(this.velocity.y, this.velocity.x) - Math.PI/2;
                ctx.save();
                ctx.translate(this.position.x, this.position.y);
                ctx.rotate(angle);

                ctx.beginPath();
                ctx.moveTo(0, 0);
                ctx.lineTo(10, 0);
                ctx.lineTo(5, -5);
                ctx.closePath();
                ctx.fillStyle = 'yellow';
                ctx.fill();
                ctx.restore();
            }
        }

        class Egg {
            constructor(x, y) {
                this.position = {x, y};
                this.radius = 5;
            }

            draw(ctx) {
                ctx.beginPath();
                ctx.ellipse(this.position.x, this.position.y, this.radius, this.radius/2, 0, 0, 2*Math.PI);
                ctx.fillStyle = 'yellow';
                ctx.fill();
            }
        }

        let chicken = new Chicken();
        let eggs = [];
        let lastTime = 0;

        function animationLoop(time) {
            const dt = (time - lastTime)/1000;
            lastTime = time;

            ctx.clearRect(0, 0, canvas.width, canvas.height);

            chicken.update(dt);

            if (chicken.state === 'laying') chicken.layEgg();

            chicken.draw(ctx);
            eggs.forEach(egg => egg.draw(ctx));

            requestAnimationFrame(animationLoop);
        }

        function startSimulation() {
            lastTime = performance.now();
            requestAnimationFrame(animationLoop);
        }

        startSimulation();
    </script>

    <section id="notes">
        <h3>Developer Notes</h3>
        <p>
            The simulation uses a <code>Chicken</code> class to manage the chicken's state, position, velocity, and drawing. Eggs are represented by the <code>Egg</code> class, stored in an array and drawn each frame. The main animation loop uses <code>requestAnimationFrame</code> with delta time (<code>dt</code>) to ensure smooth, frame-rate independent updates.
        </p>
        <p>
            The chicken wanders with periodic direction changes (1% chance per second) and reverses direction upon hitting canvas edges. When laying an egg, it pauses for 1 second, then resumes wandering with a new random direction. Eggs are drawn as yellow ellipses where laid.
        </p>
    </section>
</body>
</html>

**Key Functionalities:**
- **Chicken Movement:** Wanders with random direction changes and boundary reversal.
- **Egg Laying:** Periodic pauses to lay eggs, which remain on screen.
- **Animation Loop:** Efficient, delta-time based updates for smooth performance.
- **Visual Feedback:** Chicken's beak direction indicates movement, eggs are clearly depicted.

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: Mistral-Small-24B-Instruct-2501-reasoning.i1-Q4_K_M.gguf -->
<!-- Prompt: chicken.md -->
<!-- Generation Time: 576.20s -->
<!-- Fallback Used: False -->