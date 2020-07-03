
// Encapsulate the whole of this file in its own namespace
Tiqit.search = (function() {

function bracketRightShift(theButton) {
  // These buttons don't have ids, so use onclick to identify them instead.
  if (!theButton || !theButton.onclick) {
    theButton = this;
  }
  // We get the openBracket we want to shift right. Get the close bracket too.
  var num, level;
  var openBracket = theButton.parentNode;

  var vals = openBracket.id.slice(11).split('.');
  num = parseInt(vals[0]);
  level = parseInt(vals[1]);

  var closeBracket = document.getElementById('closeBracket' + (num - 1) + '.' + level);

  // We remove both the open and the close bracket here. If there is a
  // further indented close bracket, move any potential Op to there,
  // and ditto for open and the shifters.
  var oneUp = document.getElementById('closeBracket' + (num - 1) + '.' + (level + 1));
  if (oneUp) {
    oneUp.appendChild(closeBracket.getElementsByTagName('span')[0]);
  } else {
    document.getElementById('row' + (num - 1)).appendChild(closeBracket.getElementsByTagName('span')[0]);
  }

  document.getElementById('opLevel' + (num - 1)).value = level;

  // Only actually move the shifters if there is also a new close at the right
  // level above.
  var oneDown = document.getElementById('openBracket' + num + '.' + (level + 1));
  var closeUp = document.getElementById('closeBracket' + (num - 1) + '.' + (level + 1));

  if (oneDown && closeUp) {
    var elems = openBracket.getElementsByTagName('input');
    while (elems[0]) {
      oneDown.appendChild(elems[0]);
    }
  }

  openBracket.parentNode.removeChild(openBracket);
  closeBracket.parentNode.removeChild(closeBracket);
}

function bracketLeftShift(openBracket) {
  alert('Left Shifting brackets not supported. (row ' + openBracket.id + ')');
}

function shiftRight(theButton) {
    if (!theButton || !theButton.id) {
        theButton = this;
    }
    var num = parseInt(theButton.id.slice(12));

    if (num < 1) {
        alert("Stop trying to move non-existent rows! (" + num + ")");
        return false;
    }

    // Shift the given row right by 1.
    var theP = document.getElementById('row' + num);
    var theLevel = document.getElementById('level' + num);

    theLevel.value++;

    theP.style.paddingLeft = (theLevel.value * 25) + 'px';

    // Also need to add appropriate brackets. In this case, that's an open just
    // before the row in question, and a close after it (but before the Op).
    var newBracket = document.createElement('div');
    newBracket.setAttribute('id', 'openBracket' + num + '.' + theLevel.value);
    newBracket.style.marginLeft = ((theLevel.value - 1) * 25) + 'px';
    newBracket.appendChild(document.createTextNode('('));

    theP.parentNode.insertBefore(newBracket, theP);

    var newClose = document.createElement('div');
    newClose.setAttribute('id', 'closeBracket' + num + '.' + theLevel.value);
    newClose.style.marginLeft = ((theLevel.value - 1) * 25) + 'px';
    newClose.appendChild(document.createTextNode(')'));

    theP.parentNode.insertBefore(newClose, theP.nextSibling);//document.getElementById('operation' + num));

    // If this row still has it's Op, move it to the new close bracket P.
    theOp = document.getElementById('operation' + num);
    if (theOp.parentNode == theP) {
        newClose.appendChild(theOp);
        theOp.setLevel(theLevel.value - 1);
    }

    // Check for neighbouring brackets now.

    // Below, that means having an open bracket, but not a lower level close
    var openBracket = document.getElementById('openBracket' + (num + 1) + '.' + theLevel.value);
    var oneIn = document.getElementById('closeBracket' + num + '.' + (theLevel.value - 1));
    if (openBracket && !oneIn &&
	openBracket.getElementsByTagName('input').length == 0) {
      var lefter = document.createElement('input');
      lefter.setAttribute('type', 'button');
      lefter.setAttribute('value', '<');
      lefter.onclick = bracketLeftShift;
      var righter = document.createElement('input');
      righter.setAttribute('type', 'button');
      righter.setAttribute('value', '>');
      righter.onclick = bracketRightShift;

      //openBracket.appendChild(lefter);
      openBracket.appendChild(righter);
    }

    // Above, it means a close bracket, but not a lower level open
    var closeBracket = document.getElementById('closeBracket' + (num - 1) + '.' + theLevel.value);
    var oneUpIn = document.getElementById('openBracket' + num + '.' + (theLevel.value - 1));
    if (closeBracket && !oneUpIn &&
	newBracket.getElementsByTagName('input').length == 0) {
      var lefter = document.createElement('input');
      lefter.setAttribute('type', 'button');
      lefter.setAttribute('value', '<');
      lefter.onclick = bracketLeftShift;
      var righter = document.createElement('input');
      righter.setAttribute('type', 'button');
      righter.setAttribute('value', '>');
      righter.onclick = bracketRightShift;

      //newBracket.appendChild(lefter);
      newBracket.appendChild(righter);
    }
}

function shiftLeft(theButton) {
    if (!theButton || !theButton.id) {
        theButton = this;
    }
    var num = parseInt(theButton.id.slice(11));

    // Shift the given row left by 1.
    var theP = document.getElementById('row' + num);
    var theLevel = document.getElementById('level' + num);
    var newBracket;

    if (theLevel.value == 0) {
        alert("Can't go more left!");
        return false;
    }

    // Need to remove any excessive bracketing now.

    // When removing bracketing, be sure not to remove the Op.
    var theOp = document.getElementById('operation' + num);

    // If the row above is less indented, then there is already a bracket.
    // Else, might need to create one
    // If the row below is as indented or more, then we need to give them the
    // bracket.
    var openBracket = document.getElementById('openBracket' + num + '.' + theLevel.value);
    var oneDown = document.getElementById('opLevel' + num);
    newBracket = document.getElementById('openBracket' + (num + 1) + '.' + theLevel.value);

    if (!newBracket && oneDown && oneDown.value >= theLevel.value) {
        if (!openBracket) {
            openBracket = document.createElement('div');
            openBracket.style.marginLeft = ((theLevel.value - 1) * 25) + 'px';
            openBracket.appendChild(document.createTextNode('('));
        }
        openBracket.setAttribute('id', 'openBracket' + (num + 1) + '.' + theLevel.value);
        theP.parentNode.insertBefore(
            openBracket, theP.nextSibling);

    } else if (openBracket) {
        openBracket.parentNode.removeChild(openBracket);
    }

    // If the row below is less indented, then there is already a bracket.
    // If the row above is as intended or more, give them the bracket.
    // If the row above was indented, we give the close bracket to them, else
    // we just remove it.
    var closeBracket = document.getElementById('closeBracket' + num + '.' + theLevel.value);
    var oneUp = document.getElementById('opLevel' + (num - 1));
    newBracket = document.getElementById('closeBracket' + (num - 1) + '.' + theLevel.value);

    if (!newBracket && oneUp && oneUp.value >= theLevel.value) {
        if (!closeBracket) {
            closeBracket = document.createElement('div');
            closeBracket.style.marginLeft = ((theLevel.value - 1) * 25) + 'px';
            closeBracket.appendChild(document.createTextNode(')'));
        }
        closeBracket.setAttribute('id', 'closeBracket' + (num - 1) + '.' + theLevel.value);

        if (theOp.parentNode == closeBracket) {
            theP.appendChild(theOp);
            theOp.setLevel(theLevel.value);
        }
        var otherOp = document.getElementById('operation' + (num - 1));
        closeBracket.appendChild(otherOp);
        otherOp.setLevel(theLevel.value - 1);

        theP.parentNode.insertBefore(
                closeBracket,
                theP);
    } else if (closeBracket) {
        if (theOp.parentNode == closeBracket) {
            theP.appendChild(theOp);
            theOp.setLevel(theLevel.value);
        }
        theP.parentNode.removeChild(closeBracket);
    }

    // We may also have removed what was a neighbouring bracket. If we have,
    //need to remove the bracketRightShifter.
    var theOpen = document.getElementById('openBracket' + (num + 1) + '.' + theLevel.value);
    var oneOut = document.getElementById('closeBracket' + num + '.' + (theLevel.value - 1));
    if (theOpen && !oneOut && theOpen.getElementsByTagName('input')[0]) {
      theOpen.removeChild(theOpen.getElementsByTagName('input')[0]);
    }

    theLevel.value--;
    oneDown.value--;
    theP.style.paddingLeft = (theLevel.value * 25) + 'px';
}

function updateRels(theThing) {
  if (!theThing.id) {
    theThing = this;
  }
  var num = parseInt(theThing.id.slice(5));
  var field = theThing;

  var rels = createRelPicker(num, field.value);

  var oldRel = document.getElementById('rel' + num);

  oldRel.parentNode.replaceChild(rels, oldRel);

  updateVals(field, num);
}


function getParentFieldValueSearch(field) {
    var editor;
    // Only search within a particular project is supported - other parent
    // values are ignored
    if (field == 'Project') {
        editor = document.getElementById(field);
        if (editor) {
            return editor.value;
        }
    }
}


function updateVals(field, num) {
  var rel = document.getElementById('rel' + num).value;
  var vals = getSearchEditor(getParentFieldValueSearch, field.value, 'val' + num, null, rel);

  var oldVal = document.getElementById('val' + num);

  // Save the contents if they are both text fields
  if (vals.input.type == 'text' && oldVal.input.type == 'text') {
    vals.input.value = oldVal.input.value;
  }

  oldVal.parentNode.replaceChild(vals, oldVal);
}

// Update all Vals when Proj changes
function handleProjChange() {

  for (var i = 1; true; i++) {
    var oldVal = document.getElementById('val' + i);
    if (oldVal) {
      var rel = document.getElementById('rel' + i).value;
      var vals = getSearchEditor(getParentFieldValueSearch, document.getElementById('field' + i).value, 'val' + i, null, rel);

      vals.value = oldVal.value;
      oldVal.parentNode.replaceChild(vals, oldVal);
    } else {
      break;
    }
  }
}

function createFieldPicker(num) {
    var opt;
    var newF = document.createElement('select');
    newF.setAttribute('id', 'field' + num);
    newF.setAttribute('name', 'field' + num);
    newF.onchange = updateRels;

    // Sort fields by their display names rather than their internal names
    allSearchableFields.sort(
      function(a, b) {
        return allFields[a].longname.toLowerCase().localeCompare(
                 allFields[b].longname.toLowerCase());
      }
    );

    for (var i in allSearchableFields) {
        opt = document.createElement('option');
        opt.setAttribute('value', allSearchableFields[i]);
        opt.appendChild(document.createTextNode(allFields[allSearchableFields[i]].longname));

        newF.appendChild(opt);
    }

    // If being added after an existing entry, copy that entries value
    var previousF = document.getElementById('field' + (num - 1));
    if (previousF) {
        newF.value = previousF.value;
    }

    return newF;
}

function createRelPicker(num, field) {
    var opt;
    var newRel = document.createElement('select');
    newRel.setAttribute('id', 'rel' + num);
    newRel.setAttribute('name', 'rel' + num);

    var allowedValues = [];
    for (var i in allFields[field].rels) {
        opt = document.createElement('option');
        opt.setAttribute('value', allFields[field].rels[i][1]);
        opt.appendChild(document.createTextNode(allFields[field].rels[i][0]));
        allowedValues.push(allFields[field].rels[i][1]);

        newRel.appendChild(opt);
    }

    // If being added after an existing entry, copy that entries value
    var previousRel = document.getElementById('rel' + (num - 1));
    if (previousRel && allowedValues.includes(previousRel.value)) {
        newRel.value = previousRel.value;
    }

    newRel.addEventListener("change", function()
    {
      var myNum = newRel.getAttribute('id').substr(3);
      var fieldPicker = document.getElementById('field' + myNum);
      updateVals(fieldPicker, myNum);
    }, false);

    return newRel;
}

function createOp(num, level) {
    var newDiv = document.createElement('span');
    newDiv.setAttribute('id', 'operation' + num);
    var newLevel = document.createElement('input');
    newLevel.setAttribute('id', 'opLevel' + num);
    newLevel.setAttribute('name', 'opLevel' + num);
    newLevel.setAttribute('type', 'hidden');
    newLevel.setAttribute('value', level);
    var newOp = document.createElement('select');
    newOp.setAttribute('id', 'op' + num);
    newOp.setAttribute('name', 'operation' + num);
    var newAnd = document.createElement('option');
    newAnd.setAttribute('value', 'AND');
    newAnd.appendChild(document.createTextNode('AND'));
    var newOr = document.createElement('option');
    newOr.setAttribute('value', 'OR');
    newOr.appendChild(document.createTextNode('OR'));

    newOp.appendChild(newAnd);
    newOp.appendChild(newOr);

    // If being added after an existing entry, copy that entries value
    var prevOp = document.getElementById('op' + (num - 1));
    if (prevOp) {
        newOp.value = prevOp.value;
    }

    newDiv.appendChild(newLevel);
    newDiv.appendChild(newOp);

    newDiv.setLevel = function(newLevel) {
        newDiv.getElementsByTagName('input')[0].value = newLevel;
    }

    return newDiv;
}

function moveOp(num, newNum) {
    document.getElementById('operation' + num).setAttribute('id', 'operation' + newNum);
    document.getElementById('opLevel' + num).setAttribute('name', 'opLevel' + newNum);
    document.getElementById('opLevel' + num).setAttribute('id', 'opLevel' + newNum);

    var theOp = document.getElementById('op' + num);
    theOp.setAttribute('id', 'op' + newNum);
    theOp.setAttribute('name', 'operation' + newNum);
}

// showDummyRow
//
// Show or hide the div that is shown when there are no rows in the search
// query.
function showDummyRow(show) {
    if (show) {
        display = 'inline';
    } else {
        display = 'none';
    }
    document.getElementById('tiqitSearcherDummyRow').style.display = display;
}

var numRows = 0;

function addRow(event) {
    var oldL, oldR, oldF, oldRel, oldVal, oldOp, oldPlus, oldMinus;

    if (event) {
      if (event.id) {
        theButton = event;
      } else {
        theButton = event.target;
      }
    } else {
      theButton = window;
    }

    var num = 0;
    var parentRow = null;
    if (theButton != window) {
        num = parseInt(theButton.id.slice(5));
        parentRow = theButton.parentNode.nextSibling;
    }

    // Adds a new row below the given row
    if (num > numRows) {
        alert('There are only ' + numRows + " rows. Can't add one at " + num);
        return false;
    }
    if (num < 0) {
        // Idiot.
        alert("Can't add rows at negative positions: " + num);
        return false;
    }

    if (num < numRows) {
        // Need to move all subsequent rows up one.
        for (var i = numRows; i > num; i--) {
            document.getElementById('row' + i).id = 'row' + (i + 1);

            oldLevel = document.getElementById('level' + i);
            oldLevel.setAttribute('id', 'level' + (i + 1));
            oldLevel.setAttribute('name', 'level' + (i + 1));

            oldL = document.getElementById('leftShifter' + i);
            oldL.setAttribute('id', 'leftShifter' + (i + 1));

            oldR = document.getElementById('rightShifter' + i);
            oldR.setAttribute('id', 'rightShifter' + (i + 1));

            oldF = document.getElementById('field' + i);
            oldF.setAttribute('id', 'field' + (i + 1));
            oldF.setAttribute('name', 'field' + (i + 1));

            oldRel = document.getElementById('rel' + i);
            oldRel.setAttribute('id', 'rel' + (i + 1));
            oldRel.setAttribute('name', 'rel' + (i + 1));

            oldVal = document.getElementById('val' + i);
            oldVal.setAttribute('id', 'val' + (i + 1));
            oldVal.input.setAttribute('name', 'val' + (i + 1));

            moveOp(i, i + 1);

            oldPlus = document.getElementById('adder' + i);
            oldPlus.setAttribute('id', 'adder' + (i + 1));

            oldMinus = document.getElementById('minuser' + i);
            oldMinus.setAttribute('id', 'minuser' + (i + 1));

            // Also need to up the numbers of any brackets for this row.
            for (var j = 1; j <= oldLevel.value; j++) {
                oldOpen = document.getElementById('openBracket' + i + '.' + j);
                if (oldOpen) {
                    oldOpen.setAttribute('id', 'openBracket' + (i + 1) + '.' + j);
                }

                oldClose = document.getElementById('closeBracket' + i + '.' + j);
                if (oldClose) {
                    oldClose.setAttribute('id', 'closeBracket' + (i + 1) + '.' + j);
                }
            }
        }
    }

    // Get level for new row
    var level = 0;
    if (num > 0) {
        level = document.getElementById('level' + num).value;
    }

    num++;

    // Create the new row
    var newP = document.createElement('p');
    newP.setAttribute('id', 'row' + num);
    newP.style.paddingLeft = (level * 25) + 'px';
    var newLevel = document.createElement('input');
    newLevel.setAttribute('id', 'level' + num);
    newLevel.setAttribute('name', 'level' + num);
    newLevel.setAttribute('type', 'hidden');
    newLevel.setAttribute('value', level);
    var newL = document.createElement('input');
    newL.setAttribute('id', 'leftShifter' + num);
    newL.setAttribute('type', 'button');
    newL.setAttribute('value', '<');
    newL.onclick = shiftLeft;
    var newR = document.createElement('input');
    newR.setAttribute('id', 'rightShifter' + num);
    newR.setAttribute('type', 'button');
    newR.setAttribute('value', '>');
    newR.onclick = shiftRight;
    var newF = createFieldPicker(num);
    var newRel = createRelPicker(num, newF.value);
    var newVal = getSearchEditor(getParentFieldValueSearch, newF.value, 'val' + num);
    var newOp = createOp(num, level);
    var newPlus = document.createElement('input');
    newPlus.setAttribute('id', 'adder' + num);
    newPlus.setAttribute('type', 'button');
    newPlus.setAttribute('value', '+');
    newPlus.onclick = addRow;
    var newMinus = document.createElement('input');
    newMinus.setAttribute('id', 'minuser' + num);
    newMinus.setAttribute('type', 'button');
    newMinus.setAttribute('value', '-');
    newMinus.onclick = removeRow;

    newP.appendChild(newLevel);
    newP.appendChild(newL);
    newP.appendChild(newR);
    newP.appendChild(newF);
    newP.appendChild(newRel);
    newP.appendChild(newVal);
    newP.appendChild(newPlus);
    newP.appendChild(newMinus);
    newP.appendChild(newOp);

    numRows++;

    // Insert in right place
    document.getElementById('tiqitSearcher').insertBefore(newP, parentRow);
    updateRels(newF);

    // For bracketing, we may need to move the end bracket of the row above the
    // new one.
    var closeBracket;
    for (var i = 1; i <= level; i++) {
        closeBracket = document.getElementById('closeBracket' + (num - 1) + '.' + i);
        if (closeBracket) {
            closeBracket.setAttribute('id', 'closeBracket' + num + '.' + i);
            newP.parentNode.insertBefore(closeBracket, newP.nextSibling);
        }
    }

    // If the row above doesn't have its Op, then put our Op where its Op is and give it back its Op
    var theOp = document.getElementById('operation' + (num - 1));
    var theP = document.getElementById('row' + (num - 1));
    if (theOp && theOp.parentNode != theP) {
        // Our new Op should now take on the value of the existing Op so the
        // value between the brackets remains the same.
        // The existing Op should then be updated to copy the operator of the
        // line before it if there is one so ORs/ANDs within a set of brackets
        // behave consistently
        var theOpSelect = document.getElementById('op' + (num - 1));
        var newOpSelect = document.getElementById('op' + num);
        newOpSelect.value = theOpSelect.value;
        var prevOpSelect = document.getElementById('op' + (num - 2));
        if (prevOpSelect) {
            theOpSelect.value = prevOpSelect.value;
        }

        // Position the ops
        theOp.parentNode.appendChild(newOp);
        newOp.setLevel(theOp.getElementsByTagName('input')[0].value);
        theP.appendChild(theOp);
        theOp.setLevel(document.getElementById('level' + (num - 1)).value);
    }

    showDummyRow(false);

    return true;
}

function removeRow() {
    var oldRow = null;
    var num = parseInt(this.id.slice(7));
    oldRow = this.parentNode;

    // We renumber following rows so all is still nice.
    if (num > numRows) {
        alert('There are only ' + numRows + " rows. Can't remove one from " + num);
        return false;
    }
    if (num < 1) {
        // Idiot.
        alert("Can't remove that row: " + num);
        return false;
    }

    // Before we remove the row, we need to move any close brackets owned by it
    // up, and any trailing open brackets.
    var theLevel = document.getElementById('level' + num);

    // Open brackets:
    // If the row below is less indented, remove opens
    var oneDown = document.getElementById('opLevel' + num);
    var oneDownLevel = oneDown ? oneDown.value : 0;
    var openBracket;
    for (var i = theLevel.value; i > oneDownLevel; i--) {
        openBracket = document.getElementById('openBracket' + num + '.' + i);
        if (openBracket) {
            openBracket.parentNode.removeChild(openBracket);
        }
    }

    // Close Brackets:
    // If the row above is less indented, remove closes
    var oneUp = document.getElementById('opLevel' + (num - 1));
    var oneUpLevel = oneUp ? oneUp.value : 0;
    var closeBracket;
    for (var i = theLevel.value; i > oneUpLevel; i--) {
        closeBracket = document.getElementById('closeBracket' + num + '.' + i);
        if (closeBracket) {
            closeBracket.parentNode.removeChild(closeBracket);
        }
    }

    // We may have moved two brackets into close proximity.
    //var closeUp = document.getElementById('closeBracket' + (num - 1) + '.' + 


    oldRow.parentNode.removeChild(oldRow);

    // If the Op still exists, then we need to make sure we move the above
    // row's Op to the location of the Op.
    var theOp = document.getElementById('operation' + num);
    if (theOp) {
        var oldOp = document.getElementById('operation' + (num - 1));

        // Swap the select values
        var theSelectValue = theOp.getElementsByTagName('select')[0].value;
        theOp.getElementsByTagName('select')[0].value = oldOp.getElementsByTagName('select')[0].value;
        oldOp.getElementsByTagName('select')[0].value = theSelectValue;

        // Reposition the Op
        theOp.parentNode.appendChild(oldOp);
        oldOp.setLevel(theOp.getElementsByTagName('input')[0].value);
        theOp.parentNode.removeChild(theOp);
    }

    // Any remaining brackets on this row need to have their numbers dropped.
    for (var j = 1; j <= theLevel.value; j++) {
        oldOpen = document.getElementById('openBracket' + num + '.' + j);
        if (oldOpen) {
            oldOpen.setAttribute('id', 'openBracket' + (num - 1) + '.' + j);
        }

        oldClose = document.getElementById('closeBracket' + num + '.' + j);
        if (oldClose) {
            oldClose.setAttribute('id', 'closeBracket' + (num - 1) + '.' + j);
        }
    }

    if (num < numRows) {
        // Need to move all subsequent rows down one.
        for (var i = num + 1; i <= numRows; i++) {
            document.getElementById('row' + i).id = 'row' + (i - 1);

            oldLevel = document.getElementById('level' + i);
            oldLevel.setAttribute('id', 'level' + (i - 1));
            oldLevel.setAttribute('name', 'level' + (i - 1));

            oldL = document.getElementById('leftShifter' + i);
            oldL.setAttribute('id', 'leftShifter' + (i - 1));

            oldR = document.getElementById('rightShifter' + i);
            oldR.setAttribute('id', 'rightShifter' + (i - 1));

            oldF = document.getElementById('field' + i);
            oldF.setAttribute('id', 'field' + (i - 1));
            oldF.setAttribute('name', 'field' + (i - 1));

            oldRel = document.getElementById('rel' + i);
            oldRel.setAttribute('id', 'rel' + (i - 1));
            oldRel.setAttribute('name', 'rel' + (i - 1));

            oldVal = document.getElementById('val' + i);
            oldVal.setAttribute('id', 'val' + (i - 1));
            oldVal.input.setAttribute('name', 'val' + (i - 1));

            moveOp(i, i - 1);

            oldPlus = document.getElementById('adder' + i);
            oldPlus.setAttribute('id', 'adder' + (i - 1));

            oldMinus = document.getElementById('minuser' + i);
            oldMinus.setAttribute('id', 'minuser' + (i - 1));

            // Also need to drop the numbers of any brackets for this row.
            for (var j = 1; j <= oldLevel.value; j++) {
                oldOpen = document.getElementById('openBracket' + i + '.' + j);
                if (oldOpen) {
                    oldOpen.setAttribute('id', 'openBracket' + (i - 1) + '.' + j);
                }

                oldClose = document.getElementById('closeBracket' + i + '.' + j);
                if (oldClose) {
                    oldClose.setAttribute('id', 'closeBracket' + (i - 1) + '.' + j);
                }
            }
        }
    }

    numRows--;

    if (numRows == 0) {
        showDummyRow(true);
    }

    return true;
}

function setRowValues(num, field, rel, val, op) {
  if (num < 1 || num > numRows) {
    alert("Can't set anything on a non-existant row");
    return false;
  }

  var theF = document.getElementById('field' + num);
  theF.value = field;
  updateRels(theF);

  if (rel) {
    document.getElementById('rel' + num).value = rel;
  }
  if (val) {
    document.getElementById('val' + num).input.value = val;
  }
  if (op) {
    document.getElementById('op' + num).value = op;
  }
}

// Sort Field Selector code

function createSortField(prefix, num) {
  var newS, opt, newO, newP;

  newP = document.createElement('span');
  newP.setAttribute('id', prefix + 'Selector' + num);

  newS = document.createElement('select');
  newS.setAttribute('id', prefix + num);
  newS.setAttribute('name', prefix + num);
  for (f in allViewableFields) {
    opt = document.createElement('option');
    opt.setAttribute('value', allViewableFields[f]);
    opt.appendChild(document.createTextNode(allFields[allViewableFields[f]].longname));

    newS.appendChild(opt);
  }

  newO = document.createElement('select');
  newO.setAttribute('id', prefix + 'Order' + num);
  newO.setAttribute('name', prefix + 'Order' + num);
  opt = document.createElement('option');
  opt.setAttribute('value', 'ASC');
  opt.appendChild(document.createTextNode('ASC'));
  newO.appendChild(opt);
  opt = document.createElement('option');
  opt.setAttribute('value', 'DESC');
  opt.appendChild(document.createTextNode('DESC'));
  newO.appendChild(opt);

  newP.appendChild(newS);
  newP.appendChild(newO);

  return newP;
}

function addSortField(prefix) {
  var newF;
  var selectO = document.getElementById(prefix + 'Selector');

  if (selectO.numFields == undefined) {
    selectO.numFields = 0;
  }
  num = selectO.numFields + 1;
  newF = createSortField(prefix, num);

  if (num == 1) {
    selectO.appendChild(newF);
  } else {
    selectO.insertBefore(newF, document.getElementById(prefix + 'Selector' + (num - 1)).nextSibling);
  }

  selectO.numFields++;
}

function removeSortField(prefix) {
  var selectO = document.getElementById(prefix + 'Selector');
  if (selectO.numFields == 1) {
    alert("Don't try to remove all the fields, punk");
    return false;
  }

  var field = document.getElementById(prefix + 'Selector' + selectO.numFields);
  field.parentNode.removeChild(field);
  selectO.numFields--;
}

function setSortField(prefix, num, field, order) {
  document.getElementById(prefix + num).value = field;
  document.getElementById(prefix + 'Order' + num).value = order;
}

//
// Group by checks
//

function createGroupedSortField() {
  var opt;
  var span = document.createElement('span');
  span.id = 'sortSelector1';

  var select = document.createElement('select');
  select.id = 'sort1';
  select.name = 'sort1';

  var selections = new Array();
  for (var i = 1; ; i++) {
    var selector = document.getElementById('selection' + i);
    if (selector) {
      if (!contains(selections, selector.value)) {
        selections.push(selector.value);
      }
    } else {
      break;
    }
  }

  for (var i = 0; i < selections.length; i++) {
    opt = document.createElement('option');
    opt.value = selections[i];
    opt.appendChild(document.createTextNode(allFields[selections[i]].longname));

    select.appendChild(opt);
  }

  var order = document.createElement('select');
  order.id = 'sortOrder1';
  order.name = 'sortOrder1';
  opt = document.createElement('option');
  opt.values = 'ASC';
  opt.appendChild(document.createTextNode('ASC'));
  order.appendChild(opt);
  opt = document.createElement('option');
  opt.values = 'DESC';
  opt.appendChild(document.createTextNode('DESC'));
  order.appendChild(opt);

  span.appendChild(select);
  span.appendChild(order);

  return span;
}

function checkGroupBy(event) {
  var grouping = document.getElementById('tiqitGroupBy');
  var firstSorter = document.getElementById('sort1');
  if (grouping && firstSorter) {
    grouping = grouping.checked;
  } else {
    return;
  }
  var oldVal = firstSorter.value;
  var replacement;

  if (grouping) {
    replacement = createGroupedSortField();
  } else {
    replacement = createSortField('sort', 1);
  }

  replacement.firstChild.value = oldVal;

  firstSorter.parentNode.parentNode.replaceChild(replacement, firstSorter.parentNode);
}

addCustomEventListener("FirstWindowLoad", function () { setTimeout(checkGroupBy, 1); });

    // Public
    return {
      'addRow': addRow,
      'setRowValues': setRowValues,
      'shiftLeft': shiftLeft,
      'shiftRight': shiftRight,
      'bracketLeftShift': bracketLeftShift,
      'bracketRightShift': bracketRightShift,
      'checkGroupBy': checkGroupBy,
      'addSortField': addSortField,
      'setSortField': setSortField,
      'removeSortField': removeSortField,
      'getParentFieldValueSearch': getParentFieldValueSearch,
      'showDummyRow': showDummyRow,
    };
})();
