<think>
Okay, I need to create a bouncing balls simulation using HTML Canvas and JavaScript. Let's start by understanding the requirements. The goal is to have at least 30 balls, each with properties like position, velocity, radius, mass, and color. They should interact with each other and the walls under gravity, and lose energy on collisions.

First, the HTML setup is provided, so I'll use that. The canvas is 800x600. I need to create a Ball class or object. Each ball should have x, y, vx, vy, r, mass, color. Maybe radius can be random, and color too. Mass could be proportional to radius squared, but maybe for simplicity, just use radius squared as mass.

Next, initialization. I need to create 50+ balls. Random positions within the canvas. But need to avoid initial overlaps. Hmm, how? Maybe generate positions and check if they are too close to existing balls. But with 50 balls, that might be time-consuming. Alternatively, just generate random positions and if there's an overlap, adjust. But maybe for the initial setup, just random positions and live with some overlaps. The problem says initial non-overlap isn't the primary focus.

Then the animation loop. Use requestAnimationFrame. In each frame, clear the canvas, apply gravity, update positions, handle collisions with walls and other balls, then redraw.

Physics steps:

1. Apply gravity: each ball's vy increases by gravityValue each frame. Let's pick a gravity value, maybe 0.1 or something.

2. Update positions: x += vx, y += vy.

3. Wall collisions. For each ball, check if it's outside the canvas considering the radius. For example, if x - r < 0, then it hits the left wall. Similarly for right (x + r > W), top (y - r < 0), bottom (y + r > H). When a collision occurs, reverse the velocity component (vx or vy), multiply by damping factor (like 0.8). Also, correct the position so the ball is exactly at the boundary. For example, if x - r < 0, set x = r.

4. Ball-to-ball collisions. Need to check all pairs. For each pair, calculate distance between centers. If distance <= r1 + r2, then they collide. Then need to handle the collision response.

Collision response: The standard approach for elastic collision in 2D involves calculating the impulse based on the collision normal. But since the problem says a plausible response is acceptable, maybe a simpler approach. One common method is to compute the relative velocity, and then adjust the velocities so that they bounce off each other. However, considering masses is important. Alternatively, for simplicity, when two balls collide, swap their velocities. But that might not be accurate. Alternatively, calculate the new velocities based on conservation of momentum and kinetic energy.

But for the sake of time and simplicity, perhaps use the following approach:

When two balls A and B collide:

- Compute the collision normal vector (the direction from A to B, normalized)
- Project the relative velocity onto this normal to find the component that's causing the collision.
- Then, calculate the new velocities based on the masses and the impulse.

Alternatively, use the formula for elastic collision in one dimension. Since the collision is along the line connecting the centers, we can treat the component of velocity along that line.

The formula for elastic collision between two objects along a line:

v1_new = ((m1 - m2)/(m1 + m2)) * v1 + (2*m2/(m1 + m2)) * v2

v2_new = (2*m1/(m1 + m2)) * v1 + ((m2 - m1)/(m1 + m2)) * v2

But since this is 2D, we need to apply this to the components along the collision normal.

So steps for a collision between A and B:

1. Compute the vector from A to B: dx = B.x - A.x, dy = B.y - A.y
2. The distance between centers is d = sqrt(dx^2 + dy^2)
3. If d > A.r + B.r, no collision. But since we are checking in the detection phase, we already know d <= sum of radii.
4. The collision normal is (dx/d, dy/d) → unit vector.
5. Compute the relative velocity between A and B: v_rel = (A.vx - B.vx, A.vy - B.vy)
6. The component of this relative velocity along the normal (dot product of v_rel and normal) is the part that's causing the collision.
7. If the relative velocity along the normal is positive (i.e., they are moving towards each other), then we need to resolve the collision.
8. Calculate the impulse J using the formula for elastic collision. The coefficient of restitution (e) is 1 for perfectly elastic, but since we have damping, maybe use the damping factor here. Wait, but the damping is already applied to wall collisions. For ball-ball collisions, maybe use a different damping factor, or same. The problem says to apply damping (energy loss) upon collision. So perhaps in the ball-ball collision, after calculating the new velocities, multiply by the damping factor.

Alternatively, during the collision response, after computing the new velocities, apply the damping. Or maybe the damping is applied during the collision response.

Alternatively, the damping could be applied as part of the collision response. For example, after calculating the new velocities, multiply each component by the damping factor. But the problem says that upon collision, they lose energy. So damping applies to both wall and ball collisions.

Wait, the problem says:

"For wall collision:

- Reverse the appropriate velocity component.

- Apply damping by reducing the magnitude by dampingFactor.

For ball-ball collision:

- Implement a plausible collision response.

But the problem also says that in the response, must prevent overlapping and have balls react. So perhaps the damping can be applied in the ball-ball collision as well. For example, after computing the new velocities, multiply by dampingFactor.

But how to handle that. Maybe the damping is applied in the collision response step. Alternatively, maybe the damping is applied during the velocity updates, but the problem says that damping is applied upon collision.

So for wall collisions, after reversing the velocity component, multiply by dampingFactor. For ball-ball collisions, during the response, also apply damping. But how?

Alternatively, during the collision response, after calculating the new velocities, multiply each component by dampingFactor. Or perhaps the damping is applied to the relative velocity.

This part might be a bit tricky. Let me think.

The standard approach for elastic collision (without damping) would be to calculate the new velocities as per the conservation laws. Then, to add energy loss, we can multiply the relative velocity by a restitution factor (e), which is the damping factor here. So in the collision response, after computing the new velocities, we can apply the damping.

But perhaps the simplest way is to use the following approach:

When two balls collide:

1. Compute the collision normal (unit vector from A to B)
2. Compute the relative velocity along the normal (v_rel)
3. If v_rel > 0 (they are approaching), then compute the new velocities.

