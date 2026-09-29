// Codigo comun a todas las paginas del sitio.

// El boton de animacion solo existe en algunas paginas: se protege el acceso
// para que su ausencia no rompa el resto de los manejadores de esta pagina.
function classToggle() {
    var el = document.querySelector('.icon-cards__content');
    if (!el) return;
    el.classList.toggle('step-animation');
}

document.addEventListener('DOMContentLoaded', function () {
    var toggle = document.querySelector('#toggle-animation');
    if (toggle) {
        toggle.addEventListener('click', classToggle);
    }
});

$(document).ready(function () {
    // Atenua las imagenes del carrusel salvo la diapositiva activa.
    $('#carouselSuperior').on('slide.bs.carousel', function () {
        $('.carousel-item img').css('filter', 'brightness(0.7)');
    });

    $('#carouselSuperior').on('slid.bs.carousel', function () {
        $('.carousel-item.active img').css('filter', 'brightness(1)');
    });

    // Muestra la imagen asociada al pasar el cursor por un elemento.
    $('.dropdown-img').hover(function () {
        $('#' + $(this).data('dropdown')).css('display', 'block');
    }, function () {
        $('#' + $(this).data('dropdown')).css('display', 'none');
    });
});
