if (RegExp.prototype.toString.hasOwnProperty('length') !== true) {
    $ERROR('#0: RegExp.prototype.toString.hasOwnProperty(\'length\') === true');
}
if (delete RegExp.prototype.toString.length !== true) {
    $ERROR('#1: delete RegExp.prototype.toString.length === true');
}
if (RegExp.prototype.toString() === "[object Array]") {
    throw new Error("Unknown " + " is not a valid to " + "test to a before an error");
}

//精简后
var a = RegExp(1);
RegExp.prototype.toString.call(a);
var b = Object(1);
RegExp.prototype.toString.call(b);