The formula for the change in velocity can be found here: https://www.geeksforgeeks.org/elastic-collision-two-dimensions/

But since we need to account for mass and restitution (damping), here's a possible approach:

Let’s denote:

m1, m2: masses of the two balls

v1, v2: velocity vectors

e: coefficient of restitution (damping factor, between 0 and 1)

The steps:

a. Compute the unit vector n from A to B (collision normal)

b. Compute the relative velocity along the normal: v_rel = (v1 - v2) · n

c. If v_rel > 0, then they are moving apart and no collision (but since we detected collision, this might not be the case. Wait, maybe the collision is detected when the distance is less than sum of radii, which could happen even if they are moving apart. So perhaps we should check if the relative velocity is such that they are approaching. But for simplicity, maybe proceed regardless.)

d. The impulse J is calculated as J = (1 + e) * (v_rel) / ( (m1 + m2)/(m1*m2) + ... ) Wait, perhaps better to use the formula from the link.

Alternatively, here's a method:

The change in velocity for each ball is given by:

v1_new = v1 + ( (1 + e) * (v2 - v1) · n ) / ( (m1 + m2)/(m1*m2) ) * m2 * n ?

Alternatively, the formula for the impulse J is:

J = (1 + e) * ( (v1 - v2) · n ) / ( (n · n) * (m1 + m2) ) → but n is a unit vector, so n · n = 1.

Wait, perhaps the correct formula is:

The impulse J is given by:

J = (1 + e) * (v_rel) / ( (m1 + m2) / (m1 * m2) ) → not sure.

Alternatively, from the elastic collision equations:

The relative velocity after collision is -e times the relative velocity before collision.

So, v_rel_after = -e * v_rel_before

The impulse J can be calculated as:

J = (1 + e) * m1 * m2 * v_rel / (m1 + m2)

But I'm getting stuck here. Maybe a better approach is to look up the standard code for 2D elastic collision.

Upon checking, here's a common approach:

Compute the relative velocity and the normal.

Then:

let v1n = v1 · n

let v2n = v2 · n

let e = 0.8 // damping factor

let j = (1 + e) * (v1n - v2n) / ( (m1 + m2) / (m1 * m2) )

Then, update the velocities:

v1 = v1 - (j * m2 / m1) * n

v2 = v2 + (j * m1 / m2) * n

Wait, perhaps this is the way.

Alternatively, here's a code snippet from a physics example:

function resolveCollision(ball1, ball2) {

    let dx = ball2.x - ball1.x;

    let dy = ball2.y - ball1.y;

    let distance = Math.sqrt(dx*dx + dy*dy);

    if (distance > ball1.radius + ball2.radius) return;

    // Normalize

    let normalX = dx / distance;

    let normalY = dy / distance;

    // Relative velocity

    let velocity1X = ball1.vx;

    let velocity1Y = ball1.vy;

    let velocity2X = ball2.vx;

    let velocity2Y = ball2.vy;

    let relativeVelocityX = velocity1X - velocity2X;

    let relativeVelocityY = velocity1Y - velocity2Y;

    // Dot product of relative velocity and normal

    let relativeVelocityDotNormal = relativeVelocityX * normalX + relativeVelocityY * normalY;

    // If they are moving apart, no collision

    if (relativeVelocityDotNormal > 0) return;

    // Compute the impulse

    let e = 0.8; // restitution coefficient

    let j = (1 + e) * relativeVelocityDotNormal / ( (ball1.mass + ball2.mass) / (ball1.mass * ball2.mass) )

    // Or maybe j = (1 + e) * (relativeVelocityDotNormal) * (m1 * m2) / (m1 + m2) ?

    // Then update the velocities

    ball1.vx -= (j * ball2.mass / ball1.mass) * normalX;

    ball1.vy -= (j * ball2.mass / ball1.mass) * normalY;

    ball2.vx += (j * ball1.mass / ball2.mass) * normalX;

    ball2.vy += (j * ball1.mass / ball2.mass) * normalY;

    // Also, separate the balls to prevent overlapping

    let overlap = (ball1.radius + ball2.radius) - distance;

    let minimumSeparation = distance - overlap;

    // Push them apart along the normal direction

    let push = (ball1.radius + ball2.radius - distance) / 2;

    ball1.x -= normalX * push;

    ball1.y -= normalY * push;

    ball2.x += normalX * push;

    ball2.y += normalY * push;

}

Wait, but this might be a bit involved. Also, the separation part is important to prevent the balls from overlapping after collision.

Alternatively, during collision detection, if the balls are overlapping, we need to adjust their positions so that they are just touching. This is called position correction.

But doing this during the simulation can be tricky. So perhaps, after detecting a collision, we first adjust their positions to eliminate the overlap, then apply the velocity changes.

But how to calculate the push? The push is (sum of radii - distance)/2, so that each ball is moved half the overlap distance along the normal.

But this might not be perfect, but it's a common approach.

So, putting this together, the steps for a ball-ball collision are:

1. Check if the distance between centers is less than sum of radii.

2. If so, compute the normal vector (from A to B, normalized).

3. Compute the relative velocity along the normal. If it's positive (they are moving apart), skip.

4. Otherwise, calculate the impulse J based on the masses and restitution.

5. Update the velocities of both balls based on J and the normal.

6. Then, adjust their positions to eliminate overlap.

Now, regarding damping: in this case, the restitution coefficient e (like 0.8) would act as the damping factor. So when e is less than 1, energy is lost. So this would handle the energy loss for ball-ball collisions.

But the problem states that both wall and ball collisions should have damping. So for wall collisions, we reverse the velocity component and multiply by dampingFactor. For ball collisions, the damping is handled via the restitution coefficient.

So perhaps using e=0.8 in the collision response would handle that.

