var app = new Vue({
  el: '#aside',
  delimiters:['[[', ']]'],
  data: {
      is_dropDown: false,
      primary_number:'',

  },
  created(){
        console.log('yessss')
  },
  filters: {
  },
  methods: {
    activateDropdown(){
      this.is_dropDown = true
    },    
    deactivateDropdown(){
      this.is_dropDown = false
    },
    pn(ani_id){
        var data = {
            "check": "add_primary_number",
            "ani_id": ani_id
        }
        var url = "/campaigns/primary-number/";
        var vm = this;
        sendRequest(url, "post", data)
        .then(function(response){
        	refresh();
        })
    },
  }
})
