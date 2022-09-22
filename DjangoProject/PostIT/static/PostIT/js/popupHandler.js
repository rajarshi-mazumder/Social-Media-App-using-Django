const openPopup = document.getElementById('open-popup')
const popupContainer = document.getElementById('popup-container')
const closePopup = document.getElementById('close-popup')


openPopup.addEventListener('click', () => {
    popupContainer.classList.add('show');
});

closePopup.addEventListener('click', () => {
    popupContainer.classList.remove('show');
});