Now, the problem is that checking all pairs is O(n^2), which for 50 balls is 50*49/2=1225 checks per frame. That's manageable, but for 100 balls it would be 4950, which could be slow. So the problem suggests using spatial partitioning like grids or quadtrees. But implementing a grid for collision detection might be time-consuming. However, the problem says that for 50+ balls, we need to implement optimization. So perhaps I should implement a grid-based spatial partitioning.

But how?

The idea is to divide the canvas into a grid of cells. For each frame, each ball is assigned to a cell (or cells) based on its position. Then, when checking for collisions, each ball only checks against other balls in the same or adjacent cells. This reduces the number of checks.

But implementing this requires:

- Creating a grid structure.

- For each ball, determine which cell it belongs to.

- For each frame, update the grid.

But this can add some complexity. However, given that the problem requires optimization for 50+ balls, it's better to implement this.

Alternatively, if the number of balls is 50, the O(n^2) approach might still be manageable. Let's see: 50 balls → 1225 checks per frame. If each check is a few operations, that's acceptable. But if the number is higher, say 100, it's 4950 checks. But for now, perhaps proceed with the naive approach first, then see if performance is acceptable. But the problem says to implement optimization techniques. So perhaps I should try to implement a grid.

Let me think about how to do that.

The grid can be a 2D array of cells. Each cell is a list of balls that are in that cell.

The grid size can be determined based on the average ball size. For example, if the balls have a maximum radius of, say, 20, then each cell could be 40x40 pixels. Then, for any two balls that are in the same cell or adjacent cells, check for collision.

But how to determine which cell a ball belongs to. For each ball, compute cellX = Math.floor(x / cellSize), cellY = Math.floor(y / cellSize). Then, the ball is in cell (cellX, cellY). Then, for collision detection, each ball checks against all other balls in the same cell and adjacent cells (including diagonally adjacent? Or just same and adjacent in x and y?).

But this requires for each frame, building the grid. Steps:

1. Clear the grid.

2. For each ball, determine its cell and add it to the cell's list.

3. For each ball, check collisions with other balls in the same cell and adjacent cells.

This reduces the number of checks.

But implementing this requires some code. Let's outline:

- Define cellSize. Maybe set it to the maximum possible radius of balls plus some buffer. Let's say cellSize is 40.

- Create a grid as a 2D array. The number of cells in x and y directions would be W / cellSize and H / cellSize.

But in code:

const cellSize = 40;

const grid = [];

for (let i = 0; i < Math.ceil(W / cellSize); i++) {

    grid[i] = [];

    for (let j = 0; j < Math.ceil(H / cellSize); j++) {

        grid[i][j] = [];

    }

}

Then, for each ball, compute cellX = Math.floor(ball.x / cellSize), cellY = Math.floor(ball.y / cellSize). Then add the ball to grid[cellX][cellY].

But during the simulation, for each frame, we need to rebuild the grid. So:

function buildGrid() {

    // Clear the grid

    for (let i = 0; i < grid.length; i++) {

        for (let j = 0; j < grid[i].length; j++) {

            grid[i][j] = [];

        }

    }

    // Assign balls to cells

    for (let ball of balls) {

        const cellX = Math.floor(ball.x / cellSize);

        const cellY = Math.floor(ball.y / cellSize);

        if (cellX >= 0 && cellY >= 0 && cellX < grid.length && cellY < grid[0].length) {

            grid[cellX][cellY].push(ball);

        }

    }

}

Then, for each ball, check against other balls in the same cell and adjacent cells.

But how to avoid checking the same pair twice. For example, ball A in cell (i,j) checks ball B in cell (i,j), but then ball B would also check ball A. To avoid redundant checks, we can check each pair only once. For example, when processing a ball, check against all other balls in the same cell and adjacent cells that have not been checked yet. Alternatively, during the grid building, for each cell, check all pairs within that cell and adjacent cells, but need to make sure not to check the same pair twice.

Alternatively, during the collision detection phase:

For each ball in the grid, check against all other balls in the same cell and adjacent cells, but only if the other ball's index is higher than the current ball's index. But that's not straightforward.

Alternatively, during the grid processing, for each cell, check all pairs in that cell. Then, for each cell, check adjacent cells (but that could lead to duplicates). This is getting complicated. Maybe for the sake of time, proceed with the naive approach for now, and see if performance is acceptable. But the problem requires optimization. Hmm.

Alternatively, perhaps the number of balls is manageable with the naive approach. Let's try with 50 balls. If it's too slow, then implement the grid. But given that the problem requires it, I should implement the grid.

So, let's proceed with the grid-based approach.

Another thing to consider: when building the grid, each ball can be in multiple cells if it's near the edge. Wait no, the cell is determined by the ball's position. Each ball is in exactly one cell. Because cellX and cellY are computed based on the ball's x and y.

So, each ball is in one cell. Then, for collision detection, each ball checks against other balls in the same cell and adjacent cells. But adjacent cells would include all eight surrounding cells. However, this may still lead to checking some pairs multiple times. For example, a ball in cell (i,j) checks a ball in cell (i+1,j), and then when processing the ball in (i+1,j), it checks the first ball again. To avoid this, perhaps during the collision detection, we can check each pair only once. One way is to process the balls in order and only check pairs where the other ball has a higher index. But that's not possible with the grid approach.

Alternatively, during the grid processing, for each cell, check all pairs in that cell. Then, for each cell, check against the cells to the right and below (to avoid checking the same pair twice). For example, cell (i,j) checks with cell (i+1,j), (i,j+1), (i+1,j+1), etc. But this can get complicated.

Alternatively, during the collision detection, for each ball, check against all other balls in the same cell and adjacent cells. Even if this leads to checking some pairs twice, it's acceptable for the sake of correctness, and the optimization is still better than O(n^2). Because each ball only checks a small number of neighbors.

So, in code:

For each ball in the balls array:

   Get its cell (cellX, cellY)

   For each adjacent cell (including same cell):

      For each otherBall in that cell:

          if otherBall is not the same as ball and not already checked:

              check collision between ball and otherBall

But how to track which pairs have been checked. Alternatively, during the grid processing, each pair is checked twice (once for each ball). But in practice, it's manageable.

But perhaps for the purposes of this simulation, even with checking pairs twice, the grid approach reduces the number of checks enough. So proceed.

So steps for collision detection:

1. Build the grid.

2. For each ball:

   a. Find its cell.

   b. Check against all other balls in the same cell and adjacent cells.

   c. For each such otherBall, if ball's index < otherBall's index (to check once per pair), then check collision.

Wait, but in the grid, the same pair may be in adjacent cells. So perhaps during the grid processing, for each ball, we check all other balls in the same cell and adjacent cells, but only if the otherBall's index is higher than the current ball's index. But how to track the index. Alternatively, during the initial loop through all balls, for each ball, check all other balls that come after it in the array. But that's the naive approach. Hmm.

Alternatively, during the grid-based approach, each ball checks all other balls in the same cell and adjacent cells, regardless of their position. But this could check the same pair multiple times. For example, ball A in cell (i,j) checks ball B in cell (i,j), and then ball B in cell (i,j) checks ball A in cell (i,j). To avoid this, perhaps during the collision detection, we can check each pair only once. For example, when processing ball A, check all other balls in the grid cells, but only if the otherBall's index is higher than A's index. But how to do that with the grid?

Alternatively, perhaps it's easier to proceed with the naive approach for now and see. If the performance is acceptable, then proceed. Otherwise, implement the grid.

But the problem says that the preferred feature is to implement optimization techniques. So perhaps the grid is needed.

Alternatively, another optimization is to use a spatial hash. For example, each ball's position is hashed into a cell, and during collision detection, each ball checks against others in the same cell. This would reduce the number of checks.

But let's proceed with implementing the grid.

Now, putting this all together.

First, create the Ball class.

class Ball {

    constructor(x, y, vx, vy, r, mass, color) {

        this.x = x;

        this.y = y;

        this.vx = vx;

        this.vy = vy;

        this.r = r;

        this.mass = mass; // mass can be proportional to r^2, or just set to r^2 * density

        this.color = color;

    }

}

But for mass, since the problem says mass can be proportional to radius squared, let's compute it as r^2.

Now, initialization: create 50 balls.

const balls = [];

function initBalls() {

    for (let i = 0; i < 50; i++) {

        let r = Math.random() * 10 + 5; // radius between 5 and 15

        let mass = r * r; // assuming density is 1

        let x = Math.random() * (W - 2*r) + r;

        let y = Math.random() * (H - 2*r) + r;

        // Check for overlaps with existing balls. But for now, skip this step.

        let vx = (Math.random() - 0.5) * 2; // between -1 and 1

        let vy = (Math.random() - 0.5) * 2;

        let color = '#' + Math.floor(Math.random()*16777215).toString(16);

        balls.push(new Ball(x, y, vx, vy, r, mass, color));

    }

}

But this may lead to initial overlaps. The problem says that initial overlaps are not the primary focus, so perhaps it's acceptable.

Now, the animation loop.

The gameLoop function is called via requestAnimationFrame.

In each frame:

- Clear the canvas.

- Apply gravity to each ball (vy += gravity).

- Update positions.

- Handle wall collisions.

- Handle ball collisions.

- Draw the balls.

Now, the code structure.

First, define constants:

const gravity = 0.1;

const damping = 0.8; // for wall collisions

const restitution = 0.8; // for ball collisions (damping)

Now, the gameLoop function.

function gameLoop(timestamp) {

    ctx.clearRect(0, 0, W, H);

    // Apply gravity and update positions

    for (let ball of balls) {

        ball.vy += gravity;

        ball.x += ball.vx;

        ball.y += ball.vy;

    }

    // Handle wall collisions

    for (let ball of balls) {

        // Left and right walls

        if (ball.x - ball.r < 0 || ball.x + ball.r > W) {

            ball.vx = -ball.vx * damping;

            // Correct position

            if (ball.x - ball.r < 0) {

                ball.x = ball.r;

            } else {

                ball.x = W - ball.r;

            }

        }

        // Top and bottom walls

        if (ball.y - ball.r < 0 || ball.y + ball.r > H) {

            ball.vy = -ball.vy * damping;

            if (ball.y - ball.r < 0) {

                ball.y = ball.r;

            } else {

                ball.y = H - ball.r;

            }

        }

    }

    // Handle ball collisions

    // Build grid for spatial partitioning

    // ... code to build grid ...

    // Then check collisions between balls

    // For now, using naive approach

    for (let i = 0; i < balls.length; i++) {

        for (let j = i + 1; j < balls.length; j++) {

            let ball1 = balls[i];

            let ball2 = balls[j];

            let dx = ball2.x - ball1.x;

            let dy = ball2.y - ball1.y;

            let distance = Math.sqrt(dx*dx + dy*dy);

            if (distance <= ball1.r + ball2.r) {

                // Collision detected

                resolveCollision(ball1, ball2);

            }

        }

    }

    // Draw balls

    for (let ball of balls) {

        ctx.beginPath();

        ctx.arc(ball.x, ball.y, ball.r, 0, Math.PI*2);

        ctx.fillStyle = ball.color;

        ctx.fill();

    }

    requestAnimationFrame(gameLoop);

}

But the resolveCollision function needs to be implemented.

Now, the resolveCollision function.

