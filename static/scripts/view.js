
//
// When creating bugs, need to handle attempts to change the project
//

function changeProject(select) {
  var search = document.location.search;
  if (search[0] == '?') {
    search = search.substring(1);
  }
  var args = search.split('&');
  var newArgs = new Array();
  for (var i = 0; i < args.length; i++) {
    var arg = args[i];
    if (arg && arg.indexOf('Project=') != 0) {
      newArgs.push(arg);
    }
  }
  newArgs.push('Project=' + select.value);

  document.location.assign(document.location.pathname + '?' + newArgs.join('&'));
}

function changeBugType(select) {
  if (document.location.search) {
    document.location.assign(document.baseURI + 'newbug/' + select.value + document.location.search);
  } else {
    document.location.assign(document.baseURI + 'newbug/' + select.value);
  }
}

//
// Setting up default values of selects
//

function initSelects() {
  var selects = document.getElementsByTagName('select');
  var opts;

  // Go through each <select>, and look for the first <option> with
  // defaultSelected = true, then save that as the defaultValue.
  //
  // This assumes single select only!
  for (var i = 0; i < selects.length; i++) {

    opts = selects[i].options;

    for (var j = 0; j < opts.length; j++) {

      if (opts[j].defaultSelected) {
	selects[i].defaultValue = opts[j].value;
	break;
      }
    }
  }
}

addCustomEventListener("FirstWindowLoad", initSelects);

//
// Initialise calendars for all the date fields
//

function calDropDownInit() {
  for (var field in dateFields) {
    var input = document.getElementById(dateFields[field].name);
    if (input) {
      var calendar = new TiqitCalendar('mm/dd/yyyy');
      calendar.attachPopup(input, input.previousSibling);
    }
  }
}

addCustomEventListener("FirstWindowLoad", calDropDownInit);

//
// Enclosure Handling
//

// The object currently being edited.
var amEditing = null;

var editMsg = "You have already changed another section of this bug.\nYou may only edit one section at a time.\n\nPlease save those changes, or undo them, then try again."

// Create a <select> with all the note types in it.
function makeNoteTypeSelect() {
  var opt;
  var newS = document.createElement('select');
  newS.setAttribute('name', 'noteType')

  for (i in noteTypes) {
    opt = document.createElement('option');
    opt.setAttribute('value', noteTypes[i]);
    opt.text = noteTypes[i];

    newS.appendChild(opt);
  }

  return newS;
}

function showEnclosure(row) {
  var table = row.parentNode.parentNode;
  table.rows[row.rowIndex + 1].style.display = 'table-row';

  var img = row.getElementsByTagName('img')[0];
  img.src = 'images/minus.gif';
  img.parentNode.setAttribute('onclick', 'hideEnclosure(this.parentNode);');
  img.alt = '[\u2212]';
  img.title = 'Hide Enclosure';
}

function hideEnclosure(row) {
  var table = row.parentNode.parentNode;
  table.rows[row.rowIndex + 1].style.display = 'none';

  var img = row.getElementsByTagName('img')[0];
  img.src = 'images/plus.gif';
  img.parentNode.setAttribute('onclick', 'showEnclosure(this.parentNode);');
  img.alt = '[+]';
  img.title = 'Show Enclosure';

  if (amEditing == row) {
    cancelEnclosureEdit(row.cells[6].getElementsByTagName('input')[0]);
  }
}

