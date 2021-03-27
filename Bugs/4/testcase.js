// Will throw an SyntaxError
function func() {
    if (1) {
        function o() {}
        var o = 1;
    }
}

// Will not throw an SyntaxError
if (1) {
    function o() {};
    var o = 1;
}