function resolveCollision(ball1, ball2) {

    // Compute normal vector (from ball1 to ball2)

    let dx = ball2.x - ball1.x;

    let dy = ball2.y - ball1.y;

    let distance = Math.sqrt(dx*dx + dy*dy);

    if (distance == 0) {

        // Avoid division by zero

        // Just separate them randomly

        ball1.x += Math.random() - 0.5;

        ball1.y += Math.random() - 0.5;

        ball2.x -= Math.random() - 0.5;

        ball2.y -= Math.random() - 0.5;

        return;

    }

    let normalX = dx / distance;

    let normalY = dy / distance;

    // Relative velocity

    let v1x = ball1.vx;

    let v1y = ball1.vy;

    let v2x = ball2.vx;

    let v2y = ball2.vy;

    let relativeVelocityX = v1x - v2x;

    let relativeVelocityY = v1y - v2y;

    // Dot product of relative velocity and normal

    let relativeVelocityDotNormal = relativeVelocityX * normalX + relativeVelocityY * normalY;

    // If they are moving apart, no collision

    if (relativeVelocityDotNormal > 0) {

        return;

    }

    // Compute the impulse

    let e = restitution; // 0.8

    let m1 = ball1.mass;

    let m2 = ball2.mass;

    // The formula for the impulse J

    // From https://www.geeksforgeeks.org/elastic-collision-two-dimensions/

    // The relative velocity along the normal

    let v1n = v1x * normalX + v1y * normalY;

    let v2n = v2x * normalX + v2y * normalY;

    let v1n_new = ((m1 - m2) * v1n + 2 * m2 * v2n) / (m1 + m2);

    let v2n_new = (2 * m1 * v1n + (m2 - m1) * v2n) / (m1 + m2);

    // But this is for elastic collision. To add restitution:

    v1n_new = v2n - e * (v1n - v2n);

    v2n_new = v1n - e * (v2n - v1n);

    // Then, compute the new velocities

    // The component of velocity along the normal is updated, the tangential component remains the same.

    // So:

    // v1_new = v1 - (v1n - v1n_new) * normal

    // Similarly for v2.

    let v1tangentialX = v1x - v1n * normalX;

    let v1tangentialY = v1y - v1n * normalY;

    let v2tangentialX = v2x - v2n * normalX;

    let v2tangentialY = v2y - v2n * normalY;

    ball1.vx = v1tangentialX + v1n_new * normalX;

    ball1.vy = v1tangentialY + v1n_new * normalY;

    ball2.vx = v2tangentialX + v2n_new * normalX;

    ball2.vy = v2tangentialY + v2n_new * normalY;

    // Now, adjust positions to prevent overlap

    let overlap = (ball1.r + ball2.r) - distance;

    ball1.x += normalX * overlap / 2;

    ball1.y += normalY * overlap / 2;

    ball2.x -= normalX * overlap / 2;

    ball2.y -= normalY * overlap / 2;

}

Wait, but this is a bit complex. Another approach is to use the formula from the resolve collision function in the article.

The article says:

// Relative velocity

float relativeVelocityX = ball1.VelocityX - ball2.VelocityX;

float relativeVelocityY = ball1.VelocityY - ball2.VelocityY;

// Normal

float normalX = (ball2.X - ball1.X) / distance;

float normalY = (ball2.Y - ball1.Y) / distance;

// Calculate the relative velocity along the normal

float relativeVelocityNormal = relativeVelocityX * normalX + relativeVelocityY * normalY;

// If the relative velocity is positive, they are moving apart

if (relativeVelocityNormal > 0) {

    return;

}

// Calculate the impulse

float e = 0.8; // restitution

float m1 = ball1.Mass;

float m2 = ball2.Mass;

float j = (1 + e) * relativeVelocityNormal;

j = j / (m1 + m2);

// Apply the impulse

ball1.VelocityX += j * m2 * normalX;

ball1.VelocityY += j * m2 * normalY;

ball2.VelocityX -= j * m1 * normalX;

ball2.VelocityY -= j * m1 * normalY;

// Adjust positions to prevent overlap

float overlap = (ball1.Radius + ball2.Radius) - distance;

ball1.X += normalX * overlap / 2;

ball1.Y += normalY * overlap / 2;

ball2.X -= normalX * overlap / 2;

ball2.Y -= normalY * overlap / 2;

This approach seems simpler and is based on the conservation of momentum.

So, implementing this:

function resolveCollision(ball1, ball2) {

    let dx = ball2.x - ball1.x;

    let dy = ball2.y - ball1.y;

    let distance = Math.sqrt(dx*dx + dy*dy);

    if (distance == 0) {

        // Handle as before

        ball1.x += Math.random() - 0.5;

        ball1.y += Math.random() - 0.5;

        ball2.x -= Math.random() - 0.5;

        ball2.y -= Math.random() - 0.5;

        return;

    }

    let normalX = dx / distance;

    let normalY = dy / distance;

    let relativeVelocityX = ball1.vx - ball2.vx;

    let relativeVelocityY = ball1.vy - ball2.vy;

    let relativeVelocityNormal = relativeVelocityX * normalX + relativeVelocityY * normalY;

    if (relativeVelocityNormal > 0) {

        return;

    }

    let e = restitution;

    let m1 = ball1.mass;

    let m2 = ball2.mass;

    let j = (1 + e) * relativeVelocityNormal;

    j = j / (m1 + m2);

    // Apply impulse

    ball1.vx += j * m2 * normalX;

    ball1.vy += j * m2 * normalY;

    ball2.vx -= j * m1 * normalX;

    ball2.vy -= j * m1 * normalY;

    // Adjust positions

    let overlap = (ball1.r + ball2.r) - distance;

    ball1.x += normalX * overlap / 2;

    ball1.y += normalY * overlap / 2;

    ball2.x -= normalX * overlap / 2;

    ball2.y -= normalY * overlap / 2;

}

This seems more straightforward.

Now, testing this code.

But there's a problem with the position adjustment. If the balls are overlapping, moving them apart along the normal by half the overlap each. But this may not be sufficient if the overlap is large. However, in practice, with small time steps, this should work.