function editEnclosure(button) {
  if (amEditing) {
    alert(editMsg);
    return;
  }

  var row = button.parentNode.parentNode;
  var table = row.parentNode.parentNode;

  showEnclosure(row);

  // Text box
  var textBox = document.createElement('textarea');
  textBox.setAttribute('name', 'noteContent');
  textBox.setAttribute('rows', 20);

  var pre = table.rows[row.rowIndex + 1].cells[0].firstChild;

  textBox.appendChild(document.createTextNode(pre.textContent));

  pre.parentNode.appendChild(textBox);
  pre.style.display = 'none';

  // Type select
  var types = makeNoteTypeSelect();
  types.setAttribute('name', 'noteType');
  types.value = row.cells[1].textContent.substring(1, row.cells[1].textContent.lastIndexOf("'"));
  types.defaultValue = types.value;

  row.cells[1].replaceChild(types, row.cells[1].firstChild);

  // Note title
  // First save old one
  var oldTitle = document.createElement('input');
  oldTitle.setAttribute('name', 'noteTitle');
  oldTitle.setAttribute('type', 'hidden');
  oldTitle.setAttribute('value', row.cells[0].lastChild.textContent);
  row.cells[2].appendChild(oldTitle);

  var title = document.createElement('input');
  title.setAttribute('name', 'newNoteTitle');
  title.setAttribute('type', 'text');
  title.setAttribute('value', row.cells[0].lastChild.textContent.trim());
  title.setAttribute('size', 40);
  title.addEventListener('click', function(event) { event.stopPropagation(); }, true);
  row.cells[0].replaceChild(title, row.cells[0].lastChild);

  button.nextSibling.style.display = 'inline';
  button.nextSibling.nextSibling.style.display = 'inline';
  button.nextSibling.nextSibling.nextSibling.style.display = 'none';
  button.style.display = 'none';

  amEditing = row;
}

function cancelEnclosureEdit(button) {

  var row = button.parentNode.parentNode;
  var table = row.parentNode.parentNode;

  if (amEditing != row) {
    alert("How did you manage to cancel an edit you weren't performing?");
    return;
  }

  // Text box
  var pre = document.createElement('textarea');

  var pre = table.rows[row.rowIndex + 1].cells[0].firstChild;
  var textBox = table.rows[row.rowIndex + 1].cells[0].lastChild;

  textBox.parentNode.removeChild(textBox);
  pre.style.display = 'block';

  // Note Type
  row.cells[1].replaceChild(document.createTextNode("'" + row.cells[1].firstChild.defaultValue + "' Note"), row.cells[1].firstChild);

  // Note title
  row.cells[0].replaceChild(document.createTextNode(" " + row.cells[0].lastChild.defaultValue), row.cells[0].lastChild);

  row.cells[2].removeChild(row.cells[2].lastChild);

  button.nextSibling.style.display = 'none';
  button.nextSibling.nextSibling.style.display = 'none';
  button.nextSibling.nextSibling.nextSibling.style.display = 'inline';
  button.style.display = 'inline';

  amEditing = null;
}

function deleteEnclosure(button) {
  if (amEditing) {
    alert(editMsg);
    return;
  }

  var row = button.parentNode.parentNode;
  var table = row.parentNode.parentNode;

  // Note title
  var oldTitle = document.createElement('input');
  oldTitle.setAttribute('name', 'deleteTitle');
  oldTitle.setAttribute('type', 'hidden');
  oldTitle.setAttribute('value', row.cells[0].lastChild.textContent);
  row.cells[2].appendChild(oldTitle);

  amEditing = row;

  button.form.submit();
}

function renameAttachment(button) {
  if (amEditing) {
    alert(editMsg);
    return;
  }

  var row = button.parentNode.parentNode;
  var table = row.parentNode.parentNode;

  // Title
  // First save old one
  var oldTitle = document.createElement('input');
  oldTitle.setAttribute('name', 'fileTitle');
  oldTitle.setAttribute('type', 'hidden');
  oldTitle.setAttribute('value', row.cells[0].lastChild.textContent.trim());
  row.cells[2].appendChild(oldTitle);

  var title = document.createElement('input');
  title.setAttribute('name', 'newTitle');
  title.setAttribute('type', 'text');
  title.setAttribute('value', row.cells[0].lastChild.textContent.trim());
  title.setAttribute('size', 40);
  title.addEventListener('click', function(event) { event.stopPropagation(); }, true);
  row.cells[0].replaceChild(title, row.cells[0].lastChild);

  amEditing = row;

  button.style.display = 'none';
  button.nextSibling.style.display = 'inline';
  button.nextSibling.nextSibling.style.display = 'inline';
  button.nextSibling.nextSibling.nextSibling.style.display = 'none';
}

