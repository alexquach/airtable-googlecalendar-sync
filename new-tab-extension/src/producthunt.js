const QUERY_URL = "https://api.producthunt.com/v2/api/graphql";
const TOKEN_URL = "https://api.producthunt.com/v2/oauth/token";

const TOKEN_QUERY = {
    "client_id": "mhlOGIZkEIJyAneh_VEdiIMbe-bzirnGyHduy6FFDZc",
    "client_secret": "34HwRl2jSpI-LPl35ylzJW5KDZe3Dmam9-avpLjqJ10",
    "grant_type": "client_credentials"
}

const FEATURED_QUERY = {
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
                var posts = JSON.parse(xhr.response)['data']['posts']['edges']
                console.log(posts)
                
                var table = document.querySelector('.product_hunt');
                for (var i in posts) {
                    var post_name = posts[i]['node']['name'];
                    var tagline = posts[i]['node']['tagline'];
                    var votesCount = posts[i]['node']['votesCount'];
                    var website = posts[i]['node']['website'];
                    var thumbnail = posts[i]['node']['thumbnail']['url'];
                    var slug = posts[i]['node']['slug'];
                    var product_hunt_site = "https://www.producthunt.com/posts/" + slug

                    var new_elem = document.createElement('div');
                    new_elem.classList.add('product')
                    new_elem.innerHTML = `
                        <a href="${product_hunt_site}">
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