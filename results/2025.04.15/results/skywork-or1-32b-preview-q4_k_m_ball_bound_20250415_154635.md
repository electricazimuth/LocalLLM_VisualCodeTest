Okay, I need to create a bouncing balls simulation using HTML, CSS, and JavaScript. Let me start by understanding the requirements. The main goal is to have a canvas with multiple balls bouncing around, interacting with each other and the walls. The key features are gravity, damping, collisions, and performance optimizations.

First, the HTML structure is already provided. I need to use the canvas element and set up the script. The CSS seems okay, just some styling for the canvas and body. So I'll focus on the JavaScript part.

The balls need to be represented as objects. Each ball has position, velocity, radius, mass, and color. Initialization requires random positions and velocities. But I have to prevent them from overlapping initially. Hmm, maybe check for overlaps when creating each ball and reposition if needed. But the user said perfect initial non-overlap isn't required, so maybe just random positions within the canvas, considering their radius.

For the animation loop, using requestAnimationFrame is straightforward. The physics updates happen each frame. Gravity affects the vertical velocity. Then update positions. Wall collisions: check if the ball's x or y plus radius exceeds the canvas dimensions. When a collision occurs, reverse the velocity component and apply damping. Also, correct the position to prevent sticking. For example, if the ball goes beyond the left wall, set x to radius and multiply vx by -dampingFactor.

Ball-to-ball collisions are trickier. The naive approach is checking every pair, which is O(n²). With 50 balls, that's 1225 pairs per frame. That might be manageable with some optimizations. But maybe implement spatial partitioning. However, for simplicity and time constraints, perhaps start with the naive approach and see if it's performant enough. If not, then think about grids or quadtrees.

The collision response between two balls: need to calculate the distance between centers. If it's less than the sum of radii, they collide. Then compute the direction vector between them. Project the velocities onto that direction. Calculate the relative velocity along that axis. Apply impulse based on mass and restitution coefficient. Wait, but elastic collision equations can be complex. Maybe use a simplified approach where velocities are adjusted based on their masses and the collision normal.

Alternatively, for each collision, reverse the component of velocity along the line connecting the two centers, applying some damping. But that might not be physically accurate. Need to look up the correct way to handle elastic collisions with two objects.

The standard formula for elastic collision in 2D involves calculating the impulse based on the masses and the collision normal. Let me recall: for two objects with masses m1 and m2, velocities v1 and v2, and collision normal n, the impulse is ( (v2 - v1) · n ) * (m1 + m2) / (m1 * n² + m2 * n²). Wait, maybe it's better to use the formula from physics. Let me check.

The formula for the change in velocity for each object in an elastic collision is:

v1' = v1 - ( (2 * m2) / (m1 + m2) ) * ( (v1 - v2) · n ) * n

v2' = v2 + ( (2 * m1) / (m1 + m2) ) * ( (v1 - v2) · n ) * n

Where n is the unit vector from the center of mass of object 1 to object 2.

But maybe in this simulation, mass is proportional to the radius squared. So each ball's mass is Math.PI * r^2, but maybe for simplicity, just use r squared since the actual mass proportionality might not matter as much as the relative masses.

Wait, the problem says mass can be proportional to radius squared or constant. So perhaps using radius squared as mass would be better for realism.

So, for each pair of balls, when they collide, compute the unit vector between their centers. Then compute the relative velocity. The impulse would then adjust their velocities to prevent overlap and apply damping.

But implementing this correctly is crucial. Let me outline the steps:

1. For each pair of balls, check if distance <= r1 + r2.

2. If so, compute the collision normal (unit vector from ball1 to ball2).

3. Calculate the relative velocity between the two balls along the collision normal.

4. If the relative velocity is negative (they are moving towards each other), compute the impulse.

5. Apply the impulse to both balls' velocities, considering their masses and damping.

6. Also, adjust their positions to prevent overlapping.

