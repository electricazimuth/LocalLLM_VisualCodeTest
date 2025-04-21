Here's how you can implement the game using plain JavaScript and the Canvas API. This version includes jumping and acceleration/deceleration. It also handles multiple key presses simultaneously for diagonal movement.

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
            xVelocity: 0,
            yVelocity: 0,
            jumping: false,
        };

        const keys = {
            left: false,
            right: false,
            up: false,
        };

        window.addEventListener('keydown', (e) => {
            switch (e.key) {
                case 'ArrowLeft':
                case 'a':
                    keys.left = true;
                    break;
                case 'ArrowRight':
                case 'd':
                    keys.right = true;
                    break;
                case 'ArrowUp':
                case 'w':
                    if (!player.jumping) {
                        player.yVelocity -= 15;
                        player.jumping = true;
                    }
                    break;
            }
        });

        window.addEventListener('keyup', (e) => {
            switch (e.key) {
                case 'ArrowLeft':
                case 'a':
                    keys.left = false;
                    break;
                case 'ArrowRight':
                case 'd':
                    keys.right = false;
                    break;
            }
        });

        function gameLoop(timestamp) {
            ctx.clearRect(0, 0, W, H);

            if (keys.left) player.xVelocity -= 0.5;
            if (keys.right) player.xVelocity += 0.5;

            player.xVelocity *= 0.9;
            player.yVelocity += 1;

            player.x += player.xVelocity;
            player.y += player.yVelocity;

            if (player.x < 0) player.x = 0;
            if (player.x > W - player.width) player.x = W - player.width;
            if (player.y > H - player.height) {
                player.y = H - player.height;
                player.jumping = false;
                player.yVelocity = 0;
            }

            ctx.fillStyle = 'black';
            ctx.fillRect(player.x, player.y, player.width, player.height);

            requestAnimationFrame(gameLoop);
        }

        requestAnimationFrame(gameLoop);
    </script>
</body>
</html>
```

The `player` object now has `xVelocity` and `yVelocity` to handle acceleration and deceleration. The `jumping` property is used to prevent the player from jumping while already in the air.

In the `keydown` event listener, we check if the `up` key is pressed and the player is not already jumping. If so, we decrease the `yVelocity` to make the player jump.

In the `gameLoop` function, we update the `xVelocity` and `yVelocity` based on the keys that are pressed. We then update the `x` and `y` positions using these velocities. We also apply gravity (increasing `yVelocity`) and check for boundary conditions.
 <!-- 96.14s -->