<think>

Okay, I need to create a bouncing balls simulation using HTML, CSS, and JavaScript. The user wants at least 50 balls with gravity, damping, and collisions. Let me start by setting up the HTML structure they provided. 

First, the canvas is already in the HTML. I'll need to initialize the balls. Each ball should have position, velocity, radius, mass, and color. Maybe use an array to hold all the balls.

For the physics, gravity affects the vertical velocity. Each frame, I'll add gravity to vy. Then update positions. Wall collisions: check if each ball is touching the edges. If so, reverse velocity and apply damping. Need to correct position to prevent sticking.

Ball-to-ball collisions are tricky. The naive approach is O(n²), which might be slow for 50 balls. Maybe implement a spatial partitioning like a grid to reduce checks. Divide the canvas into cells and only check balls in nearby cells.

Wait, but how to implement the grid? Let me think. Create a grid where each cell holds references to the balls in that area. Then, for each ball, check collisions only with balls in the same or adjacent cells. That should reduce the number of pairs to check.

First, I'll write the Ball class. Properties: x, y, vx, vy, r, mass (maybe mass is proportional to radius squared?), color. The initial positions should be random but not overlapping. Hmm, maybe just random positions and check overlaps later? But that might complicate things. Maybe just start with random positions and handle overlaps in the physics loop.

The animation loop uses requestAnimationFrame. In each frame, clear the canvas, update all balls, check collisions, then draw them.

Collision response between two balls: need to calculate the direction vector between their centers, then compute the impulse. The velocities should be adjusted based on their masses and the collision normal. Alternatively, a simpler method: swap velocities or adjust based on the normal direction. Wait, the user allows an approximation. Maybe reverse the velocities along the collision axis?

Let me outline steps:

1. Initialize canvas and context.
2. Create an array of balls with random properties.
3. Set up the grid for spatial partitioning.
4. In the game loop:
   a. Clear canvas.
   b. Update each ball's velocity (add gravity).
   c. Update positions.
   d. Check wall collisions and handle them with damping.
   e. Check ball collisions using the grid.
   f. Draw all balls.

For the grid, each frame, reassign balls to their current cell. Then, for each ball, check collisions with balls in the same and neighboring cells.

Collision detection between two balls: compute distance between centers. If less than sum of radii, they collide. Then, resolve the collision by moving them apart and adjusting velocities.

Velocity adjustment for collision: maybe use the formula for elastic collisions. The formula involves the normal vector between the centers. Let me recall the equations. The relative velocity along the normal direction is used to compute the impulse. The new velocities can be calculated using:

v1' = v1 - ( ( (m1 + m2) / (m1 + m2) ) * ( (v1 - v2) · n ) * n )

Wait, maybe it's better to look up the formula. Alternatively, a simpler approach: swap velocities in the direction of the collision. Or, use the following method:

Let’s denote the two balls as A and B. The normal vector n is (xB - xA, yB - yA) normalized. The relative velocity is (vA - vB). The impulse is calculated, and then the velocities are adjusted.

Alternatively, here's a simplified approach:

var dx = ballA.x - ballB.x;
var dy = ballA.y - ballB.y;
var distance = Math.sqrt(dx*dx + dy*dy);
var sumRadii = ballA.r + ballB.r;
if (distance < sumRadii) {
    var overlap = (sumRadii - distance) / 2;
    // move them apart
    var nx = dx / distance;
    var ny = dy / distance;
    ballA.x -= nx * overlap;
    ballB.x += nx * overlap;
    ballA.y -= ny * overlap;
    ballB.y += ny * overlap;
    // adjust velocities
    var dot = (ballA.vx - ballB.vx)*nx + (ballA.vy - ballB.vy)*ny;
    var impulse = (2 * dot) / (ballA.mass + ballB.mass);
    ballA.vx -= impulse * ballB.mass * nx;
    ballA.vy -= impulse * ballB.mass * ny;
    ballB.vx += impulse * ballA.mass * nx;
    ballB.vy += impulse * ballA.mass * ny;
}

Hmm, that might work. The impulse calculation here is a simplified version. The key is to prevent overlap and adjust velocities in the direction of collision.

