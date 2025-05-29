document.addEventListener('DOMContentLoaded', async function() {
    const form = document.getElementById('email-form');
    const searchButton = document.querySelector('.link-block-2');
    const weatherList = document.querySelector('.list');
    const searchInput = document.getElementById('field');
    const weatherBlock = document.getElementById('weather-block');
    const inlineSuggestion = document.getElementById('inline-suggestion');
    const enteredSpan = inlineSuggestion.querySelector('.entered');
    const suggestedSpan = inlineSuggestion.querySelector('.suggested');
  
    weatherBlock.style.display = 'none';
  
    const lastCity = localStorage.getItem('lastCity');
    if (lastCity) {
        searchInput.placeholder = lastCity;
    }
  
    const WEEK_ORDER = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
  
    // --- Inline autocomplete logic ---
    let currentSuggestion = '';
    let lastQuery = '';
  
    async function fetchCitySuggestions(query) {
        if (!query) return [];
        try {
            const url = `https://geocoding-api.open-meteo.com/v1/search?name=${encodeURIComponent(query)}&count=5&language=en&format=json`;
            const res = await fetch(url);
            if (!res.ok) return [];
            const data = await res.json();
            return (data.results || []).map(item => item.name);
        } catch {
            return [];
        }
    }
  
    async function updateInlineSuggestion() {
        const value = searchInput.value;
        enteredSpan.textContent = value;
        if (!value.trim()) {
            suggestedSpan.textContent = '';
            currentSuggestion = '';
            return;
        }
        if (lastQuery === value) return;
        lastQuery = value;
        const suggestions = await fetchCitySuggestions(value);
        const match = suggestions.find(name => name.toLowerCase().startsWith(value.toLowerCase()) && name.length > value.length);
        if (match) {
            suggestedSpan.textContent = match.slice(value.length);
            currentSuggestion = match;
        } else {
            suggestedSpan.textContent = '';
            currentSuggestion = '';
        }
    }
  
    searchInput.addEventListener('input', updateInlineSuggestion);
  
    searchInput.addEventListener('keydown', async function(e) {
        if ((e.key === 'Tab' || e.key === 'ArrowRight') && currentSuggestion) {
            e.preventDefault();
            searchInput.value = currentSuggestion;
            enteredSpan.textContent = currentSuggestion;
            suggestedSpan.textContent = '';
            currentSuggestion = '';
        } else if (e.key === 'Enter' && currentSuggestion) {
            e.preventDefault();
            searchInput.value = currentSuggestion;
            enteredSpan.textContent = currentSuggestion;
            suggestedSpan.textContent = '';
            const city = currentSuggestion;
            currentSuggestion = '';
            await searchWeather(city);
        }
    });
  
    searchInput.addEventListener('blur', function() {
        setTimeout(() => {
            suggestedSpan.textContent = '';
            currentSuggestion = '';
        }, 100);
    });
  
    // --- Weather logic ---
    async function searchWeather(city) {
        try {
            const response = await fetch(`/api/v1/weather/${city}`);
            if (!response.ok) {
                weatherBlock.style.display = 'none';
                throw new Error('City not found');
            }

            const data = await response.json();
            const weather = data.weather;

            localStorage.setItem('lastCity', city);

            weatherBlock.style.display = 'block';
            weatherList.style.display = 'block';
            setTimeout(() => {
                weatherList.classList.add('visible');
            }, 10);

            weatherList.innerHTML = '';

            const daysWithNames = weather.daily.map(day => {
                const date = new Date(day.date);
                const dayName = date.toLocaleDateString('en-US', { weekday: 'long' });
                return { ...day, dayName, dateObj: date };
            });
            daysWithNames.sort((a, b) => {
                return WEEK_ORDER.indexOf(a.dayName) - WEEK_ORDER.indexOf(b.dayName);
            });

            daysWithNames.forEach((day, index) => {
                setTimeout(() => {
                    const li = document.createElement('li');
                    li.className = 'list-item';
                    li.innerHTML = `
                        <div class="div-block-7">
                        <div>
                            <div class="text-block-2">${day.dayName}</div>
                            <div class="text-block-3">
                            Max: ${day.temperature_max}°C<br>
                            Min: ${day.temperature_min}°C
                            </div>
                        </div>
                        <div class="div-block-8">
                            <img src="/static/images/calendar.png" loading="lazy" class="image-3" />
                        </div>
                        </div>
                    `;
                    weatherList.appendChild(li);
                }, index * 100);
            });
        } catch (error) {
            weatherBlock.style.display = 'none';
            alert(error.message);
        }
    }
  
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        const city = searchInput.value.trim();
        if (city) {
            await searchWeather(city);
        } else {
            weatherBlock.style.display = 'none';
        }
    });
  
    searchButton.addEventListener('click', async function(e) {
        e.preventDefault();
        const city = searchInput.value.trim();
        if (city) {
            await searchWeather(city);
        } else {
            weatherBlock.style.display = 'none';
        }
    });
});