function saveAttachmentRename(button) {
  var row = button.parentNode.parentNode;

  var fileTitle = row.cells[2].lastChild.value;
  var newTitle = row.cells[0].lastChild.value;
  var bugid = document.getElementById('Identifier').value;

  document.location.assign('editfile.py?bugid=' + bugid + '&renameTitle=' + fileTitle + '&newTitle=' + newTitle);
}

function cancelAttachmentRename(button) {
  var row = button.parentNode.parentNode;

  var oldTitle = row.cells[2].lastChild;
  var fileTitle = oldTitle.value;
  oldTitle.parentNode.removeChild(oldTitle);

  row.cells[0].replaceChild(document.createTextNode(" " + fileTitle), row.cells[0].lastChild);

  button.previousSibling.previousSibling.style.display = 'inline';
  button.previousSibling.style.display = 'none';
  button.style.display = 'none';
  button.nextSibling.style.display = 'inline';

  amEditing = null;
}

function deleteAttachment(button) {
  if (amEditing) {
    alert(editMsg);
    return;
  }

  var row = button.parentNode.parentNode;
  var bugid = document.getElementById('Identifier').value;
  var fileTitle = row.cells[0].textContent.trim();

  document.location.assign('editfile.py?bugid=' + bugid + '&deleteTitle=' + escape(fileTitle));
}

function showAllEnclosures() {
  var table = document.getElementById('encTable');

  for (var i = 1; i < table.rows.length; i += 2) {
    // Only show enclosures that aren't suppressed by filters
    if (table.rows[i].style.display != 'none') {
      showEnclosure(table.rows[i]);
    }
  }
}

function hideAllEnclosures() {
  var table = document.getElementById('encTable');

  for (var i = 1; i < table.rows.length; i += 2) {
    hideEnclosure(table.rows[i]);
  }
}

//
// Special filtering handling for our double-row entries
//

function encTableFilter() {
  // We get the existing headers from the <th> elements.
  var resTable = document.getElementById('encTable');

  var headers = resTable.getElementsByTagName('th');
  var filters = new Array();
  var filterVal, show, cols;
  var showing = 0;

  for (var i = 0; i < headers.length; i++) {
    filterVal = document.getElementById('encTableFilter' + headers[i].textContent);

    if (filterVal) {
      filters[i] = filterVal.value;
    }
  }

  var theResults = resTable.rows;

  for (var i = 1; i < theResults.length; i += 2) {
    // For each row, check if it filters.
    show = true;
    cols = theResults[i].cells;

    for (var j = 0; j < cols.length; j++) {
      if (filters[j] != undefined && filters[j] != 'NOFILTER' &&
	  filters[j] != cols[j].textContent) {
	show = false;
	break;
      }
    }

    if (show) {
      theResults[i].style.display = 'table-row';
      showing++;
    } else {
      theResults[i].style.display = 'none';
      hideEnclosure(theResults[i]);
    }
  }

  return showing;
}

//
// Handler for loading attachments after initial page load is complete.
//

function loadAttachments() {
  var frames = document.getElementById('tiqitSectionContentsNotes').getElementsByTagName('iframe');

  for (var i = 0; i < frames.length; i++) {
    if (frames[i].hasAttribute('fileloc')) {
      frames[i].contentDocument.location.replace(frames[i].getAttribute('fileloc'));
    }
  }
}

// New Note/File functions

function showNewNote() {
  if (amEditing) {
    alert(editMsg);
    return false;
  }

  var newNote = document.getElementById("newnote");
  var theButton = document.getElementById("newencbuttons");

  newNote.style.display = "block";
  theButton.style.display = "none";

  amEditing = theButton;
}

