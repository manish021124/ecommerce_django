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
  let button = event.target;
  let uuid = button.getAttribute('data-uuid');
  let quantityElement = document.getElementById('quantity' + uuid);
  let quantityInput = document.getElementById('quantity_input' + uuid);
  let currentQuantity = parseInt(quantityElement.innerText);
  if(currentQuantity < stock) {
    quantityElement.innerText = currentQuantity + 1;
    quantityInput.value = currentQuantity + 1;
  }  
}

// decrement of quantity
function decrementQuantity() {
  let button = event.target;
  let uuid = button.getAttribute('data-uuid');
  let quantityElement = document.getElementById('quantity' + uuid);
  let quantityInput = document.getElementById('quantity_input' + uuid);
  let currentQuantity = parseInt(quantityElement.innerText);
  if (currentQuantity > 1) {
    quantityElement.innerText = currentQuantity - 1;
    quantityInput.value = currentQuantity - 1;
  }
}

// fetch the initial cart count 
document.addEventListener('DOMContentLoaded', function() {
  const cartCounts = document.querySelectorAll('.cart-number');

  fetch('/carts/get-cart-count/')
    .then(response => response.json())
    .then(data => {
      cartCounts.forEach(cartCount => {
        cartCount.textContent = data.cartCount;
      });
    })
    .catch(error => {
      console.error('Error fetching cart count:', error);
    });
});