Now, putting all together.

But in the code above, the grid-based collision detection is not implemented. Instead, the naive approach is used. To implement the grid, we need to modify the collision detection part.

Let's outline the grid-based approach.

First, define cellSize.

const cellSize = 40;

Then, during the gameLoop:

function gameLoop(timestamp) {

    ctx.clearRect(0, 0, W, H);

    // Apply gravity and update positions

    for (let ball of balls) {

        ball.vy += gravity;

        ball.x += ball.vx;

        ball.y += ball.vy;

    }

    // Handle wall collisions

    for (let ball of balls) {

        // Left and right walls

        if (ball.x - ball.r < 0 || ball.x + ball.r > W) {

            ball.vx = -ball.vx * damping;

            // Correct position

            if (ball.x - ball.r < 0) {

                ball.x = ball.r;

            } else {

                ball.x = W - ball.r;

            }

        }

        // Top and bottom walls

        if (ball.y - ball.r < 0 || ball.y + ball.r > H) {

            ball.vy = -ball.vy * damping;

            if (ball.y - ball.r < 0) {

                ball.y = ball.r;

            } else {

                ball.y = H - ball.r;

            }

        }

    }

    // Build grid

    const grid = {};

    const cellSize = 40;

    for (let ball of balls) {

        const cellX = Math.floor(ball.x / cellSize);

        const cellY = Math.floor(ball.y / cellSize);

        if (!grid[cellX]) grid[cellX] = {};

        if (!grid[cellX][cellY]) grid[cellX][cellY] = [];

        grid[cellX][cellY].push(ball);

    }

    // Handle ball collisions using grid

    for (let cellX in grid) {

        for (let cellY in grid[cellX]) {

            let currentCell = grid[cellX][cellY];

            for (let i = 0; i < currentCell.length; i++) {

                let ball1 = currentCell[i];

                // Check against other balls in this cell

                for (let j = i + 1; j < currentCell.length; j++) {

                    let ball2 = currentCell[j];

                    resolveCollision(ball1, ball2);

                }

                // Check against adjacent cells

                for (let dx = -1; dx <= 1; dx++) {

                    for (let dy = -1; dy <= 1; dy++) {

                        if (dx === 0 && dy === 0) continue;

                        let adjCellX = cellX + dx;

                        let adjCellY = cellY + dy;

                        if (!grid[adjCellX] || !grid[adjCellX][adjCellY]) continue;

                        let adjCell = grid[adjCellX][adjCellY];

                        for (let k = 0; k < adjCell.length; k++) {

                            let ball2 = adjCell[k];

                            // Avoid checking the same pair twice

                            // For example, if ball1 is in cell (i,j) and ball2 is in cell (i+1,j), then when processing cell (i+1,j), ball2 would check ball1 again. To avoid this, we can check if ball1's index < ball2's index. But since we're using a grid, it's not straightforward.

                            // For now, proceed without checking, which may lead to duplicate checks.

                            resolveCollision(ball1, ball2);

                        }

                    }

                }

            }

        }

    }

    // Draw balls

    for (let ball of balls) {

        ctx.beginPath();

        ctx.arc(ball.x, ball.y, ball.r, 0, Math.PI*2);

        ctx.fillStyle = ball.color;

        ctx.fill();

    }

    requestAnimationFrame(gameLoop);

}

But this code has several issues:

1. The grid is built inside the gameLoop, which can be memory-intensive. It's better to reuse a grid structure.

2. The grid is built using a plain object, which may not be efficient.

3. The code checks for collisions between ball1 and ball2 multiple times, leading to redundant resolveCollision calls.

To address this, perhaps during the grid processing, each pair is checked only once. For example, when processing cell (i,j), check against cells (i+1,j), (i,j+1), (i+1,j+1), etc., but this can get complicated.

Alternatively, during the grid processing, for each ball in a cell, check against all other balls in the same cell and adjacent cells, but only if the other ball's index is higher than the current ball's index. But how to track the index.

Alternatively, during the grid building, assign each ball a unique ID, and during collision detection, only check pairs where ball1.id < ball2.id. But this requires additional code.

Given time constraints, perhaps proceed with the naive approach for now and see if performance is acceptable. If not, then implement the grid.

But the problem requires optimization, so perhaps proceed with the grid.

Another approach is to build a list of pairs to check. For each ball, check against other balls in the same cell and adjacent cells. But to avoid checking the same pair twice, during the grid processing, for each ball, check against other balls in the same cell and adjacent cells that have a higher index in the balls array. But how to do that.

Alternatively, during the grid processing, for each ball, check against all other balls in the same cell and adjacent cells, and if the other ball has a higher index than the current ball, then resolveCollision. But this requires knowing the index of each ball in the balls array.

Modify the Ball class to include an index:

class Ball {

    constructor(x, y, vx, vy, r, mass, color, index) {

        this.x = x;

        this.y = y;

        this.vx = vx;

        this.vy = vy;

        this.r = r;

        this.mass = mass;

        this.color = color;

        this.index = index;

    }

}

Then, during initialization:

for (let i = 0; i < 50; i++) {

    let r = Math.random() * 10 + 5;

    let mass = r * r;

    let x = Math.random() * (W - 2*r) + r;

    let y = Math.random() * (H - 2*r) + r;

    let vx = (Math.random() - 0.5) * 2;

    let vy = (Math.random() - 0.5) * 2;

    let color = '#' + Math.floor(Math.random()*16777215).toString(16);

    balls.push(new Ball(x, y, vx, vy, r, mass, color, i));

}

Then, during collision detection using the grid:

