var postModal = document.getElementById('postmodal{{ post.id }}');
function modalClick(id) {
    window.history.pushState({},"", "/feed/popup_post/" + id );
    postModal.show();
}  
postModal.addEventListener('hidden.bs.modal', function (event) {
    window.history.replaceState({}, "", "{% url 'user:profile' user.id %}")
})