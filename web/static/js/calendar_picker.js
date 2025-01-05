// 1) Primarni element, v katerega vse vstavljamo
const app = document.getElementById('app');

// Ustvarimo tri glavne predele:
const top_container = document.createElement('div');
top_container.classList.add('top_container');
app.appendChild(top_container);

const mid_container = document.createElement('div');
mid_container.classList.add('mid_container');
app.appendChild(mid_container);

const bottom_container = document.createElement('div');
bottom_container.classList.add('bottom_container');
app.appendChild(bottom_container);

// -----------------------------------------
// ZGORNJI DEL - top_container
// -----------------------------------------
// Dodaj "headerBar" v top_container
const headerBar = document.createElement('div');
headerBar.classList.add('header-bar');
top_container.appendChild(headerBar);

// -----------------------------------------
// SREDNJI DEL mid_container
// -----------------------------------------
// V mid_container bo leva stran (z gumbi in izpisom) ter desno stran (ml_detector)

// 1) LEVI blok (leftBlock) za gumbovje + resultContainer
const leftBlock = document.createElement('div');
leftBlock.classList.add('left-block');
mid_container.appendChild(leftBlock);

// -- selectionContainer --
const selectionContainer = document.createElement('div');
selectionContainer.classList.add('selection-container');
leftBlock.appendChild(selectionContainer);

// -- resultContainer --
const resultContainer = document.createElement('div');
resultContainer.classList.add('result-container');
leftBlock.appendChild(resultContainer);

// 2) DESNI blok (ml_detector)
const ml_detector = document.createElement('div');
ml_detector.classList.add('ml_detector');
// Začetno besedilo
ml_detector.innerHTML = '<p>Tu je nov pravokotnik <strong>ml_detector</strong><br>Podatki se nalagajo...</p>';
mid_container.appendChild(ml_detector);

// -----------------------------------------
//bottom_container (fiksiran)
// -----------------------------------------
const mainRectangle = document.createElement('div');
mainRectangle.classList.add('main-rectangle');
bottom_container.appendChild(mainRectangle);

// Notranji 4 deli
const rect1 = document.createElement('div');
rect1.classList.add('rectangle', 'gray');
const rect2 = document.createElement('div');
rect2.classList.add('rectangle', 'white');
const rect3 = document.createElement('div');
rect3.classList.add('rectangle', 'gray');
const rect4 = document.createElement('div');
rect4.classList.add('rectangle', 'white');

mainRectangle.appendChild(rect1);
mainRectangle.appendChild(rect2);
mainRectangle.appendChild(rect3);
mainRectangle.appendChild(rect4);

// -----------------------------------------
// OBSTOJEČA LOGIKA: LETA, MESECI, PICKERJI
// -----------------------------------------
const years = [2023, 2024, 2025];
const months = ['Jan', 'Feb', 'Mar', 'Apr', 'Maj', 'Jun', 'Jul', 'Avg', 'Sep', 'Okt', 'Nov', 'Dec'];

let choosen_graph1 = '';
let choosen_graph3 = '';

function clearLowerSelections(level) {
    const levels = ['year', 'month', 'day', 'hour', 'minute'];
    let startIndex = levels.indexOf(level);
    const nodes = Array.from(selectionContainer.children);
    nodes.forEach(node => {
        if (levels.indexOf(node.dataset.level) >= startIndex) {
            selectionContainer.removeChild(node);
        }
    });
}

function createYearPicker() {
    clearLowerSelections('year');
    const container = document.createElement('div');
    container.classList.add('picker');
    container.dataset.level = 'year';

    years.forEach(year => {
        const button = document.createElement('button');
        button.innerText = year;
        button.onclick = () => selectYear(year, button);
        container.appendChild(button);
    });
    selectionContainer.appendChild(container);
}

function selectYear(year, button) {
    clearLowerSelections('month');
    highlightButton(button);
    const container = document.createElement('div');
    container.classList.add('picker');
    container.dataset.level = 'month';

    months.forEach((month, index) => {
        const btn = document.createElement('button');
        btn.innerText = month;
        btn.onclick = () => selectMonth(year, index + 1, btn);
        container.appendChild(btn);
    });
    selectionContainer.appendChild(container);
}

