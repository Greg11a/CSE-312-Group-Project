// Make like button clickable
document.addEventListener('DOMContentLoaded', () => {
    const likeButtons = document.querySelectorAll('.like-button');

    // likeButtons.forEach(button => {
    //     button.addEventListener('click', () => {
    //         const isLiked = button.getAttribute('liked') === 'true';
    //         button.setAttribute('liked', !isLiked);
    //         const icon = button.querySelector('.material-icons');
    //         if (isLiked) {
    //             icon.textContent = 'thumb_up_off_alt';
    //         } else {
    //             icon.textContent = 'thumb_up';
    //         }
    //     });
    // });
    document.querySelectorAll('.like-button').forEach(button => {
        button.addEventListener('click', () => {
            const postId = button.getAttribute('data-id');
            const isLiked = button.getAttribute('liked') === 'true';
            fetch(`/like/${postId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                },
                credentials: 'include',
            }).then(response => response.json()).then(data => {
            });
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
let serverTime = parseFloat(document.body.getAttribute('data-server-time')) * 1000; // Convert to milliseconds
let clientTime = new Date().getTime();
let timeOffset = serverTime - clientTime;

function updateCountdowns() {
    const posts = document.querySelectorAll('.post[data-is-published="False"]');
    posts.forEach(post => {
        const timestamp = parseFloat(post.getAttribute('data-timestamp')) * 1000; // Convert to milliseconds
        const countdownElement = post.querySelector('.countdown-timer');
        const now = new Date().getTime() + timeOffset;
        const distance = timestamp - now;

        if (distance > 0) {
            // Calculate time components
            const days = Math.floor(distance / (1000 * 60 * 60 * 24));
            const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
            const seconds = Math.floor((distance % (1000 * 60)) / 1000);

            countdownElement.innerHTML = `${days}d ${hours}h ${minutes}m ${seconds}s`;
        } else {
            countdownElement.innerHTML = "Posting...";
            // Optionally, refresh the page or remove the countdown
            setTimeout(() => {
                location.reload();
            }, 1000);
        }
    });
}

document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".follow-button").forEach(button => {
        button.addEventListener("click", () => {
            const username = button.dataset.username;
            const isFollowing = button.dataset.following === "true";
            const url = isFollowing ? `/unfollow/${username}` : `/follow/${username}`;

            fetch(url, {
                method: "POST",
                headers: { "X-CSRFToken": csrfToken },
                credentials: "include"
            }).then(response => response.json()).then(data => {
                if (data.success) {
                    button.dataset.following = !isFollowing;
                    button.textContent = !isFollowing ? "Followed" : "Follow";
                }
            });
        });
    });
});

// Update countdowns every second
setInterval(updateCountdowns, 1000);

function syncServerTime() {
    fetch('/get_server_time')
        .then(response => response.json())
        .then(data => {
            serverTime = data.server_time * 1000;
            clientTime = new Date().getTime();
            timeOffset = serverTime - clientTime;
        });
}

// Sync server time every 10 seconds
setInterval(syncServerTime, 10000);
