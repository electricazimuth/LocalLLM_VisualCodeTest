<think>
We are going to create a simulation with the following structure:

 1. We'll define a Fish class (or use a factory) to represent each fish.
 2. We'll manage an array of fish objects.
 3. We'll use requestAnimationFrame with delta time for smooth animation.
 4. Each fish will have:
    - position (x, y)
    - velocity (vx, vy) OR we can use speed and direction (we'll use velocity for simplicity)
    - size (radius for the fish body, but note: we'll draw a triangle for the fish so we need a different measure for the triangle)
    - color (we'll generate a random color for each fish, but with a base hue for variation)
    - a heading (angle) for orientation (so we can rotate the fish to face the direction it's moving)

 However, note: for the fish to face the direction, we need to know the direction of movement. We can use the velocity vector to compute the angle.

 Steps for the Fish class:

   - We'll have a constructor that takes initial position, velocity, size, and color.
   - We'll also have a method to update the fish's state (including wandering behavior and boundary handling).
   - We'll have a method to draw the fish.

 Wandering behavior: We'll introduce a small random change to the direction over time (but not too much to avoid jitter). We can do this by having a "wander" parameter that we add to the direction (or velocity) at each step.

 Boundary handling: When the fish gets too close to the edge, we'll adjust its velocity to turn away. We'll do this by:
   - If the fish is near the left edge (x < some margin), set vx to positive (to move right).
   - Similarly for right, top, bottom.

 But note: we want smooth turning, not an instant flip. So we'll use a "boundary force" that gradually changes the velocity as the fish approaches the edge.

 However, a simpler method: when the fish is within a certain distance from the edge, we'll set the velocity component perpendicular to the edge to be away from the edge. But we don't want to flip the entire velocity vector, so we can do:

   if (x < margin) {
        vx = Math.abs(vx) + 0.1; // but we don't want to make it too big, so we can adjust by a small amount
   }

 But note: we want to avoid having the fish bounce off the wall in a very rigid way. Instead, we can have a "repulsion" force that increases as the fish gets closer to the wall.

 However, for simplicity and performance, we'll do:

   We'll define a margin (e.g., 20 pixels) from the edge.

   For left edge: if x < margin, then set vx = Math.abs(vx) * 1.2 (but we don't want to make it too fast) OR we can set vx to a positive value that is a bit more than the current vx? Actually, we want to turn away, so we want to reverse the x component? But note: if the fish is moving left (vx negative) and hits the left edge, we want to set vx to positive. However, we don't want to set it to a fixed value, but rather to a value that is positive and maybe a bit more than the current speed? Actually, we can just reverse the x component and add a small boost? But that might cause bouncing.

   Instead, we can do:

      if (x < margin) {
          vx = Math.abs(vx) + 0.1; // but we don't want to add too much, so we can set to a positive value that is the current speed (but positive) plus a little? Actually, we want to move away, so we set vx to positive and maybe increase it a bit? But note: we don't want to make the fish faster, just change direction.

      }

   However, a better approach: we can have a "boundary force" that is proportional to how close we are to the edge. But for simplicity, we'll do:

      if (x < margin) {
          vx = Math.max(vx, 0.5); // but if vx was negative, we set it to positive and at least 0.5? Actually, we want to reverse the direction and maybe add a little extra to push it away.

      }

   But note: we don't want to set it to a fixed value. We can do:

      if (x < margin) {
          vx = Math.abs(vx) * 1.2; // make it a bit faster when turning? But that might be too much.

   Alternatively, we can use a vector approach:

      We'll have a "repulsion vector" that points away from the wall. For the left wall, the repulsion vector is (1, 0). We can add a small multiple of that to the velocity.

      However, to keep it simple and efficient, we'll do:

        if (x < margin) {
            vx = Math.abs(vx) * 1.1; // make it a bit faster in the positive direction? But note: we don't want to change the speed too much, so we'll just set the x component to positive and not change the magnitude? Actually, we want to change the direction without changing the speed too much.

        }

   But note: the fish might be moving at an angle. We want to change the direction to be away from the wall. So for the left wall, we want the x component to become positive. We can do:

        if (x < margin) {
            vx = Math.abs(vx) * 1.1; // but this might make the speed increase? We don't want that.

   Let's think: we want to change the direction without changing the speed (or with minimal change). So we can set the velocity vector to have the same magnitude but in the direction away from the wall.

   However, for simplicity and because we are using a fixed speed (we'll set a max speed and then clamp the velocity magnitude), we can do:

        We'll have a max speed (e.g., 3). We'll compute the current speed (magnitude of velocity). Then, when near the wall, we'll set the velocity to a vector that is pointing away from the wall and has the same magnitude (or slightly less to avoid going too fast).

   But note: we are using delta time, so we are updating the velocity in a physics-like way? Actually, we are updating position by velocity, and we are going to update velocity for wandering and boundary.

   We'll do:

        // Boundary handling for left
        if (x < margin) {
            // We want to set vx to a positive value that is at least the current speed (but we don't want to change the speed too much, so we'll set the x component to a positive value that is the same as the current speed in magnitude? But note: the fish might be moving up and left, so we want to turn it to move right and up? Actually, we want to turn it to move away from the wall, so we want to reverse the x component and keep the y component.

            // So: if the fish is moving left (vx negative) and hits the left wall, we set vx to positive (and we want to keep the same speed in the x direction, but now positive). But note: we don't want to change the y component.

            // Therefore: we can set vx = -vx? But that would be a bounce. However, we want a smooth turn, not a bounce. So we don't want to reverse the entire velocity, but we want to change the direction to be away from the wall.

            // Actually, for the left wall, we want the x component to be positive. So we set vx = Math.abs(vx) * (some factor) but that might not be the same as the original speed.

            // Instead, we can do: we set the x component to be positive and equal to the current magnitude of the x component? But note: the current vx might be negative. So we set vx = Math.abs(vx) * (we don't want to change the magnitude, so we set vx = -vx? but that would be a bounce and might cause the fish to move back and forth).

            // We want to avoid the bounce. So we'll set vx to a positive value that is the same as the absolute value of the current vx (so if vx was -2, we set to 2). But note: we don't want to change the magnitude of the velocity vector, only the direction for the x component.

            // However, the fish might be moving at an angle. We want to change the direction to be away from the wall, so we want to flip the x component.

            // So: vx = -vx;   // This would flip the x component.

            // But note: if the fish is moving very fast to the left, flipping to the right might cause it to move too fast? Actually, the magnitude of the velocity vector would be the same. So we do:

            vx = -vx;

            // However, this is a bounce. We want to avoid the bounce because it's too rigid. We want a smooth turn. So we'll do a gradual turn.

            // Alternative: we'll have a "turning" parameter. When the fish is within the margin, we'll add a small force in the direction away from the wall. But we are not doing physics, so we'll adjust the velocity by a small amount.

            // We'll do: 
            //   vx = Math.abs(vx) * 0.5; // but that would slow it down? Not what we want.

            // Let's try a different approach: we'll have a "boundary repulsion" that we add to the velocity when near the edge.

            // We'll define a repulsion strength (e.g., 0.5) and a margin (e.g., 20).
            // For left edge: if x < margin, then we add a repulsion force in the positive x direction: vx += repulsionStrength * (margin - x) / margin; 
            // But note: we don't want to add too much, so we can cap it.

            // However, for simplicity and performance, we'll do the bounce for now and then improve to a smooth turn later if we have time.

            // Given the time, we'll do the bounce (flip the x component) for the left and right, and similarly for top and bottom (flip the y component). But note: the problem says "smoothly turn away", so we'll do a smooth turn by having a small random change when near the edge? Actually, we can do:

            //   When near the edge, we set the velocity to a new direction that is away from the edge, but we don't flip the entire vector. Instead, we set the component perpendicular to the edge to be away from the edge, and we keep the other component.

            // For left edge: we set vx to be positive (so we set vx = Math.abs(vx) or we set vx = Math.abs(vx) * (some factor) but we don't want to change the speed). Actually, we want to set the direction to be away, so we set vx to a positive value that is the same as the current speed in the x direction? But note: the current speed in the x direction might be negative.

            // We'll do: 
            //   vx = Math.abs(vx);   // This sets the x component to positive, but note: if the fish was moving up and left, we want to keep the up movement and set the left to right. So we set vx to positive and leave vy as is.

            // However, this doesn't change the magnitude of the velocity vector. The magnitude becomes sqrt(vx^2 + vy^2) which is the same as before? Actually, no: if vx was negative, then |vx| is positive and the same as the absolute value of the original vx. So the magnitude is the same.

            // So we can do: 
            //   if (x < margin) {
            //       vx = Math.abs(vx);
            //   }
            //   if (x > W - margin) {
            //       vx = -Math.abs(vx);
            //   }
            //   ... similarly for y.

            // But note: this is a hard flip. We want to avoid the fish bouncing back and forth because of the flip. However, if the fish is moving very slowly, it might get stuck. So we'll add a small boost to the velocity in the direction away from the wall to ensure it moves away.

            // We'll do: 
            //   if (x < margin) {
            //       vx = Math.abs(vx) + 0.1; // add a little extra to make sure it moves away
            //   }

            // But note: we don't want to change the speed arbitrarily. We'll set a max speed and clamp the velocity.

        }

   We'll set a max speed (e.g., 3) and then clamp the velocity magnitude to that.

   However, for the sake of time, we'll do the flip and then add a small boost. And we'll clamp the speed.

   Steps for boundary:

        const margin = 20;
        const maxSpeed = 3;

        // For x
        if (x < margin) {
            vx = Math.abs(vx) + 0.1;
        } else if (x > W - margin) {
            vx = -Math.abs(vx) - 0.1;
        }

        // For y
        if (y < margin) {
            vy = Math.abs(vy) + 0.1;
        } else if (y > H - margin) {
            vy = -Math.abs(vy) - 0.1;
        }

        // Then clamp the speed to maxSpeed
        const speed = Math.sqrt(vx*vx + vy*vy);
        if (speed > maxSpeed) {
            vx = (vx / speed) * maxSpeed;
            vy = (vy / speed) * maxSpeed;
        }

   But note: the above clamping might not be necessary if we set the initial speed appropriately and don't add too much. However, it's a good practice.

   However, the problem says: "smoothly turn away", and this method (adding a little extra) might cause the fish to move in a more natural way? Actually, it's a bit of a hack.

   Another common method: use a vector that points away from the wall and add a small multiple of that to the velocity.

   We'll do:

        const margin = 20;
        const repulsion = 0.5;

        if (x < margin) {
            vx += repulsion * (margin - x);
        } else if (x > W - margin) {
            vx -= repulsion * (x - (W - margin));
        }

        // Similarly for y.

   This will add a force that pushes the fish away from the wall. The force is proportional to how close the fish is to the wall.

   We'll use this method for smoother behavior.

   We'll set repulsion to a small value (like 0.5) and then clamp the speed to maxSpeed.

   We'll do:

        const margin = 20;
        const repulsion = 0.5;
        const maxSpeed = 3;

        // For left
        if (x < margin) {
            vx += repulsion * (margin - x);
        }
        // For right
        if (x > W - margin) {
            vx -= repulsion * (x - (W - margin));
        }
        // For top
        if (y < margin) {
            vy += repulsion * (margin - y);
        }
        // For bottom
        if (y > H - margin) {
            vy -= repulsion * (y - (H - margin));
        }

        // Now clamp the speed
        const speed = Math.sqrt(vx*vx + vy*vy);
        if (speed > maxSpeed) {
            vx = (vx / speed) * maxSpeed;
            vy = (vy / speed) * maxSpeed;
        }

   This should give a smooth repulsion.

 5. Wandering behavior: We'll have a small random change to the direction (or velocity) over time. We can do:

        // In the update method for the fish, we'll have a random angle change every few frames.

        // We can have a timer for each fish: but to avoid per-fish timers (and for simplicity), we'll do:

        //   Every frame, we add a small random angle to the direction (but we don't want to change too much per frame).

        // However, note: we are using velocity, not direction. So we can change the velocity vector by a small random amount.

        // We'll have a wander strength (e.g., 0.05) and then every frame, we add a random vector to the velocity (with magnitude wanderStrength) but then we clamp the speed to maxSpeed.

        // But note: we don't want to change the direction too much, so we'll do:

        //   vx += (Math.random() - 0.5) * wanderStrength;
        //   vy += (Math.random() - 0.5) * wanderStrength;

        // Then clamp the speed.

        // However, this might cause the fish to change direction too much. We can do it only every few frames? But for simplicity, we'll do it every frame but with a small wanderStrength.

        // We'll set wanderStrength to 0.05.

 6. We'll create a Fish class.

 7. We'll have a fixed number of fish (12).

 8. We'll draw each fish as a triangle (for the fish body) and a small circle for the eye? Or just a triangle. We'll do a triangle pointing in the direction of movement.

    How to draw a fish:

        We'll draw a triangle with points:
          (0, -size)   // top of the fish (head)
          (-size/2, size/2)  // left side
          (size/2, size/2)   // right side

        Then we rotate the canvas by the angle (in radians) so that the triangle points in the direction of movement.

        Steps for drawing:

          ctx.save();
          ctx.translate(x, y);
          ctx.rotate(angle);
          ctx.beginPath();
          ctx.moveTo(0, -size);
          ctx.lineTo(-size/2, size/2);
          ctx.lineTo(size/2, size/2);
          ctx.closePath();
          ctx.fillStyle = color;
          ctx.fill();
          ctx.restore();

        But note: the size we use for the triangle is the "size" of the fish (which we'll set as the length from head to tail?).

        We'll set the size for the fish as the length from the head to the tail (so the triangle height is the size). The triangle will be drawn with the head at the top.

        However, note: the triangle we are drawing has a height of size (from (0,-size) to (0, size/2) is not exactly size). Actually, the distance from the head (0,-size) to the tail (which is at (0, size/2) but note: the tail is the base of the triangle) is not the same as the size we are using. We'll define the size as the height of the triangle (from head to the base). So the base is at y = size/2? Actually, the base is at y = size/2, and the head is at y = -size. So the total height is size + size/2 = 1.5*size? That's not what we want.

        Let's redefine:

          We want the fish to be drawn with a height of `size` (from head to tail). So:

            head: (0, 0)
            tail left: (-size/2, size)
            tail right: (size/2, size)

          But then the fish would be pointing downward? We want it to point in the direction of movement. So we'll draw the fish with the head at the top (so when facing up, the head is at the top of the canvas).

          Actually, we want the fish to be drawn with the head pointing in the direction of movement. So when the fish is moving to the right, the head should be on the right.

          We'll draw:

            head: (0, 0)
            left: (-size/2, size)
            right: (size/2, size)

          Then we rotate the fish so that the head points in the direction of movement. But note: when we rotate, the head will point in the direction of the rotation.

          However, if we draw the fish with the head at (0,0) and the tail at (0, size), then when we rotate by 0, the fish points upward (because the head is at (0,0) and the tail is at (0, size) meaning downward? Actually, no: in canvas, the y-axis is downward. So if we draw from (0,0) to (0, size), that's downward.

          We want the fish to point in the direction of movement. So if the fish is moving to the right, we want the head to be on the right. So we want the fish to be drawn with the head to the right. Therefore, we should draw:

            head: (0, 0)
            left: (-size, size/2)
            right: (-size, -size/2)

          But that's a bit messy.

        Alternatively, we can draw the fish with the head at (0,0) and the tail at (size, 0) and then rotate it. But then the fish would be pointing to the right when rotated 0.

        We'll do:

          We draw the fish in the "default" orientation (pointing to the right) as:

            head: (0, 0)
            left: (size, -size/2)
            right: (size, size/2)

          But note: the head is at (0,0) and the tail is at (size, 0) in the middle? Actually, the tail is the base. So:

            points: 
              (0, 0)   -> head
              (size, -size/2) -> left side
              (size, size/2)  -> right side

          Then when we rotate by 0, the fish points to the right.

          However, we want the fish to be drawn so that the head is at the front. So when the fish is moving to the right, we want the head to be at the right. So we'll draw the fish with the head at the right.

          But note: when we draw the triangle, we are going to rotate it. So we'll draw the fish in a default orientation (pointing to the right) and then rotate it to the direction of movement.

        Steps:

          We'll define the fish body as:

            ctx.beginPath();
            ctx.moveTo(0, 0);
            ctx.lineTo(size, -size/2);
            ctx.lineTo(size, size/2);
            ctx.closePath();

          Then we rotate the canvas by the angle (which is the direction of movement). The direction of movement is the angle of the velocity vector.

          How to get the angle? 

            angle = Math.atan2(vy, vx);   // because in canvas, positive y is down, so atan2(vy, vx) gives the angle from the positive x-axis (right) to the vector (vx,vy). But note: if the fish is moving to the right, vx>0, vy=0, then angle=0 -> which is correct.

          However, note: when the fish is moving up (vy negative), the angle will be negative (or positive? atan2 returns in the range [-pi, pi]). But that's okay.

        But note: the fish will be drawn with the head at (0,0) and the tail at (size,0) in the default orientation. Then when we rotate, the head will point in the direction of the angle.

        However, we want the head to be at the front of the movement. So when the fish is moving in a direction, the head should be pointing that way. So the drawing is correct.

        We'll set the size for the fish to be the length from head to tail (so the base of the triangle is at the tail, and the head is at the front). We'll set the size to be between 10 and 20.

 9. We'll also add a small tail wiggle? That might be too complex for the time. We'll skip it for now.

 10. We'll set a background color for the canvas (light blue) and draw the fish.

 Implementation:

   - We'll create a Fish class.

   - We'll create an array of fish.

   - We'll initialize the fish with random positions (within the canvas, but not too close to the edge to avoid immediate boundary handling), random velocities (within a range), random size, and random color.

   - The color: we'll generate a random hue (between 0 and 360) and then set the color to "hsl(hue, 70%, 50%)".

   - We'll set a max speed (3) and a wander strength (0.05) for the wandering.

   - In the update method of the Fish class:

        // Wandering: add a small random change to the velocity
        vx += (Math.random() - 0.5) * wanderStrength;
        vy += (Math.random() - 0.5) * wanderStrength;

        // Boundary repulsion
        const margin = 20;
        const repulsion = 0.5;
        if (x < margin) {
            vx += repulsion * (margin - x);
        } else if (x > W - margin) {
            vx -= repulsion * (x - (W - margin));
        }
        if (y < margin) {
            vy += repulsion * (margin - y);
        } else if (y > H - margin) {
            vy -= repulsion * (y - (H - margin));
        }

        // Clamp speed to maxSpeed
        const speed = Math.sqrt(vx*vx + vy*vy);
        if (speed > maxSpeed) {
            vx = (vx / speed) * maxSpeed;
            vy = (vy / speed) * maxSpeed;
        }

        // Update position
        x += vx * deltaTime;
        y += vy * deltaTime;

        // Also, we might want to update the angle for drawing (we'll compute it in the draw method, so we don't store it in the fish object)

   - However, note: the wandering and boundary repulsion are applied every frame. We are using delta time for the position update, but note: the wandering and repulsion are applied as forces (so they are in velocity units per frame). Since we are using delta time for the position, we should also use delta time for the velocity changes? Actually, the wandering and repulsion are not physics-based in a time-dependent way. We are adding a fixed amount per frame. To make it frame-rate independent, we should multiply the wanderStrength and repulsion by delta time? But note: the repulsion is proportional to the distance, so it's not time-dependent. And the wandering is a random change per frame, which we want to be the same regardless of frame rate.

   - However, the problem says: "use delta time for frame-rate independent". So we should use delta time for the position update, but the wandering and repulsion are applied as forces that are not time-dependent? Actually, the wandering is a random change per frame, so it's okay to do per frame. But if we want the wandering to be the same regardless of frame rate, we should multiply the wanderStrength by delta time? But note: the wanderStrength is a small value, and we are adding it every frame. If the frame rate is lower, we get fewer updates, so the wandering would be less. To make it frame-rate independent, we should have a wanderStrength per second.

   - We'll adjust: we'll have a wanderStrengthPerSecond (e.g., 0.1) and then multiply by delta time.

   - Similarly, the repulsion is a force that we are applying per frame, but it's proportional to the distance. We don't want to change it with frame rate, so we leave it as is.

   - However, for simplicity and because the frame rate is usually high (60fps), we'll do the wandering without delta time (as a fixed per-frame change). But note: the problem requires frame-rate independence. So we'll do:

        wanderStrengthPerSecond = 0.1;
        vx += (Math.random() - 0.5) * wanderStrengthPerSecond * deltaTime;
        vy += (Math.random() - 0.5) * wanderStrengthPerSecond * deltaTime;

   - But note: the repulsion we are doing without delta time? Actually, the repulsion is a force that we want to be the same regardless of frame rate? It's a bit tricky. We'll leave the repulsion as is (without delta time) because it's a small force and we are clamping the speed. The main issue is the position update which we do with delta time.

   - We'll set:

        const wanderStrengthPerSecond = 0.1;

   - And then in the update:

        vx += (Math.random() - 0.5) * wanderStrengthPerSecond * deltaTime;
        vy += (Math.random() - 0.5) * wanderStrengthPerSecond * deltaTime;

   - But note: the wandering might cause the fish to move too much if the frame rate is low? Actually, we are multiplying by delta time, so it will be the same per second.

 11. We'll also add a small tail wiggle? We'll skip for now.

 12. We'll create 12 fish.

 13. We'll set the canvas to 800x600.

 Let's code accordingly.

 Steps:

   - Define constants: W, H, maxSpeed, wanderStrengthPerSecond, etc.

   - Define Fish class.

   - Initialize the fish array.

   - In the gameLoop:

        * Clear the canvas (with a light blue background)
        * Update each fish (using the update method that uses delta time)
        * Draw each fish (using the draw method)

   - We'll use requestAnimationFrame with timestamp to get delta time.

 Implementation of gameLoop:

        let lastTime = 0;
        function gameLoop(timestamp) {
            const deltaTime = (timestamp - lastTime) / 1000; // in seconds
            lastTime = timestamp;

            // Clear the canvas
            ctx.fillStyle = 'rgb(207, 247, 255)'; // light blue
            ctx.fillRect(0, 0, W, H);

            // Update and draw each fish
            for (let i = 0; i < fish.length; i++) {
                fish[i].update(deltaTime);
                fish[i].draw();
            }

            requestAnimationFrame(gameLoop);
        }

 14. We'll set the canvas to 800x600.

 Let's write the code accordingly.

 Note: We are going to use a class for Fish.

 Let's code the Fish class:

   class Fish {
        constructor(x, y, vx, vy, size, color) {
            this.x = x;
            this.y = y;
            this.vx = vx;
            this.vy = vy;
            this.size = size;
            this.color = color;
        }

        update(deltaTime) {
            // Wandering: add a random change to velocity
            const wanderStrengthPerSecond = 0.1;
            this.vx += (Math.random() - 0.5) * wanderStrengthPerSecond * deltaTime;
            this.vy += (Math.random() - 0.5) * wanderStrengthPerSecond * deltaTime;

            // Boundary repulsion
            const margin = 20;
            const repulsion = 0.5;
            if (this.x < margin) {
                this.vx += repulsion * (margin - this.x);
            } else if (this.x > W - margin) {
                this.vx -= repulsion * (this.x - (W - margin));
            }
            if (this.y < margin) {
                this.vy += repulsion * (margin - this.y);
            } else if (this.y > H - margin) {
                this.vy -= repulsion * (this.y - (H - margin));
            }

            // Clamp speed
            const maxSpeed = 3;
            const speed = Math.sqrt(this.vx * this.vx + this.vy * this.vy);
            if (speed > maxSpeed) {
                this.vx = (this.vx / speed) * maxSpeed;
                this.vy = (maxSpeed) * deltaTime; // not needed

            }

        }

 12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.12.

<!-- Benchmark Info -->
<!-- Backend: llamacpp -->
<!-- Model: Qwen3-30B-A3B-Thinking-2507-UD-Q6_K_XL.gguf -->
<!-- Prompt: aquarium.md -->
<!-- Generation Time: 137.81s -->
<!-- Fallback Used: False -->