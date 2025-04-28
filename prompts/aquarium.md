You are an expert javascript and html coder.

# Autonomous Aquarium Simulation

**Goal:**
Create a visually appealing simulation of fish swimming in an aquarium environment using HTML, JS, and CSS. Demonstrate javascript best practices for object-oriented design, managing multiple animated objects, implementing simple autonomous behaviors, handling boundaries, and using an efficient rendering loop.

**Task:**
Develop a simulation where multiple "fish" swim autonomously within the bounds of the canvas. Fish should appear to move with some natural variation, change direction periodically, and interact realistically with the edges of the "tank" (the canvas).

**Requirements:**
1.  **Object Management:** Create and manage multiple fish objects, storing them in a suitable data structure (e.g., an array).
2.  **Initialization:** Start the simulation with a predefined number of fish (e.g., 10-15) placed at random initial positions within the canvas.
3.  **Fish Representation:** Each fish object should encapsulate its state, including:
    *   Position (x, y).
    *   Velocity (vx, vy) or Speed and Direction.
    *   Size.
    *   Color (allow for variation).
    *   A simple visual form (e.g., an oval, triangle, or a combination of shapes).
4.  **Autonomous Movement:**
    *   Implement continuous movement for each fish based on its velocity/direction.
    *   Introduce a simple "wandering" behavior, causing fish to gradually change direction over time to avoid linear-only movement.
    *   Implement boundary detection: Fish must remain within the visible canvas area.
    *   Implement boundary interaction: When a fish approaches or hits an edge, it should react appropriately and smoothly turn away towards the middle of the canvas.
5.  **Animation Loop (`requestAnimationFrame`):**
    *   Use `requestAnimationFrame` for the main simulation loop.
    *   Calculate and use delta time for frame-rate independent, smooth animation and physics updates.
    *   **Update Logic:** In each frame, update the state of every fish (position, velocity/direction based on behavior rules and boundary interactions).
    *   **Draw Logic:** In each frame, clear the canvas (consider a suitable background color like light blue) and redraw all fish based on their current state (position, orientation).

**Visual Goal:**
The canvas should display a continuous, calming animation resembling an aquarium, with multiple fish swimming around within the defined space. The movement should feel somewhat organic, not just robotic bouncing.

**Functional Requirements:**
*   The simulation must run autonomously without requiring user interaction.
*   All fish must stay strictly within the canvas boundaries.
*   Animation should be smooth and consistent across different frame rates (correct delta time implementation).
*   The implementation should be reasonably efficient to handle the specified number of fish.

**Desirable Features:**
*   Implement distinct Fish classes or use factory functions for good object structure.
*   Vary the appearance (size, color, simple shape) and speed of different fish.
*   Orient the fish graphic to face the direction it's moving.
*   Implement smoother turning behavior near boundaries rather than instantaneous direction flips.
*   Add subtle secondary motion (e.g., a simple tail wiggle).
*   Consider adding static background elements like simple plants or rocks (optional).

# Deliverable
The simulation must run directly in a modern web browser using only plain JavaScript and the Canvas API (no external libraries). Provide the complete solution within a single HTML file, using the following boilerplate. You may add notes about your implementation approach within HTML comments or a dedicated `<section id="notes">` if desired.

```html
<!DOCTYPE html>
<html>
<head>
    <title>Aquarium Simulation</title>
    <style>
        body { margin: 0; overflow: hidden; background-color: #e0f7fa; } /* Light blue background */
        canvas { display: block; margin: 20px auto; border: 1px solid #888; background-color:rgb(207, 247, 255); } /* blue water */
    </style>
</head>
<body>
    <canvas id="simulationCanvas" width="512" height="512"></canvas>
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

<body>
    <canvas id="simulationCanvas" width="800" height="600"></canvas>

    <script>
        // --- YOUR JAVASCRIPT CODE GOES HERE ---
        // Setup canvas, context, fish objects, animation loop, etc.

    </script>

    <!-- Optional section for notes -->
    <!--
    <section id="notes">
        Developer notes here...
    </section>
    -->
</body>
</html>