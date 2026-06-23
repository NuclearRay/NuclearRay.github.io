// ==========================================
// DATA
// ==========================================
const factions = [
    { name: "Marquise de Cat", reach: 10 },
    { name: "Lord of the Hundreds", reach: 9 },
    { name: "Keepers in Iron", reach: 8 },
    { name: "Underground Duchy", reach: 8 },
    { name: "Lilypad Diaspora", reach: 7 },
    { name: "Eyrie Dynasties", reach: 7 },
    { name: "Vagabond", reach: 5 },
    { name: "Riverfolk Company", reach: 5 },
    { name: "Knaves of the Deepwood", reach: 4 },
    { name: "Twilight Council", reach: 4 },
    { name: "Woodland Alliance", reach: 3 },
    { name: "Corvid Conspiracy", reach: 3 },
    { name: "Lizard Cult", reach: 2 }
];

const viableSums = { 2: 17, 3: 18, 4: 21, 5: 25, 6: 28 };

const captains = [
    { name: "Harrier", items: ["Boots", "Crossbow"] },
    { name: "Tinker", items: ["Bag", "Hammer"] },
    { name: "Vagrant", items: ["Tea", "Coins"] },
    { name: "Thief", items: ["Bag", "Boots"] },
    { name: "Scoundrel", items: ["Crossbow", "Tea"] },
    { name: "Ronin", items: ["Boots", "Sword"] },
    { name: "Jailor", items: ["Crossbow", "Bag"] },
    { name: "Ranger", items: ["Sword", "Crossbow"] },
    { name: "Arbiter", items: ["Sword", "Coins"] },
    { name: "Cheat", items: ["Boots", "Tea"] },
    { name: "Gladiator", items: ["Sword", "Hammer"] },
    { name: "Adventurer", items: ["Hammer", "Coins"] }
];
const allItems = [...new Set(captains.flatMap(c => c.items))].sort();

const rawMaps = {
    "Autumn": "1-5, 5-2, 1-10, 10-2, 1-9, 10-12, 2-6, 6-11, 3-6, 3-11, 9-12, 11-12, 3-7, 7-12, 7-8, 4-8, 4-12",
    "Winter": "1-5, 5-6, 2-6, 1-10, 1-11, 4-10, 4-11, 4-9, 9-11, 2-7, 2-12, 3-7, 3-12, 3-8, 8-12, 8-9",
    "Mountain": "1-8, 1-9, 4-8, 4-12, 9-12, 9-10, 10-12, 7-12, 5-10, 5-11, 2-11, 2-6, 3-6, 3-11, 10-11",
    "Lake": "2-7, 2-10, 2-8, 7-10, 8-10, 6-7, 7-11, 6-11, 4-6, 4-5, 5-11, 1-5, 1-9, 3-9, 9-12, 3-12, 3-8",
    "Gorge": "1-5, 2-5, 1-11, 5-11, 2-6, 5-6, 1-10, 6-10, 11-12, 6-7, 9-10, 7-9, 3-12, 3-7, 8-12, 3-8, 8-9, 4-8, 4-9"
};

const parsedMaps = Object.keys(rawMaps).map(name => {
    let adjacency = {};
    let clearingsSet = new Set();
    
    rawMaps[name].split(',').forEach(conn => {
        let parts = conn.split('-').map(s => parseInt(s.trim()));
        if (parts.length === 2 && !isNaN(parts[0]) && !isNaN(parts[1])) {
            let [u, v] = parts;
            clearingsSet.add(u);
            clearingsSet.add(v);
            if (!adjacency[u]) adjacency[u] = [];
            if (!adjacency[v]) adjacency[v] = [];
            if (!adjacency[u].includes(v)) adjacency[u].push(v);
            if (!adjacency[v].includes(u)) adjacency[v].push(u);
        }
    });
    
    return {
        name,
        clearings: Array.from(clearingsSet).sort((a,b)=>a-b),
        adjacency
    };
});

