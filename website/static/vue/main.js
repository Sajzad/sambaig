function changeLanguage(language) {
  var element = document.getElementById("url");
  element.value = language;
  element.innerHTML = language;
}

function refresh() {    
    setTimeout(function () {
        location.reload()
    }, 300);
}

function confirm_delete(){
    return confirm("Are you sure?")
}

function confirmed(text) {
    return confirm(text)
}

function sweetText(text){
    const Toast = Swal.mixin({
        toast: true,
        position: 'top-end',
        showConfirmButton: false,
        timer: 1000,
        timerProgressBar: true,
        didOpen: (toast) => {
            toast.addEventListener('mouseenter', Swal.stopTimer)
            toast.addEventListener('mouseleave', Swal.resumeTimer)
        }
    })

    Toast.fire({
        icon: 'success',
        title: text

    })
}

function sendRequest(url, method, data){
    var r = axios({
        method:method,
        url: url,
        data: data,
        xsrfCookieName:'csrftoken',
        xsrfHeaderName:'X-CSRFToken',
        headers:{
            'X-Requested-With':'XMLHttpRequest'
        }
    })
    return r
}

function fileRequest(url, method, data){
    var r = axios({
        method:method,
        url: url,
        data: data,
        xsrfCookieName:'csrftoken',
        xsrfHeaderName:'X-CSRFToken',
        headers:{
            'Content-Type': 'multipart/form-data'
        }
    })
    return r
}
