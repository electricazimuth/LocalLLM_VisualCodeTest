You are an expert javascript and html coder.

# Bouncing Balls in a Container Simulation Webgame

Use Javascript, HTML and Canvas to simulate 20 balls bouncing inside a spinning heptagon

**Goal:**
Create a bouncing ball physics simulations using HTML, JavaScript and Canvas. Utilize the HTML Canvas API for complex rendering, implement physics (including gravity, damping, and inter-object collisions) with JavaScript, manage an efficient animation loop, and apply optimization techniques for performance.

**The Task:**
Create a single HTML page that displays a spinning heptagon container drawn on an HTML Canvas. Inside this container, simulate 20 balls that interact with each other and the container walls under the influence of gravity, losing energy upon collision.

**Specific Requirements:**

- All balls have the same radius.
- All balls have a number on it from 1 to 20.
- All balls drop from the heptagon center when starting.
- Ball colors are: #f8b862, #f6ad49, #f39800, #f08300, #ec6d51, #ee7948, #ed6d3d, #ec6800, #ec6800, #ee7800, #eb6238, #ea5506, #ea5506, #eb6101, #e49e61, #e45e32, #e17b34, #dd7a56, #db8449, #d66a35
- The balls should be affected by gravity and friction, and they must bounce off the rotating walls realistically. 
- There should be collisions between balls.
- The balls impact bounce height will not exceed the radius of the heptagon, but higher than ball radius.
- All balls rotate with friction, the numbers on the ball can be used to indicate the spin of the ball.
- The heptagon is spinning around its center, and the speed of spinning is 360 degrees per 5 seconds.
- The heptagon size should be large enough to contain all the balls.
- Do not use any javascript libraries, only vanilla javascript
- Implement collision detection algorithms and collision response etc. by yourself. 
- All codes should be put in a single html file.

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
*   Create 20 balls.
*   Initialize them within the spinning heptagon centralized and with random initial velocities. Attempt to prevent initial overlaps, though perfect initial non-overlap isn't the primary focus.

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
The naive approach for ball-to-ball collision detection involves checking every pair, which is O(n^2) complexity and becomes slow with many balls. Implement optimization strategies to improve the performance of the collision detection phase, allowing the simulation to run smoothly with 20+ balls. Common techniques include spatial partitioning (e.g., grids, quadtrees).

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
    <canvas id="gameCanvas" width="500" height="500"></canvas>
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
Implement all required features (spinning heptagon container, gravity, wall bounce + damping, ball-ball collision detection & response)  
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