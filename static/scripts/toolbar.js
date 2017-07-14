//
// Toolbar editing behaviour
//

//
// Contents:
//
// tiqitToolbarEditStart
// tiqitToolbarEditStop
// tiqitToolbarItemDelete
// tiqitToolbarItemRevert
// tiqitToolbarSave
// tiqitToolbarRemove
//

//
// Convert the toolbar into editing mode
//

function tiqitToolbarEditStart(event) {
  // This function does the following:
  // - replaces the edit icon with a save icon
  // - adds a 'delete toolbar' icon
  // - adds a 'delete' icon next to each entry

  var toolbar = event.target.parentNode.parentNode;
  var items = toolbar.getElementsByTagName('a');
  var anims = new Array();
  var newItems = new Array();
  var del, edit, span;

  // Abort if we're mid-animation
  if (toolbar.animating) {
    return;
  }

  // Replace edit with save
  event.target.src = 'images/save-16x16.png';
  event.target.alt = '[Save]';
  event.target.tiqitOriginalTitle = event.target.title;
  event.target.title = 'Save changes';
  event.target.onclick = '';
  event.target.removeEventListener('click', tiqitToolbarEditStart, false);
  event.target.addEventListener('click', tiqitToolbarSave, false);
  toolbar.tiqitToolbarEditor = event.target;

  // Create a delete
  del = document.createElement('img');
  del.src = 'images/delete-small.png';
  del.alt = '[Delete]';
  del.title = 'Remove this toolbar completely';
  del.addEventListener('click', tiqitToolbarRemove, false);
  del.width = 0;
  del.height = 16;

  event.target.parentNode.insertBefore(del, event.target.nextSibling);
  toolbar.tiqitToolbarDeleter = del;
  anims.push(del);

  // For each item, create a deleter and an input box
  while (items.length > 0) {
    span = document.createElement('span');

    edit = document.createElement('input');
    edit.type = 'text';
    edit.tiqitValue = items[0].textContent;
    edit.value = edit.tiqitValue;
    edit.style.width = items[0].offsetWidth + 'px';
    edit.className = 'tiqitToolbarEditing';

    editHandler = function(event) {
      var icon = event.target.parentNode.tiqitToolbarDeleter;
      if (event.target.value != event.target.tiqitValue) {
        icon.src = 'images/undo-16x16.png';
        icon.alt = '[Undo]';
        icon.title = 'Undo changes';
        icon.removeEventListener('click', tiqitToolbarItemDelete, false);
        icon.addEventListener('click', tiqitToolbarItemRevert, false);
      } else {
        icon.src = 'images/error-small.png';
        icon.alt = '[X]';
        icon.title = 'Delete item';
        icon.removeEventListener('click', tiqitToolbarItemRevert, false);
        icon.addEventListener('click', tiqitToolbarItemDelete, false);
      }
    };
    edit.addEventListener('change', editHandler, false);
    edit.addEventListener('keyup', editHandler, false);

    del = document.createElement('img');
    del.src = 'images/error-small.png';
    del.alt = '[X]';
    del.title = 'Delete item';
    del.addEventListener('click', tiqitToolbarItemDelete, false);
    del.width = 0;
    del.height = 16;

    span.tiqitToolbarEditor = edit;
    span.tiqitToolbarDeleter = del;
    span.tiqitPrefValue = items[0].getAttribute('tiqitPrefValue');
    span.tiqitViewing = items[0].getAttribute('tiqitViewing');

    span.appendChild(edit);
    span.appendChild(del);

    items[0].parentNode.replaceChild(span, items[0]);
    anims.push(del);
    newItems.push(span);
  }

  toolbar.tiqitItems = newItems;

  // Animate them into view! :D
  var animator =  function() {
    for (var i = 0; i < anims.length; i++) {
      anims[i].width += 1;
    }
    if (anims[0].width < 16) {
      setTimeout(animator, 30);
    } else {
      toolbar.animating = false;
    }
  };
  setTimeout(animator, 30);
  toolbar.animating = true;
  toolbar.editing = true;
}

