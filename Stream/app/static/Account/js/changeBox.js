(function change() {
    var Box = {};
    Box.box = document.getElementById("changeBox");
    Box.openBotton = document.getElementById("change");
    Box.closeBotton = document.getElementById("closeChangeBox");

    Box.showBox = function(){
        console.log(this.box);
        this.box.style.display = "block";
    }

    Box.closeBox = function(){
        this.box.style.display = "none";
    }

    Box.outsideClick = function(){
        var box = this.box;
        window.onclick = function(event){
            if(event.target == box){
                box.style.display = "none";
            }
        }
    }
    Box.init = function(){
        var that = this;
        this.openBotton.onclick = function(){
            that.showBox();
        }
        this.closeBotton.onclick = function(){
            that.closeBox();
        }
        this.outsideClick();
    }

    Box.init();

})();