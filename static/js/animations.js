document.addEventListener('DOMContentLoaded', function(){
    // simple reveal animations
    document.querySelectorAll('.fade-in').forEach(function(el){
        el.style.opacity = 0;
        el.style.transform = 'translateY(6px)';
        setTimeout(function(){
            el.style.transition = 'opacity 450ms ease, transform 450ms ease';
            el.style.opacity = 1;
            el.style.transform = 'translateY(0)';
        }, 80);
    });

    document.querySelectorAll('.slide-up').forEach(function(el, i){
        el.style.opacity = 0;
        el.style.transform = 'translateY(10px)';
        setTimeout(function(){
            el.style.transition = 'opacity 420ms ease '+(i*60)+'ms, transform 420ms ease '+(i*60)+'ms';
            el.style.opacity = 1;
            el.style.transform = 'translateY(0)';
        }, 120);
    });
});
