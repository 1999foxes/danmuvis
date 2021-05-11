const clipList = [];
const clipRanges = [];
//const colorScheme = ['rgba(0, 115, 168, 1)',
//    'rgba(155, 123, 221, 1)',
//    'rgba(255, 96, 162, 1)',
//    'rgba(255, 95, 95, 1)',
//    'rgba(255, 124, 67, 1)',
//    'rgba(255, 166, 0, 1)'];
const colorScheme = d3.schemeSet1;
let colorSchemeIndex = 0;
const colorSchemeMap = new Map();
function getColorByFilename(filename) {
    if (colorSchemeMap.has(filename)) {
        return colorSchemeMap.get(filename);
    } else {
        const color = colorScheme[(colorSchemeIndex++) % colorScheme.length];
        colorSchemeMap.set(filename, color);
        return color;
    }
}


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

async function doClip(clip) {
    const fd = new FormData();
    fd.append('filename', clip.filename);
    fd.append('video_filename', filename);
    fd.append('start', clip.range[0]);
    fd.append('end', clip.range[1]);

    const response = await fetch('/do_clip', {
        method: 'POST',
        body: fd
    });

    return response.text();
}

function color2Gradient(color) {
    return 'linear-gradient(to right, ' + color + ', ' + color + ')';
}

function drawClipList() {
    let clips = d3.select('#clipList')
        .selectAll('.clip')
        .data(clipList);

    clips.enter()
        .append('div')
            //.style('background-color', (d, i) => colorScheme[i % colorScheme.length])
            .classed('clip', true)
            .each(drawClip);
    clips.each(drawClip);
    clips.exit().remove();
}

const downloadButton = '<button class="downloadButton" onclick="downloadClipHandler(this.parentElement.parentElement); event.stopPropagation();"><i class="fa fa-download"></i></button>';
const confirmButton = '<button class="confirmButton" onclick="confirmClipHandler(this.parentElement.parentElement); event.stopPropagation();"><i class="fa fa-check-circle"></i></button>';
const cancelButton = '<button class="cancelButton" onclick="removeClipHandler(this.parentElement.parentElement); event.stopPropagation();"><i class="fa fa-times-circle"></i></button>';
const spinnerButton = '<button class="spinnerButton"><i class="fa fa-spinner fa-spin"></i></button>';

function drawClip(d, i, nodes) {
    clipNode = d3.select(nodes[i]);
    clipNode.attr('index', i);
    let range = clipNode.select('.clipRange');
    let control = clipNode.select('.clipControl');
    if (range.empty()) {
        clipNode.on('click', (e, d) => playClip(d));
        range = clipNode.append('p')
                .classed('clipRange', true);
        control = clipNode.append('div')
                .classed('clipControl', true);
    }
    range.text(d.range[0] + '-' + d.range[1])
            //.style('color', colorScheme[i % colorScheme.length]);
            .style('color', getColorByFilename(d.filename));

    if (d.state == 0) {
        control.node().innerHTML = spinnerButton;
    } else if (d.state == 1) {
        control.node().innerHTML = downloadButton + cancelButton;
    } else if (d.state == 2) {
        control.node().innerHTML = confirmButton + cancelButton;
    }
}

function removeClipHandler(clipNode) {
    index = clipNode.getAttribute("index");
    clip = d3.select(clipNode).datum();
    if (clip.state == 1) {
        console.log('fetch:', '/file/remove_clip/' + clip.filename);
        fetch('/file/remove_clip/' + clip.filename);
    }
    removeClip(index);
    drawClipList();
    danmuvisDrawClipRanges();
}

function confirmClipHandler(clipNode) {
    index = clipNode.getAttribute("index");
    setClip({state: 0}, index);
    drawClipList();
    // send clip request, alert if get error
    doClip(d3.select(clipNode).datum()).then(text => { if (text != 'ok') alert(text); });
}

function downloadClipHandler(clipNode) {
    let filename = d3.select(clipNode).datum().filename;
    window.open('/clip/' + filename);
}

function updateClipList() {
    return fetchClipList(undefined, filename, undefined)
        .then(newClipList => { mergeClipList(newClipList); })
        .then(drawClipList)
        .then(danmuvisDrawClipRanges);
}

function mergeClipList(newClipList) {
    const newClipFilenames = newClipList.map(clip => clip.filename);
    const clipFilenames = clipList.map(clip => clip.filename);
    for (const clip of newClipList) {
        const index = clipFilenames.indexOf(clip.filename)
        if (index != -1) {
            setClip(clip, index);
        } else {
            addClip(clip);
        }
    }
    for (let i = clipList.length-1; i >= 0; i--) {
        const clip = clipList[i];
        if (clip.state != 2 && !newClipFilenames.includes(clip.filename)) {
            removeClip(i);
        }
    }
}

function second2Time(second) {
    if (second == undefined || second == 0)
        return '';
    return new Date(second * 1000).toISOString().substr(12, 11);
}

function time2Second(time) {
    let h, m, s, ms;
    [h, m, s] = time.split(':');
    [s, ms] = s.split('.');
    [h, m, s, ms] = [h, m, s, ms].map(str => parseInt(str));
    second = (ms / 1000 + s) + (h * 60 + m) * 60;
    return second;
}

function randomFilename() {
    return Math.floor(Math.random() * 99999999).toString()+'.mp4';
}

function addClipRange(range) {
    clipRanges.push(range);
    clipList.push({range: [second2Time(range[0]), second2Time(range[1])], state: 2, filename: randomFilename()});
}

function setClipRange(range, i=clipRanges.length-1) {
    if (range != undefined) {
        clipRanges[i] = range;
        clipList[i].range[0] = second2Time(range[0]);
        clipList[i].range[1] = second2Time(range[1]);
    }
}

function removeClipRange(i=clipRanges.length-1) {
    clipRanges.splice(i, 1);
    clipList.splice(i, 1);
}

function addClip(clip) {
    clipRanges.push([time2Second(clip.range[0]), time2Second(clip.range[1])]);
    clipList.push(clip);
}

function setClip(clip, i=clipRanges.length-1) {
    Object.assign(clipList[i], clip);
    if (clip.range != undefined) {
        clipRanges[i][0] = time2Second(clip.range[0]);
        clipRanges[i][1] = time2Second(clip.range[1]);
    }
}

function removeClip(i=clipRanges.length-1) {
    clipRanges.splice(i, 1);
    clipList.splice(i, 1);
}

function autoUpdateClipList() {
    console.log('autoUpdateClipList');
    updateClipList();
}

let checkWhenToStopTimeoutID = undefined;
function checkWhenToStop(end) {
    if (videoElement.currentTime >= end) {
        videoElement.pause();
        window.clearTimeout(checkWhenToStopTimeoutID);
        checkWhenToStopTimeoutID = undefined;
    } else {
        checkWhenToStopTimeoutID = window.setTimeout(checkWhenToStop, 1000, end);
    }
}

function playClip(clip) {
    videoElement.currentTime = time2Second(clip.range[0]);
    videoElement.play()
    if (checkWhenToStopTimeoutID != undefined) {
        window.clearTimeout(checkWhenToStopTimeoutID);
    }
    checkWhenToStop(time2Second(clip.range[1]));
}

window.setInterval(autoUpdateClipList, 10000);
