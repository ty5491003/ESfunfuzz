var NISLFuzzingFunc = function() {
    var t = this.__proto__, e = t in this.constructor ? this.constructor : t, n = e in this.constructor ? this.constructor.name : this.constructor;
    if (this.constructor === Object) return this.constructor.prototype;
    var t = this.constructor.call(this, t);
    return this.then(function(e) {
        return n ? [ e, n ] : [ t, t ];
    }).otherwise(function(e) {
        return n ? [ e, e ] : [ t, t ];
    }).then(function(e) {
        return n ? [ e, e ] : e;
    });
};

var NISLCallingResult = NISLFuzzingFunc();

print(NISLCallingResult);