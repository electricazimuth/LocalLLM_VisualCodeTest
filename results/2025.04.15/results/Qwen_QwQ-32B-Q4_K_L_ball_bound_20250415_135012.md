<think>

Okay, I need to create a bouncing balls simulation using HTML, CSS, and JavaScript. Let's start by understanding the requirements. The user wants a square container on a canvas with at least 30 balls that bounce off each other and the walls. The balls should have gravity and damping, and I need to handle collisions between them efficiently.

First, I'll look at the provided HTML boilerplate. The canvas is set to 800x600, so I'll make sure the container is the same size. The CSS is already set up, so I don't need to change that much except maybe the background colors to make the balls stand out.

Next, the JavaScript part. The main structure is there with the canvas and context. I need to create a Ball class or object to represent each ball. Each ball needs position (x, y), velocity (vx, vy), radius, mass, and color. The mass could be proportional to the radius squared, but maybe for simplicity, I'll set it as a constant for now. Wait, the user says mass can be proportional to radius squared or constant. Let me decide. Maybe using radius squared would be better for realistic physics, but might complicate calculations. Hmm, maybe start with a constant mass for simplicity, but I can note that in the code.

The initialization: I need to create 50+ balls. Each should have random positions within the canvas, but not overlapping initially. To prevent overlaps, I can generate a position and check against existing balls. But that might be time-consuming for 50 balls. Alternatively, just generate random positions and hope for the least overlap. The user says perfect initial non-overlap isn't required, so maybe it's okay. Let's proceed with that.

The animation loop uses requestAnimationFrame. The loop should clear the canvas, update each ball's position, apply gravity, check for collisions with walls and other balls, then redraw.

Gravity: Each frame, add gravity to the vertical velocity (vy). So, in the update step, for each ball, vy += gravity. Then, update x and y based on vx and vy.

Wall collisions: For each ball, check if it's touching the left/right walls (x - r < 0 or x + r > W) or top/bottom (y - r < 0 or y + r > H). When a collision is detected, reverse the velocity component (vx or vy) and apply damping. Also, adjust the position so it's just touching the wall to prevent going through.

Ball-to-ball collisions: This is the tricky part. The naive approach is O(n^2), which is slow for 50 balls. The user mentioned using spatial partitioning like grids. Let's think: divide the canvas into a grid. Each cell contains a list of balls. Then, for each ball, check collisions only with balls in the same or adjacent cells. That reduces the number of pairs to check.

Implementing a grid: Let's say the grid has cells of size, say, 100x100. Each frame, for each ball, determine which cell it's in and add it to that cell's list. Then, for each cell, check collisions between all pairs in that cell and adjacent cells. But how to manage this efficiently?

Alternatively, for each ball, check against all balls in the same grid cell and neighboring cells. To implement this, first, create a grid array. The grid size can be determined based on the canvas size. Let's say gridWidth = 20, gridHeight = 15 (for 800x600, each cell is 40x40). Wait, 800/20 is 40, 600/15 is 40. So each cell is 40x40. That might be a good start.

So steps for collision detection between balls:

1. Create a grid structure (array of arrays) where each cell holds a list of balls in that cell.
2. For each ball, determine its current cell based on its position.
3. Add the ball to the grid's cell list.
4. For each ball, check collisions with other balls in the same cell and adjacent cells (up to 8 surrounding cells). This reduces the number of pairs to check.

But how to handle this efficiently? Maybe after updating all positions, first build the grid, then iterate through each ball and check against other balls in the same and neighboring cells.

Wait, perhaps it's better to:

- For each ball, check all other balls in the grid cells that are within a certain range. But the exact implementation needs to be thought through.

Alternatively, here's an approach:

- Create a grid array where each cell is an array of balls.
- For each ball, compute its grid cell (xCell = Math.floor(ball.x / cellSize), yCell similarly).
- Add the ball to the grid's cell.
- Then, for each ball, check collisions with all balls in the same cell and adjacent cells (including diagonally adjacent cells).
- To avoid checking the same pair twice, perhaps only check against balls with a higher index.

But this might still be O(n^2) in the worst case if all balls are in the same cell. Hmm. Maybe the grid approach can help in reducing the number of pairs.

Alternatively, maybe just proceed with the O(n^2) approach for now, and see if it's manageable with 50 balls. Let's see: 50 balls would have 50*49/2 = 1225 pairs. That might be okay for a canvas, but maybe with more balls, it's better optimized. But the user wants at least 30, so maybe 50 is manageable with some optimizations.

Wait, the user specified to implement optimization strategies. So I need to do the grid approach.

