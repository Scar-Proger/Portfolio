/* ===== Boot sequence ===== */
  const bootWords = ['открываю', 'портфолио', '...', 'готово.'];
  const bootLine = document.getElementById('bootLine');
  const boot = document.getElementById('boot');
  const mainContent = document.getElementById('mainContent');



  
  function initNavigation(){
    const nav = document.querySelector('.topnav');
    if(!nav) return;
    const links = nav.querySelectorAll('a');
    const moveIndicator = link=>{
      nav.style.setProperty('--indicator-left', `${link.offsetLeft}px`);
      nav.style.setProperty('--indicator-width', `${link.offsetWidth}px`);
    };
    const activeLink = nav.querySelector('.active') || links[0];
    moveIndicator(activeLink);
    links.forEach(link=>{
      link.addEventListener('click', ()=>{
        links.forEach(item=>item.classList.remove('active'));
        link.classList.add('active');
        moveIndicator(link);
      });
    });
    window.addEventListener('resize', ()=>{
      moveIndicator(nav.querySelector('.active') || links[0]);
    });
  }

  initNavigation();

  let wi = 0;
  function nextWord(){
    if(wi >= bootWords.length){
      setTimeout(()=>{
        boot.classList.add('hidden');
        mainContent.classList.add('show');
        initReveal();
        initCodeTyping();
      }, 150);
      return;
    }
    bootLine.innerHTML = bootWords[wi] + '<span class="caret"></span>';
    wi++;
    setTimeout(nextWord, 240);
  }
  nextWord();

  function initReveal(){
    const items = document.querySelectorAll('.reveal');
    const obs = new IntersectionObserver((entries)=>{
      entries.forEach(e=>{
        if(e.isIntersecting){ e.target.classList.add('in'); obs.unobserve(e.target); }
      });
    }, { threshold: 0.15 });
    items.forEach(it=> obs.observe(it));
  }

  setTimeout(()=>{
    if(!mainContent.classList.contains('show')){
      boot.classList.add('hidden');
      mainContent.classList.add('show');
      initReveal();
      initCodeTyping();
    }
  }, 2500);

  /* ===== Code typing animation (replays every time a code block re-enters view) ===== */
  function renderTyped(node, state){
    /* Once the typed budget (state.n) runs out, nothing after that point —
       not even a structural tag like <br> — should be included. Previously
       <br> and empty <span> wrappers were cloned unconditionally, so
       not-yet-typed line breaks still showed up as blank lines, and the
       caret (appended last) ended up parked below them instead of right
       after the last visible character. */
    if(state.done) return null;

    if(node.nodeType === Node.TEXT_NODE){
      const text = node.textContent;
      if(state.n >= text.length){
        state.n -= text.length;
        return document.createTextNode(text);
      } else if(state.n > 0){
        const t = text.slice(0, state.n);
        state.n = 0;
        state.done = true;
        return document.createTextNode(t);
      }
      state.done = true;
      return null;
    }
    const clone = node.cloneNode(false);
    node.childNodes.forEach(child=>{
      if(state.done) return;
      const res = renderTyped(child, state);
      if(res) clone.appendChild(res);
    });
    return clone;
  }

  /* Renders `n` characters of the code into `el`, then always appends
     a blinking caret at the end — so the cursor is visible both while
     typing/deleting AND during the pauses in between. */
  function paintCode(el, template, n){
    const state = { n };
    const rendered = renderTyped(template.content.cloneNode(true), state);
    el.innerHTML = '';
    el.appendChild(rendered);
    const caret = document.createElement('span');
    caret.className = 'caret';
    el.appendChild(caret);
  }

  /* Full loop for one code block: type it out, hold for 3s (caret blinking),
     delete it, hold briefly, then start typing again — forever, while the
     block stays visible. */
  function loopTyping(el){
    const template = document.createElement('template');
    template.innerHTML = el.dataset.code;
    const totalLen = template.content.textContent.length;

    function typeStep(n){
      if(el._stopped) return;
      paintCode(el, template, n);
      el._curLen = n;
      if(n < totalLen){
        el._typeTimer = setTimeout(()=>typeStep(n + 1), 26);
      } else {
        el._typeTimer = setTimeout(()=>deleteStep(n), 3000); // pause with caret before deleting
      }
    }

    function deleteStep(n){
      if(el._stopped) return;
      n = Math.max(0, n - 2);
      paintCode(el, template, n);
      el._curLen = n;
      if(n > 0){
        el._typeTimer = setTimeout(()=>deleteStep(n), 18);
      } else {
        el._typeTimer = setTimeout(()=>typeStep(0), 500); // brief pause before retyping
      }
    }

    el._stopped = false;
    typeStep(el._curLen || 0);
  }

  function stopTyping(el){
    el._stopped = true;
    if(el._typeTimer){ clearTimeout(el._typeTimer); el._typeTimer = null; }
  }

  function initCodeTyping(){
    const blocks = document.querySelectorAll('.proj-visual .code');
    if(!blocks.length) return;
    blocks.forEach(block=>{
      if(!block.dataset.code){
        block.dataset.code = block.innerHTML;
      }
      block.innerHTML = '';
      block._curLen = 0;
    });
    const obs = new IntersectionObserver((entries)=>{
      entries.forEach(entry=>{
        const el = entry.target;
        if(entry.isIntersecting){
          if(!el._typeTimer) loopTyping(el);
        } else {
          stopTyping(el);
        }
      });
    }, { threshold: 0.4 });
    blocks.forEach(b=> obs.observe(b));
  }