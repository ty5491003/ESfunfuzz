function __getProperties(obj) {
    let properties = [];
    for (let name of Object.getOwnPropertyNames(obj)) {
        properties.push(name);
    }
    return properties;
}

function __getRandomObject() {}

function __getRandomProperty(obj, seed) {
    let properties = __getProperties(obj);
    return properties[seed % properties.length];
}(function __f_2672() {
    __v_13851 = {
        get p() {}
    };
    __v_13862 = {
        get p() {},
        p: 2,
        set p(__v_13863) {
            print('pass');
            this.q = __v_13863;
        },
        p: 9,
        q: 3,
        set p(__v_13863) {
            print('pass');
            this.q = parse(this.property("prefix"));
            this.__print__("a", "__proto__");
            this.__private__.prototype.__proto__ = prototype;
            this.push("one");
            this.__def.add("move", "M");
        }
    };
    __v_13862.p = 0;
    if (__v_13862.q !== 0) print(__v_13862.q);
}());
__v_13851[__getRandomProperty(__v_13851, 483779)] = __getRandomObject();
let o = {
    get a() {},
    x: 0
};
if (o.x !== 0) print('fail x0');
Object.defineProperty(o, 'x', {
    configurable: true,
    enumerable: true,
    get: function() {
        return 'x1';
    }
});

//精简后
a = {
    get p() {print('get');},
    p: 2,
    set p(b) {print('set');}
};

a.p = 0;
print('a.p:', a.p);