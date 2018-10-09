tinymce.init({
  selector: 'textarea',
  height: 300,
  menubar: false,
  plugins: [
    'advlist autolink lists link charmap print preview textcolor',
    'searchreplace visualblocks code fullscreen',
    'insertdatetime table contextmenu paste code help wordcount'
  ],
  toolbar: 'insert | undo redo |  formatselect | bold italic backcolor  | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | help',
  content_css: [
    '//fonts.googleapis.com/css?family=Lato:300,300i,400,400i',
    '//www.tinymce.com/css/codepen.min.css']
});