for (let cellX in grid) {

    for (let cellY in grid[cellX]) {

        let currentCell = grid[cellX][cellY];

        for (let i = 0; i < currentCell.length; i++) {

            let ball1 = currentCell[i];

            // Check against other balls in this cell

            for (let j = i + 1; j < currentCell.length; j++) {

                let ball2 = currentCell[j];

                if (ball1.index < ball2.index) {

                    resolveCollision(ball1, ball2);

                }

            }

            // Check against adjacent cells

            for (let dx = -1; dx <= 1; dx++) {

                for (let dy = -1; dy <= 1; dy++) {

                    if (dx === 0 && dy === 0) continue;

                    let adjCellX = cellX + dx;

                    let adjCellY = cellY + dy;

                    if (!grid[adjCellX] || !grid[adjCellX][adjCellY]) continue;

                    let adjCell = grid[adjCellX][adjCellY];

                    for (let k = 0; k < adjCell.length; k++) {

                        let ball2 = adjCell[k];

                        if (ball1.index < ball2.index) {

                            resolveCollision(ball1, ball2);

                        }

                    }

                }

            }

        }

    }

}

This way, each pair is checked only once, where ball1.index < ball2.index.

This should reduce the number of checks.

Now, putting this all together.

But building the grid inside the gameLoop may be time-consuming. Perhaps pre-allocate the grid.

But for now, proceed.

Now, testing the code.

Potential issues:

1. The grid is built using an object, which may not be efficient. Using a 2D array may be better.

But for simplicity, proceed.

Another issue: the grid is built every frame, which can be slow for large grids. But with W and H being the canvas size, and cellSize=40, the number of cells is manageable.

Now, the final code.

But given the complexity, perhaps the code should be written step by step.

First, define the constants and classes.

Then, the initBalls function.

Then, the gameLoop function with grid-based collision detection.

Now, writing the code.

But given the time, perhaps proceed with the naive collision detection first, then add the grid if needed.

But the problem requires optimization, so proceed with the grid.

Final code:

// Constants

const W = canvas.width;

const H = canvas.height;

const gravity = 0.1;

const damping = 0.8;

const restitution = 0.8;

const cellSize = 40;

// Ball class

class Ball {

    constructor(x, y, vx, vy, r, mass, color, index) {

        this.x = x;

        this.y = y;

        this.vx = vx;

        this.vy = vy;

        this.r = r;

        this.mass = mass;

        this.color = color;

        this.index = index;

    }

}

// Balls array

const balls = [];

// Initialize balls

function initBalls() {

    for (let i = 0; i < 50; i++) {

        let r = Math.random() * 10 + 5;

        let mass = r * r;

        let x = Math.random() * (W - 2*r) + r;

        let y = Math.random() * (H - 2*r) + r;

        let vx = (Math.random() - 0.5) * 2;

        let vy = (Math.random() - 0.5) * 2;

        let color = '#' + Math.floor(Math.random()*16777215).toString(16);

        balls.push(new Ball(x, y, vx, vy, r, mass, color, i));

    }

}

// Resolve collision function

function resolveCollision(ball1, ball2) {

    let dx = ball2.x - ball1.x;

    let dy = ball2.y - ball1.y;

    let distance = Math.sqrt(dx*dx + dy*dy);

    if (distance == 0) {

        // Handle as before

        ball1.x += Math.random() - 0.5;

        ball1.y += Math.random() - 0.5;

        ball2.x -= Math.random() - 0.5;

        ball2.y -= Math.random() - 0.5;

        return;

    }

    let normalX = dx / distance;

    let normalY = dy / distance;

    let relativeVelocityX = ball1.vx - ball2.vx;

    let relativeVelocityY = ball1.vy - ball2.vy;

    let relativeVelocityNormal = relativeVelocityX * normalX + relativeVelocityY * normalY;

    if (relativeVelocityNormal > 0) {

        return;

    }

    let e = restitution;

    let m1 = ball1.mass;

    let m2 = ball2.mass;

    let j = (1 + e) * relativeVelocityNormal;

    j = j / (m1 + m2);

    // Apply impulse

    ball1.vx += j * m2 * normalX;

    ball1.vy += j * m2 * normalY;

    ball2.vx -= j * m1 * normalX;

    ball2.vy -= j * m1 * normalY;

    // Adjust positions

    let overlap = (ball1.r + ball2.r) - distance;

    ball1.x += normalX * overlap / 2;

    ball1.y += normalY * overlap / 2;

    ball2.x -= normalX * overlap / 2;

    ball2.y -= normalY * overlap / 2;

}

// Game loop

function gameLoop(timestamp) {

    ctx.clearRect(0, 0, W, H);

    // Apply gravity and update positions

    for (let ball of balls) {

        ball.vy += gravity;

        ball.x += ball.vx;

        ball.y += ball.vy;

    }

    // Handle wall collisions

    for (let ball of balls) {

        // Left and right walls

        if (ball.x - ball.r < 0 || ball.x + ball.r > W) {

            ball.vx = -ball.vx * damping;

            // Correct position

            if (ball.x - ball.r < 0) {

                ball.x = ball.r;

            } else {

                ball.x = W - ball.r;

            }

        }

        // Top and bottom walls

        if (ball.y - ball.r < 0 || ball.y + ball.r > H) {

            ball.vy = -ball.vy * damping;

            if (ball.y - ball.r < 0) {

                ball.y = ball.r;

            } else {

                ball.y = H - ball.r;

            }

        }

    }

    // Build grid

    let grid = {};

    for (let ball of balls) {

        let cellX = Math.floor(ball.x / cellSize);

        let cellY = Math.floor(ball.y / cellSize);

        if (!grid[cellX]) grid[cellX] = {};

        if (!grid[cellX][cellY]) grid[cellX][cellY] = [];

        grid[cellX][cellY].push(ball);

    }

    // Handle ball collisions using grid

    for (let cellX in grid) {

        for (let cellY in grid[cellX]) {

            let currentCell = grid[cellX][cellY];

            for (let i = 0; i < currentCell.length; i++) {

                let ball1 = currentCell[i];

                // Check against other balls in this cell

                for (let j = i + 1; j < currentCell.length; j++) {

                    let ball2 = currentCell[j];

                    if (ball1.index < ball2.index) {

                        resolveCollision(ball1, ball2);

                    }

                }

                // Check against adjacent cells

                for (let dx = -1; dx <= 1; dx++) {

                    for (let dy = -1; dy <= 1; dy++) {

                        if (dx === 0 && dy === 0) continue;

                        let adjCellX = cellX + dx;

                        let adjCellY = cellY + dy;

                        if (!grid[adjCellX] || !grid[adjCellX][adjCellY]) continue;

                        let adjCell = grid[adjCellX][adjCellY];

                        for (let k = 0; k < adjCell.length; k++) {

                            let ball2 = adjCell[k];

                            if (ball1.index < ball2.index) {

                                resolveCollision(ball1, ball2);

                            }

                        }

                    }

                }

            }

        }

    }

    // Draw balls

    for (let ball of balls) {

        ctx.beginPath();

        ctx.arc(ball.x, ball.y, ball.r, 0, Math.PI*2);

        ctx.fillStyle = ball.color;

        ctx.fill();

    }

    requestAnimationFrame(gameLoop);

}

