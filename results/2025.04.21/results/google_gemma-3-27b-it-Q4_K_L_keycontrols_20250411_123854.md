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
            isJumping: false,
            gravity: 0.5,
        };

        const keys = {};

        document.addEventListener('keydown', (e) => {
            keys[e.key] = true;
        });

        document.addEventListener('keyup', (e) => {
            keys[e.key] = false;
        });

        function gameLoop(timestamp) {
            // Clear canvas
            ctx.clearRect(0, 0, W, H);

            // Update logic
            update(timestamp);

            // Draw logic
            draw();

            requestAnimationFrame(gameLoop);
        }

        function update(timestamp) {
            let deltaTime = timestamp - lastTime;
            lastTime = timestamp;

            // Horizontal Movement
            if (keys['a'] || keys['ArrowLeft']) {
                player.velocityX -= player.acceleration;
            } else if (keys['d'] || keys['ArrowRight']) {
                player.velocityX += player.acceleration;
            } else {
                // Deceleration
                if (player.velocityX > 0) {
                    player.velocityX -= player.deceleration;
                    if (player.velocityX < 0) player.velocityX = 0;
                } else if (player.velocityX < 0) {
                    player.velocityX += player.deceleration;
                    if (player.velocityX > 0) player.velocityX = 0;
                }
            }

            // Vertical Movement (Jumping)
            if (player.isJumping) {
                player.velocityY += player.gravity;
                player.y += player.velocityY;

                if (player.y >= H - player.height) {
                    player.y = H - player.height;
                    player.velocityY = 0;
                    player.isJumping = false;
                }
            }

            // Boundary Checks
            player.x = Math.max(0, Math.min(player.x, W - player.width));
            player.y = Math.max(0, Math.min(player.y, H - player.height));

            player.x += player.velocityX;
        }

        function draw() {
            ctx.fillStyle = 'blue';
            ctx.fillRect(player.x, player.y, player.width, player.height);
        }
        
        //Event listener for Space Bar
        document.addEventListener('keydown', function(event) {
            if (event.code === 'Space' && !player.isJumping) {
                player.velocityY = -10; // Initial jump velocity
                player.isJumping = true;
            }
        });

        let lastTime = 0;
        // Start the loop
        requestAnimationFrame(gameLoop);

        // Add any initial setup or event listeners here

    </script>
    <section id="notes">
        <p>Implemented jumping with spacebar.  Horizontal movement is now using acceleration and deceleration.  Multiple key presses now work.</p>
        <p>The player object contains all variables related to the player.  The gameLoop function is the main loop of the game.</p>
        <p>Update function handles all updates to the player's position and velocity.</p>
        <p>Draw function draws the player on the canvas.</p>
        <p>Event listeners are used to detect key presses.</p>
    </section>
</body>
</html>
```
 <!-- 89.52s -->