Wait, adjusting positions might be necessary if the collision response isn't enough. But in reality, during the simulation, if the collision is detected and response applied, the overlap should be minimal. However, in practice, due to frame rate limitations, sometimes the objects might have moved past each other in a single frame. So, perhaps position correction is needed.

But position correction can cause tunneling. So maybe it's better to use a continuous collision detection approach, but that's more complex. For this project, perhaps just applying the velocity change and then moving the balls apart if they are overlapping.

Alternatively, after resolving the velocities, check if they are still overlapping and adjust their positions. But that might cause jittering. Hmm.

Alternatively, during the collision response, calculate the overlap and move the balls along the collision normal by the overlap distance. But how to split the overlap between the two balls? Maybe proportionally based on their masses.

But this could get complicated. Maybe for the sake of time, just adjust their positions by half the overlap each. But that might not be physically accurate. Alternatively, after detecting the collision, compute how much they overlap and move them apart.

The overlap distance is (distanceBetweenCenters - (r1 + r2)). So if distance is 10 and sum of radii is 8, overlap is 2. So each ball is moved along the collision normal by (overlap / 2) * normal. But maybe split based on mass. Heavier balls move less.

But perhaps for simplicity, split equally. So, after detecting the collision, compute the overlap, and adjust the positions of both balls along the collision normal by (overlap / 2) * normal.

But this could lead to issues if the balls are stuck again in the next frame. But with velocity adjustments and damping, they should rebound.

So the steps for ball-to-ball collision response:

- Compute the unit vector between the centers (normal).

- Compute the overlap distance (sum of radii - distanceBetweenCenters). Wait, no: if distance is less than sum, then sum - distance is the overlap.

Wait, distance = sqrt( (x2 -x1)^2 + (y2 - y1)^2 )

sum = r1 + r2.

If distance < sum, then overlap is sum - distance.

So to correct the positions, we need to move the balls apart by overlap distance. How to split that? Let's say we move each ball along the normal by (overlap * normal) * (mass of other / total mass). So the heavier ball moves less.

Wait, perhaps. For example, if ball1 has mass m1 and ball2 has mass m2, the total mass is m1 + m2. Then, ball1 moves by (overlap * normal) * (m2 / (m1 + m2)), and ball2 moves by (overlap * normal) * (-m1 / (m1 + m2)). Wait, no. Because the normal vector points from ball1 to ball2. So to move them apart, ball1 should move in the opposite direction of the normal, and ball2 in the direction of the normal.

Wait, the normal vector is (x2 - x1, y2 - y1). So the direction from ball1 to ball2. To move them apart, ball1 should move in the direction opposite to the normal, and ball2 in the direction of the normal.

But how much each moves depends on their masses. So the total overlap is sum - distance. So the correction is (sum - distance) * normal. So the total correction vector is (sum - distance) * normal. Then, split this between the two balls based on their masses. So ball1's position is adjusted by (correction * (m2 / (m1 + m2))) and ball2's position is adjusted by (correction * (-m1 / (m1 + m2))). Wait, that way, the total correction is (m2/(m1+m2) - m1/(m1+m2)) ) * correction? No, perhaps I'm getting confused.

Alternatively, the total correction needed is (sum - distance) in the direction of the normal. So the vector to add to ball1's position is (correction * (m2 / (m1 + m2))) * normal, and ball2's position is (correction * (m1 / (m1 + m2))) * (-normal). Wait, perhaps. Because the heavier ball should be moved less. So if m1 is larger, then ball2 is moved more.

But I'm not sure. Maybe for the purpose of this simulation, just split the correction equally. So each ball is moved along the normal by (overlap / 2) * normal. But that could lead to oscillations if the masses are very different. But maybe with damping in the velocity, it's manageable.

Alternatively, perhaps position correction isn't necessary if the collision response is handled correctly. But in reality, when using velocity-based collision response, if the objects are overlapping, you might need to separate them to prevent continuous collisions.

So perhaps both: adjust their velocities to rebound and adjust their positions to prevent overlapping.

But how to calculate the velocity change.

Let me look up the formula for elastic collision between two circles.

The standard approach is:

