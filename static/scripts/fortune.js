//
// Fortune cookies! Yum yum...
//

allFortunes = new Array();

function nextFortune() {
  var oldFortune = document.getElementById('tiqitFortune');
  var newFortune = document.getElementById('tiqitFortuneNew');

  if (oldFortune) {
    allFortunes.push(oldFortune);
    oldFortune.id = null;
    oldFortune.parentNode.removeChild(oldFortune);
  }

  newFortune.id = 'tiqitFortune';
}

function endFortunes() {
  var fortune = document.getElementById('tiqitFortune');

  if (fortune) {
    allFortunes.push(fortune);
    fortune.id = null;
    fortune.parentNode.removeChild(fortune);
  }
}

function showFortune(event) {
  var current = document.getElementById('tiqitFortune');
  if (current) {
    current.id = null;
    current.parentNode.removeChild(current);
  }

  var content = document.getElementById('tiqitContent');
  content.insertBefore(event.target.fortune, content.firstChild);
  event.target.fortune.id = 'tiqitFortune';
}

function hideFortune(icon) {
  if (!contains(allFortunes, icon.parentNode)) {
    allFortunes.push(icon.parentNode);
  }

  icon.parentNode.id = null;
  icon.parentNode.parentNode.removeChild(icon.parentNode);
}

function initFortuneMenu() {
  if (Tiqit.prefs['miscHideFortunes'] == 'false') {
    var menu = document.createElement('div');
    menu.id = 'tiqitMenuFortunes';
    menu.className = 'tiqitMenu';

    var item = document.createElement('img');
    item.src = 'images/fortune-small.gif';
    item.alt = '[Fortunes]';
    menu.appendChild(item);

    var list = document.createElement('ul');
    menu.appendChild(list);

    for (var i = 0; i < allFortunes.length; i++) {
      item = document.createElement('li');
      item.addEventListener('click', showFortune, false);
      item.className = 'tiqitMenuAction';
      item.fortune = allFortunes[i];

      var img = document.createElement('img');
      img.src = 'images/fortune-small.gif';
      img.alt = '[Cookie]';
      item.appendChild(img);

      var text = allFortunes[i].textContent.trim();

      if (allFortunes[i].textContent.length > 20) {
        item.appendChild(document.createTextNode(text.substring(0, 17) + '...'));
      } else {
        item.appendChild(document.createTextNode(text));
      }

      list.appendChild(item);
    }

    var container = document.getElementById('tiqitMenus');
    container.appendChild(menu);
  }
}

addCustomEventListener("FirstWindowLoad", endFortunes);
addCustomEventListener("FirstWindowLoad", initFortuneMenu);
