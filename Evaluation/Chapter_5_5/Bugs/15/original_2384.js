var target = function() {};
var handler = {
    defineProperty(target) {
        throw 42;
    },
    construct() {
        return {};
    }
};
var proxy = new Proxy(target, handler);
Array.of.call(proxy, 5);
var g_target, g_name;
var handler = {
    defineProperty: function(target, name, desc) {
        g_target = target;
        g_name = name;
        return true;
    }
};
var target = {};
var proxy = new Proxy(target, handler);
var desc = {
    value: 1,
    writable: true,
    configurable: true
};
Object.defineProperty(proxy, 'foo', desc);
print(target === g_target);
print('foo' === g_name);
var handler = {
    defineProperty: function(target, name, desc) {
        Object.defineProperty(target, name, desc);
    }
};
var proxy = new Proxy(target, handler);
try {
    Object.defineProperty(proxy, 'bar', desc);
    print(false);
} catch (e) {
    print(e instanceof TypeError);
}
var bar = Object.getOwnPropertyDescriptor(proxy, 'bar');
print(bar.value === 1);
print(bar.writable);
print(bar.configurable);
try {
    Object.defineProperty(proxy, 'name', {});
    print(false);
} catch (e) {
    print(e instanceof TypeError);
}
var target = {};
var handler = {
    defineProperty: 1
};
var proxy = new Proxy(target, handler);
try {
    Object.defineProperty(proxy, 'foo', {
        value: 'foo'
    });
    print(false);
} catch (e) {
    print(e instanceof TypeError);
}
var target = {};
var handler = {
    defineProperty: undefined
};
var proxy = new Proxy(target, handler);
var desc = {
    value: 1
};
Object.defineProperty(proxy, 'prop1', desc);
print(proxy.prop1 === 1);
var target2 = {};
var proxy2 = new Proxy(target2, {});
Object.defineProperty(proxy2, 'prop2', desc);
print(proxy2.prop2 === 1);
var target = {};
var handler = {
    defineProperty: function(target, name, desc) {
        return true;
    }
};
var proxy = new Proxy(target, handler);
Object.preventExtensions(target);
try {
    Object.defineProperty(proxy, 'foo', {
        value: 1
    });
    print(false);
} catch (e) {
    print(e instanceof TypeError);
}
var target = {};
var desc = {
    value: 1,
    writable: true,
    configurable: false,
    enumerable: true
};
var proxy = new Proxy(target, handler);
try {
    Object.defineProperty(proxy, 'foo', desc);
    print(false);
} catch (e) {
    print(e instanceof TypeError);
}
var target = {};
var handler = {
    defineProperty: function(target, name, desc) {
        return true;
    }
};
var proxy = new Proxy(target, handler);
Object.defineProperty(target, 'foo', {
    value: 1,
    writable: false,
    configurable: false
});
try {
    Object.defineProperty(proxy, 'foo', {
        value: 2
    });
    print(false);
} catch (e) {
    print(e instanceof TypeError);
}
target.bar = 'baz';
try {
    Object.defineProperty(proxy, 'bar', {
        value: 2,
        configurable: false
    });
    print(false);
} catch (e) {
    print(e instanceof TypeError);
}
var trapCalls = 0;
var p = new Proxy({}, {
    defineProperty: function(t, prop, desc) {
        Object.defineProperty(t, prop, {
            configurable: false,
            writable: true
        });
        trapCalls++;
        return true;
    }
});
try {
    Reflect.defineProperty(p, 'prop', {
        writable: false
    });
    print(false);
} catch (e) {
    print(e instanceof TypeError);
}
print(trapCalls == 1);