function hideNewNote() {
  var newNote = document.getElementById("newnote");
  var theButton = document.getElementById("newencbuttons");

  if (theButton != amEditing) {
    alert("You're not editing a new Note!");
    return false;
  }

  newNote.style.display = "none";
  theButton.style.display = "inline";

  amEditing = null;
}

function showNewFile() {
  if (amEditing) {
    alert(editMsg);
    return false;
  }

  var newNote = document.getElementById("newfile");
  var theButton = document.getElementById("newencbuttons");

  newNote.style.display = "block";
  theButton.style.display = "none";

  amEditing = theButton;
}

function hideNewFile() {
  var newNote = document.getElementById("newfile");
  var theButton = document.getElementById("newencbuttons");

  if (theButton != amEditing) {
    alert("You're not editing a new File!");
    return false;
  }

  newNote.style.display = "none";
  theButton.style.display = "inline";

  amEditing = null;
}

function initNoteTitleChange() {
  var theSelect = document.getElementById('newnotetype');
  
  if (theSelect && !theSelect.oldValue) {
    theSelect.oldValue = theSelect.value;
  }
}

addCustomEventListener("FirstWindowLoad", initNoteTitleChange);

function newNoteTitle(theSelect) {
  var theT = document.getElementById('newnotetitle');
  var templ = document.getElementById('newnotecontent');

  if (!theT.value ||
      (theSelect.oldValue && theSelect.oldValue == theT.value)) {
    theT.value = theSelect.value;
  }

  if (!templ.value || templ.value == noteTemplates[theSelect.oldValue]) {
    if (noteTemplates[theSelect.value]) {
      templ.value = noteTemplates[theSelect.value];
    } else {
      templ.value = '';
    }
  }

  theSelect.oldValue = theSelect.value;
}

//
// Validity checker
//

// Fields not required when 'not-a-bug'
notbugFields = new Array('Triggers', 'Reason', 'Origin', 'Category',
			 'Dev-escape-activity-display');

function checkS1S2Downgrade() {
  var sev = document.getElementById('Severity');

  if (sev.defaultValue <= 2 && sev.value >= 3) {
    var S1S2 = document.getElementById('S1S2-without-workaround');

    if (!S1S2) {
      S1S2 = document.createElement('input');
      S1S2.setAttribute('type', 'hidden');
      S1S2.setAttribute('id', 'S1S2-without-workaround');
      S1S2.setAttribute('name', 'S1S2-without-workaround');

      document.getElementById('tiqitBugEdit').appendChild(S1S2);
    }

    S1S2.value = confirm("If you are downgrading the Severity because there\n" +
                         "is now a workaround for this S1/S2 Bug, press OK.");
  }
}


function getFieldValueView(field) {
    var editor;

    editor = document.getElementById(field);
    if (editor) {
        return editor.input ? editor.input.value : editor.value;
    }
}

function resetForm() {
    // Want to reset both initial form and extras form.
    document.getElementById("tiqitBugEdit").reset();
    document.getElementById("tiqitExtraFormData").reset();

    // Also clear the indicator on the Component name if it has been set - 
    // not being reset in checkFormValidity().
    element = document.getElementById("Component");
    Tiqit.clearIndicator(element);

    checkChildren();
    checkFormValidity();
}

function checkChildren() {
    var ev = new Object();

    for (field in allFields) {
        ev.currentTarget = allFields[field];
        ev.target = allFields[field];
        updateChildrenView(ev);
    }
}