Now, for the grid. Let's say the grid has a cell size of, say, 100x100. The number of cells would be (canvas width / cell size) in each dimension. For each ball, determine which cell it's in and add it to that cell's list. Then, for collision detection, check all pairs in the same cell and adjacent cells.

The grid needs to be updated each frame as balls move. So, first, clear all cells, then reinsert each ball into its current cell.

Putting it all together:

First, the Ball class:

class Ball {
    constructor(x, y, vx, vy, r, color) {
        this.x = x;
        this.y = y;
        this.vx = vx;
        this.vy = vy;
        this.r = r;
        this.mass = Math.PI * r * r; // area as mass
        this.color = color;
    }
}

Then, create an array of balls. Maybe loop 50 times, generate random positions and velocities. Ensure they are within the canvas boundaries. Maybe start with radius between 5-20.

For the grid:

const gridSize = 100; // adjust based on canvas size
let grid = [];

function initGrid() {
    grid = [];
    const cols = Math.ceil(W / gridSize);
    const rows = Math.ceil(H / gridSize);
    for (let i = 0; i < cols; i++) {
        grid[i] = [];
        for (let j = 0; j < rows; j++) {
            grid[i][j] = [];
        }
    }
}

function updateGrid(balls) {
    for (let i = 0; i < grid.length; i++) {
        for (let j = 0; j < grid[i].length; j++) {
            grid[i][j].length = 0;
        }
    }
    balls.forEach(ball => {
        const col = Math.floor(ball.x / gridSize);
        const row = Math.floor(ball.y / gridSize);
        if (col >= 0 && col < grid.length && row >=0 && row < grid[col].length) {
            grid[col][row].push(ball);
        }
    });
}

But need to call updateGrid each frame before collision detection.

In the game loop:

function gameLoop(timestamp) {
    ctx.clearRect(0, 0, W, H);
    updatePhysics();
    drawBalls();
    requestAnimationFrame(gameLoop);
}

function updatePhysics() {
    // Update each ball's velocity with gravity
    balls.forEach(ball => {
        ball.vy += gravity; // gravity is a constant like 0.5
    });

    // Update positions
    balls.forEach(ball => {
        ball.x += ball.vx;
        ball.y += ball.vy;
    });

    // Handle wall collisions
    balls.forEach(ball => {
        if (ball.x - ball.r < 0) {
            ball.x = ball.r;
            ball.vx = -ball.vx * damping;
        } else if (ball.x + ball.r > W) {
            ball.x = W - ball.r;
            ball.vx = -ball.vx * damping;
        }
        if (ball.y - ball.r < 0) {
            ball.y = ball.r;
            ball.vy = -ball.vy * damping;
        } else if (ball.y + ball.r > H) {
            ball.y = H - ball.r;
            ball.vy = -ball.vy * damping;
        }
    });

    // Now handle ball collisions using grid
    updateGrid(balls);
    checkCollisions();
}

function checkCollisions() {
    for (let col = 0; col < grid.length; col++) {
        for (let row = 0; row < grid[col].length; row++) {
            const cell = grid[col][row];
            for (let i = 0; i < cell.length; i++) {
                const a = cell[i];
                // Check adjacent cells and current cell
                for (let dx = -1; dx <= 1; dx++) {
                    for (let dy = -1; dy <= 1; dy++) {
                        const neighborCol = col + dx;
                        const neighborRow = row + dy;
                        if (neighborCol >=0 && neighborCol < grid.length &&
                            neighborRow >=0 && neighborRow < grid[neighborCol].length) {
                            const neighborCell = grid[neighborCol][neighborRow];
                            for (let j = 0; j < neighborCell.length; j++) {
                                const b = neighborCell[j];
                                if (a === b) continue;
                                // Check collision between a and b
                                resolveCollision(a, b);
                            }
                        }
                    }
                }
            }
        }
    }
}

But this might still have duplicates (checking a and b twice). Maybe need to track pairs.

Alternatively, in the loop over cells, for each cell, check with its neighbors and current cell, but avoid redundant pairs.

Alternatively, to prevent checking the same pair twice, perhaps only check when i < j in the cell's list.