When two circles collide, calculate the collision normal (unit vector from center1 to center2). Then, compute the relative velocity between the two objects along the collision normal. If the relative velocity is towards each other, apply an impulse to both objects to reverse the relative velocity.

The formula for the impulse is:

impulse = ( (v2 - v1) · n ) * (kn / (1/m1 + 1/m2 + 0.1)) )

Wait, perhaps it's better to use the following approach:

let nx = (x2 - x1) / distance;

let ny = (y2 - y1) / distance;

let relativeVelocityX = vx2 - vx1;

let relativeVelocityY = vy2 - vy1;

let dotProduct = relativeVelocityX * nx + relativeVelocityY * ny;

if (dotProduct > 0) { // they are moving towards each other

   let impulse = dotProduct / (mass1 + mass2);

   vx1 += impulse * mass2 * nx;

   vy1 += impulse * mass2 * ny;

   vx2 -= impulse * mass1 * nx;

   vy2 -= impulse * mass1 * ny;

}

Wait, I think that's the correct way. But I'm not entirely sure. Let me check some references.

Alternatively, according to the physics formula, the impulse magnitude is ( (v2 - v1) · n ) * (2 * m1 * m2) / (m1 + m2) ), and then each velocity is adjusted by impulse * (1/mass). So:

let velocityDifference = (vx2 - vx1) * nx + (vy2 - vy1) * ny;

if (velocityDifference > 0) {

   let impulse = velocityDifference / ( (mass1 + mass2) / (mass1 * mass2) );

   // Wait, maybe impulse = (velocityDifference) * (2 * m1 * m2) / (m1 + m2);

   impulse = velocityDifference * (2 * mass1 * mass2) / (mass1 + mass2);

  vx1 += (impulse / mass1) * nx;

   vy1 += (impulse / mass1) * ny;

   vx2 -= (impulse / mass2) * nx;

   vy2 -= (impulse / mass2) * ny;

}

But I'm not confident. Alternatively, perhaps use the following approach from the article "2D Collision Detection and Response".

The formula for elastic collision is:

v1' = v1 - ( (2 * m2) / (m1 + m2) ) * ( (v1 - v2) · n ) * n

v2' = v2 + ( (2 * m1) / (m1 + m2) ) * ( (v1 - v2) · n ) * n

Where n is the unit normal vector pointing from object 1 to object 2.

So, in code:

let dx = x2 - x1;

let dy = y2 - y1;

let distance = Math.sqrt(dx * dx + dy * dy);

if (distance < r1 + r2) {

   let nx = dx / distance;

   let ny = dy / distance;

   let relativeVelocityX = vx2 - vx1;

   let relativeVelocityY = vy2 - vy1;

   let dotProduct = relativeVelocityX * nx + relativeVelocityY * ny;

   if (dotProduct > 0) {

      let impulse = (dotProduct) * (2 * mass1 * mass2) / (mass1 + mass2);

      let impulseOverMass1 = impulse / mass1;

      let impulseOverMass2 = impulse / mass2;

      vx1 += impulseOverMass1 * nx;

      vy1 += impulseOverMass1 * ny;

      vx2 -= impulseOverMass2 * nx;

      vy2 -= impulseOverMass2 * ny;

   }

}

But also, after applying this, the balls might still overlap. So perhaps we need to separate them.

So, compute the overlap distance, which is (r1 + r2 - distance). Then, compute the separation vector: (overlap) * nx * 0.5 (assuming split equally). But maybe split based on mass.

So, for position correction:

let overlap = (r1 + r2) - distance;

let ax = nx * overlap * (mass2 / (mass1 + mass2));

let ay = ny * overlap * (mass2 / (mass1 + mass2));

ball1.x -= ax;

ball1.y -= ay;

ball2.x += ax;

ball2.y += ay;

Wait, because the normal vector is from ball1 to ball2. So to separate them, ball1 moves in the opposite direction of the normal, and ball2 moves in the direction of the normal. The amount each moves is proportional to the other's mass. So the total separation is overlap.

