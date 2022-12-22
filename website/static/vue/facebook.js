var app = new Vue({
  el: '#app',
  delimiters:['[[', ']]'],
  data: {
    leadIds: [],
    form : '',
    currentList: '',
    deleteAllLeads : false,

  },
  created(){
    
  },
  filters: {
  },
  methods: {
    deleteAllContacts(){
      var msg = 'Are you sure you want to delete all the contacts from this List?'
      if (confirm(msg)){
        var url = window.location.href;
        var data = {
            check: "delete_all_lead",
        }
        sendRequest(url,'post',data)
        .then(function(response){
            sweetText("Leads deleted!")
            refresh()
        })
      }
    },
    deleteAll(){
      if (this.deleteAllLeads==false){
        this.deleteAllLeads = true;
      }else{
        this.deleteAllLeads = false;
      }
    },
    getForm(form_id){
      var url = window.location.href;
      var vm = this;
      var data = {
          check: "get_form",
          form_id: form_id
      }
      sendRequest(url,'post',data)
      .then(function(response){
          vm.form = response.data.form;
        })

    },
    moveContact(form_id){
      this.currentList = form_id;
    },
    deleteLead(){
      if (confirm("Are you sure you want to delete the Leads?")){
        var url = window.location.href;
        var data = {
            check: "delete_lead",
            lead_ids: this.leadIds
        }
        sendRequest(url,'post',data)
        .then(function(response){
            sweetText("Leads deleted!")
            refresh()
        })
      }
    },
    deleteForm(form_id){
      console.log(form_id);
      if (confirm_delete()){
          var url = window.location.href;
          var data = {
              check: "delete_form",
              form_id: form_id
          }
          sendRequest(url,'post',data)
          .then(function(response){
              sweetText("Leads deleted!")
              refresh()
          })
      }
    }
  }
})
