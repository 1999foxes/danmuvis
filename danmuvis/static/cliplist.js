let clipList;
let colorScheme = d3.schemeSet2;

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
        .data(clipList)
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
                else if (d == 3)
                    return '待确认';
                else return d;
            });
    if (clipList.length == 0) {
        tbody.append('tr')
            .append('td')
                .text('暂无');
    }
}

function initCliplist(keyword, video_filename, state) {
    return fetchClipList(keyword, video_filename, state)
        .then(result => {
            clipList = result;
        })
        .then(drawCliplist);
}

initCliplist();

const clipRanges = [];

function addClipRange(range) {
    clipRanges.push(range);
    clipList.push([range.toString(), 3]);
    drawCliplist();
}

function setClipRange(range, i=clipRanges.length-1) {
    clipRanges[i] = range;
    clipList[i][0] = range.toString();
    drawCliplist();
}

function removeClipRange(i=clipRanges.length-1) {
    clipRanges.splice(i, 1);
    clipList.splice(i, 1);
    drawCliplist();
}