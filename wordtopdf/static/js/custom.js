function toggle_left_panel() {
    var left_panel = document.getElementById("left_panel");
    var right_panel = document.getElementById("right_panel");
    var img_gal = document.getElementsByClassName("img-gal");

    console.log(img_gal)

    if (left_panel.style.display === "none") {
        left_panel.style.display = "block";

        right_panel.classList.add('col-md-6');
        right_panel.classList.remove('col-md-12');

        for (var i = 0 ; i < img_gal.length ; i++) {
            img_gal[i].style.width = "150px";
            img_gal[i].style.height = "150px";
        };

    } else {
        left_panel.style.display = "none";

        right_panel.classList.add('col-md-12');
        right_panel.classList.remove('col-md-6');

        for (var i = 0 ; i < img_gal.length ; i++) {
            img_gal[i].style.width = "250px";
            img_gal[i].style.height = "250px";
        };

    }
}