var app = new Vue({
  el: '#app',
    components: { 
        Multiselect: window.VueMultiselect.default 
    },
  delimiters:['[[', ']]'],
  data: {
    leads:'',
    // update contact
    list: '',
    lists: '',
    dnis:'',
    clickedDnis: null,
    message:'',
    name: '',
    chat:'',
    chats:'',
    first: 0,
    second: 0,
    check_text_input: '',
    text_output: '',
    newNumber: '',
    newMessage: '',
    newResponse: '',
    scheduledAt: '',
    ani: '',
    newMsgInput: false,
    showQResponse: false,
    isMsg: true,
    isManual: false,
    isNote: false,
    toShow: false,
    isEmoji: false,
    is_loading: false,
    image: [],
    images: [],
    responses: [],
    mms: '',
    respId: '',
    searchGif: '',
    selectedGif: '',
    searchedGifs: [],
    emojiSearch : '',
    emojis: [],
    // quick response
    responses : '',
    response : '',
    newResponse : '',
    respId : '',
    showQResponse : false,
    stopLoadingLead: false,
    messageLoading: false,
    group_title_id: null,
    groupTitle: '',
    titles : [],
    title : '',
    isGroup: false,
    input_dnis: '',
    total_lead: '',
    filter_types: {
        'newest': 'newest wait',
        'longest': 'longest'
    },
    filter_type: 'newest wait',
    // contact
    contact: {
        'first_name': 'first name',
        'last_name': 'last name',
        'email': 'test@gmail.com'
    },

  },
  created(){
    var url = window.location.href;
    var vm = this;
    let data = {
        "check": "leads",
        "first":this.first,
        "filter_type": this.filter_type,
        "second": this.second+50
    };

    var r = sendRequest(url, 'post', data)
        .then(function(response){
            console.log(vm.leads)
            if (response.data.leads){
                vm.leads = response.data.leads;
                console.log(response.data.leads)
            }
            console.log(vm.leads)
            vm.ani = response.data.ani;
            console.log(response.data.ani)
            vm.total_lead = response.data.total_lead;
            vm.first = 50;
            vm.second = 100;
        })

    sendRequest(url, 'get')
    .then(function(response){
        vm.images = response.data.images
    })
    var elem = document.getElementById('chat');
    if (elem){
        elem.scrollTop = elem.scrollHeight;
    }
  },
    
  //   watch:{
  //   message: function(){
  //       if(this.message.length>0){
  //           document.getElementById("send-message").disabled=false;
  //       }else{
  //          document.getElementById("send-message").disabled=true; 
  //       }
  //   }
  // },

  filters: {
    phone_number: function(input){
        if (input){
            input = input.replace("+", "")
            input = input.replace(/\D/g,'');
            var size = input.length;
            if (input[0]=='1'){
                var first = input.slice(1,4)
                var second = input.slice(4,7)
                var third = input.slice(7, size)
                return '1 '+'(' + first + ')' + '-' +second+ '-'+ third;
            }else if (input[0]=='+'){
                var first = input.slice(3,6)
                var second = input.slice(6,9)
                var third = input.slice(9, size)
                return '+1 '+'(' + first + ')' + '-' +second+ '-'+ third;
            }else{
                var first = input.slice(0,3)
                var second = input.slice(3,6)
                var third = input.slice(6, size)
                return '1 '+'(' + first + ')' + '-' +second+ '-'+ third;
            }
            
        }
        
    },
    truncate: function (text, length) {
        if(text){
            if (text.length > length) {
                return text.substring(0, length) + "...";
            } else {
                return text;
            }
        }else{
            return text
        }
    },
  },

  methods: {
    inboxScrolling(){
        var elem = document.getElementById('chat');
        if (elem){
            elem.scrollTop = elem.scrollHeight;
        }
    },
    updateList(){
        if (this.list){
            let data = {
                check: 'update_list',
                list: this.list,
                contact: this.contact,
                dnis: this.dnis
            }
            var vm = this;
            var url = window.location.href;
            sendRequest(url, 'post', data)
            .then(function(response){
                vm.getLeads();
            })
        }else{
            alert('please select List.')
        }
    },
    getList(){
        let data = {
            check: 'get_list',
            dnis: this.dnis,
        }
        var vm = this;
        var url = window.location.href;
        sendRequest(url, 'post', data)
        .then(function(response){
            vm.lists = response.data.lists;
            if (response.data.contact){
               vm.contact = response.data.contact;
            }
            vm.list = vm.contact.contact;

        })

    },
    cancelGif(){
        this.selectedGif = null;
    },
    closeEmoji(){
        this.isEmoji = false;
    },
    filterLeads(){
        console.log(this.filter_type)
        var url = window.location.href;
        var vm = this;
        let data = {
            "check": "filter_leads",
            "first":0,
            "second": 50,
            "filter_type": this.filter_type
        };
        // this.first = this.second;
        
        sendRequest(url, 'post', data)
            .then(function(response){
                vm.leads = response.data.leads;
                vm.ani = response.data.ani;
                vm.responses = response.data.responses;
                vm.total_lead = response.data.total_lead;
                vm.first = 0;
                vm.second = 50;
                var elem = document.getElementById('chat');
                if (elem){
                    elem.scrollTop = elem.scrollHeight;
                }
            })

    },
    getLeads(){
        var url = window.location.href;
        var vm = this;
        let data = {
            "check": "leads",
            "first":0,
            "filter_type": this.filter_type,
            "second": 50
        };
        // this.first = this.second;
        
        sendRequest(url, 'post', data)
            .then(function(response){
                vm.leads = response.data.leads;
                vm.ani = response.data.ani;
                vm.responses = response.data.responses;
                vm.total_lead = response.data.total_lead;
                vm.first = 0;
                vm.second = 50;
                var elem = document.getElementById('chat');
                if (elem){
                    elem.scrollTop = elem.scrollHeight;
                }
            })

    },
    chatDetails(dnis){
        this.clickedDnis = dnis;
        this.dnis = "";
        this.isNote = false;
        this.messageLoading = true;
        document.getElementsByClassName("leads")[0].classList.remove("sm-display-block");
        document.getElementsByClassName("leads")[0].classList.add("sm-display-none");

        document.getElementById("aside").classList.remove("sm-display-block");
        document.getElementById("aside").classList.add("sm-display-none");
        
        document.getElementById("chat-details").classList.add("sm-display-block");
        this.isEmoji = false;
        this.isMsg = true;
        var vm = this;
        var url = '/campaigns/leads/conversations/'+dnis;
        var data = {
            'check':'chat_details',
            'ani': this.ani,
        }
        console.log(data)
        sendRequest(url, 'post', data)
            .then(function(response){
                // vm.chats = "";
                vm.chats = response.data.chats;
                vm.isManual = response.data.is_manual;
                vm.ani = response.data.ani;
                vm.dnis = response.data.dnis;
                vm.name = response.data.name;
                vm.newMsgInput = false;
                // vm.getLeads();
                vm.isManual = response.data.is_manual;
                setTimeout(vm.inboxScrolling, 700);
                vm.messageLoading = false;
        })

    },
    selectGif(gifUrl){
        this.selectedGif = gifUrl;
        this.scheduledAt = null;
        this.mms = null;
    },
    searchEmojis(){
        var apiKey = '42b4b1a86b67e8a88dd7acf87bd4b966c2d79356';
        var url = "https://emoji-api.com/emojis?search="+this.emojiSearch+"&access_key="+apiKey;
        console.log(url);
        var vm = this;
        sendRequest(url, 'get')
        .then(function(response){
            vm.emojis = response.data
        })
        .catch(function(error){
                console.log(error)
            })
    },
    getEmojis(){

        if(this.isEmoji == true){
            this.isEmoji = false;
        }else{
            this.isEmoji =true
        }

        if (this.emojis.length<1){
            var apiKey = '42b4b1a86b67e8a88dd7acf87bd4b966c2d79356';
            var url = "https://emoji-api.com/emojis?access_key="+apiKey;
            console.log(url);
            var vm = this;
            sendRequest(url, 'get')
            .then(function(response){
                vm.emojis = response.data
                console.log(response.data)
            })
            .catch(function(error){
                    console.log(error)
                })
        }
    },
    selectEmoji(emoji){
        this.message = this.message+emoji;
    },
    searchGifs(){
        var apiKey = 'FIKVI7J2078L';
        var url = "https://g.tenor.com/v1/search?q="+this.searchGif+"&key="+apiKey+"&limit=30";
        console.log(url);
        // var url = "http://api.giphy.com/v1/gifs/search?api_key="+apiKey+"&q="+this.searchGif;
        var vm = this;
        sendRequest(url, 'get')
        .then(function(response){
            vm.searchedGifs = response.data.results;
        })
        .catch(function(error){
                console.log(error)
            })
    },
    showTitleForm(){
        this.isGroup = true;
    },
    createGroupTitle(){
        var data = {
            "check": "create_title",
            "title": this.groupTitle
        }
        var url = "/campaigns/autoresponders/";
        var vm = this;
        sendRequest(url, "post", data)
        .then(function(response){
            vm.titles = response.data.titles;
            vm.isGroup = false;
            sweetText("Title is created")
        })
    },
    getTitles(){
        var data = {
                check: 'get_titles',
            }
        var url = "/campaigns/autoresponders/";
        var vm = this;
        sendRequest(url, "post", data)
        .then(function(response){
            vm.titles = response.data.titles;
        })
    },
    createQResponse(){
        var vm = this;
        var data = {
            check: 'quick_response',
            group_title_id: this.group_title_id,
            response: this.newResponse
        }
        var url = "/campaigns/autoresponders/";
        sendRequest(url, 'post', data)
        .then(function(response){
            vm.responses = response.data.responses;
            vm.newResponse = null;
            vm.getTitles()
        })
    },
    getTitleToEdit(title_id){
        var data = {
            check: 'get_title_to_edit',
            title_id: title_id,
        }
        var url = "/campaigns/autoresponders/";
        var vm = this;
        sendRequest(url, "post", data)
        .then(function(response){
            vm.groupTitle = null;
            vm.title_id = null;
            vm.title = response.data.title;
        }) 
    },
    deleteTitle(title_id){
        if (confirm_delete()){
            var data = {
                    check: 'delete_title',
                    title_id: title_id,
                }
            var url = "/campaigns/autoresponders/";
            var vm = this;
            sendRequest(url, "post", data)
            .then(function(response){
                vm.getTitles()
                sweetText("Title deleted successfully")
            })    
        }
    },
    editQTitle(title_id){
        var data = {
                check: 'edit_title',
                title_id: title_id,
                group_title: this.title.title
            }
        var url = "/campaigns/autoresponders/";
        var vm = this;
        sendRequest(url, "post", data)
        .then(function(response){
            vm.getTitles()
            sweetText("Title edited successfully")
        })    
    },
    deleteResponse(resp_id){
        if(confirm_delete()){
            var data = {
                check: 'delete_response',
                resp_id: resp_id,
            }
            var url = "/campaigns/autoresponders/";
            var vm = this;
            sendRequest(url, "post", data)
            .then(function(response){
                vm.newResponse = null;
                vm.respId = null;
                vm.getTitles()
                sweetText("Item deleted successfully")
            })
        }
    },
    getQResponse(resp_id){
        var data = {
            check: 'get_single_response',
            resp_id: resp_id,
        }
        var url = "/campaigns/autoresponders/";
        var vm = this;
        sendRequest(url, "post", data)
        .then(function(response){
            vm.response = response.data.response;
            vm.group_title_id = vm.response.title.id;
        })
    },
    editResponse(resp_id){
        var data = {
            check: 'edit_response',
            resp_id: resp_id,
            title_id: this.group_title_id,
            response: this.response.response,
        }
        var url = "/campaigns/autoresponders/";
        var vm = this;
        sendRequest(url, "post", data)
        .then(function(response){
            vm.getTitles()
        })
    },
    selectResponse(resp_id){
        var url = "/campaigns/autoresponders/";
        var data = {
            check: 'get_quick_response',
            quic_resp_id: resp_id,
        }
        var vm = this;
        sendRequest(url, "post", data)
        .then(function(response){
            vm.message = vm.message + " " + response.data.response;
            vm.message = vm.message.trim();
        })
    },

    showQuickResponse(){
        if(this.showQResponse == true){
            this.showQResponse = false;
        }else{
            this.showQResponse = true;
        }
    },
    autoHeight(){
        const { textarea } = this.$refs;
        setTimeout(function(){
            textarea.style.cssText = 'height:auto; padding:0';
            textarea.style.cssText = 'height:' + textarea.scrollHeight + 'px';
            let height = document.getElementById('chat').offsetHeight;
            // document.getElementById('chat').style.height = height-textarea.scrollHeight+'px';
        }, 0)
    },
    switchAutoresponse(){
        var url = window.location.href;
        var vm = this;
        var data = {
            check: 'switch_autoresponse',
            is_manual: this.isManual,
            dnis: this.dnis
        }
        sendRequest(url, 'post', data)
        .then(function(response){
            vm.isManual = response.data.is_manual;
        })
    },

    selectMMS(){
        this.mms = null;
        this.selectedGif = null;
    },
    handlingFile(e){
        this.image = e.target.files[0]
        this.selectedGif = null;

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
            this.mms = null;
            this.image = e.target.files[0]
            this.selectedGif = null;
        })
    },
    sendNote(){
        if (confirmed("Are you sure you want to leave a note?")){
            var url = window.location.href;
            var vm = this;
            var data = {
                check: 'send_note',
                ani:this.ani,
                dnis:this.dnis,            
                message: this.message,
            }
            sendRequest(url, 'post', data)
            .then(function(response){
                vm.chats = response.data.chats;
                vm.scheduledAt = null;
                vm.newMessage = null;
                vm.newNumber = null;
                vm.mms = null;
                vm.image = null,
                vm.selectedGif = null;
                vm.message = "";

            })
        }
    },
    shiftToNote(){
        this.isMsg = false;
        this.newMsgInput = false;
        this.scheduledAt = null;
        this.isNote = true;
    },    
    shiftToMsg(){
        this.isMsg = true;
        this.isNote = false;
    },
    enableNewMsgInput(){
        document.getElementsByClassName("leads")[0].classList.remove("sm-display-block");
        document.getElementsByClassName("leads")[0].classList.add("sm-display-none");

        document.getElementById("aside").classList.remove("sm-display-block");
        document.getElementById("aside").classList.add("sm-display-none");

        document.getElementById("chat-details").classList.remove("sm-display-none");
        document.getElementById("chat-details").classList.add("sm-display-block");

        this.chats = [];
        this.dnis = '';
        this.name = '';
        this.isMsg = false;
        this.isNote = false;
        this.scheduledAt = null;
        if (this.newMsgInput==false){
            this.newMsgInput = true;
        }else{
            this.newMsgInput = false;
            this.isMsg = true;
        }
    },
    backToLead(){
        document.getElementsByClassName("leads")[0].classList.add("sm-display-block");        
        document.getElementsByClassName("leads")[0].classList.remove("sm-display-none");

        document.getElementById("aside").classList.remove("sm-display-none");
        document.getElementById("aside").classList.add("sm-display-block");

        document.getElementById("chat-details").classList.remove("sm-display-block");
        document.getElementById("chat-details").classList.add("sm-display-none");
    },
    formatDate(date) {
      return moment(date).format("Do MMM YYYY LT")
    },
    formatTime(date) {
      return moment(date).format("LT, D MMM")
    },    
    timeSince(date) {
      return moment(date).fromNow(true);
    },
    sendNewMessage(){
        console.log("new message")
        if(!this.newNumber){
            alert("Please add a recepient number")
        }
        else if (this.message || this.mms || this.selectedGif || this.newNumber){
            var url = window.location.href;
            var vm = this;
            var data = {
                check: 'new_message',
                new_number: this.newNumber,
                new_message: this.message,
                mms : this.mms,
                gif_url: this.selectedGif,
                scheduled_at: this.scheduledAt,
            }
            console.log(data)
            sendRequest(url, 'post', data)
            .then(function(response){
                vm.chats = response.data.chats;
                vm.ani = response.data.ani;
                vm.dnis = response.data.dnis;
                vm.scheduledAt = '';
                vm.message = '';
                vm.newNumber = '';
                vm.newMsgInput = false;
                vm.isMsg = true;
                vm.mms = '';
                vm.isNote = false;
                this.image = '',
                this.selectedGif = '';
                vm.getLeads();

            })
        }
        else{
            alert("You have nothing to send!")
        }
    },

    loadMoreLead(){
        this.stopLoadingLead = true;
        this.is_loading = true;
        var url = window.location.href;
        var vm = this;
        let data = {
            "check": "leads",
            "first":this.first,
            "second": this.second
        };

        console.log(data)
        var r = sendRequest(url, 'post', data)
            .then(function(response){
                if (response.data.leads != null){
                    new_leads = response.data.leads;
                    vm.leads = [...vm.leads, ...response.data.leads]
                    vm.total_lead = response.data.total_lead;
                    vm.is_loading = false;
                    vm.first = vm.second;
                    vm.second = vm.second + 50;
                    
                    var elem = document.getElementById('scroll');
                    if (elem){
                        elem.scrollTop = elem.scrollHeight;
                    }
                }else{
                    vm.is_loading = false;
                }
            })
    },
    lead_refresh(){
        this.created();
    },
    sendText(){
        if (this.message || this.mms || this.selectedGif){

            let formData = {
                'mms': this.mms,
                'check': 'manual_text',
                'ani': this.ani,
                'dnis': this.dnis,
                'scheduled_at': this.scheduledAt,
                'gif_url': this.selectedGif,
                'message': this.message,
            }
            let url = window.location.href;
            let vm = this;
            sendRequest(url, "post", formData)
                .then(function(response){
                    // vm.ani = response.data.ani;
                    vm.chatDetails(vm.dnis);
                    vm.scheduledAt = '';
                    vm.message = '';
                    vm.mms =  '';
                    vm.selectedGif = '';
                    var elem = document.getElementById('chat');
                    if (elem){
                        elem.scrollTop = elem.scrollHeight;
                    }
                })
        }else{
            alert("You have nothing to send.")
        }
    },

    removeItem(dnis){
        console.log("yes")
        if (confirm_delete()){
            let data = {
                "check":"remove_dnis",
                "dnis": dnis
            }
            let vm = this;
            let url = window.location.href;
            sendRequest(url, 'post', data)
                .then(function(response){
                    vm.getLeads();
                    vm.dnis = '';
                    vm.chats = [];
                })
        }
    },

    cancelScheduledSms(sms_id){
        var text = "Are you going to cancel the scheduled sms?"
        if (confirmed(text)){
            let data = {
                "check":"cancel_scheduled_sms",
                "sms_id": sms_id
            }
            let vm = this;
            let url = window.location.href;
            sendRequest(url, 'post', data)
                .then(function(response){
                    vm.chatDetails(vm.dnis)
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
        this.stopLoadingLead = true;
        if (this.input_dnis.length==0){
            this.getLeads()
            this.stopLoadingLead = false;

        }
        let data = {
            "dnis": this.input_dnis,
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
    },
    likeNote(sms_id){
        console.log(sms_id)
        var vm = this;
        var url = '/campaigns/conversations/';
        var data = {
            'sms_id': sms_id,
            'check':'manage_like'
        }
        sendRequest(url, 'post', data)
            .then(function(response){
                vm.getLeads()
                vm.chatDetails(vm.dnis)
        })
    },
    chatPulling(){
        // this.isEmoji = false;
        // this.isMsg = true;
        if (this.newMsgInput == false && this.dnis.length>1){
            var vm = this;
            var url = '/campaigns/leads/conversations/'+this.dnis;
            var data = {
                'check':'chat_details',
                'ani': this.ani,
            }
            sendRequest(url, 'post', data)
                .then(function(response){
                    vm.chats = response.data.chats;
                    vm.dnis = response.data.dnis;
                    vm.ani = response.data.ani;
                    vm.isManual = response.data.is_manual;
            })
            // var elem = document.getElementById('chat');
            // if (elem){
            //     elem.scrollTop = elem.scrollHeight;
            // }            
        }
    },
    pullLeads(){
        var url = window.location.href;
        var vm = this;
        let data = {
            "check": "leads",
            "first":0,
            "filter_type": this.filter_type,
            "second": 50
        };
        
        sendRequest(url, 'post', data)
            .then(function(response){
                vm.leads = response.data.leads;
                vm.ani = response.data.ani;
                vm.total_lead = response.data.total_lead;
                vm.responses = response.data.responses;
            })

    },
  },
    mounted: function () {
        var vm = this;
        var loadData = function(){
            if (!vm.stopLoadingLead){
                console.log('switch')
                vm.pullLeads();
            }
            if(vm.dnis){
                vm.chatPulling();
            }
            setTimeout(loadData, 10000);
        };
        setTimeout(loadData,10000);
    }
})
