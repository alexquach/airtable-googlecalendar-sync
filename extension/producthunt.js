const QUERY_URL = "https://api.producthunt.com/v2/api/graphql";
const TOKEN_URL = "https://api.producthunt.com/v2/oauth/token";

TOKEN_QUERY = {
    "client_id": "",
    "client_secret": "",
    "grant_type": "client_credentials"
}

FEATURED_QUERY = {
    "query": "query {posts(first: 10, featured:true) {edges { node { id, name, tagline, slug, thumbnail { url }, website, votesCount } } } } "
}

function get_token(callback, access_token) {
    if (access_token != "") {
        callback(access_token)
        return
    }

    const xhr = new XMLHttpRequest();
    xhr.addEventListener('readystatechange', function () {
        if (xhr.readyState == 4) {
            if (xhr.status == 200) {
                console.log(JSON.parse(xhr.response))
                const access_token = JSON.parse(xhr.response)["access_token"];
                console.log(access_token);

                callback(access_token)
                // chrome.storage.local.set({ "producthunt_at": access_token }, post_data => {
                //     console.log("Saved data!");
                // });
            }
        }
    });
    xhr.open('POST', TOKEN_URL)
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.setRequestHeader('Accept', 'application/json');
    xhr.send(JSON.stringify(TOKEN_QUERY));
}


function get_featured_posts(access_token) {
    /* Request */
    const xhr = new XMLHttpRequest();

    xhr.addEventListener('readystatechange', function () {
        if (xhr.readyState == 4) {
            if (xhr.status == 200) {
                posts = JSON.parse(xhr.response)['data']['posts']['edges']
                console.log(posts)
                
                table = document.querySelector('.product_hunt');
                for (i in posts) {
                    post_name = posts[i]['node']['name'];
                    tagline = posts[i]['node']['tagline'];
                    votesCount = posts[i]['node']['votesCount'];
                    website = posts[i]['node']['website'];
                    thumbnail = posts[i]['node']['thumbnail']['url'];

                    new_elem = document.createElement('div');
                    new_elem.classList.add('product')
                    new_elem.innerHTML = `
                        <a href="${website}">
                            <img src="${thumbnail}">
                        </a>
                        <div class="name">${post_name}</div>
                        <p class="tagline">${tagline}</p>
                        
                    `;
                    console.log(new_elem)
                    table.appendChild(new_elem);
                }
            }
        }
    });
    xhr.open('POST', QUERY_URL)
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.setRequestHeader('Accept', 'application/json');
    xhr.setRequestHeader('Authorization', 'Bearer ' + access_token)
    xhr.send(JSON.stringify(FEATURED_QUERY));
}

get_token(get_featured_posts, "P1QshzX1ZU9-eZ39_8MX6VOCa97xvpZasfklRxU1bkI")
//get_featured_posts()