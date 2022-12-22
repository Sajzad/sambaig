var app = new Vue({
  el: '#app',
  delimiters:['[[', ']]'],
  data: {
  	ani_ids: [],
  },
  created(){
        try{
            msg = document.getElementById("response").value;
            this.selectedGif = document.getElementById("gif_url").value;
            this.message = msg;
        }catch{

        }
  },
  filters: {
  },
  methods: {
    removeAni(){
      if (confirm_delete()){
        let url = window.location.href;
          let data = {
            "check": 'remove_ani',
            "ani_ids": this.ani_ids
          }
          sendRequest(url, 'post', data)
          .then(function(response){
            refresh()
          })
      }
    }
  }
})