Let me outline the steps for the grid:

Initialize grid:

- Determine grid size. Let's say cellSize is 40 (so 800/40=20 cells in width, 600/40=15 in height).

Then, for each ball in each frame:

1. Clear the grid.
2. For each ball, compute their current cell (xCell = Math.floor((ball.x + ball.r) / cellSize), but maybe better to compute based on the center. Wait, the position is the center, so the cell can be calculated as:

xCell = Math.floor((ball.x - ball.r) / cellSize); no, better to use the center:

xCell = Math.floor( (ball.x) / cellSize );
yCell = Math.floor( (ball.y) / cellSize );

But the cell size is fixed, so each cell is cellSize x cellSize.

Wait, actually, the ball's position is the center. To determine which cell it's in, divide the x and y by cellSize and take the floor.

Once the grid is built, for each ball, check collisions with all balls in the same cell and adjacent cells.

Wait, but how to loop through adjacent cells? For each cell around the current cell's coordinates, check those cells.

Alternatively, for a given ball, iterate through the current cell and the 8 surrounding cells, and for each ball in those cells, check collision.

But to avoid redundant checks, perhaps only check balls with a higher index? Not sure.

Alternatively, for each ball, check all balls in the current cell and adjacent cells, but skip the same ball.

But this could be computationally intensive. Let's proceed step by step.

Implementing the grid:

First, in the update loop, after updating all positions, but before checking collisions:

- Create a grid array (2D array of arrays).
- Iterate over all balls, compute their cell, and add them to the grid's cell array.

Then, for each ball, check collisions with all balls in the same cell and adjacent cells.

Wait, but how to loop through adjacent cells? Let's see:

For the current ball's cell (xCell, yCell), we need to check all cells in the 3x3 grid around it (including itself). So for dx from -1 to 1, and dy from -1 to 1.

But need to check if the cell is within the grid's boundaries.

So for each cell (xCell + dx, yCell + dy), if within grid, then check all balls in that cell.

For each of those balls, check if it's the same ball (index) or not. If not, check collision between the two.

Wait, but this way, each pair is checked twice (once from each ball's perspective). To avoid that, perhaps only check balls with a higher index, but that complicates.

Alternatively, just proceed with checking all pairs, but it's okay since the grid reduces the number of pairs.

Alternatively, when checking the current ball, only check balls that are in the list after the current ball's position? Not sure.

Alternatively, for each ball A, check all balls B in the nearby cells where B comes after A in the list. That way, each pair is checked only once. But the order in the list may not be sorted by cell, so this might not work.

Hmm, perhaps it's better to just proceed with checking all balls in the nearby cells and allow checking pairs twice, but the grid reduces the total number of pairs.

So the steps for collision between balls:

Loop through each ball in the array:

for (let i = 0; i < balls.length; i++) {

   let ballA = balls[i];

   // Get the cell of ballA

   let xCellA = Math.floor(ballA.x / cellSize);

   let yCellA = Math.floor(ballA.y / cellSize);

   // Now, loop through the 3x3 grid around this cell

   for (let dx = -1; dx <= 1; dx++) {

      for (let dy = -1; dy <= 1; dy++) {

         let x = xCellA + dx;

         let y = yCellA + dy;

         // Check if cell is within grid bounds

         if (x >=0 && x < gridWidth && y >=0 && y < gridHeight) {

             let cellBalls = grid[y][x]; // assuming grid is [y][x] or [x][y]?

             // Assuming grid is grid[x][y] or perhaps grid is a 2D array where grid[x][y] is the list.

             // Need to be consistent with how grid is built.

             // For example, if grid is built as grid[x][y], then yes.

             // Wait, grid is built as grid[x][y] or grid[y][x]? Let me think.

             // Suppose grid is an array of rows. Let's say grid is an array where grid[y][x] is the list.

             // Or perhaps grid is a 2D array where grid[x][y] is the list. Need to decide.

             // To avoid confusion, perhaps grid is a 2D array where grid[x][y] is the list.

             // So when building the grid:

             let xCell = Math.floor( ball.x / cellSize );

             let yCell = Math.floor( ball.y / cellSize );

             grid[xCell][yCell].push( ball );

             So in the loop above, for a given xCellA and yCellA, the cell to check is grid[x + dx][y + dy] ?

             Wait, no. The current cell is (xCellA, yCellA), so adding dx and dy to xCellA and yCellA gives the neighboring cells. So:

             let targetX = xCellA + dx;

             let targetY = yCellA + dy;

             So the cell is grid[targetX][targetY].

             So if grid is a 2D array where grid[x][y] is the list, then yes.

             So in code:

             let cellBalls = grid[targetX][targetY];

             Then, for each ball in cellBalls:

             for (let j =0; j < cellBalls.length; j++) {

                 let ballB = cellBalls[j];

                 if (ballB === ballA) continue;

                 // Check collision between A and B

                 // compute distance between centers

                 let dx = ballA.x - ballB.x;

                 let dy = ballA.y - ballB.y;

                 let distance = Math.sqrt( dx*dx + dy*dy );

                 if (distance < ballA.r + ballB.r) {

                     // collision detected, handle response

                     handleCollision(ballA, ballB);

                 }

             }

         }

      }

   }

}

Wait, but this will check ballA against all balls in the neighboring cells, including those in the same cell. But this could lead to checking the same pair multiple times (e.g., ballA and ballB in the same cell, then when ballB is processed, it will check again with ballA). To avoid redundant checks, perhaps only check balls with index higher than A's index? Not sure.

Alternatively, the collision response can be designed to handle each pair once. But this might complicate.

Alternatively, accept that some pairs are checked twice, but the grid reduces the total number of pairs. Since for 50 balls, the grid approach would reduce the number from 1225 to maybe a few hundred, which is manageable.

Now, the collision response between two balls. The user says a plausible approximation is acceptable. The standard elastic collision equations involve calculating the impulse and updating velocities based on mass, but maybe a simpler approach can be used.

The standard method:

When two balls collide, their velocities are updated based on their masses and the direction of collision.

The formula for elastic collisions (assuming no friction, perfect elasticity):

Let’s denote:

- m1, m2: masses of ball1 and ball2

- v1, v2: velocity vectors (vx, vy)

- pos1, pos2: positions (x,y)

The relative velocity between the two balls is v1 - v2.

The direction of collision is the unit vector pointing from ball2 to ball1: (pos1 - pos2) normalized.

The impulse is calculated as:

impulse = (2 * m1 * m2 / (m1 + m2)) * ( (v1 - v2) · (direction) ) * direction

Then, subtract this impulse from v1 and add to v2.

Wait, perhaps an easier way is to compute the collision normal (unit vector between centers), then compute the relative velocity along that normal, and then adjust the velocities so that they move apart.

Alternatively, here's a simplified approach:

Compute the direction vector between the two centers (dx, dy). The unit vector is (dx/d, dy/d) where d is the distance between centers.

Then, compute the relative velocity along this direction: v1's velocity towards the other ball minus v2's velocity towards ball1. Wait, perhaps:

The relative velocity along the normal is (v1.x - v2.x)*dx + (v1.y - v2.y)*dy. Wait, no, maybe better to compute the dot product of (v1 - v2) with the normal.

Let me think in terms of vectors:

Let’s have:

- v1 = [vx1, vy1]

- v2 = [vx2, vy2]

- delta = [x1 - x2, y1 - y2]

- normal = delta normalized (unit vector pointing from 2 to 1)

- The relative velocity along the normal is (v1 - v2) · normal.

- The impulse is such that after the collision, the velocities along the normal are reversed.

Alternatively, a common approximation is to swap the velocities along the collision normal, but scaled by the masses.

Alternatively, a simple approach (though not perfectly accurate) could be:

1. Compute the normal vector between the two balls.

2. Compute the relative velocity along that normal.

3. Compute the new velocities so that they separate.

But perhaps a better way is to use the standard elastic collision equations.

The standard formula for elastic collision in 2D is:

Let’s denote:

m1, m2: masses

v1, v2: velocity vectors of the two balls.

r1, r2: position vectors.

The collision normal is the unit vector pointing from ball2 to ball1: n = (r1 - r2)/d, where d is the distance between centers.

The relative velocity between the two balls is (v1 - v2).

The component of the relative velocity along the normal is (v1 - v2) · n.

The impulse magnitude is:

impulse = ( (2 * m1 * m2) / (m1 + m2) ) * ( (v1 - v2) · n ) / (m1 + m2) ?

Wait, perhaps better to look up the formula.

The correct formula for elastic collision:

The change in velocity for each ball is:

v1' = v1 - ( (2 * m2) / (m1 + m2) ) * ( (v1 - v2) · n ) * n

v2' = v2 + ( (2 * m1) / (m1 + m2) ) * ( (v1 - v2) · n ) * n

Where n is the unit normal vector from ball2 to ball1.

Alternatively, if the masses are equal (m1 = m2), this simplifies to swapping the velocity components along the normal.

But in our case, masses can vary (if we decide to use radius squared as mass). Let's assume mass is proportional to radius squared. So m = Math.PI * r^2? Or maybe just r^2 for simplicity. Alternatively, for simplicity, set all masses equal (m=1). The user says mass can be constant if preferred. Let's see.

The user's requirement says mass can be proportional to radius squared or constant. Let me choose to set mass as proportional to radius squared. So m = r*r. That way, larger balls have more mass and thus affect collisions more.

So, in code:

Each ball has a mass property, which is r*r.

Now, when handling collision between two balls, compute the normal vector between them, then compute the velocities using the above formulas.

Let me code that.

First, compute the vector between the two centers:

dx = ballA.x - ballB.x;

dy = ballA.y - ballB.y;

distance = Math.sqrt(dx*dx + dy*dy);

// They are already overlapping, so distance is less than rA + rB.

// The normal vector is (dx, dy) normalized.

let nx = dx / distance;

let ny = dy / distance;

// Compute relative velocity along the normal.

let vRelX = ballA.vx - ballB.vx;

let vRelY = ballA.vy - ballB.vy;

let vDotN = vRelX * nx + vRelY * ny;

// Compute the impulse scalar.

let m1 = ballA.mass;

let m2 = ballB.mass;

let j = ( (2 * m1 * m2) / (m1 + m2) ) * vDotN / (distance); // Wait, maybe the formula is different.

Wait, I might be mixing up the formulas. Let me recall:

The impulse J is calculated as:

J = ( ( (v1 - v2) · n ) * (m1 + m2) ) / ( (1/m1) + (1/m2) ) )

Wait, perhaps better to use the formula for the change in velocity.

Alternatively, here's a derivation:

The impulse applied to each ball is along the normal direction. The total impulse must be such that the velocities after collision are correct.

The change in velocity for ball A is:

ΔvA = ( ( -2 * m2 / (m1 + m2) ) * ( (v1 - v2) · n ) ) * n

Similarly for ball B:

ΔvB = ( ( 2 * m1 / (m1 + m2) ) * ( (v1 - v2) · n ) ) * n

Wait, perhaps:

The relative velocity along the normal before collision is vDotN = (v1 - v2) · n

After collision, the relative velocity along the normal should be -vDotN (if perfectly elastic).

So, the total change in relative velocity is -2*vDotN along the normal.

This change is distributed between the two balls based on their masses.

The impulse J is the force that causes this change.

The impulse applied to ball A is J * n, and to ball B is -J * n.

The total change in velocity for A is (J * n) / m1,

and for B is (-J * n) / m2.

The total change in relative velocity is (J/m1 - (-J)/m2) * n · n (since n is unit vector, dot product is 1).

Thus:

( J/m1 + J/m2 ) * n · n = -2 vDotN n · n

Wait, perhaps:

The change in v1 along n is (J / m1) * n,

the change in v2 along n is (-J / m2) * n,

so the total change in (v1 - v2) · n is (J/m1 + J/m2) * (n · n).

This should equal -2 vDotN.

Thus,

J (1/m1 + 1/m2) ) = -2 vDotN

