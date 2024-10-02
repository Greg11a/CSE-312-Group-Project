document.getElementById('login-icon').addEventListener('click', function(event) {
    event.preventDefault();

    window.location.href = '/login'; // Redirect to login page
});
document.getElementById('chat-icon').addEventListener('click', function(event) {
    event.preventDefault();
    window.location.href = '/chat'; // Redirect to chat page
});