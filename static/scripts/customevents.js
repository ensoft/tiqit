
//
// Custom Event Handling
//

customEvents = new Array();

function addCustomEventListener(event, handler) {
  if (!customEvents[event]) {
    customEvents[event] = new Array();
  }

  if (!contains(customEvents[event], handler)) {
    customEvents[event].push(handler);
  }
}

function removeCustomEventListener(event, handler) {
  if (event in customEvents) {
    arrayRemove(customEvents[event], handler);
  }
}

function generateCustomEvent(event, target) {
  if (event in customEvents) {
    var ev = new Object();
    ev.target = target;
    for (var i = 0; i < customEvents[event].length; i++) {
      // Protect callers from exceptions in event handlers
      try {
        customEvents[event][i](ev);
      } catch (err) {
        // Do nothing
      }
    }
  }
}
