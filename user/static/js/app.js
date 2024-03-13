// fetch the initial cart count 
document.addEventListener('DOMContentLoaded', function() {
  const cartCounts = document.querySelectorAll('.cart-number');
  const toggleSwitch = document.getElementById("toggleswitch");
  const gyapuHead = document.getElementById("gyapu-head");

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

    toggleSwitch.addEventListener('change', function() {
      nightMode();
    });

    // check local storage on page load
    let nightModeEnabled = localStorage.getItem("nightModeEnabled");
    if (nightModeEnabled === "true") {
      document.body.classList.add("nightmode");
      gyapuHead.src = "/static/images/gyapu-header-nightmode.svg";
      toggleSwitch.style.backgroundImage = 'url("/static/images/moon.svg")';
    }
});

window.onscroll = function () { scrollShowNavbar() };

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
  const toggleSwitch = document.getElementById("toggleswitch");
  const gyapuHead = document.getElementById("gyapu-head");
  
  document.body.classList.toggle("nightmode");
  if(document.body.classList.contains("nightmode")) {
    gyapuHead.src = "/static/images/gyapu-header-nightmode.svg";
    toggleSwitch.style.backgroundImage = 'url("/static/images/moon.svg")';
    // store night mode state in local storage 
    localStorage.setItem("nightModeEnabled", "true");
  } else {
    gyapuHead.src = "/static/images/gyapu-header-lightmode.svg";
    toggleSwitch.style.backgroundImage = 'url("/static/images/sun.svg")';
    // remove night mode state from local storage 
    localStorage.removeItem("nightModeEnabled");
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

// can be done as in product update form
// allow user to add product image one by one
function addProductImage() {
  let addImageBtn = document.getElementById('add_image');
  let formsetDiv = document.getElementById('image_formset');
  let count = formsetDiv.getElementsByClassName('image-form').length; // Count the elements with class name 'image-form'
  if (count < 5) {
    let newImageForm = document.createElement('div');
    newImageForm.classList.add('image-form');
    // copied default django html
    newImageForm.innerHTML = `
      <div>
        <label for="id_images-${count}-image">Product Image:</label>
        <input type="file" name="images-${count}-image" accept="image/*" id="id_images-${count}-image">
      </div>
      <p>
        <label for="id_images-${count}-DELETE">Delete:</label>
        <input type="checkbox" name="images-${count}-DELETE" id="id_images-${count}-DELETE">
        <input type="hidden" name="images-${count}-id" id="id_images-${count}-id">
        <input type="hidden" name="images-${count}-product" id="id_images-${count}-product">
      </p>
    `;
    formsetDiv.appendChild(newImageForm);
    if (count == 4) {
      addImageBtn.style.display = 'none';
    }
  }
}