function selectMonth(year, month, button) {
    clearLowerSelections('day');
    highlightButton(button);
    const container = document.createElement('div');
    container.classList.add('picker');
    container.dataset.level = 'day';

    const daysInMonth = new Date(year, month, 0).getDate();
    for (let day = 1; day <= daysInMonth; day++) {
        const btn = document.createElement('button');
        btn.innerText = day;
        btn.onclick = () => selectDay(year, month, day, btn);
        container.appendChild(btn);
    }
    selectionContainer.appendChild(container);
}

function selectDay(year, month, day, button) {
    clearLowerSelections('hour');
    highlightButton(button);
    const container = document.createElement('div');
    container.classList.add('picker');
    container.dataset.level = 'hour';

    fetch(`/get_hour_status?year=${year}&month=${month}&day=${day}`)
        .then(response => response.json())
        .then(status => {
            for (let hour = 0; hour < 24; hour++) {
                const btn = document.createElement('button');
                btn.innerText = `${hour}:00`;
                btn.onclick = () => selectHour(year, month, day, hour, btn);

                if (status[hour] === 'g') {
                    btn.style.backgroundColor = 'rgba(0, 255, 0, 0.3)';
                } else if (status[hour] === 'r') {
                    btn.style.backgroundColor = 'rgba(255, 0, 0, 0.3)';
                } else {
                    btn.style.backgroundColor = 'white';
                }
                container.appendChild(btn);
            }
        })
        .catch(error => {
            console.error('Napaka pri nalaganju statusa ur:', error);
            for (let hour = 0; hour < 24; hour++) {
                const btn = document.createElement('button');
                btn.innerText = `${hour}:00`;
                btn.onclick = () => selectHour(year, month, day, hour, btn);
                container.appendChild(btn);
            }
        });
    selectionContainer.appendChild(container);
}

function selectHour(year, month, day, hour, button) {
    clearLowerSelections('minute');
    highlightButton(button);
    const container = document.createElement('div');
    container.classList.add('picker');
    container.dataset.level = 'minute';

    fetch(`/get_minute_status?year=${year}&month=${month}&day=${day}&hour=${hour}`)
        .then(response => response.json())
        .then(status => {
            for (let minute = 0; minute < 60; minute += 10) {
                const btn = document.createElement('button');
                btn.innerText = `${hour}:${minute.toString().padStart(2, '0')}`;
                btn.onclick = () => showResult(year, month, day, hour, minute, btn);

                const index = minute / 10;
                if (status[index] === 'g') {
                    btn.style.backgroundColor = 'rgba(0, 255, 0, 0.3)';
                } else if (status[index] === 'r') {
                    btn.style.backgroundColor = 'rgba(255, 0, 0, 0.3)';
                } else {
                    btn.style.backgroundColor = 'white';
                }
                container.appendChild(btn);
            }
        })
        .catch(error => {
            console.error('Napaka pri nalaganju statusa minut:', error);
            for (let minute = 0; minute < 60; minute += 10) {
                const btn = document.createElement('button');
                btn.innerText = `${hour}:${minute.toString().padStart(2, '0')}`;
                btn.onclick = () => showResult(year, month, day, hour, minute, btn);
                container.appendChild(btn);
            }
        });
    selectionContainer.appendChild(container);
}

