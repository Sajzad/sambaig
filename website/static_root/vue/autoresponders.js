var app = new Vue({
  el: '#app',
  delimiters:['[[', ']]'],
  data: {
    leads: [],
    urls: [],
    resp_id: null,
    resp_details: '',
    isEmoji: false,
    isEditUrl: false,
    emojis: '',
    emojiSearch : '',
    message: '',
    toShow: false,
    responses : '',
    response : '',
    newResponse : '',
    respId : '',
    showQResponse : false,
    group_title_id: null,
    groupTitle: null,
    titles : [],
    title : '',
    isGroup: false,
    primary_number: '',
    createAutoresponder: false,
    ani: '',
    url: '',
    // gif
    searchedGifs: '',
    selectedGif: '',
    searchGif: '',
    givenUrl: '',
    addToNew: false,
    // endgif
    unsubscribed_msg: "Reply stop to stop"

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
    // Short Url
    deleteUrl(url_id){
        if (confirmed("Are you sure you want to delete the item?")){
            var vm = this;
            var url = '/shortened-url/'
            var data = {
                'url_id': url_id,
                'check': 'delete_url'
            }
            sendRequest(url, 'post', data)
            .then(function(response){
                vm.getShortUrls()
            })
        }
    },
    updateUrl(){
        var text = 'Are you sure you want to edit current URL?'
        if (confirmed(text))
        var vm = this;
        var url = '/shortened-url/'
        var data = {
            'url': this.url,
            'check': 'update_url'
        }
        sendRequest(url, 'post', data)
        .then(function(response){
            vm.getShortUrls()
            vm.isEditUrl=false;
        })
    },
    getUrl(url_id){
        var vm = this;
        var url = '/shortened-url/'
        var data = {
            'url_id': url_id,
            'check': 'get_url'
        }
        sendRequest(url, 'post', data)
        .then(function(response){
            vm.url = response.data.url
        })
    },
    enableUrlEdit(){
        if (this.isEditUrl){
            this.isEditUrl = false
        }else{
            this.isEditUrl = true
        }
    },
    getShortUrls(){
        var vm = this;
        var url = '/shortened-url/'
        
        sendRequest(url, 'get')
        .then(function(response){
            vm.urls = response.data.urls
        })
    },
    shortenURl(){
        var vm = this;
        var url = '/shortened-url/'
        var data = {
            'given_url': this.givenUrl,
            'check': 'shorten_url'
        }
        sendRequest(url, 'post', data)
        .then(function(response){
            vm.getShortUrls()
            vm.givenUrl = '';
        })
    },
    // end Short url
    toggleListSelection(){
        if(this.addToNew){
            this.addToNew=false;
        }else{
            this.addToNew=true
        }
    },
    cancelGif(){
        this.selectedGif = null;
    },
    selectGif(gifUrl){
        this.selectedGif = gifUrl;
        this.mms = null;
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
    closeEmoji(){
        this.isEmoji = false;
    },
    activateAutoresp(){
        if (this.createAutoresponder){
            this.createAutoresponder = false;
        }else{
            this.createAutoresponder = true;
        }
    },
    pn(){
        console.log("yes")
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
        console.log("ttiles")
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
    addCustomField(field){
        this.message = this.message + " " + field
    },
    activateResponse(resp_id, is_active){
        if (confirm_delete()){
            var vm = this;
            var url = window.location.href;
            var data = {
                'check': 'pause_response',
                'resp_id': resp_id,
                'is_active': is_active
            }
            sendRequest(url, 'post', data)
            .then(function(response){
                vm.respDetails(resp_id)               
            })

        }
 
    },
    deleteAutoresponse(resp_id){
        if (confirm_delete()){
            var vm = this;
            var url = window.location.href;
            var data = {
                'check': 'response_delete',
                'resp_id': resp_id
            }
            sendRequest(url, 'post', data)
            .then(function(response){
                refresh()                
            })

        }
    },
    respDetails(resp_id){
        this.resp_id = resp_id;
        var vm = this;
        var url = window.location.href;
        var data = {
            'check': 'response_details',
            'resp_id': resp_id
        }
        sendRequest(url, 'post', data)
        .then(function(response){
            console.log(response.data.resp_details)
            vm.resp_details = response.data.resp_details;

            document.getElementById('aside').classList.remove("sm-display-block")
            document.getElementById('aside').classList.add("sm-display-none")            

            document.getElementById('drip').classList.remove("sm-display-block")
            document.getElementById('drip').classList.add("sm-display-none")

            document.getElementById('drip_details').classList.remove("sm-display-none")
            document.getElementById('drip_details').classList.add("sm-display-block")
        })
    },
    backToLead(){
        document.getElementById('aside').classList.remove("sm-display-none")
        document.getElementById('aside').classList.add("sm-display-block")            

        document.getElementById('drip').classList.remove("sm-display-none")
        document.getElementById('drip').classList.add("sm-display-block")

        document.getElementById('drip_details').classList.remove("sm-display-block")
        document.getElementById('drip_details').classList.add("sm-display-none")
    },
    searchEmojis(){
        var apiKey = '42b4b1a86b67e8a88dd7acf87bd4b966c2d79356';
        var url = "https://emoji-api.com/emojis?search="+this.emojiSearch+"&access_key="+apiKey;
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
    formatDate(date) {
      return moment(date).format("Do MMM YYYY LT")
    },
    formatTime(date) {
      return moment(date).format("LT")
    },
    formattingTime(time) {
        if (time){
            return moment(time, "HH:mm:ss").format("hh:mm A")
        }else{
            return ""
        }
    },    
    timeSince(date) {
      return moment(date).fromNow(true);
    }

  }
})