So, for example, if mass1 is much larger than mass2, then ball2 moves more.

So, the correction for ball1 is (overlap * (mass2 / (mass1 + mass2))) * (-nx, -ny)

And for ball2, (overlap * (mass1 / (mass1 + mass2))) * (nx, ny)

But wait, the normal vector is from ball1 to ball2. So to separate, ball1 should move in the direction opposite to the normal, and ball2 in the direction of the normal.

So the separation for ball1 is (-nx * overlap * mass2 / (mass1 + mass2)), and for ball2, nx * overlap * mass1 / (mass1 + mass2).

Yes, that way, the total separation is overlap.

So, for each ball:

ball1.x += (-nx) * (mass2 / (mass1 + mass2)) * overlap;

ball1.y += (-ny) * (mass2 / (mass1 + mass2)) * overlap;

ball2.x += nx * (mass1 / (mass1 + mass2)) * overlap;

ball2.y += ny * (mass1 / (mass1 + mass2)) * overlap;

But this would require that after moving, the distance between them is exactly r1 + r2. But in practice, after applying the velocity changes and the position correction, they should no longer overlap.

But how to handle this in code. So during the collision response, after calculating the overlap, we need to adjust their positions.

So, in code:

if (distance < r1 + r2) {

   // calculate normal, etc.

   let overlap = (r1 + r2) - distance;

   // calculate position correction

   let ax = nx * overlap * (mass2 / (mass1 + mass2));

   let ay = ny * overlap * (mass2 / (mass1 + mass2));

   ball1.x -= ax;

   ball1.y -= ay;

   ball2.x += ax;

   ball2.y += ay;

}

But this might need to be done before or after the velocity adjustments. Probably after detecting the collision, first separate them, then adjust velocities. Or vice versa. Hmm.

Alternatively, some sources suggest that position correction should be done before velocity adjustment. But I'm not sure. Maybe the order doesn't matter. But for the simulation, it's important to prevent overlapping.

But perhaps the position correction is needed to avoid tunneling. However, if the velocity adjustments are correct, the overlap would be minimal. But in cases where the balls move fast, they might pass through each other. So position correction helps here.

But implementing both collision response and position correction might be necessary.

So, the plan for ball-to-ball collision:

1. Check distance between centers.

2. If distance < r1 + r2, compute normal, overlap.

3. Apply position correction to separate them.

4. Apply velocity changes based on elastic collision.

But how to handle multiple collisions in one frame. For example, if after moving the balls apart, their velocities are adjusted, but in the same frame, another collision occurs. But perhaps in this simulation, it's acceptable.

Now, the problem is that checking all pairs is O(n²), which can be slow for 50 balls. So 50*50=2500 pairs per frame. But maybe with some optimizations.

The user mentioned using spatial partitioning, like grids. So, for example, divide the canvas into a grid of cells, and for each cell, check only the balls in adjacent cells. But implementing a grid would take some time.

Alternatively, in the naive approach, just check all pairs. Let's see. 50 balls would be 50*49/2 = 1225 pairs per frame. For each pair, calculate distance. But calculating distance (sqrt) is expensive. But maybe first check the squared distance to avoid the sqrt.

So, for each pair, compute dx = x2 - x1, dy = y2 - y1. Then dx*dx + dy*dy < (r1 + r2)^2. So squared distance compared to squared sum of radii. This avoids the sqrt, which is good.

So, for 50 balls, 1225 pairs, each with a couple of multiplications and additions. Modern CPUs can handle that, but in JavaScript, it might be a bit slow. So perhaps the naive approach is manageable, but for 50 balls, it's possible.

But to optimize, perhaps implement a spatial grid. Let's think about that.

Create a grid where each cell is, say, 100x100 pixels. For each ball, add it to the grid cells it overlaps. Then, for each ball, when checking for collisions, only check balls in the same or adjacent cells. This reduces the number of pairs to check.

But implementing this requires:

- Creating a grid structure.

- For each ball, determine which cells it is in.

