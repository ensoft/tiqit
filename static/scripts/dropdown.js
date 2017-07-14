//
// Provides a drop down box.
//

var dropDown;

addCustomEventListener("FirstWindowLoad", dropDownInit);

function dropDownInit() {
  dropDown = document.createElement('div');
  dropDown.setAttribute('id', 'dropdown');
  dropDown.style.display = 'none';
  dropDown.onmouseout = function(event) {
    try {
      if (event.relatedTarget != dropDown &&
	  event.relatedTarget.parentNode != dropDown) {
	document.getElementById('dropdown').style.display = 'none';
      }
    } catch (e) {
      document.getElementById('dropdown').style.display = 'none';
    }
  };

  dropDown.onclick = function(event) {
    document.getElementById('dropdown').style.display = 'none';
  };

  document.body.appendChild(dropDown);
}

function makeDropDown(links, name, event) {
  while (dropDown.hasChildNodes()) {
    dropDown.removeChild(dropDown.childNodes[0]);
  }

  if (typeof(name) != 'string') {
    if (name.nodeName.toLowerCase() == 'input') {
      name = name.value;
    } else {
      name = name.textContent;
    }
  }

  for (var i = 0; i < links.length; i++) {
    temp = document.createElement('a');
    temp.appendChild(document.createTextNode(links[i][0]));
    if (typeof(links[i][1]) == "function") {
      temp.setAttribute('href', links[i][1](name));
    } else {
      temp.setAttribute('href', links[i][1].replace('NAME', name));
    }

    dropDown.appendChild(temp);
  }

  dropDown.style.display = 'block';
  dropDown.style.left = (event.clientX - 3) + 'px';
  dropDown.style.top = (event.clientY - 3) + 'px';
}
