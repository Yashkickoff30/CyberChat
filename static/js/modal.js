
//Signup modal
const modal = document.querySelector("#my-modal-signup");
const modalBtn = document.querySelector("#modal-btn-signup");
const closeBtn = document.querySelector(".close");

// Events
modalBtn.addEventListener("click", openModal);
closeBtn.addEventListener("click", closeModal);
window.addEventListener("click", outsideClick);

// Open
function openModal() {
  modal.style.display = "block";
}

// Close
function closeModal() {
  modal.style.display = "none";
}

// Close If Outside Click
function outsideClick(e) {
  if (e.target == modal) {
    modal.style.display = "none";
  }
}

//login modal

const modal1 = document.querySelector("#my-modal-login");
const modalBtn1 = document.querySelector("#modal-btn-login");
const closeBtn1 = document.querySelector(".close1");

// Events
modalBtn1.addEventListener("click", openModal1);
closeBtn1.addEventListener("click", closeModal1);
window.addEventListener("click", outsideClick1);

// Open
function openModal1() {
  modal1.style.display = "block";
}

// Close
function closeModal1() {
  modal1.style.display = "none";
}

// Close If Outside Click
function outsideClick1(e) {
  if (e.target == modal1) {
    modal1.style.display = "none";
  }
}