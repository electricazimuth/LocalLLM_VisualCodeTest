You are an expert javascript and html coder.

# Vehicle Collision & Restart Simulation

**Goal:**
Create a simulation demonstrating object movement, boundary wrapping, collision detection, simple visual effects, and state management for restarting the simulation loop. Use HTML, JS, and CSS, adhering to best practices for animation and object handling.

**Task:**
Develop a simulation where several "Vehicles" move around the canvas. When vehicles go off one edge of the canvas, they should reappear on the opposite edge ("wrap"). If any two vehicles collide, trigger a visual "explosion" effect at the collision point. After the explosion animation completes, the entire simulation should reset and start again with a new set of vehicles.

**Requirements:**
1.  **Object Management:** Manage multiple `Vehicle` objects, likely stored in an array. Also, manage temporary `ExplosionParticle` objects when a collision occurs.
2.  **Initialization:** Start the simulation with a defined number of vehicles (e.g., 5-10). Assign each vehicle a random starting position within the canvas bounds and a random initial velocity (vx, vy).
3.  **Vehicle Representation:** Each `Vehicle` object should have:
    *   Position (x, y).
    *   Velocity (vx, vy).
    *   Size (width, height or radius for collision detection).
    *   A simple visual representation of a car or truck using simple rectangles and circles for wheels.
    *   An indicator of its active state (e.g., `isActive = true`).
4.  **Movement & Wrapping:**
    *   Update vehicle positions based on their velocity and delta time for smooth animation.
    *   Implement screen wrapping: If a vehicle's position goes beyond a canvas boundary (top, bottom, left, right), its position should be set to the opposite edge, maintaining its velocity.
5.  **Collision Detection:**
    *   Implement a method to detect collisions between any two active vehicles (e.g., rectangle intersection or distance check between circle centers).
    *   Optimize collision checks (e.g., avoid checking a vehicle against itself or checking pairs twice).
6.  **Collision Response & Explosion:**
    *   Upon detecting a collision between two vehicles:
        *   Mark the involved vehicles as inactive or remove them.
        *   Calculate the approximate collision point.
        *   Trigger an "explosion" effect: Create a burst of `ExplosionParticle` objects (e.g., 15-30) originating from the collision point.
        *   Show the "BOOM" text, maybe expanding at the viewer
        *   Explosion particles should have random outward velocities, a limited lifespan, and potentially fade out.
        *   Transition the simulation state to indicate an explosion is occurring.
        *   Wait for a few (3-5) seconds before restarting the simulation
7.  **Explosion Particles:**
    *   Each particle needs position, velocity, lifespan, size, and color.
    *   Particles should move based on velocity and delta time.
    *   Decrease lifespan over time. Remove particles when lifespan expires.
8.  **Simulation State & Restart:**
    *   Manage the overall state of the simulation (e.g., `RUNNING`, `EXPLODING`, `RESTARTING`).
    *   **`RUNNING` State:** Update vehicles, check for collisions. If collision occurs, switch to `EXPLODING`.
    *   **`EXPLODING` State:** Update and draw explosion particles. Do not update/draw vehicles. Check if all explosion particles have expired. If yes, switch to `RESTARTING`.
    *   **`RESTARTING` State:** Perform cleanup (clear any remaining objects), re-initialize the vehicles (new random positions/velocities), and switch the state back to `RUNNING`.
9.  **Animation Loop (`requestAnimationFrame`):**
    *   Use `requestAnimationFrame` for the main loop.
    *   Calculate and use delta time correctly.
    *   The loop's update and draw logic should depend on the current simulation state.
    *   **Update Logic:** Handle updates for vehicles OR explosion particles based on the state. Manage state transitions.
    *   **Draw Logic:** Clear the canvas. Draw active vehicles OR explosion particles based on the state.

**Visual Goal:**
The canvas shows several simple shapes moving across the screen, wrapping around the edges. When two shapes collide, they disappear and are replaced by a brief, expanding burst of smaller particles. Once the particles fade, the simulation resets, and new shapes appear and start moving again.

**Functional Requirements:**
*   The simulation must run autonomously after initialization.
*   Vehicles must wrap correctly around all four canvas edges.
*   Collision detection must reliably identify overlaps between vehicles.
*   The explosion effect must be visually distinct and temporary.
*   The simulation must cleanly restart after an explosion sequence concludes.
*   Animation must be smooth (correct delta time implementation).

**Desirable Features:**
*   Use Classes or factory functions for `Vehicle` and `ExplosionParticle`.
*   Implement efficient collision detection.
*   Add variety to vehicle appearance (color, shape) or speed.
*   Make the explosion particle behavior more visually interesting (e.g., add gravity, color changes).
*   Introduce a slight delay before the simulation restarts after an explosion.

# Deliverable
The simulation must run directly in a modern web browser using only plain JavaScript and the Canvas API (no external libraries). Provide the complete solution within a single HTML file, using the following boilerplate. You may add notes about your implementation approach within HTML comments or a dedicated `<section id="notes">` if desired.

```html
<!DOCTYPE html>
<html>
<head>
    <title>Vehicle Collision Simulation</title>
    <style>
        body { margin: 0; overflow: hidden; background-color: #333; } /* Dark background */
        canvas { display: block; margin: 20px auto; border: 1px solid #666; background-color: #000; } /* Black canvas */
    </style>
</head>
<body>
    <canvas id="simulationCanvas" width="512" height="512"></canvas>

    <script>
        // --- YOUR JAVASCRIPT CODE GOES HERE ---
        // Setup canvas, context, vehicle array, particle array, state variable,
        // initialization function, animation loop, etc.

        // Example state management hint:
        // let simulationState = 'RUNNING'; // Possible states: 'RUNNING', 'EXPLODING', 'RESTARTING'
        // let vehicles = [];
        // let explosionParticles = [];

    </script>

    <!-- Optional section for notes -->
    <!--
    <section id="notes">
        Developer notes regarding collision detection method, state management, design choices, etc.
    </section>
    -->
</body>
</html>