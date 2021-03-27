function f2() {
    [ 1 ].forEach(function(e) {
        try {
            throw "abc";
        } catch (e) {
            var x = e;
            x;
        }
    });
}

f2();

function f3() {
    var e = "outer";
    try {
        throw "throw 1";
    } catch (e) {
        var x = e;
        e;
        function foo() {
            var r = false;
            return f(r);
        }
        function e() {
            return e;
        }
        function e() {
            return e;
        }
        function e() {
            return e;
        }
        return f();
    }
}


// 精简后：
if (1) {
    function o() {}
    var o = 1;
}

