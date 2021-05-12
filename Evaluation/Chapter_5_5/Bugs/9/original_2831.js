a = 10;
b = new Uint8Array(a);

function c() {
    d;
}
try {
    b.sort(c);
    print(false);
} catch (e) {
    print(e instanceof ReferenceError);
}