function updateChildrenView(event) {
    var ev = new Object();
    var field = allFields[event.target.name];
    var child;
    var old_editor;
    var editor;
    var value;
    var parent;

    for (child in field.childfields) {
        // Generate a new dropdown box with the correct allowed values based
        // on the new value of the field:

        // Get the old dropdown off the page
        old_editor = document.getElementById(field.childfields[child]);
        if (old_editor && old_editor.type != 'hidden') {
            value = old_editor.value;

            // Call getFieldEditor to generate the new dropdown
            editor = getFieldEditor(getFieldValueView, field.childfields[child], field.childfields[child], value);
            // On page load, the editor doesn't have an 'input', and instead
            // the input has the ID. Detect this, and remove the parent.
            if (editor.input != editor && // The editor is more than just input
                !old_editor.input) { // The old editor is from page load
                old_editor.parentNode.input = old_editor;
                old_editor = old_editor.parentNode;
            } else if (!old_editor.input) {
                old_editor.input = old_editor;
            }

            // Go back to the default value if we are not a checkbox
            if (!(field.childfields[child].nodeName == 'INPUT' && field.childfields[child].type == 'checkbox')) {
                editor.input.value = old_editor.input.defaultValue;
            }
           
            // Add the event listener(s) updateChildrenView and checkFormValidity
            // to the dropdown
            editor.input.addEventListener('change', updateChildrenView, false);
            editor.input.addEventListener('change', checkFormValidity, false);
            if (field.childfields[child] == "Severity") {
                editor.input.addEventListener('change', checkS1S2Downgrade, false);
            }
            if (field.childfields[child].nodeName == 'INPUT' && field.childfields[child].type == 'checkbox') {
                editor.input.defaultChecked = old_editor.input.defaultChecked;
            } else {
                editor.input.defaultValue = old_editor.input.defaultValue;
            }
           
            parent = old_editor.parentNode;
            parent.removeChild(old_editor);
            parent.appendChild(editor);
           
            // If the new selected value in the dropdown is different from the 
            // old one then update this fields children recursively (i.e.
            // the grandchildren of the current field
            if (editor.value != value) {
                ev.currentTarget = allFields[field.childfields[child]];
                ev.target = ev.currentTarget;
                updateChildrenView(ev);
            }
        }
    }
}

function checkFieldValue(editor) {
  var field = allFields[editor.id];
  var input = editor.input ? editor.input : editor;
  var value = input.value;
  var values;
  if (field.values && field.values.length > 0) {
    values = field.values;
  } else if (field.parentfields && field.parentfields.length > 0) {
    var keys = [];
    for (var key in field.parentfields) {
      keys.push(document.getElementById(field.parentfields[key]).value);
    }
    values = new Array();
    for (var val in field.perparentvalues[keys]) {
      values.push(field.perparentvalues[keys][val][0]);
    }
  }
  if (values && value.length > 0 && !contains(values, value)) {
    Tiqit.indicateUnknown(input);
  } else {
    Tiqit.clearIndicator(input);
  }
}