// Initialize and start

initBalls();

gameLoop();

This code should handle the collisions using a grid-based approach, reducing the number of checks.

Potential issues:

1. The grid is built using a plain object, which may not be the most efficient.

2. The code may have performance issues if the number of balls is large.

3. The position correction may not be perfect, leading to overlapping balls in some cases.

But overall, this should work for demonstration purposes.

Now, the final answer is the code provided above.
</think>
To implement a physics simulation with collisions between balls, we need to handle motion, collision detection, and response. Here's a structured approach using a grid-based collision detection for efficiency.

### Step-by-Step Explanation

1. **Constants and Setup**:
   - Define constants like gravity, damping (for wall collisions), restitution (for elasticity of collisions), and cell size for grid-based collision detection.
   - Set up the canvas dimensions.

2. **Ball Class**:
   - Create a `Ball` class to encapsulate properties like position, velocity, radius, mass, color, and an index for tracking.

3. **Initialization**:
   - Initialize an array of balls with random positions, velocities, and colors.

4. **Collision Response**:
   - Implement a `resolveCollision` function that handles the physics of collisions between two balls:
     - Calculate the normal vector between the balls.
     - Determine the relative velocity along the normal.
     - Apply impulses to both balls based on their masses and the restitution coefficient.
     - Adjust positions to prevent overlapping.

5. **Game Loop**:
   - Update ball positions based on gravity and velocity.
   - Handle wall collisions by reversing velocity and adjusting positions.
   - Use a grid to efficiently detect potential collisions between balls:
     - Each ball is placed into a grid cell based on its position.
     - For each ball, check for collisions only with other balls in the same or adjacent grid cells, ensuring each pair is checked only once.

6. **Rendering**:
   - Draw each ball on the canvas.

### Complete Code

```javascript
const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

const W = canvas.width;
const H = canvas.height;
const gravity = 0.1;
const damping = 0.8;
const restitution = 0.8;
const cellSize = 40;

class Ball {
    constructor(x, y, vx, vy, r, mass, color, index) {
        this.x = x;
        this.y = y;
        this.vx = vx;
        this.vy = vy;
        this.r = r;
        this.mass = mass;
        this.color = color;
        this.index = index;
    }
}

const balls = [];

function initBalls() {
    for (let i = 0; i < 50; i++) {
        let r = Math.random() * 10 + 5;
        let mass = r * r;
        let x = Math.random() * (W - 2 * r) + r;
        let y = Math.random() * (H - 2 * r) + r;
        let vx = (Math.random() - 0.5) * 2;
        let vy = (Math.random() - 0.5) * 2;
        let color = '#' + Math.floor(Math.random() * 16777215).toString(16);
        balls.push(new Ball(x, y, vx, vy, r, mass, color, i));
    }
}

function resolveCollision(ball1, ball2) {
    let dx = ball2.x - ball1.x;
    let dy = ball2.y - ball1.y;
    let distance = Math.sqrt(dx * dx + dy * dy);

    if (distance === 0) {
        ball1.x += Math.random() - 0.5;
        ball1.y += Math.random() - 0.5;
        ball2.x -= Math.random() - 0.5;
        ball2.y -= Math.random() - 0.5;
        return;
    }

    let normalX = dx / distance;
    let normalY = dy / distance;

    let relativeVelocityX = ball1.vx - ball2.vx;
    let relativeVelocityY = ball1.vy - ball2.vy;
    let relativeVelocityNormal = relativeVelocityX * normalX + relativeVelocityY * normalY;

    if (relativeVelocityNormal > 0) {
        return;
    }

    let e = restitution;
    let m1 = ball1.mass;
    let m2 = ball2.mass;
    let j = (1 + e) * relativeVelocityNormal;
    j = j / (m1 + m2);

    ball1.vx += j * m2 * normalX;
    ball1.vy += j * m2 * normalY;
    ball2.vx -= j * m1 * normalX;
    ball2.vy -= j * m1 * normalY;

    let overlap = (ball1.r + ball2.r) - distance;
    ball1.x += normalX * overlap / 2;
    ball1.y += normalY * overlap / 2;
    ball2.x -= normalX * overlap / 2;
    ball2.y -= normalY * overlap / 2;
}

function gameLoop() {
    ctx.clearRect(0, 0, W, H);

    for (let ball of balls) {
        ball.vy += gravity;
        ball.x += ball.vx;
        ball.y += ball

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: Nemotron-Super-49B-v1_5-IQ4_XS.gguf -->
<!-- Prompt: ball_bound.md -->
<!-- Generation Time: 553.45s -->
<!-- Fallback Used: False -->