- For each cell, keep a list of balls in that cell.

- When checking collisions, for a ball, check all balls in the same cell and adjacent cells.

But the grid size is a parameter that affects performance. Too small cells would mean each ball is in multiple cells, increasing overhead. Too large cells might not reduce the number of pairs.

Alternatively, for each ball, check balls in a certain radius around it. But that's similar to the grid approach.

But given time constraints, perhaps start with the naive approach and see. If performance is an issue, then implement a grid.

But the problem requires implementing optimization strategies. So the user expects some optimization.

So, perhaps implement a spatial grid.

So, in code:

Create a grid object, which is a 2D array. Each cell has a list of balls.

The grid size can be a variable, like GRID_SIZE = 100.

Then, for each ball, determine which cells it occupies. Since a ball has a radius, it can span multiple cells. For example, if the grid size is 100, and the ball's position is at (95, 95) with radius 10, it spans into the next cell. So need to check all cells that the ball's bounding box covers.

For each ball, compute the min and max x and y coordinates (x - r, x + r, y - r, y + r). Then, determine which grid cells these coordinates fall into. For each cell in that range, add the ball to those cells.

Then, when checking for collisions, for each ball, find all the cells it is in, and check all balls in those cells and adjacent cells. But this can get complicated.

Alternatively, for each ball, when checking for collisions, look into the current cell and adjacent cells, and check all balls in those cells. But to avoid checking the same pair twice, we can mark pairs as checked.

Alternatively, for each ball, check all balls in the same cell and adjacent cells, but only check pairs where the current ball's index is less than the other ball's index to avoid duplicates.

But managing the grid can be tricky. Alternatively, use an array to store all balls, and for each ball, check other balls in a subset of the array. But this doesn't help with the O(n²) problem.

Alternatively, during the update loop, for each ball, check only the balls that come after it in the array. So for i from 0 to n-1, and j from i+1 to n-1. This way, each pair is checked once. But this is still O(n²).

So perhaps the naive approach is the way to go, but with the squared distance optimization.

So, in code:

for (let i = 0; i < balls.length; i++) {

   for (let j = i + 1; j < balls.length; j++) {

      const ball1 = balls[i];

      const ball2 = balls[j];

      const dx = ball1.x - ball2.x;

      const dy = ball1.y - ball2.y;

      const distanceSquared = dx * dx + dy * dy;

      const sumRadii = ball1.r + ball2.r;

      if (distanceSquared < sumRadii * sumRadii) {

          // handle collision

      }

   }

}

This way, each pair is checked once.

But with 50 balls, this is 50*49/2 = 1225 checks. Each check involves a few calculations. But in JavaScript, this could be manageable, especially if the code is optimized.

So perhaps proceed with this approach.

Now, the next step is to implement the collision response.

So, for each pair that collides:

1. Compute the unit vector (nx, ny) from ball1 to ball2.

2. Compute the relative velocity between the two balls along the collision normal.

3. If the relative velocity is positive (they are moving towards each other), compute the impulse and adjust velocities.

4. Apply damping to the velocities (multiply by a damping factor).

Wait, but the problem says to apply damping (energy loss) upon collision. So after reversing the velocity component, multiply by a damping factor. But in the ball-to-ball collision, how to apply damping.

In the wall collision, when reversing the velocity, multiply by a damping factor (e.g., 0.8). For ball-to-ball, perhaps after calculating the impulse and adjusting velocities, multiply the velocities by a damping factor. Or perhaps include the damping in the impulse calculation.

Alternatively, the collision response should include a restitution coefficient, which is a factor by which the relative velocity is reduced. For example, in elastic collisions, the restitution is 1. For inelastic, it's 0. But in this case, the problem requires damping, so perhaps multiply the impulse by a restitution factor.

But the problem statement says that a mathematically perfect elastic collision is complex and an approximation is acceptable. So perhaps after calculating the impulse, multiply the velocity change by a damping factor.

Alternatively, in the impulse calculation, include a restitution coefficient. For example:

