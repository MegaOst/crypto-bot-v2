async function updateStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        document.getElementById('bot-status').textContent = 
            data.running ? 'Running ✅' : 'Stopped ❌';
    } catch (error) {
        document.getElementById('bot-status').textContent = 'Error ⚠️';
    }
}

async function updatePositions() {
    try {
        const response = await fetch('/api/positions');
        const positions = await response.json();
        const list = document.getElementById('positions-list');
        
        if (positions.length === 0) {
            list.innerHTML = '<p>Aucune position active</p>';
        } else {
            list.innerHTML = positions.map(p => `
                <div class="position">
                    <strong>${p.symbol}</strong>: ${p.quantity} @ ${p.entry_price}
                </div>
            `).join('');
        }
    } catch (error) {
        document.getElementById('positions-list').innerHTML = 
            '<p>Erreur de chargement</p>';
    }
}

// Mise à jour toutes les 5 secondes
setInterval(() => {
    updateStatus();
    updatePositions();
}, 5000);

// Chargement initial
updateStatus();
updatePositions();