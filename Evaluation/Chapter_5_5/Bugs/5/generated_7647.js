var a = new Int32Array([1, 2, 3, 4, 5]);
print(a.subarray().toString());
a.set(a.length, a.length);
a.set(a.length, a.length);

// 精简后
var a = new Int32Array([1, 2, 3, 4, 5]);
a.set(1);
