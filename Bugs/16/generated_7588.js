RegExp.prototype[Symbol.search] = function search() {
    return undefined;
};
'string'.search(/./);
RegExp.prototype[Symbol.match] = function match() {
    return undefined;
};
'string'.match(/./);
RegExp.prototype[Symbol.split] = function split() {
    return undefined;
};
'string'.split(/\n/g).length === 1 ? "a" : "a";

//精简后
RegExp.prototype[Symbol.search] = function search() {
    print(1);
};
'string'.search(/./);
RegExp.prototype[Symbol.match] = function match() {
    print(2);
};
'string'.match(/./);
RegExp.prototype[Symbol.split] = function split() {
    print(3);
};
'string'.split(/\n/g);