function tiqitToolbarEditStop(toolbar) {
  // Let's fade it out all nice like
  // - images go
  // - save returns to being edit
  // - items go back to being links

  var items = toolbar.tiqitItems;
  var prefix = toolbar.getAttribute('tiqitPrefPrefix');
  var urlprefix = toolbar.getAttribute('tiqitUrlPrefix');
  var icons = new Array(toolbar.tiqitToolbarDeleter);
  var dels = new Array();
  var saves = new Array();
  var saveType = toolbar.getAttribute('tiqitSaveType');
  var saver = document.getElementById("tiqitBar" + saveType + "Saver");

  // Replace save with edit
  toolbar.tiqitToolbarEditor.src = 'images/edit-small.png';
  toolbar.tiqitToolbarEditor.alt = '[Edit]';
  toolbar.tiqitToolbarEditor.title = toolbar.tiqitToolbarEditor.tiqitOriginalTitle;
  toolbar.tiqitToolbarEditor.removeEventListener('click', tiqitToolbarSave, false);
  toolbar.tiqitToolbarEditor.addEventListener('click', tiqitToolbarEditStart, false);

  for (var i = 0; i < items.length; i++) {
    if (!items[i].tiqitDeleting) {
      saves.push(items[i]);
    } else {
      var editor = items[i].tiqitToolbarEditor;
      dels.push(editor);
      editor.tiqitOriginalWidth = editor.offsetWidth;
    }
    icons.push(items[i].tiqitToolbarDeleter);
  }

  // Animate them out of view! :D
  var animator =  function() {
    for (var i = 0; i < icons.length; i++) {
      icons[i].width -= 1;
    }
    if (icons[0].width > 0) {
      setTimeout(animator, 30);
    } else {

      // Hide the separator.
      var sep;
      if (saves.length > 0) {
        sep = saves[0].parentNode.getElementsByClassName("tiqitBarSep")[0];
      } else {
        if (saver) {
            sep = saver.parentNode.getElementsByClassName("tiqitBarSep")[0];
        }

        // Also hide the intro string if nothing remains.
        toolbar.getElementsByClassName('tiqitBarIntroStr')[0].style.display = 'none';

        // If there is no saver then hide the entire toolbar.
        if (!saver) {
            toolbar.style.display = 'none';
        }
      }
      if (sep) {
          sep.style.display = 'none';
      }

      for (var i = 0; i < saves.length; i++) {
        var link = document.createElement('a');
        link.className = prefix;
        link.setAttribute('tiqitPrefValue', saves[i].tiqitPrefValue);
        link.setAttribute('tiqitViewing', saves[i].tiqitViewing);
        link.href = urlprefix + encodeURIComponent(saves[i].tiqitToolbarEditor.value);
        link.appendChild(document.createTextNode(saves[i].tiqitToolbarEditor.value));
        saves[i].parentNode.replaceChild(link, saves[i]);
      }
      for (var i = 0; i < dels.length; i++) {
        // If we've deleted the bug we're viewing, make the "Name this bug" box
        // appear.
        if (dels[i].parentNode.tiqitViewing == "1") {
            saver.parentNode.style.display = 'inline';
        }

        dels[i].parentNode.parentNode.parentNode.removeChild(dels[i].parentNode.parentNode);
      }
      toolbar.tiqitToolbarDeleter.parentNode.removeChild(toolbar.tiqitToolbarDeleter);
      toolbar.animating = false;
      toolbar.editing = false;
    }
  };
  setTimeout(animator, 30);
  toolbar.animating = true;
}

