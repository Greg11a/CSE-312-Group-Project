// Make like button clickable
document.addEventListener('DOMContentLoaded', () => {
    const likeButtons = document.querySelectorAll('.like-button');

    likeButtons.forEach(button => {
        button.addEventListener('click', () => {
            const isLiked = button.getAttribute('liked') === 'true';
            button.setAttribute('liked', !isLiked);
            const icon = button.querySelector('.material-icons');
            if (isLiked) {
                icon.textContent = 'thumb_up_off_alt';
            } else {
                icon.textContent = 'thumb_up';
            }
        });
    });
});

document.addEventListener("DOMContentLoaded", function () {
    const dropbtn = document.getElementById("dropbtn");
    const dropdownContent = document.getElementById("dropdown-content");

    if (dropbtn && dropdownContent) {
        dropdownContent.style.minWidth = dropbtn.offsetWidth + "px";
    }
});

document.addEventListener("DOMContentLoaded", function () {
    const visiblePassword = document.querySelectorAll(".visibility-password");

    visiblePassword.forEach(button => {
        const passwordInput = button.previousElementSibling; 
        const icon = button.querySelector(".material-icons");
        button.addEventListener("click", () => {
            const isPasswordVisible = passwordInput.getAttribute("type") === "text";
            if (isPasswordVisible) {
                passwordInput.setAttribute("type", "password");
                icon.textContent = "visibility_off";
            } else {
                passwordInput.setAttribute("type", "text");
                icon.textContent = "visibility";
            }
        });
    });
});
