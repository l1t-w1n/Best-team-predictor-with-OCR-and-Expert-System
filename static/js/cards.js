// Function to get a random card from the "cards" folder
function getRandomCard() {
    var randomIndex = Math.floor(Math.random() * cardImages.length);
    return cardImages[randomIndex];
}

// Function to insert random cards to generic.html
function insertPlayerCards() {
    const genericCardsContainer = document.getElementById('player-cards');
    for (let i = 0; i < 5; i++) {
        const card = getRandomCard();
        genericCardsContainer.innerHTML += '<img src="./static/' + card + '" alt="Random Card">';;
    }
}

function showSearchPopup(cardIndex) {
    const card_placeholder = document.getElementById(`card-placeholder-${cardIndex}`);
    if (!card_placeholder.querySelector('#searchBox-' + cardIndex)) {
        card_placeholder.innerHTML = `
            <input type="text" id="searchBox-${cardIndex}" placeholder="Type to search heroes..." oninput="searchHeroes(${cardIndex})">
            <div id="searchResults-${cardIndex}"></div>
        `;
        card_placeholder.onclick = null;  // Remove the event listener to prevent showing the popup again
    }
}

function searchHeroes(cardIndex) {
    const input = document.getElementById(`searchBox-${cardIndex}`).value;
    fetch(`/search_heroes?query=${encodeURIComponent(input)}`)
        .then(response => response.json())
        .then(data => {
            const resultsContainer = document.getElementById(`searchResults-${cardIndex}`);
            resultsContainer.innerHTML = '';
            data.forEach(hero => {
                const resultItem = document.createElement('div');
                resultItem.textContent = hero;
                resultItem.onclick = () => selectHero(hero, cardIndex);
                resultsContainer.appendChild(resultItem);
            });
        });
}

function selectHero(heroName, cardIndex) {
    // Removed fetch to get hero ID, assuming heroName is directly usable
    const formats = ['jpeg', 'png', 'jpg']; // List of possible image formats
    const cardImage = document.createElement('img');
    cardImage.alt = "Hero Image";

    const placeholder = document.getElementById(`card-placeholder-${cardIndex}`);
    placeholder.innerHTML = '';  // Clear the existing content
    placeholder.appendChild(cardImage);
    placeholder.style.backgroundColor = 'white';
    placeholder.style.cursor = 'default';

    // Function to try loading next format
    function tryLoadImage(index) {
        if (index >= formats.length+1) {
            console.error('No valid image format found');
            return; // Stop if no formats left to try
        }
        cardImage.src = `./static/images/cards/${encodeURIComponent(heroName)}.${formats[index]}`;
        cardImage.onerror = () => tryLoadImage(index + 1); // Try next format on error
    }

    tryLoadImage(0); // Start trying from the first format
    updateSelectedHeroesCookie(heroName, cardIndex); // Update to use hero name
    selectHeroByName(heroName, cardIndex); // Function adjusted to use names
}



function updateSelectedHeroesCookie(heroName, cardIndex) {
    let selectedHeroes = getSelectedHeroesFromCookie();
    let found = false;
    for (let i = 0; i < selectedHeroes.length; i++) {
        if (selectedHeroes[i].name === heroName) {
            selectedHeroes[i].index = cardIndex;
            found = true;
            break;
        }
    }
    if (!found) {
        selectedHeroes.push({ name: heroName, index: cardIndex });
    }
    document.cookie = "selectedHeroes=" + JSON.stringify(selectedHeroes) + ";path=/;max-age=86400"; // expires after 1 day
}

function getSelectedHeroesFromCookie() {
    let matches = document.cookie.match(/(^| )selectedHeroes=([^;]+)/);
    if (matches) {
        return JSON.parse(decodeURIComponent(matches[2]));
    } else {
        return [];
    }
}

function restoreSelectedHeroes() {
    let selectedHeroes = getSelectedHeroesFromCookie();
    selectedHeroes = selectedHeroes.filter(hero => hero.name && typeof hero.index === 'number');  // Ensure each item has 'name' and 'index'
    selectedHeroes.forEach(hero => {
        selectHeroByName(hero.name, hero.index);
    });
}

function deleteHero(heroName, cardIndex) {
    let selectedHeroes = getSelectedHeroesFromCookie();
    selectedHeroes = selectedHeroes.filter(hero => hero.name !== heroName);
    document.cookie = "selectedHeroes=" + JSON.stringify(selectedHeroes) + ";path=/;max-age=86400";

    const placeholder = document.getElementById(`card-placeholder-${cardIndex}`);
    placeholder.innerHTML = '';
    placeholder.style.backgroundColor = 'lightgray';
    placeholder.style.cursor = 'pointer';
    placeholder.onclick = () => showSearchPopup(cardIndex);
}

function selectHeroByName(heroName, cardIndex) {
    const formats = ['jpeg', 'png', 'jpg']; // List of possible image formats
    const placeholder = document.getElementById(`card-placeholder-${cardIndex}`);
    placeholder.style.backgroundColor = 'white';
    placeholder.innerHTML = '';
    placeholder.onclick = null; // Remove the click event that shows the search popup

    const cardImage = document.createElement('img');
    cardImage.alt = "Hero Image";
    placeholder.appendChild(cardImage); // Add the image element to the DOM before setting src

    const deleteButton = document.createElement('button');
    deleteButton.textContent = 'Delete';
    deleteButton.style.marginTop = '5px'; // Add some spacing for better UI
    deleteButton.onclick = () => deleteHero(heroName, cardIndex); // Function adjusted to use hero name
    placeholder.appendChild(deleteButton); // Add the delete button

    // Function to try loading next format
    function tryLoadImage(index) {
        if (index >= formats.length) {
            console.error('No valid image format found for', heroName);
            return; // Stop if no formats left to try
        }
        cardImage.src = `./static/images/cards/${encodeURIComponent(heroName)}.${formats[index]}`;
        cardImage.onerror = () => tryLoadImage(index + 1); // Try next format on error
    }

    tryLoadImage(0); // Start trying from the first format
}

function analyzeSelectedHeroes() {
    fetch('/analyze')
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                alert(data.message);
            } else if (data.heroes) {
                const playerCardsContainer = document.getElementById('player-cards');
                playerCardsContainer.innerHTML = ''; // Clear existing cards
                data.heroes.forEach(hero => {
                    const heroCard = `<img src="./${hero.image}" alt="${hero.name}">`;
                    playerCardsContainer.innerHTML += heroCard;
                });
            } else if (data.error) {
                alert("Error: " + data.error);
            } else {
                alert("No common color found or no heroes selected.");
            }
        })
        .catch(error => console.error('Error analyzing heroes:', error));
}


function clearSelections() {
    let selectedHeroes = getSelectedHeroesFromCookie();
    selectedHeroes.forEach(hero => {
        deleteHero(hero.id, hero.index);
    });
    clearTestCookie();
}

document.addEventListener('DOMContentLoaded', function() {
    for (let i = 1; i <= 5; i++) {
        const placeholder = document.getElementById(`card-placeholder-${i}`);
        placeholder.onclick = function() {
            showSearchPopup(i);
        };
    }
});

function clearTestCookie() {
    document.cookie = "selectedHeroes=;path=/;expires=Thu, 01 Jan 1970 00:00:00 GMT";
}

window.onload = function() {
    // Function to insert random cards to opponent
    // Function to insert random cards to generic.html
    //insertPlayerCards();
    restoreSelectedHeroes();
}