const clearingLocations = {
  "Autumn": {
    "1": { x: 18.87, y: 26.56 },
    "2": { x: 80.45, y: 34.87 },
    "3": { x: 80.99, y: 71.12 },
    "4": { x: 18.87, y: 66.41 },
    "5": { x: 57.70, y: 26.46 },
    "6": { x: 82.36, y: 50.19 },
    "7": { x: 60.56, y: 65.11 },
    "8": { x: 41.49, y: 71.92 },
    "9": { x: 19.01, y: 41.98 },
    "10": { x: 44.07, y: 35.47 },
    "11": { x: 63.42, y: 48.89 },
    "12": { x: 38.22, y: 53.80 }
  },
  "Winter": {
    "1": { x: 15.74, y: 21.94 },
    "2": { x: 85.35, y: 22.33 },
    "3": { x: 84.67, y: 70.26 },
    "4": { x: 16.28, y: 64.80 },
    "5": { x: 40.40, y: 23.40 },
    "6": { x: 61.24, y: 27.10 },
    "7": { x: 86.44, y: 47.56 },
    "8": { x: 62.60, y: 63.73 },
    "9": { x: 40.94, y: 70.55 },
    "10": { x: 14.78, y: 44.25 },
    "11": { x: 42.03, y: 45.12 },
    "12": { x: 65.33, y: 46.10 }
  },
  "Mountain": {
    "1": { x: 13.96, y: 31.49 },
    "2": { x: 85.49, y: 31.58 },
    "3": { x: 84.54, y: 80.78 },
    "4": { x: 14.24, y: 75.42 },
    "5": { x: 57.56, y: 32.95 },
    "6": { x: 86.17, y: 57.88 },
    "7": { x: 47.89, y: 80.87 },
    "8": { x: 12.19, y: 54.09 },
    "9": { x: 33.72, y: 48.44 },
    "10": { x: 51.98, y: 50.48 },
    "11": { x: 62.47, y: 64.12 },
    "12": { x: 35.63, y: 63.34 }
  },
  "Lake": {
    "1": { x: 82.49, y: 67.72 },
    "2": { x: 15.46, y: 22.04 },
    "3": { x: 15.46, y: 65.29 },
    "4": { x: 85.22, y: 22.43 },
    "5": { x: 86.04, y: 47.95 },
    "6": { x: 65.05, y: 26.81 },
    "7": { x: 44.07, y: 23.69 },
    "8": { x: 13.96, y: 44.05 },
    "9": { x: 57.43, y: 70.26 },
    "10": { x: 37.94, y: 40.45 },
    "11": { x: 64.92, y: 45.90 },
    "12": { x: 41.35, y: 59.05 }
  },
  "Gorge": {
    "1": { x: 23.77, y: 24.46 },
    "2": { x: 79.77, y: 25.46 },
    "3": { x: 70.64, y: 69.12 },
    "4": { x: 21.87, y: 71.42 },
    "5": { x: 53.07, y: 25.36 },
    "6": { x: 75.68, y: 39.58 },
    "7": { x: 74.05, y: 53.90 },
    "8": { x: 45.30, y: 66.71 },
    "9": { x: 19.01, y: 55.40 },
    "10": { x: 20.23, y: 41.38 },
    "11": { x: 43.94, y: 36.87 },
    "12": { x: 48.30, y: 51.59 }
  }
};

const suitColors = {
  "Fox": { bg: "#e74c3c", border: "#c0392b" },
  "Mouse": { bg: "#e67e22", border: "#d35400" },
  "Rabbit": { bg: "#f1c40f", border: "#f39c12" }
};

// ==========================================
// UTILS
// ==========================================
function getCombinations(array, size) {
    let result = [];
    let f = function(prefix, array) {
        for (let i = 0; i < array.length; i++) {
            let newPrefix = prefix.concat([array[i]]);
            if (newPrefix.length === size) {
                result.push(newPrefix);
            } else {
                f(newPrefix, array.slice(i + 1));
            }
        }
    }
    f([], array);
    return result;
}

function shuffle(array) {
    let currentIndex = array.length, randomIndex;
    while (currentIndex !== 0) {
        randomIndex = Math.floor(Math.random() * currentIndex);
        currentIndex--;
        [array[currentIndex], array[randomIndex]] = [array[randomIndex], array[currentIndex]];
    }
    return array;
}

// ==========================================
// UI INIT
// ==========================================
const playerCounts = Object.keys(viableSums).map(Number).sort((a,b)=>a-b);

// Tab switching
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        btn.classList.add('active');
        document.getElementById(btn.dataset.tab).classList.add('active');
    });
});

