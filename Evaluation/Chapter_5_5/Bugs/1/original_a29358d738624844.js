var NISLFuzzingFunc = function(e) {
    var o = /[a-zA-Z0-9\-\._~]/;
    var t = Object.freeze;
    var r = e.tileID.match(o.IDENTITY);
    null !== r && (e.tileID = r[1]);
    var i = t(e.imageData, r[2]);
    t(i) && (e.imageData = i);
};
var NISLParameter0 = 88921935;
var NISLCallingResult = NISLFuzzingFunc(NISLParameter0);
print(NISLCallingResult);