Hence,

J = -2 vDotN / (1/m1 + 1/m2 )

Then,

ΔvA = (J / m1) * n

ΔvB = (-J / m2) * n

Wait, let me recheck:

Wait, the impulse J is applied to A, so:

v1' = v1 + (J * n)/m1

v2' = v2 + (-J * n)/m2

The relative velocity after is (v1' - v2') · n = (v1 - v2) · n + (J/m1 + J/m2) * (n · n) 

We want this to be equal to -vDotN (since it was vDotN before, and we want it to be -vDotN after).

So,

(v1 - v2) · n + J (1/m1 + 1/m2) ) = -vDotN

Thus,

J (1/m1 + 1/m2) ) = -2 vDotN

Therefore,

J = ( -2 vDotN ) / ( (1/m1) + (1/m2) )

Thus,

ΔvA = ( J / m1 ) * n 

ΔvB = ( -J / m2 ) * n 

So substituting J:

ΔvA = ( (-2 vDotN ) / ( (1/m1)+(1/m2) ) ) / m1 * n 

Hmm, this might be getting too complex. Alternatively, perhaps use the following code:

let j = ( ( (vRelX * nx) + (vRelY * ny) ) * (2) ) / ( (1/m1) + (1/m2) ) );

Wait, maybe I should look for a code snippet or formula.

