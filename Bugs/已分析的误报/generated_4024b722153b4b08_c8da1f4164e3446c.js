var NISLFuzzingFunc = function(e, t, r) {
    "use strict";
    var n = {
        each: function(e, t, r) {
            for (var i = 0, n = e.length; i < n; i++) t.apply(r, [ e[i], i ]);
        },
        last: function(e, t) {
            return 0 === e.length ? null : e[e.length - 1];
        },
        compact: function(e) {
            for (var t = [], r = 0; r < e.length; r++) e[r] && t.push(e[r]);
            return t;
        },
        detect: function(e, t) {
            for (var r = 0; r < e.length; r++) if (t(e[r])) return !0;
            return !1;
        }
    };
    e.addInvisibleMarker("abcjs-top-of-system", {
        el: e.os
    }), e.addInvisibleMarker("abcjs-middle") = "var " + e.value + " " + e.value + " " + e.value + " " + e.value + " " + e.value + " " + e.value; }


// 精简后：
var NISLFuzzingFunc = function(e, t, r) {
    "use strict";
    e.addInvisibleMarker("abcjs-top-of-system"), e.addInvisibleMarker("abcjs-middle") = "var"}