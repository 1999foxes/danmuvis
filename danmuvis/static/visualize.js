async function visualize() {

highlight = await fetch('/highlight/' + filename).then(response => response.json());


yLabel = 'density';
deltaTime = 10;
data = highlight[yLabel];

height = 150
width = 1000
margin = ({top: 20, right: 20, bottom: 30, left: 30})

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

  const gx = svg.append("g")
      .call(xAxis, x);

  svg.append("g")
      .call(yAxis, y);

  let mousedownTime, mouseupTime;

  const clipRangeRect = svg.append("rect")
      .style("fill", "red")
      .style("opacity", 0.4)
      .attr("height", height)
      .attr("width", 0);

  const zoom = d3.zoom()
      .scaleExtent([1, 32])
      .extent([[margin.left, 0], [width - margin.right, height]])
      .translateExtent([[margin.left, -Infinity], [width - margin.right, Infinity]])
      .on("zoom", zoomed)
      .filter(filterWheelOnly);

  let zoomedTransform;

  function zoomed(event) {
    zoomedTransform = event.transform;
    const xz = event.transform.rescaleX(x);
    path.attr("d", area(data, xz));
    if (mousedownTime != null)
        clipRangeRect.attr("x", xz(mousedownTime));
    if (mouseupTime != null && mouseupTime > mousedownTime)
        clipRangeRect.attr("width", xz(mouseupTime) - xz(mousedownTime));
    gx.call(xAxis, xz);
  }

  function filterWheelOnly(event) {
    return event instanceof WheelEvent;
  }

  svg.call(zoom)
    .call(zoom.scaleTo, 1);

  cursor = svg.append('rect')
      .attr('width', 1)
      .attr('height', 500)
      .style('fill', 'red');

  cursorLabel = svg.append("text")
      .text("0:00:00.000")
      .attr("x", margin.left + 10)
      .attr("y", margin.top + 10)
      .style('fill', 'black')
      .style('font-weight', 'bold')
      .style('font-size', '15px');

  function followTime(time, timeX, durationTime) {
    cursor
      .transition()
        .duration(durationTime)
        .attr("x", timeX);
    return cursorLabel
      .transition()
        .duration(durationTime)
        .text(new Date(time * 1000).toISOString().substr(12, 11))
        .attr("x", (width - timeX > 100 ? timeX + 10 : timeX - 100));
  }

  function loopingFollowTime() {
    let time = videoElement.currentTime;
    let timeX = zoomedTransform.rescaleX(x)(time);
    followTime(time, timeX, 1000)
        .on("end", loopingFollowTime);
  }

  loopingFollowTime();

  svg.on("mousedown", function(e, d) {
    let timeX = d3.pointer(e)[0];
    let time = x.invert(zoomedTransform.invert([timeX, 0])[0]);
    videoElement.currentTime = time;
    mousedownTime = time;
    mouseupTime = null;
    clipRangeRect.attr("x", timeX)
      .attr("width", 0);
  });

  svg.on("mouseup", function(e, d) {
    let timeX = d3.pointer(e)[0];
    mouseupTime = x.invert(zoomedTransform.invert([timeX, 0])[0]);

    if (mouseupTime <= mousedownTime) {
      mousedownTime = null;
      mouseupTime = null;
    } else {
      console.log("clip: ", mousedownTime, mouseupTime);
      addClipRange([mousedownTime, mouseupTime]);
    }
  });

  svg.on("mousemove", function(e) {
    let timeX = d3.pointer(e)[0];

    if (timeX < x.range()[0])
        timeX = x.range()[0];
    else if (timeX > x.range()[1])
      timeX = x.range()[1];

    let time = x.invert(zoomedTransform.invert([timeX, 0])[0]);

    followTime(time, timeX, 0);

    d3.transition                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    ()
        .duration(1000)
        .on("end", loopingFollowTime);

    if (mousedownTime != null && mouseupTime == null) {
      videoElement.currentTime = time;
      clipRangeRect.attr("width",
        (timeX > clipRangeRect.attr("x") ? timeX - clipRangeRect.attr("x") : 0)
      );
    }
  });

  function timeTranslateBy(deltaX, durationTime) {
    return svg.transition()
      .duration(durationTime)
      .call(zoom.translateBy, deltaX, 0);
  }

  function loopingTimeTranslateBy(deltaX, durationTime) {
    timeTranslateBy(deltaX, durationTime)
      .on("end", function() { loopingTimeTranslateBy(deltaX, durationTime); });
  }

  svg.append("rect")
      .attr("x", width - 100)
      .attr("width", 100)
      .attr("height", height)
      .attr("fill", "black")
      .attr("opacity", 0)
      .on("mouseover", function(e) {
        loopingTimeTranslateBy(-10 / zoomedTransform.k, 500);
      })
      .on("mouseleave", function() {
        svg.transition();
      });

  svg.append("rect")
      .attr("width", 100)
      .attr("height", height)
      .attr("fill", "black")
      .attr("opacity", 0)
      .on("mouseover", function(e) {
        loopingTimeTranslateBy(10 / zoomedTransform.k, 500);
      })
      .on("mouseleave", function() {
        svg.transition();
      });

  return svg.node();
}

document.body.append(chart())

}

visualize();