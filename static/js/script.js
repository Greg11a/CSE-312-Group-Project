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

// document.getElementById('login-icon').addEventListener('click', function (event) {
//     event.preventDefault();
//     window.location.href = '/login'; // Redirect to login page
// });
// document.getElementById('chat-icon').addEventListener('click', function (event) {
//     event.preventDefault();
//     window.location.href = '/chat'; // Redirect to chat page
// });
