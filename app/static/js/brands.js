// static/js/scripts.js

document.addEventListener('DOMContentLoaded', () => {
    // Get references to the search input and all brand cards
    const searchInput = document.getElementById('brandSearchInput');
    const brandCards = document.querySelectorAll('.brand-card');
    const generateSloganButtons = document.querySelectorAll('.generate-slogan-btn');
    const generateDescriptionButtons = document.querySelectorAll('.generate-description-btn'); // New button selector

    // Function to filter brand cards based on search input
    const filterBrands = () => {
        // Get the current value from the search input, trim whitespace, and convert to lowercase for case-insensitive search
        const searchTerm = searchInput.value.trim().toLowerCase();

        // Iterate over each brand card
        brandCards.forEach(card => {
            // Get the brand name from the card's title, convert to lowercase
            const brandName = card.querySelector('.card-title').textContent.toLowerCase();

            // Check if the brand name includes the search term
            if (brandName.includes(searchTerm)) {
                // If it includes the term, display the card (remove Tailwind's 'hidden' class)
                card.style.display = 'block';
                card.classList.remove('hidden');
            } else {
                // If it doesn't include the term, hide the card (add Tailwind's 'hidden' class)
                card.style.display = 'none';
                card.classList.add('hidden');
            }
        });
    };

    // Add an event listener to the search input for 'input' events
    searchInput.addEventListener('input', filterBrands);

    // --- Gemini API Integration for Slogan Generation ---
    generateSloganButtons.forEach(button => {
        button.addEventListener('click', async (event) => {
            const brandName = event.target.dataset.brandName;
            const brandId = event.target.dataset.brandId;
            const sloganDisplayElement = document.getElementById(`slogan-${brandId}`);

            // Clear previous slogan and show loading indicator
            sloganDisplayElement.textContent = 'Generating slogan...';
            sloganDisplayElement.classList.add('text-gray-500'); // Add a loading text style
            button.disabled = true; // Disable button during generation

            try {
                let chatHistory = [];
                const prompt = `Generate a short, catchy, and creative slogan for a brand named "${brandName}". Keep it concise, under 15 words.`;
                chatHistory.push({ role: "user", parts: [{ text: prompt }] });

                const payload = { contents: chatHistory };
                const apiKey = ""; // Canvas will automatically provide the API key
                const apiUrl = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${apiKey}`;

                const response = await fetch(apiUrl, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                const result = await response.json();

                if (result.candidates && result.candidates.length > 0 &&
                    result.candidates[0].content && result.candidates[0].content.parts &&
                    result.candidates[0].content.parts.length > 0) {
                    const text = result.candidates[0].content.parts[0].text;
                    sloganDisplayElement.textContent = text;
                    sloganDisplayElement.classList.remove('text-gray-500'); // Remove loading text style
                } else {
                    sloganDisplayElement.textContent = 'Could not generate slogan. Please try again.';
                    sloganDisplayElement.classList.add('text-red-500'); // Indicate error
                    console.error('Gemini API response structure unexpected for slogan:', result);
                }
            } catch (error) {
                sloganDisplayElement.textContent = 'Error generating slogan.';
                sloganDisplayElement.classList.add('text-red-500'); // Indicate error
                console.error('Error calling Gemini API for slogan:', error);
            } finally {
                button.disabled = false; // Re-enable button
            }
        });
    });

    // --- Gemini API Integration for Description Generation (NEW FEATURE) ---
    generateDescriptionButtons.forEach(button => {
        button.addEventListener('click', async (event) => {
            const brandName = event.target.dataset.brandName;
            const brandId = event.target.dataset.brandId;
            const descriptionDisplayElement = document.getElementById(`description-${brandId}`);

            // Clear previous description and show loading indicator
            descriptionDisplayElement.textContent = 'Generating description...';
            descriptionDisplayElement.classList.add('text-gray-500'); // Add a loading text style
            button.disabled = true; // Disable button during generation

            try {
                let chatHistory = [];
                const prompt = `Write a concise and compelling marketing description for a brand named "${brandName}". Focus on its potential industry or product type. Keep it under 50 words.`;
                chatHistory.push({ role: "user", parts: [{ text: prompt }] });

                const payload = { contents: chatHistory };
                const apiKey = ""; // Canvas will automatically provide the API key
                const apiUrl = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${apiKey}`;

                const response = await fetch(apiUrl, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                const result = await response.json();

                if (result.candidates && result.candidates.length > 0 &&
                    result.candidates[0].content && result.candidates[0].content.parts &&
                    result.candidates[0].content.parts.length > 0) {
                    const text = result.candidates[0].content.parts[0].text;
                    descriptionDisplayElement.textContent = text;
                    descriptionDisplayElement.classList.remove('text-gray-500'); // Remove loading text style
                } else {
                    descriptionDisplayElement.textContent = 'Could not generate description. Please try again.';
                    descriptionDisplayElement.classList.add('text-red-500'); // Indicate error
                    console.error('Gemini API response structure unexpected for description:', result);
                }
            } catch (error) {
                descriptionDisplayElement.textContent = 'Error generating description.';
                descriptionDisplayElement.classList.add('text-red-500'); // Indicate error
                console.error('Error calling Gemini API for description:', error);
            } finally {
                button.disabled = false; // Re-enable button
            }
        });
    });
});

// A simple utility function that could be expanded for other dynamic behaviors
function logMessage(message) {
    console.log(message);
}
