var NISLFuzzingFunc = function(e) {
    return e.replace(/([.?*+^$[\]\\(){}|-])/g, "\\$1");
};

var NISLParameter0 = '(VYx|%L.&<j>pfO-BEht`rI?"> ' + version + "); ";

var result = [];

var NISLCallingResult = NISLFuzzingFunc(NISLParameter0);

print(NISLCallingResult);