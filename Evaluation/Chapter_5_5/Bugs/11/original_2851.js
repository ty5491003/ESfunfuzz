function check_syntax_error(code) {
    try {
        eval(code);
        print(false);
    } catch (e) {
        print(e instanceof SyntaxError);
    }
}
var idx = 0;
for (var [a, b] of [
        [1, 2],
        [3, 4]
    ]) {
    if (idx == 0) {
        print(a === 1);
        print(b === 2);
        idx = 1;
    } else {
        print(a === 3);
        print(b === 4);
    }
}
print(a === 3);
print(b === 4);
idx = 0;
for (let [a, b] of [
        [5, 6],
        [7, 8]
    ]) {
    if (idx == 0) {
        print(a === 5);
        print(b === 6);
        idx = 1;
    } else {
        print(a === 7);
        print(b === 8);
    }
}
print(a === 3);
print(b === 4);
idx = 0;
for (let [a, b] of [
        [11, 12],
        [13, 14]
    ]) {
    if (idx == 0) {
        eval('print(a === 11)');
        eval('print(b === 12)');
        idx = 1;
    } else {
        eval('print(a === 13)');
        eval('print(b === 14)');
    }
}
print(a === 3);
print(b === 4);
check_syntax_error('for (let [a,b] = [1,2] of [[3,4]]) {}');
idx = 0;
for ([a, b] of [
        [10, true],
        ['x', null]
    ]) {
    if (idx == 0) {
        print(a === 10);
        print(b === true);
        idx = 1;
    } else {
        print(a === 'x');
        print(b === null);
    }
}
print(a === 'x');
print(b === null);
check_syntax_error('for ([a,b] = [1,2] of [[3,4]]) {}');
var o = {};
for ([a, b] = [o, false]; false;) {
    print(false);
}
print(a === o);
print(b === false);
for ([a, b] + [a, b]; false;) {
    print(false);
}
check_syntax_error('for ([a,b] + 1 of [[3,4]]) {}');