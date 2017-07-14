
//
// Global Scripts
//

Tiqit = (function() {
    // Private
    var firstWindowLoadFired = false;
    window.addEventListener('load', function(ev) {
        if (!firstWindowLoadFired) {
            generateCustomEvent('FirstWindowLoad', ev.target);
            firstWindowLoadFired = true;
        }
    }, false);

    // Public
    return {
	// Utility Functions
	objectHasKeys: function(obj) {
	    var key;
	    for (key in obj) {
		if (obj.hasOwnProperty(key)) {
		    return true;
		}
	    }
	    return false;
	},
        handleXMLMessages: function(doc) {
            var msgs = doc.getElementsByTagName('message');

            // If there were any messages, print them out
            for (var i = msgs.length - 1; i >= 0; i--) {
                sendMessage(msgs[i].getAttribute('type'), msgs[i].textContent, '', true);
            }
        },
        indicateUnknown: function(input) {
            Tiqit.addIndicator(input);
            input.parentNode.tiqitIndicator.title = 'This value is not a known valid value for this field';
            input.parentNode.tiqitIndicator.style.backgroundImage = 'url("images/warning-small.png")';
            input.parentNode.style.borderColor = 'red';
            input.parentNode.tiqitIndicator.style.display = 'inline';
        },
        indicateLoading: function(input) {
            Tiqit.addIndicator(input);
            input.parentNode.tiqitIndicator.title = 'Loading related data...';
            input.parentNode.tiqitIndicator.style.backgroundImage = 'url("images/fetching-small.gif")';
            input.parentNode.style.borderColor = 'transparent';
            input.parentNode.tiqitIndicator.style.display = 'inline';
        },
        clearIndicator: function(input) {
            if (input.parentNode.tiqitIndicator) {
                input.parentNode.style.borderColor = 'transparent';
                input.parentNode.tiqitIndicator.style.display = 'none';
            }
        },
        addIndicator: function(input) {
            if (!input.parentNode.tiqitIndicator) {
                input.parentNode.tiqitIndicator = document.createElement('a');
                input.parentNode.tiqitIndicator.className = 'tiqitIndicator';
                input.parentNode.tiqitIndicator.style.display = 'none';
                input.parentNode.appendChild(input.parentNode.tiqitIndicator);
            }
        },
    };
})();

//
// Utility Functions
//

var inited = false;
function runInitOnce() {

    if (!inited) {
        init();
        inited = true;
    }
}

String.prototype.trim = function() {
  return this.replace(/^\s+|\s+$/g, "");
}

function contains(array, item) {
  if (array.indexOf) {
    return (array.indexOf(item) != -1);
  } else {
    for (idx in array) {
      if (array[idx] == item)
	return true;
}
    return false;
  }
}

function arrayRemove(arr, val) {
  for (var i = 0; i < arr.length; i++) {
    if (arr[i] == val) {
      arr.splice(i, 1);
    }
  }
}

function selectSort(sel, reverse) {
  var selected = sel.value;
  var opts = new Array();
  for (var i = 0; i < sel.options.length; i++) {
    opts.push(sel.options[i]);
  }
  opts.sort(function(a, b) {
          // NOFILTER is for some inexplicable reason always lowest
          var retval;
          if (a.value == b.value) {
              return 0;
          } else if (a.value == 'NOFILTER') {
              return reverse ? 1 : -1;
          } else if (b.value == 'NOFILTER') {
              return reverse ? -1 : 1;
          } else if (reverse) {
            return a.value < b.value;
          } else {
            return b.value < a.value;
          }
      });
  for (var i = 0; i < opts.length; i++) {
    sel.add(opts[i], null);
  }
  sel.value = selected;
}

function getElementsByClassName(className, parent, tagName) {
  var retval = new Array();
  if (parent == null) {
    parent = document;
  }
  if (tagName == null) {
    tagName = "*";
  }
  var els = parent.getElementsByTagName(tagName);
  var pattern = new RegExp("(^|\\s)" + className + "(\\s|$)");
  for (var i = 0; i < els.length; i++) {
    if (pattern.test(els[i].className)) {
      retval.push(els[i]);
    }
  }
  return retval;
}

function getAncestorOfType(node, ancestorType) {
  while (node && node.nodeName != ancestorType) {
    node = node.parentNode;
  }

  return node;
}

function isAncestorOf(ancestor, node) {
  while (node && node != ancestor) {
    node = node.parentNode;
  }

  return node == ancestor;
}

function getClientPos(obj) {
  var x = 0, y = 0;
  var objTrail = obj;

  while (objTrail) {
    x += objTrail.offsetLeft;
    y += objTrail.offsetTop;
    objTrail = objTrail.offsetParent;
  }

  return new Array(x - window.scrollX, y - window.scrollY);
}

//
// Query string parsing
//