Wait, maybe the current approach is too slow. Maybe the grid approach is not sufficient. Alternatively, use a spatial hash or other structure. Alternatively, for now proceed with the grid and see.

The resolveCollision function would perform the collision response.

function resolveCollision(a, b) {
    const dx = a.x - b.x;
    const dy = a.y - b.y;
    const distance = Math.hypot(dx, dy);
    const sumRadii = a.r + b.r;
    if (distance < sumRadii) {
        // Calculate overlap and move them apart
        const overlap = (sumRadii - distance) / 2;
        const nx = dx / distance;
        const ny = dy / distance;
        a.x -= nx * overlap;
        a.y -= ny * overlap;
        b.x += nx * overlap;
        b.y += ny * overlap;

        // Calculate relative velocity
        const rvx = a.vx - b.vx;
        const rvy = a.vy - b.vy;
        const dot = rvx * nx + rvy * ny;

        // Impulse
        const impulse = (2 * dot) / (a.mass + b.mass);
        const im = impulse * a.mass;
        a.vx -= im * nx;
        a.vy -= im * ny;
        const imB = impulse * b.mass;
        b.vx += imB * nx;
        b.vy += imB * ny;
    }
}

Hmm, maybe that's the way. The mass is area (pi*r²). The impulse calculation here might need adjustment. Wait, the formula for elastic collision:

The standard approach is:

Let’s denote the normal vector as n (unit vector pointing from A to B).

The relative velocity along n is (vA - vB) · n.

The impulse magnitude is ( (m1 + m2) / (m1 + m2) ) * ( (vA - vB) · n ) ?

Wait, the formula for impulse in elastic collision is:

impulse = (2 * m2 * (vA - vB) · n) / (m1 + m2)

Wait, perhaps better to look up the formula. Alternatively, the standard equations for elastic collision:

v1' = v1 - (2 * m2 / (m1 + m2)) * ( (v1 - v2) · n ) * n

v2' = v2 - (2 * m1 / (m1 + m2)) * ( (v2 - v1) · n ) * n

But I might be mixing variables. Alternatively, the impulse J is calculated as:

J = (2 * m1 * m2 / (m1 + m2)) * ( (v2 - v1) · n ) / |n|² 

Wait, perhaps I should use the following approach:

The impulse is calculated as:

J = ( (vB - vA) · n ) * (m1 + m2) / (m1 + m2) ?

Hmm, maybe it's better to use a simplified version where the velocities are adjusted based on the normal direction.

Alternatively, here's a different approach:

The relative velocity along the normal direction is (vA - vB) · n.

The impulse needed to make the relative velocity zero along the normal is:

impulse = ( (vA - vB) · n ) / ( (1/m1) + (1/m2) )

Then, the velocity changes are:

deltaV_A = - (m2 / (m1 + m2)) * impulse * n

deltaV_B = (m1 / (m1 + m2)) * impulse * n

Wait, perhaps that's better. Let me recalculate.

The total momentum before collision along the normal direction is m1*(vA · n) + m2*(vB · n).

After collision, since it's elastic, the relative velocity along the normal reverses direction. So:

(vA' - vB') · n = - (vA - vB) · n 

Assuming coefficient of restitution e=1.

The impulse J along the normal direction is:

J = ( (m1 m2)/(m1 + m2) ) * ( (vB - vA) · n )

Wait, perhaps this is getting too complicated. Maybe the code I have earlier is okay for an approximation. Let's proceed with the code in resolveCollision.

Testing the code, if the balls overlap, they are pushed apart, and their velocities are adjusted based on the normal direction and masses. The damping is applied in wall collisions, but not in ball collisions. Maybe ball collisions should also have some damping? The problem says damping is applied on wall collisions, but not necessarily on ball collisions. The user specified damping for wall collisions, so perhaps ball collisions don't need damping unless specified. The problem states "apply damping (energy loss)" when wall collisions occur. So ball collisions can be elastic or with some damping, but the user didn't specify, so maybe just handle it without damping in ball collisions.

Now, putting all together:

Initialize the balls:

const numBalls = 50;
const balls = [];
const minRadius = 5;
const maxRadius = 20;
const gravity = 0.5;
const damping = 0.8; // damping factor for wall collisions

