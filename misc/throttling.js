// David Nolen pointed out http://underscorejs.org/docs/underscore.html#section-64
// as an example of hairy code. I wrote this to understand it. Everything on this
// page is untested.

// Basis to elaborate on: a wrapper for func.
function unthrottled(func) {
    return function() {
        return func.apply(this, arguments);
    };
}

// For the following wrappers for func let's say a 'request' is when
// you call the wrapper; and when the wrapper actually calls func,
// that's a 'call'.

// A sync throttle: any requests within refractoryPeriod after the
// last call get the last call's result.
function throttle(func, refractoryPeriod) {
    var lastTime = -refractoryPeriod, lastResult;
    return function() {
        var now = Date.now();
        if (lastTime + refractoryPeriod <= now) {
            lastTime = now;
            lastResult = func.apply(this, arguments);
        }
        return lastResult;
    };
}

// A simplest async throttle-ish thing: call func() periodically until
// someone calls .stop(); get the latest result from .value.
function throttle(func, interval) {
    function update() {
        result.value = func(); // N.B. different interface
        timeoutId = setTimeout(update, interval);
    }
    var result = {
        value: undefined,
        stop: function() { clearTimeout(timeoutId); },
    };
    var timeoutId = setTimeout(update, 0);
    return result;
}

// Fancier: like Underscore's, passes `this` and arguments each time.
// Unlike Underscore's, it always calls the func asynchronously. This
// happens every interval msec, using the most recent this/arguments
// each time, until the whole interval goes by without a request. (It
// still does one final update then, like Underscore's.)
function throttle(func, interval, value) {
    // Return the most recent async result, and ensure it'll get
    // updated.
    function ask() {
        context = this, args = arguments;
        asked = true;
        schedule(0);
        return value;
    }
    function schedule(wait) {
        if (timeoutId === null)
            timeoutId = setTimeout(update, wait);
    }
    function update() {
        timeoutId = null;
        if (asked) schedule(interval);
        asked = false;
        value = func.apply(context, args);
    }
    var context, args;
    var asked = false, timeoutId = null;
    return ask;
}

// Mixed sync/async throttling, Underscore-style.
// A request in the refractoryPeriod after a call schedules an async
// call for the end of the period, and immediately returns the last
// result. Other requests call func immediately. The async call uses
// `this` and `arguments` from the most recent request.
function throttle(func, refractoryPeriod) {
    var lastResult, context, args;
    var lastCallTime = -refractoryPeriod, timeoutId = null;
    function ask() {
        context = this, args = arguments;
        var now = Date.now();
        var refractory = lastCallTime + refractoryPeriod - now;
        if (0 < refractory) {
            // We're in the refractory period after a call.
            if (timeoutId === null)
                timeoutId = setTimeout(update, refractory);
        } else {
            // We're good to go. First cancel any lagging async call.
            clearTimeout(timeoutId);
            update(now);
        }
        return lastResult;
    }
    function update(now) {
        timeoutId = null;
        lastCallTime = now || Date.now();
        lastResult = func.apply(context, args);
    }
    return ask;
}

// Editorial: Underscore's works out to be nearly the same code as I'd
// write for the same spec, but as usual with Underscore it's scantily
// documented and it's a pain to reverse-engineer the details.

// Mixing sync and async calls to the same function seems a recipe for
// trouble and I wonder if it's a root cause of the complexity of this
// function too.
