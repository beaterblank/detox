const SeenThumbnailData = [];

function sendDataToAPI(data) {
    if (data) {
        return fetch('http://localhost:8000/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .catch((error) => {
                console.error('Error:', error);
                return false; // Return false in case of error
            });
    } else {
        return false;
    }
}

function extractThumbnails() {
    const thumbnails = document.querySelectorAll("a#thumbnail[href]");
    const promises = [];

    thumbnails.forEach(thumbnail => {
        let thumbnailInfo = {
            "href": thumbnail.href,
            "text": thumbnail.innerText
        };

        if (thumbnail && !SeenThumbnailData.some(seen => seen.href === thumbnailInfo.href)) {
            SeenThumbnailData.push(thumbnailInfo);

            const promise = sendDataToAPI(thumbnailInfo)
                .then(responseData => {
                    if (responseData === true) {
                        // Hide the thumbnail element if the API returns true
			console.log("hiding thumbnail")
			content_div = thumbnail.closest('#content')
                        content_div.style.display = 'none';
                    }
                });

            promises.push(promise);
        }
    });

    // Wait for all API requests to complete
    Promise.all(promises).then(() => {
        console.log('All thumbnails processed.');
    });
}

const observer = new MutationObserver((mutations) => {
    let updated = false;
    mutations.forEach(mutation => {
        if (mutation.addedNodes.length || mutation.removedNodes.length) {
            updated = true;
        }
    });

    if (updated) {
        const data = extractThumbnails();
        sendDataToAPI(data);
    }
});

observer.observe(document.body, {
    childList: true,
    subtree: true
});

const data = extractThumbnails();
sendDataToAPI(data)
