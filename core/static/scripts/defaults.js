

Tiqit.defaults = (function() {
  var step2, step3, step4;
  function selectField(event) {
    if (step3) {
      step3.style.display = 'none';
    }
    if (step4) {
      step4.style.display = 'none';
    }
    if (!event.target.value) {
      if (step2) {
        step2.style.display = 'none';
      }
      return;
    }
    var field = allFields[event.target.value];

    if (!field || !field.defaultsWith || field.defaultsWith.length == 0) {
      sendMessage(1, event.target.value + " is not a field that triggers defaults. How did you even select it? :-/");
      return;
    }

    if (!step2) {
      var div = document.createElement('div');
      var h3 = document.createElement('h3');
      var span = document.createElement('span');
      var tab = document.createElement('table');

      step2 = div;
      span.appendChild(document.createTextNode('Step 2:'));
      span.style.color = 'darkred';
      span.style.fontSize = '150%';
      h3.appendChild(span);
      h3.appendChild(document.createTextNode(' Choose Values'));
      div.appendChild(h3);

      var p = document.createElement('p');
      var em = document.createElement('em');
      em.appendChild(document.createTextNode("Select the value(s) for which to view/set the defaults."));
      p.appendChild(em);
      div.appendChild(p);

      div.appendChild(tab);
      div.tiqitFieldTable = tab;

      document.getElementById('tiqitDefaultVals').appendChild(div);

      p = document.createElement('p');
      var submit = document.createElement('input');
      submit.type = 'button';
      submit.value = 'Get Defaults';
      submit.addEventListener('click', getDefaults, false);
      p.appendChild(submit);
      step2.appendChild(p);
    } else {
      while (step2.tiqitFieldTable.rows.length > 0) {
        step2.tiqitFieldTable.deleteRow(-1);
      }
    }
    step2.style.display = 'block';

    // Whenever a value is changed regenerate all editors with parent
    // dependencies whose values have changed.
    function getParentVal(f) {
      var ed = document.getElementById(f);
      return ed.input ? ed.input.value : ed.value;
    }

    function regenerateEditors(event) {
      for (var i = 0; i < field.defaultsWith.length; i++) {
        var parent = allFields[field.defaultsWith[i]];
        var editor = document.getElementById(parent.name);
         
        if (!parent.checkInputOptions(getParentVal, editor.input)) {
          editor.parentNode.replaceChild(makeEditor(parent), editor);
        }
      }
    }

    function makeEditor(f) {
      editor = getFieldEditor(getParentVal, f.name, f.name, Tiqit.prefs['miscDefault' + f.name]);
      editor.addEventListener("change", regenerateEditors, false);
      return editor;
    }

    // Now for each field in the defaultsWith array, add a row
    for (var i = 0; i < field.defaultsWith.length; i++) {
      var parent = allFields[field.defaultsWith[i]];
      var row = step2.tiqitFieldTable.insertRow(-1);

      var label = document.createElement('label');
      label.appendChild(document.createTextNode(parent.name + ':'));
      var cell = row.insertCell(-1);
      cell.appendChild(label);

      cell = row.insertCell(-1);

      cell.appendChild(makeEditor(parent));
    }
  }
  function getDefaults(event) {
    var field = document.getElementById('tiqitDefaultField').value;
    if (!field) {
      return;
    }
    field = allFields[field];
    var keys = [];
    for (var i = 0; i < field.defaultsWith.length; i++) {
      keys.push(document.getElementById(field.defaultsWith[i]).value);
    }
    if (!step3) {
      var div = document.createElement('div');
      var h3 = document.createElement('h3');
      var span = document.createElement('span');
      var tab = document.createElement('table');
      var hidden = document.createElement('input');

      step3 = div;
      span.appendChild(document.createTextNode('Step 3:'));
      span.style.color = 'darkred';
      span.style.fontSize = '150%';
      h3.appendChild(span);
      h3.appendChild(document.createTextNode(' Set Default Values'));
      div.appendChild(h3);

      var p = document.createElement('p');
      var em = document.createElement('em');
      em.appendChild(document.createTextNode("Edit the default values triggered by the above fields."));
      p.appendChild(em);
      div.appendChild(p);

      hidden.type = 'hidden';
      hidden.name = 'defaultFields';
      hidden.id = 'tiqitDefaultFields';
      div.appendChild(hidden);

      div.appendChild(tab);
      div.tiqitFieldTable = tab;

      p = document.createElement('p');
      var submit = document.createElement('input');
      submit.type = 'submit';
      submit.value = 'Save Defaults';
      p.appendChild(submit);
      div.appendChild(p);

      document.getElementById('tiqitDefaultVals').appendChild(div);
    } else {
      while (step3.tiqitFieldTable.rows.length > 0) {
        step3.tiqitFieldTable.deleteRow(-1);
      }
    }
    step3.style.display = 'none';

    if (!step4) {
      var div = document.createElement('div');
      var h3 = document.createElement('h3');
      var span = document.createElement('span');
      var tab = document.createElement('dl');

      step4 = div;
      span.appendChild(document.createTextNode('Step 4:'));
      span.style.color = 'darkred';
      span.style.fontSize = '150%';
      h3.appendChild(span);
      h3.appendChild(document.createTextNode(' Review Reverse Mappings'));
      div.appendChild(h3);

      var p = document.createElement('p');
      var em = document.createElement('em');
      em.appendChild(document.createTextNode("The following fields/values lead to the target field being defaulted to the current value."));
      p.appendChild(em);
      div.appendChild(p);

      div.appendChild(tab);
      div.tiqitFieldTable = tab;

      document.getElementById('tiqitDefaultVals').appendChild(div);
    } else {
      while (step4.tiqitFieldTable.hasChildNodes()) {
        step4.tiqitFieldTable.removeChild(step4.tiqitFieldTable.firstChild);
      }
    }
    step4.style.display = 'none';

    fetchDefaults(field, function(defaults, input) {
      step3.style.display = 'block';
      var existing = new Object();
      for (var i = 0; i < defaults.length; i++) {
        var update = defaults[i];
        existing[update.getAttribute('name')] = update.textContent;
      }
      
      var defs = [];
      for (var i = 0; i < field.defaultsFor.length; i++) {
        var name = field.defaultsFor[i];
        var row = step3.tiqitFieldTable.insertRow(-1);
        var cell = row.insertCell(-1);
        var label = document.createElement('label');
        label.appendChild(document.createTextNode(name + ':'));
        cell.appendChild(label);

        cell = row.insertCell(-1);
        var editor = getFieldEditor(function(f) {
          var field = document.getElementById(f);
          return field ? field.input ? field.input.value : field.value : null;
        }, name, name, existing[name]);
        cell.appendChild(editor);

        defs.push(name);
      }

      document.getElementById('tiqitDefaultFields').value = defs.join(',');
    }, function(revs) {
      if (revs.length > 0) {
        step4.style.display = 'block';
        for (var i = 0; i < revs.length; i++) {
          var field = revs[i].getAttribute('name');
          var di = document.createElement("di");
          var dt = document.createElement("dt");
          dt.appendChild(document.createTextNode(field));
          di.appendChild(dt);
          var entries = revs[i].getElementsByTagName('entry');
          for (var j = 0; j < entries.length; j++) {
            var dd = document.createElement('dd');
            var a = document.createElement('a');
            a.className = 'tiqitDefaultLink';
            var href = 'defaultvals?tiqitDefaultField=' + encodeURI(field);
            var vals = [];
            var fields = entries[j].getElementsByTagName('field');
            for (var k = 0; k < fields.length; k++) {
              var name = fields[k].getAttribute('name');
              vals.push(name + ": " + fields[k].textContent);
              href += '&' + encodeURI(name) + '=' + encodeURI(fields[k].textContent);
            }
            a.href = href;
            dd.appendChild(a);
            dd.appendChild(document.createTextNode(vals.join(", ")));
            di.appendChild(dd);
          }
          step4.tiqitFieldTable.appendChild(di);
        }
      }
    });
  }
  function checkForArgs() {
    var args = parseQueryString(document.location.search);
    if (args['tiqitDefaultField']) {
      var input = document.getElementById('tiqitDefaultField');
      input.value = args['tiqitDefaultField'];

      var ev = new Object();
      ev.target = input;
      selectField(ev);

      var field = allFields[input.value];
      var gotAll = true;
      for (var i = 0; i < field.defaultsWith.length; i++) {
        var w = field.defaultsWith[i];
        var editor = document.getElementById(w);
        if (args[w]) {
          editor.input.value = args[w];
          fireEvent('change', editor.input);
        } else {
          gotAll = false;
        }
      }

      if (gotAll) {
        getDefaults();
      }
    }
  }
  function fetchDefaults(field, handler, revhandler) {
    // Fetch the values for each of the dependent fields
    args = ['field=' + encodeURI(field.name)];

    for (var other in field.defaultsWith) {
      other = field.defaultsWith[other];
      var input = document.getElementById(other);
      input = input.input ? input.input : input;
      if (input && input.value) {
        args.push(encodeURI(other) + '=' + encodeURI(input.value));
      } else {
        return;
      }
    }

    var editor = document.getElementById(field.name);
    var input = editor.input ? editor.input : editor;
    Tiqit.indicateLoading(input);

    var url = 'fetchDefaults?' + args.join('&')
    var req = new XMLHttpRequest();
    //currentRequest.onprogress = onProgress;
    req.open("GET", url, true);
    req.onload = function(event) {
      Tiqit.clearIndicator(input);
      if (event.target.status == 200 && event.target.responseXML) {
        var def = event.target.responseXML.getElementsByTagName('defaults');
        var rev = event.target.responseXML.getElementsByTagName('reversedefaults');
        var defaults = def.length > 0 ? def[0].getElementsByTagName('field') : [];
        var revs = rev.length > 0 ? rev[0].getElementsByTagName('defaultfrom') : [];
        Tiqit.handleXMLMessages(event.target.responseXML);

        handler(defaults, input);
        if (revhandler) {
          revhandler(revs);
        }
      } else {
        sendMessage(2, "Failed to load defaults for field " + field.name + ". Error " + event.target.status + ".");
      }
    };
    req.onerror = function(event) {
      Tiqit.clearIndicator(input);
      sendMessage(2, "Failed to fetch defaults for field " + field.name + " due to networking error.");
    };
    req.send(null);
  }
  
  function updateURL(editor, parentValFn) {
    var name;
    var url = Tiqit.config['general']['metaurl'] + 'defaultvals';

    if (typeof(editor) == 'string') {
      name = editor;
      editor = document.getElementById(name).parentNode;
    } else {
      name = editor.getAttribute("field");
    }

    var field = allFields[name];
    var input = editor.input ? editor.input : editor.getElementsByClassName("tiqitDefaultLinkInput")[0];
    var value = input.value;
    var a = editor.a ? editor.a : editor.getElementsByClassName("tiqitDefaultLink")[0];
    if (!value) {
        a.href = url;
        return;
    }
    var args = '?tiqitDefaultField=' + encodeURI(name) + '&' + encodeURI(name) + '=' + encodeURI(value);

    for (var i = 0; i < field.defaultsWith.length; i++) {
      var parentVal = parentValFn(field.defaultsWith[i]);
      if (parentVal) {
        args += '&' + encodeURI(field.defaultsWith[i]) + '=' + encodeURI(parentVal);
      }
    }

    url += args;
    a.href = url;
  }
  function initURLs(parentValFn) {
      var inputs = document.getElementsByClassName('tiqitDefaultLinkEditor');

      for (var i = 0; i < inputs.length; i++) {
          updateURL(inputs[i], parentValFn);
      }
  }
  addCustomEventListener("FirstWindowLoad", checkForArgs);
  return {
    selectField: selectField,
    fetchDefaults: fetchDefaults,
    updateURL: updateURL,
    initURLs: initURLs,
  }
})();
