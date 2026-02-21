document.getElementById('analyzeBtn').addEventListener('click', async () => {
    const message = document.getElementById('messageInput').value.trim();
    if (!message) {
        // Shake animation for empty input
        const wrapper = document.querySelector('.textarea-wrapper');
        wrapper.style.animation = 'shake 0.4s ease';
        setTimeout(() => wrapper.style.animation = '', 400);
        return;
    }

    const btn = document.getElementById('analyzeBtn');
    const btnText = btn.querySelector('.btn-text');
    const loader = btn.querySelector('.btn-loader');
    const resultCard = document.getElementById('resultCard');

    // UI Loading State
    btn.disabled = true;
    btnText.textContent = "Analyzing...";
    loader.classList.remove('hidden');

    // Hide old result with animation
    if (!resultCard.classList.contains('hidden')) {
        resultCard.style.opacity = '0';
        resultCard.style.transform = 'translateY(10px)';
        await new Promise(r => setTimeout(r, 300));
        resultCard.classList.add('hidden');
        resultCard.style = '';
    }

    try {
        const response = await fetch('/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: message })
        });

        if (!response.ok) throw new Error(`Server error: ${response.status}`);

        const data = await response.json();

        // Add a slight artificial delay for the "AI thinking" effect to make it feel more real
        setTimeout(() => {
            displayResult(data);
            btn.disabled = false;
            btnText.textContent = "Analyze Risk Level";
            loader.classList.add('hidden');
        }, 600);

    } catch (error) {
        console.error("Error analyzing message:", error);
        alert("Server connection failed. Ensure backend is running.");
        btn.disabled = false;
        btnText.textContent = "Analyze Risk Level";
        loader.classList.add('hidden');
    }
});

function displayResult(data) {
    const resultCard = document.getElementById('resultCard');
    const riskLevel = document.getElementById('riskLevel');
    const verdictIcon = document.getElementById('verdictIcon');
    const confidenceValue = document.getElementById('confidenceValue');
    const confidenceBar = document.getElementById('confidenceBar');
    const reasonsList = document.getElementById('reasonsList');
    const highlightBox = document.querySelector('.highlight-box');
    const highlightedWords = document.getElementById('highlightedWords');

    // Reset card classes
    resultCard.className = 'result-card glass-panel';

    // Set text, class, and icon based on prediction
    const prediction = data.prediction.toLowerCase();
    riskLevel.textContent = data.prediction;

    if (prediction === 'safe') {
        resultCard.classList.add('safe');
        verdictIcon.textContent = '🛡️';
    } else if (prediction === 'suspicious') {
        resultCard.classList.add('suspicious');
        verdictIcon.textContent = '⚠️';
    } else if (prediction === 'dangerous') {
        resultCard.classList.add('dangerous');
        verdictIcon.textContent = '🚨';
    } else {
        resultCard.classList.add('safe');
        verdictIcon.textContent = '🛡️';
    }

    // Animate Confidence Bar
    const confidencePct = Math.round(data.confidence * 100);
    confidenceValue.textContent = `${confidencePct}%`;
    confidenceBar.style.width = '0%';

    // Staggered typing effect for reasons
    reasonsList.innerHTML = '';
    if (data.reasons && data.reasons.length > 0) {
        data.reasons.forEach((reason, index) => {
            const li = document.createElement('li');
            li.textContent = reason;
            li.style.opacity = '0';
            li.style.transform = 'translateX(-10px)';
            li.style.transition = 'all 0.3s ease';
            reasonsList.appendChild(li);

            setTimeout(() => {
                li.style.opacity = '1';
                li.style.transform = 'translateX(0)';
            }, 100 + (index * 150));
        });
    }

    // Set highlighted tags
    highlightedWords.innerHTML = '';
    if (data.highlighted_words && data.highlighted_words.length > 0) {
        highlightBox.classList.remove('hidden');
        data.highlighted_words.forEach(word => {
            const span = document.createElement('span');
            span.className = 'tag';
            span.textContent = word;
            highlightedWords.appendChild(span);
        });
    } else {
        highlightBox.classList.add('hidden');
    }

    // Show result card
    resultCard.classList.remove('hidden');

    // Trigger bar fill animation
    setTimeout(() => {
        confidenceBar.style.width = `${confidencePct}%`;
    }, 100);
}

// Add CSS for shake animation dynamically
const style = document.createElement('style');
style.innerHTML = `
@keyframes shake {
    0%, 100% { transform: translateX(0); }
    25% { transform: translateX(-5px); }
    50% { transform: translateX(5px); }
    75% { transform: translateX(-5px); }
}
`;
document.head.appendChild(style);
