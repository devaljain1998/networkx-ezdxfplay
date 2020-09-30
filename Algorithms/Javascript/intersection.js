// Library Function:

// Given three colinear points p, q, r, the function checks if 
// point q lies on line segment 'pr' 
const onSegment = (p, q, r) => {
    if (q.x <= Math.max(p.x, r.x) && q.x >= Math.min(p.x, r.x) && 
        q.y <= Math.max(p.y, r.y) && q.y >= Math.min(p.y, r.y)) 
        return true; 
    return false; 
}

// To find orientation of ordered triplet (p, q, r). 
// The function returns following values 
// 0 --> p, q and r are colinear 
// 1 --> Clockwise 
// 2 --> Counterclockwise 
const getOrientation = (p, q, r) => {
    let val = (q.y - p.y) * (r.x - q.x) - (q.x - p.x) * (r.y - q.y); 

    if (val === 0) return 0;  // colinear 
    return (val > 0) ? 1: 2; // clock or counterclock wise         
}

// The function that returns true if line segment 'p1q1' 
// and 'p2q2' intersect. 
const doIntersect = (p1, q1, p2, q2) => {
    // Find the four orientations needed for general and 
    // special cases 
    let o1 = getOrientation(p1, q1, p2); 
    let o2 = getOrientation(p1, q1, q2); 
    let o3 = getOrientation(p2, q2, p1); 
    let o4 = getOrientation(p2, q2, q1); 

    // General case 
    if (o1 !== o2 && o3 !== o4) 
        return true; 

    // Special Cases 
    // p1, q1 and p2 are colinear and p2 lies on segment p1q1 
    if (o1 === 0 && onSegment(p1, p2, q1)) return true; 

    // p1, q1 and p2 are colinear and q2 lies on segment p1q1 
    if (o2 === 0 && onSegment(p1, q2, q1)) return true; 

    // p2, q2 and p1 are colinear and p1 lies on segment p2q2 
    if (o3 === 0 && onSegment(p2, p1, q2)) return true; 

    // p2, q2 and q1 are colinear and q1 lies on segment p2q2 
    if (o4 === 0 && onSegment(p2, q1, q2)) return true; 

    return false; // Doesn't fall in any of the above cases         
}

// Function to calculate the intersection point
// Reference: https://stackoverflow.com/questions/13937782/calculating-the-point-of-intersection-of-two-lines
const getIntersectionPoint = (x11, y11, x12, y12, x21, y21, x22, y22) => {
    var slope1, slope2, yint1, yint2, intx, inty;
    if (x11 == x21 && y11 == y21) return [x11, y11];
    if (x12 == x22 && y12 == y22) return [x12, y22];

    slope1 = this.slope(x11, y11, x12, y12);
    slope2 = this.slope(x21, y21, x22, y22);
    if (slope1 === slope2) return false;

    yint1 = this.yInt(x11, y11, x12, y12);
    yint2 = this.yInt(x21, y21, x22, y22);
    if (yint1 === yint2) return yint1 === false ? false : [0, yint1];

    if (slope1 === false) return [y21, slope2 * y21 + yint2];
    if (slope2 === false) return [y11, slope1 * y11 + yint1];
    intx = (slope1 * x11 + yint1 - yint2)/ slope2;
    return {x: intx, y: slope1 * intx + yint1};
}


/*
BLUEPRINT:

line: start, end

const getIntersection(line1, beams) -> 



*/
const getSleevePoints = (line, beams) => {
    let sleeves = []

    p1 = line[0]
    q1 = line[1]

    beams.forEach(beam => {
        p2 = beam[0]
        q2 = beam[1]

        if (doIntersect(p1, q1, p2, q2)) {
            const intersectionPoint = getIntersectionPoint(p1.x, p1.y, q1.x, q1.y, p2.x, p2.y, q2.x, q2.y)
            sleeves.push(intersectionPoint)
        }
            
    })

    return sleeves
}

/*


detectPointInPolygon

*/

const isPointInsidePolygon = (point, polygon) => {
    // Logic:
    const n = polygon.length

    if (n < 3) return false

    let extreme = {x: Number.MAX_VALUE, y: point.y}

    let count = 0
    let i = 0

    do {
        next = (i + 1) % n

        if (doIntersect(polygon[i], polygon[next], p, extreme)) {
            if (getOrientation(polygon[i], p, polygon[next]) === 0)
                return onSegment(polygon[i], p, polygon[next]); 
            
            count++;
        }

        i = next;
    } while (i != 0)
    // Return true if count is odd, false otherwise 
    return count & 1;
}

/*

nearestTwoLinesToAPoint

*/
/*

nearestLineToAPoint


*/

const getLinesSortedByDistance = (lines) => {
    var getDist = (x, y, x1, y1, x2, y2) => {
        return Math.abs(((x * (y2 - y1)) - (y * (x2 - x1)) + (x2 * y1) - (y2 * x1))) / Math.sqrt(((y2 - y1) ^ 2) + ((x2 - x1) ^ 2));
    }

    var comparator = (a, b) => {
        distA = getDist(point.x, point.y, a[0].x, a[0].y, a[1].x, a[1].y)
        distB = getDist(point.x, point.y, b[0].x, b[0].y, b[1].x, b[1].y)
        
        if (distA == distB) return 0;
        return distA < distB ? -1 : 1;
    }

    lines.sort(comparator)

    return lines;
}

const getNearestLineToAPoint = (point, lines) => {
  lines = getLinesSortedByDistance(lines);
  // Returning the first lines
  return { firstNearestLine: lines[0] };
};

const getNearestTwoLinesToAPoint = (point, lines) => {
    // Edge cases
    if (lines.length < 2) {
        throw RangeError("The length of the lines should be atleast two.")
    }

    let referenceLines = [...lines]

    // const firstNearestLine = getNearestLineToAPoint(point, referenceLines)

    // // Removing the value from the refernce line
    // const index = referenceLines.indexOf(firstNearestLine);
    // if (index > -1) {
    //     referenceLines.splice(index, 1);
    // }

    // const secondNearestLine = getNearestLineToAPoint(point, referenceLines)

    // sorting the reference lines:
    referenceLines = getLinesSortedByDistance(referenceLines)

    const firstNearestLine = referenceLines[0]
    const secondNearestLine = referenceLines[1]

    return {firstNearestLine, secondNearestLine}
}

export {getIntersectionPoint,  getSleevePoints,  isPointInsidePolygon, getNearestLineToAPoint, getNearestTwoLinesToAPoint};