function parseQueryString(str) {
  var obj = new Object();

  if (str[0] == '?') {
    str = str.substring(1);
  }
  var args = str.split('&');
  for (var i = 0; i < args.length; i++) {
    var val = args[i].split('=');
    obj[val[0]] = val[1];
  }

  return obj;
}

//
// Section Show and hide
//

function showSection(name, dontgothere) {
  var section = document.getElementById('tiqitSectionContents' + name);
  var shower  = document.getElementById('show' + name + 'Button');
  var hider = document.getElementById('hide' + name + 'Button');

  if (section) {
    section.style.display = 'block';
    shower.style.display = 'none';
    hider.style.display = 'inline';

    if (!dontgothere) {
      document.location.hash = '#anchor' + name;
    }
  }
}

function hideSection(name) {
  var section = document.getElementById('tiqitSectionContents' + name);
  var shower  = document.getElementById('show' + name + 'Button');
  var hider = document.getElementById('hide' + name + 'Button');

  if (section) {
    section.style.display = 'none';
    shower.style.display = 'inline';
    hider.style.display = 'none';
  }
}

//
// Save Searches
//

// Validate a bug/search name. May prompt the user with alert() or confirm()
// dialog boxes.
//
// Return: 1 if the value is valid
// saveType: Either "bug" or "search".
// newName:  The value to be validated.
// editor: Input editor that contains the value being validated.
function validateSavedValue(saveType, newName, editor) {
  // Do some input validation.
  if (newName.length == 0) {
    alert("Please enter a name for this " + saveType);
    editor.focus();
    return 0;
  }

  var looksLikeBug = false;

  if (newName.length >= 10) {
      for (backend in Tiqit.config['backends']) {
        if (newName.indexOf(backend) == 0) {
            looksLikeBug = true;
            break;
        }
      }
  }

  // If the name looks like a bug id, check this is what the user wants.
  if (looksLikeBug) {
    if (!confirm("Looks like you were trying to search for a bug, and not " +
		 "name one. Are you sure you want to save with the name '" +
		 newName + "'?")) {
      var gotoBox = document.getElementById('tiqitGotoField');

      if (!gotoBox.value) {
      	gotoBox.value = newName;
      	gotoBox.focus();
      }

      return 0;
    }
  }

  return 1;
}

// saveType: either "bug" or "search", depending on what is being saved.
// bugid: If a bug is being saved, this is the ID of the bug to save.
// 
function saveSearch(button, saveType, bugid) {
  var input = document.getElementById("saveName");
  var newName = input.value;

  if (button.parentNode.parentNode.parentNode.parentNode.editing) {
    alert("Exit editing mode before saving.");
    return;
  }

  if (!validateSavedValue(saveType, newName, input)) {
    return;
  }

  // Construct the query string. For bugs this is just the bugid and name. For
  // searches this is the entire search query, with the name added on.
  var query = 'saveSearch.py';
  if (saveType === "bug") {
    query += "?bugid=" + bugid;
    value = "view.py" + query;
  } else {
    query += "?" + tiqitSearchQuery;
    value = "results.py" + query;
  }
  query += '&name=' + escape(newName);

  showSaveError = function(msg) {
    sendMessage(2, "Failed to save " + saveType + ": " + msg);
  }

  // Send the request, and handle the response.
  var req = new XMLHttpRequest();
  req.open('GET', query, true);
  req.onload = function(event) {
    if (event.target.status != 200) {
      showSaveError("Received bad server response.");
      return;
    }
    if (req.responseXML === null) {
      showSaveError("No body XML.");
      return;
    }
    var responseArray = req.responseXML.getElementsByTagName('saveSearchResponse');
    if (!responseArray || responseArray.length === 0) {
      showSaveError("Could not find response tag")
    }

    var response = responseArray[0];
    var saved = (response.getAttribute('saved') === "1");
    var exists = (response.getAttribute('exists') === "1");

    if (!saved) {
      if (confirm("A " + saveType + " with that name already exists. Overwrite?")) {
        req.open('GET', query + "&overwrite=true", true);
        req.send(null);
      }
    } else {
      var path;
      if (saveType == "bug") {
        path = "view/" + encodeURIComponent(newName);
      } else {
        path = "results/" + encodeURIComponent(tiqitUserID) + "/" + encodeURIComponent(newName);
      }
      addNewSearch(saveType, newName, path, value, exists);
    }
  }
  req.onerror = function(event) {
    showSaveError("Likely this is due to a networking issue.");
  }
  req.send(null);
}

