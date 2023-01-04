var app = new Vue({
  el: '#app',
  delimiters:['[[', ']]'],
  data: {
    leads:[],
    dnis:null,
    message:null,
    chats:[],
    chat:[],
    ppls: [],
    first: 0,
    second: 100,
    check_text_input: null,
    text_output: null,
    newNumber: null,
    newMessage: null,
    scheduledAt: null,
    ani: null,
    newMsgInput: false,
    isMsg: true,
    isNote: false,
    image: [],
    images: [],
    mms: null,

  },
  created(){
    var url = window.location.href;
    var vm = this;
    let data = {
        "check": "leads",
        "first":this.first,
        "second": this.second
    };
    this.first = this.second;
    this.second = this.second + 2;
    console.log(this.first, this.second)
    console.log(data)
    var r = sendRequest(url, 'post', data)
        .then(function(response){
            vm.leads = response.data.leads;
            vm.ani = response.data.ani
        })

    sendRequest(url, 'get')
    .then(function(response){
        vm.images = response.data.images
    })
  },
  filters: {
  },
  methods: {
    handlingFile(e){
        this.image = e.target.files[0]

    },
    uploadImage(){
        var url = window.location.href;
        var vm = this;
        let formData = new FormData();
        formData.append('image', this.image);
        formData.append('check', 'upload_image');

        sendRequest(url, 'post', formData)
        .then(function(response){
            console.log(response.data.images);
            vm.images = response.data.images;
        })
    },
    sendNote(){
        console.log('yess')
        var url = window.location.href;

        var vm = this;
        var data = {
            check: 'send_note',
            ani:this.ani,
            dnis:this.dnis,            
            message: this.message,
        }
        console.log(data)
        fileRequest(url, 'post', data)
        .then(function(response){
            vm.chats = response.data.chats;
            vm.leads = response.data.leads;
            vm.scheduledAt = null;
            vm.newMessage = null;
            vm.newNumber = null;
        })
    },
    shiftToNote(){
        this.isMsg = false;
        this.isNote = true;
    },    
    shiftToMsg(){
        this.isMsg = true;
        this.isNote = false;
    },
    enableNewMsgInput(){
        this.chats = [];
        this.isMsg = false;
        if (this.newMsgInput==false){
            this.newMsgInput = true;
        }else{
            this.newMsgInput = false;
            this.isMsg = true;
        }
    },
    getUserName(admin_id){
        
    },
    formatDate(date) {
      return moment(date).format("Do MMM YYYY LT")
    },    
    formatTime(date) {
      return moment(date).format("LT")
    },
    sendNewMessage(){
        var url = window.location.href;
        var vm = this;
        var data = {
            check: 'new_message',
            new_number: this.newNumber,
            new_message: this.message,
            mms : this.mms,
            scheduled_at: this.scheduledAt,
        }
        sendRequest(url, 'post', data)
        .then(function(response){
            vm.chats = response.data.chats;
            vm.leads = response.data.leads;
            vm.ani = response.data.ani;
            vm.dnis = response.data.dnis;
            vm.scheduledAt = null;
            vm.message = null;
            vm.newNumber = null;
            vm.newMsgInput = false;
            vm.isMsg = true;
            vm.mms = null;
            vm.isNote = false;
        })
    },
    loadMoreLead(){
        var url = window.location.href;
        var vm = this;
        let data = {
            "check": "leads",
            "first":this.first,
            "second": this.second
        };
        this.first = this.second;
        this.second = this.second + 100;
        console.log(this.first, this.second)
        console.log(data)
        var r = sendRequest(url, 'post', data)
            .then(function(response){
                new_leads = response.data.leads;
                vm.leads = [...vm.leads, ...response.data.leads]
            })
    },
    lead_refresh(){
        this.created();
    },
    chatDetails(cam_id,dnis){
        this.newMsgInput = false;
        this. isMsg = true;
        this.isNote = false;
        document.getElementById("session").style.display = "none";
        var vm = this;
        var url = '/campaigns/leads/conversations/'+cam_id+'/'+dnis;
        var data = {
            'check':'chat_details'
        }
        var r = sendRequest(url, 'post', data)
            .then(function(response){
                vm.chats = response.data.chats;
                // vm.ani = response.data.ani;
                vm.dnis = response.data.dnis;
                vm.chat = response.data.chat
                // vm.chats.push(response.data.chats);
            })

    },
    sendText(){
        if (this.message.length>0){
            let formData = {
                'mms': this.mms,
                'check': 'manual_text',
                'ani': this.ani,
                'dnis': this.dnis,
                'scheduled_at': this.scheduledAt,
                'message': this.message,
            }

            console.log(formData)
            let url = window.location.href;
            let vm = this;
            sendRequest(url, "post", formData)
                .then(function(response){
                    vm.chats = response.data.chats;
                    vm.ani = response.data.ani;
                    vm.chat = response.data.chat;
                    vm.scheduledAt = null;
                    vm.message = null;
                    vm.image = null;
                })
        }
    },

    removeItem(dnis){
        if (confirm_delete()){
            let data = {
                "check":"remove_dnis",
                "dnis": dnis
            }
            let vm = this;
            let url = '/campaigns/conversations/';
            sendRequest(url, 'post', data)
                .then(function(response){
                    vm.leads = response.data.leads;
                    vm.chats = [];
                    vm.dnis = null;
                })
        }
    },
    deleteCampaign(cam_id){
        if (confirm_delete()){
           let data = {
            "check":"delete_campaign",
            "cam_id": cam_id
            }
            let vm = this;
            let url = '/campaigns/';
            sendRequest(url, 'post', data)
                .then(function(response){
                    sweetText(response.data.alert)
                    refresh();
                })

        }
        
    },
    removeCam(cam_id){
        if (confirm_delete()){
           let data = {
            "check":"remove",
            "cam_id": cam_id
            }
            let vm = this;
            let url = '/campaigns/';
            sendRequest(url, 'post', data)
                .then(function(response){
                    sweetText(response.data.alert)
                    refresh();
                })

        }
        
    },
    cleanCampaign(cam_id){
        if (confirm_delete()){
           let data = {
            "check":"clean",
            "cam_id": cam_id
            }
            let vm = this;
            let url = '/campaigns/';
            sendRequest(url, 'post', data)
                .then(function(response){
                    sweetText(response.data.alert)
                    refresh();
                })

        }
        
    },
    activateCampaign(cam_id, to_confirm){
        if (confirm_delete()){
           let data = {
            "check":"activate_deactivate",
            "cam_id": cam_id,
            "to_confirm": to_confirm,
            }
            let vm = this;
            let url = '/campaigns/';
            sendRequest(url, 'post', data)
                .then(function(response){
                    sweetText(response.data.alert)
                    refresh();
                })
        }
    },
    deleteAllSms(){
        let confirmation = document.getElementById("delete").value
        if (confirmation == "Confirm"){
            if (confirm_delete()){
                alert("Please wait a moment")
                let data = {
                    "check": "delete_all_sms"
                }
                let url = "/home/admin/"
                sendRequest(url, "post", data)
                    .then(function(response){
                        if (response.data.alert == "deleted"){
                            sweetText("Deleted all sms")
                        }
                    })
                }
        }else{
            alert("Type 'Confirm' to confirm the request")
        }
    },   
    searchDnis(){
        let dnis = document.getElementById("search").value;
        let data = {
            "dnis":dnis,
            "check":"search_dnis"
        }
        let url = window.location.href;
        let vm = this;
        sendRequest(url,"post", data)
        .then(function(response){
            vm.leads = response.data.leads;
        })
    },
    CheckText(){
        console.log(this.check_text_input);
        let data = {
            "text-input":this.check_text_input,
            "check":"check_text_input"
        }
        let url = window.location.href;
        let vm = this;
        sendRequest(url,"post", data)
        .then(function(response){
            vm.text_output = response.data.text_output;
        })
    }
  }
})