impulse = (dotProduct) * (2 * m1 * m2) / (m1 + m2) * restitution;

Where restitution is a value less than 1 (e.g., 0.8).

But the problem mentions applying damping (energy loss) upon collision. So perhaps after the collision response, multiply the velocities of both balls by a damping factor. But that would reduce their overall speed, which might not be correct. Because in a collision, energy is lost as heat, etc., but in a way that depends on the materials.

Alternatively, when applying the impulse, include a restitution coefficient that reduces the rebound velocity.

So, perhaps the code would look like:

let dotProduct = (vx2 - vx1) * nx + (vy2 - vy1) * ny;

if (dotProduct > 0) {

   let impulse = (dotProduct) * (2 * m1 * m2) / (m1 + m2) * restitution;

   // apply impulse to velocities

}

Where restitution is a value like 0.8.

But how to handle restitution between two balls. Each could have a restitution property, but the problem doesn't specify. So perhaps use a global restitution factor.

Alternatively, the problem mentions a damping factor for wall collisions. Maybe use the same factor for ball-to-ball collisions.

But the problem says that in wall collisions, after reversing the velocity component, apply damping by multiplying by a damping factor. For ball-to-ball, perhaps apply a similar damping by using a restitution coefficient.

So, in the code, perhaps have a global damping factor (like 0.8) and apply it to the impulse.

So, in the code:

const restitution = 0.8;

impulse = (dotProduct) * (2 * m1 * m2) / (m1 + m2) * restitution;

But I'm not sure if this is the correct approach. Alternatively, after calculating the impulse as in the elastic case, multiply the velocity changes by the restitution.

But perhaps the correct way is to multiply the relative velocity by a restitution factor. For example:

impulse = (dotProduct * restitution) * (2 * m1 * m2) / (m1 + m2);

So that the rebound velocity is reduced by the restitution factor.

But I need to test this.

Alternatively, after resolving the collision, apply a damping to the velocities of both balls. For example, multiply their velocities by a damping factor. But that might not be correct, as some energy is lost during the collision, but not all.

Alternatively, in the wall collision, the velocity is reversed and multiplied by a damping factor. For ball-to-ball, perhaps the same damping is applied to the component of velocity along the collision normal.

But this is getting complicated.

Alternatively, after calculating the impulse and adjusting the velocities, multiply the normal component of the velocities by the damping factor.

For example:

After applying the impulse:

vx1 += dx * nx;

vy1 += dx * ny;

vx2 -= dx * nx;

vy2 -= dx * ny;

Then, multiply the normal component by damping.

But perhaps this is not the right approach.

Alternatively, after the collision, the velocity component along the normal is multiplied by a damping factor.

But how to extract the velocity component along the normal.

For ball1:

let normalVelocity1 = (vx1 * nx + vy1 * ny);

normalVelocity1 *= -damping; // reverse and dampen

vx1 = vx1 - normalVelocity1 * nx;

vy1 = vy1 - normalVelocity1 * ny;

Wait, no. Because the velocity component along the normal is (vx * nx + vy * ny). So to set it to -damping * original, you can do:

let normalComponent = vx1 * nx + vy1 * ny;

normalComponent *= -damping;

vx1 = (vx1 - normalComponent * nx) + normalComponent * nx;

Wait, that's not correct. Let me think.

The velocity can be decomposed into tangential and normal components.

The normal component is (normalComponent) * (nx, ny).

The tangential component is (vx, vy) - normalComponent * (nx, ny).

So, to apply damping to the normal component:

newNormalComponent = normalComponent * -damping;

Then, the new velocity is tangential component + newNormalComponent.

So:

let normalComponent = vx1 * nx + vy1 * ny;

let tangentialComponentX = vx1 - normalComponent * nx;

let tangentialComponentY = vy1 - normalComponent * ny;

normalComponent *= -damping;

vx1 = tangentialComponentX + normalComponent * nx;

vy1 = tangentialComponentY + normalComponent * ny;

But this
 <!-- 762.73s -->