function addNewSearch(saveType, name, path, value, overwrite) {
  var input = document.getElementById('saveName');
  var link;
  var toolbar = input.parentNode.parentNode.parentNode;
  var id = 'tiqitBar' + saveType + '' + escape(name);

  if (!overwrite) {
    link = document.createElement('a');
    link.setAttribute('href', path);
    link.appendChild(document.createTextNode(name));
    link.id = id;

    var sep = document.createElement('span');
    sep.appendChild(document.createTextNode(' | '));
    sep.className = 'tiqitBarSep';
    if (toolbar.getElementsByTagName("a").length == 0) {
      sep.style.display = 'none';
    } else {
      sep.style.display = 'inline';
    }

    var span = document.createElement('span');
    span.style.display = 'inline';
    span.appendChild(sep);
    span.appendChild(link);

    toolbar.insertBefore(span, input.parentNode.parentNode);
    toolbar.getElementsByClassName('tiqitBarIntroStr')[0].style.display = 'inline';
  } else {
    link = document.getElementById(id);
  }

  link.setAttribute('tiqitPrefValue', value);
  link.setAttribute('tiqitViewing', '1');

  input.parentNode.parentNode.style.display = 'none';
  input.parentNode.parentNode.getElementsByClassName("tiqitBarSep")[0].style.display
      = 'inline';
}

//
// Print Messages to the page
//

var msgTypes = new Array(new Array("/!\\", 'images/warning-small.png'),
                         new Array("(i)", 'images/about-small.png'),
                         new Array("[x]", 'images/error-small.png'));

function removeMessage(event) {
  event.target.parentNode.parentNode.removeChild(event.target.parentNode);
}

function sendMessage(type, message, extraclass, parsehtml) {
  var msg = document.createElement('p');

  if (!extraclass) {
    extraclass = '';
  }

  msg.className = 'tiqitMessage ' + extraclass;

  if (!parsehtml) {
    msg.appendChild(document.createTextNode(' ' + message));
  } else {
    // Use innerHTML so that messages with HTML in them work too.
    msg.innerHTML = ' ' + message;
  }

  var img = document.createElement('img');
  img.title = 'Clear Message';
  img.onclick = removeMessage;
  img.alt = msgTypes[type][0];
  img.src = msgTypes[type][1];

  msg.insertBefore(img, msg.firstChild);

  var content = document.getElementById('tiqitContent');
  content.insertBefore(msg, content.firstChild);

  return msg;
}

function tiqitNewsMarkRead(event) {
  var req = new XMLHttpRequest();
  req.onload = function(ev) {
    if (ev.target.status == 200) {
      event.target.parentNode.parentNode.removeChild(event.target.parentNode);
    } else {
      sendMessage(2, "Failed to mark all news as read.");
    }
  };
  req.onerror = function(ev) {
    sendMessage(2, "Networking error: failed to mark all news as read.");
  };
  req.open("GET", "news", true);
  req.send(null);
}

//
// Content functions (use values in fielddata.js)
//

// getFieldDisplay()
// 
// Create an element to display a field. Used for when such a field is
// dynamically altered or created by Javascript.
// 
// field: The type of field being displayed.
// 
// value: The value of the field
function getFieldDisplay(field, value) {
  if (contains(userFields, allFields[field]) && value) {
    var anchor = document.createElement('a');
    anchor.onclick = showUserDropDown;
    anchor.className = 'tiqitUserDropDown';
    anchor.appendChild(document.createTextNode(value));
    return anchor;
  } else if (field == 'Identifier') {
    var anchor = document.createElement('a');
    anchor.href = value;
    anchor.appendChild(document.createTextNode(value));
    return anchor;
  } else if (field == 'Link') {
    var container = document.createElement('a');
    var img = document.createElement('img');
	img.src = 'images/bug-tiny.png';
    container.href = value;
    container.title = value;
    container.appendChild(img);
    return container;
  } else if (field == 'CommitEncs') {
    var container = document.createElement('span');
    var vals = value.split(' ');
    var encs = ['Code-Review', 'Unit-Test', 'Static-Analysis'];
    for (idx in vals) {
      var img = document.createElement('img');
      var span = document.createElement('span');
      span.style.visibility = 'hidden';
      span.style.fontSize = '25%';
      if (vals[idx] == 'Y') {
	img.src = 'images/thumbs-up.gif';
	img.alt = '[Yes]';
	img.title = 'Has ' + encs[idx] + ' enclosure';
	span.appendChild(document.createTextNode('Y'));
      } else {
	img.src = 'images/thumbs-down.gif';
	img.alt = '[No]';
	img.title = 'Does not have ' + encs[idx] + ' enclosure';
	span.appendChild(document.createTextNode('N'));
      }
      // Only need a space after the first one
      if (idx > 0) {
        container.appendChild(document.createTextNode(' '));
      }
      container.appendChild(span);
      container.appendChild(img);
    }
    return container;
  } else if (field == 'Bug-number') {
    parts = value.split(' ')
    var container = document.createElement('a');
    container.href = parts[0];
    container.title = parts[0];
    container.appendChild(document.createTextNode(parts[1]));
    return container;
  } else {
    // Check if any plugins know how to handle this.
    var displays = Tiqit.pluginManager.call("getFieldDisplay", arguments);
    for (var i in displays) {
      if (displays[i] !== undefined) {
        return displays[i];
      }
    }

    // Otherwise just return a text node.
    return document.createTextNode(value);
  }
}

