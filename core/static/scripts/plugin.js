
// Mechanism for Javascripts outside of the Tiqit core to be called from the
// Tiqit core.
Tiqit.pluginManager = (function() {
  var handlers = new Object();

  function registerPlugin(pluginHandlers) {
    for (var key in pluginHandlers) {
      if (handlers[key] === undefined) {
        handlers[key] = new Array();
      }
      handlers[key] = handlers[key].concat(pluginHandlers[key])
    } 
  }

  // Call all plugins registered with a "name" handler. Return the results in
  // an array.
  function call(name, args) {
    var out = new Array();

    if (handlers[name] !== undefined) {
      for (var i in handlers[name]) {
        var element = handlers[name][i].apply(undefined, args);

        if (element instanceof Array) {
          out = out.concat(element);
        } else {
          out.push(element);
        }
      }
    }

    return out;
  }

  // Public
  return {
    'registerPlugin': registerPlugin,
    'call': call,
  };
})();

