print('Start');
TypeError.prototype.toString = function() {
    quit();
};
try {
    throw new TypeError();
} catch (e) {
    print('Caught');
    try {
        print(e.stack);
    } catch (other) {
        print('Caught:', other);
    }
}