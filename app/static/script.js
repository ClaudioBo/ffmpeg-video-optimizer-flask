// Diccionario: filename → uuid
const filenameUUIDMap = {};
// Diccionario: uuid → DOM element
const processingItems = {};
// Progreso para calcular ETAs
const progressStats = {}; 

// Función para generar un UUID v4 básico
function generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
        const r = Math.random() * 16 | 0;
        const v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

// Generar un color en base al porcentaje, interpolando de rojo, naranja y verde
function getColorInterpolation(percent) {
    const rojo = [220, 53, 69];
    const naranja = [255, 193, 7];
    const verde = [40, 167, 69];

    let r, g, b;

    if (percent < 50) {
        const ratio = percent / 50;
        r = Math.round(verde[0] + ratio * (naranja[0] - verde[0]));
        g = Math.round(verde[1] + ratio * (naranja[1] - verde[1]));
        b = Math.round(verde[2] + ratio * (naranja[2] - verde[2]));
    } else {
        const ratio = (percent - 50) / 50;
        r = Math.round(naranja[0] + ratio * (rojo[0] - naranja[0]));
        g = Math.round(naranja[1] + ratio * (rojo[1] - naranja[1]));
        b = Math.round(naranja[2] + ratio * (rojo[2] - naranja[2]));
    }

    return `rgb(${r},${g},${b})`;
}


// Conectarse al SSE
const evtSource = new EventSource("/events");
evtSource.onmessage = function (event) {
    const msg = JSON.parse(event.data);
    if (msg.type === "reload") {
        location.reload();
    } else if (msg.type === "disk") {
        const used = msg.used
        const total = msg.total
        const diskInfoElement = document.getElementById("disk-info");
        const humanReadableUsed = `${(used / (1024 ** 3)).toFixed(2)} GB`
        const humanReadableTotal = `${(total / (1024 ** 3)).toFixed(2)} GB`
        const percentage = ((used / total) * 100).toFixed(2)
        diskInfoElement.style.backgroundColor = getColorInterpolation(percentage)
        diskInfoElement.style.width = `${percentage}%`
        diskInfoElement.ariaValueNow = percentage
        diskInfoElement.textContent = `${humanReadableUsed} / ${humanReadableTotal} (${percentage}%)`
    } else if (msg.type === "status") {
        const table = document.getElementById("processing-list");
        const activeUUIDs = new Set();

        msg.processing.forEach(fileObj => {
            const filename = fileObj.filename;
            const progress = fileObj.progress || 0;

            // Asignar UUID si no tiene
            if (!filenameUUIDMap[filename]) {
                filenameUUIDMap[filename] = generateUUID();
            }

            const uuid = filenameUUIDMap[filename];
            activeUUIDs.add(uuid);

            const now = Date.now();

            if (!progressStats[uuid]) {
                progressStats[uuid] = {
                    lastProgress: progress,
                    lastTime: now,
                    speed: null
                };
            } else {
                const stat = progressStats[uuid];
                const deltaProgress = progress - stat.lastProgress;
                const deltaTime = (now - stat.lastTime) / 1000;

                if (deltaProgress > 0 && deltaTime > 0) {
                    stat.speed = deltaProgress / deltaTime;
                }

                stat.lastProgress = progress;
                stat.lastTime = now;
            }

            let etaText = "Calculando…";

            const speed = progressStats[uuid].speed;
            if (speed && speed > 0) {
                const remaining = 100 - progress;
                const etaSeconds = remaining / speed;

                const mins = Math.floor(etaSeconds / 60);
                const secs = Math.floor(etaSeconds % 60);
                etaText = `${mins}m ${secs}s restantes`;
            }

            if (!processingItems[uuid]) {
                // Crear nuevo item
                const template = document.getElementById("item-processing-template").content;
                const fragment = template.cloneNode(true);
                const newItem = fragment.querySelector("tr");
                newItem.id = `item-${uuid}`;
                newItem.hidden = false;

                newItem.querySelector(".processing-filename").textContent = filename;
                const progressBar = newItem.querySelector(".progress-bar");
                progressBar.style.width = progress + "%";
                progressBar.setAttribute("aria-valuenow", progress);
                progressBar.textContent = progress + "%";
                newItem.querySelector(".eta-text").textContent = etaText;

                table.appendChild(newItem);
                processingItems[uuid] = newItem;
            } else {
                // Solo actualizar
                const item = processingItems[uuid];
                item.querySelector(".processing-filename").textContent = filename;
                const progressBar = item.querySelector(".progress-bar");
                progressBar.style.width = progress + "%";
                progressBar.setAttribute("aria-valuenow", progress);
                progressBar.textContent = progress + "%";
                item.querySelector(".eta-text").textContent = etaText;
            }
        });

        // Remover elementos que ya no están en la lista
        for (const uuid in processingItems) {
            if (!activeUUIDs.has(uuid)) {
                processingItems[uuid].remove();
                delete processingItems[uuid];
            }
        }
    }
};