for (let i = 0; i < numBalls; i++) {
    const r = Math.random() * (maxRadius - minRadius) + minRadius;
    const x = Math.random() * (W - 2*r) + r;
    const y = Math.random() * (H - 2*r) + r;
    const vx = (Math.random() - 0.5) * 10;
    const vy = (Math.random() - 0.5) * 10;
    const color = `hsl(${Math.random() * 360}, 50%, 50%)`;
    balls.push(new Ball(x, y, vx, vy, r, color));
}

Wait, but the initial positions might overlap. Maybe not a big issue since the physics will handle it, but to prevent initial overlaps, perhaps check and adjust. But that complicates things. Maybe skip for now.

The grid needs to be initialized. Let's set gridSize to something like 100. Maybe 100 is okay for 800x600 canvas. Let's see, 800/100=8 columns, 600/100=6 rows. So grid will have 8 columns and 6 rows.

Now, in the game loop, after updating positions, handle wall collisions, then update the grid and check collisions.

Wait, the order is important. First, update velocities with gravity, then positions, then handle wall collisions (which can adjust position and velocity), then update grid, then check ball collisions.

Wait, in the physics update:

First, apply gravity to velocity.

Then, update positions.

Then, check wall collisions and adjust position and velocity (with damping).

Then, check ball collisions. Because after moving, the ball might have moved into another ball, so need to handle that.

Yes.

But in the code above, after updating positions, the wall collision code adjusts the position again. So the grid needs to be updated after that.

Hmm, so the sequence is:

- Update velocities (gravity)
- Update positions
- Apply wall collisions (adjust position and velocity)
- Update grid (based on new positions)
- Check ball collisions

Yes, that makes sense.

Now, implementing the grid:

The grid is a 2D array. Each cell contains a list of balls in that cell.

The updateGrid function loops through all balls and places them into their current cell.

In checkCollisions, for each cell, we check the current cell and adjacent cells for collisions between balls. This reduces the number of pairs to check from 50*50=2500 to maybe a few hundred.

Now, the draw function:

function drawBalls() {
    balls.forEach(ball => {
        ctx.beginPath();
        ctx.arc(ball.x, ball.y, ball.r, 0, Math.PI*2);
        ctx.fillStyle = ball.color;
        ctx.fill();
        ctx.closePath();
    });
}

Okay, putting all together in the HTML.

Wait, in the initial code skeleton, the gameLoop is commented out. Need to uncomment and start it.

Also, need to initialize the grid before starting the loop.

Wait, let me structure the code step by step.

First, the Ball class.

Then, variables:

const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const W = canvas.width;
const H = canvas.height;

// Physics constants
const gravity = 0.5;
const damping = 0.8;
const gridSize = 100;

// Grid setup
let grid = [];

// Initialize grid
function initGrid() {
    grid = [];
    const cols = Math.ceil(W / gridSize);
    const rows = Math.ceil(H / gridSize);
    for (let i = 0; i < cols; i++) {
        grid[i] = [];
        for (let j = 0; j < rows; j++) {
            grid[i][j] = [];
        }
    }
}

// Initialize balls
const numBalls = 50;
const balls = [];
const minRadius = 5;
const maxRadius = 20;

function initBalls() {
    for (let i = 0; i < numBalls; i++) {
        const r = Math.random() * (maxRadius - minRadius) + minRadius;
        const x = Math.random() * (W - 2*r) + r;
        const y = Math.random() * (H - 2*r) + r;
        const vx = (Math.random() - 0.5) * 10;
        const vy = (Math.random() - 0.5) * 10;
        const color = `hsl(${Math.random() * 360}, 50%, 50%)`;
        balls.push(new Ball(x, y, vx, vy, r, color));
    }
}

// Update grid function
function updateGrid() {
    for (let i = 0; i < grid.length; i++) {
        for (let j = 0; j < grid[i].length; j++) {
            grid[i][j].length = 0;
        }
    }
    balls.forEach(ball => {
        const col = Math.floor(ball.x / gridSize);
        const row = Math.floor(ball.y / gridSize);
        if (col >= 0 && col < grid.length && row >= 0 && row < grid[col].length) {
            grid[col][row].push(ball);
        }
    });
}

