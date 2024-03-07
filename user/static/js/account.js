const registerPwdInput = document.getElementById("password1");
const registerPwdConfirmInput = document.getElementById("password2");
const loginPwdInput = document.getElementById("password");
const registerPwdImage = document.getElementById("register-pwd-visibility-image");
const registerPwdConfirmImage = document.getElementById("register-pwd-confirm-visibility-image");
const loginPwdImage = document.getElementById("login-pwd-visibility-image");

registerPwdImage.addEventListener("click", function () { togglePasswordVisibility(registerPwdInput, registerPwdImage) });
registerPwdConfirmImage.addEventListener("click", function () { togglePasswordVisibility(registerPwdConfirmInput, registerPwdConfirmImage) });
loginPwdImage.addEventListener("click", function () { togglePasswordVisibility(loginPwdInput, loginPwdImage) });

function togglePasswordVisibility(input, image) {
  if (input.type === "password") {
    input.type = "text";
    image.src = "/static/images/account/visibility.svg";
  } else {
    input.type = "password";
    image.src = "/static/images/account/visibility_off.svg";
  }
}