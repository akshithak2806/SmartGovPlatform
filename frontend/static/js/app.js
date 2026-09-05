document.addEventListener("DOMContentLoaded", function () {

    /* =========================================
       AI TEXT ANIMATION
       ========================================= */

    const aiText = document.querySelector(".visual-text");

    if (aiText) {
        const messages = [
            "Understanding your problem...",
            "Analyzing your request...",
            "Finding the right service...",
            "Finding the best professional..."
        ];

        let currentMessage = 0;

        setInterval(function () {
            currentMessage = (currentMessage + 1) % messages.length;

            aiText.style.opacity = "0";

            setTimeout(function () {
                aiText.textContent = messages[currentMessage];
                aiText.style.opacity = "1";
            }, 350);

        }, 2500);
    }


    /* =========================================
       SCROLL REVEAL ANIMATION
       ========================================= */

    const animatedElements = document.querySelectorAll(
        ".card, .step-card"
    );

    const observer = new IntersectionObserver(function (entries) {

        entries.forEach(function (entry) {

            if (entry.isIntersecting) {
                entry.target.classList.add("show");
                observer.unobserve(entry.target);
            }

        });

    }, {
        threshold: 0.15
    });


    animatedElements.forEach(function (element) {

        element.classList.add("reveal");

        observer.observe(element);

    });

});