function checkFormValidity(event) {
  // First things first: check if the changed field triggers any defaults
  var field = allFields[event ? event.target ? event.target.id : null : null];
  if (field && field.reverseDefaultsWith && field.reverseDefaultsWith.length > 0) {
    // Pass around a set of already updated field names, to make sure a field
    // is not written twice in a chain of default value lookups.
    //
    // Bug: Behaviour here is timing dependent in some scenarios. E.g. If A
    // has defaults for B and C, and B and C have defaults for D. If A is
    // changed the ultimate value of D will depend on whether the defaults
    // lookup for B is faster than the defaults lookup for C.
    if (event.updatedFields === undefined) {
      // This is a direct change by the user. Create a new set.
      event.updatedFields = new Object();
    }
    event.updatedFields[field.name] = true;

    for (var i = 0; i < field.reverseDefaultsWith.length; i++) {
      var defaultsField = allFields[field.reverseDefaultsWith[i]];
      Tiqit.defaults.fetchDefaults(defaultsField, function(defaults, input) {
        for (var i = 0; i < defaults.length; i++) {
          var update = defaults[i];
          var editor = document.getElementById(update.getAttribute('name'));
          if (editor) {
            var input = editor.input ? editor.input : editor;
            if (input.value != update.textContent &&
                !event.updatedFields[update.getAttribute('name')]) {
              input.value = update.textContent;
              var ev = document.createEvent('HTMLEvents');
              ev.initEvent('change', true, true);
              ev.updatedFields = event.updatedFields;
              input.dispatchEvent(ev);
            }
          }
        }

        if (defaults.length == 0) {
          // Likely means the field value is unknown
          Tiqit.indicateUnknown(input);
        }
      });
    }
  }

  var form = document.getElementById('tiqitBugEdit');
  var f, l;
  var bannedif_field;
  var mandatoryif_field;
  var found_field;
  var value;
  var disabled = false;
  var mandatory = false;
  var valid = true;
  var editing = false;

  for (var field in allFields) {
    f = document.getElementById(field);
    l = document.getElementById(field + 'Label');

    if (!f || !l) continue;

    // If field is a user field, it might still be possible to check validity
    if (allFields[field].ftype == 'Userid') {
      checkFieldValue(f);
    }

    // The rest of this function wants the actual input, not the editor
    if (f.input) {
      f = f.input;
    }

    // First determine if the field should be disabled - if any of the
    // "banned if" fields have a value, then check its not in the list
    // of values associated 
    disabled = false;
    for (bannedif_field in allFields[field].bannedif) {
      found_field = document.getElementById(bannedif_field);
      if (found_field) {
        value = found_field.value;
        if (contains(allFields[field].bannedif[bannedif_field], value)) {
          disabled = 'disabled';
          break;
        }
      }
    }
    f.disabled = disabled;

    // Now select the right colour for the label.
    if (!f.disabled) {
      var def, curr;
      // Checkboxes are valued by their checked state, not their 'value'
      if (f.nodeName == 'INPUT' && f.type == 'checkbox') {
        def = f.defaultChecked;
        curr = f.checked;
      } else {
        def = f.defaultValue;
        curr = f.value;
      }

      // A field is mandatory if all of the requirements are met
      // If there are no requirements, then it is never mandatory, otherwise
      // its mandatory unless one of the requirements are not met
      if (Tiqit.objectHasKeys(allFields[field].mandatoryif)) {
        mandatory = true;
        for (mandatoryif_field in allFields[field].mandatoryif) {
          found_field = document.getElementById(mandatoryif_field);
          if (found_field) {
            value = found_field.value;
            if (!contains(allFields[field].mandatoryif[mandatoryif_field], value)) {
              mandatory = false;
            }
          }
        }
      } else {
        mandatory = false;
      }
      // If the field is required by this state, or by the 'N' state, then
      // mark it in red. Unless it's a checkbox. Checkboxes can't be red.
      if (mandatory && !f.value) {
        l.style.color = 'red';
        valid = false;
      } else if (def != curr) {
        editing = true;
        if (amEditing && amEditing != form) {
          if (f.nodeName == 'INPUT' && f.type == 'checkbox') {
            f.checked = f.defaultChecked;
          } else {
            f.value = f.defaultValue;
          }
        } else if (document.location.href.indexOf('new.py') == -1) {
          l.style.color = 'blue';
        } else {
          l.style.color = 'black';
        }
      } else {
        l.style.color = 'black';
      }
    } else {
      l.style.color = 'black';
    }
  }

  if (editing) {
    if (amEditing && amEditing != form) {
      alert(editMsg);
      return false;
    } else {
      amEditing = form;
    }
  } else if (amEditing == form) {
    amEditing = null;
  }

  return valid;
}


var isWaitingOnAsyncCall = false;
var hasShownSubmissionMessage = false;
var isSubmittingChanges = false;

