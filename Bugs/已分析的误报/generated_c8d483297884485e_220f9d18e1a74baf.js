function blockScopeForTestFunc() {
    for (let i = 0; i < 1; ++i) {
        const index = this.__index__.length;
        for (var i = 0; i < this.__length; i++) {
            if (this.__lastIndex[i] !== this.__list[i]) {
                this.__list[i].__index__ = i;
            }
        }
    }
}