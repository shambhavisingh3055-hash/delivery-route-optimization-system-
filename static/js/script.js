// ===============================
// AI Route Dashboard Script
// ===============================

// Animate dashboard numbers
function animateValue(element, start, end, duration, suffix = "") {

    let startTime = null;

    function animation(currentTime) {

        if (!startTime) startTime = currentTime;

        const progress = Math.min((currentTime - startTime) / duration, 1);

        const value = Math.floor(progress * (end - start) + start);

        element.innerHTML = value + suffix;

        if (progress < 1) {
            requestAnimationFrame(animation);
        }

    }

    requestAnimationFrame(animation);

}

// Start animation when page loads

window.onload = () => {

    const cards = document.querySelectorAll(".card h2");

    if(cards.length >= 4){

        animateValue(cards[0],0,124,1500);

        animateValue(cards[1],0,268,1700," km");

        animateValue(cards[2],0,315,1800," min");

        animateValue(cards[3],0,52,1600," L");

    }

};

// Button animation

const button = document.querySelector(".btn");

if(button){

button.addEventListener("click",()=>{

button.innerHTML="Optimizing...";

button.disabled=true;

setTimeout(()=>{

button.innerHTML="Route Optimized ✔";

button.style.background="#16a34a";

},2500);

});

}

// Card hover effect

const cards=document.querySelectorAll(".card");

cards.forEach(card=>{

card.addEventListener("mouseenter",()=>{

card.style.transform="translateY(-10px) scale(1.03)";

});

card.addEventListener("mouseleave",()=>{

card.style.transform="translateY(0px) scale(1)";

});

});

// Sidebar Active Menu

const menuItems=document.querySelectorAll(".sidebar ul li");

menuItems.forEach(item=>{

item.addEventListener("click",()=>{

menuItems.forEach(i=>i.classList.remove("active"));

item.classList.add("active");

});

});

// Greeting

const hour=new Date().getHours();

let greeting="Welcome";

if(hour<12){

greeting="Good Morning 👋";

}
else if(hour<17){

greeting="Good Afternoon ☀";

}
else{

greeting="Good Evening 🌙";

}

const title=document.querySelector(".header h1");

if(title){

title.innerHTML=greeting+"<br>AI/ML Delivery Route Optimization System";

}
// ===============================
// Upload Dataset
// ===============================

const csvFile=document.getElementById("csvFile");

if(csvFile){

csvFile.addEventListener("change",function(){

const file=this.files[0];

if(file){

document.getElementById("fileName").innerHTML=
"Selected File : "+file.name+" ✅";

}

});

}
// Route Optimization Button

const optimizeBtn = document.getElementById("optimizeBtn");

if(optimizeBtn){

optimizeBtn.addEventListener("click",function(){

document.getElementById("stops").innerHTML="12";

document.getElementById("distance").innerHTML="23.5 km";

document.getElementById("time").innerHTML="48 min";

this.innerHTML="Route Optimized ✔";

this.style.background="#16a34a";

});

}
/* ===========================
   AI Prediction
=========================== */

const predictBtn=document.getElementById("predictBtn");

if(predictBtn){

predictBtn.addEventListener("click",()=>{

document.getElementById("predictionTime").innerHTML="42 min";

document.getElementById("traffic").innerHTML="Medium";

document.getElementById("weather").innerHTML="Cloudy";

document.getElementById("accuracy").innerHTML="96%";

predictBtn.innerHTML="Prediction Complete ✔";

predictBtn.style.background="#16a34a";

});
}
/* ===========================
   Report Chart
=========================== */

const chart=document.getElementById("deliveryChart");

if(chart){

new Chart(chart,{

type:"bar",

data:{

labels:["Mon","Tue","Wed","Thu","Fri","Sat"],

datasets:[{

label:"Deliveries",

data:[18,22,15,28,26,32],

backgroundColor:"#2563eb"

}]

},

options:{

responsive:true,

plugins:{

legend:{

display:false

}

}

}

});

}
// ===============================
// Upload Dataset
// ===============================

const csvFile=document.getElementById("csvFile");

if(csvFile){

csvFile.addEventListener("change",function(){

const file=this.files[0];

if(file){

document.getElementById("fileName").innerHTML=
"Selected File : "+file.name+" ✅";

}

});
