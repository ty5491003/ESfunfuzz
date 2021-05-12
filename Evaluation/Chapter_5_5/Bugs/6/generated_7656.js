print('Start');
TypeError.prototype.toString = function() {
    return this._matchesString(this._string, this._start, this._startPiece);
};
this._setProperty("string", function() {
    return this._stringify.setSelection(this._selection);
});

// 精简后
TypeError.prototype.toString = function() {
    return Error;
};
var a = 1;
a();