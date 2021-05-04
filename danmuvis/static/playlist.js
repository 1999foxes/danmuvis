async function fetchVideoList(keyword='', streamer='', dateFrom='', dateTo='') {
    const fd = new FormData();
    fd.append('keyword', keyword);
    fd.append('streamer', streamer);
    fd.append('dateFrom', dateFrom.replaceAll('-', ''));
    fd.append('dateTo', dateTo.replaceAll('-', ''));

    const response = await fetch('/file/video_list', {
        method: 'POST',
        body: fd
    });

    return response.json();
}


function drawPlaylist() {
    const tbody = d3.select('#playlist').select('tbody');
    tbody.selectAll('tr')
        .data(video_list)
        .join('tr')
            .on('click', (e, d) => window.location.href = `/play/${ d[0] }`)
        .selectAll('td')
        .data(d => d)
        .join('td')
            .text(d => d);
}


let video_list;

function initPlaylist(keyword, streamer, dateFrom, dateTo) {
    return fetchVideoList(keyword, streamer, dateFrom, dateTo)
        .then(result => video_list = result)
        .then(() => sortPlaylist(2, true))
        .then(drawPlaylist);
}

function sortPlaylist(keyIndex, descending=false) {
    video_list.sort((v1, v2) => ((v1[keyIndex] < v2[keyIndex]) != descending ? -1 : 1));
}

initPlaylist();

function sortPlaylistHandlerFactory(keyIndex) {
    let descending = true;
    return function() { sortPlaylist(keyIndex, descending = !descending); drawPlaylist() }
}

document.querySelectorAll('#playlist th').forEach((e, i) => e.addEventListener('click', sortPlaylistHandlerFactory(i)));


async function fetchStreamerList() {
    const response = await fetch('/file/streamer_list', {
        method: 'POST',
    });

    return response.json();
}

let streamer_list;
fetchStreamerList().then(result => streamer_list = result).then(initStreamerSelect)

function initStreamerSelect() {
    streamer_list.sort();
    d3.select('select#streamer')
        .selectAll('option')
        .data([''].concat(streamer_list))
        .join('option')
            .attr('value', d => d)
            .text(d => d);
}


document.querySelector('#playlistFilter #applyFilter').addEventListener('click', function() {
    let keyword = this.form.elements['keyword'].value;
    let streamer = this.form.elements['streamer'].value;
    let dateFrom = this.form.elements['dateFrom'].value;
    let dateTo = this.form.elements['dateTo'].value;
    initPlaylist(keyword, streamer, dateFrom, dateTo);
});

document.querySelector('#playlistFilter #resetDate').addEventListener('click', function() {
    this.form.elements['dateFrom'].value = '';
    this.form.elements['dateTo'].value = '';
});
