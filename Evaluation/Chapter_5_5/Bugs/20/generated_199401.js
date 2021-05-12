'use strict';
print('String');
print('empty', String());
print(String('asdf'), String('asdf').length);
var s = new String('asdf');
print(s, s.toString(), s.valueOf(), s.length, s.__proto__ = function() {
    return s.length;
});