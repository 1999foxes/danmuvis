var clip_list;

async function fetchClipList(keyword='', video_filename='', state='') {
    const fd = new FormData();
    fd.append('keyword', keyword);
    fd.append('video_filename', video_filename);
    fd.append('state', state);

    const response = await fetch('/file/clip_list', {
        method: 'POST',
        body: fd
    });

    return response.json();
}

function drawCliplist() {
    const tbody = d3.select('#cliplist').select('tbody');
    tbody.selectAll('tr')
        .data(clip_list)
        .join('tr')
            .on('click', (e, d) => {
                if (d[1] == 1)
                    window.open(`/clip/${ d[0] }`);
            })
        .selectAll('td')
        .data(d => d)
        .join('td')
            .text(d => {
                if (d == 1)
                    return '已完成';
                else if (d == 0)
                    return '生成中';
                else return d;
            });
}

function initCliplist(keyword, video_filename, state) {
    return fetchClipList(keyword, video_filename, state)
        .then(result => {
            clip_list = result;
        })
        .then(drawCliplist);
}

initCliplist();