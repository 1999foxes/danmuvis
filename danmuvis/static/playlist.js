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
    if (document.querySelector('#playlist') == null) {
        document.querySelector('#playlistDiv').innerHTML = '<table id="playlist"><colgroup><col style="width:70%"><col style="width:20%"><col style="width:10%"></colgroup><thead><tr><th>录播标题 <i class="fas fa-angle-down"></i></th><th>主播 <i class="fas fa-angle-down"></i></th><th>日期 <i class="fas fa-angle-down"></i></th></tr></thead><tbody></tbody></table>';
        document.querySelectorAll('#playlist th').forEach((e, i) => e.addEventListener('click', sortPlaylistHandlerFactory(i)));
    }
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

function drawVideoCards() {
    if (!d3.select('#playlistDiv').empty()) {
        document.querySelector('#playlistDiv').innerHTML = '';
    }
    d3.select('#playlistDiv')
        .selectAll('.videoCard')
        .data(video_list)
        .join('div')
            .on('click', (e, d) => window.location.href = `/play/${ d[0] }`)
            .classed('videoCard', true)
            .each(drawVideoCard);
}


function drawVideoCard(d, i, nodes) {
    let filename = d[0];
    let streamer = d[1];
    let date = d[2];
    let videoCard = d3.select(nodes[i]);
    videoCard.node().innerHTML = '';
    videoCard.node().style.backgroundImage='url(/image/'+encodeURIComponent(filename)+'), linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.2))';
    videoCard.append('h3')
            .classed('filename', true)
            .text(filename);
    videoCard.append('p')
            .classed('streamer', true)
            .classed('date', true)
            .text(streamer + '-' + date);
}


let video_list;
let layout = 'cards';
function initPlaylist(keyword, streamer, dateFrom, dateTo) {
    return fetchVideoList(keyword, streamer, dateFrom, dateTo)
        .then(result => video_list = result)
        .then(() => sortPlaylist(2, true))
        .then(() => { if (layout == 'list') drawPlaylist(); else if (layout == 'cards') drawVideoCards(); });
}

initPlaylist();

function layoutToggle() {
    if (layout == 'cards') {
        layout = 'list';
        initPlaylist();
        document.querySelector('#layoutButton>i').setAttribute('class', 'fas fa-images');
    } else if (layout == 'list') {
        layout = 'cards';
        initPlaylist();
        document.querySelector('#layoutButton>i').setAttribute('class', 'fas fa-list');
    }
}
document.querySelector('#layoutButton').addEventListener('click', layoutToggle);



/*
 *      video filter
 */

function sortPlaylist(keyIndex, descending=false) {
    video_list.sort((v1, v2) => ((v1[keyIndex] < v2[keyIndex]) != descending ? -1 : 1));
}

function sortPlaylistHandlerFactory(keyIndex) {
    let descending = true;
    return function() {
        sortPlaylist(keyIndex, descending = !descending);
        drawPlaylist();
        if (descending) {
            document.querySelector('#playlist thead tr:nth-child(' + (keyIndex + 1) + ') i').setAttribute('class', 'fas fa-angle-up');
        } else {
            document.querySelector('#playlist thead tr:nth-child(' + (keyIndex + 1) + ') i').setAttribute('class', 'fas fa-angle-down');
        }
    }
}

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

function applyFilter() {
    let keyword = this.form.elements['keyword'].value;
    let streamer = this.form.elements['streamer'].value;
    let dateFrom = this.form.elements['dateFrom'].value;
    let dateTo = this.form.elements['dateTo'].value;
    initPlaylist(keyword, streamer, dateFrom, dateTo);
}

document.querySelector('#playlistFilter #applyFilter').addEventListener('click', applyFilter);

document.querySelector('#playlistFilter #resetFilter').addEventListener('click', function() {
    this.form.elements['keyword'].value = '';
    this.form.elements['streamer'].value = '';
    this.form.elements['dateFrom'].value = '';
    this.form.elements['dateTo'].value = '';
    initPlaylist();
});
