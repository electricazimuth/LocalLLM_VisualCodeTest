You are an expert javascript and html coder.

# Bouncing Balls Simulation Webgame

**Goal:**
Create a bouncing ball physics simulations using html, js and css. Utilize the HTML Canvas API for complex rendering, implement moderately complex physics (including gravity, damping, and inter-object collisions) with JavaScript, manage an efficient animation loop, and apply optimization techniques for performance.

**The Task:**
Create a single HTML page that displays a square container drawn on an HTML Canvas. Inside this container, simulate a significant number of balls (e.g., 50+) that interact with each other and the container walls under the influence of gravity, losing energy upon collision.

**Specific Requirements:**

**HTML Setup:**
Use the provided html skeleton

**Canvas Rendering:**
Use the Canvas 2D context (`getContext('2d')`) for all drawing.
Draw multiple balls (target **at least 30**) as filled circles, potentially with varying radii and colors.

**JavaScript Logic & Physics Implementation:**
**Ball Representation:** 
Represent each ball using an object or class. Each ball must have properties like:
*   Position (`x`, `y`)
*   Velocity (`vx`, `vy`)
*   Radius (`r`)
*   Mass (can be proportional to radius squared, or constant if preferred)
*   Color (`color`)

**Initialization:**
*   Create the specified number of balls (aim for 50+).
*   Initialize them with random positions *within* the canvas boundaries and random initial velocities. Attempt to prevent initial overlaps, though perfect initial non-overlap isn't the primary focus.

**Animation Loop:** 
Use `requestAnimationFrame` for a smooth and efficient animation loop.

**Physics Update (per frame):**
*   **Clear Canvas:** Clear the canvas completely.
*   **Apply Gravity:** For *each* ball, update its vertical velocity (`vy`) based on a constant gravitational acceleration (e.g., `vy += gravityValue`).
*   **Update Positions:** Update each ball's position based on its current velocity (`x += vx`, `y += vy`).
*   **Wall Collision Detection & Response:**
    *   Check if each ball collides with the container walls (consider radius).
    *   If a wall collision occurs:
        *   Reverse the appropriate velocity component (`vx` or `vy`).
        *   **Apply Damping (Energy Loss):** Reduce the magnitude of the reversed velocity component by a damping factor (e.g., `vx = -vx * dampingFactor`, where `dampingFactor` is less than 1, like 0.8 or 0.9).
        *   Correct the ball's position to ensure it's fully inside the boundary after the bounce.
*   **Ball-to-Ball Collision Detection & Response:**
    *   **Detection:** Implement logic to detect collisions between *pairs* of balls. A collision occurs if the distance between the centers of two balls is less than or equal to the sum of their radii.
    *   **Response:** Implement a *plausible* collision response. A common approach involves calculating the impulse and updating the velocities of the colliding pair based on their masses and the collision angle. (Note: A mathematically perfect elastic collision response is complex; a well-reasoned, functional approximation is acceptable. Focus on preventing overlap and having balls react to each other). You *must* prevent balls from significantly overlapping or sticking together after a collision.
*   **Draw:** Redraw all balls in their new positions.

**Preferred Features:**
The naive approach for ball-to-ball collision detection involves checking every pair, which is O(n^2) complexity and becomes slow with many balls. Implement optimization strategies to improve the performance of the collision detection phase, allowing the simulation to run smoothly with 50+ balls. Common techniques include spatial partitioning (e.g., grids, quadtrees).

# Deliverable
The page must run directly in a modern web browser without external physics engines or utility libraries (plain JavaScript and Canvas API only).
Use the following boilerplate html. If you want to add notes to your response add them into the section#notes area in the html page.

```
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

        // --- YOUR CODE GOES HERE ---

        function gameLoop(timestamp) {
            // Clear canvas (usually needed)
            // ctx.clearRect(0, 0, W, H);

            // --- Update logic ---

            // --- Draw logic ---

            requestAnimationFrame(gameLoop);
        }

        // Start the loop
        // requestAnimationFrame(gameLoop);

        // Add any initial setup or event listeners here

    </script>
    <section id="notes">
    
    </section>
</body>
</html>
```

# Important

**Correctness & Completeness:**  
Implement all required features (gravity, wall bounce + damping, ball-ball collision detection & response)  
**Canvas Usage:**  
Proper and efficient use of the Canvas API.  
**JavaScript Structure & Readability:**  
Clean, organized, well-commented code. Effective use of objects/classes, functions, and data structures.  
**Physics Implementation:**   
Sound logic for gravity, wall collisions, damping, and ball-to-ball interactions (detection accuracy and plausible response).  
**Collision Handling:** 
Correct detection logic for both wall and inter-ball collisions. Reasonable response implementation that prevents sticking/major overlap.  
**Animation & Performance:** 
Smooth animation using `requestAnimationFrame`. Demonstrable consideration and/or implementation of optimization techniques, especially for collision detection, allowing a reasonable frame rate with the target number of balls.

Respond with a working html, css and js webpage that implements your solution.