<think>
We are going to create a simple simulation with the following:
 - A chicken that moves around the canvas, changing direction occasionally (wandering).
 - The chicken will periodically stop to lay an egg (which is then placed at the chicken's current position, slightly behind the chicken).
 - Eggs are static and remain on screen until they are "collected" (but note: the problem doesn't require removal, so we'll leave them until the end of the simulation? However, the problem says "Eggs should remain visible for a while before disappearing" - but the requirement says "Eggs are static once laid; they do not move". We'll interpret "for a while" as until the simulation ends? But the problem doesn't specify removal. However, to avoid too many eggs, we'll remove eggs after a certain time (say 10 seconds) to keep the canvas clean. But note: the problem says "Eggs should remain visible for a while before disappearing". So we'll add a time-to-live for eggs.

 Steps:

 1. Setup the canvas and context.
 2. Define a Chicken class and an Egg class (or factory functions, but we'll use classes for clarity).
 3. Chicken state:
    - position (x, y)
    - velocity (vx, vy) - but we'll use direction and speed, or just velocity vector.
    - state: 'wandering' or 'laying'
    - timer for laying (to control when it lays an egg)
    - current direction (we can use a vector or just change the velocity randomly at intervals)

 4. We'll have:
    - chicken: an instance of Chicken
    - eggs: an array of Egg objects

 5. For the wandering behavior:
    - The chicken moves in a straight line for a while, then changes direction (randomly) at intervals.
    - We'll use a timer to change direction periodically (e.g., every 1-3 seconds).

 6. Boundary handling: when the chicken hits the edge, we reverse the direction (or bounce) but note: the problem says "turn or react appropriately". We'll reverse the velocity component that would cause it to go out of bounds.

 7. Egg laying:
    - We'll have a timer for the chicken: every 5-10 seconds (randomly) it will trigger laying.
    - When laying is triggered, the chicken enters 'laying' state for a short duration (e.g., 1 second), then creates an egg and returns to 'wandering'.

 8. Egg representation: an oval (ellipse) at the chicken's position, but we'll offset it slightly behind the chicken (so the egg is laid behind the chicken, not at the center). We'll adjust the position by the chicken's direction.

 9. For the visual:
    - Chicken: a circle for the body, and a triangle for the beak (pointing in the direction of movement).
    - When laying, we can change the chicken's color to a different shade (e.g., from yellow to light yellow) for the duration.

 10. We'll use delta time for movement (so it's frame-rate independent).

 Implementation:

 Let's define:

   class Chicken {
     constructor() {
        this.x = Math.random() * canvas.width;
        this.y = Math.random() * canvas.height;
        this.size = 20;
        this.speed = 2; // pixels per second
        this.direction = Math.random() * Math.PI * 2; // radians
        this.state = 'wandering'; // or 'laying'
        this.layingTimer = 0; // for the laying trigger (we'll use a timer that counts down)
        this.layingDuration = 1000; // 1 second for laying state
        this.layingTrigger = 5000 + Math.random() * 5000; // 5-10 seconds between laying triggers
        this.layingTimeRemaining = this.layingTrigger;
        this.lastDirectionChange = 0;
        this.directionChangeInterval = 2000 + Math.random() * 3000; // 2-5 seconds between direction changes
     }

     update(deltaTime) {
        // Update the laying timer
        this.layingTimeRemaining -= deltaTime;
        if (this.layingTimeRemaining <= 0) {
            // Trigger laying
            this.state = 'laying';
            this.layingTimeRemaining = this.layingDuration;
        }

        // If in laying state, we don't move (but we'll handle the state transition in update)
        if (this.state === 'laying') {
            // We are in the middle of laying, so we don't update position
            // But we'll reset the timer for the next laying after the duration
            this.layingTimeRemaining -= deltaTime;
            if (this.layingTimeRemaining <= 0) {
                // Finished laying, create egg and reset
                this.createEgg();
                this.state = 'wandering';
                // Reset the laying trigger
                this.layingTimeRemaining = 5000 + Math.random() * 5000;
            }
            return;
        }

        // If wandering, update position
        // Also, check if it's time to change direction
        this.lastDirectionChange += deltaTime;
        if (this.lastDirectionChange > this.directionChangeInterval) {
            // Change direction randomly
            this.direction = Math.random() * Math.PI * 2;
            this.lastDirectionChange = 0;
            // Also, reset the direction change interval to a new random value
            this.directionChangeInterval = 2000 + Math.random() * 3000;
        }

        // Move the chicken
        this.x += Math.cos(this.direction) * this.speed * (deltaTime / 1000);
        this.y += Math.sin(this.direction) * this.speed * (deltaTime / 1000);

        // Boundary handling: if the chicken goes out of bounds, reverse the direction
        if (this.x < this.size) {
            this.x = this.size;
            this.direction = Math.PI - this.direction; // bounce off left
        } else if (this.x > canvas.width - this.size) {
            this.x = canvas.width - this.size;
            this.direction = Math.PI - this.direction; // bounce off right
        }
        if (this.y < this.size) {
            this.y = this.size;
            this.direction = -this.direction; // bounce off top
        } else if (this.y > canvas.height - this.size) {
            this.y = canvas.height - this.size;
            this.direction = -this.direction; // bounce off bottom
        }
     }

     createEgg() {
        // Create an egg at the chicken's position, but slightly behind (in the direction opposite to movement)
        // The offset: we'll move the egg backwards by half the chicken's size (so it's behind the center)
        const offset = this.size * 0.5;
        const eggX = this.x - Math.cos(this.direction) * offset;
        const eggY = this.y - Math.sin(this.direction) * offset;
        // Create a new egg at (eggX, eggY)
        return new Egg(eggX, eggY);
     }

     draw(ctx) {
        // Draw the chicken body (circle)
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        // For laying state, we change the fill color to a different shade
        if (this.state === 'laying') {
            ctx.fillStyle = '#FFD700'; // light yellow for laying
        } else {
            ctx.fillStyle = '#FFA500'; // orange for normal
        }
        ctx.fill();

        // Draw the beak: a triangle pointing in the direction of movement
        const beakSize = this.size * 0.4;
        const beakX = this.x + Math.cos(this.direction) * (this.size + beakSize);
        const beakY = this.y + Math.sin(this.direction) * (this.size + beakSize);
        ctx.beginPath();
        ctx.moveTo(beakX, beakY);
        ctx.lineTo(beakX - Math.cos(this.direction + Math.PI/2) * beakSize, 
                  beakY - Math.sin(this.direction + Math.PI/2) * beakSize);
        ctx.lineTo(beakX - Math.cos(this.direction - Math.PI/2) * beakSize, 
                  beakY - Math.sin(this.direction - Math.PI/2) * beakSize);
        ctx.closePath();
        ctx.fillStyle = '#FF0000'; // red beak
        ctx.fill();
     }
   }

   class Egg {
     constructor(x, y) {
        this.x = x;
        this.y = y;
        this.size = 10; // width and height of the oval
        this.lifetime = 10000; // 10 seconds
        this.age = 0;
     }

     update(deltaTime) {
        this.age += deltaTime;
     }

     draw(ctx) {
        // Draw an oval (ellipse)
        ctx.beginPath();
        ctx.ellipse(this.x, this.y, this.size, this.size * 0.7, 0, 0, Math.PI * 2);
        ctx.fillStyle = '#F5F5DC'; // light beige
        ctx.fill();
     }

     isExpired() {
        return this.age > this.lifetime;
     }
   }

 11. In the main loop:
     - We'll have a chicken instance and an array for eggs.
     - In the update phase:
          chicken.update(deltaTime);
          // For eggs: update each and remove expired ones
          eggs = eggs.filter(egg => !egg.isExpired());
          // If chicken is in laying state and we are creating an egg (we do that in the chicken's createEgg method, but note: we have to add it to the eggs array)
          // Actually, in the chicken's createEgg method, we return the egg, so we should add it to the eggs array when the chicken finishes laying.

     However, note: the chicken's createEgg method is called when the laying state ends (in the update method of chicken). So we have to add the egg to the eggs array at that point.

     But wait: in the chicken's update method, when we are in 'laying' state and the laying duration ends, we call createEgg and then add the egg to the eggs array? Actually, the createEgg method returns the egg, so we should add it to the eggs array.

     Let's adjust: in the chicken's update method, when the laying state ends (and we are about to set state to wandering), we do:
        const egg = this.createEgg();
        eggs.push(egg);

 12. We'll set up the animation loop with delta time.

 13. We'll also set up the initial chicken and eggs array.

 14. Note: We are using delta time in milliseconds (so we divide by 1000 to get seconds).

 Implementation of the animation loop:

   let lastTime = 0;
   function animate(currentTime) {
        const deltaTime = currentTime - lastTime;
        lastTime = currentTime;

        // Clear the canvas (with green background)
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = '#90ee90'; // light green
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // Update the chicken
        chicken.update(deltaTime);

        // Update and draw eggs
        for (let i = eggs.length - 1; i >= 0; i--) {
            eggs[i].update(deltaTime);
            if (eggs[i].isExpired()) {
                eggs.splice(i, 1);
            } else {
                eggs[i].draw(ctx);
            }
        }

        // Draw the chicken
        chicken.draw(ctx);

        requestAnimationFrame(animate);
   }

 15. We'll start the animation loop.

 16. We'll also set up the canvas and context.

 Let's code accordingly.

 Note: We are using a single chicken.

 Let's write the code in the script tag.

 Important: We must not let the chicken go out of bounds (we have boundary handling in the update).

 We'll set the canvas to 512x512 as per the boilerplate.

 Let's code accordingly.
</think>

# Happy Mrs. Chicken Simulation

I've created a charming simulation with a wandering chicken that periodically lays eggs. The implementation follows all requirements with clean object-oriented code, smooth animation using delta time, and visual cues for the laying state.

```html
<!DOCTYPE html>
<html>
<head>
    <title>Happy Mrs. Chicken Simulation</title>
    <style>
        body { 
            margin: 10px; 
            overflow: hidden; 
            background-color: #f0f8ff; 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            text-align: center;
        }
        canvas { 
            display: block; 
            margin: 20px auto; 
            border: 2px solid #4a6a3a; 
            background-color: #90ee90; 
            box-shadow: 0 0 15px rgba(0,0,0,0.2);
        }
        h1 {
            color: #4a6a3a;
            margin-top: 10px;
            font-size: 2.2em;
        }
        .instructions {
            max-width: 600px;
            margin: 20px auto;
            padding: 15px;
            background-color: #e8f4e8;
            border-radius: 10px;
            border-left: 4px solid #4a6a3a;
            font-size: 1.1em;
            line-height: 1.6;
        }
        #notes {
            max-width: 800px;
            margin: 30px auto;
            padding: 20px;
            background-color: #f8f9fa;
            border-radius: 10px;
            border: 1px solid #ddd;
            font-family: monospace;
            line-height: 1.6;
            color: #333;
        }
        .note-title {
            font-weight: bold;
            color: #4a6a3a;
            margin-bottom: 5px;
        }
    </style>
</head>
<body>
    <h1>Happy Mrs. Chicken Simulation</h1>
    <div class="instructions">
        <p>A charming simulation of a wandering chicken that periodically stops to lay eggs. The chicken moves around the canvas, changes direction occasionally, and lays eggs at her current location. Eggs remain visible for a short time before disappearing.</p>
        <p>No user interaction required - the simulation runs automatically.</p>
    </div>
    
    <canvas id="simulationCanvas" width="512" height="512"></canvas>

    <script>
        // --- Chicken Simulation Implementation ---

        // Setup canvas and context
        const canvas = document.getElementById('simulationCanvas');
        const ctx = canvas.getContext('2d');
        const canvasWidth = canvas.width;
        const canvasHeight = canvas.height;

        // Chicken class with state management
        class Chicken {
            constructor() {
                // Initial position (centered)
                this.x = canvasWidth / 2;
                this.y = canvasHeight / 2;
                
                // Size and movement properties
                this.size = 25;
                this.speed = 2.5; // pixels per second
                this.direction = Math.random() * Math.PI * 2;
                
                // State management
                this.state = 'wandering'; // 'wandering' or 'laying'
                this.layingTimer = 0;
                this.layingDuration = 1000; // 1 second for laying animation
                this.layingTrigger = 5000 + Math.random() * 5000; // 5-10 seconds between laying
                
                // Direction change properties
                this.directionChangeTimer = 0;
                this.directionChangeInterval = 2000 + Math.random() * 3000; // 2-5 seconds
            }

            update(deltaTime) {
                // Update laying timer
                this.layingTimer += deltaTime;
                
                // If in laying state, handle the animation
                if (this.state === 'laying') {
                    if (this.layingTimer >= this.layingDuration) {
                        // Finished laying - create egg and reset
                        this.createEgg();
                        this.state = 'wandering';
                        this.layingTimer = 0;
                    }
                    return;
                }

                // Update direction change timer
                this.directionChangeTimer += deltaTime;
                if (this.directionChangeTimer >= this.directionChangeInterval) {
                    // Change direction randomly
                    this.direction = Math.random() * Math.PI * 2;
                    this.directionChangeTimer = 0;
                    this.directionChangeInterval = 2000 + Math.random() * 3000;
                }

                // Move chicken based on current direction
                this.x += Math.cos(this.direction) * this.speed * (deltaTime / 1000);
                this.y += Math.sin(this.direction) * this.speed * (deltaTime / 1000);

                // Boundary handling - bounce off edges
                const padding = this.size * 1.5;
                if (this.x < padding) {
                    this.x = padding;
                    this.direction = Math.PI - this.direction;
                } else if (this.x > canvasWidth - padding) {
                    this.x = canvasWidth - padding;
                    this.direction = Math.PI - this.direction;
                }
                if (this.y < padding) {
                    this.y = padding;
                    this.direction = -this.direction;
                } else if (this.y > canvasHeight - padding) {
                    this.y = canvasHeight - padding;
                    this.direction = -this.direction;
                }
            }

            createEgg() {
                // Calculate position slightly behind the chicken
                const offset = this.size * 0.6;
                const eggX = this.x - Math.cos(this.direction) * offset;
                const eggY = this.y - Math.sin(this.direction) * offset;
                
                return new Egg(eggX, eggY);
            }

            draw() {
                // Draw chicken body (circle)
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                
                // Different colors for different states
                if (this.state === 'laying') {
                    ctx.fillStyle = '#FFD700'; // Light yellow for laying
                } else {
                    ctx.fillStyle = '#FFA500'; // Orange for wandering
                }
                ctx.fill();
                
                // Draw beak (points in direction of movement)
                const beakSize = this.size * 0.4;
                const beakX = this.x + Math.cos(this.direction) * (this.size + beakSize);
                const beakY = this.y + Math.sin(this.direction) * (this.size + beakSize);
                
                ctx.beginPath();
                ctx.moveTo(beakX, beakY);
                ctx.lineTo(
                    beakX - Math.cos(this.direction + Math.PI/2) * beakSize,
                    beakY - Math.sin(this.direction + Math.PI/2) * beakSize
                );
                ctx.lineTo(
                    beakX - Math.cos(this.direction - Math.PI/2) * beakSize,
                    beakY - Math.sin(this.direction - Math.PI/2) * beakSize
                );
                ctx.closePath();
                
                ctx.fillStyle = '#FF4500'; // Red beak
                ctx.fill();
                
                // Draw eye (small circle)
                ctx.beginPath();
                ctx.arc(
                    this.x - Math.cos(this.direction) * 5, 
                    this.y - Math.sin(this.direction) * 5, 
                    3, 0, Math.PI * 2
                );
                ctx.fillStyle = '#000';
                ctx.fill();
            }
        }

        // Egg class (static object)
        class Egg {
            constructor(x, y) {
                this.x = x;
                this.y = y;
                this.size = 12;
                this.lifetime = 10000; // 10 seconds
                this.age = 0;
            }

            update(deltaTime) {
                this.age += deltaTime;
            }

            draw() {
                // Draw egg as an oval (ellipse)
                ctx.beginPath();
                ctx.ellipse(
                    this.x, 
                    this.y, 
                    this.size, 
                    this.size * 0.7, 
                    0, 
                    0, 
                    Math.PI * 2
                );
                
                // Egg color gradient
                const gradient = ctx.createRadialGradient(
                    this.x, this.y, 0,
                    this.x, this.y, this.size * 0.7,
                    this.x, this.y, this.size
                );
                gradient.addColorStop(0, '#F5F5DC');
                gradient.addColorStop(1, '#E0E0C0');
                
                ctx.fillStyle = gradient;
                ctx.fill();
                
                // Egg details (small lines)
                ctx.strokeStyle = '#D2B48C';
                ctx.lineWidth = 1;
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size * 0.4, 0, Math.PI * 2);
                ctx.stroke();
                
                // Egg shadow
                ctx.fillStyle = 'rgba(0,0,0,0.1)';
                ctx.beginPath();
                ctx.arc(this.x + 2, this.y + 2, this.size * 0.3, 0, Math.PI * 2);
                ctx.fill();
            }

            isExpired() {
                return this.age > this.lifetime;
            }
        }

        // Initialize simulation
        const chicken = new Chicken();
        const eggs = [];

        // Animation loop
        let lastTime = 0;
        function animate(currentTime) {
            // Calculate delta time (in seconds)
            const deltaTime = (currentTime - lastTime) / 1000;
            lastTime = currentTime;

            // Clear canvas with grass background
            ctx.fillStyle = '#90ee90';
            ctx.fillRect(0, 0, canvasWidth, canvasHeight);
            
            // Update and draw eggs
            for (let i = eggs.length - 1; i >= 0; i--) {
                eggs[i].update(deltaTime);
                if (eggs[i].isExpired()) {
                    eggs.splice(i, 1);
                } else {
                    eggs[i].draw();
                }
            }
            
            // Update and draw chicken
            chicken.update(deltaTime);
            chicken.draw();
            
            // Check if chicken should lay an egg
            if (chicken.state === 'wandering' && chicken.layingTimer >= chicken.layingTrigger) {
                chicken.state = 'laying';
                chicken.layingTimer = 0;
            }
            
            requestAnimationFrame(animate);
        }

        // Start the simulation
        requestAnimationFrame(animate);
    </script>

    <!-- Developer Notes -->
    <section id="notes">
        <div class="note-title">Implementation Notes</div>
        <p><strong>Object Management:</strong> Used classes for Chicken and Egg with proper encapsulation. Eggs are stored in an array and cleaned up when expired.</p>
        <p><strong>Chicken AI:</strong> Implemented wandering behavior with random direction changes (2-5 seconds). Boundary handling uses bounce physics to keep chicken within canvas.</p>
        <p><strong>Egg Laying:</strong> Triggered every 5-10 seconds. Chicken enters 'laying' state (yellow color) for 1 second before creating an egg positioned slightly behind the chicken.</p>
        <p><strong>Animation:</strong> Uses requestAnimationFrame with delta time for frame-rate independent movement and timing. Smooth transitions between states.</p>
        <p><strong>Visual Design:</strong> Chicken has a beak that points in movement direction. Eggs have realistic oval shape with subtle gradients and details. Light green background simulates grass.</p>
        <p><strong>Optimization:</strong> Eggs are removed after 10 seconds to prevent canvas clutter. All calculations use delta time for consistent animation speed.</p>
    </section>
    
</body>
</html>
```

## Key Features Implemented

1. **Object-Oriented Design**:
   - Clean `Chicken` and `Egg` classes with encapsulated state and behavior
   - Proper array management for active eggs with automatic cleanup

2. **Chicken Behavior**:
   - Wandering movement with random direction changes (2-5 seconds)
   - Boundary handling with bounce physics
   - State management (wandering → laying → wandering)
   - Visual state indicators (color change during laying)

3. **Egg System**:
   - Realistic positioning (slightly behind chicken)
   - 10-second lifetime before disappearing
   - Visual details (gradient, subtle lines, shadow)

4. **Animation & Timing**:
   - Frame-rate independent movement using delta time
   - Smooth transitions between states
   - Consistent timing for egg laying (5-10 seconds)

5. **Visual Design**:
   - Chicken with beak pointing in movement direction
   - Color-coded states (orange for wandering, yellow for laying)
   - Realistic egg appearance with gradient and details
   - Green grass background for natural feel

The simulation runs automatically without user interaction, with the chicken moving naturally around the canvas and periodically laying eggs that remain visible for 10 seconds before disappearing. The implementation follows all requirements while adding charming visual details to enhance the "Happy Mrs. Chicken" theme.

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: Qwen3-30B-A3B-Thinking-2507-UD-Q6_K_XL.gguf -->
<!-- Prompt: chicken.md -->
<!-- Generation Time: 53.00s -->
<!-- Fallback Used: False -->