function checkBugChange(bugid, lastMod, inMsg) {
  var tiqitApi = new TiqitApi();
  var msg = inMsg;

  function submitChanges(msg) {
    // Perform the bug submission letting the user confirm a prompt if
    // submission may not be smooth (msg != "")
    // Also reset flags regarding waiting on an async call (checking history) and if 
    // a submission message has been shown.
    var doSubmit = true;
    if (msg != "") {
      msg += "\nClick OK to submit new changes despite the above warnings.";
      msg += "\nOtherwise, press cancel and hit refresh to update your bug view.";
      doSubmit = confirm(msg);
    }

    if (doSubmit) {
      isSubmittingChanges = true;
      document.getElementById("tiqitBugEdit").submit();
    }

    isWaitingOnAsyncCall = false;
    hasShownSubmissionMessage = false;
  }

  // Prepare the async event functions
  function bugChangeOnLoad(eventLoad) {
    if (eventLoad.target.status == 200 && eventLoad.target.responseXML) {
      // Check if the first date predates lastMod and only Note or Attachment
      // related changes were made.
      // If not, we may have overwriteable changes. (See hasHistoryOverwriteableChanges).
      // If this is the case, check with the user if bug changes should be submitted.
      var history = historyDataFromXML(eventLoad.target.responseXML);
      var lastModHistoryDate = new Date(history[0]['Date']);
      var lastModDate = new Date(lastMod);
      var hasHistoryOverwriteableChanges = false;
      var historyItem;
      var historyItemDate;

      // Checking for legitimate changes here
      if (lastModHistoryDate > lastModDate) {
        for (i in history) {
          historyItem = history[i];
          historyItemDate = new Date(historyItem['Date']);
          if (historyItem['Field'] != "File Name" &&
              historyItem['Field'] != "Note Title" &&
              historyItemDate > lastModDate) {
                hasHistoryOverwriteableChanges = true;
                break;
          }
        }
      }

      // Inform the user of changes that will be overwritten.
      if (hasHistoryOverwriteableChanges) {
        msg += "Your bug view is from " + lastModDate.toLocaleString();
        msg += ", and the bug now contains changes from " + lastModHistoryDate.toLocaleString() + ".\n\n";
        msg += "The following set of changes to this bug will likely be overwritten:\n\n";
        for (i in history) {
          historyItem = history[i];
          historyItemDate = new Date(historyItem['Date']);
          if (historyItem['Field'] == "File Name" ||
              historyItem['Field'] == "Note Title") {
                // Do not tell the user that their note or attachment
                // may be overwritten. It won't be!
                continue;
          }
          if (historyItemDate > lastModDate) {
            if (historyItem['Operation'] == 'Delete') {
              msg += "    Deleted '" + historyItem['Field'] + "', which was set to '" + historyItem['OldValue'] + "'\n";
            } else if (historyItem['Operation'] == 'New Record') {
              if (historyItem['NewValue'] == "") {
                msg += "    Created " + historyItem['Field'] + "\n";
              } else {
                msg += "    Created '" + historyItem['Field'] + "' as '" + historyItem['NewValue'] + "'\n";
              }
            } else if (historyItem['Operation'] == 'Modify') {
              if (historyItem['OldValue'] == "" && historyItem['NewValue'] == "") {
                msg += "    Modified '" + historyItem['Field'] + "'\n";
              } else if (historyItem['OldValue'] == "") {
                msg += "    Set '" + historyItem['Field'] + "' as '" + historyItem['NewValue'] + "'\n";
              } else {
                msg += "    Set '" + historyItem['Field'] + "' from '" + historyItem['OldValue'] + "' to '" + historyItem['NewValue'] + "'\n";
              }
            } else {
              msg += "    Performed '" + historyItem['Operation'] + "'\n";
            }
          }
        }
      }
    } else {
      // Failed to get the bug history.
      // Let user still attempt submission.
      msg += "Unable to retrieve bug history.\n";
      msg += "Cannot confirm if past changes will be overwritten.\n";
    }

    submitChanges(msg);
  }

  function bugChangeError(eventErr) {
    msg += "Unable to retrieve bug history.\n";
    msg += "Cannot confirm if past changes will be overwritten.\n";

    msg += "\n\nClick OK to overwrite previous modifications and submit new changes.";
    msg += "\nOtherwise, press cancel and hit refresh to load previous modifications.";

    submitChanges(msg);
  }

  function bugChangeTimeout(eventErr) {
    msg += "Bug history fetch has timed out.\n";
    msg += "Cannot confirm if past changes will be overwritten.\n";

    msg += "\n\nClick OK to overwrite previous modifications and submit new changes.";
    msg += "\nOtherwise, press cancel and hit refresh to load previous modifications.";

    submitChanges(msg);
  }

  if (!isWaitingOnAsyncCall && !isSubmittingChanges) {
    isWaitingOnAsyncCall = true;
    // Generously wait 25s for bug history to arrive.
    tiqitApi.historyForBugs([bugid], bugChangeOnLoad, bugChangeError,
                            25000, bugChangeTimeout);
  } else if (!hasShownSubmissionMessage) {
    sendMessage(1, "Bug submission in progress, please wait.");
    hasShownSubmissionMessage = true;
  }
}

