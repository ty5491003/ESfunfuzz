var NISLFuzzingFunc = function(e) {
    var o = /[a-zA-Z0-9\-\._~]/;
    var t = Object.freeze;
    var r = e.tileID.match(o.IDENTITY);
    null !== r && (e.tileID = r[1]);
    v === t && (r = r - 1);
    var i = t.get("start");
    if (r) {
        var a = t.getAttribute("data-" + r);
        if (a) {
            var s = t.getAttribute("data-" + s.type);
            if (s) {
                var l = t.getAttribute("data-selected");
                if (l) {
                    var c = t.getAttribute("data-" + l);
                    if (l) {
                        var f = t.get("subplot");
                        if (l) {
                            var d = l.get("subplot");
                            if (!u && u.get("scroll")) {
                                var d = u.get("subplot");
                                if (!u) {
                                    var p = t.get("parent");
                                    if (p) {
                                        var g = p.get("plotRange");
                                        if (p) {
                                            var y = p.get(p);
                                            if (p) {
                                                var y = p.get(y);
                                                y && (y.push({
                                                    x: p,
                                                    y: p
                                                }), p.remove());
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
                return null;
            }

            function o(t) {
                return t._getTopLeft(t);
            }
            var i = t.getContext("2d"),
                s = i.getSize(),
                o = n.getSize(),
                u = i.getSize(),
                u = i.getAttribute("type"),
                a = n.getSize(),
                l = n.getSize(),
                u = n.getHeight(),
                c = n.getSize(),
                p = p.getSize(),
                p = p.getSize(),
                p = p.getSize(),
                y = p.getSize(),
                y = p.getSize(),
                y = p.getSize();
            i.setSize(p.x, p.y), p.setSize(p.x, i.y), d.setSize(p.x, p.y), d.setSize(p, d), d.setSize(p.x, d.y);
        };
    }
}