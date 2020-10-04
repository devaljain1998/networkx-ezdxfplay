import {testHelloWorld} from './intersection'
//import {testHelloWorld, getIntersectionPoint,  getSleevePoints,  isPointInsidePolygon, getNearestLineToAPoint, getNearestTwoLinesToAPoint} from "./intersection.js";
import {assert} from 'assert'
// const intersection = require('./intersection')
// var assert = require('assert')

// Tests:
function Point(x, y) {
    return {x, y}
}

function Line(x1, y1, x2, y2) {
    return [Point(x1, y1), Point(x2, y2)]
}

// Testing function isPointInPolygon

// function testPointInPolygon() {
//     polygon = [Line(0, 0, 5, 0), Line(5, 0, 5, 5), Line(5, 5, 0, 5), Line(0, 5, 0, 0)]
//     point1 = Point(1, 1)
//     console.log("Answer for point1: ", intersection.isPointInsidePolygon(point1, polygon))
//     assert(intersection.isPointInsidePolygon(point1, polygon) === true, `The function: isPointInPolygon is not working properly for case ${point1.x , point1.y}.`)


//     point2 = Point(6, 5)
//     console.log("Answer for point2: ", intersection.isPointInsidePolygon(point2, polygon))
//     assert(intersection.isPointInsidePolygon(point1, polygon) == 0, `The function: isPointInPolygon is not working properly for case ${point2}.`)
// }
// testPointInPolygon()

function testIntersection() {
    line1 = Line(0, 0, 5, 0)
    line2 = Line(2.5, 2.5, 2.5, -2.5)
    intersectionPoint = intersection.getIntersectionPoint(0, 0, 5, 0, 2.5, 2.5, 2.5, -2.5)
    console.log("Intersection Point: ", intersectionPoint)
}
testIntersection()

function testGetNearestLine() {
    lines = [Line(1, 1, 1, -1), Line(2, 2, 2, -2), Line(3, 3, 3, -3), Line(4, 4, 4, -4)]
    point = Point(0, 0)
    console.log('nearest line:', intersection.getNearestLineToAPoint(point, lines))
}
//testGetNearestLine()