//
// Submitting Support
//

function prepareForm(bugid, lastMod) {
  var form = document.getElementById('tiqitBugEdit');
  var extra = document.getElementById('tiqitExtraFormData');

  var inputs = extra.getElementsByTagName('input');
  var selects = extra.getElementsByTagName('select');

  var extraDiv = document.getElementById('extraCopies');
  var msg = "";

  while (extraDiv.childNodes.length) {
    extraDiv.removeChild(extraDiv.childNodes[0]);
  }

  for (var i = 0; i < inputs.length; i++) {
    if (inputs[i].name && ((inputs[i].type != 'checkbox' && inputs[i].value) || inputs[i].checked) && !inputs[i].disabled) {
      var hidden = document.createElement('input');
      hidden.type = 'hidden';
      hidden.name = inputs[i].name;
      hidden.value = inputs[i].value;
      extraDiv.appendChild(hidden);
    }
  }

  for (var i = 0; i < selects.length; i++) {
    if (selects[i].name && selects[i].value && !selects[i].disabled) {
      var hidden = document.createElement('input');
      hidden.type = 'hidden';
      hidden.name = selects[i].name;
      hidden.value = selects[i].value;
      extraDiv.appendChild(hidden);
    }
  }

  var oldRelates = new Array();
  var newRelates = document.getElementById('tiqitNewRelates');

  var relatesTable = document.getElementById('tiqitRelatesTable');

  if (relatesTable) {
    for (row = 0; row < relatesTable.rows.length; row++) {
      // Related bugs with disabled check boxes are those that aren't tracked
      // by the backend, so don't submit them.
      if (!relatesTable.rows[row].cells[0].firstChild.disabled &&
          !relatesTable.rows[row].cells[0].firstChild.checked) {
        oldRelates.push(relatesTable.rows[row].cells[1].textContent);
      }
    }
  }

  if (newRelates) {
    var hidden = document.createElement('input');
    hidden.type = 'hidden';
    hidden.name = 'newRelates';
    hidden.value = oldRelates.join(',') + ',' + newRelates.value;
    extraDiv.appendChild(hidden);
  }

  // Determine what message to return to the caller
  if (!checkFormValidity()) {
    msg = "There is potential missing info in the bug. Please see fields highlighted in red.\n\n";
  }

  checkBugChange(bugid, lastMod, msg);
}

//
// Update the default file name when a file is entered
//
var default_being_used = true;

function updateFileName() {
  var encTitle = document.getElementById("fileTitle");
  var fileInput = document.getElementById("theFile");

  var fileName = fileInput.files.item(0).name.split('.', 1)[0];

  //window.alert(fileName);

  if (encTitle.value == "" || default_being_used) {
      encTitle.value = fileName;
      default_being_used = true;
  }
}

function unsetDefault() {
    default_being_used = false;
}
