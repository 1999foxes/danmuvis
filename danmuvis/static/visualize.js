async function visualize() {

highlight = await fetch('/highlight/' + filename).then(response => response.json());


yLabel = 'density';
deltaTime = 10;
data = highlight[yLabel];

height = 100
width = 1000
margin = ({top: 10, right: 50, bottom: 0, left: 50})

x = d3.scaleLinear()
    .domain([0, data.length * deltaTime])
    .range([margin.left, width - margin.right])

y = d3.scaleLinear()
    .domain([0, d3.max(data)]).nice()
    .range([height - margin.bottom, margin.top])

xAxis = (g, x) => g
    .attr("transform", `translate(0,${height - margin.bottom})`)
    .call(d3.axisBottom(x).ticks(width / 80).tickSizeOuter(0))

yAxis = (g, y) => g
    .attr("transform", `translate(${margin.left},0)`)
    .call(d3.axisLeft(y).ticks(null, "s"))
    .call(g => g.select(".domain").remove())
    .call(g => g.select(".tick:last-of-type text").clone()
        .attr("x", 3)
        .attr("text-anchor", "start")
        .attr("font-weight", "bold")
        .text(yLabel))

area = (data, x) => d3.area()
    .curve(d3.curveNatural)
    .x((d, i) => x(i * deltaTime))
    .y0(y(0))
    .y1(d => y(d))
  (data)


chart = function() {

  const svg = d3.create("svg")
      .attr("viewBox", [0, 0, width, height])
      .classed("noselect", true);

  const clip = {id: 'clip0'};

  svg.append("clipPath")
      .attr("id", clip.id)
    .append("rect")
      .attr("x", margin.left)
      .attr("y", margin.top)
      .attr("width", width - margin.left - margin.right)
      .attr("height", height - margin.top - margin.bottom);

  const path = svg.append("path")
      .attr("clip-path", clip)
      .attr("fill", "steelblue")
      .attr("d", area(data, x));

//  const gx = svg.append("g")
//      .call(xAxis, x);
//
//  const gy = svg.append("g")
//      .call(yAxis, y);

  const cursor = svg.append('rect')
      .attr('width', 1)
      .attr('height', 500)
      .style('fill', 'red');

  const cursorLabel = svg.append("text")
      .text("0:00:00.000")
      .attr("x", margin.left + 10)
      .attr("y", margin.top + 10)
      .style('fill', 'black')
      .style('font-weight', 'bold')
      .style('font-size', '15px');

  const zoom = d3.zoom()
      .scaleExtent([1, 32])
      .extent([[margin.left, 0], [width - margin.right, height]])
      .translateExtent([[margin.left, -Infinity], [width - margin.right, Infinity]])
      .on("zoom", zoomed)
      .filter(filterWheelOnly);

  let zoomedTransform;
  let isMousedown = false;
  let mousedownTime, mouseupTime;
  let timeTranslateSpeed = 0;

  function zoomed(event) {
    zoomedTransform = event.transform;
    const xz = event.transform.rescaleX(x);
    path.attr("d", area(data, xz));
//    gx.call(xAxis, xz);
    drawClipRanges();
    const cursorTime = xz.invert(cursor.attr("x"));
    cursorLabelUpdate(cursorTime);
  }

  function filterWheelOnly(event) {
    return event instanceof WheelEvent;
  }

  svg.call(zoom)
    .call(zoom.scaleTo, 1);

  function cursorLabelUpdate(time) {
    cursorLabel
        .text(new Date(time * 1000).toISOString().substr(12, 11));
    if (isMousedown) {
      videoElement.currentTime = time;
      setClipRange([mousedownTime, time]);
    }
  }

  function cursorTranslate(time, timeX, durationTime) {
    cursor
      .transition()
        .duration(durationTime)
        .attr("x", timeX);
    return cursorLabel
      .transition()
        .duration(durationTime)
        .attr("x", (width - timeX > 100 ? timeX + 10 : timeX - 100));
  }

  function loopCursorTranslateWithCurrentTime() {
    let time = videoElement.currentTime;
    let timeX = zoomedTransform.rescaleX(x)(time);

    if (timeX >= x.range()[1]) {
      svg.transition()
        .duration(1000)
        .call(zoom.translateBy, (x.range()[1] - timeX) / zoomedTransform.k, 0);
    } else if (timeX <= x.range()[0]) {
      svg.transition()
        .duration(1000)
        .call(zoom.translateBy, (x.range()[0] - timeX) / zoomedTransform.k, 0);
    }

    cursorLabelUpdate(time);
    cursorTranslate(time, timeX, 1000)
        .on("end", loopCursorTranslateWithCurrentTime);
  }

  loopCursorTranslateWithCurrentTime();

  function drawClipRanges() {
    const zx = zoomedTransform.rescaleX(x);
    cr = svg.selectAll(".clip_ranges")
      .data(clipRanges);

    cr.attr("x", function(d) { return zx(d[0]); })
        .attr("width", function(d) { return Math.max(zx(d[1]) - zx(d[0]), 0); });

    cr.enter()
      .append("rect")
        .classed("clip_ranges", true)
        .attr("x", function(d) { return zx(d[0]); })
        .attr("width", function(d) { return Math.max(zx(d[1]) - zx(d[0]), 0); })
        .attr("height", height)
        .style("fill", function(d, i) { return colorScheme[i % colorScheme.length]; })
        .style("opacity", 0.2);

    cr.exit().remove();
  }

  function onMousedown(e, d) {
    isMousedown = true;

    let timeX = d3.pointer(e)[0];
    let time = x.invert(zoomedTransform.invert([timeX, 0])[0]);
    videoElement.currentTime = time;
    mousedownTime = time;
    mouseupTime = null;

    addClipRange(time, 0);
  }

  function onMouseup(e, d) {
    isMousedown = false;

    let timeX = d3.pointer(e)[0];
    mouseupTime = x.invert(zoomedTransform.invert([timeX, 0])[0]);

    if (mouseupTime <= mousedownTime) {
      mousedownTime = null;
      mouseupTime = null;
      removeClipRange();
    } else {
      console.log("clip: ", mousedownTime, mouseupTime);
      setClipRange([mousedownTime, mouseupTime]);
    }
  }

  function onMousemove(e) {
    let timeX = d3.pointer(e)[0];

    if (timeX < x.range()[0]) {
      timeX = x.range()[0];
      setTimeTranslateSpeed(20 / zoomedTransform.k);
    } else if (timeX > x.range()[1]) {
      timeX = x.range()[1];
      setTimeTranslateSpeed(-20 / zoomedTransform.k);
    } else {
      setTimeTranslateSpeed(0);
    }

    let time = x.invert(zoomedTransform.invert([timeX, 0])[0]);
    cursorLabelUpdate(time);
    cursorTranslate(time, timeX, 0);

    if (isMousedown) {
      drawClipRanges();
    }
  }

  function onMouseleave(e) {
    if (isMousedown)
        onMouseup(e);
    d3.transition()
        .duration(1000)
        .on("end", loopCursorTranslateWithCurrentTime);
  }

  svg.on("mousedown", onMousedown)
      .on("mousemove", onMousemove)
      .on("mouseup", onMouseup)
      .on("mouseleave", onMouseleave);


  function timeTranslateBy(deltaX, durationTime) {
    return svg.transition()
      .duration(durationTime)
      .call(zoom.translateBy, deltaX, 0);
  }

  function loopTimeTranslateBy(deltaX, durationTime) {
    timeTranslateBy(deltaX, durationTime)
      .on("end", function() { loopTimeTranslateBy(deltaX, durationTime); });
  }

  function setTimeTranslateSpeed(speed) {
    if (timeTranslateSpeed == speed)
      return;
    timeTranslateSpeed = speed;
    if (speed == 0) {
      svg.transition();
    } else {
      loopTimeTranslateBy(speed, 500);
    }
  }

  function resumeTimeTranslate() {
    let s = timeTranslateSpeed;
    timeTranslateSpeed = 0;
    setTimeTranslateSpeed(s);
  }

  return svg.node();
}

document.getElementById("visualize_container").append(chart())

}

visualize();