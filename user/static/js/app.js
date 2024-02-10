const toggleSwitch = document.getElementById("toggleswitch");
const gyapuHead = document.getElementById("gyapu-head");

window.onscroll = function () { scrollShowNavbar() };
toggleSwitch.addEventListener('change', nightMode);

function scrollShowNavbar() {
  const nav = document.getElementById("secondNav");

  if (document.body.scrollTop > 300 || document.documentElement.scrollTop > 300) {
    nav.style.position = "fixed";
    nav.style.marginTop = "-40px";
  } else {
    nav.style.position = "static";
    nav.style.marginTop = "0";
  }
}

function nightMode(){
  document.body.classList.toggle("nightmode");
  if(document.body.classList == "nightmode")
    gyapuHead.src = "/static/images/gyapu-header-nightmode.svg";
  else{
    gyapuHead.src = "/static/images/gyapu-header-lightmode.svg";
  }
}

// increment of quantity
function incrementQuantity(stock) {
  var button = event.target;
  var uuid = button.getAttribute('data-uuid');
  var quantityElement = document.getElementById('quantity' + uuid);
  var quantityInput = document.getElementById('quantity_input' + uuid);
  var currentQuantity = parseInt(quantityElement.innerText);
  if(currentQuantity < stock) {
    quantityElement.innerText = currentQuantity + 1;
    quantityInput.value = currentQuantity + 1;
  }  
}

// decrement of quantity
function decrementQuantity() {
  var button = event.target;
  var uuid = button.getAttribute('data-uuid');
  var quantityElement = document.getElementById('quantity' + uuid);
  var quantityInput = document.getElementById('quantity_input' + uuid);
  var currentQuantity = parseInt(quantityElement.innerText);
  if (currentQuantity > 1) {
    quantityElement.innerText = currentQuantity - 1;
    quantityInput.value = currentQuantity - 1;
  }
}