function showResult(year, month, day, hour, minute, button) {
    highlightButton(button);

    let koncne_min = (minute + 10) % 60;
    let koncna_hour = hour + Math.floor((minute + 10) / 60);
    let koncni_dan = day;
    let koncni_mesec = month;
    let konco_leto = year;

    const daysInMonth = new Date(year, month, 0).getDate();
    if (koncna_hour === 24) {
        koncna_hour = 0;
        koncni_dan++;
        if (koncni_dan > daysInMonth) {
            koncni_dan = 1;
            koncni_mesec++;
            if (koncni_mesec > 12) {
                koncni_mesec = 1;
                konco_leto++;
            }
        }
    }

    const startUnix = Math.floor(new Date(year, month - 1, day, hour, minute).getTime() / 1000) + 3600;
    const endUnix = Math.floor(new Date(konco_leto, koncni_mesec - 1, koncni_dan, koncna_hour, koncne_min).getTime() / 1000) + 3600 - 1;
    const timestamp = new Date().getTime();

    function fetchWithTimeout(url, options = {}, timeout = 10000) {
        return Promise.race([
            fetch(url, options),
            new Promise((_, reject) =>
                setTimeout(() => reject(new Error('Timeout')), timeout)
            )
        ]);
    }

    fetch(`/check_table?start=${startUnix}&end=${endUnix}`)
        .then(response => response.json())
        .then(data => {
            const exists = data.exists ? 'DA' : 'NE';
            const columns = data.columns || 0;
            const rows = data.rows || 0;

            resultContainer.innerHTML = `
                <div class="result-box">
                    Izbrano: ${day}. ${months[month - 1]}, ${year}, ${hour}:${minute.toString().padStart(2, '0')} -
                    ${koncni_dan}. ${months[koncni_mesec - 1]}, ${konco_leto}, ${koncna_hour}:${koncne_min.toString().padStart(2, '0')}
                    (UNIX: ${startUnix} - ${endUnix})<br>
                    Obstaja tabela: ${exists}<br>
                    Stolpci: ${columns}, Vrstice: ${rows}
                </div>
            `;

            if (data.exists) {
                const tableName = `main_tab_${startUnix}_${endUnix}`;
                rect2.innerHTML = '<p>Nalaganje grafa...</p>';
                rect4.innerHTML = '<p>Nalaganje grafa...</p>';

                fetchWithTimeout(`/graph_lat_lon?table=${tableName}&t=${timestamp}`, {}, 10000)
                    .then(response => {
                        if (!response.ok) throw new Error(`Napaka HTTP ${response.status}`);
                        const img1 = document.createElement('img');
                        img1.src = `/graph_lat_lon?table=${tableName}&t=${timestamp}`;
                        img1.alt = 'Graf Latitude/Longitude';
                        img1.style.width = '100%';
                        img1.style.height = '100%';
                        rect2.innerHTML = '';
                        rect2.appendChild(img1);

                        console.log('Graf lat/lon uspešno naložen.');
                        return fetchWithTimeout(`/graph_sv?table=${tableName}&t=${timestamp}`, {}, 10000);
                    })
                    .then(response => {
                        if (!response.ok) throw new Error(`Napaka HTTP ${response.status}`);
                        const contentType = response.headers.get('Content-Type');
                        if (contentType && contentType.includes('application/json')) {
                            return response.json(); // Prazen graf
                        } else {
                            const img2 = document.createElement('img');
                            img2.src = `/graph_sv?table=${tableName}&t=${timestamp}`;
                            img2.alt = 'Graf Signalov (sv_*_cno)';
                            img2.style.width = '100%';
                            img2.style.height = '100%';
                            rect4.innerHTML = '';
                            rect4.appendChild(img2);

                            console.log('Graf sv_*_cno uspešno naložen.');
                            return null;
                        }
                    })
                    .then(data => {
                        if (data && data.status === 'empty') {
                            rect4.innerHTML = '<p>Graf ni na voljo (prazni podatki).</p>';
                            console.log('Graf sv_*_cno je prazen.');
                        }
                    })
                    .catch(error => {
                        console.error('Napaka pri nalaganju grafa:', error);
                        rect4.innerHTML = '<p>Napaka pri nalaganju grafa.</p>';
                    });
            } else {
                rect2.innerHTML = '<p>Graf ni na voljo.</p>';
                rect4.innerHTML = '<p>Graf ni na voljo.</p>';
            }
        })
        .catch(error => {
            console.error('Napaka:', error);
            resultContainer.innerHTML = '<div class="result-box">Napaka pri nalaganju podatkov!</div>';
            rect2.innerHTML = '<p>Graf ni na voljo.</p>';
            rect4.innerHTML = '<p>Graf ni na voljo.</p>';
        });
}

function highlightButton(button) {
    const parent = button.parentElement;
    Array.from(parent.children).forEach(btn => btn.classList.remove('selected'));
    button.classList.add('selected');
}

function highlightRectButton(button, container) {
    Array.from(container.children).forEach(b => b.classList.remove('selected'));
    button.classList.add('selected');
}