Alternatively, here's a simplified approach for the velocity change:

let m1 = ballA.mass;

let m2 = ballB.mass;

let nx = dx / distance;

let ny = dy / distance;

let vRelDotN = (ballA.vx - ballB.vx)*nx + (ballA.vy - ballB.vy)*ny;

let j = ( (vRelDotN) * ( -2 ) ) / ( (1/m1) + (1/m2) );

// then,

ballA.vx += (j / m1) * nx;

ballA.vy += (j / m1) * ny;

ballB.vx -= (j / m2) * nx;

ballB.vy -= (j / m2) * ny;

Wait, but the sign here might need adjustment.

Alternatively, perhaps:

let impulse = ( (vRelDotN) * ( -2 ) ) / ( (1/m1) + (1/m2) );

ballA.vx += impulse * nx / m1;

ballA.vy += impulse * ny / m1;

ballB.vx -= impulse * nx / m2;

ballB.vy -= impulse * ny / m2;

Hmm, not sure. Maybe I can find a better way.

Alternatively, here's an alternative approach:

The relative velocity along the normal is (v1 - v2) · n.

The desired relative velocity after collision is - (v1 - v2) · n (assuming perfectly elastic).

The change in velocity along the normal for each ball is:

deltaV1 = ( (m2 / (m1 + m2)) ) * ( -2 * (v1 - v2) · n )

