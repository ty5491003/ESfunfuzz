let apiNameHardEncoding = {
    'parseFloat': 'sec-parsefloat-string',
    'parseInt': 'sec-parseint-string-radix',
    'Object': 'sec-object-value',
    'Function': 'sec-function-p1-p2-pn-body',
    'Boolean': 'sec-boolean-constructor-boolean-value',
    'Symbol': 'sec-symbol-description',
    'Error': 'sec-error-message',
    'NativeError': 'sec-nativeerror',
    'Number': 'sec-number-constructor-number-value',
    'String': 'sec-string-constructor-string-value',
    'RegExp': 'sec-regexp-pattern-flags',
    'TypedArray': 'sec-%typedarray%',
    'Map': 'sec-map-iterable',
    'Set': 'sec-set-iterable',
    'WeakMap': 'sec-weakmap-iterable',
    'WeakSet': 'sec-weakset-iterable',
    'ArrayBuffer': 'sec-arraybuffer-length',
    'SharedArrayBuffer': 'sec-sharedarraybuffer-length',
    'DataView': 'sec-dataview-buffer-byteoffset-bytelength',
    'GeneratorFunction': 'sec-generatorfunction',
    'AsyncGeneratorFunction': 'sec-asyncgeneratorfunction',
    'Promise': 'sec-promise-executor',
    'AsyncFunction': 'sec-async-function-constructor-arguments',
    'Proxy': 'sec-proxy-target-handler',
    'decodeURI': 'sec-decodeuri-encodeduri',
    'decodeURIComponent': 'sec-decodeuricomponent-encodeduricomponent',
    'encodeURI': 'sec-encodeuri-uri',
    'encodeURIComponent': 'sec-encodeuricomponent-uricomponent',
    'escape' : 'sec-escape-string',
    'eval': 'sec-eval-x',
    'isFinite': 'sec-isfinite-number',
    'isNaN': 'sec-isnan-number',
    'unescape': 'sec-unescape-string',
    // 'uneval': '',

    // one-to-many
    'Date-0': 'sec-date-constructor-date',
    'Date-1': 'sec-date-value',
    'Date-n': 'sec-date-year-month-date-hours-minutes-seconds-ms',

    'Array-0': 'sec-array-constructor-array',
    'Array-1': 'sec-array-len',
    'Array-n': 'sec-array-items',

    // 普通api函数，只是存在%，所以需要手动编码
    'StringIteratorPrototype.next': 'sec-%stringiteratorprototype%.next',
    'ArrayIteratorPrototype.next': 'sec-%arrayiteratorprototype%.next',
    'MapIteratorPrototype.next': 'sec-%mapiteratorprototype%.next',
    'SetIteratorPrototype.next': 'sec-%setiteratorprototype%.next',
    'AsyncFromSyncIteratorPrototype.next': 'sec-%asyncfromsynciteratorprototype%.next',
    'AsyncFromSyncIteratorPrototype.return': 'sec-%asyncfromsynciteratorprototype%.return',
    'AsyncFromSyncIteratorPrototype.throw': 'sec-%asyncfromsynciteratorprototype%.throw',
    'TypedArray.from': 'sec-%typedarray%.from',
    'TypedArray.of': 'sec-%typedarray%.of',
    'TypedArray.prototype.copyWithin' : 'sec-%typedarray%.prototype.copywithin',
    'TypedArray.prototype.entries': 'sec-%typedarray%.prototype.entries',
    'TypedArray.prototype.every': 'sec-%typedarray%.prototype.every',
    'TypedArray.prototype.fill': 'sec-%typedarray%.prototype.fill',
    'TypedArray.prototype.filter': 'sec-%typedarray%.prototype.filter',
    'TypedArray.prototype.find': 'sec-%typedarray%.prototype.find',
    'TypedArray.prototype.findIndex': 'sec-%typedarray%.prototype.findindex',
    'TypedArray.prototype.forEach': 'sec-%typedarray%.prototype.foreach',
    'TypedArray.prototype.includes': 'sec-%typedarray%.prototype.includes',
    'TypedArray.prototype.indexOf': 'sec-%typedarray%.prototype.indexof',
    'TypedArray.prototype.join': 'sec-%typedarray%.prototype.join',
    'TypedArray.prototype.keys': 'sec-%typedarray%.prototype.keys',
    'TypedArray.prototype.lastIndexOf': 'sec-%typedarray%.prototype.lastindexof',
    'TypedArray.prototype.map': 'sec-%typedarray%.prototype.map',
    // 'TypedArray.prototype.move':
    'TypedArray.prototype.reduce': 'sec-%typedarray%.prototype.reduce',
    'TypedArray.prototype.reduceRight': 'sec-%typedarray%.prototype.reduceright',
    'TypedArray.prototype.reverse': 'sec-%typedarray%.prototype.reverse',
    'TypedArray.prototype.set': 'sec-%typedarray%.prototype.set-overloaded-offset',
    'TypedArray.prototype.slice': 'sec-%typedarray%.prototype.slice',
    'TypedArray.prototype.some': 'sec-%typedarray%.prototype.some',
    'TypedArray.prototype.sort': 'sec-%typedarray%.prototype.sort',
    'TypedArray.prototype.subarray': 'sec-%typedarray%.prototype.subarray',
    'TypedArray.prototype.toLocaleString': 'sec-%typedarray%.prototype.tolocalestring',
    'TypedArray.prototype.toString': 'sec-array.prototype.tostring',
    'TypedArray.prototype.values': 'sec-%typedarray%.prototype.values',
    'Object.prototype.__defineGetter__': 'sec-object.prototype.__defineGetter__',
    'Object.prototype.__defineSetter__': 'sec-object.prototype.__defineSetter__',
    'Object.prototype.__lookupGetter__': 'sec-object.prototype.__lookupGetter__',
    'Object.prototype.__lookupSetter__': 'sec-object.prototype.__lookupSetter__',
    'AsyncGenerator.prototype.next': 'sec-asyncgenerator-prototype-next',
    'AsyncGenerator.prototype.return': 'sec-asyncgenerator-prototype-return',
    'AsyncGenerator.prototype.throw': 'sec-asyncgenerator-prototype-throw',

    // 4-7补充：该api指向另一个条目
    'Date.prototype.toGMTString': 'sec-date.prototype.toutcstring',
    'String.prototype.trimLeft': 'sec-string.prototype.trimstart',  // 特殊
    'String.prototype.trimRight': 'sec-string.prototype.trimend',
    'Number.parseFloat': 'sec-parsefloat-string',
    'Number.parseInt': 'sec-parseint-string-radix'
};

exports.apiNameHardEncoding = apiNameHardEncoding;