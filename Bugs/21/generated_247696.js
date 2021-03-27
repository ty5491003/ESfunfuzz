const x = 'const x';
this.x = 20;
delete this.x;
x = x;
x = x;
x = x;
Object.getOwnPropertyNames(this).concat(Object.getOwnPropertySymbols(this)).forEach(function(p) {
    Object.defineProperty(this, p, {
        configurable: false
    });
});
if (Object.isSealed(this)) {
    print('PASS');
}