// Factions Init
const factionPlayersDiv = document.getElementById('faction-players');
playerCounts.forEach((p, i) => {
    factionPlayersDiv.innerHTML += `
        <label class="radio-item">
            <input type="radio" name="faction-p" value="${p}" ${i===2?'checked':''}> ${p}
        </label>`;
});
const factionReqsDiv = document.getElementById('faction-reqs');
factions.forEach(f => {
    factionReqsDiv.innerHTML += `
        <label class="checkbox-item">
            <input type="checkbox" name="faction-r" value="${f.name}"> ${f.name}
        </label>`;
});

// Knaves Init
const knaveReqsDiv = document.getElementById('knave-reqs');
captains.forEach(c => {
    knaveReqsDiv.innerHTML += `
        <label class="checkbox-item">
            <input type="checkbox" name="knave-r" value="${c.name}"> ${c.name}
        </label>`;
});
const itemReqsDiv = document.getElementById('item-reqs');
allItems.forEach(i => {
    itemReqsDiv.innerHTML += `
        <label class="checkbox-item">
            <input type="checkbox" name="item-r" value="${i}"> ${i}
        </label>`;
});

// Draft Init
const draftPlayersDiv = document.getElementById('draft-players');
playerCounts.forEach((p, i) => {
    draftPlayersDiv.innerHTML += `
        <label class="radio-item">
            <input type="radio" name="draft-p" value="${p}" ${i===2?'checked':''}> ${p}
        </label>`;
});
const draftExclusionsDiv = document.getElementById('draft-exclusions');
factions.forEach(f => {
    draftExclusionsDiv.innerHTML += `
        <label class="checkbox-item">
            <input type="checkbox" name="draft-e" value="${f.name}"> ${f.name}
        </label>`;
});

// Map Init
const mapSelect = document.getElementById('map-select');
parsedMaps.forEach((m, i) => {
    mapSelect.innerHTML += `<option value="${i}">${m.name}</option>`;
});

// ==========================================
// LOGIC: FACTIONS
// ==========================================
function updateFactions() {
    let p = parseInt(document.querySelector('input[name="faction-p"]:checked').value);
    let reqs = Array.from(document.querySelectorAll('input[name="faction-r"]:checked')).map(cb => cb.value);
    
    let reqReach = viableSums[p];
    let combos = getCombinations(factions, p);
    let validCombos = [];

    combos.forEach(combo => {
        let names = combo.map(f => f.name);
        let hasAllReqs = reqs.every(r => names.includes(r));
        if (!hasAllReqs) return;

        let totalReach = combo.reduce((sum, f) => sum + f.reach, 0);
        if (totalReach >= reqReach) {
            let sorted = combo.map(f=>f.name).sort((a,b) => {
                let rA = factions.find(f=>f.name===a).reach;
                let rB = factions.find(f=>f.name===b).reach;
                return rB - rA;
            });
            validCombos.push({ names: sorted, reach: totalReach });
        }
    });

    validCombos.sort((a,b) => b.reach - a.reach);

    document.getElementById('faction-summary').innerText = `Required Reach for ${p} Players: ${reqReach} | Found ${validCombos.length} valid combos.`;
    
    let html = '';
    validCombos.forEach(vc => {
        html += `<div class="result-card">
            <div class="reach">Reach: ${vc.reach}</div>
            <div>${vc.names.join(", ")}</div>
        </div>`;
    });
    document.getElementById('faction-results').innerHTML = html;
}

document.querySelectorAll('input[name="faction-p"], input[name="faction-r"]').forEach(el => el.addEventListener('change', updateFactions));
document.getElementById('clear-faction-filters').addEventListener('click', () => {
    document.querySelectorAll('input[name="faction-r"]').forEach(cb => cb.checked = false);
    updateFactions();
});

// ==========================================
// LOGIC: KNAVES
// ==========================================
function updateKnaves() {
    let reqCaps = Array.from(document.querySelectorAll('input[name="knave-r"]:checked')).map(cb => cb.value);
    let reqItems = Array.from(document.querySelectorAll('input[name="item-r"]:checked')).map(cb => cb.value);
    
    let combos = getCombinations(captains, 3);
    let validCombos = [];

    combos.forEach(combo => {
        let names = combo.map(c => c.name);
        let hasAllCaps = reqCaps.every(r => names.includes(r));
        if (!hasAllCaps) return;

        let items = [];
        combo.forEach(c => items.push(...c.items));
        let uniqueItems = new Set(items);
        
        if (uniqueItems.size < 6) return; // not unique

        let hasAllItems = reqItems.every(r => uniqueItems.has(r));
        if (!hasAllItems) return;

        validCombos.push({ names, items });
    });

    document.getElementById('knave-summary').innerText = `Found ${validCombos.length} valid combinations.`;
    
    let html = '';
    validCombos.forEach(vc => {
        html += `<div class="result-card">
            <div class="reach">${vc.names.join(" + ")}</div>
            <div class="items">Items: ${vc.items.join(", ")}</div>
        </div>`;
    });
    document.getElementById('knave-results').innerHTML = html;
}