// Collision resolution
function resolveCollision(a, b) {
    const dx = a.x - b.x;
    const dy = a.y - b.y;
    const distance = Math.hypot(dx, dy);
    const sumRadii = a.r + b.r;
    if (distance < sumRadii) {
        const overlap = (sumRadii - distance) / 2;
        const nx = dx / distance;
        const ny = dy / distance;
        a.x -= nx * overlap;
        a.y -= ny * overlap;
        b.x += nx * overlap;
        b.y += ny * overlap;

        // Calculate relative velocity
        const rvx = a.vx - b.vx;
        const rvy = a.vy - b.vy;
        const dot = rvx * nx + rvy * ny;

        // Impulse calculation
        const im = (2 * dot) / (a.mass + b.mass);
        a.vx -= im * b.mass * nx;
        a.vy -= im * b.mass * ny;
        b.vx += im * a.mass * nx;
        b.vy += im * a.mass * ny;
    }
}

// Check collisions using grid
function checkCollisions() {
    for (let col = 0; col < grid.length; col++) {
        for (let row = 0; row < grid[col].length; row++) {
            const currentCell = grid[col][row];
            for (let dx = -1; dx <= 1; dx++) {
                for (let dy = -1; dy <= 1; dy++) {
                    const neighborCol = col + dx;
                    const neighborRow = row + dy;
                    if (neighborCol >= 0 && neighborCol < grid.length && 
                        neighborRow >= 0 && neighborRow < grid[neighborCol].length) {
                        const neighborCell = grid[neighborCol][neighborRow];
                        for (let i = 0; i < currentCell.length; i++) {
                            const a = currentCell[i];
                            for (let j = 0; j < neighborCell.length; j++) {
                                const b = neighborCell[j];
                                if (a !== b) {
                                    resolveCollision(a, b);
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

// Update physics
function updatePhysics() {
    // Apply gravity
    balls.forEach(ball => {
        ball.vy += gravity;
    });

    // Update positions
    balls.forEach(ball => {
        ball.x += ball.vx;
        ball.y += ball.vy;
    });

    // Wall collisions
    balls.forEach(ball => {
        // Left wall
        if (ball.x - ball.r < 0) {
            ball.x = ball.r;
            ball.vx = -ball.vx * damping;
        }
        // Right wall
        else if (ball.x + ball.r > W) {
            ball.x = W - ball.r;
            ball.vx = -ball.vx * damping;
        }
        // Top wall
        if (ball.y - ball.r < 0) {
            ball.y = ball.r;
            ball.vy = -ball.vy * damping;
        }
        // Bottom wall
        else if (ball.y + ball.r > H) {
            ball.y = H - ball.r;
            ball.vy = -ball.vy * damping;
        }
    });

    // Update grid after position changes
    updateGrid();

    // Check ball collisions
    checkCollisions();
}

// Draw function
function draw() {
    ctx.clearRect(0, 0, W, H);
    balls.forEach(ball => {
        ctx.beginPath();
        ctx.arc(ball.x, ball.y, ball.r, 0, Math.PI * 2);
        ctx.fillStyle = ball.color;
        ctx.fill();
        ctx.closePath();
    });
}

// Game loop
function gameLoop() {
    updatePhysics();
    draw();
    requestAnimationFrame(gameLoop);
}

// Initialization
initGrid();
initBalls();
requestAnimationFrame(gameLoop);

Wait, but in the code above, the updateGrid is called after wall collisions, which is correct. Then checkCollisions uses the updated grid.

Wait, but the checkCollisions function is called after updating the grid. Yes.

Hmm, I think this should work. Let me check for possible errors.

In the Ball class, the mass is set as Math.PI * r * r. Maybe that's okay, but perhaps using a constant mass (like 1) would be simpler. Let me see if the collision code uses mass correctly. The resolveCollision function uses mass in the impulse calculation. If the mass is radius squared, then larger balls have more mass and thus affect the collision differently. That's okay.

Testing the code in the browser, but since I can't run it now, I'll proceed.

Potential issues:

1. The grid's cell size might be too large or small. If the cell is too large, it might include too many balls, making the collision check not much better. Maybe adjust the grid size based on the canvas dimensions. Alternatively, set it to 50 for better partitioning.

2. The resolveCollision function might have a mistake in the impulse calculation. Let me recheck:

The impulse im is (2 * dot) / (a.mass + b.mass). Then:

a's velocity change is im * b.mass * nx?

Wait, let me re-derive the formula.

The relative velocity along the normal direction is (vA - vB) · n. Let's call this v_rel.

The impulse J is calculated as:

J = ( (vB - vA) · n ) * (m1 + m2) / (m1 + m2) ?

Hmm, perhaps the correct formula is:

The impulse magnitude is:

J = ( (vB - vA) · n ) * (m1 * m2) / (m1 + m2)

Then, the change in velocity for A is (J / m1) * n, and for B is (-J / m2) * n.

Wait, perhaps I need to re-calculate.

Let me denote:

vA = velocity of ball A before collision

vB = velocity of ball B before collision

n is the unit normal vector pointing from A to B.

The relative velocity along the normal is (vB - vA) · n. Wait, no, (vA - vB) · n is the component of (vA - vB) along n. So the relative velocity towards each other is (vA - vB) · n.

Wait, to have an elastic collision, the relative velocity after collision along the normal should be the negative of before.

The impulse J is applied to both balls along the normal direction.

The impulse on A is J * n, and on B is -J * n.

The change in velocity for A: (J / m_A) * n

For B: (-J / m_B) * n

The total change in relative velocity along n should be:

( (vA + (J/m_A)*n ) - (vB - (J/m_B)*n ) ) · n 

= (vA - vB) · n + (J/m_A + J/m_B) * (n · n)

= (vA - vB) · n + J ( (1/m_A + 1/m_B) ) 

We want this to be equal to - (vA - vB) · n 

So:

(vA - vB) · n + J ( (1/m_A + 1/m_B) ) = - (vA - vB) · n 

=> J ( (1/m_A + 1/m_B) ) = -2 (vA - vB) · n 

=> J = -2 (vA - vB) · n / (1/m_A + 1/m_B )

= 2 (vB - vA) · n / ( (m_A + m_B)/(m_A m_B) ) )

= 2 m_A m_B (vB - vA) · n / (m_A + m_B )

Thus, J = (2 m_A m_B / (m_A + m_B)) * ( (vB - vA) · n )

Then, the change in velocity for A is (J/m_A) * n = (2 m_B / (m_A + m_B)) * ( (vB - vA) · n ) * n 

Similarly for B:

( -J/m_B ) * n = ( -2 m_A / (m_A + m_B) ) * ( (vB - vA) · n ) * n 

Wait, so the correct formula is:

delta_vA = (2 * m_B / (m_A + m_B)) * ( (vB - vA) · n ) * n 

delta_vB = (2 * m_A / (m_A + m_B)) * ( (vB - vA) · n ) * (-n )

Wait, perhaps I made a mistake in the direction. Let me recheck:

The impulse J is applied to A in direction n, so delta_vA = J / m_A * n 

J is equal to 2 m_A m_B ( (vB - vA) · n ) / (m_A + m_B )

So delta_vA = (2 m_B (vB - vA) · n / (m_A + m_B )) * n 

Similarly, delta_vB = (-J)/m_B * n 

= - (2 m_A (vB - vA) · n / (m_A + m_B )) * n 

Thus, combining:

delta_vA = (2 m_B / (m_A + m_B )) * ( (vB - vA) · n ) * n 

delta_vB = (2 m_A / (m_A + m_B )) * ( (vA - vB) · n ) * n 

Wait, this is getting complicated, but the key point is that the code's current approach might not be accurate.

In the current code's resolveCollision function:

im = (2 * dot) / (a.mass + b.mass)

Then:

a.vx -= im * b.mass * nx;

Wait, let's see:

dot = (a.vx - b.vx)*nx + (a.vy - b.vy)*ny = (vA - vB) · n 

So im = 2 * dot / (m1 + m2)

Then, delta_vA is im * (b.mass) * nx ?

Wait, if delta_vA is (2 * m_B / (m_A + m_B )) * ( (vB - vA) · n ) * n 

Then, (vB - vA) · n = - (vA - vB) · n = -dot 

Thus, delta_vA = (2 m_B / (m_A + m_B )) * (-dot) * n 

So delta_vA.x = (2 m_B / (m_A + m_B )) * (-dot) * nx 

Similarly for y component.

Thus, the code's current approach:

a.vx -= im * b.mass * nx 

im is 2*dot/(m1+m2), so:

delta_vA.x = - im * b.mass * nx 

= - (2 dot / (m1 + m2)) * b.mass * nx 

But according to the formula, it should be ( -2 m_B dot / (m_A + m_B )) * nx 

Which matches the code's approach. Because m_B is b.mass.

Yes, so:

delta_vA.x = - (2 * dot / (m_A + m_B )) * b.mass * nx 

Wait, no:

Wait, the code has:

im = (2 * dot) / (a.mass + b.mass)

then:

a.vx -= im * b.mass * nx 

So delta_vA.x = - im * b.mass * nx 

= - (2 dot / (m_A + m_B )) * b.mass * nx 

Which is the same as:

- (2 * b.mass / (m_A + m_B )) * dot * nx 

But according to the formula, delta_vA.x is:

(2 * m_B / (m_A + m_B )) * (-dot) * nx 

= - (2 m_B / (m_A + m_B )) * dot * nx 

Which matches the code's result. Thus the code is correct.

Therefore, the code's impulse calculation is correct.

Another possible error is the direction of the normal vector. In the code:

dx = a.x - b.x 

so the normal vector points from b to a. Wait, no: dx is a.x - b.x, so if a is to the right of b, dx is positive, so the normal vector points towards a from b. But the direction of the normal vector should be from a to b? Or from b to a?

Wait, in the code:

dx = a.x - b.x 

so the vector from b to a is (dx, dy). The normal vector n is (dx, dy) normalized. So it points from b to a. 

Thus, the normal vector is pointing from b to a. So when resolving the collision, the overlap is moved in the direction of n (from b to a), so a moves back, and b moves forward. That's correct.

Thus, the code should work.

Now, testing performance. With 50 balls, the grid approach should reduce the number of collision checks. Let's see:

Each ball is in a cell. For each cell, we check adjacent cells (up to 9 cells around). For each ball in the current cell, check against all balls in the neighboring cells. 

The total number of pairs would be roughly (number of cells) * (number of balls per cell)^2 * 9. If the grid partitions the balls evenly, this could be manageable.

Another optimization could be to avoid checking the same pair twice. For example, when checking cell (i,j) and cell (i+1,j), the pairs between them are checked twice. To avoid this, perhaps only check in one direction, but that's more complex.

Alternatively, the current code may have some redundant checks but it's acceptable for the problem's requirements.

Now, putting all the code into the HTML skeleton.

Wait, in the Ball class, the constructor should be inside the script.

Also, the initial grid needs to be initialized before starting the game loop.

So, the complete HTML would be:

<!DOCTYPE html>
<html>
<head>
    <title>Bouncing Balls</title>
    <style>
        body { margin: 0; overflow: hidden; background-color: #f0f0f0; }
        canvas { border: 1px solid black; background-color: #fff; display: block; margin: 20px auto; }
    </style>
</head>
<body>
    <canvas id="gameCanvas" width="800" height="600"></canvas>
    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const W = canvas.width;
        const H = canvas.height;

        class Ball {
            constructor(x, y, vx, vy, r, color) {
                this.x = x;
                this.y = y;
                this.vx = vx;
                this.vy = vy;
                this.r = r;
                this.mass = Math.PI * r * r; // Mass proportional to area
                this.color = color;
            }
        }

        // Physics constants
        const gravity = 0.5;
        const damping = 0.8;
        const gridSize = 100; // Adjust based on canvas size

        let grid = [];
        const balls = [];
        const numBalls = 50;
        const minRadius = 5;
        const maxRadius = 20;

        // Initialize grid
        function initGrid() {
            grid = [];
            const cols = Math.ceil(W / gridSize);
            const rows = Math.ceil(H / gridSize);
            for (let i = 0; i < cols; i++) {
                grid[i] = [];
                for (let j = 0; j < rows; j++) {
                    grid[i][j] = [];
                }
            }
        }

        // Initialize balls
        function initBalls() {
            for (let i = 0; i < numBalls; i++) {
                const r = Math.random() * (maxRadius - minRadius) + minRadius;
                const x = Math.random() * (W - 2 * r) + r;
                const y = Math.random() * (H - 2 * r) + r;
                const vx = (Math.random() - 0.5) * 10;
                const vy = (Math.random() - 0.5) * 10;
                const color = `hsl(${Math.random() * 360}, 50%, 50%)`;
                balls.push(new Ball(x, y, vx, vy, r, color));
            }
        }

        // Update grid with current ball positions
        function updateGrid() {
            for (let i = 0; i < grid.length; i++) {
                for (let j = 0; j < grid[i].length; j++) {
                    grid[i][j].length = 0;
                }
            }
            balls.forEach(ball => {
                const col = Math.floor(ball.x / gridSize);
                const row = Math.floor(ball.y / gridSize);
                if (col >= 0 && col < grid.length && row >= 0 && row < grid[col].length) {
                    grid[col][row].push(ball);
                }
            });
        }

        // Resolve collision between two balls
        function resolveCollision(a, b) {
            const dx = a.x - b.x;
            const dy = a.y - b.y;
            const distance = Math.hypot(dx, dy);
            const sumRadii = a.r + b.r;
            if (distance < sumRadii) {
                const overlap = (sumRadii - distance) / 2;
                const nx = dx / distance;
                const ny = dy / distance;
                // Move balls apart
                a.x -= nx * overlap;
                a.y -= ny * overlap;
                b.x += nx * overlap;
                b.y += ny * overlap;

                // Calculate relative velocity components
                const rvx = a.vx - b.vx;
                const rvy = a.vy - b.vy;
                const dot = rvx * nx + rvy * ny;

                // Calculate impulse
                const im = (2 * dot) / (a.mass + b.mass);
                // Update velocities
                a.vx -= im * b.mass * nx;
                a.vy -= im * b.mass * ny;
                b.vx += im * a.mass * nx;
                b.vy += im * a.mass * ny;
            }
        }

        // Check all ball collisions using grid
        function checkCollisions() {
            for (let col = 0; col < grid.length; col++) {
                for (let row = 0; row < grid[col].length; row++) {
                    const currentCell = grid[col][row];
                    for (let dx = -1; dx <= 1; dx++) {
                        for (let dy = -1; dy <= 1; dy++) {
                            const neighborCol = col + dx;
                            const neighborRow = row + dy;
                            if (neighborCol >= 0 && neighborCol < grid.length &&
                                neighborRow >= 0 && neighborRow < grid[neighborCol].length) {
                                const neighborCell = grid[neighborCol][neighborRow];
                                for (let i = 0; i < currentCell.length; i++) {
                                    const a = currentCell[i];
                                    for (let j = 0; j < neighborCell.length; j++) {
                                        const b = neighborCell[j];
                                        if (a !== b) {
                                            resolveCollision(a, b);
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

        // Update physics state
        function updatePhysics() {
            // Apply gravity
            balls.forEach(ball => {
                ball.vy += gravity;
            });

            // Update positions
            balls.forEach(ball => {
                ball.x += ball.vx;
                ball.y += ball.vy;
            });

            // Handle wall collisions with damping
            balls.forEach(ball => {
                // Left wall
                if (ball.x - ball.r < 0) {
                    ball.x = ball.r;
                    ball.vx = -ball.vx * damping;
                }
                // Right wall
                else if (ball.x + ball.r > W) {
                    ball.x = W - ball.r;
                    ball.vx = -ball.vx * damping;
                }
                // Top wall
                if (ball.y - ball.r < 0) {
                    ball.y = ball.r;
                    ball.vy = -ball.vy * damping;
                }
                // Bottom wall
                else if (ball.y + ball.r > H) {
                    ball.y = H - ball.r;
                    ball.vy = -ball.vy * damping;
                }
            });

            // Update grid after position changes
 <!-- 1200.10s -->