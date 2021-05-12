if (RegExp.prototype.toString.hasOwnProperty('length') !== true) {
    $ERROR('#0: RegExp.prototype.toString.hasOwnProperty(\'length\') === true');
}
if (delete RegExp.prototype.toString.length !== true) {
    $ERROR('#1: delete RegExp.prototype.toString.length === true');
}
if (RegExp.prototype.toString.hasOwnProperty('length') !== false) {
    $ERROR('#2: delete RegExp.prototype.toString.length; RegExp.prototype.toString.hasOwnProperty(\'length\') === false');
}