document.querySelectorAll('input[name="knave-r"], input[name="item-r"]').forEach(el => el.addEventListener('change', updateKnaves));
document.getElementById('clear-knave-filters').addEventListener('click', () => {
    document.querySelectorAll('input[name="knave-r"], input[name="item-r"]').forEach(cb => cb.checked = false);
    updateKnaves();
});

// ==========================================
// LOGIC: DRAFT
// ==========================================
function clearDraft() {
    document.getElementById('draft-error').innerText = '';
    document.getElementById('draft-results').innerHTML = '<p class="placeholder">Select your options and click a generate button.</p>';
}

document.querySelectorAll('input[name="draft-p"], input[name="draft-e"]').forEach(el => el.addEventListener('change', clearDraft));
document.getElementById('clear-draft-filters').addEventListener('click', () => {
    document.querySelectorAll('input[name="draft-e"]').forEach(cb => cb.checked = false);
    clearDraft();
});

function getAvailableDraftFactions() {
    let excl = Array.from(document.querySelectorAll('input[name="draft-e"]:checked')).map(cb => cb.value);
    return factions.filter(f => !excl.includes(f.name));
}

document.getElementById('btn-draft-random').addEventListener('click', () => {
    let p = parseInt(document.querySelector('input[name="draft-p"]:checked').value);
    let reqReach = viableSums[p];
    let avail = getAvailableDraftFactions();
    let draftSize = p + 1;

    if (avail.length < draftSize) {
        document.getElementById('draft-error').innerText = "Not enough available factions.";
        return;
    }

    let combos = getCombinations(avail, draftSize);
    let validDrafts = [];

    combos.forEach(combo => {
        let names = combo.map(f => f.name);
        if (names.includes("Knaves of the Deepwood") && names.includes("Vagabond")) return;

        let sorted = [...combo].sort((a,b) => a.reach - b.reach);
        let worstCase = sorted.slice(0, p).reduce((sum, f) => sum + f.reach, 0);

        if (worstCase >= reqReach) {
            validDrafts.push(combo);
        }
    });

    if (validDrafts.length === 0) {
        document.getElementById('draft-error').innerText = "No valid drafts found for the selected options.";
        return;
    }

    let chosen = validDrafts[Math.floor(Math.random() * validDrafts.length)];
    displayDraft(chosen, p, reqReach);
});

document.getElementById('btn-draft-adset').addEventListener('click', () => {
    let p = parseInt(document.querySelector('input[name="draft-p"]:checked').value);
    let reqReach = viableSums[p];
    let avail = getAvailableDraftFactions();
    let draftSize = p + 1;

    if (avail.length < draftSize) {
        document.getElementById('draft-error').innerText = "Not enough available factions.";
        return;
    }

    let militants = avail.filter(f => f.reach >= 7);
    if (militants.length === 0) {
        document.getElementById('draft-error').innerText = "No militant factions available.";
        return;
    }

    let chosen = null;
    for (let i=0; i<1000; i++) {
        let pool = shuffle([...avail]);
        let selectedMilitant = null;
        let rest = [];

        for (let f of pool) {
            if (!selectedMilitant && f.reach >= 7) {
                selectedMilitant = f;
            } else {
                rest.push(f);
            }
        }

        if (selectedMilitant) {
            let draft = [selectedMilitant, ...rest.slice(0, draftSize - 1)];
            let names = draft.map(f => f.name);
            if (names.includes("Knaves of the Deepwood") && names.includes("Vagabond")) continue;
            
            chosen = draft;
            break;
        }
    }

    if (!chosen) {
        document.getElementById('draft-error').innerText = "Failed to generate Standard Adset draft.";
        return;
    }

    displayDraft(chosen, p, reqReach);
});

