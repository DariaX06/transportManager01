var maps = document.querySelectorAll(".map");
maps.forEach(el => {
    // Дождёмся загрузки API и готовности DOM.
    ymaps.ready(init);
    function init () {
        // Создание экземпляра карты и его привязка к контейнеру с
        // заданным id ("map").
        coord = Array.from(el.getAttribute('data').split(', '), x => parseFloat(x));
        var myMap = new ymaps.Map(el.getAttribute('id'), {
            // При инициализации карты обязательно нужно указать
            // её центр и коэффициент масштабирования.
            
            center: [coord[0], coord[1]],
            zoom: 10
        }, {
            searchControlProvider: 'yandex#search'
        });
        var myGeoObject = new ymaps.GeoObject({
            // Описание геометрии.
            geometry: {
                type: "Point",
                coordinates: [coord[0], coord[1]]
            }
        });
        myMap.geoObjects.add(myGeoObject);
    }
});