function tiqitToolbarSave(event) {
  // Build up a query to do the save
  // The save involves building a query with all the items in it

  var toolbar = event.target.parentNode.parentNode;
  var items = toolbar.tiqitItems;
  var query = new Array();
  var prefix = toolbar.getAttribute('tiqitPrefPrefix');
  var saveType = toolbar.getAttribute('tiqitSaveType');

  // Abort if we're mid-animation
  if (toolbar.animating) {
    return;
  }

  // Build a hash-table of names so we can check for duplicates.
  var valCounts = Object();
  for (var i = 0; i < items.length; i++) {
      if (!items[i].tiqitDeleting) {
        if (valCounts[items[i].tiqitToolbarEditor.value]) {
          valCounts[items[i].tiqitToolbarEditor.value]++;
        } else {
          valCounts[items[i].tiqitToolbarEditor.value] = 1;
        }
      }
  }

  var arg = 0
  for (var i = 0; i < items.length; i++) {
    var name = items[i].tiqitToolbarEditor.tiqitValue;
    if (items[i].tiqitDeleting) {
      query.push('key' + arg + '=' + prefix + encodeURIComponent(name));
      arg++;
    } else if (name != items[i].tiqitToolbarEditor.value) {
      if (valCounts[items[i].tiqitToolbarEditor.value] > 1) {
          alert("A " + saveType + " named " + items[i].tiqitToolbarEditor.value +
                  " already exists! Choose a different " +
                  "name or delete the other bug.");
          return;
      }
      if (!validateSavedValue(saveType, items[i].tiqitToolbarEditor.value, items[i].tiqitToolbarEditor)) {
        return;
      }
      query.push('key' + arg + '=' + prefix + encodeURIComponent(name));
      arg++;
      query.push('key' + arg + '=' + prefix + encodeURIComponent(items[i].tiqitToolbarEditor.value));
      query.push('val' + arg + '=' + encodeURIComponent(items[i].tiqitPrefValue));
      arg++;
    }
  }

  if (query.length == 0) {
    // Nothing to save. Just make the whole thing slide away
    tiqitToolbarEditStop(toolbar);
    return;
  }

  toolbar.tiqitToolbarEditor.src = 'images/saver.gif';
  toolbar.tiqitToolbarEditor.alt = '[Saving]';
  toolbar.tiqitToolbarEditor.title = 'Saving changes...';
  toolbar.tiqitToolbarEditor.removeEventListener('click', tiqitToolbarSave, false);

  var req = new XMLHttpRequest();
  req.open('GET', 'updateprefs.py?' + query.join('&'), true);

  req.onload = function(event) {
    if (event.target.status == 200) {
      tiqitToolbarEditStop(toolbar);
    } else {
      sendMessage(2, "Failed to save changes to toolbar. Received bad server response.");
      toolbar.tiqitToolbarEditor.src = 'images/save-16x16.png';
      toolbar.tiqitToolbarEditor.alt = '[Save]';
      toolbar.tiqitToolbarEditor.title = 'Save changes';
      toolbar.tiqitToolbarEditor.addEventListener('click', tiqitToolbarSave, false);
    }
  }
  req.onerror = function(event) {
    sendMessage(2, "Failed to save changes to toolbar. Likely this is due to a networking issue.");
    toolbar.tiqitToolbarEditor.src = 'images/save-16x16.png';
    toolbar.tiqitToolbarEditor.alt = '[Save]';
    toolbar.tiqitToolbarEditor.title = 'Save changes';
    toolbar.tiqitToolbarEditor.addEventListener('click', tiqitToolbarSave, false);
  }

  req.send(null);
}

function tiqitToolbarRemove(event) {
  var toolbar = event.target.parentNode.parentNode;

  if (!confirm("This will remove this toolbar from all " +
	       Tiqit.config['general']['sitename'] + " pages.\n\n" +
               "You can restore it by editing your Preferences.")) {
    return;
  }

  var prefName;
  if ('miscHide' + toolbar.id.substr(5) in Tiqit.prefs) {
    prefName = 'miscHide' + toolbar.id.substr(5) + '=on';
  } else {
    prefName = 'miscShow' + toolbar.id.substr(5) + '=false';
  }

  var query = 'updateprefs.py?' + prefName;

  var req = new XMLHttpRequest();
  req.open('GET', query, true);

  req.onload = function(event) {
    if (event.target.status == 200) {
      toolbar.parentNode.removeChild(toolbar);
    } else {
      sendMessage(2, "Failed to remove toolbar. Received bad server response.");
    }
  }
  req.onerror = function(event) {
    sendMessage(2, "Failed to remove toolbar. Likely this is due to a networking issue.");
  }

  req.send(null);
}

function tiqitToolbarItemDelete(event) {
  event.target.parentNode.style.textDecoration = 'line-through';
  event.target.src = 'images/undo-16x16.png';
  event.target.alt = '[Undo]';
  event.target.title = 'Undo changes';
  event.target.removeEventListener('click', tiqitToolbarItemDelete, false);
  event.target.addEventListener('click', tiqitToolbarItemRevert, false);
  event.target.parentNode.tiqitToolbarEditor.value = event.target.parentNode.tiqitToolbarEditor.tiqitValue;
  event.target.parentNode.tiqitToolbarEditor.disabled = true;
  event.target.parentNode.tiqitDeleting = true;

  event.preventDefault();
}

function tiqitToolbarItemRevert(event) {
  event.target.parentNode.style.textDecoration = 'inherit';
  event.target.src = 'images/error-small.png';
  event.target.alt = '[X]';
  event.target.title = 'Delete item';
  event.target.removeEventListener('click', tiqitToolbarItemRevert, false);
  event.target.addEventListener('click', tiqitToolbarItemDelete, false);
  event.target.parentNode.tiqitToolbarEditor.value = event.target.parentNode.tiqitToolbarEditor.tiqitValue;
  event.target.parentNode.tiqitToolbarEditor.disabled = false;
  event.target.parentNode.tiqitDeleting = false;

  event.preventDefault();
}