function displayDraft(draft, p, reqReach) {
    document.getElementById('draft-error').innerText = '';
    
    let sortedAsc = [...draft].sort((a,b) => a.reach - b.reach);
    let worstCase = sortedAsc.slice(0, p).reduce((sum, f) => sum + f.reach, 0);
    
    draft.sort((a,b) => b.reach - a.reach);
    
    let html = `<div style="margin-bottom: 10px;">Draft pool of ${draft.length} factions for ${p} players:</div>`;
    draft.forEach(f => {
        html += `<div class="draft-item">• ${f.name} (Reach: ${f.reach})</div>`;
    });
    
    html += `<div style="margin-top: 15px; font-style: italic; color: #a0a0b0; font-size: 0.9rem;">
        Worst-case reach for ${p} players: ${worstCase} (Required: ${reqReach})
    </div>`;
    
    document.getElementById('draft-results').innerHTML = html;
}

// ==========================================
// LOGIC: MAP
// ==========================================
const mapContainer = document.getElementById('map-container');
const mapImage = document.getElementById('map-image');
const mapOverlay = document.getElementById('map-overlay');
const btnMapRandom = document.getElementById('btn-map-random');

function renderMapImage() {
    let idx = parseInt(mapSelect.value);
    let map = parsedMaps[idx];
    mapImage.src = `images/${map.name}.webp`;
    mapContainer.style.display = 'block';
    mapOverlay.innerHTML = '';
}

mapSelect.addEventListener('change', () => {
    document.getElementById('map-error').innerText = '';
    document.getElementById('map-results').innerHTML = '<p class="placeholder">Select a map and click \'Randomize Clearings\'.</p>';
    renderMapImage();
});

btnMapRandom.addEventListener('click', () => {
    let idx = parseInt(mapSelect.value);
    let map = parsedMaps[idx];
    let n = map.clearings.length;

    renderMapImage(); // Ensure map is visible and cleared

    if (n % 3 !== 0) {
        document.getElementById('map-error').innerText = `Number of clearings (${n}) must be divisible by 3.`;
        return;
    }

    let suitsCount = n / 3;
    let basePool = [];
    for(let i=0; i<suitsCount; i++) {
        basePool.push({name: "Fox", icon: "images/Fox_Icon.png"});
        basePool.push({name: "Mouse", icon: "images/Mouse_Icon.png"});
        basePool.push({name: "Rabbit", icon: "images/Bunny_Icon.png"});
    }

    let assignment = {};
    let valid = false;

    for (let attempts=0; attempts<10000; attempts++) {
        let pool = shuffle([...basePool]);
        assignment = {};
        map.clearings.forEach((c, i) => assignment[c] = pool[i]);

        valid = true;
        outer: for (let b of map.clearings) {
            let suitB = assignment[b].name;
            let neighbors = map.adjacency[b] || [];
            
            for (let i = 0; i < neighbors.length; i++) {
                let a = neighbors[i];
                if (assignment[a].name !== suitB) continue;
                
                for (let j = i + 1; j < neighbors.length; j++) {
                    let c = neighbors[j];
                    if (assignment[c].name === suitB) {
                        valid = false;
                        break outer;
                    }
                }
            }
        }

        if (valid) break;
    }

    if (!valid) {
        document.getElementById('map-error').innerText = "Failed to find a valid layout.";
        return;
    }

    document.getElementById('map-error').innerText = '';
    
    // Render suit markers on the map overlay
    mapOverlay.innerHTML = '';
    let locs = clearingLocations[map.name];
    map.clearings.forEach(c => {
        let s = assignment[c];
        let color = suitColors[s.name];
        let loc = locs[c];
        
        let marker = document.createElement('div');
        marker.className = 'clearing-marker';
        marker.style.left = `${loc.x}%`;
        marker.style.top = `${loc.y}%`;
        marker.style.background = '#fff';
        marker.style.borderColor = color.bg;
        let img = document.createElement('img');
        img.src = s.icon;
        img.alt = s.name;
        img.style.width = '70%';
        img.style.height = '70%';
        img.style.objectFit = 'contain';
        marker.appendChild(img);
        marker.title = `Clearing ${c}: ${s.name}`;
        mapOverlay.appendChild(marker);
    });
    
    // Keep text list as well
    let html = `<div style="margin-bottom: 10px; font-weight: bold; color: var(--accent);">Valid layout generated:</div>`;
    map.clearings.forEach(c => {
        let s = assignment[c];
        html += `<div class="draft-item">Clearing ${String(c).padStart(2, '0')}: ${s.name}</div>`;
    });
    document.getElementById('map-results').innerHTML = html;
});

// Init calculations
updateFactions();
updateKnaves();
renderMapImage(); // Show initial map
