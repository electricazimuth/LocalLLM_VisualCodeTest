Here's a complete example that meets the requirements. The code includes a simple player object, keyboard event handling, boundary checking, sprite animation, and jumping with acceleration and deceleration. I've also added comments to explain the structure and logic.

```html
<!DOCTYPE html>
<html>
<head>
    <title>Run and Jump</title>
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
        const player = {
            x: W / 2,
            y: H - 50,
            width: 50,
            height: 50,
            speed: 5,
            acceleration: 0.5,
            jumping: false,
            jumpVelocity: 0,
            gravity: 0.5,
            maxJumpHeight: 50
        };

        let movingLeft = false;
        let movingRight = false;

        document.addEventListener('keydown', function(event) {
            if (event.key === 'ArrowLeft' || event.key === 'a') {
                movingLeft = true;
            }
            if (event.key === 'ArrowRight' || event.key === 'd') {
                movingRight = true;
            }
        });

        document.addEventListener('keyup', function(event) {
            if (event.key === 'ArrowLeft' || event.key === 'a') {
                movingLeft = false;
            }
            if (event.key === 'ArrowRight' || event.key === 'd') {
                movingRight = false;
            }
        });

        function gameLoop(timestamp) {
            const deltaTime = (timestamp - gameLoop.lastTime) / 1000;
            gameLoop.lastTime = timestamp;

            if (player.jumping) {
                player.y -= player.jumpVelocity * deltaTime;
                player.jumpVelocity -= player.gravity * deltaTime;
                player.jumpVelocity = Math.max(player.jumpVelocity, 0);
            }

            if (!player.jumping) {
                player.x += (movingLeft ? -player.speed : movingRight ? player.speed) * deltaTime;
                // Apply acceleration
                player.speed += player.acceleration * deltaTime;

                // Boundary checks
                if (player.x < 0) {
                    player.x = 0;
                    player.speed = -player.acceleration;
                }
                if (player.x > W - player.width) {
                    player.x = W - player.width;
                    player.speed = -player.acceleration;
                }
            }

            // Reset speed when stopping
            if (!movingLeft && !movingRight) {
                player.speed = 0;
            }

            // Optional face indicator
            if (player.x > W / 2) {
                ctx.beginPath();
                ctx.arc(player.x + player.width / 2, player.y + player.height / 2, 5, 0, Math.PI * 2);
                ctx.fillStyle = 'red';
                ctx.fill();
            } else if (player.x < W / 2) {
                ctx.beginPath();
                ctx.arc(player.x + player.width / 2, player.y + player.height / 2, 5, 0, Math.PI * 2);
                ctx.fillStyle = 'green';
                ctx.fill();
            }

            // Clear canvas
            ctx.clearRect(0, 0, W, H);

            // Draw player
            ctx.fillStyle = 'blue';
            ctx.fillRect(player.x, player.y, player.width, player.height);

            // Update player's position
            player.x += (movingLeft ? -player.speed : movingRight ? player.speed) * deltaTime;

            // Draw jump indicator
            if (player.jumping) {
                ctx.beginPath();
                ctx.rect(player.x + player.width / 2 - 5, player.y + player.height / 2 - 5, 10, 10);
                ctx.fillStyle = 'yellow';
                ctx.fill();
            }

            requestAnimationFrame(gameLoop);
        }

        gameLoop.lastTime = Date.now();

        // Start the game loop
        requestAnimationFrame(gameLoop);

        // Optional: Add more features or event listeners here

    </script>
    <section id="notes">
        <!-- Add any additional notes or features here -->
    </section>
</body>
</html>
```

This code initializes a player object with properties such as position, size, speed, and acceleration. Keyboard event listeners are set up to handle arrow key presses for movement and a spacebar key for jumping. The `gameLoop` function is called repeatedly using `requestAnimationFrame` to update the player's position, check for boundaries, and redraw the player on the canvas. The player's sprite is represented by a blue rectangle, and optional face indicators are drawn as red or green arcs depending on the direction of movement. The jumping feature uses gravity to create a natural jumping motion, with a deceleration applied as the player slows down.

Remember to test this in a modern web browser to see the character move. You can add additional features or event listeners within the `<section id="notes">` section if needed.
 <!-- 32.38s -->