function getFieldEditor(parentValFn, field, name, defval, rel) {
  var vals = allFields[field].getValues(parentValFn, rel);
  return getEditorCommon(field, name, defval, vals, false, null, parentValFn);
}

function getSearchEditor(parentValFn, field, name, defval, rel) {
  var vals = allFields[field].getSearchValues(parentValFn);
  return getEditorCommon(field, name, defval, vals, true, rel, parentValFn);
}

/*
 * Returns an editor object. The form element will have a name and id
 * matching the name argument. It will be initialised to the given defval,
 * and if vals is non null will be a select with those values. The returned
 * object can have slightly different behaviour depending on the 'search'
 * argument.
 *
 * The returned object will have an 'input' field that is the actual input
 * object that values can be read from/set on, and can be disabled/enabled.
 */
dropdownEditTypes = new Array('Text', 'Number');
function getEditorCommon(field, name, defval, vals, search, rel, parentValFn) {
  var newVal;
  if (contains(dropdownEditTypes, allFields[field].ftype) && vals && vals.length > 0) {
    var opt;
    newVal = document.createElement('select');
    newVal.setAttribute('id', name);
    newVal.setAttribute('name', name);

    for (i in vals) {
        opt = document.createElement('option');
        opt.setAttribute('value', vals[i][0]);
        opt.appendChild(document.createTextNode(vals[i][1]));

        newVal.appendChild(opt);
    }
    if (defval) {
      newVal.value = defval;
    }

    newVal.input = newVal;

  } else if (contains(dateFields, allFields[field]) && rel != "withinlast") {
    var trigger, input;
    newVal = document.createElement('span');
    newVal.id = name;

    trigger = document.createElement('a');
    trigger.className = 'tiqitCalendarDropDown';
    newVal.appendChild(trigger);

    input = document.createElement('input');
    input.name = name;
    input.setAttribute('type', 'text');
    input.setAttribute('size', 15);
    if (defval) {
      input.value = defval;
    }
    newVal.appendChild(input);
    newVal.tiqitCalVal = input;

    var fmt = search ? 'dd/mm/yyyy' : 'mm/dd/yyyy';

    var cal = new TiqitCalendar(fmt);
    cal.attachPopup(input, trigger);

    newVal.input = input;

  } else if (contains(dateFields, allFields[field]) && rel == "withinlast") {
    var input;

    newVal = document.createElement('span');
    newVal.id = name;

    input = document.createElement('input');
    input.setAttribute('id', name);
    input.setAttribute('name', name);
    input.setAttribute('type', 'text');
    input.setAttribute('size', 3);

    newVal.appendChild(input);
    newVal.appendChild(document.createTextNode('days'));
    if (defval) {
      newVal.value = defval;
    }
    newVal.input = input;
  } else {
    field = allFields[field];
    newVal = document.createElement('span');
    newVal.className = 'tiqitIndicatorContainer';
    newVal.id = name;
    var input = document.createElement('input');
    newVal.input = input;
    input.setAttribute('name', name);
    input.setAttribute('type', 'text');
    input.setAttribute('size', field.displaylen);
    if (field.maxlen > 0 && !field.mvf) {
      input.setAttribute('maxlength', field.maxlen);
    }
    if (defval) {
      input.value = defval;
    }

    if (field.ftype == 'Userid') {
      var a = document.createElement('a');
      a.className = 'tiqitUserDropDown';
      a.onclick = showUserDropDown;
      var classes = newVal.className.split(' ');
      classes.push('tiqitUserEditable');
      newVal.className = classes.join(' ');
      newVal.appendChild(a);
    }

    if (!search && field.defaultsWith && field.defaultsWith.length > 0) {
      var a = document.createElement('a');
      newVal.className += ' tiqitDefaultLinkEditor';
      a.className = 'tiqitDefaultLink';
      a.href = 'defaultvals';
      function updateURL(event) {
          Tiqit.defaults.updateURL(newVal, parentValFn);
          return true;
      }
      input.addEventListener('change', updateURL, false);
      input.size -= 5;
      newVal.setAttribute("field", field.name);
      newVal.appendChild(a);
      newVal.a = a;
      updateURL();
    }

    newVal.appendChild(input);
  }

  return newVal;
}

//
// Event helpers
//

function fireEvent(evtType, source) {
  var ev = document.createEvent('HTMLEvents');
  ev.initEvent(evtType, true, true);
  source.dispatchEvent(ev);
}