// -----------------------------------------
// DODAJANJE GUMBOV v rect1
// -----------------------------------------
const rect1ButtonsContainer = document.createElement('div');
rect1ButtonsContainer.classList.add('rect-buttons');
rect1.appendChild(rect1ButtonsContainer);

const rect1ChoiceLabel = document.createElement('div');
rect1ChoiceLabel.classList.add('rect-choice-label');
rect1ChoiceLabel.innerText = 'Izbrano: nič';
rect1.appendChild(rect1ChoiceLabel);

const latLonButton1 = document.createElement('button');
latLonButton1.innerText = 'lat_lon';
latLonButton1.onclick = () => {
    highlightRectButton(latLonButton1, rect1ButtonsContainer);
    choosen_graph1 = 'lat_lon';
    rect1ChoiceLabel.innerText = 'Izbrano: ' + choosen_graph1;
};
rect1ButtonsContainer.appendChild(latLonButton1);

const cnoButton1 = document.createElement('button');
cnoButton1.innerText = 'c/no';
cnoButton1.onclick = () => {
    highlightRectButton(cnoButton1, rect1ButtonsContainer);
    choosen_graph1 = 'c/no';
    rect1ChoiceLabel.innerText = 'Izbrano: ' + choosen_graph1;
};
rect1ButtonsContainer.appendChild(cnoButton1);

const timeDriftButton1 = document.createElement('button');
timeDriftButton1.innerText = 'clock_drift';
timeDriftButton1.onclick = () => {
    highlightRectButton(timeDriftButton1, rect1ButtonsContainer);
    choosen_graph1 = 'clock_drift';
    rect1ChoiceLabel.innerText = 'Izbrano: ' + choosen_graph1;
};
rect1ButtonsContainer.appendChild(timeDriftButton1);

// -----------------------------------------
// DODAJANJE GUMBOV v rect3
// -----------------------------------------
const rect3ButtonsContainer = document.createElement('div');
rect3ButtonsContainer.classList.add('rect-buttons');
rect3.appendChild(rect3ButtonsContainer);

const rect3ChoiceLabel = document.createElement('div');
rect3ChoiceLabel.classList.add('rect-choice-label');
rect3ChoiceLabel.innerText = 'Izbrano: nič';
rect3.appendChild(rect3ChoiceLabel);

const latLonButton3 = document.createElement('button');
latLonButton3.innerText = 'lat_lon';
latLonButton3.onclick = () => {
    highlightRectButton(latLonButton3, rect3ButtonsContainer);
    choosen_graph3 = 'lat_lon';
    rect3ChoiceLabel.innerText = 'Izbrano: ' + choosen_graph3;
};
rect3ButtonsContainer.appendChild(latLonButton3);

const cnoButton3 = document.createElement('button');
cnoButton3.innerText = 'c/no';
cnoButton3.onclick = () => {
    highlightRectButton(cnoButton3, rect3ButtonsContainer);
    choosen_graph3 = 'cno';
    rect3ChoiceLabel.innerText = 'Izbrano: ' + choosen_graph3;
};
rect3ButtonsContainer.appendChild(cnoButton3);

const timeDriftButton3 = document.createElement('button');
timeDriftButton3.innerText = 'clcok_drift';
timeDriftButton3.onclick = () => {
    highlightRectButton(timeDriftButton3, rect3ButtonsContainer);
    choosen_graph3 = 'clock_drift';
    rect3ChoiceLabel.innerText = 'Izbrano: ' + choosen_graph3;
};
rect3ButtonsContainer.appendChild(timeDriftButton3);

// -----------------------------------------
// 1) FUNKCIJA ZA NALAGANJE in IZPIS ML_DETECTOR
// -----------------------------------------
/**
 * Prebere seznam (table_name, score, first_unix)
 * iz /ml_detector_data in ustvari gumbe v ml_detector,
 * razvrščene od najvišjega do najnižjega 'score'.
 */
// -----------------------------------------
// 1) Funkcija za avtomatizirano izbiro časa
// -----------------------------------------

