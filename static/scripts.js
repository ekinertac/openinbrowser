const toggleSwitch = document.querySelector('.theme-switch input[type="checkbox"]');
const currentTheme = localStorage.getItem('theme');
const socket = io();

// Notify server when the page is closed
window.addEventListener("beforeunload", () => {
    socket.emit("disconnect");
});

// Function to set the theme
function setTheme(theme) {
    document.documentElement.setAttribute('class', theme);
    localStorage.setItem('theme', theme);
    toggleSwitch.checked = (theme === 'dark-theme');
}

// Check for saved user preference, if any, on load of the website
if (currentTheme) {
    setTheme(currentTheme);
} else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
    setTheme('dark-theme');
} else {
    setTheme('light-theme');
}

// Listen for toggle switch change
toggleSwitch.addEventListener('change', function(e) {
    setTheme(e.target.checked ? 'dark-theme' : 'light-theme');
});

// Listen for system theme change
window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
    setTheme(e.matches ? 'dark-theme' : 'light-theme');
});

// Function to load folder contents
function loadFolder(folderPath) {
    // Remove the leading 'folder/' if it exists
    const cleanPath = folderPath.replace(/^folder\//, '');
    fetch(`/api/folder/${cleanPath}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(data.error);
                return;
            }
            updateGallery(data.items);
        })
        .catch(error => console.error("Error loading folder:", error));
}

// Function to update the gallery with new items
function updateGallery(items) {
    const gallery = document.getElementById("gallery");
    gallery.innerHTML = ""; // Clear current items

    items.forEach(item => {
        const itemDiv = document.createElement("div");
        itemDiv.classList.add("gallery-item");

        if (item.type === "file") {
            itemDiv.innerHTML = `
                <a href="/${item.path}" class="gallery-link" target="_blank">
                    <img src="/${item.path}" alt="${item.name}" class="gallery-image">
                    <div class="image-caption">${item.name}</div>
                </a>
            `;
        } else if (item.type === "folder") {
            itemDiv.classList.add("folder");
            itemDiv.setAttribute("onclick", `loadFolder('${item.path}')`);
            itemDiv.innerHTML = `
                <div class="folder-collage">
                    ${item.preview_images ? item.preview_images.map(img => `<img src="/${img}" class="collage-image" alt="Folder Preview">`).join("") : ''}
                </div>
                <div class="folder-caption">${item.name}</div>
            `;
        }

        gallery.appendChild(itemDiv);
    });
}

// Scroll by viewport height with PageUp/PageDown keys
document.addEventListener('keydown', function(event) {
    const viewportHeight = window.innerHeight;
    if (event.key === 'PageUp') {
        event.preventDefault();
        window.scrollBy(0, -viewportHeight);
    } else if (event.key === 'PageDown') {
        event.preventDefault();
        window.scrollBy(0, viewportHeight);
    }
});