deltaV2 = ( (m1 / (m1 + m2)) ) * ( 2 * (v1 - v2) · n )

Wait, perhaps:

deltaV1 = ( ( -2 * m2 * (vRelDotN) ) / (m1 + m2) ) * n;

deltaV2 = ( ( 2 * m1 * (vRelDotN) ) / (m1 + m2) ) * n;

Then,

ballA.vx += deltaV1.x;

ballA.vy += deltaV1.y;

ballB.vx += deltaV2.x;

ballB.vy += deltaV2.y;

Hmm, maybe this is better.

Alternatively, perhaps I can find a code example for 2D elastic collisions.

Looking up, a common approach is:

function resolveCollision(ballA, ballB) {

    let dx = ballA.x - ballB.x;

    let dy = ballA.y - ballB.y;

    let dist = Math.sqrt(dx*dx + dy*dy);

    let overlap = (ballA.r + ballB.r - dist);

    if (dist == 0) return;

    let nx = dx / dist;

    let ny = dy / dist;

    let dot = (ballA.vx - ballB.vx)*nx + (ballA.vy - ballB.vy)*ny;

    if (dot < 0) return;

    // Calculate impulse

    let j = ( - (1 + restitution) * dot ) / ( (ballA.mass / ballA.r) + (ballB.mass / ballB.r) );

    // Wait, maybe masses are involved.

    let j = ( - (1 + 0.9) * dot ) / ( (1/ballA.mass) + (1/ballB.mass) );

    // Apply impulse

    let invMassA = 1 / ballA.mass;

    let invMassB = 1 / ballB.mass;

    ballA.vx += invMassA * j * nx;

    ballA.vy += invMassA * j * ny;

    ballB.vx -= invMassB * j * nx;

    ballB.vy -= invMassB * j * ny;

    // Move them apart to prevent tunneling

    let correction = overlap / (1 + invMassA + invMassB) * 0.5;

    ballA.x += nx * correction * invMassA;

    ballB.x -= nx * correction * invMassB;

    ballA.y += ny * correction * invMassA;

    ballB.y -= ny * correction * invMassB;

}

Wait, perhaps this is better. The restitution here is the coefficient of restitution (set to 0.9 for some damping). The correction moves the balls apart to prevent overlapping.

This seems more manageable. Let me try to structure this.

First, calculate the normal vector between the two balls.

Then compute the relative velocity along the normal.

If the relative velocity is towards each other (dot product negative?), then proceed.

Wait, the dot product is (vA - vB) · n. If this is positive, it means they are moving away from each other, so no collision. If negative, moving towards each other.

Wait, actually, if the balls are moving towards each other, the relative velocity along the normal would be negative (since n is pointing from B to A, so if vA is towards B and vB is towards A, then (vA - vB) · n would be negative).

Hmm, perhaps the condition should be if (dot > 0) then they are moving away, so no need to resolve. Wait, maybe the opposite.

Wait, let me think:

Suppose the normal vector points from B to A (dx, dy). The velocity of A is vA, velocity of B is vB.

The relative velocity of A minus B is (vA - vB). The dot product with n gives the component of their relative velocity along the normal direction.

If this dot product is positive, that means A is moving away from B along the normal direction, so no collision. Wait, no. Wait, if the balls are overlapping, but moving away, then the collision is already happening, but they are moving away, so maybe the collision was already resolved. Hmm, perhaps the condition should be if (dot < 0), meaning they
 <!-- 763.92s -->