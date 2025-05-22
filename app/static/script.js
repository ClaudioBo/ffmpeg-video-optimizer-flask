// Diccionario: filename → uuid
const filenameUUIDMap = {};
// Diccionario: uuid → DOM element
const processingItems = {};

// Función para generar un UUID v4 básico
function generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        const r = Math.random() * 16 | 0;
        const v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

// Conectarse al SSE
const evtSource = new EventSource("/events");
evtSource.onmessage = function(event) {
    const msg = JSON.parse(event.data);

    if (msg.type === "reload") {
        location.reload();
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

            if (!processingItems[uuid]) {
                // Crear nuevo item
                const template = document.getElementById("item-processing-template").content;
                const newItem = template.cloneNode(true);
                newItem.id = `item-${uuid}`;
                newItem.hidden = false;

                newItem.querySelector(".processing-filename").textContent = filename;
                const progressBar = newItem.querySelector(".progress-bar");
                progressBar.style.width = progress + "%";
                progressBar.setAttribute("aria-valuenow", progress);
                progressBar.textContent = progress + "%";

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