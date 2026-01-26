You are an expert javascript and html coder.

# Happy Mrs. Chicken Simulation Challenge

**Goal:**
Create a charming visual simulation inspired by the character "Happy Mrs. Chicken" using HTML, JS, and CSS. The focus is on implementing simple game AI for movement and state-driven actions (laying eggs), alongside good practices for object management and animation within the Canvas API.

**Task:**
Develop a simulation where a single "Chicken" character moves around the canvas based on simple game AI rules. The chicken should periodically pause its movement to "lay" an "Egg" object, which remains on screen.

**Requirements:**
1.  **Object Management:** Define and manage JavaScript objects for the `Chicken` and any active `Egg` entities. Use an appropriate structure (e.g., an array) to keep track of the eggs currently on screen.
2.  **Chicken Character:**
    *   Represent the chicken with a simple visual shape (e.g., circle, polygon, or combination), make sure it has a beak.
    *   Implement its state, including at least: Position (x, y), Velocity/Direction, and potentially a state indicator (e.g., 'wandering', 'laying').
    *   Needs a mechanism (like an internal timer or probability check) to trigger the egg-laying action periodically.
3.  **Egg Objects:**
    *   Represent eggs with a simple visual shape (e.g., oval).
    *   Each egg needs a Position (where it was laid).
    *   Eggs are static once laid; they do not move.
4.  **Simple Game AI & Behavior:**
    *   Implement a "wandering" behavior for the chicken's movement. It should change direction occasionally to simulate non-linear paths.
    *   Boundary Handling: The chicken must stay within the canvas area. Implement logic for it to turn or react appropriately when reaching an edge.
    *   Egg Laying Action: When the trigger condition is met, the chicken should:
        *   Briefly pause or change its visual state to indicate laying.
        *   Create a new `Egg` object at its current location.
        *   Add the new egg to the collection of active eggs.
        *   Resume its wandering behavior after a short delay.
5.  **Simulation Loop (`requestAnimationFrame`):**
    *   Use `requestAnimationFrame` for the main animation loop.
    *   Calculate and utilize delta time for smooth, frame-rate independent movement, timing an egg laying timer, and state transitions.
    *   **Update Logic:**
        *   Update the chicken's state (check egg-laying timer/condition).
        *   Update the chicken's position based on its current state and movement/boundary logic.
        *   If the chicken lays an egg, create and store the new `Egg` object.
    *   **Draw Logic:**
        *   Clear the canvas (a green background might be suitable).
        *   Draw the chicken based on its current position and state.
        *   Draw all eggs at their positions.

**Visual Goal:**
The canvas should show a single chicken character moving around within the boundaries. Periodically, it should stop briefly, leaving behind an egg shape. Eggs should remain visible for a while before disappearing. The overall effect should be a simple, continuous character simulation.

**Functional Requirements:**
*   The simulation must run without requiring user interaction after starting.
*   The chicken character must remain fully within the canvas bounds at all times.
*   Animation and timing should be smooth and consistent (correct delta time usage).
*   Eggs should appear at the chicken's location when laid and stay on screen.

**Desirable Features:**
*   Use a Class or factory function for the `Chicken` and `Egg` objects.
*   Orient the chicken's visual representation to face its direction of movement.
*   Implement slightly more varied wandering behavior (e.g., occasional longer pauses, variable speed).
*   Add a visual cue when the chicken is in the 'laying' state (e.g., slight color change, brief animation).
*   Ensure the egg appears slightly behind the chicken's center, appropriate to where an egg would realistically be laid.

# Deliverable
The simulation must run directly in a modern web browser using only plain JavaScript and the Canvas API (no external libraries). Provide the complete solution within a single HTML file, using the following boilerplate. You may add notes about your implementation approach within HTML comments or a dedicated `<section id="notes">` if desired.

```html
<!DOCTYPE html>
<html>
<head>
    <title>Chicken Simulation</title>
    <style>
        body { margin: 10px; overflow: hidden; background-color: #eee; }
        canvas { display: block; margin: 20px auto; border: 1px solid #999; background-color: #90ee90; } /* Light green grass background */
    </style>
</head>
<body>
    <canvas id="simulationCanvas" width="512" height="512"></canvas>

    <script>
        // --- YOUR JAVASCRIPT CODE GOES HERE ---
        // Setup canvas, context, chicken object, egg array, animation loop, etc.

    </script>

    <!-- Optional section for notes -->
    
    <section id="notes">
        Developer notes regarding the simulation logic, AI choices, etc.
    </section>
    
</body>
</html>
```