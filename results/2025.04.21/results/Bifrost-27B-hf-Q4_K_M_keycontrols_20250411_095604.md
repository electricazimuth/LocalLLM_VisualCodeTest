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

        // --- YOUR CODE GOES HERE ---

        const player = {
            x: 50,
            y: H - 50,
            width: 30,
            height: 50,
            speed: 5,
            acceleration: 0.2,
            deceleration: 0.1,
            velocityX: 0,
            velocityY: 0,
            isJumping: false
        };

        const keys = {
            ArrowLeft: false,
            ArrowRight: false,
            ArrowUp: false,
            KeyA: false,
            KeyD: false,
            KeyW: false
        };

        // Event listeners for key presses
        document.addEventListener('keydown', (event) => {
            if (Object.keys(keys).includes(event.code)) {
                keys[event.code] = true;
            }
        });

        document.addEventListener('keyup', (event) => {
            if (Object.keys(keys).includes(event.code)) {
                keys[event.code] = false;
            }
        });

        let lastTimestamp = 0;

        function gameLoop(timestamp) {
            const deltaTime = (timestamp - lastTimestamp) / 1000;
            lastTimestamp = timestamp;

            // Clear canvas
            ctx.clearRect(0, 0, W, H);

            // --- Update logic ---
            // Horizontal movement
            if (keys.ArrowLeft || keys.KeyA) {
                player.velocityX -= player.acceleration;
            } else if (keys.ArrowRight || keys.KeyD) {
                player.velocityX += player.acceleration;
            } else {
                // Apply deceleration
                player.velocityX *= 0.9;
            }

            // Limit the velocity
            player.velocityX = Math.max(-player.speed, Math.min(player.velocityX, player.speed));

            // Vertical movement (jumping)
            if (keys.ArrowUp || keys.KeyW && !player.isJumping) {
                player.velocityY = -10;
                player.isJumping = true;
            }

            // Apply gravity
            if (player.isJumping) {
                player.velocityY += 0.5;
                if (player.y >= H - player.height) {
                    player.y = H - player.height;
                    player.velocityY = 0;
                    player.isJumping = false;
                }
            }

            // Update position
            player.x += player.velocityX;
            player.y += player.velocityY;

            // Boundary checks
            if (player.x < 0) {
                player.x = 0;
                player.velocityX = 0;
            } else if (player.x > W - player.width) {
                player.x = W - player.width;
                player.velocityX = 0;
            }

            // --- Draw logic ---
            ctx.fillStyle = 'blue';
            ctx.fillRect(player.x, player.y, player.width, player.height);

            requestAnimationFrame(gameLoop);
        }

        // Start the loop
        requestAnimationFrame(gameLoop);

        // Add any initial setup or event listeners here

    </script>
    <section id="notes">
        <p>
            This code implements a simple character movement with acceleration/deceleration, jumping, and boundary checks.
            It uses the Canvas API to draw a rectangle representing the player on the screen.
        </p>
    </section>
</body>
</html>
```
 <!-- 85.35s -->