Array.prototype.push(1);
Object.freeze(Array.prototype);
print(Array.prototype.push.call(Array.prototype.push));
print(Array.prototype.push.length);
try {
    new RegExp().constructor.prototype.exec();
} catch ($) {}