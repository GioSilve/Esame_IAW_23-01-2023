'use strict'

const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]')
const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl))

document.querySelectorAll('input[type="search"]').forEach(searchbar => {
    let searchbtn = document.querySelector(`#searchbtn${searchbar.id}`)
    searchbtn.addEventListener("click", e => {
        let input_search = searchbar.value.toLowerCase();
        let titles = [];
        let episodes_spans = document.querySelectorAll(`#collapseEpisodes${searchbar.id} span`)
        episodes_spans.forEach(span => {
            titles.push(span.dataset.episodetitle.toLowerCase());
        });
        let descriptions = [];
        let episodes_icons = document.querySelectorAll(`#collapseEpisodes${searchbar.id} i`)
        episodes_icons.forEach(icon => {
            descriptions.push(icon.dataset.episodedescription.toLowerCase());
        });
        for (let i = 0; i < titles.length; i++) {
            if (!(titles[i].includes(input_search)) && !(descriptions[i].includes(input_search))) {
                let episode_id = episodes_spans[i].dataset.episodeid
                let episode_container = document.querySelector(`a[data-episodeid="${episode_id }"`);
                episode_container.classList.add('d-none');
            }
            //console.log(`${titles[i]} = ${descriptions[i]}`);
        }
    });
});
