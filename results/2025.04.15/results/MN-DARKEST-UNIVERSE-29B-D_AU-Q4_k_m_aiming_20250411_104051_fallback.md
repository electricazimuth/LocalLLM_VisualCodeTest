<!DOCTYPE html>
<html>
<head>
    <title>Basic Aiming and Shooting Game</title>
    <style>
        body { margin: 0; overflow: hidden; background-color: #f0f0f0; }
        canvas { border: 1px solid black; background-color: #fff; display: block; margin: 20px auto; }
        #info { position: absolute; top: 10px; left: 10px; font-size: 16px; font-family: sans-serif; 
            background: rgba(0, 0, 0, 0.5); padding: 5px; border-radius: 5px; pointer-events: none; }
    </style>
</head>
<body>
    <canvas id="gameCanvas" width="800" height="600"></canvas>
    <div id="info"></div>
    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const W = canvas.width;
        const H = canvas.height;
        const TURRET_X = W / 2 | 0;
        const TURRET_Y = H - 20;
        const BARREL_LENGTH = 50;
        const PI2 = 2 * Math.PI;
        const FREEPOS = { x: W / 2, y: H / 2 };
        const TURRET_ANGLE = 0; 
        const TURRET_COLOR = '#ff0000';
        const BARREL_COLOR = '#ffff00'; 
        const FPS = 60; 
        const MS_PER_FRAME = 1000 / FPS; 
        const GRAVITY = 0.1; 
        const MAX_VEL = 3.0; 
        const MAX_LIFE = 60; 
        const COoldown = 30; 
        const BARREL_ANGLE = 0;
        const BARREL_OPTIONS = { 
            length: BARREL_LENGTH,  
            thickness: 2,  
            fill: BARREL_COLOR,  
            strokeStyle: BARREL_COLOR,  
            strokeWidth: 2  
        };
        const TURRET_OPTIONS = { 
            width: 40, height: 20, fill: TURRET_COLOR, strokeStyle: '#000000', strokeWidth: 2 
        };
        const FiringAngle = 0; 
        const firingAngle = 0; 
        const firingVel = 0; 
        const fired = 0; 
        const particles = []; 
        const particleoptions = {
            radius: 5, 
            color: '#ff0000', 
            life: 60, 
            gravity: 0.1,  
            restitution: 0.7 
        };

        const mouse = { x: W / 2, y: H / 2 };
        const aimpoint = { x: mouse.x, y: mouse.y };

        const drawCircle = (p, options = {}) => {
            const opt = { radius: options.radius || particleoptions.radius, fill: options.fill || particleoptions.color };
            const { radius, fill = particleoptions.color } = opt;
            ctx.beginPath();
            ctx.arc(p.x, p.y, radius, 0, 2 * Math.PI);
            ctx.fillStyle = fill;
            ctx.fill();
            ctx.strokeStyle = particleoptions.strokeStyle || particleoptions.strokeStyle || particleoptions.strokeStyle || particleoptions.strokeStyle || particleoptions.strokeStyle || particleoptions.strokeStyle || particleoptions.strokeStyle || particleoptions.strokeStyle || particleoptions.strokeStyle || particleoptions.strokeStyle || particleoptions.strokeStyle || particleoptions.strokeStyle || particleoptions.strokeStyle || particleoptions.strokeStyle || particleoptions.strokeStyle || particleoptions.strokeStyle || particleoptions.strokeStyle || particleoptions.strokeStyle || particleoptions.strokeStyle || particleoptions.strokeStyle || particleoptions.strokeStyle || particleoptions.strokeStyle || particleoptions.strokeStyle || particleoptions.strokeStyle || particleoptions.strokeStyle || particleoptions.strokeStyle || particleoptions.strokeStyle || particleoptions.strokeStyle || particleoptions.strokeStyle || particleoptions.strokeStyle || particleoptions.strokeStyle || particleoptions.strokeStyle || particleoptions.strokeStyle || particleoptions strokeStyle = particleoptions.strokeStyle || particleoptions.strokeStyle || particleoptions.strokeStyle || particleoptions.strokeStyle || particleoptions.strokeStyle || particleoptions strokeStyle = particleoptions.strokeStyle || particleoptions.strokeStyle || particleoptions.strokeStyle || particleoptions strokeStyle = particleoptions.strokeStyle || particleoptions.strokeStyle || particleoptions.strokeStyle || particleoptions strokeStyle = particleoptions.strokeStyle || particleoptions.strokeStyle || particleoptions strokeStyle = particleoptions strokeStyle = particleoptions strokeStyle = particleoptions strokeStyle = particleoptions strokeStyle = particleoptions strokeStyle = particleoptions strokeStyle = particleoptions strokeStyle = particleoptions strokeStyle = particleoptions strokeStyle = particleoptions strokeStyle = particleoptions strokeStyle = particleoptions strokeStyle = particleoptions strokeStyle = particleoptions strokeStyle = particleoptions strokeStyle = particleoptions strokeStyle = particleoptions strokeStyle = particleoptions strokeStyle = particleoptions strokeStyle = particleoptions strokeStyle = particleoptions strokeStyle = particleoptions strokeStyle = particleoptions strokeStyle = particleoptions strokeStyle = particleoptions strokeStyle = particleoptions strokeStyle = particleoptions strokeStyle = particleoptions strokeStyle = particleoptions strokeStyle = particleoptions strokeStyle = particleoptions strokeStyle = particleoptions strokeStyle = particleoptions strokeStyle = particleoptions strokeStyle = particleoptions strokeStyle = particleoptions strokeStyle = particleoptions strokeStyle = particleoptions strokeStyle = particleoptions strokeStyle = particleoptions strokeStyle = particle
``` 
        const mouseclick = (e) => {
            const rect = canvas.getBoundingClientRect();
            mouse.x = e.clientX - rect.left - BARREL_LENGTH * Math.cos(BARREL_ANGLE);
            mouse.y = e.clientY - rect.top - BARREL_LENGTH * Math.sin(BARREL_ANGLE);
            FiringAngle = Math.atan2(mouse.y - aimpoint.y, mouse.x - aimpoint.x);
            firingVel = Math.sqrt((mouse.x - aimpoint.x) ** 2 + (mouse.y - aimpoint.y) ** 2) / MAX_VEL;
            fired = true;
        };

        const drawbarrel = (x, y, length, angle, options) => {
            const opt = { length: length || BARREL_LENGTH, thickness: options.thickness || BARREL_OPTIONS.thickness,
                fill: options fill || BARREL_OPTIONS.fill, strokeStyle: options strokeStyle || BARREL_OPTIONS strokeStyle || BARREL_OPTIONS strokeStyle || BARREL_OPTIONS strokeStyle || BARREL_OPTIONS strokeStyle || BARREL_OPTIONS strokeStyle || BARREL_OPTIONS strokeStyle || BARREL_OPTIONS strokeStyle || BARREL_OPTIONS strokeStyle || BARREL_OPTIONS strokeStyle || BARREL_OPTIONS strokeStyle || BARREL_OPTIONS strokeStyle || BARREL_OPTIONS strokeStyle || BARREL_OPTIONS strokeStyle || BARREL_OPTIONS strokeStyle || BARREL_OPTIONS strokeStyle || BARREL_OPTIONS strokeStyle || BARREL_OPTIONS strokeStyle || BARREL_OPTIONS strokeStyle || BARREL_OPTIONS strokeStyle || BARREL_OPTIONS strokeStyle || BARREL_OPTIONS strokeStyle || BARRE
``` 
        const drawparticle = (p, options) => {
            const opt = {
                radius: options.radius || particleoptions.radius,  
                fill: options fill || particleoptions.fill,  
                strokeStyle: options strokeStyle || particleoptions strokeStyle,  
                strokeWidth: options strokeWidth || particleoptions strokeWidth,  
                life: options life || particleoptions life,  
                gravity: options gravity || particleoptions gravity,  
                restitution: options restitution || particleoptions restitution  
            };
            const { radius, fill, strokeStyle, strokeWidth, life, gravity, restitution, life, gravity, restitution, restit
``` 
        const drawparticle = (p, options) => {
            const opt = {
                radius: options.radius || particleoptions.radius, 
                fill: options.fill || particleoptions.fill, 
                strokeStyle: options.strokeStyle || particleoptions.strokeStyle, 
                strokeWidth: options.strokeWidth || particleoptions.strokeWidth, 
                life: options.life || particleoptions.life, 
                gravity: options.gravity || particleoptions.gravity, 
                restitution: options.restitution || particleoptions.restitution
            };
            const { radius, fill, strokeStyle, strokeWidth, life, gravity, restitution } = opt;
            ctx.beginPath();
            ctx.arc(p.x, p.y, radius, 0, 2 * Math.PI);
            ctx.fillStyle = fill;
            ctx.fill();
            ctx.strokeStyle = strokeStyle;
            ctx.strokeWidth = strokeWidth; 
            ctx.stroke();
        };

        const drawparticles = () => {
            particles.forEach((p, i) => {
                const angle = p.angle + p.angularVel * delta;
                const velX = p.velX + p.accX * delta;
                const velY = p.velY + p.accY * delta - gravity * delta; 
                particles[i].x += velX * delta;
                particles[i].y += velY * delta; 
                particles[i].accX += particles[i].dragX * delta;
                particles[i].accY += particles[i].dragY * delta; 
                particles[i].velX += particles[i].accX * delta; 
                particles[i].velY += particles[i].accY * delta; 
                particles[i].life -= delta; 
                particles[i].radius -= particles[i].radiusDecay * delta; 
                particles[i].alpha -= particles[i].alphaDecay * delta; 
                particles[i].alpha = particles[i].alpha < 0 ? 0 : particles[i].alpha; 
                particles[i].radius = particles[i].radius < 0 ? 0 : particles[i].radius; 
                particles[i].alpha = particles[i].alpha / 255; 
                particles[i].alpha = particles[i].alpha < 0 ? 0 : particles[i].alpha; 
                particles[i].strokeWidth = particles[i].strokeWidth > 0 ? particles[i].strokeWidth - particles[i].strokeWidthDecay * delta : particles[i].strokeWidth; 
                particles[i].strokeWidth = particles[i
``` 
        const drawparticles = ( particles, options ) => {
            const opt = { 
                radius: options.radius || particleoptions.radius, fill: options.fill || particleoptions.fill, strokeStyle: options.strokeStyle || particleoptions strokeStyle, strokeWidth: options.strokeWidth || particleoptions.strokeWidth, life: options.life || particleoptions.life, gravity: options.gravity || particleoptions.
 <!-- 600.10s -->