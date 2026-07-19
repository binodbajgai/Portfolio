// ===============================
// NAVBAR SCROLL EFFECT
// ===============================

const navbar = document.querySelector(".navbar");

window.addEventListener("scroll", () => {

    if (window.scrollY > 50) {
        navbar.classList.add("scrolled");
    } else {
        navbar.classList.remove("scrolled");
    }

});

// ===============================
// TYPING EFFECT
// ===============================

const roles = [
    "AI Developer",
    "Python Developer",
    "Flask Developer",
    "Backend Developer"
];

const typingElement = document.getElementById("typing-role");

let roleIndex = 0;
let charIndex = 0;
let deleting = false;

function typeRole() {

    const currentRole = roles[roleIndex];

    if (!deleting) {

        typingElement.textContent = currentRole.substring(0, charIndex + 1);

        charIndex++;

        if (charIndex === currentRole.length) {

            deleting = true;

            setTimeout(typeRole, 1800);

            return;
        }

    } else {

        typingElement.textContent = currentRole.substring(0, charIndex - 1);

        charIndex--;

        if (charIndex === 0) {

            deleting = false;

            roleIndex = (roleIndex + 1) % roles.length;
        }

    }

    setTimeout(typeRole, deleting ? 50 : 100);

}

typeRole();

// ===============================
// SCROLL PROGRESS BAR
// ===============================

const progressBar = document.querySelector(".scroll-progress");

window.addEventListener("scroll", () => {

    const scrollTop = window.scrollY;

    const documentHeight =
        document.documentElement.scrollHeight -
        window.innerHeight;

    const progress =
        (scrollTop / documentHeight) * 100;

    progressBar.style.width = progress + "%";

});

// ===============================
// ACTIVE NAVIGATION
// ===============================

const sections = document.querySelectorAll("section");
const navLinks = document.querySelectorAll(".nav-link");

window.addEventListener("scroll", () => {

    let current = "";

    sections.forEach(section => {

        const sectionTop = section.offsetTop - 140;
        const sectionHeight = section.offsetHeight;

        if (
            window.scrollY >= sectionTop &&
            window.scrollY < sectionTop + sectionHeight
        ) {
            current = section.getAttribute("id");
        }

    });

    navLinks.forEach(link => {

        link.classList.remove("active");

        if (link.getAttribute("href") === "#" + current) {

            link.classList.add("active");

        }

    });

});

// ===============================
// MOUSE GLOW
// ===============================

const mouseGlow = document.querySelector(".mouse-glow");

document.addEventListener("mousemove",(e)=>{

    mouseGlow.style.left = e.clientX + "px";

    mouseGlow.style.top = e.clientY + "px";

});

// ======================================
// PARTICLE BACKGROUND
// ======================================

const canvas = document.getElementById("particles");
const ctx = canvas.getContext("2d");

let particles = [];

function resizeCanvas(){

    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

}

resizeCanvas();

window.addEventListener("resize", resizeCanvas);

class Particle{

    constructor(){

        this.reset();

        this.x = Math.random()*canvas.width;
        this.y = Math.random()*canvas.height;

    }

    reset(){

        this.radius = Math.random()*2+1;

        this.speedX = (Math.random()-0.5)*0.4;
        this.speedY = (Math.random()-0.5)*0.4;

        this.alpha = Math.random()*0.6+0.2;

    }

    update(){

        this.x += this.speedX;
        this.y += this.speedY;

        if(this.x<0) this.x=canvas.width;
        if(this.x>canvas.width) this.x=0;

        if(this.y<0) this.y=canvas.height;
        if(this.y>canvas.height) this.y=0;

    }

    draw(){

        ctx.beginPath();

        ctx.arc(
            this.x,
            this.y,
            this.radius,
            0,
            Math.PI*2
        );

        ctx.fillStyle=`rgba(0,245,255,${this.alpha})`;

        ctx.fill();

    }

}

for(let i=0;i<90;i++){

    particles.push(new Particle());

}

function animateParticles(){

    ctx.clearRect(0,0,canvas.width,canvas.height);

    particles.forEach(p=>{

        p.update();
        p.draw();

    });

    requestAnimationFrame(animateParticles);

}

animateParticles();
