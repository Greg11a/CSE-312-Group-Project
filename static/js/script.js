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
    const passwordInput = document.getElementById("password");
    const visiblePassword = document.querySelector(".visibility-password");
    const icon = visiblePassword.querySelector(".material-icons");

    visiblePassword.addEventListener("click", function () {
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
