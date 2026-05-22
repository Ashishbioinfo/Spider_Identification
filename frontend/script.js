function goToAnimalPage(){

let selectedAnimal = document.getElementById("animal").value

if(selectedAnimal === ""){
alert("Please select an animal")
return
}

if(selectedAnimal === "spider"){
window.location.href = "spider.html"
}

if(selectedAnimal === "frog"){
alert("Frog page coming soon")
}

if(selectedAnimal === "snail"){
alert("Snail page coming soon")
}

}