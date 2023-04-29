var expands = document.querySelectorAll(".expand");
expands.forEach(el => {
    el.addEventListener("click", function() {
        info = el.closest('.item').querySelector('.item_info');
        el.classList.toggle("active");
        info.classList.toggle('active');
    });
});