async function jumpToTime(unixTime) {
    const date = new Date(unixTime * 1000); // Pretvori unix v datum
    const year = date.getFullYear();
    const month = date.getMonth() + 1;
    const day = date.getDate();
    const hour = date.getHours();
    const minute = Math.floor(date.getMinutes() / 10) * 10; // Zaokroži na 10 minut

    // Resetiraj izbire
    clearLowerSelections('year');
    createYearPicker();

    // 1. Izberi leto
    await clickButtonWithDelay('[data-level="year"] button', btn => btn.innerText == year.toString());
    selectYear(year, document.querySelector('[data-level="year"] button.selected')); // Aktiviraj naslednje gumbe

    // 2. Izberi mesec
    await clickButtonWithDelay('[data-level="month"] button', btn => btn.innerText == months[month - 1]);
    selectMonth(year, month, document.querySelector('[data-level="month"] button.selected'));

    // 3. Izberi dan
    await clickButtonWithDelay('[data-level="day"] button', btn => btn.innerText == day.toString());
    selectDay(year, month, day, document.querySelector('[data-level="day"] button.selected'));

    // 4. Izberi uro
    await clickButtonWithDelay('[data-level="hour"] button', btn => btn.innerText.startsWith(`${hour}:`));
    selectHour(year, month, day, hour, document.querySelector('[data-level="hour"] button.selected'));

    // 5. Izberi minute
    await clickButtonWithDelay('[data-level="minute"] button', btn => btn.innerText.endsWith(`:${minute.toString().padStart(2, '0')}`));
    showResult(year, month, day, hour, minute, document.querySelector('[data-level="minute"] button.selected'));

    console.log('Samodejna izbira časa končana.');
}

// Funkcija za čakanje na gumb in simulacijo klika
function clickButtonWithDelay(selector, matchFunc, maxRetries = 10) {
    return new Promise((resolve, reject) => {
        let retries = 0;

        function tryClick() {
            const buttons = document.querySelectorAll(selector);
            const button = Array.from(buttons).find(matchFunc);

            if (button) {
                button.click();
                resolve(); // Uspešno kliknil
            } else if (retries < maxRetries) {
                retries++;
                setTimeout(tryClick, 300); // Počakaj 300 ms in poskusi znova
            } else {
                reject(`Gumb ni bil najden: ${selector}`);
            }
        }

        tryClick();
    });
}

// -----------------------------------------
// 2) Funkcija za obdelavo klikov v ML_DETECTOR
// -----------------------------------------

function handleMlDetectorClick(button) {
    const tableName = button.dataset.tableName; // Preberi ime tabele iz atributa
    const unixTime = parseInt(tableName.split('_')[2]); // Izvleci prvi unix čas
    jumpToTime(unixTime); // Sproži avtomatsko izbiro časa
}

// -----------------------------------------
// 3) Nalaganje ML_DETECTOR gumbov
// -----------------------------------------

function loadMlDetectorData() {
    fetch('/ml_detector_data')
        .then(response => response.json())
        .then(data => {
            ml_detector.innerHTML = '<h4>ML Detektor - Rangirano</h4>';

            data.forEach(item => {
                const dObj = new Date(item.first_unix * 1000);
                const d = dObj.getDate();
                const m = dObj.getMonth() + 1;
                const y = dObj.getFullYear();
                const hh = String(dObj.getHours()).padStart(2, '0');
                const mm = String(dObj.getMinutes()).padStart(2, '0');
                const dateStr = `${d}.${m}.${y} ${hh}:${mm}`;

                // Ustvari gumb
                const btn = document.createElement('button');
                btn.classList.add('ml_date_button');
                btn.innerText = `${dateStr} (Kritično: ${item.score})`;
                btn.dataset.tableName = item.table_name; // Shrani ime tabele

                // Dodaj klik funkcijo
                btn.onclick = () => handleMlDetectorClick(btn);

                ml_detector.appendChild(btn);
                ml_detector.appendChild(document.createElement('br'));
            });
        })
        .catch(error => {
            console.error('Napaka pri nalaganju /ml_detector_data:', error);
            ml_detector.innerHTML = '<p>Napaka pri nalaganju ML podatkov.</p>';
        });
}



createYearPicker(); // Ustvari začetne gumbe
loadMlDetectorData(); // Naloži ML gumbe
